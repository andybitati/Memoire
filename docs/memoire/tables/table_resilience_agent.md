# Resilience Et Modes De Degradation

| Scenario | Etat actuel | Preuve | Conclusion |
| --- | --- | --- | --- |
| Redis indisponible | Supporte | FastAPI et dashboard fonctionnent sans Redis; bus JSONL/CSV reste exploitable | Degradation acceptable pour prototype local |
| Log corrompu/incomplet | Supporte | robustness_scalability_report.csv: statut kept_unknown | Pas de perte silencieuse; entree conservee |
| Agent collecteur sans acces admin | Supporte partiellement | Privilege agent genere une demande/lanceur admin | Le systeme ne contourne pas les droits OS |
| Arret volontaire d'un agent | Non prouve en campagne longue | Architecture modulaire V1/V2; pas de stress test prolonge | A presenter comme limite/perspective |
