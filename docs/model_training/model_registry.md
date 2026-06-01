# Registre Des Modeles Entraines

Ce registre conserve les artefacts utilisables pour l'exploitation future du
prototype Logminer. Les fichiers `.joblib` sont stockes dans `models/`; chaque
artefact contient le modele, les colonnes de features et des metadonnees
d'entrainement quand elles sont disponibles.

## Routeur Principal

Commande de base:

```powershell
python src\logminer\agents\model_router.py -i <csv-ou-parquet> --sep auto --detect
```

Le routeur choisit automatiquement la famille et charge le modele adapte.

## Modeles Disponibles

| Famille | Artefact | Type | Usage |
| --- | --- | --- | --- |
| `windows` | `models/isolation_forest_windows_local.joblib` | Isolation Forest | Journaux Windows Event/Security normalises |
| `wazuh` | `models/isolation_forest_wazuh.joblib` | Isolation Forest | Exports Wazuh/Elastic, auditd, syscheck, SCA, web-accesslog |
| `network_cicids` | `models/random_forest_network_cicids.joblib` | RandomForest supervise | CICIDS2017 / MachineLearningCVE |
| `network` | `models/random_forest_network_unsw_80_20_sampled.joblib` | RandomForest supervise | UNSW/CIC-DDoS, flux reseau tabulaires compatibles |
| `linux_auth` | `models/random_forest_linux_auth.joblib` | RandomForest supervise | Datasets Linux/auth tabulaires `linux_auth_logs_*` |
| `linux` | `models/isolation_forest_linux_colab.joblib` | Isolation Forest | Linux/syslog structure, Linux_2k et petits logs systeme |
| `hdfs` | `models/isolation_forest_hdfs_colab.joblib` | Isolation Forest | Journaux HDFS |
| `bgl` | `models/isolation_forest_bgl_colab.joblib` | Isolation Forest | Journaux BlueGene/L |
| `fallback` | `models/isolation_forest_fallback_colab.joblib` | Isolation Forest | Source inconnue ou distribution generale |

## Nouveaux Modeles Ajoutes

### Wazuh

Artefact:

```text
models/isolation_forest_wazuh.joblib
```

Donnees:

```text
data/processed/wazuh_months_logminer.csv
```

Entrainement:

```powershell
python src\logminer\agents\detector.py `
  -i data\processed\wazuh_months_logminer.csv `
  -o data\processed\wazuh_months_anomalies.csv `
  --sep ";" `
  --contamination 0.03 `
  --max-categorical-unique 250 `
  --model-out models\isolation_forest_wazuh.joblib
```

Resultat:

```text
evenements: 122563
anomalies candidates: 3676
```

### CICIDS / MachineLearningCVE

Artefact:

```text
models/random_forest_network_cicids.joblib
```

Entrainement:

```powershell
python scripts\train_cicids_network_model.py `
  --input-dir data\raw\Datasets\MachineLearningCSV\MachineLearningCVE `
  --model-out models\random_forest_network_cicids.joblib `
  --metrics-out data\processed\random_forest_network_cicids_metrics.csv `
  --max-benign 150000 `
  --max-attack 180000 `
  --max-per-attack-label 30000
```

Metriques:

```text
train_rows: 223692
test_rows: 55924
accuracy: 0.997371
precision: 0.997760
recall: 0.996567
f1: 0.997163
tp: 25835
fp: 58
fn: 89
tn: 29942
```

### Linux/Auth

Artefact:

```text
models/random_forest_linux_auth.joblib
```

Entrainement:

```powershell
python scripts\train_linux_auth_model.py `
  -i "data\raw\Datasets\linux_auth_logs_labeled.csv" `
  -i "data\raw\Datasets\linux_auth_logs_full(new_unbalanced).csv" `
  --model-out models\random_forest_linux_auth.joblib `
  --metrics-out data\processed\random_forest_linux_auth_metrics.csv `
  --max-normal 120000 `
  --max-anomaly 0
```

Metriques:

```text
train_rows: 155765
test_rows: 38942
accuracy: 0.936444
precision: 0.923040
recall: 0.910253
f1: 0.916602
tp: 13601
fp: 1134
fn: 1341
tn: 22866
```

## Notes D'exploitation

- Les modeles supervises (`random_forest_*`) doivent etre utilises seulement
  sur des schemas compatibles avec leur famille.
- Les modeles Isolation Forest sont adaptes aux sources non labellisees, mais
  leurs alertes restent des candidats a interpreter.
- Les nouveaux artefacts `linux_auth`, `network_cicids` et `wazuh` ont ete
  sauvegardes avec compression `joblib` afin de faciliter leur archivage local.
- Des avertissements scikit-learn peuvent apparaitre si la version locale
  differe de la version d'entrainement. L'inference a ete verifiee localement,
  mais la version doit etre notee dans le memoire pour la reproductibilite.
