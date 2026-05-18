param(
    # Repertoire officiel ou Windows stocke les journaux .evtx actifs.
    [string]$LogDirectory = "C:\Windows\System32\winevt\Logs",

    # Fenetre de collecte des evenements recents.
    [int]$Days = 2,

    # Dossier ou placer les copies .evtx exportees avec wevtutil.
    [string]$RawDirectory = "data\raw\windows_events",

    # Dossier des CSV produits.
    [string]$OutputDirectory = "data\processed",

    # Journaux Windows a copier avant parsing Logminer.
    [string[]]$CopyLogs = @("Application", "System", "Security"),

    # Nom du CSV Logminer produit depuis les copies .evtx.
    [string]$PipelineOutputName = "windows_copies_pipeline.csv",

    # Permet de relancer seulement une partie du workflow.
    [switch]$SkipRecentExport,
    [switch]$SkipCopyExport,
    [switch]$SkipPipeline
)

$ErrorActionPreference = "Continue"

function Resolve-ProjectPath {
    param([string]$Path)

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }

    return (Join-Path (Get-Location) $Path)
}

function Count-CsvRows {
    param(
        [string]$Path,
        [char]$Delimiter = ','
    )

    if (-not (Test-Path $Path)) {
        return 0
    }

    try {
        return @((Import-Csv -Path $Path -Delimiter $Delimiter)).Count
    }
    catch {
        return 0
    }
}

$rawDir = Resolve-ProjectPath $RawDirectory
$outDir = Resolve-ProjectPath $OutputDirectory
$summaryPath = Join-Path $outDir "windows_collection_summary.txt"
$recentScript = Join-Path (Get-Location) "scripts\export_recent_windows_events.ps1"
$pipelineCsv = Join-Path $outDir $PipelineOutputName
$pipelineInputDir = $rawDir

New-Item -ItemType Directory -Path $rawDir -Force | Out-Null
New-Item -ItemType Directory -Path $outDir -Force | Out-Null

$summary = New-Object System.Collections.Generic.List[string]
$summary.Add("Windows Event collection summary")
$summary.Add("Run time: $(Get-Date -Format s)")
$summary.Add("Log directory: $LogDirectory")
$summary.Add("Days: $Days")
$summary.Add("")

if (-not $SkipRecentExport) {
    Write-Host "== Export des evenements recents via Get-WinEvent =="

    & powershell -ExecutionPolicy Bypass -File $recentScript `
        -LogDirectory $LogDirectory `
        -Days $Days `
        -OutputDirectory $outDir

    $recentExitCode = $LASTEXITCODE
    $recentEventsPath = Join-Path $outDir "windows_recent_events.csv"
    $recentFailuresPath = Join-Path $outDir "windows_recent_failures.csv"
    $recentManifestPath = Join-Path $outDir "windows_recent_manifest.csv"

    $recentRows = Count-CsvRows -Path $recentEventsPath -Delimiter ';'
    $recentFailures = Count-CsvRows -Path $recentFailuresPath
    $recentSelected = Count-CsvRows -Path $recentManifestPath

    $summary.Add("Recent export:")
    $summary.Add("- exit_code: $recentExitCode")
    $summary.Add("- selected_evtx_files: $recentSelected")
    $summary.Add("- exported_events: $recentRows")
    $summary.Add("- failures_or_empty_logs: $recentFailures")
    $summary.Add("- events_csv: $recentEventsPath")
    $summary.Add("- failures_csv: $recentFailuresPath")
    $summary.Add("")
}

if (-not $SkipCopyExport) {
    Write-Host "== Export des copies EVTX avec wevtutil =="

    $copyResults = New-Object System.Collections.Generic.List[object]
    $copyRunDir = Join-Path $rawDir (Get-Date -Format "yyyyMMdd_HHmmss")
    New-Item -ItemType Directory -Path $copyRunDir -Force | Out-Null
    $pipelineInputDir = $copyRunDir

    foreach ($logName in $CopyLogs) {
        $safeFileName = ($logName -replace '[\\/:*?"<>|]', '_') + ".evtx"
        $destination = Join-Path $copyRunDir $safeFileName

        Write-Host "Copie du journal $logName -> $destination"

        & wevtutil epl $logName $destination
        $copyExitCode = $LASTEXITCODE

        if ($copyExitCode -eq 0 -and (Test-Path $destination)) {
            $item = Get-Item $destination
            $copyResults.Add([pscustomobject]@{
                LogName = $logName
                Destination = $destination
                Status = "OK"
                SizeBytes = $item.Length
                Error = ""
            })
        }
        else {
            $copyResults.Add([pscustomobject]@{
                LogName = $logName
                Destination = $destination
                Status = "FAILED"
                SizeBytes = 0
                Error = "wevtutil exit code $copyExitCode"
            })
        }
    }

    $copyReportPath = Join-Path $outDir "windows_evtx_copy_report.csv"
    $copyResults | Export-Csv -Path $copyReportPath -NoTypeInformation -Encoding UTF8

    $copyOk = @($copyResults | Where-Object { $_.Status -eq "OK" }).Count
    $copyFailed = @($copyResults | Where-Object { $_.Status -ne "OK" }).Count

    $summary.Add("EVTX copies:")
    $summary.Add("- requested_logs: $($CopyLogs -join ', ')")
    $summary.Add("- copied: $copyOk")
    $summary.Add("- failed: $copyFailed")
    $summary.Add("- copy_report: $copyReportPath")
    $summary.Add("- raw_directory: $copyRunDir")
    $summary.Add("")
}

if (-not $SkipPipeline) {
    Write-Host "== Parsing Logminer des copies EVTX =="

    if ($SkipCopyExport) {
        $latestRunDir = Get-ChildItem -Path $rawDir -Directory -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

        if ($latestRunDir) {
            $pipelineInputDir = $latestRunDir.FullName
        }
    }

    $evtxCopies = @(Get-ChildItem -Path $pipelineInputDir -Filter "*.evtx" -File -ErrorAction SilentlyContinue)

    if ($evtxCopies.Count -eq 0) {
        Write-Warning "Aucune copie .evtx trouvee dans $rawDir; parsing ignore."
        $summary.Add("Pipeline:")
        $summary.Add("- status: skipped")
        $summary.Add("- reason: no .evtx copy found")
    }
    else {
        $pythonCode = @"
import sys
sys.path.insert(0, r'src\logminer')
import pipeline
print(pipeline.run_pipeline(r'$pipelineInputDir', r'$outDir', r'$PipelineOutputName', debug=True))
"@

        python -c $pythonCode
        $pipelineExitCode = $LASTEXITCODE
        $pipelineRows = Count-CsvRows -Path $pipelineCsv -Delimiter ';'

        $summary.Add("Pipeline:")
        $summary.Add("- exit_code: $pipelineExitCode")
        $summary.Add("- input_directory: $pipelineInputDir")
        $summary.Add("- parsed_events: $pipelineRows")
        $summary.Add("- output_csv: $pipelineCsv")
    }
}

$summary | Set-Content -Path $summaryPath -Encoding UTF8

Write-Host ""
Write-Host "Resume: $summaryPath"
Get-Content $summaryPath
