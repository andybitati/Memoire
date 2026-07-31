param(
    [string]$TaskName = "LogminerMonthlyRetraining",
    [int]$DayOfMonth = 1,
    [string]$At = "02:00",
    [switch]$Promote
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$runner = Join-Path $root "scripts\run_monthly_retraining.ps1"
$runnerArgs = "-NoProfile -ExecutionPolicy Bypass -File `"$runner`""
if ($Promote) {
    $runnerArgs += " -Promote"
}

$taskCommand = "powershell.exe $runnerArgs"
& schtasks.exe /Create `
    /TN $TaskName `
    /TR $taskCommand `
    /SC MONTHLY `
    /D $DayOfMonth `
    /ST $At `
    /F | Out-Null

if ($LASTEXITCODE -ne 0) {
    throw "schtasks.exe failed with exit code $LASTEXITCODE"
}

Write-Host "Tache planifiee installee: $TaskName"
Write-Host "Planification: jour $DayOfMonth a $At"
Write-Host "Promotion automatique: $Promote"
