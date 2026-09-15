# EXPERIMENT HDFS/BGL STRICT — SUMMARY

Objectif: Remplacer l'ancienne expérience exploratoire par un protocole train/validation/test indépendant, avec Drain3 et toutes les statistiques ajustés sur train uniquement.

Protocole: Figé dans `configs/strict_sequence_protocol.json` avant inspection de la distribution des labels dans les nouvelles fenêtres.

Nombre de runs prévus: 36 résultats — 18 par dataset. Les trois méthodes déterministes ont un run chacune ; IsolationForest, AutoencoderMLP et EnsembleTrainCalibrated ont cinq seeds chacune.

Nombre terminé: 36/36 résultats — 18 HDFS et 18 BGL.

Nombre échoué: 0.

## Audit de l'ancien pipeline

- `drain3_templates()` construit un nouveau `TemplateMiner` à chaque appel ; train et test obtenaient donc des espaces de templates séparés.
- `add_sequence_window_features()` calcule `template_totals` sur la partition entière, y compris le test.
- `evaluate_sequence_split.py` ne possède pas de partition validation.
- `_top_by_score()` impose au test un nombre de positifs dérivé d'un quota au lieu d'appliquer un seuil figé sur validation.
- `_rank_strength()` calcule des rangs sur les scores du test pour l'ensemble.
- Les anciens CSV sont équilibrés à environ 50/50 et le split est chronologique séparément dans chaque classe.

Conclusion de l'audit: Les anciens résultats HDFS/BGL restent `EXPLORATOIRE` conformément à D004.

## Résultats agrégés disponibles

| Dataset | Méthode | N | F1 moyen | Écart-type | Précision | Rappel | PR-AUC | MCC | FPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| HDFS | Histogram | 1 | 0,269307 | n/a | 0,175711 | 0,576271 | 0,099431 | 0,311464 | 0,016045 |
| HDFS | IQR | 1 | 0,268775 | n/a | 0,175258 | 0,576271 | 0,154748 | 0,311042 | 0,016095 |
| HDFS | EnsembleTrainCalibrated | 5 | 0,242946 | 0,010487 | 0,154410 | 0,571186 | 0,090662 | 0,289505 | 0,018630 |
| HDFS | ZScore | 1 | 0,226230 | n/a | 0,140244 | 0,584746 | 0,110571 | 0,278582 | 0,021276 |
| HDFS | AutoencoderMLP | 5 | 0,214286 | 0,015815 | 0,131259 | 0,586441 | 0,095514 | 0,269074 | 0,023207 |
| HDFS | IsolationForest | 5 | 0,204530 | 0,004496 | 0,123291 | 0,600000 | 0,079169 | 0,263521 | 0,025340 |

Le meilleur F1 HDFS strict est `0,269307` pour Histogram. Il est descriptif pour ce test gelé de 20 000 événements et 118 anomalies ; la faible prévalence explique notamment que le rappel supérieur à 0,57 coexiste avec une précision inférieure à 0,18.

| Dataset | Méthode | N | F1 moyen | Écart-type | Précision | Rappel | PR-AUC | MCC | FPR |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| BGL | Histogram | 1 | 0,913698 | n/a | 0,841108 | 1,000000 | 0,841108 | 0,902319 | 0,032016 |
| BGL | AutoencoderMLP | 5 | 0,278511 | 0,000997 | 0,161791 | 0,999792 | 0,467383 | 0,140318 | 0,877859 |
| BGL | ZScore | 1 | 0,277885 | n/a | 0,161362 | 1,000000 | 0,161472 | 0,138683 | 0,880808 |
| BGL | IQR | 1 | 0,265446 | n/a | 0,153034 | 1,000000 | 0,428025 | 0,097433 | 0,937966 |
| BGL | EnsembleTrainCalibrated | 5 | 0,253473 | 0,000048 | 0,145129 | 1,000000 | 0,162227 | 0,015745 | 0,998285 |
| BGL | IsolationForest | 5 | 0,253473 | 0,000048 | 0,145129 | 1,000000 | 0,146129 | 0,015745 | 0,998285 |

