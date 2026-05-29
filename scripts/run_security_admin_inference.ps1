param(
    [string]$ProjectRoot = "F:\Cours\TFE"
)

$ErrorActionPreference = "Stop"

Set-Location $ProjectRoot

$rawDir = Join-Path $ProjectRoot "data\raw\windows_events_admin"
$processedDir = Join-Path $ProjectRoot "data\processed"
$logPath = Join-Path $processedDir "security_admin_run.log"

New-Item -ItemType Directory -Force $rawDir | Out-Null
New-Item -ItemType Directory -Force $processedDir | Out-Null

Start-Transcript -Path $logPath -Force | Out-Null

try {
    Write-Host "Export Security.evtx..."
    wevtutil epl Security (Join-Path $rawDir "Security.evtx")

    Write-Host "Parse Security.evtx..."
    python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'data\raw\windows_events_admin\Security.evtx', r'data\processed', 'windows_security_pipeline.csv', debug=True))"

    Write-Host "Detection anomalies avec modele Colab..."
    python src\logminer\agents\detector.py `
        -i data\processed\windows_security_pipeline.csv `
        -o data\processed\anomalies_security_colab_model.csv `
        --model-in models\isolation_forest_colab.joblib

    Write-Host "Correlation incidents..."
    python src\logminer\agents\correlator.py `
        -i data\processed\anomalies_security_colab_model.csv `
        -o data\processed\incidents_security_colab_model.csv

    Write-Host "Resume rapide..."
    python -c "import pandas as pd; a=pd.read_csv(r'data\processed\anomalies_security_colab_model.csv', sep=';', dtype=str, keep_default_na=False); i=pd.read_csv(r'data\processed\incidents_security_colab_model.csv', sep=';', dtype=str, keep_default_na=False); print('Evenements analyses:', len(a)); print('Anomalies candidates:', int((a['is_anomaly'].astype(str)=='1').sum())); print('Incidents correles:', len(i))"
}
finally {
    Stop-Transcript | Out-Null
}
