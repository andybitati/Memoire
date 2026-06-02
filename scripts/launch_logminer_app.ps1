param(
    [int]$ApiPort = 8000,
    [int]$DashboardPort = 5173
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Windows.Forms

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$processed = Join-Path $root "data\processed"
$python = Join-Path $root ".venv\Scripts\python.exe"
$dashboardDir = Join-Path $root "web\dashboard"

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

if (-not (Test-Path $python)) {
    [System.Windows.Forms.MessageBox]::Show("Environnement Python introuvable: $python", "Ariel Logminer") | Out-Null
    exit 1
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

$apiReady = Wait-Http -Url "http://127.0.0.1:$ApiPort/health" -Seconds 45
$dashboardReady = Wait-Http -Url "http://127.0.0.1:$DashboardPort" -Seconds 45

if ($dashboardReady) {
    Start-Process "http://127.0.0.1:$DashboardPort"
    exit 0
}

$message = "Le dashboard ne repond pas encore. API: $apiReady. Consultez data\processed\dashboard_server.err.log"
[System.Windows.Forms.MessageBox]::Show($message, "Ariel Logminer") | Out-Null
exit 1
