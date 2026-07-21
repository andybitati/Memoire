# Ablation Operationnelle Routage Familial

Comparaison entre une baseline globale limitee a un espace commun minimal et les configurations specialisees completes.

| Famille | Global common F1 | Family-aware full F1 | Delta F1 | Global FP/1000 | Family-aware FP/1000 |
| --- | --- | --- | --- | --- | --- |
| Linux/auth | 0.819388 | 0.916602 | 0.097214 | 48.778 | 29.120 |
| CICIDS2017 | 0.998887 | 0.997163 | -0.001724 | 0.000 | 1.037 |

Interpretation: the controlled common-space ablation isolates routing under the same feature space, while this operational comparison measures the full Logminer contribution for datasets with matching specialized artifacts. CIC-DDoS2019 is not merged with the official UNSW-NB15 ablation.
