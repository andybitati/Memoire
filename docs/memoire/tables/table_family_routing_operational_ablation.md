# Ablation Operationnelle Routage Familial

Comparaison entre une baseline globale limitee a un espace commun minimal et les configurations specialisees completes.

| Famille | Global common F1 | Family-aware full F1 | Delta F1 | Global FP/1000 | Family-aware FP/1000 |
| --- | --- | --- | --- | --- | --- |
| Linux/auth | 0.819404 | 0.916602 | 0.097198 | 48.800 | 29.120 |
| CICIDS2017 | 0.999132 | 0.997163 | -0.001969 | 0.067 | 1.037 |

Interpretation: the controlled common-space ablation isolates routing under the same feature space, while this operational comparison measures the full Logminer contribution for datasets with matching specialized artifacts. CIC-DDoS2019 is not merged with the official UNSW-NB15 ablation.
