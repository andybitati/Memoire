# Comparaison De Modeles CICIDS2017 En Holdout Strict

| Modele | Seeds | Test moy. | Precision | Rappel | F1 mu+-sigma | PR-AUC | MCC | FP moy. | FN moy. | Duree moy. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LogisticRegression | 5 | 6436 | 0.402899 | 0.189932 | 0.233670 +- 0.312455 | 0.458829 | 0.186858 | 40.0 | 1963.2 | 0.3663 s |
| RandomForest | 5 | 6436 | 0.390476 | 0.128650 | 0.157827 +- 0.347377 | 0.506615 | 0.146206 | 0.2 | 1921.0 | 1.8448 s |
| SGDLogistic | 5 | 6436 | 0.249990 | 0.112100 | 0.143598 +- 0.319155 | 0.501021 | 0.091464 | 32.8 | 1987.2 | 0.2927 s |
| ExtraTrees | 5 | 6436 | 0.381818 | 0.110900 | 0.143265 +- 0.317571 | 0.507360 | 0.125863 | 0.6 | 1992.0 | 1.1690 s |
| HistGradientBoosting | 5 | 6436 | 0.200000 | 0.001800 | 0.003568 +- 0.007978 | 0.569002 | 0.001050 | 3.6 | 2428.4 | 1.8532 s |

Note: les modeles utilisent les memes fichiers tenus hors entrainement, les memes features et les memes plafonds d'echantillonnage. Le test compare des candidats legers disponibles dans scikit-learn; il ne couvre pas XGBoost/LightGBM faute de dependances figees dans l'environnement de base.
