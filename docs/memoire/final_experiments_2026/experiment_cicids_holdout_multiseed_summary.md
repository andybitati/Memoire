# EXPERIMENT CICIDS HOLDOUT MULTISEED — SUMMARY

Objectif: Mesurer séparément la variabilité entre seeds et la difficulté des cinq scénarios CICIDS2017 entièrement tenus hors entraînement.

Protocole: RandomForest strict, 78 caractéristiques numériques, 8 000 observations maximum par classe en entraînement, 4 000 par classe en test, fichier du scénario totalement exclu du train. Seeds 42 à 46. La sélection plafonnée prend les premières observations admissibles ; la seed varie l'ordre des lignes et l'aléa interne du RandomForest, pas l'identité du sous-échantillon plafonné.

Nombre de runs prévus: 25.

Nombre terminé: 5.

Nombre échoué: 0.

## Résultats agrégés disponibles

| Scénario | N | F1 moyen | Écart-type | Médiane | Min | Max | IC 95 % demi-largeur | Précision | Rappel | PR-AUC | MCC | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDoS | 5 | 0,778774 | 0,001342 | 0,779371 | 0,776384 | 0,779558 | 0,001667 | 1,000000 | 0,637700 | 0,910292 | 0,684183 | 0,000000 |

Confusion cumulée sur les cinq runs DDoS: TN = 20 000, FP = 0, FN = 7 246, TP = 12 754. Chaque run utilise 16 000 observations d'entraînement et 8 000 observations de test.

## Résultats importants

- La performance DDoS tenue hors entraînement reste faible et stable sur les cinq seeds : F1 entre 0,776384 et 0,779558.
- La précision moyenne est 1,0 et le FPR moyen 0,0, mais le rappel moyen n'est que 0,6377 : le déficit provient des faux négatifs, pas des faux positifs.

## Résultat négatif

Le modèle manque en moyenne 1 449,2 attaques DDoS sur 4 000 par run. La répétition des seeds ne résout pas cette faiblesse de généralisation au scénario tenu à l'écart.

## Limites

- Résumé partiel : quatre scénarios holdout et le contrôle random restent à exécuter.
- L'intervalle de confiance t sur cinq seeds décrit seulement cette variabilité algorithmique conditionnelle au sous-échantillon fixe ; il ne mesure ni l'incertitude de population ni la variabilité entre captures.
- La provenance officielle des copies locales est non établie ; leur identité locale est figée dans `dataset_manifest_final.csv`.

## Chemins des artefacts

- Runs unitaires : `data/processed/final_experiments_2026/phase_1/e1_holdout_ddos_seed*.json`
- Brut consolidé : `data/processed/final_experiments_2026/cicids_holdout_multiseed_raw.csv`
- Résumé CSV : `data/processed/final_experiments_2026/cicids_holdout_multiseed_summary.csv`
- Ledger : `docs/memoire/final_experiments_2026/state/EXPERIMENT_LEDGER.csv`

