# Ablation Operationnelle Routage Familial

Comparaison entre une baseline globale limitee a un espace commun minimal et les configurations specialisees completes.

| Famille | Global common F1 | Family-aware full F1 | Delta F1 | Global FP/1000 | Family-aware FP/1000 |
| --- | --- | --- | --- | --- | --- |
| linux_auth | 0.824368 | 0.916602 | 0.092234 | 50.000 | 29.120 |
| cicids | 0.999667 | 0.997163 | -0.002503 | 0.000 | 1.037 |
| unsw | 0.995662 | 0.999965 | 0.004303 | 1.667 | 0.001 |

Interpretation: the controlled common-space ablation isolates routing under the same feature space, while this operational comparison measures the full Logminer contribution: family detection, native feature compatibility and specialized model selection.
