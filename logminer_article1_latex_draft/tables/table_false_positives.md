# Faux Positifs Et Taux Associes

| Dataset | Modele | Lignes test | FP | TN | FPR | FP / 1000 lignes | Periode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Linux/auth | random_forest_linux_auth | 38942 | 1134 | 22866 | 0.047250 | 29.120 | Periode non calculable: metriques agregees sans horodatage ligne par ligne |
| CICIDS2017 | random_forest_cicids | 55924 | 58 | 29942 | 0.001933 | 1.037 | Periode non calculable: metriques agregees sans horodatage ligne par ligne |
| UNSW/CIC-DDoS | random_forest | 1474193 | 2 | 1168 | 0.001709 | 0.001 | Periode non calculable: metriques agregees sans horodatage ligne par ligne |
| bgl | ensemble_selected | 6000 | 17 | 2983 | 0.005667 | 2.833 | Validation controlee; periode non conservee dans le CSV de metriques |
| bgl | ensemble_global | 6000 | 17 | 2983 | 0.005667 | 2.833 | Validation controlee; periode non conservee dans le CSV de metriques |
| bgl | autoencoder_mlp | 6000 | 17 | 2983 | 0.005667 | 2.833 | Validation controlee; periode non conservee dans le CSV de metriques |
| hdfs | ensemble_selected | 6000 | 1202 | 1798 | 0.400667 | 200.333 | Validation controlee; periode non conservee dans le CSV de metriques |
| hdfs | ensemble_global | 6000 | 1199 | 1801 | 0.399667 | 199.833 | Validation controlee; periode non conservee dans le CSV de metriques |
| hdfs | autoencoder_mlp | 6000 | 1273 | 1727 | 0.424333 | 212.167 | Validation controlee; periode non conservee dans le CSV de metriques |
| simulated_windows | isolation_forest | 6000 | 0 | 5700 | 0.000000 | 0.000 | Validation controlee; periode non conservee dans le CSV de metriques |
| simulated_windows | rule_baseline | 6000 | 0 | 5700 | 0.000000 | 0.000 | Validation controlee; periode non conservee dans le CSV de metriques |
| simulated_windows | histogram | 6000 | 9 | 5691 | 0.001579 | 1.500 | Validation controlee; periode non conservee dans le CSV de metriques |
