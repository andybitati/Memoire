# Ablation Routage Familial

| Variante | Famille | Lignes test moy. | Precision | Rappel | F1 | PR-AUC | MCC | Faux positifs / 1000 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| family_aware_models | CICIDS2017 | 3000 | 0.999778 | 0.998889 | 0.999333 | 0.999986 | 0.998667 | 0.111 |
| global_common_model | CICIDS2017 | 3000 | 1.000000 | 0.997778 | 0.998887 | 0.999984 | 0.997782 | 0.000 |
| family_aware_models | Linux/auth | 3000 | 0.880328 | 0.764444 | 0.818254 | 0.910388 | 0.666298 | 52.000 |
| global_common_model | Linux/auth | 3000 | 0.886501 | 0.761778 | 0.819388 | 0.909306 | 0.670928 | 48.778 |
| family_aware_models | UNSW-NB15 | 3000 | 0.990058 | 0.994000 | 0.992020 | 0.999544 | 0.984018 | 5.000 |
| global_common_model | UNSW-NB15 | 3000 | 0.990262 | 0.993556 | 0.991904 | 0.999587 | 0.983788 | 4.889 |
