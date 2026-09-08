# PHASE 3 COMPLETED

Objectif: Remplacer l'ancienne expérience HDFS/BGL exploratoire par une validation locale train/validation/test sans apprentissage sur test.

Protocole: Fenêtres contiguës centrées à 30 %, 70 % et 90 % des journaux, appartenant respectivement aux plages source 0–60 %, 60–80 % et 80–100 %. La sélection ne consulte pas les labels. HDFS exclut les lignes sans bloc labellable et impose des blocs disjoints. Drain3 0.9.11 est ajusté uniquement sur train, persisté, rechargé puis utilisé par `match` sans mise à jour. Les fréquences, vocabulaire, scaler, IQR et calibrations sont appris sur les lignes normales du train. Les fenêtres de 30 minutes sont causales et réinitialisées à chaque partition. Le seuil maximise le F1 de validation avec départage par FPR, MCC puis seuil ; il est appliqué une seule fois au test gelé.

Runs prévus: 36 — 18 par dataset.

Runs terminés: 36.

Runs échoués: 0.

Résultats principaux:

- HDFS: Histogram meilleur F1 `0,269307`, précision `0,175711`, rappel `0,576271`, PR-AUC `0,099431`, MCC `0,311464`, FPR `0,016045`.
- HDFS: IQR est presque identique par F1 (`0,268775`) et a la meilleure PR-AUC (`0,154748`).
- HDFS ensemble, cinq seeds: F1 `0,242946 ± 0,010487`.
- BGL: Histogram meilleur F1 `0,913698`, précision `0,841108`, rappel `1`, PR-AUC `0,841108`, MCC `0,902319`, FPR `0,032016`.
- BGL AutoencoderMLP, cinq seeds: F1 `0,278511 ± 0,000997`, mais FPR `0,877859`.
- BGL IsolationForest et ensemble, cinq seeds: F1 `0,253473 ± 0,000048`, rappel `1`, FPR `0,998285`.

Réseaux de données:

- HDFS train/validation/test: 50 000/20 000/20 000 événements ; 1 858/599/118 anomalies ; zéro bloc partagé.
- BGL train/validation/test: 49 999/17 764/19 908 événements ; 0/8 126/2 885 anomalies.
- HDFS Drain3: 13 clusters, taux de templates inconnus test 1,880 %.
- BGL Drain3: 7 clusters, taux de templates inconnus test 89,808 %.
- Les SHA-256 des journaux HDFS et BGL correspondent au manifeste phase 0.
- Les hashes des états Drain3 sont identiques avant et après les 36 évaluations.

Résultat négatif éventuel:

- HDFS strict chute de `0,652789` exploratoire à `0,269307` descriptif.
- BGL strict chute de `1,000000` exploratoire à `0,913698` descriptif.
- La plupart des méthodes BGL deviennent quasi triviales sous le déplacement temporel et prédisent presque tous les événements positifs.
- Plusieurs autoencodeurs atteignent 80 itérations sans convergence complète ; le plafond n'a pas été modifié.

Artefacts:

- `configs/strict_sequence_protocol.json`.
- `data/processed/final_experiments_2026/phase_3/` — 36 JSON et bundles préparés.
- `data/processed/final_experiments_2026/drain3_train_state/` — deux états figés.
- `drain3_template_manifest.json`.
- `hdfs_strict_drain3_raw.csv`, `hdfs_strict_drain3_summary.csv`.
- `bgl_strict_drain3_raw.csv`, `bgl_strict_drain3_summary.csv`.
- `hdfs_bgl_old_vs_strict_protocol.csv`.
- `tables/hdfs_bgl_old_vs_strict_protocol.md`.
- `figures/hdfs_bgl_ancien_vs_strict_f1.png`.
- `figures/hdfs_bgl_strict_methodes_f1.png`.

Problèmes:

- Les fenêtres couvrent une fraction locale de chaque journal et ne constituent pas plusieurs splits temporels indépendants.
- La prévalence varie fortement ; elle n'est ni équilibrée ni corrigée.
- Les seuils utilisent les labels de validation : le système de score est non supervisé ou semi-supervisé selon la méthode, mais la décision finale est calibrée avec supervision.
- HDFS est évalué par événement bien que le label soit porté par le bloc.
- Les durées du bundle mutualisé ne sont pas comparables par méthode et sont exclues.

Conclusion scientifique: La phase 3 soutient une validation locale strictement séparée, pas une généralisation universelle. Histogram est le meilleur résultat sur les deux tests gelés. BGL reste favorable pour Histogram mais révèle un déplacement de templates extrême ; HDFS reste difficile. L'ancien score BGL parfait et l'ancien score HDFS ne doivent plus être présentés comme preuve principale.

Impact probable sur le mémoire: Remplacer la lecture “Drain3 train-test” actuelle par le protocole train/validation/test exact, les tailles/prévalences, les résultats stricts et les limites. Conserver les anciens chiffres uniquement dans une comparaison explicitement exploratoire.
