# NEXT ACTION

Phase: PHASE 3

Experiment: HDFS/BGL — audit et préparation du protocole strict

Last completed step: PHASE 2 complète, 125/125 artefacts valides ; tableaux, agrégats et figures produits.

Next exact step: Lire le pipeline séquentiel existant, identifier précisément les fuites de l'ancien protocole et spécifier un split train/validation/test sans recouvrement avant tout nouveau run.

Command to run: `rtk powershell -NoProfile -Command "Get-Content scripts/evaluate_sequence_split.py,src/logminer/features/drain_templates.py,src/logminer/features/sequence_windows.py"`

Expected output: Carte exacte du pipeline actuel, liste des corrections nécessaires et configuration strict_sequence_protocol.json figée avant exécution.

Files that must be read: `scripts/evaluate_sequence_split.py`, `src/logminer/features/drain_templates.py`, `src/logminer/features/sequence_windows.py`, les entrées HDFS/BGL de `dataset_manifest_final.csv`, `state/DECISIONS.md`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, anciens rapports éditoriaux et multi-VM.

Success criterion: Split strict documenté ; Drain3 appris uniquement sur train puis état figé ; statistiques/scaler train-only ; seuil choisi sur validation ; test évalué une fois.

If failure: Écrire `INFORMATION À VÉRIFIER.` pour tout point non démontrable, consigner le blocage et ne pas réutiliser l'ancien résultat exploratoire comme validation stricte.
