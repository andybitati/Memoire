# Entrainement Cloud Et Sauvegarde Des Modeles

Ce document prepare l'objectif 6: entrainer sur de grands datasets dans le
cloud, puis reutiliser les modeles localement.

## Pourquoi Joblib

Les datasets complets HDFS, BGL ou reseau peuvent etre trop volumineux pour un
poste local. `joblib` permet de sauvegarder un modele scikit-learn entraine dans
le cloud, puis de le recharger dans l'agent detecteur sans relancer
l'entrainement.

## Entrainement Sur Le Cloud

Le flux retenu pour le projet est Google Colab + Google Drive. Les donnees
volumineuses sont stockees dans `cloud_upload/logminer_cloud_data/`, puis
montees directement dans Colab depuis Google Drive.

Exemple generique avec un CSV normalise volumineux:

```powershell
python src\logminer\agents\detector.py `
  -i data\processed\cloud_training_dataset.csv `
  -o data\processed\cloud_training_anomalies.csv `
  --contamination 0.02 `
  --max-categorical-unique 200 `
  --model-out models\isolation_forest_cloud.joblib
```

Si plusieurs CSV traites doivent etre utilises ensemble, construire d'abord un
fichier d'entrainement fusionne:

```powershell
python scripts\build_cloud_training_dataset.py `
  --input-dir data\processed\cloud_train_sources `
  --output data\processed\cloud_training_dataset.csv `
  --max-rows-per-file 50000
```

`--max-rows-per-file` permet d'eviter qu'un seul dataset tres volumineux domine
tout l'entrainement. Pour utiliser toutes les lignes, mettre `0`.

Dans Colab, la commande utilisee avec Google Drive est:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-dir "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train" \
  --output data/processed/cloud_training_dataset.csv \
  --max-rows-per-file 50000
```

Puis:

```bash
python src/logminer/agents/detector.py \
  -i data/processed/cloud_training_dataset.csv \
  -o data/processed/cloud_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 200 \
  --model-out "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_models/isolation_forest_colab.joblib"
```

L'artefact contient:

- le modele `IsolationForest`;
- les colonnes de features utilisees pendant l'entrainement;
- le nombre de lignes d'entrainement;
- les parametres utiles;
- la date d'entrainement.

## Inference Locale

Apres recuperation du fichier `.joblib` depuis le cloud:

```powershell
python src\logminer\agents\detector.py `
  -i data\processed\windows_copies_pipeline.csv `
  -o data\processed\anomalies_from_colab_model.csv `
  --model-in models\isolation_forest_colab.joblib
```

L'agent reconstruit les features du CSV local, puis les realigne sur les
colonnes sauvegardees dans l'artefact. Cela evite les erreurs dues aux colonnes
one-hot absentes ou nouvelles.

## Resultats Colab Du 29/05/2026

Entrainement realise sur Google Colab avec les donnees Drive:

```text
Evenements d'entrainement: 287862
Colonnes du CSV fusionne: 79
Modele: Isolation Forest
Contamination: 0.02
Max categories one-hot: 200
Anomalies candidates cloud: 5754
Taux d'anomalies: 0.019988744606790752
Artefact: models/isolation_forest_colab.joblib
Taille: 2158082 octets
```

Test local du modele Colab sur `data/processed/windows_copies_pipeline.csv`:

```text
Evenements Windows analyses: 61313
Anomalies candidates: 81
Incidents correles: 71
Sorties:
  data/processed/anomalies_from_colab_model.csv
  data/processed/incidents_from_colab_model.csv
```

Point de vigilance: le modele a ete entraine avec scikit-learn `1.6.1` dans
Colab et charge localement avec scikit-learn `1.7.2`. L'inference fonctionne,
mais il faut noter cet ecart pour la reproductibilite.

## Test Live Sur Journaux Windows

Test realise le 29/05/2026 sur `C:\Windows\System32\winevt\Logs`.

Collecte et parsing:

```text
Fichiers .evtx recents selectionnes: 99
Evenements recents exportes: 17725
Echecs ou journaux vides: 12
Copies EVTX exploitables: Application, System
Copie Security.evtx: echec, acces refuse sans administrateur
Evenements parses dans windows_live_pipeline_colab_test.csv: 61356
```

