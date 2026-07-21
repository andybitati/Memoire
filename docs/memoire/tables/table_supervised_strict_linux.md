# Splits Supervises Stricts

| Dataset | Split | Seeds | Test moy. | Precision | Rappel | F1 | PR-AUC | MCC | FP moy. | FN moy. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Linux/auth | server_holdout | 3 | 10000 | 0.885681 | 0.784667 | 0.831046 | 0.917604 | 0.689281 | 504.3 | 1076.7 |

Note: ces resultats completent les scores supervises. Les splits par serveur, fichier ou scenario reduisent le risque d'observations quasi identiques entre entrainement et test, mais ne constituent pas encore une validation industrielle multi-environnement.

