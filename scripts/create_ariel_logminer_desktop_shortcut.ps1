param(
    [string]$ShortcutName = "Ariel Logminer"
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$launcher = Join-Path $root "scripts\launch_logminer_app.cmd"
$icon = Join-Path $root "web\dashboard\ariel_logminer_icon.ico"
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "$ShortcutName.lnk"

if (-not (Test-Path $launcher)) {
    throw "Lanceur introuvable: $launcher"
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $launcher
$shortcut.WorkingDirectory = $root
$shortcut.Description = "Lancer Ariel Logminer: API, dashboard et agents intelligents"
if (Test-Path $icon) {
    $shortcut.IconLocation = "$icon,0"
}
$shortcut.Save()

Write-Host "Raccourci cree ou mis a jour: $shortcutPath"
