# NEXT ACTION

Phase: PHASE 4

Experiment: Mise à jour contrôlée — exécution end-to-end réelle

Last completed step: Bundle, évaluation gelée et trois modèles courants isolés présents et hashés ; candidats absents ; affichage console corrigé.

Next exact step: Lancer l'entraînement réel des trois candidats, comparer courant/candidat sur le même CSV gelé et autoriser uniquement la branche dont delta ≥ 0,02.

Command to run: `rtk python scripts/monthly_model_retraining.py --plan docs/memoire/final_experiments_2026/configs/model_update_e2e_plan.json --audit-path data/processed/final_experiments_2026/phase_4/model_update_audit.jsonl --feedback-csv data/processed/final_experiments_2026/phase_4/feedback.csv --report-out data/processed/final_experiments_2026/phase_4/model_update_end_to_end_report.json --backups-dir data/processed/final_experiments_2026/phase_4/backups --promote`

Expected output: Rapport JSON avec trois scores/deltas/décisions, un backup et une promotion seulement pour le cas éligible, audit isolé.

Files that must be read: `configs/model_update_e2e_plan.json`, `scripts/prepare_model_update_e2e.py`, `scripts/monthly_model_retraining.py`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, anciens rapports éditoriaux et multi-VM.

Success criterion: Un candidat réellement promu avec backup, un rejet moins bon, un gain positif inférieur à 0,02 sans promotion ; aucun modèle de production touché.

If failure: Conserver tout candidat et audit, restaurer le modèle courant depuis le backup isolé et documenter le cas comme non évalué plutôt que simuler une promotion.
