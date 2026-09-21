param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^cnp_endurance_multivm_\d{8}T\d{6}Z$')]
    [string]$RunId,

    [int]$DurationSec = 3600,
    [string]$VBoxManagePath = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    [string]$GuestRedisUrl = "redis://192.168.56.1:6379/0",
    [ValidateSet("Both", "Debian", "Ubuntu")]
    [string]$OnlyVm = "Both"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$namespace = "logminer:cnp:$RunId"
$eventStream = "logminer:events:$RunId"
$idleTimeout = [Math]::Max(300, $DurationSec + 1800)

function Get-LocalVmCredential {
    param([string]$VmName)

    $path = Join-Path $projectRoot (".secrets\" + $VmName.ToLowerInvariant() + "_vm.credential.json")
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Identifiant local absent pour $VmName"
    }
    $record = Get-Content -LiteralPath $path -Raw -Encoding utf8 | ConvertFrom-Json
    Add-Type -AssemblyName System.Security
    $encrypted = [Convert]::FromBase64String($record.encrypted_password)
    $plainBytes = [Security.Cryptography.ProtectedData]::Unprotect(
        $encrypted,
        $null,
        [Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    return [pscustomobject]@{
        Vm = $VmName
        User = [string]$record.username
        Password = [Text.Encoding]::UTF8.GetString($plainBytes)
    }
}

function Invoke-GuestBash {
    param(
        [pscustomobject]$Credential,
        [string]$Command
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $VBoxManagePath guestcontrol $Credential.Vm run `
            --username $Credential.User `
            --password="$($Credential.Password)" `
            --exe /bin/bash `
            -- -lc $Command
        $exitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousPreference
        if ($exitCode -eq 0) {
            return
        }
        if ($attempt -lt 5) {
            Start-Sleep -Seconds 3
        }
    }
    throw "Commande guestcontrol echouee sur $($Credential.Vm) apres cinq tentatives"
}

function Wait-GuestReady {
    param([pscustomobject]$Credential)

    $deadline = (Get-Date).AddMinutes(3)
    while ((Get-Date) -lt $deadline) {
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = "SilentlyContinue"
        & $VBoxManagePath guestcontrol $Credential.Vm run `
            --username $Credential.User `
            --password="$($Credential.Password)" `
            --exe /bin/bash `
            -- -lc "true" *> $null
        $exitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousPreference
        if ($exitCode -eq 0) {
            Start-Sleep -Seconds 2
            return
        }
        Start-Sleep -Seconds 5
    }
    throw "Guest Control indisponible sur $($Credential.Vm) apres trois minutes"
}

function Run-GuestAgent {
    param(
        [pscustomobject]$Credential,
        [string]$Command
    )

    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $VBoxManagePath guestcontrol $Credential.Vm run `
        --username $Credential.User `
        --password="$($Credential.Password)" `
        --exe /bin/bash `
        -- -lc $Command
    $exitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference
    if ($exitCode -ne 0) {
        throw "Agent termine avec le code $exitCode sur $($Credential.Vm)"
    }
}

function Copy-ToGuest {
    param(
        [pscustomobject]$Credential,
        [string]$HostPath,
        [string]$GuestPath
    )

    for ($attempt = 1; $attempt -le 5; $attempt++) {
        $previousPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        & $VBoxManagePath guestcontrol $Credential.Vm copyto `
            --username $Credential.User `
            --password="$($Credential.Password)" `
            $HostPath `
            $GuestPath
        $exitCode = $LASTEXITCODE
        $ErrorActionPreference = $previousPreference
        if ($exitCode -eq 0) {
            return
        }
        if ($attempt -lt 5) {
            Start-Sleep -Seconds 3
        }
    }
    throw "Copie echouee vers $($Credential.Vm): $GuestPath"
}

if (-not (Test-Path -LiteralPath $VBoxManagePath)) {
    throw "VBoxManage introuvable"
}

$profiles = @(
    [pscustomobject]@{
        Vm = "Debian"
        AgentId = "debian-alpha"
        Profile = "alpha"
        Home = "/home/vboxuser"
        Python = "/home/vboxuser/.venv-logminer/bin/python"
        ExtraArgs = "--crash-after-persisted-result-once"
    },
    [pscustomobject]@{
        Vm = "Ubuntu"
        AgentId = "ubuntu-beta"
        Profile = "beta"
        Home = "/home/andy"
        Python = "python3"
        ExtraArgs = ""
    }
)

$sourceFiles = @(
    [pscustomobject]@{ Host = "scripts\logminer_redis_cnp_agent.py"; Guest = "scripts/logminer_redis_cnp_agent.py" },
    [pscustomobject]@{ Host = "src\logminer\agents\bus.py"; Guest = "src/logminer/agents/bus.py" },
    [pscustomobject]@{ Host = "src\logminer\agents\contract_net.py"; Guest = "src/logminer/agents/contract_net.py" },
    [pscustomobject]@{ Host = "src\logminer\agents\idempotency.py"; Guest = "src/logminer/agents/idempotency.py" },
    [pscustomobject]@{ Host = "src\logminer\agents\intelligent_runtime.py"; Guest = "src/logminer/agents/intelligent_runtime.py" },
    [pscustomobject]@{ Host = "src\logminer\agents\redis_contract_net.py"; Guest = "src/logminer/agents/redis_contract_net.py" }
)

foreach ($profile in $profiles) {
    if ($OnlyVm -ne "Both" -and $OnlyVm -ne $profile.Vm) {
        continue
    }
    $credential = Get-LocalVmCredential -VmName $profile.Vm
    Write-Output ("WAIT " + $profile.Vm)
    Wait-GuestReady -Credential $credential
    Write-Output ("PREPARE " + $profile.Vm)
    Invoke-GuestBash -Credential $credential -Command ("mkdir -p " + $profile.Home + "/scripts " + $profile.Home + "/src/logminer/agents")
    foreach ($source in $sourceFiles) {
        Write-Output ("COPY " + $profile.Vm + " " + $source.Guest)
        Copy-ToGuest `
            -Credential $credential `
            -HostPath (Join-Path $projectRoot $source.Host) `
            -GuestPath ($profile.Home + "/" + $source.Guest)
    }

    Write-Output ("STOP_STALE " + $profile.Vm)
    Invoke-GuestBash -Credential $credential -Command "pkill -f '[l]ogminer_redis_cnp_agent.py' || true"

    $guestLog = "/tmp/$RunId`__$($profile.AgentId).log"
    $command = @(
        "cd $($profile.Home) &&"
        "exec $($profile.Python) -B scripts/logminer_redis_cnp_agent.py"
        "--redis-url '$GuestRedisUrl'"
        "--event-stream '$eventStream'"
        "--namespace '$namespace'"
        "--run-id '$RunId'"
        "--agent-id '$($profile.AgentId)'"
        "--profile '$($profile.Profile)'"
        "--memory on"
        "--idle-timeout-sec $idleTimeout"
        $profile.ExtraArgs
        "> '$guestLog' 2>&1 < /dev/null"
    ) -join " "
    Write-Output ("START " + $profile.Vm)
    Run-GuestAgent -Credential $credential -Command $command
    Write-Output ("STARTED " + $profile.Vm + " " + $profile.AgentId + " log=" + $guestLog)
}

Write-Output ("RUN_ID=" + $RunId)
Write-Output ("NAMESPACE=" + $namespace)
Write-Output ("EVENT_STREAM=" + $eventStream)
