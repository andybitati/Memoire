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
modele adapte. Le routeur n'est plus seulement binaire systeme/reseau: il
prepare une architecture multi-modeles par famille de logs. Le choix se fait a
partir d'un profil de features de l'echantillon: colonnes actives, valeurs,
marqueurs textuels, IP/ports/protocoles, densite numerique, EventID, BlockId et
signaux propres a chaque famille.

```text
Windows/Event/Security -> models/isolation_forest_windows_local.joblib
HDFS                   -> models/isolation_forest_hdfs_colab.joblib
BGL                    -> models/isolation_forest_bgl_colab.joblib
Wazuh/SIEM/auditd/FIM  -> models/isolation_forest_wazuh.joblib
Reseau/CICIDS2017      -> models/random_forest_network_cicids.joblib
Reseau/tcpdump/UNSW    -> models/random_forest_network_unsw_80_20_sampled.joblib
Linux/auth tabulaire   -> models/random_forest_linux_auth.joblib
Linux/syslog           -> models/isolation_forest_linux_colab.joblib
Inconnu/fallback       -> models/isolation_forest_colab.joblib
```

Verifier la route:

```powershell
python src\logminer\agents\model_router.py -i data\processed\windows_security_pipeline.csv
python src\logminer\agents\model_router.py -i data\raw\Datasets\03-04-January.csv --sep auto
python src\logminer\agents\model_router.py -i data\processed\outside_tcp_dump_sample.csv
python src\logminer\agents\model_router.py -i data\raw\Datasets\MachineLearningCSV\MachineLearningCVE\Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv --sep auto
python src\logminer\agents\model_router.py -i data\raw\Datasets\linux_auth_logs_labeled.csv --sep auto
```

Executer detection + correlation avec le modele choisi:

```powershell
python src\logminer\agents\model_router.py `
  -i data\processed\outside_tcp_dump_sample.csv `
  --detect `
  --network-model models\isolation_forest_network_colab.joblib
```

## Entrainement Par Famille De Logs

Le modele global initial reste utile comme preuve de faisabilite, mais son
analyse par dataset montre une limite: certains formats absorbent la majorite
des anomalies. La strategie retenue est donc d'entrainer un modele par famille.

Commandes Colab recommandees apres montage Drive et clone du projet:

Windows local admin:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/windows_copies_pipeline.csv" \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/windows_recent_events.csv" \
  --sep auto \
  --output data/processed/windows_training_dataset.csv \
  --max-rows-per-file 100000

python src/logminer/agents/detector.py \
  -i data/processed/windows_training_dataset.csv \
  -o data/processed/windows_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out models/isolation_forest_windows_local.joblib
```

Wazuh/SIEM/auditd/FIM:

Les fichiers dates `*-January.csv`, `*-October*.csv` et `*-December*.csv`
places dans `data/raw/Datasets` sont des exports Wazuh/Elastic. Ils couvrent
une surface differente des datasets reseau et Linux/auth:

```text
auditd / audit_command
syscheck / File Integrity Monitoring
SCA / Security Configuration Assessment
web-accesslog / attaques web
dpkg / changements de paquets
pam, sshd, sudo / authentification et elevation
rootcheck / controles hote
```

Ils sont exploitables, mais doivent etre separes des modeles Windows, Linux/auth
et reseau. Le routeur les identifie comme `wazuh` et utilise:

```text
models/isolation_forest_wazuh.joblib
```

Normalisation des 17 CSV dates vers le schema Logminer:

```bash
python scripts/prepare_wazuh_dataset.py \
  --input-dir data/raw/Datasets \
  -o data/processed/wazuh_months_logminer.csv
```

Entrainement du modele Wazuh:

```bash
python src/logminer/agents/detector.py \
  -i data/processed/wazuh_months_logminer.csv \
  -o data/processed/wazuh_months_anomalies.csv \
  --sep ";" \
  --contamination 0.03 \
  --max-categorical-unique 250 \
  --model-out models/isolation_forest_wazuh.joblib
```

Resultats locaux:

