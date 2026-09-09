param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("Debian", "Ubuntu")]
    [string]$VM,

    [switch]$RevealPassword
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$credentialPath = Join-Path $projectRoot (".secrets\" + $VM.ToLowerInvariant() + "_vm.credential.json")
if (-not (Test-Path -LiteralPath $credentialPath)) {
    throw "Identifiant local absent : $credentialPath"
}

$record = Get-Content -LiteralPath $credentialPath -Raw -Encoding utf8 | ConvertFrom-Json
Write-Output ("VM : " + $record.vm)
Write-Output ("Utilisateur : " + $record.username)
Write-Output ("Protection : " + $record.protection)

if ($RevealPassword) {
    Add-Type -AssemblyName System.Security
    $encrypted = [Convert]::FromBase64String($record.encrypted_password)
    $plainBytes = [Security.Cryptography.ProtectedData]::Unprotect(
        $encrypted,
        $null,
        [Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    Write-Output ("Mot de passe : " + [Text.Encoding]::UTF8.GetString($plainBytes))
}
