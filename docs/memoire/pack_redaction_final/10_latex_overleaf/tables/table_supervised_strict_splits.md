# Splits Supervises Stricts

| Dataset | Split | Seeds | Test moy. | Precision | Rappel | F1 | PR-AUC | MCC | FP moy. | FN moy. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CIC-DDoS2019 | file_or_scenario_holdout | 5 | 2677 | 0.999598 | 0.995600 | 0.997577 | 0.999991 | 0.994091 | 0.8 | 8.8 |
| CICIDS2017 | file_or_scenario_holdout | 5 | 6436 | 0.390476 | 0.128650 | 0.157827 | 0.506615 | 0.146206 | 0.2 | 1921.0 |
| Linux/auth | server_holdout | 5 | 10000 | 0.887734 | 0.774720 | 0.826251 | 0.917113 | 0.683796 | 487.4 | 1126.4 |

Note: ces resultats sont calcules sur cinq graines. Les holdouts tiennent hors entrainement des serveurs, fichiers ou scenarios entiers; CICIDS2017 utilise les memes hyperparametres que le modele reseau principal dans la comparaison controlee.
