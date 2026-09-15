# HDFS/BGL — ancien protocole vs protocole strict

| Dataset | Protocole | Split | Drain3 | Features | Seuil | N test | Prévalence test | Meilleure méthode | F1 | Statut |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- | ---: | --- |
| HDFS | old_exploratory | class-stratified chronological; HDFS additionally grouped | refit separately on each partition | partition-wide template statistics, including test | test ranking with fixed prediction quota | 1201 | 0.500416 | histogram_train_test | 0.652789 | EXPLORATORY |
| HDFS | new_strict_local | disjoint chronological source windows; HDFS blocks disjoint | fit train only, persisted, reloaded and frozen | train-only template/source statistics; causal past-only windows | selected on validation, applied once to frozen test | 20000 | 0.005900 | Histogram | 0.269307 | STRICT_LOCAL_VALIDATION |
| BGL | old_exploratory | class-stratified chronological; HDFS additionally grouped | refit separately on each partition | partition-wide template statistics, including test | test ranking with fixed prediction quota | 1200 | 0.500000 | isolation_forest_train_test | 1.000000 | EXPLORATORY |
| BGL | new_strict_local | disjoint chronological source windows; HDFS blocks disjoint | fit train only, persisted, reloaded and frozen | train-only template/source statistics; causal past-only windows | selected on validation, applied once to frozen test | 19908 | 0.144917 | Histogram | 0.913698 | STRICT_LOCAL_VALIDATION |

Les variations de F1 ne sont pas des effets causaux attribuables à Drain3 seul : split, prévalence, volumes, features et règle de seuil changent simultanément. Le tableau documente une différence de protocole, pas une ablation contrôlée.
