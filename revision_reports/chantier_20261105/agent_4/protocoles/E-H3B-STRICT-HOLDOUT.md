# Protocole préenregistré — E-H3B-STRICT-HOLDOUT

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit C13-proc**.

## Question

Lorsqu'une catégorie d'attaque est absente de l'entraînement, des modèles spécialisés par famille sont-ils au moins non inférieurs à un modèle commun aux trois familles ?

## Motif : défauts d'E-H3B-FAMILY-MODELS

Cette expérience a été décidée après lecture d'E-H3b, et un contrôle diagnostique hors protocole a été fait sur UNSW avant ce dépôt. Elle corrige deux défauts du chargement de `scripts/run_family_routing_ablation.py`, découverts après l'exécution d'E-H3b :

1. **Fuite de l'étiquette sur UNSW.** `load_unsw` inclut `target` dans les colonnes du résumé numérique. Diagnostic sur les mêmes lignes, graines 42 à 44, split aléatoire : F1 du modèle spécialisé 0,9926 avec la fuite, 0,9000 sans elle.
2. **Sélection par premières lignes.** `load_cicids` et `load_linux_auth` retiennent les premières lignes des fichiers, sans échantillonnage par graine. La famille CICIDS d'E-H3b ne contient donc que des attaques DDoS d'un seul fichier.

Les résultats d'E-H3b ne sont ni modifiés ni supprimés. Le script source n'est pas modifié, car le manifeste d'E-H3b enregistre son empreinte.

## Entrées et programme gelés

- Programme : `revision_reports/chantier_20261105/agent_4/run_e_h3b_strict.py`, SHA-256 `2a02354f7b3a158f684cb233833d2c1796af0132f8c5fa9986cb7e8da101d265`.
- Importés du script source, sans modification : `make_model`, `COMMON_FEATURES`, `_numeric_summary`, `_metric_row`, `_positive_scores`. Hyperparamètres inchangés : Random Forest de 120 arbres, profondeur 22, `min_samples_leaf=2`, `class_weight=balanced`.
- Données : `data/raw/Datasets/linux_auth_logs_labeled.csv`, les huit CSV de `data/raw/Datasets/MachineLearningCSV/MachineLearningCVE/`, les deux Parquet `UNSW_NB15_*`, **lus en entier**.
- Un essai technique a vérifié le programme avant ce dépôt, sur les graines réservées 1 et 2 et de petits échantillons. Il a confirmé que la préparation reproduit le chargeur source, hormis le résumé UNSW. Ses métriques n'ont pas été consultées ni conservées comme résultat.

## Comparateurs

1. `global_common_model` : modèle commun, entraîné sur les trois familles.
2. `family_aware_models` : modèle propre à la famille testée, sélectionné par la famille correcte. C'est une borne à routage parfait et non un test du routeur.

## Partition : catégorie tenue à l'écart

Pour chaque graine et chaque catégorie H d'une famille F :

- Test : au plus 1 500 lignes de H et autant de lignes normales de F, soit un test équilibré.
- Entraînement de F : au plus 6 000 normales, disjointes du test, et au plus 6 000 attaques de F hors H.
- Modèle spécialisé : entraînement de F. Modèle commun : entraînement de F, plus un échantillon de 6 000 normales et 6 000 attaques de chacune des deux autres familles.

Catégories, fixées avant exécution :

- `cicids` : DDoS, PortScan, Bot, Infiltration, WebAttacks. Les autres attaques restent toujours à l'entraînement.
- `linux_auth` : brute_force, geo_anomaly, port_scan, privilege_escalation.
- `unsw` : Analysis, Backdoor, DoS, Exploits, Fuzzers, Generic, Reconnaissance, Shellcode, Worms.

Graines : 42, 43, 44, 45, 46, soit 90 comparaisons.

## Référence corrigée

Pour chaque graine et chaque famille : 6 000 normales et 6 000 attaques tirées aléatoirement dans toutes les données, split stratifié 75/25, mêmes comparateurs. Elle sépare l'effet de la correction des données de celui de la partition. Elle est rapportée et ne participe pas à la décision.

## Métriques et critère numérique

- Métrique primaire : delta de F1 `spécialisé - commun`, moyenné par graine sur les catégories de la famille.
- Intervalle : IC bilatéral de Student à 95 % sur les cinq graines.
- Critère, même marge qu'E-H3b : pour chacune des trois familles, la borne inférieure de l'IC doit être supérieure ou égale à `-0,01`. Si une seule famille échoue, la non-infériorité globale n'est pas établie.
- Secondaires : F1 par catégorie, PR-AUC, MCC, FPR. Le test étant équilibré, la prédiction systématiquement positive obtient un F1 de 0,666667 : les F1 lui seront comparés.

## Conséquences préfixées

- Le statut de H3 reste NON TRANCHÉE quel que soit le résultat, car la comparaison du routeur à une table statique reste non exécutée.
- Le manuscrit présente cette expérience comme la comparaison de référence. E-H3b y est mentionnée avec ses deux défauts, et son résultat sur UNSW n'est plus retenu.
- Critère satisfait : la spécialisation n'est pas inférieure de plus de la marge sur ces catégories. Critère non satisfait : la non-infériorité n'est pas établie, en nommant les familles concernées.

## Portée

Les effectifs de Worms, d'Infiltration et d'autres catégories rares sont faibles : leur F1 est bruité, et ils pèsent autant que les autres dans la moyenne par famille. La partition retire une catégorie d'attaque, non une période ni un système. L'expérience ne teste pas le routeur.

## Commande

Depuis la racine du dépôt :

```powershell
.venv\Scripts\python.exe revision_reports\chantier_20261105\agent_4\run_e_h3b_strict.py
```

## Artefacts attendus

Dossier `experiments/phase_revision_20261105/E-H3B-STRICT-HOLDOUT/` : `metrics_by_seed_family_category.csv`, `summary.json`, `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
