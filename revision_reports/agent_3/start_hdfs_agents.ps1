param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [string]$GuestRedisUrl = "redis://10.0.2.2:6379/0",
    [int]$IdleTimeoutSec = 900
)

$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$vbox = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"

function Get-CredentialRecord([string]$VmName) {
    $path = Join-Path $projectRoot (".secrets\" + $VmName.ToLowerInvariant() + "_vm.credential.json")
    $record = Get-Content -LiteralPath $path -Raw -Encoding utf8 | ConvertFrom-Json
    Add-Type -AssemblyName System.Security
    $encrypted = [Convert]::FromBase64String($record.encrypted_password)
    $plainBytes = [Security.Cryptography.ProtectedData]::Unprotect($encrypted, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
    [pscustomobject]@{ Vm=$VmName; User=[string]$record.username; Password=[Text.Encoding]::UTF8.GetString($plainBytes) }
}

function Invoke-Guest([object]$Credential, [string]$Command) {
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        & $vbox guestcontrol $Credential.Vm run --username $Credential.User --password="$($Credential.Password)" --exe /bin/bash -- -lc $Command
        if ($LASTEXITCODE -eq 0) { return }
        if ($attempt -lt 5) { Start-Sleep -Seconds 3 }
    }
    throw "guestcontrol échoué sur $($Credential.Vm)"
}

$profiles = @(
    [pscustomobject]@{Vm="Debian"; Agent="debian-alpha"; Home="/home/vboxuser"; Python="/home/vboxuser/.venv-logminer/bin/python"},
    [pscustomobject]@{Vm="Ubuntu"; Agent="ubuntu-beta"; Home="/home/andy"; Python="python3"}
)
$sourceFiles = @(
    @{Host="revision_reports\agent_3\hdfs_redis_agent.py"; Guest="scripts/hdfs_redis_agent.py"},
    @{Host="src\logminer\agents\bus.py"; Guest="src/logminer/agents/bus.py"},
    @{Host="src\logminer\agents\contract_net.py"; Guest="src/logminer/agents/contract_net.py"},
    @{Host="src\logminer\agents\idempotency.py"; Guest="src/logminer/agents/idempotency.py"},
    @{Host="src\logminer\agents\intelligent_runtime.py"; Guest="src/logminer/agents/intelligent_runtime.py"},
    @{Host="src\logminer\agents\redis_contract_net.py"; Guest="src/logminer/agents/redis_contract_net.py"}
)

foreach ($profile in $profiles) {
    $credential = Get-CredentialRecord $profile.Vm
    Invoke-Guest $credential "mkdir -p $($profile.Home)/scripts $($profile.Home)/src/logminer/agents"
    foreach ($source in $sourceFiles) {
        & $vbox guestcontrol $profile.Vm copyto --username $credential.User --password="$($credential.Password)" (Join-Path $projectRoot $source.Host) ($profile.Home + "/" + $source.Guest)
        if ($LASTEXITCODE -ne 0) { throw "copie échouée sur $($profile.Vm)" }
    }
    Invoke-Guest $credential "pkill -f '[h]dfs_redis_agent.py' || true"
    $namespace = "logminer:cnp:$RunId"
    $eventStream = "logminer:events:$RunId"
    $log = "/tmp/$RunId`__$($profile.Agent).log"
    $command = "cd $($profile.Home) && exec setsid $($profile.Python) -B scripts/hdfs_redis_agent.py --redis-url '$GuestRedisUrl' --event-stream '$eventStream' --namespace '$namespace' --run-id '$RunId' --agent-id '$($profile.Agent)' --idle-timeout-sec $IdleTimeoutSec > '$log' 2>&1 < /dev/null"
    # « run » attend la fin du processus invité : « start » rend la main immédiatement.
    & $vbox guestcontrol $profile.Vm start --username $credential.User --password="$($credential.Password)" --exe /bin/bash -- -lc $command
    if ($LASTEXITCODE -ne 0) { throw "lancement échoué sur $($profile.Vm)" }
    Write-Output "STARTED $($profile.Vm) $($profile.Agent)"
}
