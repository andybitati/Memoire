# TFE - Détection d'anomalies dans les journaux systèmes et réseaux

Ce dépôt accompagne le mémoire:

**Détection Autonome et Distribuée d'Anomalies dans les Journaux Systèmes et Réseaux à l'aide d'Agents Intelligents Multi-Tâches**.

Le but est de construire progressivement un système capable de collecter des journaux hétérogènes, les parser, les normaliser, puis les préparer pour des agents IA de détection d'anomalies.

## Structure Du Projet

```text
TFE/
├── README.md
├── requirements.txt
├── src/
│   └── logminer/
├── docs/
│   ├── anomaly_detection/
│   ├── architecture/
│   ├── memoire/
│   ├── references/
│   └── recovery/
├── examples/
├── scripts/
├── data/
│   ├── raw/
│   ├── processed/
│   └── samples/
└── archive/
    └── recovery_artifacts/
```

Rôles des dossiers:

- `src/logminer/`: code principal du pipeline de prétraitement des logs.
- `docs/anomaly_detection/`: étude comparative liée à l'objectif 2.
- `docs/architecture/`: conception de l'architecture multi-agents IA liée à l'objectif 3.
- `docs/memoire/`: documents liés au mémoire.
- `docs/references/`: articles, normes et PDF de référence.
- `docs/recovery/`: notes sur la récupération des fichiers `.py` depuis les `.pyc`.
- `examples/`: petits fichiers d'exemple pour tester rapidement le code.
- `scripts/`: scripts utilitaires, par exemple extraction de texte PDF.
- `data/raw/`: datasets bruts volumineux, non versionnés.
- `data/processed/`: sorties de prétraitement, non versionnées.
- `data/samples/`: petits échantillons locaux de test.
- `archive/recovery_artifacts/`: artefacts de récupération à garder localement si nécessaire.

## Installation

Créer ou activer un environnement Python, puis installer les dépendances:

```powershell
python -m pip install -r requirements.txt
```

La dépendance `python-evtx` sert uniquement à lire les fichiers Windows `.evtx`. Si elle pose problème, il est possible d'exporter les journaux Windows en XML et de les traiter sans dépendance supplémentaire.

Les expériences deep learning de l'objectif 2 sont séparées pour éviter une installation de base trop lourde:

```powershell
python -m pip install -r requirements-ai.txt
```

TensorFlow/Keras est privilégié pour le LSTM. PyTorch est aussi intégré comme backend de secours expérimental.

## Logminer

`src/logminer` est la brique de prétraitement du mémoire. Elle couvre principalement:

- Agent 1: collecte et parsing des logs.
- Agent 2: prétraitement et normalisation.

La conception globale des agents est documentée dans `docs/architecture/README.md`.

Flux général:

```text
logs bruts -> détection du format -> parseur spécialisé -> CSV normalisé -> modèles IA/dashboard
```

### Composants

- `pipeline.py`: orchestre le traitement complet d'un fichier ou dossier.
- `detectors/file_detector.py`: détecte le format d'un log (`syslog`, `win_event`, `apache`, `hdfs`, `bgl`, `pcap`, etc.).
- `io/csv_writer.py`: écrit un CSV conforme au schéma commun.
- `schema/columns.py`: définit les colonnes normalisées.
- `parsers/`: contient les parseurs spécialisés par format.
- `normalizers/`: prépare l'harmonisation des sévérités et la catégorisation sécurité.
- `writer.py`: compatibilité avec les parseurs récupérés qui importent `emit`.

## Utiliser Le Pipeline

Tester avec l'exemple Windows Event fourni:

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'examples\windows_event_sample.xml', r'data\processed', 'windows_events.csv', debug=True))"
```

Sortie attendue:

```text
data/processed/windows_events.csv
```

Traiter un fichier unique:

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'chemin\vers\fichier.log', r'data\processed', 'dataset.csv', debug=True))"
```

Traiter un dossier:

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'data\raw', r'data\processed', 'dataset.csv', debug=True))"
```

## Tester La Détection De Format

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); from detectors.file_detector import detect_kind; print(detect_kind(r'examples\windows_event_sample.xml'))"
```

Résultat attendu:

```text
win_event
```

## Utiliser Le Parseur Windows Event

