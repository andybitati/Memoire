# NEXT ACTION

Phase: PHASE 2

Experiment: Comparaison multi-modèles — préparation et réutilisation RandomForest

Last completed step: PHASE 1 terminée, 30/30 runs COMPLETED et cinq figures validées visuellement.

Next exact step: Ajouter au runner une réutilisation traçable des 25 résultats RandomForest identiques de phase 1, puis valider le plan de phase 2 en dry-run.

Command to run: `rtk python scripts/run_final_experiments.py --resume --phase 2 --dry-run`

Expected output: 125 résultats planifiés, dont 25 RandomForest réutilisables et 100 nouveaux ajustements.

Files that must be read: `configs/cicids_final_protocol.json`, `state/EXPERIMENT_LEDGER.csv`, `dataset_manifest_final.csv`.

Files that DO NOT need to be reread: mémoire LaTeX complet, anciens rapports éditoriaux, anciens artefacts multi-VM.

Success criterion: Seeds 42 à 46 COMPLETED ; chaque artefact contient configuration, seed, run_id, confusion et métriques demandées.

If failure: Le runner écrit FAILED et le traceback ; corriger sans supprimer la ligne, puis reprendre explicitement avec `--resume`.
