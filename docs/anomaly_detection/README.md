# Objectif 2 - Approches de detection d'anomalies

Ce document formalise l'objectif 2 du memoire:

> Etudier, comparer et choisir des approches classiques et intelligentes pour la detection d'anomalies dans les journaux.

L'objectif n'est pas seulement de lancer un modele IA. Il faut montrer une demarche comparative: partir de methodes simples et explicables, puis evaluer des modeles non supervises legers capables de fonctionner sur une machine standard.

## Approches Retenues

| Approche | Type | Role dans le projet | Fichier |
| --- | --- | --- | --- |
| Baseline par regles | Heuristique explicable | Point de comparaison simple | `src/logminer/agents/baseline_detector.py` |
| z-score | Statistique | Ecart maximal a la moyenne | `src/logminer/agents/model_compare.py` |
| IQR | Statistique robuste | Sortie des bornes interquartiles | `src/logminer/agents/model_compare.py` |
| Histogramme | Statistique explicable | Rarete des valeurs event/source/severite | `src/logminer/agents/model_compare.py` |
| Isolation Forest | IA non supervisee | Modele principal initial | `src/logminer/agents/detector.py` |
| k-Means | IA non supervisee | Distance au groupe le plus proche | `src/logminer/agents/model_compare.py` |
| One-Class SVM | IA non supervisee | Comparaison ML classique | `src/logminer/agents/model_compare.py` |
| Local Outlier Factor | IA non supervisee | Comparaison par densite locale | `src/logminer/agents/model_compare.py` |
| Autoencoder MLP | IA / deep learning leger | Erreur de reconstruction | `src/logminer/agents/model_compare.py` |
| LSTM TensorFlow/PyTorch | IA sequence optionnelle | Prediction de sequence d'evenements | `src/logminer/agents/model_compare.py` |

## Pourquoi Ces Methodes

- La baseline par regles donne un resultat interpretable: severite, categorie securite, mots suspects et rarete.
- z-score, IQR et histogramme donnent des references statistiques simples, utiles pour expliquer les anomalies sans modele opaque.
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

- statistiques: `rule_baseline`, `z_score`, `iqr`, `histogram`;
- IA tabulaire: `isolation_forest`, `kmeans`, `one_class_svm`, `local_outlier_factor`, `autoencoder_mlp`;
- IA sequence: `lstm_tensorflow` ou `lstm_pytorch`, marque comme ignore si aucun backend deep learning n'est installe.

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
| `precision`, `recall`, `f1` | Ajoutes seulement si une colonne de labels est fournie |

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
python src\logminer\agents\model_compare.py -i data\processed\dataset_labelise.csv --label-column label
```

## Etat Actuel

Fait:

- baseline explicable;
- z-score, IQR et histogramme;
- Isolation Forest operationnel;
- comparaison avec k-Means, One-Class SVM, LOF et Autoencoder MLP;
- prototype LSTM TensorFlow prioritaire avec secours PyTorch;
- export CSV comparatif;
- compatibilite future avec labels.

Reste a faire:

- tester sur datasets labellises HDFS/BGL;
- ajuster les features pour les logs reseau;
- integrer les resultats dans le chapitre 2 et le chapitre 5 du memoire.