Pour un export XML Windows Event:

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'C:\chemin\security.xml', r'data\processed', 'windows_security.csv', debug=True))"
```

Pour un fichier `.evtx`:

```powershell
python -m pip install python-evtx
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'C:\chemin\Security.evtx', r'data\processed', 'security_evtx.csv', debug=True))"
```

## Vérifier Les Journaux Windows Récents

Le dossier Windows utilisé pour les journaux actifs est:

```text
C:\Windows\System32\winevt\Logs
```

Un script principal a été ajouté pour automatiser toute la collecte Windows. Il:

- sélectionne les fichiers `.evtx` modifiés pendant les derniers jours demandés;
- exporte les événements récents lisibles via `Get-WinEvent`;
- crée des copies `.evtx` des journaux importants avec `wevtutil`;
- lance le pipeline Logminer sur les copies disponibles;
- écrit un résumé d'exécution.

Commande à lancer depuis la racine du projet:

```powershell
cd F:\Cours\TFE
powershell -ExecutionPolicy Bypass -File scripts\collect_windows_events.ps1 -Days 2
```

Fichiers produits:

- `data/processed/windows_recent_manifest.csv`: liste des fichiers `.evtx` sélectionnés, avec leur date, taille et nom logique Windows.
- `data/processed/windows_recent_events.csv`: événements extraits, au format CSV avec séparateur `;`.
- `data/processed/windows_recent_failures.csv`: journaux non lus et raison de l'échec.
- `data/processed/windows_evtx_copy_report.csv`: résultat des copies `.evtx` faites avec `wevtutil`.
- `data/processed/windows_copies_pipeline.csv`: CSV normalisé produit par Logminer depuis les copies `.evtx`.
- `data/processed/windows_collection_summary.txt`: résumé de l'exécution.

Par défaut, le script tente de copier `Application`, `System` et `Security` dans `data/raw/windows_events/`. Si `Security` échoue avec `Accès refusé`, relancer la même commande depuis PowerShell ouvert en administrateur.

Pour choisir explicitement les journaux à copier:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\collect_windows_events.ps1 -Days 2 -CopyLogs Application,System,Security
```

