# NEXT ACTION

Phase: PHASE 3

Experiment: HDFS — préparation stricte train/validation/test

Last completed step: Protocole phase 3 figé ; venv Drain3 isolé ; runner spécialisé validé en dry-run sur 36 plans.

Next exact step: Extraire les trois fenêtres HDFS gelées, supprimer tout bloc partagé, ajuster Drain3 uniquement sur train, sauvegarder/recharger l'état et produire le bundle de 19 features causales.

Command to run: `rtk .\.venv-final-experiments\Scripts\python.exe scripts/run_strict_sequence_experiments.py --dataset hdfs --prepare-only`

Expected output: Trois CSV HDFS préparés, bundle NPZ, état Drain3 persistant, manifeste avec hashes, effectifs, prévalences et taux de templates inconnus.

Files that must be read: `configs/strict_sequence_protocol.json`, `scripts/run_strict_sequence_experiments.py`, `state/EXPERIMENT_LEDGER.csv`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, anciens rapports éditoriaux et multi-VM.

Success criterion: Les trois partitions sont non vides, chronologiquement ordonnées et sans bloc HDFS partagé ; l'état Drain3 est non vide et hashé ; validation/test n'appellent jamais `add_log_message`.

If failure: Conserver le log, ne pas modifier les fenêtres après lecture des labels pour améliorer les résultats, corriger uniquement un défaut technique puis reprendre explicitement.
