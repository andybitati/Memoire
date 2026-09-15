# Analyse statistique transversale

## Objectif

Uniformiser les statistiques descriptives des campagnes terminées, sans transformer des scénarios, fichiers ou méthodes déterministes en répétitions indépendantes.

## Règles d'unité

- CICIDS: agrégation séparée pour chaque couple scénario–modèle sur les cinq seeds.
- HDFS/BGL: agrégation par dataset–méthode; trois méthodes stochastiques ont N=5, les méthodes déterministes ont N=1.
- Comparaison de modèles CICIDS: différences descriptives entre les cinq moyennes de scénario.
- Routeur, multiformat, corrélation et benchmark architectural: évaluations uniques; aucune dispersion inter-run inventée.
- IC95 de Student uniquement quand N≥2, conditionnel au protocole et aux seeds fixés.
- Aucun test inférentiel: les cinq scénarios sont un ensemble fixe et N=5 seeds est insuffisant pour une inférence transversale crédible.

## Résultats structurants

- RandomForest random stratifié: F1 moyen `0,995142`, écart-type `0,001013`, IC95 `[0,993884; 0,996400]`, N=5.
- RandomForest DDoS holdout: F1 moyen `0,778774`, écart-type `0,001342`, IC95 `[0,777107; 0,780441]`, N=5.
- Le contraste random contre holdout est descriptif seulement, car les unités et les tests diffèrent.
- LogisticRegression a le meilleur F1 macro historique (`0,233670`) sur cinq scénarios, mais face à RandomForest elle gagne 2 scénario(s), fait 1 égalité(s) et perd 2 scénario(s); différence moyenne de scénario `+0.075926`.
- HDFS Histogram F1 `0,269307` avec N=1; aucune dispersion ni IC ne peut être donnée.
- BGL Histogram F1 `0,913698` avec N=1; aucune dispersion ni IC ne peut être donnée.
- Les tableaux transversaux conservent séparément les évaluations uniques de l'architecture, du routeur, du multiformat et de la corrélation.

## Limites

- Les seeds mesurent une sensibilité conditionnelle, pas la variabilité de nouveaux datasets.
- Les scénarios CICIDS ne sont pas des répétitions identiques.
- Les IC95 N=5 sont larges ou dégénérés lorsque les résultats sont constants; ils ne démontrent pas une généralisation externe.
- Les lignes N=1 ne permettent aucune estimation de variance.
- Aucun test statistique n'est utilisé pour donner artificiellement du poids aux conclusions.

## Artefacts

- `configs/transversal_statistics_protocol.json`.
- `data/processed/final_experiments_2026/transversal_repeated_statistics.csv`.
- `data/processed/final_experiments_2026/cicids_model_scenario_effects.csv`.
- `data/processed/final_experiments_2026/transversal_single_evaluations.csv`.
- `tables/transversal_statistics_key_results.md`.