Pour relancer uniquement le parsing des copies déjà présentes:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\collect_windows_events.ps1 -SkipRecentExport -SkipCopyExport
```

Lors de la vérification du 15/05/2026, le script a sélectionné `114` fichiers `.evtx` modifiés dans les deux derniers jours. Il a exporté `23402` événements lisibles depuis `95` journaux. `19` journaux ont demandé des droits administrateur ou un accès Windows plus élevé.

Exemples de journaux protégés rencontrés:

- `Security.evtx`
- `Microsoft-Windows-GroupPolicy%4Operational.evtx`
- `Microsoft-Windows-SMBServer%4Operational.evtx`
- `Microsoft-Windows-SMBClient%4Operational.evtx`
- `Microsoft-Windows-Hyper-V-Hypervisor-Admin.evtx`

Ces fichiers ne doivent pas être ignorés: ils sont importants pour la sécurité. Pour les exploiter, ouvrir PowerShell en administrateur et relancer `scripts\collect_windows_events.ps1`; le script copiera les journaux protégés dans `data/raw/windows_events/`, puis traitera les copies.

Exemple prévu pour plus tard, en console administrateur:

```powershell
cd F:\Cours\TFE
New-Item -ItemType Directory -Force data\raw\windows_events
wevtutil epl Security data\raw\windows_events\Security.evtx
wevtutil epl System data\raw\windows_events\System.evtx
wevtutil epl Application data\raw\windows_events\Application.evtx
```

Ensuite, les copies pourront être analysées directement avec le pipeline Python ou en relançant `scripts\collect_windows_events.ps1 -SkipRecentExport -SkipCopyExport`.

## Extraire Le Texte D'un PDF

```powershell
python scripts\extract_pdf.py docs\memoire\mon_memoire.pdf
```

Si aucun PDF n'est donné, le script utilise le premier PDF trouvé dans `docs/memoire`.

## Données Produites

Les CSV produits suivent le schéma de `src/logminer/schema/columns.py`.

Colonnes importantes:

- `timestamp_iso`
- `severity`
- `event`
- `source`
- `host`
- `user`
- `src_ip`, `dst_ip`, `src_port`, `dst_port`
- `http_method`, `http_url`, `http_status`
- `category`, `subcategory`
- `message`

Ces données serviront ensuite à l'entraînement ou au test de méthodes statistiques et IA: z-score, IQR, histogramme, Isolation Forest, k-Means, Autoencoder, One-Class SVM, LOF ou LSTM léger.

La comparaison des approches de détection est documentée dans `docs/anomaly_detection/README.md`.

## Détecter Les Anomalies

Un premier agent de détection non supervisé est disponible avec Isolation Forest. Il lit un CSV normalisé Logminer, construit des features ML, puis produit un fichier enrichi avec `anomaly_score`, `is_anomaly` et `anomaly_rank`.

```powershell
python src\logminer\agents\detector.py -i data\processed\windows_copies_pipeline.csv -o data\processed\anomalies.csv
```

La conversion en variables ML se trouve dans `src/logminer/features/event_features.py`.

Pour comparer les approches de l'objectif 2:

```powershell
python src\logminer\agents\baseline_detector.py -i data\processed\windows_copies_pipeline.csv -o data\processed\baseline_anomalies.csv --contamination 0.02
python src\logminer\agents\model_compare.py -i data\processed\windows_copies_pipeline.csv -o data\processed\model_comparison.csv --contamination 0.02
```

Le comparateur `model_compare.py` produit une grille expérimentale complète pour le mémoire: baseline explicable, méthodes statistiques (`z_score`, `iqr`, `histogram`) et méthodes IA non supervisées (`isolation_forest`, `kmeans`, `one_class_svm`, `local_outlier_factor`, `autoencoder_mlp`, `lstm`). Le LSTM utilise TensorFlow/Keras en priorité, puis PyTorch si TensorFlow n'est pas disponible. Il sera ignoré automatiquement si aucun backend deep learning n'est installé.

## Communication Entre Agents

Les agents disponibles communiquent avec un bus local JSONL. Chaque étape publie un message dans `data/processed/agent_messages.jsonl`: lancement du workflow, parsing terminé, détection lancée, détection terminée, etc.

Commande d'orchestration locale:

```powershell
python src\logminer\agents\orchestrator.py -i examples\windows_event_sample.xml --parsed-name orchestrated_windows.csv --anomalies-name orchestrated_anomalies.csv
```

Pour les journaux Windows, `scripts\collect_windows_events.ps1` lance aussi la détection après le parsing, sauf si `-SkipDetection` est fourni.

## Corréler Et Visualiser

L'agent corrélateur regroupe les anomalies candidates en incidents:

```powershell
python src\logminer\agents\correlator.py -i data\processed\anomalies.csv -o data\processed\incidents.csv
```

Le dashboard Streamlit lit les événements, anomalies, incidents et messages d'agents:

```powershell
streamlit run src\logminer\agents\dashboard.py
```

Une version React plus responsive est disponible dans `web/dashboard`. Elle utilise un petit serveur Node natif pour exposer les CSV de `data/processed` en JSON.

```powershell
cd web\dashboard
npm run dev
```

URL locale:

```text
http://127.0.0.1:5173
```

## État Actuel

Le code a été récupéré depuis des fichiers `.pyc`, puis réorganisé.

Déjà réparé et utilisable:

- `src/logminer/pipeline.py`
- `src/logminer/detectors/file_detector.py`
- `src/logminer/io/csv_writer.py`
- `src/logminer/parsers/windows_event.py`
- `src/logminer/writer.py`
- `src/logminer/normalizers/runner.py`
- `src/logminer/normalizers/categorizer.py`
- `src/logminer/features/event_features.py`
- `src/logminer/agents/baseline_detector.py`
- `src/logminer/agents/detector.py`
- `src/logminer/agents/model_compare.py`
- `src/logminer/agents/correlator.py`
- `src/logminer/agents/dashboard.py`
- `src/logminer/agents/bus.py`
- `src/logminer/agents/parser_agent.py`
- `src/logminer/agents/orchestrator.py`
- `web/dashboard/`
- `scripts/export_recent_windows_events.ps1`
- `scripts/process_recent_windows_events.py`

Avancées du 15/05/2026:

- réorganisation du dépôt autour de `src/`, `docs/`, `scripts/`, `data/` et `archive/`;
- ajout de `requirements.txt`;
- ajout d'un script PowerShell pour vérifier les journaux Windows récents;
- vérification réelle sur `C:\Windows\System32\winevt\Logs` avec uniquement les fichiers des deux derniers jours;
- production de CSV dans `data/processed`;
- identification claire des journaux qui exigent une console administrateur;
- décision de traiter ces journaux protégés plus tard par copie/export administrateur.

À compléter/réparer ensuite:

- certains parseurs récupérés dans `src/logminer/parsers/`;
- tests sur HDFS, BGL, Apache, Syslog et EVTX réel.
- copie/export des journaux Windows protégés en mode administrateur.

## Prochaines Étapes

- Exporter les journaux Windows protégés avec une console administrateur.
- Stabiliser tous les parseurs.
- Améliorer la catégorisation sécurité avec plus de règles.
- Ajouter un agent de corrélation temporelle.
- Construire un dashboard simple de visualisation des anomalies.
