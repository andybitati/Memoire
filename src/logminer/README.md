# Logminer recupere

Logminer est le module de pretraitement du memoire:

> Detection autonome et distribuee d'anomalies dans les journaux systemes et reseaux a l'aide d'agents intelligents multi-taches.

Son role est de transformer des journaux bruts et heterogenes en CSV normalise. Ce CSV devient ensuite utilisable par les futurs agents IA: detection d'anomalies, correlation, tableau de bord, evaluation, etc.

## Role dans l'architecture du memoire

Le memoire prevoit plusieurs agents:

- Agent 1: collecte et parsing des logs.
- Agent 2: pretraitement et normalisation.
- Agent 3: detection d'anomalies.
- Agent 4: correlation contextuelle.
- Agent 5: visualisation des alertes.

Ce dossier couvre surtout les agents 1 et 2.

Flux general:

```text
logs bruts -> pipeline.py -> detection du format -> parseur specialise -> csv_writer.py -> CSV normalise
```

## Fichiers principaux

- `pipeline.py`: orchestre le traitement. Il parcourt un fichier ou dossier, detecte le type de log, charge le parseur adapte, puis ecrit le CSV.
- `detectors/file_detector.py`: detecte le format des fichiers avant parsing. Il expose `detect_kind(path)`, `detect_file(path)` et `iter_files(path)`.
- `io/csv_writer.py`: ecrit les lignes CSV selon le schema commun.
- `schema/columns.py`: definit toutes les colonnes normalisees du dataset.
- `writer.py`: module de compatibilite utilise par les parseurs recuperes.
- `parsers/windows_event.py`: parseur Windows Event XML et EVTX.
- `parsers/*.py`: parseurs specialises: syslog, Apache, HDFS, BGL, tcpdump, JSONL, CEF/LEEF, etc.
- `normalizers/*.py`: normalisation semantique, severite et categories de securite.

## Utilisation rapide

Depuis la racine du projet:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'recovered_pycdc\examples\windows_event_sample.xml', r'recovered_pycdc\examples\out', 'windows_events.csv', debug=True))"
```

Le CSV produit sera par exemple:

```text
recovered_pycdc\examples\out\windows_events.csv
```

## Utiliser un dossier de logs

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'Datasets\logs_bruts', r'Dataset_csv', 'dataset.csv', debug=True))"
```

Le pipeline parcourt le dossier recursivement et tente de detecter chaque fichier.

## Tester seulement la detection de format

Pour savoir quel parseur sera choisi avant de lancer tout le pipeline:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); from detectors.file_detector import detect_kind; print(detect_kind(r'recovered_pycdc\examples\windows_event_sample.xml'))"
```

Pour obtenir le premier fichier exploitable dans un dossier:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); from detectors.file_detector import detect_file; print(detect_file(r'recovered_pycdc\examples'))"
```

## Utiliser un fichier Windows Event XML

Exporter depuis l'observateur d'evenements Windows en XML, puis lancer:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'C:\chemin\security.xml', r'Dataset_csv', 'windows_security.csv', debug=True))"
```

Colonnes importantes produites:

- `timestamp_iso`: date normalisee UTC.
- `severity`: niveau converti en `ERROR`, `WARNING`, `INFO`, etc.
- `event`: EventID Windows.
- `source`: provider Windows.
- `host`: machine.
- `user`: Security/UserID.
- `message`: champs EventData concatenes.

## Utiliser un fichier EVTX

Le parseur EVTX fonctionne seulement si `python-evtx` est installe:

```powershell
python -m pip install python-evtx
```

Puis:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'C:\chemin\Security.evtx', r'Dataset_csv', 'security_evtx.csv', debug=True))"
```

Si l'installation n'est pas possible, exporter le journal en XML depuis Windows Event Viewer.

## Format CSV normalise

Le schema commun est dans `schema/columns.py`.

Exemples de colonnes:

- `dataset`, `subtype`, `filepath`, `lineno`, `recno`
- `timestamp_iso`, `severity`, `event`, `source`, `component`
- `host`, `pid`, `tid`, `user`
- `src_ip`, `src_port`, `dst_ip`, `dst_port`, `proto`
- `http_method`, `http_url`, `http_status`
- `category`, `subcategory`, `message`

Ce format est important pour entrainer ou tester des modeles comme Isolation Forest, Autoencoder, One-Class SVM ou LSTM leger.

## Notes de recuperation

Ces fichiers viennent d'une recuperation `.pyc -> .py`.

Les fichiers suivants ont ete rendus fonctionnels et commentes:

- `pipeline.py`
- `io/csv_writer.py`
- `parsers/windows_event.py`
- `writer.py`

Certains autres parseurs recuperes peuvent encore contenir des zones incompletes. Le pipeline bascule vers un parseur `unknown` si un parseur specialise plante au chargement, afin de ne pas perdre les lignes brutes.

## Exemple de test inclus

Un exemple Windows Event est fourni:

```text
recovered_pycdc\examples\windows_event_sample.xml
```

Commande de test:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'recovered_pycdc\examples\windows_event_sample.xml', r'recovered_pycdc\examples\out', 'windows_events.csv', debug=True))"
```
