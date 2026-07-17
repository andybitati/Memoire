# Resultats Principaux

| Famille | Dataset | Modele | Type | Resultat principal |
| --- | --- | --- | --- | --- |
| Windows | Security/Application/System | Isolation Forest | Non supervise | Anomalies candidates et incidents correles |
| Wazuh | Exports Janvier/Octobre/Decembre | Isolation Forest | Non supervise | 122563 evenements, 3676 anomalies candidates |
| Linux/auth | linux_auth_logs_* | RandomForest | Supervise | F1=0.916602 |
| CICIDS | MachineLearningCVE | RandomForest | Supervise | F1=0.997163 |
| CIC-DDoS2019 | DrDoS/UDPLag/SYN | RandomForest | Supervise | F1=0.999965, protocole 80/20 exploratoire |
| HDFS | HDFS logs | Ensemble/Isolation Forest | Non supervise | Resultat exploratoire autour de F1=0.599333, non independant |
| BGL | BlueGene/L | Ensemble/Autoencoder/IForest | Non supervise | Resultat exploratoire autour de F1=0.994333, sensible au protocole |
