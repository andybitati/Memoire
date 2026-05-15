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

## Logminer

`src/logminer` est la brique de prétraitement du mémoire. Elle couvre principalement:

- Agent 1: collecte et parsing des logs.
- Agent 2: prétraitement et normalisation.

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

Un script a été ajouté pour travailler avec ce dossier sans prendre tous les journaux du système. Il sélectionne uniquement les fichiers `.evtx` modifiés pendant les deux derniers jours, puis exporte les événements lisibles vers `data/processed`.

Commande à lancer depuis la racine du projet:

```powershell
cd F:\Cours\TFE
powershell -ExecutionPolicy Bypass -File scripts\export_recent_windows_events.ps1 -Days 2
```

Fichiers produits:

- `data/processed/windows_recent_manifest.csv`: liste des fichiers `.evtx` sélectionnés, avec leur date, taille et nom logique Windows.
- `data/processed/windows_recent_events.csv`: événements extraits, au format CSV avec séparateur `;`.
- `data/processed/windows_recent_failures.csv`: journaux non lus et raison de l'échec.

Lors de la vérification du 15/05/2026, le script a sélectionné `114` fichiers `.evtx` modifiés dans les deux derniers jours. Il a exporté `23402` événements lisibles depuis `95` journaux. `19` journaux ont demandé des droits administrateur ou un accès Windows plus élevé.

Exemples de journaux protégés rencontrés:

- `Security.evtx`
- `Microsoft-Windows-GroupPolicy%4Operational.evtx`
- `Microsoft-Windows-SMBServer%4Operational.evtx`
- `Microsoft-Windows-SMBClient%4Operational.evtx`
- `Microsoft-Windows-Hyper-V-Hypervisor-Admin.evtx`

Ces fichiers ne doivent pas être ignorés: ils sont importants pour la sécurité. Pour les exploiter plus tard, il faudra ouvrir PowerShell en administrateur et copier/exporter les journaux protégés dans `data/raw/windows_events/`, puis traiter les copies.

Exemple prévu pour plus tard, en console administrateur:

```powershell
cd F:\Cours\TFE
New-Item -ItemType Directory -Force data\raw\windows_events
wevtutil epl Security data\raw\windows_events\Security.evtx
wevtutil epl System data\raw\windows_events\System.evtx
wevtutil epl Application data\raw\windows_events\Application.evtx
```

Ensuite, les copies pourront être analysées avec le pipeline Python ou avec un script dédié.

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

Ces données serviront ensuite à l'entraînement ou au test de modèles comme Isolation Forest, Autoencoder, One-Class SVM ou LSTM léger.

## État Actuel

Le code a été récupéré depuis des fichiers `.pyc`, puis réorganisé.

Déjà réparé et utilisable:

- `src/logminer/pipeline.py`
- `src/logminer/detectors/file_detector.py`
- `src/logminer/io/csv_writer.py`
- `src/logminer/parsers/windows_event.py`
- `src/logminer/writer.py`
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
- `src/logminer/normalizers/categorizer.py`;
- `src/logminer/normalizers/runner.py`;
- tests sur HDFS, BGL, Apache, Syslog et EVTX réel.
- copie/export des journaux Windows protégés en mode administrateur.

## Prochaines Étapes

- Exporter les journaux Windows protégés avec une console administrateur.
- Stabiliser tous les parseurs.
- Finaliser la catégorisation sécurité.
- Générer des features ML depuis les CSV.
- Ajouter un premier modèle Isolation Forest.
- Construire un dashboard simple de visualisation des anomalies.
