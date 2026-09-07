# NEXT ACTION

Phase: PHASE 1

Experiment: CICIDS2017 multi-seeds — batch PortScan

Last completed step: Batch DDoS terminé et validé, 5/5 COMPLETED.

Next exact step: Lancer les cinq runs du scénario PortScan tenu à l'écart.

Command to run: `rtk python scripts/run_final_experiments.py --resume --phase 1 --experiment cicids_holdout_multiseed --scenario PortScan`

Expected output: Cinq artefacts JSON valides, cinq états finaux COMPLETED dans le ledger et résumés partiels CICIDS.

Files that must be read: `configs/cicids_final_protocol.json`, `state/EXPERIMENT_LEDGER.csv`, `dataset_manifest_final.csv`.

Files that DO NOT need to be reread: mémoire LaTeX complet, anciens rapports éditoriaux, anciens artefacts multi-VM.

Success criterion: Seeds 42 à 46 COMPLETED ; chaque artefact contient configuration, seed, run_id, confusion et métriques demandées.

If failure: Le runner écrit FAILED et le traceback ; corriger sans supprimer la ligne, puis reprendre explicitement avec `--resume`.
