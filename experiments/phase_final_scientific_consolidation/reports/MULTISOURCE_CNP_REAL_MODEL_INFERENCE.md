# CNP multi-source avec inférence réelle des modèles routés

Run : `multisource_cnp_model_inference_20260911T003432Z`. Les conditions H et M traitent chacune `1401` unités via de vrais agents et le protocole Contract Net.

## Registre de compatibilité

Le registre a été figé avant l’exécution. Un artefact n’est appelé que lorsque son schéma et l’unité d’entrée sont compatibles. Apache reste un fallback heuristique explicite, car la fixture d’une ligne n’expose pas les champs HTTP structurés nécessaires.

## Résultats

| Condition | Inférences modèle | Fallbacks heuristiques | Unsupported | Erreurs | Refus | Réattributions | Anomalies candidates | Incidents candidats | Latence moyenne (s) | P95 (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| H | 0 | 1401 | 0 | 0 | 2602 | 0 | 139 | 24 | 0.031027 | 0.068247 |
| M | 1400 | 1 | 0 | 0 | 2602 | 0 | 142 | 44 | 0.105420 | 0.181044 |

## Ressources

H : temps mur `43.483159 s`, temps processus `42.609375 s`, RSS avant/après `220266496`/`229826560` octets. M : temps mur `147.713929 s`, temps processus `131.625000 s`, RSS avant/après `243916800`/`361304064` octets.

Le RSS est un instantané du processus, pas un pic isolé par source. La condition M conserve les sept artefacts compatibles en cache ; la variation ne doit pas être interprétée comme une consommation stable en production.

## Vérité terrain

Aucune accuracy globale n’est calculée. Les métriques prédictives de M sont séparées par source lorsque l’unité et le label sont compatibles. Pour H, elles sont `NON ÉVALUÉ` car la règle historique utilise directement les labels disponibles sur les entrées labellisées ; les présenter comme prédictions serait circulaire.

Les sorties sans vérité terrain restent des anomalies et incidents candidats. Elles ne constituent pas une accuracy.

## Limites

Cette campagne démontre le chargement et l’appel des artefacts compatibles dans une chaîne CNP locale. Elle ne démontre ni un gain prédictif global du routage, ni une validité industrielle, ni l’indépendance des sources par rapport aux données historiques d’apprentissage des artefacts.
