# NEXT ACTION

Phase: PHASE 9

Experiment: Analyse statistique transversale

Last completed step: Protocole phase 9 figé; runner compilé et dry-run validé; expérience enregistrée `PLANNED`.

Next exact step: Après checkpoint Git, construire les statistiques répétées, les effets par scénario et le registre des évaluations uniques; valider les comptages et les IC.

Command to run: `rtk python scripts/build_transversal_statistics.py --resume`

Expected output: 228 lignes de statistiques répétées, 4 comparaisons descriptives LogisticRegression contre candidats, 20 métriques d'évaluations uniques, rapport et tableau.

Files that must be read: `configs/transversal_statistics_protocol.json`, `scripts/build_transversal_statistics.py` et les trois sorties seulement.

Files that DO NOT need to be reread: mémoire complet, JSON de runs individuels si les CSV agrégés suffisent, modèles et états Drain3 binaires.

Success criterion: N, moyenne, écart-type, médiane, min, max et IC95 lorsque pertinents; aucune pseudo-réplication; tests appariés seulement si justifiés.

If failure: Produire des statistiques descriptives et documenter explicitement l'absence de test inférentiel justifiable.
