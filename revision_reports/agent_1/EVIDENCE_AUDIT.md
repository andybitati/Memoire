# Audit factuel — cohérence et forme

## Campagnes multi-VM

Le run court n'est pas fictif. Les artefacts suivants existent :

- `run_id` : `multivm_cnp_20260909T202632Z_37592` ;
- résultat JSON : `experiments/phase_multi_agent/raw/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.json` ;
- métriques par tâche : `experiments/phase_multi_agent/raw/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm_tasks.csv` ;
- trace : `experiments/phase_multi_agent/logs/multivm_cnp_20260909T202632Z_37592__agent_messages.jsonl` ;
- manifeste : `experiments/phase_multi_agent/manifests/multivm_cnp_20260909T202632Z_37592__sha256.json`.

Le JSON atteste 60 tâches réussies sur 60, une répartition de 30 tâches par agent et 15 refus. Ce run peut rester une preuve mécanistique, mais ne doit plus être la campagne principale des résumés.

La campagne principale est :

- `run_id` : `cnp_endurance_multivm_20260918T130822Z` ;
- source : `experiments/phase_cnp_endurance/aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json` ;
- résultat : 1 800 tâches réussies sur 1 800 ; Debian 451, Ubuntu 1 349 ; une réattribution ; un effet persistant et aucun effet dupliqué lors de la panne contrôlée.

## Écart entre 0,157744 et 0,157827

Les deux valeurs ne proviennent pas d'espaces de caractéristiques différents : les deux sources indiquent `feature_count=78`.

- `0,1577441435…` est la moyenne de 25 résultats Random Forest : cinq scénarios multipliés par cinq graines. Les `run_id` suivent le motif `e1_holdout_<scenario>_seed<42..46>` dans `data/processed/final_experiments_2026/cicids_holdout_multiseed_raw.csv`. Le même agrégat apparaît pour les runs `e2_models_<scenario>_seed<42..46>_randomforest` dans `data/processed/final_experiments_2026/cicids_model_multiseed_raw.csv`.
- `0,1578265760…` est la moyenne d'un ancien sous-ensemble de cinq observations : un seul couple scénario–graine par scénario. Source : `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/cicids_model_candidates_metrics.csv`, synthèse `cicids_model_candidates_summary.csv`.

Le second artefact est ancien et ne possède pas de colonne `run_id`. Il ne satisfait donc pas la règle de traçabilité imposée pour la révision finale. La valeur à retenir dans le corps est `0,157744`, adossée aux 25 runs identifiés. L'écart résulte du plan d'agrégation, non de l'espace de caractéristiques.

## Terminologie F1

Dans les expériences CICIDS binaires, la métrique de chaque run est le F1 de la classe positive. Les agrégats `0,157744` et `0,233670` sont des moyennes de ces F1 sur les scénarios et les graines. Il faut donc écrire **F1 moyen inter-scénarios et inter-graines**, et réserver **F1 macro** aux calculs explicitement macro-agrégés entre classes, par exemple le routeur multiclasses.

Source des 25 runs par candidat : `data/processed/final_experiments_2026/cicids_model_multiseed_raw.csv`, avec `run_id` dans chaque ligne ; synthèse : `data/processed/final_experiments_2026/cicids_model_multiseed_summary.csv`.

## Vérifications de forme

- Le mémoire définit bien cinq hypothèses, H1 à H5, et six questions, QR1 à QR6.
- La phrase française signalée comme cassée est déjà réparée dans l'état audité : « Sur BGL, le F1 vaut …, mais 89,8081 % des templates de test sont inconnus du train et la baseline “template inconnu” n'atteint que … ».
- Les sections de la conclusion utilisent `\chapter*` puis des `\section` numérotées. LaTeX les affiche donc comme 7.11 à 7.17. Il faut les rendre non numérotées, comme les sections de l'introduction générale.