Inference avec le modele Colab:

```text
Modele: models/isolation_forest_colab.joblib
Entree: data/processed/windows_live_pipeline_colab_test.csv
Sortie anomalies: data/processed/anomalies_live_colab_model.csv
Evenements analyses: 61356
Anomalies candidates: 86
Taux d'anomalie: 0.0014016559097724754, soit 0.140 %
Sortie incidents: data/processed/incidents_live_colab_model.csv
Incidents correles: 76
```

Repartition des anomalies:

```text
WARNING: 68 anomalies, 79.1 %
ERROR: 18 anomalies, 20.9 %

Microsoft-Windows-Ntfs: 30 anomalies, 34.9 %
Microsoft-Windows-DistributedCOM: 30 anomalies, 34.9 %
Windows App Runtime: 9 anomalies, 10.5 %
Application Error: 8 anomalies, 9.3 %
Microsoft-Windows-Time-Service: 5 anomalies, 5.8 %
```

Interpretation:

- le modele fonctionne sur des journaux Windows reels;
- les anomalies observees correspondent surtout a de l'instabilite systeme ou
  applicative, pas a des attaques explicites;
- l'absence d'attaque detectee ne prouve pas l'absence de compromission;
- l'analyse securite reste incomplete tant que `Security.evtx` n'est pas exporte
  avec des droits administrateur.

## Test Administrateur Sur Security.evtx

Test realise le 29/05/2026 apres export administrateur de `Security.evtx`.

Commande reproductible:

```powershell
cd F:\Cours\TFE
.\scripts\run_security_admin_inference.ps1
```

Resultats:

```text
Fichier brut: data/raw/windows_events_admin/Security.evtx
CSV parse: data/processed/windows_security_pipeline.csv
Anomalies: data/processed/anomalies_security_colab_model.csv
Incidents: data/processed/incidents_security_colab_model.csv
Evenements analyses: 32583
Anomalies candidates: 203
Incidents correles: 87
Priorites incidents: HIGH 3, MEDIUM 80, LOW 4
Source dominante: Microsoft-Windows-Security-Auditing
Evenements dominants: 4624 (198 anomalies), 4738 (5 anomalies)
```

Interpretation:

- le journal Security est maintenant integre au flux experimental;
- les anomalies sont surtout des authentifications Windows `4624` jugees
  atypiques par le modele;
- le correlateur ajoute maintenant une priorite (`priority`), un score
  explicable (`priority_score`) et une justification (`rationale`);
- ces incidents restent des alertes candidates: ils doivent etre interpretes
  comme des comportements inhabituels, pas comme des preuves d'intrusion.

## Test Reseau Sur outside_tcp_dump

UNSW-NB15 etant en cours de telechargement, un premier test reseau a ete mene
avec `data/raw/Datasets/Dataset_csv/outside_tcp_dump_part001.csv`.

Un echantillon de `100000` lignes a ete extrait dans:

```text
data/processed/outside_tcp_dump_sample.csv
```

Inference avec le modele Colab:

```text
Entree: data/processed/outside_tcp_dump_sample.csv
Sortie: data/processed/anomalies_outside_tcp_dump_colab_model.csv
Evenements analyses: 100000
Anomalies candidates: 0
Incidents correles: 0
```

Detection dediee au trafic reseau avec Isolation Forest local (`--contamination
0.02`):

```text
Sortie anomalies: data/processed/anomalies_outside_tcp_dump_local_iforest.csv
Sortie incidents: data/processed/incidents_outside_tcp_dump_local_iforest.csv
Evenements analyses: 100000
Anomalies candidates: 1998
Incidents correles: 22
Priorites incidents: MEDIUM 15, LOW 7
Principaux groupes: UDP/53, TCP/25, UDP/123
```

Interpretation:

- le modele Colab generalise n'a pas isole d'anomalies dans cet echantillon
  reseau precis;
- un modele entraine localement sur l'echantillon reseau isole environ 2 %
  d'evenements atypiques, conformement au parametre de contamination;
- les incidents reseau sont maintenant regroupes aussi par protocole et port
  destination (`proto`, `dst_port`), ce qui rend les resultats plus lisibles;
