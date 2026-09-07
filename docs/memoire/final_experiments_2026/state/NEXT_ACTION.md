# NEXT ACTION

Phase: PHASE 2

Experiment: Comparaison multi-modèles — RandomForest × Infiltration

Last completed step: Scénario Bot complet, 25/25 résultats disponibles.

Next exact step: Réutiliser les cinq résultats RandomForest Infiltration identiques de phase 1.

Command to run: `rtk python scripts/run_final_experiments.py --resume --phase 2 --scenario Infiltration --model RandomForest`

Expected output: Cinq artefacts RandomForest Infiltration `COMPLETED_REUSED`.

Files that must be read: `configs/cicids_final_protocol.json`, `state/EXPERIMENT_LEDGER.csv`, `dataset_manifest_final.csv`.

Files that DO NOT need to be reread: mémoire LaTeX complet, anciens rapports éditoriaux, anciens artefacts multi-VM.

Success criterion: Seeds 42 à 46 COMPLETED ; chaque artefact contient configuration, seed, run_id, confusion et métriques demandées.

If failure: Conserver les lignes FAILED et reprendre avec `--resume`; ne modifier ni scaler ni solveur après observation du test.
