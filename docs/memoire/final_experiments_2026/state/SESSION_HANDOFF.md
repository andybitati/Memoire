# SESSION HANDOFF

## Mission

Consolidation expérimentale finale du mémoire Ariel Logminer, sans réécriture.

## Current phase

PHASE 13A COMPLETE — FINAL DELIVERY PREPARATION.

## Current experiment

Aucun; cette phase n'autorise aucune réexécution expérimentale.

## Completed since previous checkpoint

- PHASE 13A démarrée au commit `ec5c049`.
- HDFS_v1: archive Zenodo officielle `HDFS_v1.zip`, taille `186645559`, MD5 publié et observé `76a24b4d9a6164d543fb275f89773260`.
- HDFS.log: exact match SHA-256 `0783096174d7832c618337f9609e06e04abd86ddd7089b3c12b407e63bfebc52`.
- anomaly_label.csv: exact match SHA-256 `1c711ed6c8848fc3243fb4d092f172f31d128c8a6ec7f26ebba72ab931885ed8`; labels attachés aux traces/blocs `block_id`.
- Linux_2k.log: exact match officiel SHA-256 `b3e20bc1afe732ab1bf3ed1de4bf9c809e4194e02f7dea911d918e5342e8e173`.
- Vérificateur reproductible et CSV de preuve créés.
- PHASE 11 clôturée au commit `d7e8ded`.
- Rapport final pour Luna créé avec 26 sections obligatoires.
- Environnement, datasets, hashes, protocoles, résultats, négatifs, exploratoires et invalidés inclus.
- Contributions architecturale, méthodologique, expérimentale et logicielle séparées.
- Statuts des hypothèses et questions repris.
- Figures, tableaux, annexes, suppressions et modifications chapitre par chapitre listés.
- Douze familles d'informations ouvertes utilisent `INFORMATION À VÉRIFIER.`.
- Ledger, index et `PHASE_12_COMPLETED.md` mis à jour.
- Checkpoint final phase 12: `844d76b`.

## Key results

- PHASE 1: 30/30; random F1 `0,995142`, holdout macro `0,157744`.
- PHASE 2: 125/125; LR F1 macro `0,233670`, pas de domination générale.
- PHASE 3: 36/36; HDFS `0,269307`, BGL `0,913698`, Drain3 train-only.
- PHASE 4: promotion et deux rejets avec hashes.
- PHASE 5: 5 001/7 001 normalisées, HDFS/BGL pipeline à zéro.
- PHASE 6: 80/81, Apache→fallback.
- PHASE 7: SKIPPED; fenêtre traitement→ACK non évaluée.
- PHASE 8: F1 pairwise `0,812500`, une fragmentation et une fusion.
- PHASE 9: descriptif seulement, aucune p-value.

## Files created or modified

- `FINAL_EXPERIMENTAL_REPORT_FOR_LUNA.md`
- `PHASE_12_COMPLETED.md`
- `state/*`

## Current blockers

- Aucun pour la clôture.
- Questions ouvertes consignées dans la section 26 du rapport final.

## Exact next action

Compiler et auditer visuellement `ARIEL_LOGMINER_MEMOIRE_FINAL/` dès qu'un moteur LaTeX est disponible.

## Read only these files first

- `FINAL_EXPERIMENTAL_REPORT_FOR_LUNA.md`
- `final_claim_evidence_matrix.md`
- `final_hypothesis_status.md`
- `final_research_questions_status.md`

## Do not reread

- Le dépôt complet.
- Les artefacts bruts déjà agrégés.

## Resume command

Consulter `state/NEXT_ACTION.md`; reprendre au dataset public indiqué, sans répéter les vérifications terminées.
