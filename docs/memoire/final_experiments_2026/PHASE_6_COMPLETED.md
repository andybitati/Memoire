# PHASE 6 COMPLETED

Objectif: Évaluer directement `route_model`, distinctement de l'ablation prédictive existante.

Protocole: 81 fichiers dérivés de neuf sources hashées, noms neutres, 100 événements par fichier sauf Apache N=1. Vraie famille fixée avant routage ; scores, raisons, marge, fallback et erreurs enregistrés.

Runs prévus: 81 décisions.

Runs terminés: 81.

Runs échoués: 0.

Résultats principaux:

- 80 décisions correctes sur 81 ; exactitude `0,987654`.
- F1 macro incluant la classe fallback prédite sans support vrai: `0,883598`.
- F1 macro sur les huit vraies familles: `0,994048`.
- Fallback 1/81 ; unknown 0 ; error 0.
- Tous les modèles sélectionnés existent.
- Huit familles vraies sont parfaitement rappelées sauf network, rappel `0,909091`.

Résultat négatif éventuel: Le fixture Apache normalisé est routé vers fallback au lieu de network, avec marge 21. Le code favorise explicitement fallback lorsque `subtype` contient `apache`, alors que le type brut Apache est mappé vers network.

Artefacts:

- `configs/router_evaluation_protocol.json`.
- `scripts/run_router_evaluation.py`.
- `data/processed/final_experiments_2026/router_evaluation_raw.csv`.
- `data/processed/final_experiments_2026/router_metrics_by_family.csv`.
- `data/processed/final_experiments_2026/router_confusion_matrix.csv`.
- `data/processed/final_experiments_2026/router_evaluation_summary.json`.
- `tables/router_metrics_by_family.md`.
- `figures/router_confusion_matrix.png`.

Problèmes:

- Les chunks d'une même source ne sont pas indépendants.
- Les métadonnées du contenu peuvent révéler la famille même si le nom du chunk est neutre.
- La famille Apache n'a pas de modèle dédié et sa taxonomie est incohérente selon représentation brute ou normalisée.

Conclusion scientifique: Le routeur réel est évalué et obtient 80/81 décisions correctes sur ce corpus local dérivé. Ce résultat mesure l'attribution de famille/modèle, pas un gain prédictif. La généralisation à des sources nouvelles reste partiellement soutenue seulement.

Impact probable sur le mémoire: Ajouter l'évaluation directe du routeur, sa métrique, l'erreur Apache et la définition exacte de la marge. Maintenir D005 : aucun gain prédictif systématique du routage spécialisé n'est établi.

