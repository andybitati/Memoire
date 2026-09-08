# CURRENT STATE

Last update: 2026-09-08
Git commit: 9f8615d (checkpoint final PHASE 9)
Active phase: PHASE 11
Active experiment: Matrices des hypothèses et questions de recherche
Status: PHASE 10 COMPLETE — PHASE 11 IN PROGRESS

## Completed

- PHASE 0: environnement et manifeste; checkpoint `4db70f0`.
- PHASE 1: CICIDS2017 holdouts et contrôle random, 30/30; `265cdfb`.
- PHASE 2: cinq modèles × cinq scénarios × cinq seeds, 125/125; `6e07c3e`.
- PHASE 3: HDFS/BGL strict Drain3 train-only, 36/36; `749625a`.
- PHASE 4: mise à jour contrôlée, 3/3 branches; `1e184ab`.
- PHASE 5: huit voies multiformat, 8/8; `f499797`.
- PHASE 6: routeur réel, 81/81 décisions, 80 correctes; `ae56145`.
- PHASE 7: résilience complémentaire `SKIPPED`; `238e94c`.
- PHASE 8: corrélation synthétique, 1/1, 120 paires; `1348eff`.
- PHASE 9: 228 statistiques répétées, 4 effets scénario, 20 mesures uniques; `9f8615d`.
- PHASE 10: 31 affirmations reliées à leurs preuves et actions rédactionnelles.

## In progress

- Extraire les formulations explicites d'hypothèses et questions de recherche puis leur attribuer un niveau de preuve.

## Pending

- Produire `final_hypothesis_status.md` et `final_research_questions_status.md`.
- PHASE 12: rapport final autonome pour Luna.

## Verified facts

- F1 `0,999965`: artefact interne exact, mais provenance officielle non démontrée; exclu.
- Multi-VM: 525 entrées lues/acquittées, pas 525 succès applicatifs; preuve de laboratoire seulement.
- `AgentMessage`: sept champs métier; aucun identifiant d'événement direct.
- CICIDS random F1 `0,995142`; holdout macro `0,157744`; LogisticRegression F1 macro `0,233670` seulement.
- HDFS strict F1 `0,269307`; BGL strict `0,913698`; Histogram N=1.
- Mise à jour contrôlée testée fonctionnellement de bout en bout, pas apprentissage autonome.
- Routage: aucun gain prédictif systématique; routeur réel 80/81 sur corpus dérivé.
- Multiformat: 5 001/7 001 normalisées; validation partielle.
- Corrélation synthétique: F1 pairwise `0,812500`, une fragmentation et une fusion.
- Statistiques transversales descriptives uniquement; aucun test inférentiel.

## Open issues

- Provenance officielle des copies locales: `INFORMATION À VÉRIFIER.`.
- Scénario Redis après traitement avant ACK: non évalué.
- Corrélation SOC réelle: non évaluée.
- `graphify update .` échoue avec `[WinError 5] Accès refusé`.

## Important artifact paths

- `docs/memoire/final_experiments_2026/final_claim_evidence_matrix.md`
- `docs/memoire/final_experiments_2026/state/`
- `docs/memoire/final_experiments_2026/PHASE_0_COMPLETED.md` à `PHASE_10_COMPLETED.md`
- `data/processed/final_experiments_2026/`
