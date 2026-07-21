# Resultats Principaux

| Famille | Dataset | Modele | Type | Resultat principal |
| --- | --- | --- | --- | --- |
| Windows | Security/Application/System | Isolation Forest | Non supervise | Anomalies candidates et incidents correles |
| Wazuh | Exports Janvier/Octobre/Decembre | Isolation Forest | Non supervise | 122563 evenements, 3676 anomalies candidates |
| Linux/auth | linux_auth_logs_* | RandomForest | Supervise | F1=0.916602 |
| CICIDS | MachineLearningCVE | RandomForest | Supervise | F1=0.997163 |
| UNSW-NB15 | unsw_nb15_80_20 | RandomForest | Supervise exploratoire | F1=0.999965, protocole a revalider par split temporel/scenario |
| HDFS | HDFS logs | Drain3 + fenetres + histogramme/IF | Non supervise train-test | F1=0.652789 au mieux, amelioration moderee; HDFS reste difficile |
| BGL | BlueGene/L | Drain3 + fenetres + IForest | Non supervise train-test | F1=1.000000 sur split local; resultat favorable a ne pas generaliser seul |