Le meilleur F1 BGL strict est `0,913698` pour Histogram : 2 885/2 885 anomalies détectées, 545 faux positifs et 16 478 vrais négatifs. Les autres méthodes ont un FPR compris entre 0,877859 et 0,998285, malgré un rappel proche de 1.

## Préparation HDFS vérifiée

- Train: 50 000 événements, 1 858 anomalies (3,716 %), 4 787 blocs, lignes source 3 327 689 à 3 377 688.
- Validation: 20 000 événements, 599 anomalies (2,995 %), 1 994 blocs, lignes source 7 812 940 à 7 832 939.
- Test gelé: 20 000 événements, 118 anomalies (0,590 %), 2 456 blocs, lignes source 10 048 066 à 10 068 065.
- Chevauchement de blocs entre partitions: zéro ; aucune ligne retirée pour chevauchement.
- Drain3 0.9.11: 13 clusters appris sur train, état de 1 212 octets, SHA-256 `18bc825effd29a8c4cd957d41d9a4502a2e47f905738dd6b193017056905ebd2`.
- Taux de templates inconnus: train 0 %, validation 0,095 %, test 1,880 %.
- Le SHA-256 du journal HDFS relu correspond au manifeste phase 0.

## Préparation BGL vérifiée

- Train: 49 999 événements, 0 anomalie, lignes source 1 399 389 à 1 449 388.
- Validation: 17 764 événements, 8 126 anomalies (45,744 %), lignes source 3 313 574 à 3 333 573.
- Test gelé: 19 908 événements, 2 885 anomalies (14,492 %), lignes source 4 263 167 à 4 283 166.
- La sélection des fenêtres n'utilise pas les labels ; les 2 237 lignes manquantes au total ne correspondaient pas au parseur BGL strict.
- Drain3 0.9.11: 7 clusters appris sur train, état de 864 octets, SHA-256 `43ef590469a379daf21f7b644b3fc2592ca66e74643353254e60659baf27db82`.
- Taux de templates inconnus: train 0 %, validation 84,367 %, test 89,808 %.
- Le SHA-256 du journal BGL relu correspond au manifeste phase 0.

## Limites préspecifiées

- Les fenêtres contiguës ne couvrent qu'une partie de chaque log.
- Les labels HDFS sont définis au niveau bloc mais les métriques principales seront événementielles ; les blocs ne se recouvrent pas entre partitions retenues.
- Les seuils sont choisis sur validation labellisée et ne mesurent donc pas une détection entièrement non supervisée.
- La prévalence HDFS varie fortement entre train, validation et test ; aucun rééquilibrage n'est appliqué.
- Quatre ajustements MLP au moins ont atteint 80 itérations sans convergence complète ; la limite préspecifiée n'a pas été modifiée après observation.
- Les durées internes du bundle partagé ne sont pas attribuables à une méthode individuelle et sont exclues des résumés scientifiques.
- BGL présente un déplacement temporel majeur de vocabulaire et de prévalence entre les trois fenêtres ; le protocole n'est pas modifié pour le réduire.

## Comparaison ancien versus strict

- HDFS: ancien meilleur F1 `0,652789` sur 1 201 événements équilibrés ; strict `0,269307` sur 20 000 événements à 0,590 % d'anomalies ; différence descriptive `-0,383482`.
- BGL: ancien meilleur F1 `1,000000` sur 1 200 événements équilibrés ; strict `0,913698` sur 19 908 événements à 14,492 % d'anomalies ; différence descriptive `-0,086302`.
- Ces différences ne sont pas une ablation causale de Drain3 : plusieurs dimensions du protocole changent simultanément.

## Chemins des artefacts prévus

- Runs: `data/processed/final_experiments_2026/phase_3/`.
- États Drain3: `data/processed/final_experiments_2026/drain3_train_state/`.
- Sorties: `hdfs_strict_drain3_{raw,summary}.csv`, `bgl_strict_drain3_{raw,summary}.csv`.
- Manifeste: `drain3_template_manifest.json`.
- Comparaison: `hdfs_bgl_old_vs_strict_protocol.csv` et `tables/hdfs_bgl_old_vs_strict_protocol.md`.
- Figures: `figures/hdfs_bgl_ancien_vs_strict_f1.png` et `figures/hdfs_bgl_strict_methodes_f1.png`.
