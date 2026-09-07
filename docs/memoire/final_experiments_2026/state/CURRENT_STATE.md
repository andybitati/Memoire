# CURRENT STATE

Last update: 2026-09-07
Git commit: 37bccf083f3c8e92a11377cf758cf1e9e183dee9
Active phase: PHASE 1
Active experiment: CICIDS2017 multi-seeds — batch DDoS
Status: READY

## Completed

- Détection du mode NEW.
- État Git et commit initial enregistrés.
- Arborescence isolée `final_experiments_2026` créée.
- Décisions scientifiques D001 à D008 figées.
- Runner central créé et validé en dry-run pour la phase 0 et le batch DDoS de la phase 1.
- Protocole CICIDS final figé dans un fichier de configuration distinct.
- Environnement et manifeste de 11 fichiers avec SHA-256 validés.
- PHASE 0 terminée.

## In progress

- Aucun run en cours.

## Pending

- Batch DDoS : cinq seeds RandomForest.
- Quatre autres batches holdout, puis contrôle random stratifié.
- Phases 2 à 12.

## Verified facts

- Aucun ancien artefact de preuve n'a été modifié.
- Le score F1 0,999965 est exclu des nouvelles expériences.
- Le dépôt avait six fichiers non suivis préexistants au démarrage de la mission.
- Le manifeste contient 8 fichiers CICIDS2017, 2 HDFS et 1 BGL, tous hashés.
- Le plan de phase 1 contient 30 runs : 25 holdout et 5 random stratifié.

## Open issues

- La provenance officielle des copies locales reste `INFORMATION À VÉRIFIER.`.
- Drain3 n'est pas installé dans l'interpréteur actuel.
- La mise à jour Graphify est bloquée par un accès refusé Windows.

## Important artifact paths

- `docs/memoire/final_experiments_2026/state/`
- `data/processed/final_experiments_2026/`
- `docs/memoire/final_experiments_2026/environment_final_experiments.json`
- `docs/memoire/final_experiments_2026/dataset_manifest_final.csv`
- `docs/memoire/final_experiments_2026/PHASE_0_COMPLETED.md`
