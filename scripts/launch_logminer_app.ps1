param(
    [int]$ApiPort = 8000,
    [int]$DashboardPort = 5173,
    [int]$AgentWorkers = 2,
    [switch]$SkipRedis,
    [switch]$SkipAgents
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$processed = Join-Path $root "data\processed"
$python = Join-Path $root ".venv\Scripts\python.exe"
$dashboardDir = Join-Path $root "web\dashboard"
$redisCompose = Join-Path $root "docker-compose.redis.yml"

New-Item -ItemType Directory -Path $processed -Force | Out-Null

function Test-Port {
    param([int]$Port)
    try {
        $connection = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop
        return [bool]$connection
    } catch {
        return $false
    }
}

function Test-CommandAvailable {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Wait-Http {
    param(
        [string]$Url,
        [int]$Seconds = 45
    )
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        try {
            Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec 2 | Out-Null
            return $true
        } catch {
            Start-Sleep -Milliseconds 600
        }
    }
    return $false
}

function Wait-Port {
    param(
        [int]$Port,
        [int]$Seconds = 20
    )
    $deadline = (Get-Date).AddSeconds($Seconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-Port $Port) {
            return $true
        }
        Start-Sleep -Milliseconds 600
    }
    return $false
}

function Test-WorkerRunning {
    param([string]$AgentId)
    try {
        $escaped = [Regex]::Escape($AgentId)
        $process = Get-CimInstance Win32_Process -Filter "Name = 'python.exe' OR Name = 'pythonw.exe'" |
            Where-Object { $_.CommandLine -match "logminer_intelligent_agent_worker.py" -and $_.CommandLine -match $escaped } |
            Select-Object -First 1
        return [bool]$process
    } catch {
        return $false
    }
}

if (-not (Test-Path $python)) {
    [System.Windows.Forms.MessageBox]::Show("Environnement Python introuvable: $python", "Ariel Logminer") | Out-Null
    exit 1
}

if (-not $SkipRedis -and -not (Test-Port 6379) -and (Test-CommandAvailable "docker") -and (Test-Path $redisCompose)) {
    Start-Process -FilePath "docker" `
        -ArgumentList @("compose", "-f", $redisCompose, "up", "-d") `
        -WorkingDirectory $root `
        -WindowStyle Hidden `
        -Wait `
        -RedirectStandardOutput (Join-Path $processed "redis_start.log") `
        -RedirectStandardError (Join-Path $processed "redis_start.err.log")
    Wait-Port -Port 6379 -Seconds 30 | Out-Null
}

if (-not (Test-Port $ApiPort)) {
    Start-Process -FilePath $python `
        -ArgumentList @("-m", "uvicorn", "src.logminer.api:app", "--host", "127.0.0.1", "--port", "$ApiPort") `
        -WorkingDirectory $root `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $processed "api_server.log") `
        -RedirectStandardError (Join-Path $processed "api_server.err.log")
}

if (-not (Test-Port $DashboardPort)) {
    Start-Process -FilePath "node" `
        -ArgumentList @("server.mjs") `
        -WorkingDirectory $dashboardDir `
        -WindowStyle Hidden `
        -RedirectStandardOutput (Join-Path $processed "dashboard_server.log") `
        -RedirectStandardError (Join-Path $processed "dashboard_server.err.log")
}

if (-not $SkipAgents -and (Test-Port 6379)) {
    for ($i = 1; $i -le [Math]::Max(1, $AgentWorkers); $i++) {
        $agentId = "ariel-desktop-agent-$i"
        if (-not (Test-WorkerRunning -AgentId $agentId)) {
            Start-Process -FilePath $python `
                -ArgumentList @(
                    "scripts\logminer_intelligent_agent_worker.py",
                    "--consumer", "desktop-worker-$i",
                    "--agent-id", $agentId,
                    "--memory", "data/processed/$agentId-memory.json",
                    "--cycles", "999999",
                    "--block-ms", "3000",
                    "--claim-idle-ms", "30000"
                ) `
                -WorkingDirectory $root `
                -WindowStyle Hidden `
                -RedirectStandardOutput (Join-Path $processed "$agentId.log") `
                -RedirectStandardError (Join-Path $processed "$agentId.err.log")
        }
    }
}

$apiReady = Wait-Http -Url "http://127.0.0.1:$ApiPort/health" -Seconds 45
$dashboardReady = Wait-Http -Url "http://127.0.0.1:$DashboardPort" -Seconds 45

if ($dashboardReady) {
    Start-Process "http://127.0.0.1:$DashboardPort"
    exit 0
}

$message = "Le dashboard ne repond pas encore. API: $apiReady. Consultez data\processed\dashboard_server.err.log"
[System.Windows.Forms.MessageBox]::Show($message, "Ariel Logminer") | Out-Null
exit 1
