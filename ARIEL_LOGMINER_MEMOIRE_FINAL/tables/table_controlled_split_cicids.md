# Comparaison Controlee Des Splits

| Dataset | Split | Seeds | Test moy. | F1 mu+-sigma | PR-AUC mu+-sigma | MCC mu+-sigma | Rappel mu+-sigma |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CICIDS2017 | file_or_scenario_holdout | 5 | 6436 | 0.157827 +- 0.347377 | 0.506615 +- 0.412162 | 0.146206 +- 0.301650 | 0.128650 +- 0.284883 |
| CICIDS2017 | random_stratified_matched | 5 | 6436 | 0.999260 +- 0.000353 | 0.999998 +- 0.000000 | 0.998523 +- 0.000703 | 0.998622 +- 0.000777 |

Note: les variantes utilisent les memes features, hyperparametres, seeds et plafonds d'echantillonnage. Le split aleatoire est apparie aux tailles train/test du holdout pour chaque seed.
