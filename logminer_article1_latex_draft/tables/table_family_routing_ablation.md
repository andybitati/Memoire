# Ablation Routage Familial

| Variante | Famille | Lignes test | Precision | Rappel | F1 | Faux positifs / 1000 |
| --- | --- | --- | --- | --- | --- | --- |
| family_aware_models | cicids | 3000 | 1.000000 | 0.999333 | 0.999667 | 0.000 |
| global_common_model | cicids | 3000 | 1.000000 | 0.999333 | 0.999667 | 0.000 |
| family_aware_models | linux_auth | 3000 | 0.877395 | 0.763333 | 0.816399 | 53.333 |
| global_common_model | linux_auth | 3000 | 0.885233 | 0.771333 | 0.824368 | 50.000 |
| family_aware_models | unsw | 3000 | 0.995989 | 0.993333 | 0.994660 | 2.000 |
| global_common_model | unsw | 3000 | 0.996660 | 0.994667 | 0.995662 | 1.667 |
