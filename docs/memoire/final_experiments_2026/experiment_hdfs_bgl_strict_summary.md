# EXPERIMENT HDFS/BGL STRICT — SUMMARY

Objectif: Remplacer l'ancienne expérience exploratoire par un protocole train/validation/test indépendant, avec Drain3 et toutes les statistiques ajustés sur train uniquement.

Protocole: Figé dans `configs/strict_sequence_protocol.json` avant inspection de la distribution des labels dans les nouvelles fenêtres.

Nombre de runs prévus: 36 résultats — 18 par dataset. Les trois méthodes déterministes ont un run chacune ; IsolationForest, AutoencoderMLP et EnsembleTrainCalibrated ont cinq seeds chacune.

Nombre terminé: 0.

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

Aucun run strict terminé.

## Limites préspecifiées

- Les fenêtres contiguës ne couvrent qu'une partie de chaque log.
- Les labels HDFS sont définis au niveau bloc mais les métriques principales seront événementielles ; les blocs ne se recouvrent pas entre partitions retenues.
- Les seuils sont choisis sur validation labellisée et ne mesurent donc pas une détection entièrement non supervisée.

## Chemins des artefacts prévus

- Runs: `data/processed/final_experiments_2026/phase_3/`.
- États Drain3: `data/processed/final_experiments_2026/drain3_train_state/`.
- Sorties: `hdfs_strict_drain3_{raw,summary}.csv`, `bgl_strict_drain3_{raw,summary}.csv`.
- Manifeste: `drain3_template_manifest.json`.
