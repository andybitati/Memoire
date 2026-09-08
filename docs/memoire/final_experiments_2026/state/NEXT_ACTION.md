# NEXT ACTION

Phase: PHASE 9

Experiment: Analyse statistique transversale

Last completed step: PHASE 8 terminée; 1/1 run, 120 paires, F1 pairwise 0,812500, reprise idempotente validée.

Next exact step: Inventorier les CSV de synthèse des phases 1–8 et le benchmark monolithique/agents; définir quelles unités sont réellement répétées et quelles comparaisons appariées sont méthodologiquement admissibles.

Command to run: `rtk graphify query "Quels artefacts agrègent les métriques multi-seeds CICIDS, HDFS/BGL, routeur, multiformat, corrélation et benchmark monolithique agents ?"`

Expected output: Liste ciblée des fichiers de synthèse permettant un tableau transversal sans confondre seeds, scénarios, méthodes déterministes et tâches.

Files that must be read: CSV de synthèse indexés, rapports PHASE_1 à PHASE_8 et artefact exact du benchmark D008.

Files that DO NOT need to be reread: mémoire complet, JSON de runs individuels si les CSV agrégés suffisent, modèles et états Drain3 binaires.

Success criterion: N, moyenne, écart-type, médiane, min, max et IC95 lorsque pertinents; aucune pseudo-réplication; tests appariés seulement si justifiés.

If failure: Produire des statistiques descriptives et documenter explicitement l'absence de test inférentiel justifiable.

