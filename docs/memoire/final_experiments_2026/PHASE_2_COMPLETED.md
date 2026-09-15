# PHASE 2 COMPLETED

Objectif: Comparer cinq candidats CICIDS2017 selon un protocole holdout identique sur cinq scénarios et cinq seeds, sans sélectionner un modèle sur une seule métrique.

Protocole: `RandomForest`, `ExtraTrees`, `HistGradientBoosting`, `LogisticRegression` et `SGDLogistic` × `DDoS`, `PortScan`, `Bot`, `Infiltration`, `WebAttacks` × seeds `42` à `46`. Le fichier du scénario testé est entièrement absent du train. La représentation contient 78 caractéristiques numériques. Les plafonds sont 8 000 lignes par classe au train et 4 000 par classe au test, avec au plus deux chunks de 100 000 lignes par fichier. Le seuil de décision par défaut du candidat est conservé ; aucun seuil n'est choisi sur le test.

Runs prévus: 125 résultats.

Runs terminés: 125.

Nouveaux ajustements: 100.

Résultats RandomForest réutilisés: 25, strictement identiques à la phase 1 et reliés à leur artefact source.

Runs en échec final: 0. Cinq échecs historiques HGB dus au bac à sable Windows restent dans le ledger ; les cinq reprises correspondantes ont réussi hors bac à sable.

Résultats macro sur 25 résultats par modèle:

| Modèle | F1 moyen | Écart-type F1 | PR-AUC | MCC | FPR | Fit moyen (s) | Test moyen (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| LogisticRegression | 0,233670 | 0,285231 | 0,458829 | 0,186858 | 0,010000 | 0,284343 | 0,015496 |
| SGDLogistic | 0,165406 | 0,293837 | 0,505504 | 0,111296 | 0,008240 | 0,149185 | 0,016656 |
| RandomForest | 0,157744 | 0,316943 | 0,556896 | 0,144366 | 0,000110 | 1,849471 | 0,060026 |
| ExtraTrees | 0,143191 | 0,287744 | 0,525826 | 0,129469 | 0,000100 | 1,001099 | 0,101020 |
| HistGradientBoosting | 0,003362 | 0,008175 | 0,567697 | -0,002419 | 0,001050 | 1,352894 | 0,050286 |

Interprétation multi-métrique:

- LogisticRegression est le meilleur des cinq candidats testés selon le F1 macro et le MCC macro, et non selon toutes les métriques.
- HistGradientBoosting a la meilleure PR-AUC macro, mais son F1 macro est presque nul. Les scores classent parfois les observations sans produire de décisions utiles au seuil courant.
- ExtraTrees a le FPR macro le plus faible et la meilleure PR-AUC DDoS, mais pas le meilleur F1 macro.
- SGDLogistic est le plus rapide en entraînement moyen, mais il est instable sur Infiltration et nul sur trois scénarios au seuil courant.
- RandomForest reste le meilleur F1 sur DDoS et PortScan, tout en échouant au seuil courant sur Bot, Infiltration et WebAttacks.

Résultat négatif:

- Aucun candidat n'offre une généralisation homogène aux cinq scénarios tenus hors entraînement.
- Sur Bot, aucun des cinq candidats ne produit de vrai positif.
- Sur PortScan, aucun F1 moyen ne dépasse `0,009947`.
- Sur WebAttacks, seul LogisticRegression produit des vrais positifs, avec F1 `0,074614` et rappel `0,039908`, ce qui reste faible.
- Infiltration ne comporte que 32 positifs sous le plafond de lecture ; son avantage LogisticRegression (`F1=0,372881`) reste fragile.

Statut du score `0,233670`:

- Il provient de `data/processed/final_experiments_2026/cicids_model_multiseed_summary.csv`.
- Il s'agit du F1 moyen macro de LogisticRegression sur 25 résultats : cinq scénarios tenus hors entraînement × cinq seeds.
- Dataset local déclaré par le protocole: CICIDS2017, huit fichiers CSV listés et hashés dans `dataset_manifest_final.csv`.
- Provenance officielle des copies locales: `INFORMATION À VÉRIFIER.`
- Candidats comparés: les cinq modèles du tableau ci-dessus avec configurations gelées dans `configs/cicids_final_protocol.json`.
- Le score est le meilleur F1 macro parmi ces cinq candidats et uniquement dans ce protocole plafonné.

Mesure des coûts:

- `train_time_sec` mesure la durée murale de `fit` via `time.perf_counter()`.
- `test_time_sec` mesure la durée murale combinée de `predict`, `predict_proba` ou `decision_function`, puis du scoring.
- Unité: seconde par run sur la machine documentée dans `environment_final_experiments.json`.
- Ces durées ne sont ni une consommation CPU, ni une mémoire RAM, ni une mesure distribuée.

Artefacts:

- `data/processed/final_experiments_2026/phase_2/*.json` — 125 artefacts unitaires validés.
- `data/processed/final_experiments_2026/cicids_model_multiseed_raw.csv`.
- `data/processed/final_experiments_2026/cicids_model_multiseed_summary.csv`.
- `data/processed/final_experiments_2026/cicids_model_scenario_summary.csv`.
- `data/processed/final_experiments_2026/cicids_model_tradeoffs.csv`.
- `tables/cicids_phase2_model_comparison.md`.
- `figures/cicids_modeles_scenarios_{f1,prauc,mcc}.png`.
- `figures/cicids_modeles_compromis_f1_temps.png`.

Conclusion scientifique: Le score F1 macro `0,233670` est reproductible et correspond au meilleur candidat des cinq configurations testées, mais il ne démontre ni une bonne généralisation globale ni une domination multi-métrique. Les résultats sont fortement dépendants du scénario tenu hors entraînement.

Impact probable sur le mémoire: Présenter `0,233670` avec son protocole complet, les quatre autres candidats, les résultats par scénario et les limites. Ne pas le qualifier de meilleur modèle absolu ni de performance CICIDS2017 générale.
