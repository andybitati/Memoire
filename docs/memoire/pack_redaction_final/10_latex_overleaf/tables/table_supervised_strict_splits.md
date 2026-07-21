# Splits Supervises Stricts

| Dataset | Split | Seeds | Test moy. | Precision | Rappel | F1 | PR-AUC | MCC | FP moy. | FN moy. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CIC-DDoS2019 | file_or_scenario_holdout | 3 | 3075 | 0.999500 | 0.992000 | 0.995702 | 0.999971 | 0.991042 | 1.0 | 16.0 |
| CICIDS2017 | file_or_scenario_holdout | 3 | 7322 | 0.650794 | 0.213417 | 0.262298 | 0.740269 | 0.239864 | 0.7 | 2468.3 |
| Linux/auth | server_holdout | 3 | 10000 | 0.885681 | 0.784667 | 0.831046 | 0.917604 | 0.689281 | 504.3 | 1076.7 |

Note: ces resultats completent les scores supervises. Les splits par serveur, fichier ou scenario reduisent le risque d'observations quasi identiques entre entrainement et test, mais ne constituent pas encore une validation industrielle multi-environnement.

