# NEXT ACTION

Phase: PHASE 5

Experiment: Validation multiformat étendue — exécution des huit formats

Last completed step: Configuration phase 5 figée, runner compilé, dry-run validé et huit plans inscrits au ledger.

Next exact step: Exécuter les huit validations avec reprise idempotente, vérifier les quatre CSV agrégés et inspecter la figure.

Command to run: `rtk python scripts/run_multiformat_validation.py --resume`

Expected output: Huit artefacts par format, quatre CSV agrégés, un tableau et `figures/validation_multiformat.png`, avec toute défaillance conservée.

Files that must be read: `configs/multiformat_validation_protocol.json`, `scripts/run_multiformat_validation.py`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, artefacts HDFS/BGL phase 3, modèles phase 4, anciens rapports éditoriaux et multi-VM.

Success criterion: Les huit validations écrivent des métriques traçables ; les quatre CSV sont lisibles ; les comptes satisfont N_brut = N_normalisé + N_perdu ; aucune défaillance n'est masquée.

If failure: Conserver les artefacts déjà écrits, inscrire FAILED uniquement pour l'erreur d'infrastructure, corriger sans changer le protocole et relancer avec `--resume`.
