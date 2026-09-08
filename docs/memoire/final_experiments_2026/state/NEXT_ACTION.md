# NEXT ACTION

Phase: PHASE 3

Experiment: BGL — préparation stricte train/validation/test

Last completed step: HDFS strict terminé, 18/18 artefacts valides ; meilleur F1 0,269307 pour Histogram.

Next exact step: Extraire les trois fenêtres BGL gelées, ajuster Drain3 uniquement sur train, sauvegarder/recharger l'état et produire le bundle causal.

Command to run: `rtk .\.venv-final-experiments\Scripts\python.exe scripts/run_strict_sequence_experiments.py --dataset bgl --prepare-only`

Expected output: Trois CSV BGL préparés, bundle NPZ, état Drain3 persistant et manifeste mis à jour.

Files that must be read: `configs/strict_sequence_protocol.json`, `scripts/run_strict_sequence_experiments.py`, `state/EXPERIMENT_LEDGER.csv`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, anciens rapports éditoriaux et multi-VM.

Success criterion: Trois partitions BGL non vides et chronologiquement ordonnées ; labels non utilisés pour la sélection ; état Drain3 non vide et hashé.

If failure: Conserver le log, ne pas modifier les fenêtres après lecture des labels pour améliorer les résultats, corriger uniquement un défaut technique puis reprendre explicitement.
