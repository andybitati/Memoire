# Ablation Routage Familial

| Variante | Famille | Lignes test moy. | Precision | Rappel | F1 | PR-AUC | MCC | Faux positifs / 1000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_aware_models | CICIDS2017 | 3000 | 0.999733 | 0.998933 | 0.999333 | 0.999991 | 0.998667 | 0.133 |
| global_common_model | CICIDS2017 | 3000 | 0.999867 | 0.998400 | 0.999132 | 0.999990 | 0.998269 | 0.067 |
| family_aware_models | Linux/auth | 3000 | 0.879076 | 0.762133 | 0.816354 | 0.910390 | 0.663183 | 52.467 |
| global_common_model | Linux/auth | 3000 | 0.886446 | 0.761867 | 0.819404 | 0.909375 | 0.670966 | 48.800 |
| family_aware_models | UNSW-NB15 | 3000 | 0.990049 | 0.993867 | 0.991950 | 0.999480 | 0.983881 | 5.000 |
| global_common_model | UNSW-NB15 | 3000 | 0.990569 | 0.993867 | 0.992214 | 0.999571 | 0.984408 | 4.733 |
