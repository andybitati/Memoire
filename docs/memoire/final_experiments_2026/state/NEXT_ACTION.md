# NEXT ACTION

Phase: PHASE 11

Experiment: Statut des hypothèses et questions de recherche

Last completed step: PHASE 10 terminée; 31 affirmations majeures reliées à leurs preuves, limites et actions.

Next exact step: Extraire uniquement les formulations explicites d'hypothèses et questions de recherche des fichiers LaTeX/plan, puis les relier aux expériences et statuts finaux.

Command to run: `rtk rg -n -S "hypoth[eè]se|question de recherche|research question|RQ[0-9]" memoire_logminer_latex_overleaf docs/memoire -g "*.tex" -g "*.md"`

Expected output: Formulations sources vérifiables, puis deux matrices sans reformulation trompeuse.

Files that must be read: Occurrences LaTeX/Markdown ciblées, `final_claim_evidence_matrix.md` et `state/DECISIONS.md`.

Files that DO NOT need to be reread: mémoire complet, artefacts bruts, modèles et fichiers binaires.

Success criterion: Chaque hypothèse et question a une formulation traçable, une réponse, une preuve, une limite et un statut autorisé.

If failure: Conserver la formulation comme `INFORMATION À VÉRIFIER.`; ne pas inventer une hypothèse ou une question.
