# Splits Supervises Stricts

| Dataset | Split | Seeds | Test moy. | Precision | Rappel | F1 | PR-AUC | MCC | FP moy. | FN moy. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Linux/auth | server_holdout | 5 | 10000 | 0.887734 | 0.774720 | 0.826251 | 0.917113 | 0.683796 | 487.4 | 1126.4 |

Note: ces resultats completent les scores supervises. Les splits par serveur, fichier ou scenario reduisent le risque d'observations quasi identiques entre entrainement et test, mais ne constituent pas encore une validation industrielle multi-environnement.
