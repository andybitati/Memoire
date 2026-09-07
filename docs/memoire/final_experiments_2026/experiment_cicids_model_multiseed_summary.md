# EXPERIMENT CICIDS MODEL MULTISEED — SUMMARY

Objectif: Comparer cinq modèles sur les mêmes cinq scénarios holdout et cinq seeds, selon plusieurs métriques et coûts.

Protocole: 5 modèles × 5 scénarios × 5 seeds. Données, caractéristiques, plafonds et splits identiques à la phase 1. Les 25 résultats RandomForest sont réutilisés sans refit car ils sont strictement identiques ; chaque artefact de phase 2 porte `execution_kind=REUSED_IDENTICAL_PHASE1_RESULT` et le chemin de sa source.

Nombre de résultats prévus: 125.

Nombre terminé: 75.

Nombre de nouveaux ajustements terminés: 60.

Nombre réutilisé: 15.

Nombre échoué: 0.

## Résultats agrégés disponibles

| Modèle | Scénario terminé | Résultats | F1 moyen disponible | Statut |
| --- | --- | ---: | ---: | --- |
| RandomForest | DDoS | 5 | 0,778774 | Réutilisé depuis PHASE 1 |
| ExtraTrees | DDoS | 5 | 0,707001 | Ajusté en PHASE 2 |
| HistGradientBoosting | DDoS | 5 | 0,016809 | Ajusté en PHASE 2 après reprise hors bac à sable |
| LogisticRegression | DDoS | 5 | 0,720357 | Ajusté en PHASE 2 |
| SGDLogistic | DDoS | 5 | 0,715936 | Ajusté en PHASE 2 |
| RandomForest | PortScan | 5 | 0,009947 | Réutilisé depuis PHASE 1 |
| ExtraTrees | PortScan | 5 | 0,008955 | Ajusté en PHASE 2 |
| HistGradientBoosting | PortScan | 5 | 0,000000 | Ajusté hors bac à sable en PHASE 2 |
| LogisticRegression | PortScan | 5 | 0,000497 | Ajusté en PHASE 2 |
| SGDLogistic | PortScan | 5 | 0,000000 | Ajusté en PHASE 2 |
| RandomForest | Bot | 5 | 0,000000 | Réutilisé depuis PHASE 1 |
| ExtraTrees | Bot | 5 | 0,000000 | Ajusté en PHASE 2 |
| HistGradientBoosting | Bot | 5 | 0,000000 | Ajusté hors bac à sable en PHASE 2 |
| LogisticRegression | Bot | 5 | 0,000000 | Ajusté en PHASE 2 |
| SGDLogistic | Bot | 5 | 0,000000 | Ajusté en PHASE 2 |

## Résultats importants

- Sur DDoS uniquement, RandomForest a le meilleur F1 moyen disponible (`0,778774`) et ExtraTrees la meilleure PR-AUC moyenne (`0,954894` contre `0,910292`).
- HistGradientBoosting détecte très peu de DDoS au seuil courant : F1 moyen `0,016809`, rappel moyen `0,008500`, malgré une PR-AUC moyenne `0,853632`.
- LogisticRegression obtient exactement le même F1 `0,720357` sur les cinq seeds DDoS ; sa PR-AUC moyenne est `0,811788` et son temps d'entraînement moyen `0,274312 s`.
- SGDLogistic obtient F1 moyen `0,715936`, PR-AUC `0,861798` et temps d'entraînement moyen `0,213420 s`.
- Classement DDoS par F1 : RandomForest, LogisticRegression, SGDLogistic, ExtraTrees, HistGradientBoosting.
- Classement DDoS par PR-AUC : ExtraTrees, RandomForest, SGDLogistic, HistGradientBoosting, LogisticRegression.
- ExtraTrees ne corrige pas PortScan : F1 moyen `0,008955`, rappel `0,004500`, PR-AUC `0,855074`.
- HistGradientBoosting ne produit aucun vrai positif PortScan : F1 et rappel nuls, PR-AUC moyenne `0,804916`.
- LogisticRegression ne corrige pas PortScan : F1 `0,000497`, rappel `0,000250`, PR-AUC `0,527866`.
- Aucun des cinq modèles ne généralise utilement à PortScan au seuil courant. RandomForest a le F1 moyen le moins faible (`0,009947`) ; les PR-AUC montrent toutefois un classement partiellement informatif pour RandomForest, ExtraTrees, HistGradientBoosting et SGDLogistic.
- ExtraTrees ne produit aucun vrai positif Bot ; PR-AUC moyenne `0,440980`, supérieure au RandomForest mais sans décision positive utile au seuil courant.
- HistGradientBoosting ne produit aucun vrai positif Bot ; PR-AUC moyenne `0,475149`.
- LogisticRegression ne produit aucun vrai positif Bot et génère en moyenne 77 faux positifs ; PR-AUC `0,313997`, inférieure à la prévalence positive `0,329534`.
- Les cinq modèles ont F1=0 et rappel=0 sur Bot. La meilleure PR-AUC est `0,485505` pour SGDLogistic, sans vrai positif au seuil courant.

## Résultat négatif éventuel

- Les cinq premières tentatives HistGradientBoosting ont échoué à cause des restrictions de pipes Windows du bac à sable. Les reprises hors bac à sable ont réussi et les échecs restent dans le ledger.

## Limites

- Résumé partiel : 50 résultats restent à produire ou réutiliser.
- Le classement DDoS ne doit pas être présenté comme classement final avant les quatre autres scénarios.
- Les temps du RandomForest sont ceux de l'exécution source de phase 1, pas de nouveaux chronométrages.

## Chemins des artefacts

- Runs : `data/processed/final_experiments_2026/phase_2/`
- Brut : `data/processed/final_experiments_2026/cicids_model_multiseed_raw.csv`
- Résumé : `data/processed/final_experiments_2026/cicids_model_multiseed_summary.csv`
- Arbitrages : `data/processed/final_experiments_2026/cicids_model_tradeoffs.csv`
