# Chantier « Refonte 150 pages » — consignes communes (2026-11-05)

Mission : `MISSION.md`. Rapports de lecture (version de 180 pages) : `RETOURS_LECTEURS.md`. État : `ETAT.md`.

## Nature du travail

Chantier de **planification** : aucun agent ne modifie les `.tex`, le code, les données ou les artefacts. Chaque agent écrit son livrable dans `revision_reports/refonte_150p/agent_<X>/LIVRABLE_<X>.md`, puis ajoute son bloc de passation à `ETAT.md`.

## Règles non négociables

1. Aucun chiffre inventé : tout nombre cité vient d'un `.tex`, d'un CSV ou d'un JSON dont on donne le chemin.
2. Si une expérience contredit le mémoire, on corrige l'affirmation, jamais le résultat. On n'efface aucun résultat négatif.
3. Aucune nouvelle revendication de supériorité. Le travail reste une étude expérimentale critique d'intégration et d'orchestration.
4. Toute expérience non exécutée est déclarée comme telle, jamais comblée par une inférence.
5. Vérifier chaque reproche contre le manuscrit actuel avant de proposer un correctif : le classer **fondé**, **partiellement fondé**, **déjà traité** ou **inexact**, avec la preuve (fichier et ligne, ou passage cité).
6. Dans la rédaction proposée : français soutenu et sobre, aucune mention de plusieurs versions du travail ou des agents, limites formulées une seule fois.
7. Chaque correctif est localisé (fichier `.tex` + passage repérable par son texte ; les numéros de ligne bougent) et rattaché à un reproche (L1 §x ou L2 §x).

## Repères

- Manuscrit : `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`, `chapters/*.tex`, `frontmatter/*.tex` ; PDF `main.pdf`, 180 pages ; table des matières : `main.toc` (numéros de page par section).
- Correspondance fichier → numérotation du PDF (les lecteurs citent le PDF) :
  - Introduction générale (p. 1–15) : `chapitre1_introduction.tex`
  - Ch. 1 État de l'art (p. 16–45) : `chapitre2_etat_art.tex`
  - Ch. 2 Modèle proposé (p. 46–73) : `chapitre3_modele_propose.tex` (+ `spec_utilite.tex`)
  - Ch. 3 Implémentation (p. 74–83) : `chapitre4_implementation.tex`
  - Ch. 4 Résultats (p. 84–117) : `chapitre5_resultats.tex`
  - Ch. 5 Validité scientifique (p. 118–124) : `chapitre6_approfondissements_scientifiques.tex` (+ `limites_consolidees.tex`)
  - Ch. 6 Discussion (p. 125–130) : `chapitre6_discussion.tex`
  - Ch. 7 Reproductibilité (p. 131–134) : `chapitre7_reproductibilite_deploiement.tex`
  - Conclusion (p. 135–141) : `chapitre6_conclusion.tex`
  - Annexe A (p. 142–152) : `annexes.tex` ; bibliographie p. 153–158 : `references.bib`
  - Pages liminaires (i–xxii) : `main.tex` (résumés), `frontmatter/`
- Artefacts : `experiments/phase_revision_20261104/`, `experiments/phase_revision_20261105/` ; registre des protocoles : `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md`.
- Historique du chantier précédent : `revision_reports/chantier_20261105/ETAT_CHANTIER.md` (décisions C1–C20, audit de la reprise) et `agent_8/LIVRABLE_8_verdict.md`.
- Environnement : `revision_reports/HANDOFF.md` §6. Dans Bash, ne pas écrire de texte français à apostrophes dans des heredocs ; utiliser l'outil d'écriture de fichiers.
