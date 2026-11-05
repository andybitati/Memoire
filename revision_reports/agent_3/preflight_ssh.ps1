$ErrorActionPreference = "Continue"
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$plink = "C:\Program Files\PuTTY\plink.exe"
Add-Type -AssemblyName System.Security
foreach ($item in @(@{Vm="Debian";Port=2222}, @{Vm="Ubuntu";Port=2223})) {
    $path = Join-Path $projectRoot (".secrets\" + $item.Vm.ToLowerInvariant() + "_vm.credential.json")
    $record = Get-Content -LiteralPath $path -Raw -Encoding utf8 | ConvertFrom-Json
    $encrypted = [Convert]::FromBase64String($record.encrypted_password)
    $plainBytes = [Security.Cryptography.ProtectedData]::Unprotect($encrypted, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser)
    $password = [Text.Encoding]::UTF8.GetString($plainBytes)
    & $plink -batch -P $item.Port -pw $password ($record.username + "@127.0.0.1") "hostname; python3 --version; python3 -c 'import socket; s=socket.create_connection((\"10.0.2.2\",6379),5); print(\"redis_tcp_ok\"); s.close()'"
    Write-Output ("EXIT " + $item.Vm + " " + $LASTEXITCODE)
}
