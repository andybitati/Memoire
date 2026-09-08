# NEXT ACTION

Phase: PHASE 8

Experiment: Corrélation d'incidents synthétique — audit GO/NO-GO

Last completed step: Protocole phase 8 figé et dry-run validé: 19 entrées, 16 anomalies, 6 incidents vrais et 3 bruits.

Next exact step: Après checkpoint Git du protocole, exécuter l'unique run, valider le résumé, les 120 paires, le tableau et la figure, puis tester la reprise idempotente.

Command to run: `rtk python scripts/run_correlation_synthetic_validation.py --resume`

Expected output: Un résumé `COMPLETED`, 120 paires évaluées, métriques pairwise, fragmentation, fusion incorrecte et exclusion du bruit.

Files that must be read: `configs/correlation_synthetic_protocol.json`, `scripts/run_correlation_synthetic_validation.py` et les sorties phase 8 seulement.

Files that DO NOT need to be reread: mémoire complet, artefacts CICIDS unitaires, JSON HDFS/BGL, modèles phase 4 et anciens rapports multi-VM.

Success criterion: Entrée sans vérité cachée, 16 anomalies couvertes exactement une fois, 120 paires, métriques cohérentes, artefacts lisibles et second `--resume` retournant `SKIPPED_ALREADY_COMPLETED`.

If failure: Conserver la trace `FAILED`, ne pas adapter les scénarios au résultat, corriger uniquement un défaut d'exécution démontré puis reprendre explicitement.