```text
Evenements Wazuh normalises: 122563
Anomalies candidates: 3676
```

Repartition des familles normalisees:

```text
linux_audit: 83520
web_attack: 26637
authentication: 4342
file_integrity: 4140
security_configuration: 1616
package: 1233
wazuh/autre: 1075
```

Les anomalies du modele Wazuh concernent surtout `file_integrity`, `package`,
`security_configuration`, puis quelques evenements web et authentification. Ce
comportement est coherent avec un modele non supervise: il isole les alertes
Wazuh rares ou structurellement differentes, sans pretendre remplacer les
niveaux de regles Wazuh.

Linux/auth tabulaire:

Les CSV `linux_auth_logs_*.csv` ajoutent une couverture utile des journaux
d'authentification Linux. Comme ils contiennent aussi `source_ip`, `port` et
`protocol`, ils peuvent ressembler a des flux reseau. Le routeur les traite
desormais comme une famille separee `linux_auth` lorsque les colonnes
`username`, `service`, `attempts`, `status` ou `anomaly_label` sont presentes.

Un modele supervise dedie est disponible:

```text
models/random_forest_linux_auth.joblib
```

Il est entraine sur:

```text
data/raw/Datasets/linux_auth_logs_labeled.csv
data/raw/Datasets/linux_auth_logs_full(new_unbalanced).csv
```

Commande reproductible:

```bash
python scripts/train_linux_auth_model.py \
  -i "data/raw/Datasets/linux_auth_logs_labeled.csv" \
  -i "data/raw/Datasets/linux_auth_logs_full(new_unbalanced).csv" \
  --model-out models/random_forest_linux_auth.joblib \
  --metrics-out data/processed/random_forest_linux_auth_metrics.csv \
  --max-normal 120000 \
  --max-anomaly 0
```

Resultats du modele combine:

```text
Validation interne:
accuracy: 0.936444
precision: 0.923040
recall: 0.910253
f1: 0.916602

Generalisation observee:
linux_auth_logs_full(new_unbalanced).csv -> F1: 1.000000
linux_auth_logs_full(balanced).csv       -> F1: 0.992251
linux_auth_logs_labeled.csv              -> F1: 0.483490
```

Le fichier `linux_auth_logs_labeled.csv` est plus difficile: le modele garde un
bon rappel, mais produit davantage de faux positifs. Pour le memoire, il doit
donc etre presente comme test de generalisation plus dur, pas comme seul
dataset d'entrainement.

Inference routee sur un fichier Linux/auth sans label:

```bash
python src/logminer/agents/model_router.py \
  -i "data/raw/Datasets/linux_auth_logs_multiple_anomalies.csv" \
  --sep auto \
  --detect \
  -o data/processed/linux_auth_multiple_anomalies_rf.csv \
  --incidents-output data/processed/linux_auth_multiple_anomalies_incidents.csv
```

Lors de la verification locale, ce fichier sans `anomaly_label` produit:

```text
Evenements analyses: 500000
Anomalies candidates: 62331
```

Option: entrainement Linux mixte non supervise:

Si l'objectif est d'avoir un modele Linux non supervise plus large, les donnees
Linux/auth peuvent aussi etre normalisees vers le schema commun puis fusionnees
avec les journaux syslog/Linux classiques:

```bash
python scripts/prepare_linux_auth_dataset.py \
  -i "data/raw/Datasets/linux_auth_logs_labeled.csv" \
  -o data/processed/linux_auth_labeled_logminer.csv
```

Construire un entrainement Linux plus large:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-file data/processed/linux_auth_labeled_logminer.csv \
  --input-file data/raw/Datasets/Dataset_csv/Linux_2k.log_structured.csv \
  --input-file data/raw/Datasets/Dataset_csv/Operating_System_Logs_logs.csv \
  --input-file data/raw/Datasets/Dataset_csv/Server_Logs_logs.csv \
  --input-file data/raw/Datasets/Dataset_csv/Syslog_Data_logs.csv \
  --sep auto \
  --output data/processed/linux_training_dataset.csv \
  --max-rows-per-file 100000

