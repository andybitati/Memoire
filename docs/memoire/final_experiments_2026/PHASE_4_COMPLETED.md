# PHASE 4 COMPLETED

Objectif: Fermer l'incertitude sur le statut réel de la mise à jour contrôlée des modèles par une exécution fonctionnelle end-to-end isolée.

Protocole: Trois copies de modèles sont comparées à trois candidats réellement entraînés sur 16 000 lignes. Tous sont évalués sur le même holdout DDoS local CICIDS2017 seed 42 de 8 000 lignes. La décision utilise le F1 et exige `delta >= 0,02`. La promotion est autorisée, mais tous les chemins de modèle, de backup et d'audit restent sous `data/processed/final_experiments_2026/phase_4`.

Runs prévus: 3.

Runs terminés: 3.

Runs échoués: 0.

Résultats principaux:

- ExtraTrees→RandomForest: F1 `0,711340→0,779185`, delta `+0,067845`, promotion réelle observée.
- RandomForest→SGDLogistic: F1 `0,779185→0,716022`, delta `-0,063163`, rejet observé.
- ExtraTrees→LogisticRegression: F1 `0,711340→0,720357`, delta `+0,009016`, courant conservé car le gain reste inférieur à `0,02`.
- Trois candidats existent ; une seule sauvegarde existe ; les quatre relations de hash du cas promu et l'invariance des deux courants rejetés sont vérifiées.
- Le rapport d'intégrité global est positif et le plan n'utilise aucun chemin de modèle de production.

Résultat négatif éventuel: Un candidat est moins bon et un candidat légèrement meilleur n'est pas promu. La procédure applique donc effectivement le garde-fou au lieu de promouvoir toute amélioration positive.

Artefacts:

- `configs/model_update_e2e_plan.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_end_to_end_report.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_integrity_report.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_promotion_case.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_rejection_case.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_min_delta_case.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_audit.jsonl`.
- `data/processed/final_experiments_2026/phase_4/model_update_decisions.csv`.
- `tables/model_update_end_to_end.md`.
- `figures/model_update_promotion_rejet.png`.

Problèmes:

- L'affichage final de la préparation a initialement échoué sous cp1252 après l'écriture réussie des artefacts ; l'échappement ASCII a été corrigé et l'erreur E0011 conservée.
- Les paires de modèles ont été choisies à partir de la phase 2 ; l'expérience ne mesure pas une nouvelle généralisation indépendante.
- Aucun cycle périodique, trafic de production, concurrence ou panne pendant la promotion n'est couvert.

Conclusion scientifique: `IMPLÉMENTÉ` et `TESTÉ FONCTIONNELLEMENT DE BOUT EN BOUT`. La comparaison réelle, une promotion avec backup et deux rejets sont observés. La performance prédictive indépendante et l'exploitation en production restent `NON ÉVALUÉES`. L'apprentissage continu autonome reste une `PERSPECTIVE`.

Impact probable sur le mémoire: Remplacer le statut limité au dry-run par la formulation « procédure contrôlée de mise à jour testée fonctionnellement de bout en bout », en décrivant les trois branches et les hashes. Interdire toute formulation d'apprentissage continu autonome, de sûreté de production ou de gain prédictif généralisable.

