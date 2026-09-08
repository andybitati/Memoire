# Profilage Temporel Par Agent

| Scenario | Lignes | Routeur s | Routeur % | Detecteur s | Detecteur % | Correlateur s | Correlateur % | Total mesure s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Windows local normalise | 8537 | 0.0449 | 0.9 | 4.3460 | 91.3 | 0.3678 | 7.7 | 4.7587 |

Note: mesure locale directe sur `data/processed/windows_events.csv` apres instrumentation de `run_routed_detection`. Le temps total mesure ici couvre routage, detection et correlation, sans le surcout HTTP/FastAPI ni le temps de decouverte collecteur.
