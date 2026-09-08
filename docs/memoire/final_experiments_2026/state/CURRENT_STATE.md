# CURRENT STATE

Last update: 2026-09-08
Git commit: 844d76b (checkpoint final PHASE 12)
Active phase: PHASE 13A — DATA TRACEABILITY
Active experiment: Aucun
Status: IN PROGRESS — SOURCE TRACEABILITY ONLY

## Completed

- PHASE 0: environnement et manifeste; `4db70f0`.
- PHASE 1: CICIDS holdouts/random, 30/30; `265cdfb`.
- PHASE 2: comparaison cinq modèles, 125/125; `6e07c3e`.
- PHASE 3: HDFS/BGL strict, 36/36; `749625a`.
- PHASE 4: mise à jour contrôlée, 3/3; `1e184ab`.
- PHASE 5: multiformat, 8/8; `f499797`.
- PHASE 6: routeur réel, 81/81; `ae56145`.
- PHASE 7: résilience complémentaire `SKIPPED`; `238e94c`.
- PHASE 8: corrélation synthétique, 1/1; `1348eff`.
- PHASE 9: statistiques transversales; `9f8615d`.
- PHASE 10: matrice de 31 affirmations; `57f8e64`.
- PHASE 11: cinq hypothèses et six questions; `d7e8ded`.
- PHASE 12: rapport final de 26 sections et rapport de clôture produits.

## In progress

- PHASE 13A: classification, official-source identification and local-copy verification.
- Current public dataset: CICIDS2017.

## Pending

- CICIDS2017, HDFS_v1, BGL, Linux_2k and UNSW-NB15 source/copy decisions.
- Local, exported, synthetic and indeterminate source classification.
- Final Phase 13A traceability artifacts and Luna-only provenance updates.

## Verified facts

- F1 `0,999965` exclu; provenance officielle non démontrée.
- Multi-VM: preuve laboratoire lecture/ACK, pas 525 succès applicatifs.
- AgentMessage: sept champs métier; transport distinct.
- HDFS/BGL stricts, mise à jour end-to-end, multiformat partiel, routeur 80/81 et corrélation synthétique documentés.
- LogisticRegression meilleur F1 macro `0,233670` seulement.
- Agents sans gain de débit à 60 tâches; unités CPU/RAM établies.
- Cinq hypothèses partiellement soutenues; QR1–QR5 partielles; QR6 forte dans le prototype.

## Open issues

- Provenance officielle des copies locales: `INFORMATION À VÉRIFIER.`.
- Résilience après traitement/avant ACK: `INFORMATION À VÉRIFIER.`.
- Corrélation SOC, utilisabilité, production et généralisation industrielle: `INFORMATION À VÉRIFIER.`.
- `graphify update .`: `[WinError 5] Accès refusé`.

## Important artifact paths

- `FINAL_EXPERIMENTAL_REPORT_FOR_LUNA.md`
- `final_claim_evidence_matrix.md`
- `final_hypothesis_status.md`
- `final_research_questions_status.md`
- `state/ARTIFACT_INDEX.json`
- `state/EXPERIMENT_LEDGER.csv`
