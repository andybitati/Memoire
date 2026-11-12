param(
    [Parameter(Mandatory = $true)][string]$RunId,
    [Parameter(Mandatory = $true)][string[]]$Vms,
    [string]$GuestRedisUrl = "redis://192.168.56.1:6379/0",
    [int]$IdleTimeoutSec = 120,
    [switch]$CheckOnly
)
# Dérivé de revision_reports/agent_3/start_hdfs_agents.ps1 : mêmes fichiers copiés et même
# agent ; seuls changent le choix des VM lancées, l'URL Redis (interface host-only) et le délai
# d'inactivité. Les identifiants viennent de .secrets/ (DPAPI) et ne sont jamais affichés.
$ErrorActionPreference = "Stop"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
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
    $out = & $vbox guestcontrol $Credential.Vm run --username $Credential.User --password="$($Credential.Password)" --exe /bin/bash -- -lc $Command 2>&1
    $out
}

$profiles = @{
    "Debian" = [pscustomobject]@{Vm="Debian"; Agent="debian-alpha"; Home="/home/vboxuser"; Python="/home/vboxuser/.venv-logminer/bin/python"};
    "Ubuntu" = [pscustomobject]@{Vm="Ubuntu"; Agent="ubuntu-beta"; Home="/home/andy"; Python="python3"}
}
$sourceFiles = @(
    @{Host="revision_reports\agent_3\hdfs_redis_agent.py"; Guest="scripts/hdfs_redis_agent.py"},
    @{Host="src\logminer\agents\bus.py"; Guest="src/logminer/agents/bus.py"},
    @{Host="src\logminer\agents\contract_net.py"; Guest="src/logminer/agents/contract_net.py"},
    @{Host="src\logminer\agents\idempotency.py"; Guest="src/logminer/agents/idempotency.py"},
    @{Host="src\logminer\agents\intelligent_runtime.py"; Guest="src/logminer/agents/intelligent_runtime.py"},
    @{Host="src\logminer\agents\redis_contract_net.py"; Guest="src/logminer/agents/redis_contract_net.py"}
)

foreach ($name in @("Debian", "Ubuntu")) {
    # Arrête tout agent résiduel sur les deux VM, y compris celles non lancées dans ce bras.
    $credential = Get-CredentialRecord $name
    Invoke-Guest $credential "pkill -f '[h]dfs_redis_agent.py' || true" | Out-Null
}
foreach ($name in $Vms) {
    $profile = $profiles[$name]
    $credential = Get-CredentialRecord $name
    if ($CheckOnly) {
        $probe = Invoke-Guest $credential "$($profile.Python) -c 'import sys,socket;print(sys.version.split()[0], socket.gethostname())'; $($profile.Python) -c 'import socket;s=socket.create_connection((""192.168.56.1"",6379),3);s.sendall(b""PING\r\n"");print(s.recv(16))'"
        Write-Output "CHECK $name : $probe"
        continue
    }
    Invoke-Guest $credential "mkdir -p $($profile.Home)/scripts $($profile.Home)/src/logminer/agents" | Out-Null
    foreach ($source in $sourceFiles) {
        & $vbox guestcontrol $name copyto --username $credential.User --password="$($credential.Password)" (Join-Path $projectRoot $source.Host) ($profile.Home + "/" + $source.Guest) 2>&1 | Out-Null
    }
    $namespace = "logminer:cnp:$RunId"
    $eventStream = "logminer:events:$RunId"
    $log = "/tmp/$RunId`__$($profile.Agent).log"
    $command = "cd $($profile.Home) && exec setsid $($profile.Python) -B scripts/hdfs_redis_agent.py --redis-url '$GuestRedisUrl' --event-stream '$eventStream' --namespace '$namespace' --run-id '$RunId' --agent-id '$($profile.Agent)' --idle-timeout-sec $IdleTimeoutSec > '$log' 2>&1 < /dev/null"
    & $vbox guestcontrol $name start --username $credential.User --password="$($credential.Password)" --exe /bin/bash -- -lc $command 2>&1 | Out-Null
    Write-Output "STARTED $name $($profile.Agent)"
}
