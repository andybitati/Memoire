# Resultats Principaux

| Famille | Dataset | Modele | Type | Resultat principal |
| --- | --- | --- | --- | --- |
| Windows | Security/Application/System | Isolation Forest | Non supervise | Anomalies candidates et incidents correles |
| Wazuh | Exports Janvier/Octobre/Decembre | Isolation Forest | Non supervise | 122563 evenements, 3676 anomalies candidates |
| Linux/auth | linux_auth_logs_* | RandomForest | Supervise | F1=0.916602 |
| CICIDS | MachineLearningCVE | RandomForest | Supervise | F1=0.997163 |
| UNSW/CIC-DDoS | UNSWNB15/CIC-DDoS | RandomForest | Supervise | F1=0.999965 |
| HDFS | HDFS logs | Ensemble/Isolation Forest | Non supervise | Meilleure selection autour de F1=0.599333 |
| BGL | BlueGene/L | Ensemble/Autoencoder/IForest | Non supervise | Meilleure selection autour de F1=0.994333 |
