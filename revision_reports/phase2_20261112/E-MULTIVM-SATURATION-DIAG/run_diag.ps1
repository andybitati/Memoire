# Orchestration d'E-MULTIVM-SATURATION-DIAG : trois bras exécutés l'un après l'autre.
# Usage : powershell -File run_diag.ps1
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$root = (Resolve-Path (Join-Path $here "..\..\..")).Path
Set-Location $root
$env:PYTHONIOENCODING = "utf-8"
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$outDir = "experiments/phase_revision_20261112/E-MULTIVM-SATURATION-DIAG"
$arms = @(
    @{Name="both";   Vms=@("Debian","Ubuntu"); Agents="debian-alpha,ubuntu-beta"; Single=$false},
    @{Name="debian"; Vms=@("Debian");          Agents="debian-alpha";             Single=$true},
    @{Name="ubuntu"; Vms=@("Ubuntu");          Agents="ubuntu-beta";              Single=$true}
)
$runIds = @()
foreach ($arm in $arms) {
    $runId = "e_multivm_diag_$($arm.Name)_$stamp"
    & (Join-Path $here "start_agents.ps1") -RunId $runId -Vms $arm.Vms -IdleTimeoutSec 120
    $pyArgs = @("revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/run_saturation_arm.py",
              "--run-id", $runId, "--agents", $arm.Agents, "--rates", "2,4,8,16,32",
              "--window-sec", "20", "--repetitions", "3", "--threads", "32", "--out-dir", $outDir)
    if ($arm.Single) { $pyArgs += "--allow-single-host" }
    & .\.venv\Scripts\python.exe @pyArgs | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "bras $($arm.Name) en échec" }
    Write-Output "ARM DONE $($arm.Name) $runId"
    $runIds += $runId
}
& .\.venv\Scripts\python.exe "revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/analyse_diag.py" $runIds[0] $runIds[1] $runIds[2]
