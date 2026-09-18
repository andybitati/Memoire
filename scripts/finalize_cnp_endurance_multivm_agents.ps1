param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^cnp_endurance_multivm_\d{8}T\d{6}Z$')]
    [string]$RunId,

    [string]$VBoxManagePath = "C:\Program Files\Oracle\VirtualBox\VBoxManage.exe"
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$hostLogDirectory = Join-Path $projectRoot "experiments\phase_cnp_endurance\logs"
New-Item -ItemType Directory -Path $hostLogDirectory -Force | Out-Null

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

$profiles = @(
    [pscustomobject]@{ Vm = "Debian"; AgentId = "debian-alpha" },
    [pscustomobject]@{ Vm = "Ubuntu"; AgentId = "ubuntu-beta" }
)

foreach ($profile in $profiles) {
    $credential = Get-LocalVmCredential -VmName $profile.Vm
    $guestLog = "/tmp/$RunId`__$($profile.AgentId).log"
    $hostLog = Join-Path $hostLogDirectory "$RunId`__$($profile.AgentId).log"

    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $VBoxManagePath guestcontrol $credential.Vm copyfrom `
        --username $credential.User `
        --password="$($credential.Password)" `
        $guestLog `
        $hostLog
    $copyExitCode = $LASTEXITCODE

    & $VBoxManagePath guestcontrol $credential.Vm run `
        --username $credential.User `
        --password="$($credential.Password)" `
        --exe /bin/bash `
        -- -lc "pkill -f '[l]ogminer_redis_cnp_agent.py' || true"
    $stopExitCode = $LASTEXITCODE
    $ErrorActionPreference = $previousPreference

    if ($copyExitCode -ne 0) {
        throw "Impossible de recuperer le journal de $($profile.Vm)"
    }
    if ($stopExitCode -ne 0) {
        throw "Impossible d'arreter l'agent sur $($profile.Vm)"
    }
    Write-Output ("FINALIZED " + $profile.Vm + " log=" + $hostLog)
}
