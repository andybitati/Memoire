# NEXT ACTION

Phase: PHASE 6

Experiment: Évaluation du routeur réel — exécution du corpus figé

Last completed step: Routeur audité, protocole à neuf sources figé, dry-run de 81 fichiers validé et plan inscrit au ledger.

Next exact step: Construire les chunks à noms neutres, appeler réellement `route_model` une fois par fichier, puis calculer les métriques et la matrice de confusion.

Command to run: `rtk python scripts/run_router_evaluation.py --resume`

Expected output: 81 décisions détaillées, métriques par famille, matrice de confusion, rapport JSON, tableau et figure en français.

Files that must be read: `configs/router_evaluation_protocol.json`, `scripts/run_router_evaluation.py`, `src/logminer/agents/model_router.py`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, artefacts HDFS/BGL phase 3, modèles phase 4, anciens rapports éditoriaux et multi-VM.

Success criterion: 81 fichiers routés ou erreurs explicitement conservées ; `true_family`, `predicted_family`, marge, règles, fallback et modèle enregistrés ; métriques lisibles.

If failure: Conserver le corpus et les lignes déjà routées, enregistrer FAILED pour l'erreur technique, corriger sans modifier la vérité terrain puis reprendre.
