# TFE - Détection d'anomalies dans les journaux systèmes et réseaux

Ce dépôt contient les documents, jeux de données, scripts et prototypes liés au mémoire:

**Détection Autonome et Distribuée d'Anomalies dans les Journaux Systèmes et Réseaux à l'aide d'Agents Intelligents Multi-Tâches**.

L'objectif général est de construire un système capable de collecter différents types de journaux, les parser, les normaliser, les catégoriser, puis les préparer pour des agents IA de détection d'anomalies.

## Objectif Du Projet

Le mémoire vise à traiter des journaux hétérogènes comme:

- logs Linux/syslog;
- journaux Windows Event Log;
- logs Apache/Nginx;
- captures réseau `pcap` ou sorties `tcpdump`;
- datasets publics comme HDFS, BGL et DARPA;
- formats sécurité comme CEF/LEEF;
- logs JSON/JSONL et CloudTrail.

Le travail actuel se concentre sur la première grande brique technique: **Logminer**, un pipeline de prétraitement qui transforme des logs bruts en CSV normalisé.

## Architecture Prévue

Le système final du mémoire est pensé comme une architecture multi-agents:

- **Agent 1 - Collecte et parsing**: lit les logs bruts et détecte leur format.
- **Agent 2 - Prétraitement et normalisation**: transforme les événements dans un schéma commun.
- **Agent 3 - Détection d'anomalies**: applique des modèles comme Isolation Forest, Autoencoder, One-Class SVM ou LSTM léger.
- **Agent 4 - Corrélation contextuelle**: relie plusieurs événements suspects.
- **Agent 5 - Visualisation**: affiche les alertes, statistiques et anomalies dans un dashboard.

Le code actuellement reconstruit prépare surtout les agents 1 et 2.

## Structure Du Dépôt

- `Memoire/`: documents de rédaction du mémoire.
- `Documentation/`: références documentaires et normes utiles.
- `Datasets/`: jeux de données ou fichiers bruts liés aux tests.
- `Preprocessing/`: emplacement historique du module Logminer.
- `recovered_pycdc/`: sources Python reconstruites depuis les fichiers `.pyc`.
- `recovered_disasm/`: désassemblages complets des `.pyc`, utiles pour réparer les parties manquantes.
- `recovered_py/`: anciennes sorties incomplètes de `decompyle3`; ne pas utiliser comme source principale.
- `tools/`: outils utilisés pour la récupération, notamment `pycdc`.
- `RECOVERY_README.md`: résumé de la récupération `.pyc -> .py`.
- `requirements.txt`: dépendances Python à installer pour utiliser les scripts et préparer les étapes IA.

## Installation

Créer/activer un environnement Python, puis installer les dépendances:

```powershell
python -m pip install -r requirements.txt
```

`python-evtx` sert uniquement à lire directement les fichiers `.evtx`. Si cette dépendance pose problème, il est possible d'exporter les journaux Windows en XML et de les traiter avec le parseur Windows Event.

## État De La Récupération

Des fichiers Python originaux avaient disparu et il ne restait que des `.pyc`. La récupération a été faite avec `pycdc`, car `decompyle3` et `uncompyle6` ne supportaient pas correctement les bytecodes Python 3.11.

Les fichiers reconstruits les plus importants sont dans:

```text
recovered_pycdc/Preprocessing/Logminer
```

Fichiers déjà réparés et commentés:

- `pipeline.py`
- `io/csv_writer.py`
- `writer.py`
- `parsers/windows_event.py`
- `detectors/file_detector.py`
- `detectors/__init__.py`

Certains autres parseurs récupérés peuvent encore contenir des zones incomplètes. Quand un parseur spécialisé ne fonctionne pas, le pipeline peut basculer vers un parseur de secours `unknown` pour conserver au moins les messages bruts.

## Composants Logminer

### `pipeline.py`

Rôle: orchestrer le traitement complet.

Il reçoit un fichier ou un dossier, détecte le type de chaque log, charge le parseur correspondant, puis écrit les résultats dans un CSV normalisé.

Exemple:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'recovered_pycdc\examples\windows_event_sample.xml', r'recovered_pycdc\examples\out', 'windows_events.csv', debug=True))"
```

### `detectors/file_detector.py`

Rôle: reconnaître le format d'un fichier de log.

Fonctions principales:

- `detect_kind(path)`: retourne le type détecté, par exemple `win_event`, `syslog`, `apache`, `hdfs`, `bgl`, `pcap`, `jsonl`, `unknown`.
- `detect_file(input_path)`: retourne le premier fichier exploitable avec son type.
- `iter_files(input_path)`: parcourt un fichier ou un dossier récursivement.

Tester uniquement la détection:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); from detectors.file_detector import detect_kind; print(detect_kind(r'recovered_pycdc\examples\windows_event_sample.xml'))"
```

