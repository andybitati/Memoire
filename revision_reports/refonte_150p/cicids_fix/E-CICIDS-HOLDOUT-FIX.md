# Protocole E-CICIDS-HOLDOUT-FIX — réexécution du holdout par scénario de CICIDS2017

Rédigé le 2026-11-05 (UTC 20:45 environ), avant toute exécution. Décision de l'auteur : « Réexécute CICIDS ». Défaut corrigé : `revision_reports/refonte_150p/agent_C/LIVRABLE_C.md` §0.1, confirmé par l'intégration (`PLAN_REFONTE_150P.md`, étape 0).

## 1. Motif

Dans la campagne d'origine (`scripts/evaluate_cicids_model_candidates.py` et `scripts/run_final_experiments.py::load_holdout`), `collect_network_sample` prend les premières lignes des fichiers dans l'ordre alphabétique : l'entraînement ne contient qu'un scénario d'attaque (DDoS, ou PortScan quand DDoS est le test), et le test ne lit que les 200 000 premières lignes du fichier tenu à l'écart. Les résultats touchés sont le tableau des cinq candidats, le F1 0,1577 du Random Forest, la ligne « holdout par scénario » du tableau de comparaison aux règles simples, QR6 et les résumés.

## 2. Ce qui est conservé à l'identique

- Données : les huit CSV `data/raw/Datasets/MachineLearningCSV/MachineLearningCVE/*.csv` (CSV d'origine, non corrigés), empreintes enregistrées dans `run_metadata.json`.
- Scénarios tenus à l'écart : DDoS, PortScan, Bot, Infiltration, WebAttacks (mêmes fichiers que `SCENARIO_FILES`).
- Graines : 42, 43, 44, 45, 46, pour chaque scénario, soit 25 évaluations par modèle.
- Variables : `_network_features` et `_network_feature_columns` de `scripts/evaluate_supervised_strict_splits.py`, qui excluent `label`, `flow id`, les adresses IP et `timestamp`.
- Plafonds : 8 000 lignes par classe à l'entraînement ; 4 000 par classe au test (toutes les attaques si le fichier en contient moins : Bot 1 966, Infiltration 36, WebAttacks 2 180).
- Modèles et hyperparamètres : `_candidate_models` de `scripts/evaluate_cicids_model_candidates.py` (RandomForest, ExtraTrees, HistGradientBoosting, LogisticRegression, SGDLogistic), graine du modèle = graine de l'évaluation.
- Seuil : décision par défaut (`predict`), sans calibration, comme dans la campagne d'origine.

## 3. Seule modification

Pour chaque (scénario, graine), avec un générateur `numpy.random.default_rng([graine, indice du scénario])` :
- entraînement : tirage uniforme sans remise de 8 000 lignes BENIGN et de 8 000 lignes d'attaque dans **l'ensemble** des lignes de chaque classe des **sept** fichiers hors scénario (proportions naturelles des fichiers) ;
- test : tirage uniforme sans remise de 4 000 lignes par classe dans **tout** le fichier tenu à l'écart.

Garde-fous vérifiés par le programme avant tout entraînement : BENIGN tiré des 7 fichiers d'entraînement ; attaques tirées d'au moins 3 fichiers ; aucune colonne d'étiquette ou d'identifiant parmi les variables ; tirage dépendant de la graine. Un tirage à blanc (`--dry-run`, sans modèle ni métrique) a été exécuté pour vérifier ces garde-fous et la taille des tests ; son fichier de composition a été supprimé.

## 4. Mesures

- Primaire : F1 de la classe attaque, par évaluation, puis moyenne sur les 25 évaluations de chaque modèle.
- Comparateur : la règle « tout positif » sur exactement les mêmes tests.
- Secondaires, descriptives : F1 moyen par scénario ; F1 micro (matrices cumulées) ; précision, rappel, PR-AUC, MCC ; composition des échantillons.

## 5. Règle de décision (fixée avant exécution)

Pour chaque modèle M : M **bat la règle** si et seulement si (a) F1 moyen de M − F1 moyen du tout positif > 0,01, et (b) le F1 moyen de M par scénario dépasse celui du tout positif dans au moins 4 des 5 scénarios.

- Si aucun modèle ne bat la règle : décision `aucun_modele_ne_bat_la_regle`. La réfutation de H4 (décision de l'auteur R-H4) s'étend au holdout par scénario de CICIDS2017.
- Si au moins un modèle la bat : décision `au_moins_un_modele_bat_la_regle`. La réfutation de H4 ne couvre pas ce protocole, et le mémoire le dit ; le modèle concerné est nommé, en rappelant qu'il est le meilleur de cinq candidats choisis après coup.

Aucune correction pour comparaisons multiples n'est appliquée à cette règle descriptive ; le nombre de modèles comparés (5) est rapporté.

## 6. Conséquences pour le manuscrit, quel que soit le résultat

Les anciens chiffres du holdout par scénario (tableau des cinq candidats, 0,1577, 0,4733 et 0,2337 du tableau de comparaison aux règles simples, QR6, résumés, figure `fig_cicids_protocol_comparison`) sont remplacés par ceux de cette réexécution. Le défaut de sélection d'origine est déclaré une fois, dans la section unique des limites. Les anciens artefacts sont conservés, marqués « non retenus ».

## 7. Limites connues avant exécution

- Protocole conçu après lecture des résultats de la campagne défectueuse, dont le score du tout positif : il ne s'agit pas d'une hypothèse confirmatoire indépendante.
- Seuil non calibré et plafonds conservés pour rester comparable à la campagne d'origine ; Infiltration (36 attaques) pèse autant que les autres scénarios dans la moyenne.
- Les 25 évaluations ne sont pas indépendantes : 5 tests distincts, rééchantillonnés.
- Versionnement local seulement, sans ancre externe tant que la branche n'est pas poussée.

## 8. Exécution

Runner : `revision_reports/refonte_150p/cicids_fix/run_e_cicids_holdout_fix.py`, SHA-256 `20959b8762010d5ee01834a8b3ac2e7f817887809f2108c68d5b2969c62665e3`. Sources importées : `scripts/evaluate_cicids_model_candidates.py` (`6464c6ede70bd1097724dc8a12db20d6a0a848c8871e602c1a63e6b7d9ccb251`) et `scripts/evaluate_supervised_strict_splits.py` (`f1bc1a5a5c069ca7aa3b944c0a3e60550228e7daf88e1460cec2d912f2533bb8`). Environnement : `.venv-final-experiments` (Python 3.11.9, scikit-learn 1.7.2, pandas 2.3.2, numpy 2.2.3). Sorties : `experiments/phase_revision_20261105/E-CICIDS-HOLDOUT-FIX/` (`metrics.csv`, `summary.csv`, `f1_by_scenario.csv`, `f1_micro.csv`, `decision.json`, `sample_composition.csv`, `run_metadata.json`, `MANIFEST_SHA256.csv`).
