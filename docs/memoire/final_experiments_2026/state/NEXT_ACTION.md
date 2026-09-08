# NEXT ACTION

Phase: PHASE 10

Experiment: Matrice affirmation→preuve

Last completed step: PHASE 9 terminée; 228 statistiques répétées, 4 effets et 20 mesures uniques; reprise idempotente validée.

Next exact step: Construire une ligne par affirmation importante avec expérience, artefact exact, résultat, statut autorisé, limite, section et action rédactionnelle.

Command to run: `rtk python scripts/build_final_evidence_matrices.py --claims-only`

Expected output: `final_claim_evidence_matrix.md` complet, couvrant D001–D029 et les expériences 1–9 sans réécriture du mémoire.

Files that must be read: `state/DECISIONS.md`, `state/ARTIFACT_INDEX.json`, `PHASE_0_COMPLETED.md` à `PHASE_9_COMPLETED.md` et les résumés hiérarchiques.

Files that DO NOT need to be reread: mémoire complet, JSON de runs individuels si les CSV agrégés suffisent, modèles et états Drain3 binaires.

Success criterion: Toute affirmation majeure a une preuve précise ou le statut NON SOUTENU/NON ÉVALUÉ; aucune valeur invalidée n'est réintroduite.

If failure: Marquer l'élément `INFORMATION À VÉRIFIER.` ou NON SOUTENU; ne rien inférer.
