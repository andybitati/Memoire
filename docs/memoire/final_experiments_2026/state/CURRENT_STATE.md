# CURRENT STATE

Last update: 2026-09-08
Git commit: a51ee59 (checkpoint protocole PHASE 8; checkpoint final PHASE 7 238e94c)
Active phase: PHASE 9
Active experiment: Analyse statistique transversale
Status: PHASE 8 COMPLETE — PHASE 9 PROTOCOL FROZEN

## Completed

- PHASE 0: environnement, manifeste de 11 fichiers hashés, runner et décisions initiales; checkpoint `4db70f0`.
- PHASE 1: CICIDS2017, 25 holdouts par scénario et 5 contrôles random stratifiés; 30/30; checkpoint `265cdfb`.
- PHASE 2: cinq modèles × cinq scénarios × cinq seeds; 125/125; checkpoint `6e07c3e`.
- PHASE 3: HDFS/BGL strict, Drain3 train-only, validation séparée, 36/36; checkpoint `749625a`.
- PHASE 4: mise à jour contrôlée, 3/3 branches end-to-end; checkpoint `1e184ab`.
- PHASE 5: validation de huit voies multiformat, 8/8; checkpoint `f499797`.
- PHASE 6: routeur réel, 81/81 décisions, 80 correctes; checkpoint `ae56145`.
- PHASE 7: audit de résilience complémentaire; nouvelle exécution `SKIPPED`; checkpoint `238e94c`.
- PHASE 8: corrélation synthétique contrôlée, 1/1 run, 120 paires évaluées.

## In progress

- Protocole transversal figé: 228 statistiques répétées attendues, effets descriptifs au niveau scénario et évaluations uniques séparées; aucun test inférentiel.

## Pending

- Créer le checkpoint de protocole puis construire les trois artefacts statistiques avec `--resume`.
- PHASE 10: matrice affirmation→preuve.
- PHASE 11: hypothèses et questions de recherche.
- PHASE 12: rapport final pour Luna.

## Verified facts

- Le F1 `0,999965` est exclu; provenance insuffisamment démontrée.
- Multi-VM: 525 entrées Redis lues/acquittées, lag et pending finaux nuls; pas 525 succès applicatifs prouvés.
- Reprise: 3 tâches enfilées/terminées/uniques, 1 reprise avant traitement/ACK, pending final 0; fenêtre après traitement/avant ACK non évaluée.
- `AgentMessage`: `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`; aucun `event_id`, `message_id` ou `metadata` direct.
- CICIDS random: F1 `0,995142 ± 0,001013`; holdout macro: `0,157744`.
- LogisticRegression est première uniquement par F1 macro (`0,233670`) et MCC macro (`0,186858`) parmi cinq candidats.
- HDFS strict: meilleur F1 Histogram `0,269307`; BGL strict: `0,913698`.
- Mise à jour: promotion `+0,067845`, rejet `-0,063163`, rejet sous seuil `+0,009016 < 0,02`.
- Multiformat: 7 001 unités lues, 5 001 normalisées, 2 000 perdues; HDFS/BGL pipeline 0/1 000.
- Routeur: exactitude `0,987654`, F1 macro union `0,883598`; Apache normalisé est l'unique erreur.
- Aucun gain prédictif systématique du routage spécialisé n'est démontré.
- Benchmark: agents sans gain de débit sur monolithique à 60 tâches; unités CPU/RAM établies par D008.
- Corrélation synthétique: précision pairwise `0,764706`, rappel `0,866667`, F1 `0,812500`; une fragmentation, une fusion, 3/3 bruits exclus.

## Open issues

- Provenance officielle des copies locales: `INFORMATION À VÉRIFIER.`.
- Ancien HDFS/BGL exploratoire; comparaison ancien/strict non causale.
- Scénario Redis après traitement avant ACK: non évalué.
- Corrélation non évaluée sur incidents SOC réels.
- `graphify update .` historiquement bloqué par `[WinError 5]`; dernier appel sans diagnostic exploitable.

## Important artifact paths

- `docs/memoire/final_experiments_2026/state/`
- `data/processed/final_experiments_2026/`
- `docs/memoire/final_experiments_2026/PHASE_0_COMPLETED.md` à `PHASE_8_COMPLETED.md`
- `docs/memoire/final_experiments_2026/experiment_correlation_synthetic_summary.md`