python src/logminer/agents/detector.py \
  -i data/processed/linux_training_dataset.csv \
  -o data/processed/linux_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out models/isolation_forest_linux_colab.joblib
```

Dans ce cas, les labels `anomaly_label` restent utiles pour l'evaluation
humaine et les comparaisons supervise/non supervise, mais le modele produit
reste un Isolation Forest non supervise afin de rester compatible avec les
journaux non labellises.

HDFS:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/hdfs.csv" \
  --sep auto \
  --output data/processed/hdfs_training_dataset.csv \
  --max-rows-per-file 100000

python src/logminer/agents/detector.py \
  -i data/processed/hdfs_training_dataset.csv \
  -o data/processed/hdfs_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_models/isolation_forest_hdfs_colab.joblib"
```

BGL:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/bgl.csv" \
  --sep auto \
  --output data/processed/bgl_training_dataset.csv \
  --max-rows-per-file 100000

python src/logminer/agents/detector.py \
  -i data/processed/bgl_training_dataset.csv \
  -o data/processed/bgl_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_models/isolation_forest_bgl_colab.joblib"
```

Linux/syslog:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/Linux_2k.log_structured.csv" \
  --sep auto \
  --output data/processed/linux_training_dataset.csv \
  --max-rows-per-file 100000

python src/logminer/agents/detector.py \
  -i data/processed/linux_training_dataset.csv \
  -o data/processed/linux_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_models/isolation_forest_linux_colab.joblib"
```

Reseau:

Les fichiers du dossier `data/raw/Datasets/MachineLearningCSV/MachineLearningCVE`
correspondent a CICIDS2017/CICFlowMeter. Ils sont exploitables dans le travail,
mais ils ne doivent pas etre confondus avec UNSW/CIC-DDoS: le transfert du
modele UNSW vers ces fichiers donne des resultats irreguliers. Un modele
dedie est donc utilise:

```text
models/random_forest_network_cicids.joblib
```

Contenu exploitable:

```text
Monday-WorkingHours.pcap_ISCX.csv                         -> BENIGN seulement
Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv          -> DDoS
Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv      -> PortScan
Friday-WorkingHours-Morning.pcap_ISCX.csv                 -> Bot
Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv -> Infiltration
Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv    -> Web attacks
Tuesday-WorkingHours.pcap_ISCX.csv                        -> FTP/SSH Patator
Wednesday-workingHours.pcap_ISCX.csv                      -> DoS/Heartbleed
```

Commande reproductible:

```bash
python scripts/train_cicids_network_model.py \
  --input-dir data/raw/Datasets/MachineLearningCSV/MachineLearningCVE \
  --model-out models/random_forest_network_cicids.joblib \
  --metrics-out data/processed/random_forest_network_cicids_metrics.csv \
  --max-benign 150000 \
  --max-attack 180000 \
  --max-per-attack-label 30000
```

Resultats locaux:

```text
train_rows: 223692
test_rows: 55924
benign_rows_used: 150000
attack_rows_used: 129616
accuracy: 0.997371
precision: 0.997760
recall: 0.996567
f1: 0.997163
tp: 25835
fp: 58
fn: 89
tn: 29942
```

Le routeur reconnait ces fichiers comme `network_cicids` et les separe du
modele `network` entraine sur UNSW.

Reseau UNSW/tcpdump:

```bash
python scripts/build_cloud_training_dataset.py \
  --input-dir "/content/logminer_network_data/UNSWNB15" \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/outside_tcp_dump.csv" \
  --input-file "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_data/train/outside_tcp_dump_part001.csv" \
  --recursive \
  --sep auto \
  --dedupe name-size \
  --output data/processed/network_training_dataset.csv \
  --max-rows-per-file 100000

python src/logminer/agents/detector.py \
  -i data/processed/network_training_dataset.csv \
  -o data/processed/network_training_anomalies.csv \
  --contamination 0.02 \
  --max-categorical-unique 250 \
  --model-out "/content/drive/MyDrive/Mémoire/cloud_upload/logminer_cloud_models/isolation_forest_network_colab.joblib"
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
