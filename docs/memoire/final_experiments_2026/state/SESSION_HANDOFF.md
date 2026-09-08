# SESSION HANDOFF

## Mission

Consolider expérimentalement le mémoire Ariel Logminer sans le réécrire, puis livrer des matrices et un rapport autonome pour Luna.

## Current phase

PHASE 10 — matrice affirmation→preuve.

## Current experiment

Construction de la matrice finale des affirmations et preuves.

## Completed since previous checkpoint

- PHASE 7 clôturée `SKIPPED` au checkpoint `238e94c`; preuve de reprise existante auditée sans rejeu.
- Corrélateur réel audité: fenêtre fixe de 15 minutes et huit clés.
- Protocole phase 8 figé au checkpoint `a51ee59`: 19 entrées, 16 anomalies, 6 incidents vrais, 3 bruits.
- Vérité terrain séparée et absente de l'entrée de l'algorithme.
- Run phase 8 terminé: 6 incidents produits, 120 paires.
- Précision `0,764706`, rappel `0,866667`, F1 pairwise `0,812500`; TP=13, FP=4, FN=2, TN=101.
- Une fragmentation de frontière et une fusion d'incidents indiscernables; 3/3 bruits exclus.
- Tableau et figure produits; figure inspectée; reprise idempotente validée.
- D028 et rapport de phase ajoutés.
- Sources statistiques ciblées inventoriées: CICIDS multi-seeds, HDFS/BGL stricts, benchmark contrôlé, routeur, multiformat et corrélation.
- Protocole phase 9 figé: regroupement scenario×modèle, méthodes déterministes N=1, évaluations uniques séparées.
- Aucun test inférentiel prévu; IC Student seulement pour N≥2 et interprétation conditionnelle.
- Runner compilé et dry-run validé; ligne `PLANNED` ajoutée.
- Agrégation phase 9 terminée: 228 lignes répétées, 4 effets descriptifs, 20 mesures uniques.
- Méthodes N=1 laissées sans écart-type/IC; IC Student uniquement à N=5.
- LogisticRegression vs RandomForest: 2 gains, 1 égalité, 2 pertes au niveau scénario; aucun gain systématique.
- Aucun test inférentiel; reprise idempotente réussie; D029 et rapport de phase ajoutés.

## Key results

- Le même nombre d'incidents vrais et prédits masque une fragmentation et une fusion: le comptage seul est insuffisant.
- Le statut maximal est `VALIDATION SUR SCÉNARIOS SYNTHÉTIQUES CONTRÔLÉS`, jamais validation SOC réelle.
- Les résultats majeurs des phases 1–8 sont condensés dans `CURRENT_STATE.md`.

## Files created or modified

- `configs/correlation_synthetic_protocol.json`
- `scripts/run_correlation_synthetic_validation.py`
- `experiment_correlation_synthetic_summary.md`
- `PHASE_8_COMPLETED.md`
- `tables/correlation_synthetic_metrics.md`
- `figures/correlation_synthetic_metrics.png`
- `configs/transversal_statistics_protocol.json`
- `scripts/build_transversal_statistics.py`
- `experiment_transversal_statistics_summary.md`
- `PHASE_9_COMPLETED.md`
- `tables/transversal_statistics_key_results.md`
- `state/*`

## Current blockers

- Provenance officielle des copies locales non démontrée.
- Le scénario Redis traitement→ACK reste non évalué.
- Corrélation SOC réelle non évaluée.

## Exact next action

Créer le checkpoint final phase 9, puis construire la matrice affirmation→preuve à partir des décisions et résumés.

## Read only these files first

- `state/CURRENT_STATE.md`
- `state/NEXT_ACTION.md`
- `state/DECISIONS.md`
- `PHASE_8_COMPLETED.md`
- CSV de synthèse révélés par l'index ou Graphify

## Do not reread

- Le mémoire complet.
- Les JSON de runs individuels lorsque les CSV agrégés suffisent.
- Les anciens rapports éditoriaux et multi-VM.

## Resume command

`rtk python scripts/build_final_evidence_matrices.py --claims-only`
