# PHASE 8 COMPLETED

Objectif: Évaluer le corrélateur réel sur une vérité terrain synthétique contrôlée, sans prétendre à une validation SOC.

Protocole: 19 événements pré-spécifiés, dont 16 anomalies réparties dans 6 incidents vrais et 3 bruits. Fenêtre fixe de 15 minutes et huit clés de groupement de l'implémentation réelle. Vérité terrain conservée dans un fichier séparé, absent de l'entrée du corrélateur. Évaluation pairwise exhaustive sur 120 paires.

Runs prévus: 1.

Runs terminés: 1.

Runs échoués: 0.

Résultats principaux:

- 6 incidents produits pour 6 incidents vrais.
- TP=13, FP=4, FN=2, TN=101 sur les paires.
- Précision pairwise `0,764706`, rappel `0,866667`, F1 `0,812500`.
- 3/3 événements de bruit exclus.
- Reprise idempotente validée: `SKIPPED_ALREADY_COMPLETED`.

Résultat négatif éventuel: Un incident traversant la frontière fixe 10:15 est fragmenté; deux incidents vrais distincts mais identiques selon toutes les clés observables sont fusionnés.

Artefacts:

- `configs/correlation_synthetic_protocol.json`.
- `scripts/run_correlation_synthetic_validation.py`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_input.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_truth.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_incidents.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_pairs.csv`.
- `data/processed/final_experiments_2026/correlation_synthetic_summary.json`.
- `experiment_correlation_synthetic_summary.md`.
- `tables/correlation_synthetic_metrics.md`.
- `figures/correlation_synthetic_metrics.png`.

Problèmes: Le nombre total d'incidents produits égale fortuitement le nombre vrai, car une fragmentation et une fusion se compensent. Ce seul comptage ne mesure donc pas la qualité de corrélation.

Conclusion scientifique: Le corrélateur est fonctionnellement évalué sur des scénarios synthétiques contrôlés. Il respecte ses règles déterministes sur les cas stables, mais la fenêtre fixe cause une fragmentation et l'absence de caractéristiques discriminantes cause une fusion. Aucune généralisation SOC réelle n'est démontrée.

Impact probable sur le mémoire: Ajouter uniquement une validation synthétique explicitement qualifiée, les métriques pairwise et les deux modes d'échec. Ne pas présenter le nombre d'incidents produit comme preuve suffisante.

