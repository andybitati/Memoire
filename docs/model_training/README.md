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
