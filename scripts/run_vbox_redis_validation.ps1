param(
    [string[]]$VmNames = @("Debian", "Ubuntu"),
    [string]$VBoxManagePath = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe",
    [string]$HostRedisUrl = "redis://localhost:6379/0",
    [string]$GuestRedisUrl = "redis://10.0.2.2:6379/0",
    [string]$TaskStream = "logminer:agent_tasks",
    [string]$Group = "logminer-intelligent-agents",
    [string]$RunId = ("redis-vbox-" + (Get-Date -Format "yyyyMMddHHmmss")),
    [string]$RepoPathInGuest = '$HOME',
    [string]$PythonInGuest = "python3",
    [string]$DebianPythonInGuest = '$HOME/.venv-logminer/bin/python',
    [string]$UbuntuPythonInGuest = "python3",
    [switch]$EnqueueDemo,
    [switch]$StartHeadless,
    [switch]$RunGuestWorkers,
    [switch]$EnsureSshForwarding,
    [int]$DebianSshPort = 2222,
    [int]$UbuntuSshPort = 2223,
    [string]$DebianUser = "",
    [string]$DebianPassword = "",
    [string]$UbuntuUser = "",
    [string]$UbuntuPassword = ""
)

$ErrorActionPreference = "Stop"

function Assert-Tool {
    param([string]$Path, [string]$Name)
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Name introuvable: $Path"
    }
}

function Invoke-VBox {
    param([string[]]$CommandArgs)
    & $VBoxManagePath @CommandArgs
    if ($LASTEXITCODE -ne 0) {
        throw "VBoxManage a echoue: $($CommandArgs -join ' ')"
    }
}

function Get-VmCredential {
    param([string]$VmName)
    if ($VmName -eq "Debian" -and $DebianUser -and $DebianPassword) {
        return @{ User = $DebianUser; Password = $DebianPassword }
    }
    if ($VmName -eq "Ubuntu" -and $UbuntuUser -and $UbuntuPassword) {
        return @{ User = $UbuntuUser; Password = $UbuntuPassword }
    }
    return $null
}

function Get-VmPython {
    param([string]$VmName)
    if ($VmName -eq "Debian") {
        return $DebianPythonInGuest
    }
    if ($VmName -eq "Ubuntu") {
        return $UbuntuPythonInGuest
    }
    return $PythonInGuest
}

function Ensure-SshForwarding {
    param([string]$VmName, [string]$RuleName, [int]$HostPort)
    $info = & $VBoxManagePath showvminfo $VmName --machinereadable
    $expected = "$RuleName,tcp,,$HostPort,,22"
    if ($info -match [regex]::Escape($expected)) {
        Write-Host "$VmName SSH NAT deja configure: localhost:$HostPort -> invite:22"
        return
    }
    & $VBoxManagePath controlvm $VmName natpf1 $expected
    if ($LASTEXITCODE -ne 0) {
        throw "Impossible d'ajouter la redirection SSH pour $VmName"
    }
    Write-Host "$VmName SSH NAT ajoute: localhost:$HostPort -> invite:22"
}

Assert-Tool -Path $VBoxManagePath -Name "VBoxManage"

Write-Host "VBoxManage: $VBoxManagePath"
Write-Host "RunId: $RunId"

$redisContainer = docker ps --filter name=logminer-redis --format "{{.Names}}"
if ($LASTEXITCODE -ne 0) {
    throw "Docker n'est pas accessible. Lancez Docker Desktop puis relancez ce script."
}
if (-not $redisContainer) {
    docker compose -f docker-compose.redis.yml up -d
    if ($LASTEXITCODE -ne 0) {
        throw "Impossible de lancer Redis avec docker-compose.redis.yml"
    }
}

docker exec logminer-redis redis-cli ping | Out-Host
if ($LASTEXITCODE -ne 0) {
    throw "Redis ne repond pas au ping."
}

foreach ($vm in $VmNames) {
    $info = & $VBoxManagePath showvminfo $vm --machinereadable
    if ($LASTEXITCODE -ne 0) {
        throw "VM introuvable ou inaccessible: $vm"
    }
    $state = ($info | Select-String '^VMState=').ToString()
    if ($state -notmatch '"running"') {
        if ($StartHeadless) {
            Invoke-VBox -CommandArgs @("startvm", $vm, "--type", "headless")
        } else {
            Write-Host "$vm n'est pas lancee. Relancez avec -StartHeadless pour demarrer automatiquement."
            continue
        }
    }
    $nic = ($info | Select-String '^nic1=').ToString()
    Write-Host "$vm pret ($nic). Depuis une VM NAT VirtualBox, Redis hote = $GuestRedisUrl"
}

if ($EnsureSshForwarding) {
    Ensure-SshForwarding -VmName "Debian" -RuleName "logminer-ssh-debian" -HostPort $DebianSshPort
    Ensure-SshForwarding -VmName "Ubuntu" -RuleName "logminer-ssh-ubuntu" -HostPort $UbuntuSshPort
}

if ($EnqueueDemo) {
    python scripts\logminer_intelligent_agent_worker.py `
        --redis-url $HostRedisUrl `
        --event-stream logminer:events `
        --task-stream $TaskStream `
        --group $Group `
        --run-id $RunId `
        --consumer windows-seeder `
        --agent-id windows-seeder `
        --enqueue-demo `
        --enqueue-only `
        --cycles 1
    if ($LASTEXITCODE -ne 0) {
        throw "L'enfilement de demonstration a echoue."
    }
}

foreach ($vm in $VmNames) {
    $cred = Get-VmCredential -VmName $vm
    $guestPython = Get-VmPython -VmName $vm
    $consumer = ($vm.ToLowerInvariant() + "-worker-1")
    $guestCommand = "cd $RepoPathInGuest && LOGMINER_REDIS_URL='$GuestRedisUrl' $guestPython scripts/logminer_intelligent_agent_worker.py --redis-url '$GuestRedisUrl' --event-stream logminer:events --task-stream '$TaskStream' --group '$Group' --run-id '$RunId' --consumer '$consumer' --agent-id '$consumer' --cycles 20 --claim-idle-ms 30000 --memory data/processed/$consumer-memory.json"

    if ($RunGuestWorkers -and $cred) {
        Invoke-VBox -CommandArgs @(
            "guestcontrol", $vm, "run",
            "--username", $cred.User,
            "--password=$($cred.Password)",
            "--exe", "/bin/bash",
            "--", "-lc", $guestCommand
        )
    } elseif ($cred) {
        Write-Host ""
        Write-Host "Identifiants fournis pour ${vm}. Ajoutez -RunGuestWorkers pour executer via VBoxManage guestcontrol."
        Write-Host "Commande a executer dans ${vm}:"
        Write-Host $guestCommand
    } else {
        Write-Host ""
        Write-Host "Commande a executer dans ${vm}:"
        Write-Host $guestCommand
    }
}

Write-Host ""
Write-Host "Verification Redis:"
Write-Host "docker exec logminer-redis redis-cli XPENDING $TaskStream $Group"
Write-Host "python -B -c `"import sys,json; sys.path.insert(0, r'src\logminer'); import api; print(json.dumps(api.agents_status(count=1000), ensure_ascii=False, indent=2))`""