- ce test doit etre presente comme une validation reseau initiale, en attendant
  l'exploitation de UNSW-NB15.

## Entrainement Cloud Reseau

Pour le prochain entrainement Colab, le dataset reseau cible combine:

- `UNSWNB15.zip`, extrait temporairement dans `/content`;
- `outside_tcp_dump.csv`;
- `outside_tcp_dump_part001.csv`;
- `UNSW_NB15_training-set.parquet` et `UNSW_NB15_testing-set.parquet` si
  presents.

Le script `scripts/build_cloud_training_dataset.py` accepte maintenant les CSV
et les Parquet, plusieurs `--input-dir`, les sous-dossiers avec `--recursive`,
la detection automatique du separateur CSV avec `--sep auto`, et la suppression
des doublons avec `--dedupe name-size`.

Commande Colab recommandee apres extraction temporaire des ZIP dans
`/content/logminer_network_data/extracted` et copie des fichiers directs dans
`/content/logminer_network_data/network_sources`:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-dir "/content/logminer_network_data/extracted/UNSWNB15" \
  --input-dir "/content/logminer_network_data/network_sources" \
  --recursive \
  --sep auto \
  --dedupe name-size \
  --output data/processed/network_training_dataset.csv \
  --max-rows-per-file 50000
```

Si un autre ZIP contient les memes fichiers, `--dedupe name-size` garde une
seule copie lorsque le nom et la taille sont identiques. Pour une verification
stricte, utiliser `--dedupe hash`, mais cela lit les gros fichiers en entier et
peut prendre beaucoup plus de temps.

Puis:

```bash
python src/logminer/agents/detector.py \
  -i data/processed/network_training_dataset.csv \
  -o data/processed/network_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_models/isolation_forest_network_colab.joblib"
```

Cet artefact doit etre garde separe du modele systeme/Windows:

```text
models/isolation_forest_colab.joblib          -> modele general/systeme actuel
models/isolation_forest_network_colab.joblib  -> modele reseau UNSW/tcpdump
```

## Routage Automatique Des Modeles

L'agent `src/logminer/agents/model_router.py` oriente chaque entree vers le
modele adapte:

```text
systeme/Windows/HDFS/BGL/syslog -> models/isolation_forest_colab.joblib
reseau/tcpdump/pcap/UNSW -> models/isolation_forest_network_colab.joblib
```

Verifier la route:

```powershell
python src\logminer\agents\model_router.py -i data\processed\windows_security_pipeline.csv
python src\logminer\agents\model_router.py -i data\processed\outside_tcp_dump_sample.csv
```

Executer detection + correlation avec le modele choisi:

```powershell
python src\logminer\agents\model_router.py `
  -i data\processed\outside_tcp_dump_sample.csv `
  --detect `
  --network-model models\isolation_forest_network_colab.joblib
```

Pour exporter le journal Security, ouvrir PowerShell en administrateur:

```powershell
cd F:\Cours\TFE
New-Item -ItemType Directory -Force data\raw\windows_events_admin
wevtutil epl Security data\raw\windows_events_admin\Security.evtx
wevtutil epl System data\raw\windows_events_admin\System.evtx
wevtutil epl Application data\raw\windows_events_admin\Application.evtx
```

Puis parser et appliquer le modele:

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'data\raw\windows_events_admin', r'data\processed', 'windows_admin_pipeline.csv', debug=True))"

python src\logminer\agents\detector.py `
  -i data\processed\windows_admin_pipeline.csv `
  -o data\processed\anomalies_admin_colab_model.csv `
  --model-in models\isolation_forest_colab.joblib

python src\logminer\agents\correlator.py `
  -i data\processed\anomalies_admin_colab_model.csv `
  -o data\processed\incidents_admin_colab_model.csv
```

## Convention De Nommage

Convention recommandee:

```text
models/
  isolation_forest_colab.joblib
  isolation_forest_hdfs_bgl_YYYYMMDD.joblib
  isolation_forest_unsw_YYYYMMDD.joblib
```

Les modeles volumineux doivent rester hors Git si necessaire. Pour le memoire,
il suffit de conserver:

- la commande d'entrainement;
- les metadonnees du modele;
- les resultats de validation;
- le chemin ou l'identifiant de stockage cloud.
