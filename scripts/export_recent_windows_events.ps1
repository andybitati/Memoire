param(
    # Repertoire officiel ou Windows stocke les journaux .evtx actifs.
    [string]$LogDirectory = "C:\Windows\System32\winevt\Logs",

    # Fenetre de verification demandee: uniquement les fichiers modifies
    # pendant les derniers jours indiques.
    [int]$Days = 2,

    # Dossier de sortie du projet.
    [string]$OutputDirectory = "data\processed"
)

$ErrorActionPreference = "Continue"

# Date limite: seuls les fichiers .evtx modifies apres cette date sont pris.
$startTime = (Get-Date).AddDays(-$Days)

# Les fichiers .evtx actifs ne sont pas toujours lisibles directement par
# chemin. On les utilise donc comme point de depart, puis on passe par
# l'API Windows Event Log avec le nom logique du journal.
$recentFiles = Get-ChildItem -Path $LogDirectory -Filter "*.evtx" |
    Where-Object { $_.LastWriteTime -ge $startTime } |
    Sort-Object LastWriteTime -Descending

New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null

$manifestPath = Join-Path $OutputDirectory "windows_recent_manifest.csv"
$eventsPath = Join-Path $OutputDirectory "windows_recent_events.csv"
$failuresPath = Join-Path $OutputDirectory "windows_recent_failures.csv"

# Cette liste officielle donne la correspondance entre un fichier .evtx et
# le nom du journal a utiliser avec Get-WinEvent -LogName.
$knownLogs = Get-WinEvent -ListLog * -ErrorAction SilentlyContinue |
    Where-Object { $_.LogFilePath } |
    Select-Object LogName, LogFilePath, RecordCount, IsEnabled

$manifest = foreach ($file in $recentFiles) {
    $matchedLog = $knownLogs | Where-Object {
        [System.IO.Path]::GetFileName($_.LogFilePath) -ieq $file.Name
    } | Select-Object -First 1

    [pscustomobject]@{
        FileName      = $file.Name
        FullName      = $file.FullName
        LastWriteTime = $file.LastWriteTime
        Length        = $file.Length
        LogName       = if ($matchedLog) { $matchedLog.LogName } else { "" }
        RecordCount   = if ($matchedLog) { $matchedLog.RecordCount } else { "" }
        IsEnabled     = if ($matchedLog) { $matchedLog.IsEnabled } else { "" }
    }
}

$manifest | Export-Csv -Path $manifestPath -NoTypeInformation -Encoding UTF8

$allEvents = New-Object System.Collections.Generic.List[object]
$failures = New-Object System.Collections.Generic.List[object]

foreach ($item in $manifest) {
    if ([string]::IsNullOrWhiteSpace($item.LogName)) {
        $failures.Add([pscustomobject]@{
            FileName = $item.FileName
            LogName  = ""
            Error    = "Nom logique du journal introuvable"
        })
        continue
    }

    try {
        # On lit uniquement les evenements recents du journal correspondant.
        $events = Get-WinEvent -FilterHashtable @{
            LogName   = $item.LogName
            StartTime = $startTime
        } -ErrorAction Stop

        foreach ($event in $events) {
            $allEvents.Add([pscustomobject]@{
                SourceFile       = $item.FileName
                LogName          = $item.LogName
                TimeCreated      = $event.TimeCreated
                EventId          = $event.Id
                ProviderName     = $event.ProviderName
                LevelDisplayName = $event.LevelDisplayName
                MachineName      = $event.MachineName
                Message          = ($event.Message -replace "\r?\n", " ")
            })
        }
    }
    catch {
        $failures.Add([pscustomobject]@{
            FileName = $item.FileName
            LogName  = $item.LogName
            Error    = $_.Exception.Message
        })
    }
}

$allEvents | Export-Csv -Path $eventsPath -NoTypeInformation -Encoding UTF8 -Delimiter ";"
$failures | Export-Csv -Path $failuresPath -NoTypeInformation -Encoding UTF8

Write-Host "Fichiers .evtx selectionnes: $($recentFiles.Count)"
Write-Host "Journaux exportes avec evenements: $(($allEvents | Select-Object -ExpandProperty LogName -Unique).Count)"
Write-Host "Evenements exportes: $($allEvents.Count)"
Write-Host "Echecs: $($failures.Count)"
Write-Host "Manifest: $((Resolve-Path $manifestPath).Path)"
Write-Host "Evenements: $((Resolve-Path $eventsPath).Path)"
Write-Host "Echecs: $((Resolve-Path $failuresPath).Path)"

if ($failures.Count -gt 0) {
    exit 1
}
