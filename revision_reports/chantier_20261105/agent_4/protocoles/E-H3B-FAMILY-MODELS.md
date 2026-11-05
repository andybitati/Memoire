# Protocole préenregistré — E-H3B-FAMILY-MODELS

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit C13-proc**.

## Question

À espace de variables, partitions et algorithme identiques, des modèles spécialisés par famille sont-ils au moins non inférieurs à un modèle commun entraîné sur les trois familles ? Cette expérience traite la composante prédictive E-H3b ; elle ne remplace pas E-H3, qui exige une comparaison indépendante du routeur.

## Entrées et programme gelés

- Familles : `linux_auth`, `cicids` et `unsw`.
- Sources : `data/raw/Datasets/linux_auth_logs_labeled.csv`, les huit CSV de `data/raw/Datasets/MachineLearningCSV/MachineLearningCVE/`, et les deux Parquet `UNSW_NB15_*`.
- Espace commun : 13 variables numériques (`duration`, ports, volumes, taux, calendrier et résumés numériques) et 4 variables catégorielles (`protocol`, `service`, `state`, `status`), telles que définies dans `scripts/run_family_routing_ablation.py`.
- Programme : `revision_reports/chantier_20261105/agent_4/run_e_h3b_family_models.py`, SHA-256 `cea78e1c5e244ada18fa83119251a088346e5118a2405a473b27fd41178ed6a2`.
- Implémentation source importée sans modification : `scripts/run_family_routing_ablation.py` ; son empreinte sera inscrite au manifeste d'exécution.

## Comparateurs

1. `global_common_model` : un Random Forest commun entraîné sur les trois familles dans l'espace commun.
2. `family_aware_models` : un Random Forest par famille, même espace commun et mêmes hyperparamètres ; la famille correcte sélectionne le modèle, ce qui constitue une borne à routage parfait et non un test du classifieur de routage.

Hyperparamètres gelés : 120 arbres, profondeur maximale 22, `min_samples_leaf=2`, `class_weight=balanced`, `n_jobs=1`; imputation médiane et standardisation des numériques, imputation modale et one-hot des catégorielles.

## Taille, partitions et graines

- Pour chaque famille et chaque graine : au plus 6 000 normales et 6 000 anomalies.
- Split stratifié 75/25, séparément dans chaque famille.
- Graines : 42, 43, 44, 45 et 46.
- Les deux variantes utilisent exactement les mêmes lignes de test pour une graine donnée.

## Métriques et critère numérique

- Métrique primaire : différence appariée de F1 `modèle spécialisé - modèle commun`, par famille et par graine.
- Intervalle : IC bilatéral de Student à 95 % sur les cinq différences appariées de chaque famille.
- Critère de non-infériorité fixé avant exécution : pour chacune des trois familles, la borne inférieure de l'IC doit être supérieure ou égale à `-0,01`. Si une seule famille échoue, la non-infériorité globale de la spécialisation n'est pas établie.
- Métriques secondaires : PR-AUC, MCC, précision, rappel, FPR et faux positifs pour 1 000 observations ; elles ne changent pas le critère primaire.

## Analyse prévue

Les résultats seront rapportés par famille, sans agréger des vérités terrain différentes pour masquer une famille défavorable. L'expérience mesure uniquement l'effet de la spécialisation du modèle dans un espace commun et sous un split aléatoire interne ; elle ne démontre ni la bonne décision du routeur, ni la généralisation à une famille ou un scénario absent de l'entraînement.

## Commande

Depuis la racine du dépôt :

```powershell
.venv\Scripts\python.exe revision_reports\chantier_20261105\agent_4\run_e_h3b_family_models.py
```

## Artefacts attendus

Dossier `experiments/phase_revision_20261105/E-H3B-FAMILY-MODELS/` :

- `metrics_by_seed_family.csv` ;
- `paired_f1_deltas.csv` ;
- `summary.json` ;
- `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
