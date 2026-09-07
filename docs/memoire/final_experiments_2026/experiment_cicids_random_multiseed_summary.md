# EXPERIMENT CICIDS RANDOM MULTISEED — SUMMARY

Objectif: Établir un contrôle par split aléatoire stratifié avec la même représentation, le même RandomForest et des tailles comparables aux holdouts de scénario.

Protocole: Pool fixe équilibré de 24 000 flux construit à partir des huit fichiers CICIDS2017, puis split stratifié de 16 000 lignes d'entraînement et 8 000 lignes de test. Seeds 42 à 46 pour le split et le RandomForest. Les transformations sont appliquées avec le protocole figé `configs/cicids_final_protocol.json`.

Nombre de runs prévus: 5.

Nombre terminé: 5.

Nombre échoué: 0.

## Résultats agrégés

| N | F1 moyen | Écart-type | Médiane | Min | Max | IC 95 % demi-largeur | Précision | Rappel | PR-AUC | MCC | FPR |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 0,995142 | 0,001013 | 0,995493 | 0,993859 | 0,996372 | 0,001258 | 0,996640 | 0,993650 | 0,999723 | 0,990305 | 0,003350 |

## Résultats importants

- Le F1 reste supérieur à 0,9938 sur les cinq seeds du contrôle aléatoire.
- L'écart-type intra-protocole est faible : 0,001013.
- Le protocole aléatoire donne un F1 moyen supérieur de 0,837398 à la moyenne macro des cinq scénarios holdout.

## Résultat négatif éventuel

Le niveau élevé du split aléatoire ne se transfère pas aux scénarios entièrement absents du train. Il ne constitue donc pas une preuve de généralisation à une nouvelle famille ou capture.

## Limites

- Le pool est plafonné et équilibré ; il ne représente pas la prévalence opérationnelle.
- Les flux provenant de plusieurs captures sont mélangés avant le split. Une fuite par doublons n'a pas été démontrée, mais ce protocole ne protège pas la séparation par capture/scénario.
- Les cinq seeds modifient à la fois le split et l'aléa du RandomForest.
- La provenance officielle des copies locales reste `INFORMATION À VÉRIFIER.`.

## Chemins des artefacts

- Runs unitaires : `data/processed/final_experiments_2026/phase_1/e1_random_stratified_seed*.json`
- Brut : `data/processed/final_experiments_2026/cicids_random_multiseed_raw.csv`
- Résumé : `data/processed/final_experiments_2026/cicids_random_multiseed_summary.csv`
- Comparaison : `data/processed/final_experiments_2026/cicids_random_vs_holdout_summary.csv`

