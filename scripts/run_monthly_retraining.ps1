param(
    [switch]$Promote,
    [string]$Plan = "docs\model_training\monthly_retraining_plan.example.json"
)

$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$logDir = Join-Path $root "data\processed\monthly"
$logPath = Join-Path $logDir "monthly_retraining_task.log"
New-Item -ItemType Directory -Path $logDir -Force | Out-Null

$arguments = @(
    "scripts\monthly_model_retraining.py",
    "--plan",
    $Plan,
    "--report-out",
    "data\processed\monthly\monthly_retraining_report.json"
)
if ($Promote) {
    $arguments += "--promote"
}

Push-Location $root
try {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] Starting monthly retraining. Promote=$Promote"
    & python @arguments 2>&1 | Tee-Object -FilePath $logPath -Append
    if ($LASTEXITCODE -ne 0) {
        throw "monthly_model_retraining.py failed with exit code $LASTEXITCODE"
    }
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Add-Content -Path $logPath -Value "[$timestamp] Completed monthly retraining."
}
finally {
    Pop-Location
}
