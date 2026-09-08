# NEXT ACTION

Phase: PHASE 4

Experiment: Mise à jour contrôlée — préparation des modèles isolés

Last completed step: Audit phase 4 terminé ; plan figé ; deux défauts du script corrigés ; outils de préparation/vérification créés.

Next exact step: Produire le bundle train, le CSV d'évaluation gelé et les trois modèles courants sous `phase_4/cases` ; enregistrer leurs hashes avant décision.

Command to run: `rtk python scripts/prepare_model_update_e2e.py`

Expected output: `model_update_preparation.json`, bundle/évaluation hashés et trois `current.joblib` isolés ; trois plans PLANNED dans le ledger.

Files that must be read: `configs/model_update_e2e_plan.json`, `scripts/prepare_model_update_e2e.py`, `scripts/monthly_model_retraining.py`.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, anciens rapports éditoriaux et multi-VM.

Success criterion: Évaluation commune non vide ; modèles courants et hashes présents ; candidats encore absents ; aucun chemin sous `models/` ciblé.

If failure: Conserver tout candidat et audit, restaurer le modèle courant depuis le backup isolé et documenter le cas comme non évalué plutôt que simuler une promotion.
