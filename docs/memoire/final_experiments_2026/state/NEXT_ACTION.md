# NEXT ACTION

Phase: PHASE 4

Experiment: Mise à jour contrôlée des modèles — audit end-to-end

Last completed step: PHASE 3 terminée, 36/36 runs et deux états Drain3 vérifiés ; ancien versus strict documenté.

Next exact step: Identifier l'API et les scripts réels de comparaison/promotion, les formats de modèle et d'audit, puis définir un jeu d'évaluation gelé pour les trois cas.

Command to run: `rtk graphify query "controlled model update candidate promotion rejection backup audit implementation"`

Expected output: Carte exacte des fonctions, scripts et artefacts nécessaires pour exécuter promotion, rejet et min_delta sans simulation de score.

Files that must be read: fichiers retournés par Graphify pour la mise à jour des modèles, `state/DECISIONS.md`, `PHASE_3_COMPLETED.md`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, anciens rapports éditoriaux et multi-VM.

Success criterion: Distinguer le code existant et le dry-run des chemins réellement exécutables ; aucun modèle de production n'est touché, les modèles de test restent isolés sous final_experiments_2026.

If failure: Conserver tout candidat et audit, restaurer le modèle courant depuis le backup isolé et documenter le cas comme non évalué plutôt que simuler une promotion.
