# EXPERIMENT HDFS/BGL STRICT — SUMMARY

Objectif: Remplacer l'ancienne expérience exploratoire par un protocole train/validation/test indépendant, avec Drain3 et toutes les statistiques ajustés sur train uniquement.

Protocole: Figé dans `configs/strict_sequence_protocol.json` avant inspection de la distribution des labels dans les nouvelles fenêtres.

Nombre de runs prévus: 36 résultats — 18 par dataset. Les trois méthodes déterministes ont un run chacune ; IsolationForest, AutoencoderMLP et EnsembleTrainCalibrated ont cinq seeds chacune.

Nombre terminé: 18 résultats HDFS ; préparation BGL en attente.

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

## Préparation HDFS vérifiée

- Train: 50 000 événements, 1 858 anomalies (3,716 %), 4 787 blocs, lignes source 3 327 689 à 3 377 688.
- Validation: 20 000 événements, 599 anomalies (2,995 %), 1 994 blocs, lignes source 7 812 940 à 7 832 939.
- Test gelé: 20 000 événements, 118 anomalies (0,590 %), 2 456 blocs, lignes source 10 048 066 à 10 068 065.
- Chevauchement de blocs entre partitions: zéro ; aucune ligne retirée pour chevauchement.
- Drain3 0.9.11: 13 clusters appris sur train, état de 1 212 octets, SHA-256 `18bc825effd29a8c4cd957d41d9a4502a2e47f905738dd6b193017056905ebd2`.
- Taux de templates inconnus: train 0 %, validation 0,095 %, test 1,880 %.
- Le SHA-256 du journal HDFS relu correspond au manifeste phase 0.

## Limites préspecifiées

- Les fenêtres contiguës ne couvrent qu'une partie de chaque log.
- Les labels HDFS sont définis au niveau bloc mais les métriques principales seront événementielles ; les blocs ne se recouvrent pas entre partitions retenues.
- Les seuils sont choisis sur validation labellisée et ne mesurent donc pas une détection entièrement non supervisée.
- La prévalence HDFS varie fortement entre train, validation et test ; aucun rééquilibrage n'est appliqué.
- Quatre ajustements MLP au moins ont atteint 80 itérations sans convergence complète ; la limite préspecifiée n'a pas été modifiée après observation.
- Les durées internes du bundle partagé ne sont pas attribuables à une méthode individuelle et sont exclues des résumés scientifiques.

## Chemins des artefacts prévus

- Runs: `data/processed/final_experiments_2026/phase_3/`.
- États Drain3: `data/processed/final_experiments_2026/drain3_train_state/`.
- Sorties: `hdfs_strict_drain3_{raw,summary}.csv`, `bgl_strict_drain3_{raw,summary}.csv`.
- Manifeste: `drain3_template_manifest.json`.