### `io/csv_writer.py`

Rôle: écrire les événements dans un CSV propre.

Il garantit que toutes les lignes respectent le même schéma, même si les parseurs ne fournissent pas tous les champs.

Fonctions principales:

- `open_writer(base_out, part=0, sep=';')`: ouvre un CSV et écrit l'en-tête.
- `emit(writer, base)`: normalise un événement et écrit une ligne.

### `schema/columns.py`

Rôle: définir le contrat de données.

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

Ce schéma sert de base pour les modèles IA et le dashboard.

### `parsers/windows_event.py`

Rôle: parser les journaux Windows.

Formats supportés:

- exports XML Windows Event Viewer;
- fichiers `.evtx` si la dépendance `python-evtx` est installée.

Utilisation avec XML:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'C:\chemin\security.xml', r'Dataset_csv', 'windows_security.csv', debug=True))"
```

Utilisation avec EVTX:

```powershell
python -m pip install python-evtx
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'C:\chemin\Security.evtx', r'Dataset_csv', 'security_evtx.csv', debug=True))"
```

### `parsers/*.py`

Rôle: parser chaque famille de logs.

Parseurs présents:

- `apache.py`: logs Apache/Nginx.
- `syslog.py`: logs Linux/syslog.
- `hdfs.py`: dataset HDFS.
- `bgl.py`: dataset BGL.
- `tcpdump_text.py`: sorties réseau tcpdump.
- `pcap.py`: captures réseau.
- `jsonl.py`: logs JSON ligne par ligne.
- `cef_leef.py`: formats sécurité CEF/LEEF.
- `cloudtrail.py`: logs AWS CloudTrail.
- `praudit_text.py` et `praudit_xml.py`: logs d'audit.
- `unknown.py`: fallback quand le format est inconnu.

Certains parseurs récupérés doivent encore être réparés avant usage avancé.

### `normalizers/*.py`

Rôle: enrichir et harmoniser les événements avant écriture CSV.

Composants:

- `base.py`: classe de base des normaliseurs.
- `default.py`: harmonise les niveaux de sévérité.
- `categorizer.py`: classe les événements en familles sécurité.
- `runner.py`: applique la chaîne de normalisation.

Ces fichiers serviront à préparer les données pour les agents IA, par exemple en ajoutant `category` et `subcategory`.

## Utilisation Complète

Traiter un fichier:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'Application.evtx', r'Dataset_csv', 'application.csv', debug=True))"
```

Traiter un dossier:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'Datasets', r'Dataset_csv', 'dataset.csv', debug=True))"
```

Changer le séparateur CSV:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'Datasets', r'Dataset_csv', 'dataset.csv', sep=',', debug=True))"
```

## Exemple Inclus

Un exemple Windows Event XML est disponible ici:

```text
recovered_pycdc/examples/windows_event_sample.xml
```

Commande de test:

```powershell
python -c "import sys; sys.path.insert(0, r'recovered_pycdc\Preprocessing\Logminer'); import pipeline; print(pipeline.run_pipeline(r'recovered_pycdc\examples\windows_event_sample.xml', r'recovered_pycdc\examples\out', 'windows_events.csv', debug=True))"
```

Résultat attendu:

```text
recovered_pycdc/examples/out/windows_events.csv
```

## Données Produites

Le CSV final est conçu pour être utilisé par:

- des notebooks d'analyse;
- des modèles de détection d'anomalies;
- des agents IA spécialisés;
- un dashboard Streamlit, Flask ou Dash;
- des évaluations de performance avec précision, rappel, F1-score et latence.

## Prochaines Étapes

- Réparer les parseurs encore incomplets.
- Finaliser `normalizers/categorizer.py` et `normalizers/runner.py`.
- Ajouter des tests sur HDFS, BGL, syslog, Apache et EVTX réel.
- Créer un module de features ML à partir du CSV.
- Implémenter un premier détecteur Isolation Forest.
- Préparer un dashboard de visualisation des anomalies.

## Remarque Importante

Le dossier de travail principal est actuellement:

```text
recovered_pycdc/Preprocessing/Logminer
```

Le dossier `recovered_py/` ne doit pas être utilisé comme base principale, car il contient surtout les échecs de décompilation produits par `decompyle3`.
