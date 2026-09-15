# EXPERIMENT CICIDS HOLDOUT MULTISEED — SUMMARY

Objectif: Mesurer séparément la variabilité entre seeds et la difficulté des cinq scénarios CICIDS2017 entièrement tenus hors entraînement.

Protocole: RandomForest strict, 78 caractéristiques numériques, 8 000 observations maximum par classe en entraînement, 4 000 par classe en test, fichier du scénario totalement exclu du train. Seeds 42 à 46. La sélection plafonnée prend les premières observations admissibles ; la seed varie l'ordre des lignes et l'aléa interne du RandomForest, pas l'identité du sous-échantillon plafonné.

Nombre de runs prévus: 25.

Nombre terminé: 25.

Nombre échoué: 0.

## Résultats agrégés disponibles

| Scénario | N | F1 moyen | Écart-type | Médiane | Min | Max | IC 95 % demi-largeur | Précision | Rappel | PR-AUC | MCC | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDoS | 5 | 0,778774 | 0,001342 | 0,779371 | 0,776384 | 0,779558 | 0,001667 | 1,000000 | 0,637700 | 0,910292 | 0,684183 | 0,000000 |
| PortScan | 5 | 0,009947 | 0,000001 | 0,009948 | 0,009945 | 0,009948 | 0,000002 | 0,935065 | 0,005000 | 0,881982 | 0,045036 | 0,000350 |
| Bot | 5 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,322471 | -0,003631 | 0,000100 |
| Infiltration | 5 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,015396 | 0,000000 | 0,000000 |
| WebAttacks | 5 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,000000 | 0,654341 | -0,003757 | 0,000100 |

Confusion cumulée sur les cinq runs DDoS: TN = 20 000, FP = 0, FN = 7 246, TP = 12 754. Chaque run utilise 16 000 observations d'entraînement et 8 000 observations de test.

Confusion cumulée sur les cinq runs PortScan: TN = 19 993, FP = 7, FN = 19 900, TP = 100. Chaque run utilise également 16 000 observations d'entraînement et 8 000 observations de test équilibré.

Confusion cumulée sur les cinq runs Bot: TN = 19 998, FP = 2, FN = 9 830, TP = 0. Le fichier tenu à l'écart ne fournit que 1 966 attaques Bot dans les deux chunks autorisés ; chaque test contient donc 5 966 lignes et un taux positif de 0,329534.

Confusion cumulée sur les cinq runs Infiltration: TN = 20 000, FP = 0, FN = 160, TP = 0. Les deux chunks autorisés ne contiennent que 32 attaques Infiltration par run ; chaque test contient 4 032 lignes et un taux positif de 0,007937.

Confusion cumulée sur les cinq runs WebAttacks: TN = 19 998, FP = 2, FN = 10 900, TP = 0. Chaque test contient 2 180 attaques Web et 4 000 observations bénignes, soit 6 180 lignes et une prévalence positive de 0,352751.

## Résultats importants

- La performance DDoS tenue hors entraînement reste faible et stable sur les cinq seeds : F1 entre 0,776384 et 0,779558.
- La précision moyenne est 1,0 et le FPR moyen 0,0, mais le rappel moyen n'est que 0,6377 : le déficit provient des faux négatifs, pas des faux positifs.
- PortScan montre une quasi-défaillance au seuil de décision du modèle : rappel moyen 0,005 et F1 moyen 0,009947.
- La PR-AUC PortScan reste pourtant 0,881982 : le classement des scores contient de l'information, mais le seuil de décision fixe ne la convertit pas en détection utile. Aucun seuil alternatif n'a été sélectionné sur le test.
- Bot n'obtient aucun vrai positif sur cinq seeds. Sa PR-AUC moyenne de 0,322471 est légèrement inférieure à la prévalence positive du test (0,329534), ce qui n'apporte pas de preuve de classement utile.
- Infiltration n'obtient aucun vrai positif parmi les 32 attaques échantillonnées par run. La faible taille positive interdit d'extrapoler ce zéro à tout le scénario.
- WebAttacks n'obtient aucun vrai positif au seuil fixe, alors que la PR-AUC moyenne atteint 0,654341, supérieure à la prévalence 0,352751. Comme pour PortScan, cela distingue une défaillance de seuil/décision d'une absence totale d'information de classement.

## Résultat négatif

Le modèle manque en moyenne 1 449,2 attaques DDoS sur 4 000 par run. La répétition des seeds ne résout pas cette faiblesse de généralisation au scénario tenu à l'écart.

Pour PortScan, le modèle manque exactement 3 980 attaques sur 4 000 dans chaque run. La stabilité entre seeds confirme que cette faiblesse n'est pas corrigée par l'aléa du RandomForest.

Pour Bot, le modèle manque les 1 966 attaques disponibles dans chaque run. Ce résultat est stable à F1 nul sur les cinq seeds.

Pour Infiltration, les 32 attaques présentes dans la fenêtre de lecture sont toutes manquées. C'est une observation négative reproductible sur l'échantillon, mais une preuve de généralisation plus faible que pour Bot ou PortScan en raison du très petit nombre de positifs.

Pour WebAttacks, les 2 180 attaques du test sont toutes manquées dans chaque run. Aucun seuil alternatif n'a été calculé sur ces données de test.

## Limites

- Les cinq scénarios holdout sont terminés. Les différences entre scénarios dominent très largement les différences entre seeds.
- Les 25 runs holdout et les cinq contrôles random stratifiés sont terminés ; voir `experiment_cicids_random_multiseed_summary.md` et `PHASE_1_COMPLETED.md` pour la comparaison.
- L'intervalle de confiance t sur cinq seeds décrit seulement cette variabilité algorithmique conditionnelle au sous-échantillon fixe ; il ne mesure ni l'incertitude de population ni la variabilité entre captures.
- La provenance officielle des copies locales est non établie ; leur identité locale est figée dans `dataset_manifest_final.csv`.

## Chemins des artefacts

- Runs unitaires : `data/processed/final_experiments_2026/phase_1/e1_holdout_ddos_seed*.json`
- Brut consolidé : `data/processed/final_experiments_2026/cicids_holdout_multiseed_raw.csv`
- Résumé CSV : `data/processed/final_experiments_2026/cicids_holdout_multiseed_summary.csv`
- Ledger : `docs/memoire/final_experiments_2026/state/EXPERIMENT_LEDGER.csv`
