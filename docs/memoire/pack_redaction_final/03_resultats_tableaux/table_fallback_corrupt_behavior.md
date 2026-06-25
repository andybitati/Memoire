# Comportement Du Modele Fallback Sur Entree Corrompue

| Scenario | Lignes conservees | Famille routee | Confiance routeur | Anomalies candidates | Incidents | Routeur s | Detection s | Correlation s |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `corrupt_incomplete.log` normalise en `unknown` | 2 | fallback | 141 | 0 | 0 | 0.0517 | 0.2317 | 0.0799 |

Note: le parseur conserve les lignes corrompues comme evenements `unknown`; le routeur les dirige vers le modele fallback afin d'eviter une rupture silencieuse ou une affectation abusive a une famille specialisee.
