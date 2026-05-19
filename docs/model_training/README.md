# Entrainement Cloud Et Sauvegarde Des Modeles

Ce document prepare l'objectif 6: entrainer sur de grands datasets dans le
cloud, puis reutiliser les modeles localement.

## Pourquoi Joblib

Les datasets complets HDFS, BGL ou reseau peuvent etre trop volumineux pour un
poste local. `joblib` permet de sauvegarder un modele scikit-learn entraine dans
le cloud, puis de le recharger dans l'agent detecteur sans relancer
l'entrainement.

## Entrainement Sur Le Cloud

Exemple avec un CSV normalise volumineux:

```powershell
python src\logminer\agents\detector.py `
  -i data\processed\cloud_training_dataset.csv `
  -o data\processed\cloud_training_anomalies.csv `
  --contamination 0.02 `
  --max-categorical-unique 200 `
  --model-out models\isolation_forest_cloud.joblib
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
  -o data\processed\anomalies_from_cloud_model.csv `
  --model-in models\isolation_forest_cloud.joblib
```

L'agent reconstruit les features du CSV local, puis les realigne sur les
colonnes sauvegardees dans l'artefact. Cela evite les erreurs dues aux colonnes
one-hot absentes ou nouvelles.

## Convention De Nommage

Convention recommandee:

```text
models/
  isolation_forest_hdfs_bgl_YYYYMMDD.joblib
  isolation_forest_unsw_YYYYMMDD.joblib
```

Les modeles volumineux doivent rester hors Git si necessaire. Pour le memoire,
il suffit de conserver:

- la commande d'entrainement;
- les metadonnees du modele;
- les resultats de validation;
- le chemin ou l'identifiant de stockage cloud.

