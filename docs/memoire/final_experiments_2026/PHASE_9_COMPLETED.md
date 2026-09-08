# PHASE 9 COMPLETED

Objectif: Produire une analyse statistique transversale sans pseudo-réplication ni inférence artificielle.

Protocole: Agrégation CICIDS par scénario–modèle sur cinq seeds; HDFS/BGL par dataset–méthode avec N=5 pour les méthodes stochastiques et N=1 pour les méthodes déterministes; effets CICIDS calculés sur les cinq moyennes de scénario; évaluations uniques conservées à part. IC95 de Student conditionnels uniquement pour N≥2.

Runs prévus: 1 agrégation déterministe.

Runs terminés: 1.

Runs échoués: 0.

Résultats principaux:

- 228 lignes de statistiques répétées pour six métriques.
- 4 comparaisons descriptives de LogisticRegression aux autres candidats, unité=scénario.
- 20 mesures issues d'évaluations uniques, sans dispersion inventée.
- RandomForest random stratifié: F1 `0,995142 ± 0,001013`, IC95 `[0,993884; 0,996400]`, N=5.
- RandomForest DDoS holdout: F1 `0,778774 ± 0,001342`, IC95 `[0,777107; 0,780441]`, N=5.
- LogisticRegression contre RandomForest: 2 scénarios gagnés, 1 égalité, 2 perdus; différence moyenne F1 `+0,075926` sur les cinq scénarios fixes.
- Reprise idempotente validée.

Résultat négatif éventuel: Le meilleur F1 macro de LogisticRegression ne correspond pas à une domination systématique scénario par scénario. Aucun test inférentiel crédible n'est justifié par les cinq scénarios fixes.

Artefacts:

- `configs/transversal_statistics_protocol.json`.
- `scripts/build_transversal_statistics.py`.
- `data/processed/final_experiments_2026/transversal_repeated_statistics.csv`.
- `data/processed/final_experiments_2026/cicids_model_scenario_effects.csv`.
- `data/processed/final_experiments_2026/transversal_single_evaluations.csv`.
- `experiment_transversal_statistics_summary.md`.
- `tables/transversal_statistics_key_results.md`.

Problèmes: Les IC95 à N=5 sont conditionnels aux seeds et ne représentent pas la variabilité de nouveaux datasets. Les méthodes N=1 n'ont aucune estimation de variance.

Conclusion scientifique: Les statistiques descriptives sont désormais uniformisées avec des unités explicites. Les conclusions doivent rester conditionnelles aux scénarios, splits et datasets observés; aucune significativité transversale n'est revendiquée.

Impact probable sur le mémoire: Utiliser les agrégats scénario–modèle et leurs N explicites. Ne pas présenter les 25 lignes CICIDS comme 25 répétitions indépendantes, ni les cinq scénarios comme un échantillon aléatoire.

