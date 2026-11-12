# Orchestration séquentielle des trois politiques d'allocation sur les deux mêmes VM.
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$root = (Resolve-Path (Join-Path $here "..\..\..")).Path
Set-Location $root
$env:PYTHONIOENCODING = "utf-8"
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outDir = "experiments/phase_revision_20261112/E-MULTIVM-DYNAMIC-ALLOCATION"
$policies = @("utility_agent_id", "utility_load", "least_loaded")
$runIds = @()
foreach ($policy in $policies) {
    $slug = $policy.Replace("_", "-")
    $runId = "e_dynamic_$($slug)_$stamp"
    & "revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/start_agents.ps1" `
        -RunId $runId -Vms @("Debian", "Ubuntu") -IdleTimeoutSec 180
    $pyArgs = @(
        (Join-Path $here "run_dynamic_arm.py"),
        "--selection-policy", $policy,
        "--run-id", $runId,
        "--agents", "debian-alpha,ubuntu-beta",
        "--rates", "8,16,32",
        "--window-sec", "15",
        "--repetitions", "3",
        "--threads", "32",
        "--out-dir", $outDir
    )
    & .\.venv\Scripts\python.exe @pyArgs | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Politique $policy en échec" }
    Write-Output "POLICY DONE $policy $runId"
    $runIds += $runId
}
& .\.venv\Scripts\python.exe (Join-Path $here "analyse_dynamic.py") $runIds[0] $runIds[1] $runIds[2]
