# Objectif 2 - Approches de detection d'anomalies

Ce document formalise l'objectif 2 du memoire:

> Etudier, comparer et choisir des approches classiques et intelligentes pour la detection d'anomalies dans les journaux.

L'objectif n'est pas seulement de lancer un modele IA. Il faut montrer une demarche comparative: partir de methodes simples et explicables, puis evaluer des modeles non supervises legers capables de fonctionner sur une machine standard.

## Approches Retenues

| Approche | Type | Role dans le projet | Fichier |
| --- | --- | --- | --- |
| Baseline par regles | Heuristique explicable | Point de comparaison simple | `src/logminer/agents/baseline_detector.py` |
| Seuils simples | Traditionnelle | Regles fixes sur severite, HTTP et message | `src/logminer/agents/model_compare.py` |
| z-score | Statistique | Ecart maximal a la moyenne | `src/logminer/agents/model_compare.py` |
| IQR | Statistique robuste | Sortie des bornes interquartiles | `src/logminer/agents/model_compare.py` |
| Histogramme | Statistique explicable | Rarete des valeurs event/source/severite | `src/logminer/agents/model_compare.py` |
| Entropie | Traditionnelle/statistique | Entropie du message et surprise categorielle | `src/logminer/agents/model_compare.py` |
| Isolation Forest | IA non supervisee | Modele principal initial | `src/logminer/agents/detector.py` |
| k-Means | IA non supervisee | Distance au groupe le plus proche | `src/logminer/agents/model_compare.py` |
| One-Class SVM | IA non supervisee | Comparaison ML classique | `src/logminer/agents/model_compare.py` |
| Local Outlier Factor | IA non supervisee | Comparaison par densite locale | `src/logminer/agents/model_compare.py` |
| Autoencoder MLP | IA / deep learning leger | Erreur de reconstruction | `src/logminer/agents/model_compare.py` |
| LSTM TensorFlow/PyTorch | IA sequence optionnelle | Prediction de sequence d'evenements | `src/logminer/agents/model_compare.py` |
| Ensemble global | Pipeline multi-modeles | Agregation des scores de plusieurs detecteurs | `src/logminer/agents/model_compare.py` |

## Pourquoi Ces Methodes

- La baseline par regles donne un resultat interpretable: severite, categorie securite, mots suspects et rarete.
- seuils, z-score, IQR, histogramme et entropie donnent des references traditionnelles/statistiques simples, utiles pour expliquer les anomalies sans modele opaque.
- Isolation Forest est robuste sur donnees tabulaires et fonctionne sans labels.
- k-Means detecte les evenements eloignes de leur groupe le plus proche.
- One-Class SVM est une reference classique pour apprendre une frontiere du comportement normal.
- Local Outlier Factor mesure l'isolement local d'un evenement par rapport a ses voisins.
- L'Autoencoder cherche les lignes difficiles a reconstruire, donc potentiellement atypiques.
- Le LSTM est garde comme prototype sequence. TensorFlow/Keras est privilegie, puis PyTorch est utilise comme secours si TensorFlow n'est pas disponible.

La grille reste volontairement legere. Les methodes statistiques et scikit-learn fonctionnent sans GPU. Le LSTM est documente et code comme extension experimentale; il peut etre ignore dans une premiere execution si aucun backend deep learning n'est present.

## Features Utilisees

Les features sont construites dans `src/logminer/features/event_features.py`.

Elles combinent:

- champs numeriques: ports, statut HTTP, PID/TID, taille;
- score de severite;
- longueur et structure du message;
- presence d'erreur ou d'adresse IP dans le message;
- heure et jour de la semaine;
- encodage one-hot de champs categoriels limites: dataset, subtype, severity, category, subcategory, event, source, host.

Cette representation evite de dependre d'un seul format de logs.

## Commandes

Baseline explicable:

```powershell
python src\logminer\agents\baseline_detector.py -i data\processed\windows_copies_pipeline.csv -o data\processed\baseline_anomalies.csv --contamination 0.02
```

Detection principale avec Isolation Forest:

```powershell
python src\logminer\agents\detector.py -i data\processed\windows_copies_pipeline.csv -o data\processed\anomalies.csv --contamination 0.02
```

Comparaison des modeles:

```powershell
python src\logminer\agents\model_compare.py -i data\processed\windows_copies_pipeline.csv -o data\processed\model_comparison.csv --contamination 0.02
```

Pour activer le LSTM deep learning:

```powershell
python -m pip install -r requirements-ai.txt
```

TensorFlow est teste en premier. Si TensorFlow n'est pas disponible mais que PyTorch est installe, le comparateur execute automatiquement le LSTM PyTorch.

Cette commande execute la grille experimentale complete:

- traditionnelles/statistiques: `rule_baseline`, `static_thresholds`, `z_score`, `iqr`, `histogram`, `entropy`;
- IA tabulaire: `isolation_forest`, `kmeans`, `one_class_svm`, `local_outlier_factor`, `autoencoder_mlp`;
- IA sequence: `lstm_tensorflow` ou `lstm_pytorch`, marque comme ignore si aucun backend deep learning n'est installe.
- pipeline global: `ensemble_global`, `ensemble_selected`.

## Logs Simules Avec Anomalies Injectees

Pour respecter l'objectif d'evaluation sur logs simules, un dataset Windows peut
etre genere en injectant des anomalies controlees:

```powershell
python scripts\inject_simulated_anomalies.py `
  -i data\processed\windows_copies_pipeline.csv `
  -o data\processed\validation_simulated_windows.csv `
  --anomaly-fraction 0.05 `
  --max-rows 6000
```

Evaluation:

```powershell
python src\logminer\agents\model_compare.py `
  -i data\processed\validation_simulated_windows.csv `
  -o data\processed\validation_simulated_windows_metrics.csv `
  --contamination auto `
  --label-column label
```

## Validation Avec Datasets Labellises

La validation objective se fait avec des datasets contenant une verite terrain.
Deux jeux sont actuellement prepares localement:

- HDFS: labels par `BlockId` dans `data/raw/Datasets/HDFS_1/anomaly_label.csv`;
- BGL: label normal/anomalie porte par le premier marqueur de chaque ligne du log brut.

Les fichiers bruts sont volumineux. Pour eviter de charger plusieurs Go en
memoire a chaque essai, `scripts/prepare_validation_dataset.py` cree des CSV
normalises et echantillonnes avec une colonne `label`.

Preparation HDFS:

```powershell
python scripts\prepare_validation_dataset.py hdfs `
  --input data\raw\Datasets\Dataset_csv\hdfs.csv `
  --labels data\raw\Datasets\HDFS_1\anomaly_label.csv `
  --output data\processed\validation_hdfs.csv `
  --max-normal 3000 `
  --max-anomaly 3000
```

Preparation BGL:

```powershell
python scripts\prepare_validation_dataset.py bgl `
  --input data\raw\Datasets\BGL\BGL.log `
  --output data\processed\validation_bgl.csv `
  --max-normal 3000 `
  --max-anomaly 3000
```

Evaluation avec labels:

```powershell
python src\logminer\agents\model_compare.py `
  -i data\processed\validation_hdfs.csv `
  -o data\processed\validation_hdfs_metrics.csv `
  --contamination auto `
  --label-column label

python src\logminer\agents\model_compare.py `
  -i data\processed\validation_bgl.csv `
  -o data\processed\validation_bgl_metrics.csv `
  --contamination auto `
  --label-column label
```

`--contamination auto` utilise le taux reel d'anomalies du dataset labellise.
Cela rend la comparaison plus juste, car chaque modele predit un volume
d'anomalies comparable au volume attendu.

Synthese des meilleurs modeles:

```powershell
python scripts\summarize_validation_metrics.py `
  data\processed\validation_hdfs_metrics.csv `
  data\processed\validation_bgl_metrics.csv `
  -o data\processed\validation_summary.csv `
  --top-n 3
