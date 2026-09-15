# PHASE 1 COMPLETED

Objectif: Déterminer si la chute de performance CICIDS2017 en scénario tenu hors entraînement persiste sur plusieurs seeds et distinguer variabilité intra-scénario et inter-scénarios.

Protocole: Cinq scénarios (`DDoS`, `PortScan`, `Bot`, `Infiltration`, `WebAttacks`) × cinq seeds (`42` à `46`) avec fichier entier exclu du train, plus cinq contrôles random stratifiés sur un pool fixe. RandomForest strict, 78 caractéristiques, plafonds 8 000/4 000 par classe et maximum deux chunks par fichier.

Runs prévus: 30.

Runs terminés: 30.

Runs échoués: 0.

Résultats principaux:

- Random stratifié : F1 moyen `0,995142`, écart-type `0,001013`, N=5.
- Holdout macro par scénario : F1 moyen `0,157744`, N=25 (cinq seeds par scénario).
- Différence descriptive random moins holdout macro : `+0,837398`.
- Moyennes holdout : DDoS `0,778774`, PortScan `0,009947`, Bot `0`, Infiltration `0`, WebAttacks `0`.
- Écart-type entre les cinq moyennes de scénarios : `0,347193`.
- Écart-type intra-scénario combiné : `0,000600`.
- La variabilité observée est donc dominée par le scénario tenu à l'écart, pas par la seed.

Résultat négatif éventuel:

- Bot, Infiltration et WebAttacks : aucun vrai positif au seuil fixe.
- PortScan : rappel moyen `0,005` malgré PR-AUC moyenne `0,881982`.
- DDoS : rappel moyen `0,6377`, soit 1 449,2 faux négatifs sur 4 000 attaques en moyenne.
- Le protocole strict ne soutient pas une généralisation homogène à des scénarios absents du train.

Artefacts:

- `cicids_holdout_multiseed_raw.csv`
- `cicids_holdout_multiseed_summary.csv`
- `cicids_random_multiseed_raw.csv`
- `cicids_random_multiseed_summary.csv`
- `cicids_random_vs_holdout_summary.csv`
- `tables/cicids_phase1_results.md`
- cinq figures PNG dans `figures/cicids_*`.
- 30 artefacts JSON unitaires dans `data/processed/final_experiments_2026/phase_1/`.

Problèmes:

- Infiltration ne contient que 32 attaques par test sous le plafond de deux chunks : résultat à faible effectif positif.
- Les intervalles t sur cinq seeds sont descriptifs et conditionnels au protocole ; ils ne sont pas des intervalles d'incertitude de population.
- Le random split mélange les captures et ne mesure pas la généralisation à un scénario inédit.

Conclusion scientifique: Oui, la chute persiste sur plusieurs seeds. Le facteur dominant est l'identité du scénario tenu hors entraînement. Le split aléatoire donne une estimation très optimiste de la performance lorsque les captures sont mélangées, sans que cette expérience suffise à attribuer causalement l'écart à des doublons ou à une fuite précise.

Impact probable sur le mémoire: Remplacer toute affirmation globale de haute généralisation CICIDS par une présentation séparée random/holdout, inclure les tailles de test et les résultats nuls, et expliciter que les scénarios inédits sont la faiblesse principale.

