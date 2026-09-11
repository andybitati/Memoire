# Audit forensique de la LogisticRegression sur CSE-CIC-IDS2018

Run : `final_csecic_lr_forensic_20260911T000140Z`. Protocole : 15 février 2018 pour l’apprentissage et 16 février 2018 pour le test, avec cinq graines et 10 000 observations par classe et par partition.

## Contrôle négatif par permutation

La permutation porte uniquement sur `y_train`. Le F1 moyen est `0.339867`, la PR-AUC `0.744143` et le MCC `0.119281`. Les labels et caractéristiques de test restent inchangés.

## Baselines mono-feature

La meilleure baseline selon F1 est `Dst Port` avec `0.999720`. Selon PR-AUC, il s’agit de `Dst Port` avec `0.999228`.

## Coefficients

Les coefficients sont extraits après ajustement du `StandardScaler` et de la LR sur le train uniquement. Ils décrivent une association discriminante dans le modèle et non une cause de l’attaque.

## Ablation

Les niveaux 1/3/5/10 ont été gelés avant exécution. Le classement des variables est recalculé pour chaque graine à partir du modèle ajusté sur le train ; aucun résultat test n’intervient dans ce classement.

| Variables retirées | Variables conservées | F1 moyen | PR-AUC moyenne | MCC moyen | Rappel moyen | FPR moyen |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 78 | 0.999212 | 0.999358 | 0.998424 | 1.000000 | 0.001580 |
| 1 | 77 | 0.759988 | 0.586814 | 0.341514 | 0.925260 | 0.596540 |
| 3 | 75 | 0.617461 | 0.333191 | -0.202636 | 0.892200 | 0.993700 |
| 5 | 73 | 0.685073 | 0.525615 | 0.195128 | 0.961980 | 0.846600 |
| 10 | 68 | 0.657859 | 0.475667 | -0.013299 | 0.965380 | 0.969560 |

## Conclusion

B — performance très dépendante de quelques features.

Les contrôles exécutés n’ont pas mis en évidence de fuite triviale correspondant aux mécanismes testés.

Cette conclusion ne signifie pas qu’aucune autre fuite est possible. Elle reste limitée aux contrôles exécutés et au holdout de deux journées DoS.

## Artefacts

- `experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_observed_metrics.csv`
- `experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_label_permutation.csv`
- `experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_single_feature_by_seed.csv`
- `experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_coefficients_by_seed.csv`
- `experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_ablation_by_seed.csv`
- `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_single_feature_scores.csv`
- `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_lr_coefficients.csv`
- `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_feature_ablation.csv`
- `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_lr_forensic_summary.json`
- `experiments/phase_final_scientific_consolidation/reports/CSE_CIC_IDS2018_LR_FORENSIC_AUDIT.md`
- `experiments/phase_final_scientific_consolidation/figures/dataset_12_external_lr_coefficients.png`
- `experiments/phase_final_scientific_consolidation/figures/dataset_13_external_single_feature_scores.png`
- `experiments/phase_final_scientific_consolidation/figures/dataset_14_external_feature_ablation.png`
- `experiments/phase_final_scientific_consolidation/figures/dataset_15_external_label_permutation.png`
