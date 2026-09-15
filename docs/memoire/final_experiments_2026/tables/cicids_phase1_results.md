# CICIDS2017 — PHASE 1

| Protocole | Scénario | N | Seeds | F1 moyen | Écart-type | PR-AUC | MCC | FPR | Limite |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Holdout fichier/scénario | Bot | 5 | 42,43,44,45,46 | 0.000000 | 0.000000 | 0.322471 | -0.003631 | 0.000100 | Sous-échantillon plafonné fixe |
| Holdout fichier/scénario | DDoS | 5 | 42,43,44,45,46 | 0.778774 | 0.001342 | 0.910292 | 0.684183 | 0.000000 | Sous-échantillon plafonné fixe |
| Holdout fichier/scénario | Infiltration | 5 | 42,43,44,45,46 | 0.000000 | 0.000000 | 0.015396 | 0.000000 | 0.000000 | 32 positifs/run |
| Holdout fichier/scénario | PortScan | 5 | 42,43,44,45,46 | 0.009947 | 0.000001 | 0.881982 | 0.045036 | 0.000350 | Sous-échantillon plafonné fixe |
| Holdout fichier/scénario | WebAttacks | 5 | 42,43,44,45,46 | 0.000000 | 0.000000 | 0.654341 | -0.003757 | 0.000100 | Sous-échantillon plafonné fixe |
| Split aléatoire stratifié | Tous scénarios, pool fixe | 5 | 42,43,44,45,46 | 0.995142 | 0.001013 | 0.999723 | 0.990305 | 0.003350 | Mélange aléatoire des captures |
