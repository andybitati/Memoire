# Phase 2 — Conflits entre agents et arbitrages

État : phase 1 terminée (agents 1 à 7). Aucun `.tex` modifié à ce stade.

## A. Conflits de fond (chiffres ou conclusions incompatibles)

| # | Sujet | Agents | Positions | Arbitrage |
|---|---|---|---|---|
| A1 | F1 HDFS principal | 1, 6 vs 2 | 1 et 6 citent 0,892308 (2 000 blocs) ; 2 mesure 0,868373 sur 115 013 blocs, IC [0,856771 ; 0,879493], 0,892308 hors IC | **0,868373** partout ; 0,892308 conservé seulement comme échantillon initial (annexe) et pour l'équivalence distribuée de l'agent 3 |
| A2 | Statut de H2 | 1 vs 3 | 1 : NON TRANCHÉE (comparateur absent) ; 3 : panne appariée exécutée, A/B dupliquent, C/D non, mais A+I/B+I non plus | **PARTIELLEMENT SOUTENUE**, avec la mention que le gain vient de l'idempotence |
| A3 | Statut de H3 | 1 vs 5 | 1 : NON TRANCHÉE ; 5 : rejet 20/20, faux rejet 3/46, sans comparateur « sans routage » | **NON TRANCHÉE** (critère falsifiable de 1 non rempli) avec les chiffres de 5 |
| A4 | Phrase « cassée » du résumé FR | 1 vs 4 | 1 : phrase intacte (lecture du source) ; 4 : `89,8081\,%` non échappé commente la fin de ligne dans le PDF | **Bug confirmé** : `\%`, dans les trois résumés et partout où `%` suit un nombre |
| A5 | Interprétation du F1 BGL 0,913698 | 4, 6 | 4 : équivaut à une règle « sévérité absente du train » ; 6 : validation 0,733460 vs test 0,913698 | Complémentaires : intégrer les deux, formulation de 4 en tête |
| A6 | Section unique des limites | 7 vs 2, 4, 5 | 7 rédige la section consolidée avec les anciens chiffres (HDFS 29/2 000, routeur 3/28, BGL 0 positif connu) ; 2, 4, 5 ajoutent des limites locales | Reprendre la section de 7 en y injectant les nouveaux chiffres ; supprimer les limites locales ajoutées par 2, 4, 5 au profit de renvois |
| A7 | Chemins des nouvelles preuves | 7 vs 2–6 | 7 retire `revision_reports` du mémoire ; les nouveaux run_id y sont stockés | Voir décision D2 |
| A9 | Mentions de « versions » antérieures | 1 (§6.4 « Un ancien tableau… »), 2 (« obtenu antérieurement… ») vs consigne de l'auteur | L'auteur exige un seul travail, sans référence à des versions | Reformuler : présenter l'échantillon de 2 000 blocs et l'agrégat à 5 observations comme des analyses du même travail, jamais comme « ancien » ou « antérieur » |
| A8 | Baselines publiées | 6 | Tableau comparatif avec 0,892308 | Remplacer par 0,868373 |

## B. Recouvrements de texte (même passage, contenus compatibles)

| Passage | Agents | Règle d'application |
|---|---|---|
| `chapitre4_implementation.tex` l. 78 (BGL « fenêtres ») | 2, 4 (P-4.1), 6 (P15) | Une seule substitution (version 2, qui renvoie à la sous-section Histogram) |
| `chapitre5_resultats.tex` l. 35 (tableau des protocoles) | 2, 4 (P-5.1), 5 (D.8), 6 (P14) | Fusion ligne par ligne |
| `chapitre5_resultats.tex` l. 165–193 (BGL) | 2, 4 (P-5.2 à P-5.4), 6 (P13, P17) | Base 4, compléments 6 |
| `chapitre6_conclusion.tex` l. 11, 99–114 | 2, 4, 5 (D.19–D.22), 7 (B.7, B.11) | Chiffres de 2 et 4, structure de renvois de 7 |
| Tableau 7.1 (hypothèses) | 1, 3, 5 | Structure 4 colonnes de 1 ; H1 de 5 ; H2 de 3 ; H3 de 1 + chiffres de 5 |
| `main.tex`, trois résumés | 1, 2, 4, 5, 7 | Réécriture unique par langue, en appliquant tous les chiffres arbitrés |
| `annexes.tex`, matrice A.2 | 1, 2, 3, 4, 5, 7 | Matrice reconstruite, un run_id par ligne |
| `chapitre6_approfondissements_scientifiques.tex` | 2, 4, 5, 7 | Section limites de 7 + validité de 5 |

## C. Points relevés hors périmètre

- PR-AUC HistGradientBoosting : résumé 0,567697, artefact des cinq candidats 0,569002 (agent 7) — à tracer avant intégration.
- Fonction d'utilité (agent 7) : M = 1 pour toute offre émise, A = L, refus pour utilité faible inactif dans les campagnes Redis, `FEEDBACK` sans effet sur la mémoire (l'annexe A.2 affirme l'inverse).
- CSE-CIC-IDS2018 : fichiers locaux de 1 048 575 lignes exactement, troncature probable (agent 4).
- `UNSWNB15.zip` contient des fichiers de type CIC-DDoS2019 (agent 5).
- Données personnelles dans des fichiers suivis par git (agent 7), à traiter avant publication.

## D. Décisions de l'auteur

- D1 Titre ; D2 emplacement des nouvelles preuves ; D3 lingala ; D4 champs de la déclaration IA (restent `[À COMPLÉTER]`).