```

## Sortie Comparative

Le fichier `data/processed/model_comparison.csv` contient:

| Colonne | Signification |
| --- | --- |
| `model` | Nom de la methode |
| `events` | Nombre d'evenements analyses |
| `anomalies` | Nombre d'anomalies candidates |
| `anomaly_rate` | Proportion d'anomalies candidates |
| `score_min`, `score_mean`, `score_max` | Distribution des scores |
| `overlap_with_baseline` | Nombre d'anomalies communes avec la baseline |
| `overlap_rate` | Part du modele recouverte par la baseline |
| `duration_sec` | Temps d'execution |
| `memory_peak_mb` | Pic memoire Python estime par `tracemalloc` |
| `adaptability_score` | Score qualitatif d'adaptation du modele |
| `selection_score` | Score multicritere: F1/precision, temps, memoire, adaptabilite |
| `precision`, `recall`, `f1` | Ajoutes seulement si une colonne de labels est fournie |
| `accuracy`, `specificity` | Exactitude globale et rappel de la classe normale |
| `tp`, `fp`, `fn`, `tn` | Matrice de confusion |

## Interpretation Pour Le Memoire

Sans labels, la comparaison ne mesure pas encore la "verite" de detection. Elle sert a:

- verifier que les methodes ne produisent pas toutes les memes alertes;
- comparer leur cout d'execution;
- observer leur proximite avec une baseline explicable;
- justifier le choix d'Isolation Forest comme premier modele operationnel.

Exploitation recommandee:

- garder la baseline, z-score, IQR et histogramme comme methodes de controle explicables;
- utiliser Isolation Forest comme detecteur operationnel initial;
- comparer k-Means, LOF, SVM et Autoencoder pour identifier les alertes que le detecteur principal ne voit pas;
- conserver le LSTM TensorFlow/PyTorch pour une experience sequence sur un dataset plus adapte, par exemple HDFS/BGL avec ordre temporel fiable.

Avec un dataset labellise plus tard, par exemple HDFS ou BGL annote, le meme script pourra produire precision, rappel et F1-score avec:

```powershell
python src\logminer\agents\model_compare.py -i data\processed\dataset_labelise.csv --label-column label --contamination auto
```

Resultats de validation actuels sur echantillons equilibres de 6000 lignes:

| Dataset | Meilleur modele observe | Precision | Recall | F1 |
| --- | --- | ---: | ---: | ---: |
| BGL | z-score / histogramme / entropie / k-Means | 0.994333 | 0.994333 | 0.994333 |
| HDFS | LSTM TensorFlow | 0.614000 | 0.614000 | 0.614000 |
| Windows simule | baseline / IQR / Isolation Forest | 1.000000 | 1.000000 | 1.000000 |

Selon le score multicritere `selection_score`, qui combine qualite, temps,
memoire et adaptabilite:

| Dataset | Meilleur modele multicritere | Selection score |
| --- | --- | ---: |
| BGL | ensemble_selected | 0.957328 |
| HDFS | ensemble_selected | 0.779572 |
| Windows simule | Isolation Forest | 0.908556 |

Ces valeurs sont des resultats experimentaux sur echantillons prepares. Elles
doivent etre presentees comme validation initiale, pas comme performance finale
generalisee a tout le dataset.

## Etat Actuel

Fait:

- baseline explicable;
- seuils simples, z-score, IQR, histogramme et entropie;
- Isolation Forest operationnel;
- comparaison avec k-Means, One-Class SVM, LOF et Autoencoder MLP;
- prototype LSTM TensorFlow prioritaire avec secours PyTorch;
- pipeline ensemble global et ensemble selectionne;
- export CSV comparatif;
- compatibilite future avec labels.
- preparation HDFS/BGL labellisee;
- generation de logs simules avec anomalies injectees;
- metriques precision, recall, F1, accuracy, specificity, memoire, temps et matrice de confusion;
- synthese `data/processed/validation_summary.csv`.

Reste a faire:

- ajuster les features pour les logs reseau;
- elargir la validation a plus de lignes ou a des splits train/test;
- integrer les resultats dans le chapitre 2 et le chapitre 5 du memoire.
