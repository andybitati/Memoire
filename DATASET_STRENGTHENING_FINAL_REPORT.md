# Rapport final — renforcement scientifique des datasets d’Ariel Logminer

Date de clôture : 11 septembre 2026  
Périmètre : nouvelles preuves sous `experiments/phase_dataset_strengthening/`  
Mémoire modifié : **NON**

## 1. État initial

Les preuves initiales comportaient six limites majeures : une évaluation HDFS à l’événement alors que le label porte sur le bloc, une lecture BGL sans décomposition des templates inconnus, deux protocoles seulement pour CICIDS2017, un routeur évalué sur 81 chunks issus de neuf sources, une couverture multiformat de 5 001/7 001 et un replay multi-agent bout en bout limité à une entrée Windows. Les résultats historiques ont été conservés sans recalcul : HDFS `0,269307`, BGL `0,913698`, CICIDS random `0,995142`, CICIDS holdout `0,157744`, routeur `80/81` et multiformat `5 001/7 001`.

## 2. Critiques scientifiques ciblées

La mission a cherché à aligner unité de vérité et unité de prédiction, séparer apprentissage et évaluation, quantifier les effets de nouveauté, distinguer fichiers et groupes de provenance, mesurer chaque voie d’ingestion et relier plusieurs sources aux vrais agents CNP. Le critère de réussite n’était pas l’augmentation des scores, mais la fermeture d’ambiguïtés expérimentales.

## 3. Sources et provenance

HDFS est la seule grande source de cette phase dont le journal et les labels ont été vérifiés bit à bit contre une archive officielle dont le MD5 publié a été retrouvé. Linux_2k correspond également exactement au fichier officiel Loghub. CICIDS2017 concorde fortement par noms, structure, dimensions et contenu local, mais son identité binaire avec un nouveau téléchargement officiel est **NON DÉMONTRÉE**. BGL est identifié comme corpus Loghub ; l’identité binaire de la copie locale est **NON DÉMONTRÉE**. Windows, Linux/auth et Wazuh sont des sources locales et ne doivent pas être présentés comme des copies de datasets publics.

Deux CSV CSE-CIC-IDS2018 ont ensuite été téléchargés directement depuis le bucket public officiel `s3://cse-cic-ids2018/`. Leurs tailles correspondent aux réponses HTTP officielles et leurs nouveaux SHA-256 locaux sont consignés dans le manifeste du run. Aucun ancien fichier UNSW local n’a été réutilisé.

Les détails sont isolés dans `docs/datasets/`. La provenance reste séparée de toute mesure de performance.

## 4. HDFS block-level

Le run `ds_hdfs_block_20260910T081756Z` a retrouvé les 575 061 blocs annotés dans 11 175 629 lignes. Les blocs ont été ordonnés par première occurrence puis répartis 60/20/20 : 345 036 train, 115 012 validation et 115 013 test. Les intersections sont vides. L’échantillon contient 6 000/2 000/2 000 blocs et 126 368/37 153/30 948 événements ; le test compte 29 blocs positifs.

Drain3 a reçu 126 368 appels `add_log_message()` sur le train. Validation et test utilisent exclusivement `match()`. Le nombre de clusters reste 28 et le hash de l’état reste `deb37a7c9feb396df2d9dde336e707b225ef508e439df9516f9457ef73d06ab7` avant et après inférence.

Le seuil événementiel `3,1811182535` est choisi sur validation. Sur le nouveau test, le F1 événementiel vaut `0,2131147541`. Parmi maximum, moyenne et proportion anormale, l’agrégateur moyenne et son seuil `1,2729429340` sont retenus sur validation. Le F1 bloc test vaut `0,8923076923`. Ce contraste étudie la granularité ; l’ancien F1 `0,269307` n’est pas un benchmark équivalent.

## 5. BGL known/unknown

Le run `ds_bgl_known_unknown_20260910T082706Z` réutilise la préparation Drain3 gelée. Le seuil Histogram `10,8197582842` est choisi sur les 17 764 événements de validation, jamais sur le test.

Sur 19 908 événements test, 17 879 (`89,8081 %`) ont un template inconnu. Les 2 885 anomalies et les 2 885 vrais positifs Histogram se trouvent tous dans ce groupe ; `KNOWN_TEMPLATE` contient 2 029 événements, tous normaux. Le F1 Histogram ALL vaut `0,9136975455`, avec 545 faux positifs. `UnknownTemplateBaseline` atteint seulement `0,2778848006` et produit 14 994 faux positifs. La nouveauté localise donc toutes les anomalies de ce test, mais la règle « template inconnu = anomalie » n’explique pas à elle seule la sélectivité de Histogram.

Le rappel sur anomalies connues ne peut pas être estimé puisque le groupe connu ne contient aucun positif.

## 6. CICIDS2017 temporal holdout

Le run `cicids_temporal_20260910T083015Z` entraîne sur les cinq fichiers lundi–jeudi et teste sur les trois fichiers du vendredi. Les fichiers sont disjoints. Les jours et timestamps servent au split, jamais aux 78 caractéristiques. Les non-finis deviennent zéro, les valeurs sont écrêtées dans `[-1e12, 1e12]` et `StandardScaler` est ajusté dans le pipeline de régression logistique sur le train uniquement.

Un balayage complet construit deux pools figés de 50 000 observations par classe. Pour les graines 42 à 46, 10 000 observations par classe sont tirées sans remise dans chaque partition. Les cinq réplications partagent donc un pool parent et restent corrélées.

| Modèle | N | F1 moyen | IC 95 % du F1 | PR-AUC | MCC | Rappel | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RandomForest | 5 | 0,437429 | [0,433883 ; 0,440976] | 0,830759 | 0,399112 | 0,280620 | 0,002400 |
| LogisticRegression | 5 | 0,556615 | [0,541605 ; 0,571625] | 0,871448 | 0,436298 | 0,400960 | 0,039360 |

Le random historique (`0,995142`), le holdout scénario (`0,157744`) et le holdout temporel répondent à trois questions différentes. Sur ce protocole temporel, LogisticRegression est le meilleur des deux candidats testés en F1 ; son gain de rappel s’accompagne d’un FPR plus élevé.

## 7. Routeur indépendant

Deux erreurs ont été découvertes puis conservées avant le résultat final : les espaces d’en-têtes CICIDS causaient huit `KeyError`, puis les colonnes communes vides biaisaient BGL vers Windows. Quatorze tests passent après correction.

Le run final `router_independent_20260910T094257Z` traite 31 fichiers originaux répartis en neuf `source_group`, sans chunks et sans signal de chemin. Il ne rencontre aucune erreur. L’accuracy sur les routes attendues vaut `0,9032258065`, le macro-F1 `0,7777777778` et l’accuracy des familles connues `1,0`. Les trois sources open-set sont toutes affectées à `network` : taux de rejet inconnu `0,0`. La marge moyenne `138,5484` est une différence de scores heuristiques, pas une probabilité calibrée.

Les 31 fichiers ne sont pas 31 environnements indépendants : les groupes Windows, Wazuh et CICIDS partagent chacun une provenance. Le nombre de groupes, neuf, doit accompagner tout résultat fichier.

## 8. Multiformat équilibré

Le run final `multiformat_balanced_20260910T094422Z` sélectionne les premières unités sans duplication, avec un maximum de 1 000 par source. Sept sources fournissent 1 000 unités ; la fixture Apache n’en fournit qu’une. Les 7 001 unités sont lues, parsées et normalisées, sans perte. HDFS et BGL passent chacun de l’ancien `0/1 000` à `1 000/1 000` grâce aux adaptateurs légers raccordés au pipeline.

La couverture n’implique pas une complétude universelle. Le message est renseigné pour 979/1 000 événements Windows et 943/1 000 lignes Wazuh ; aucun timestamp Wazuh n’est normalisé dans cet échantillon. HDFS ne fournit pas d’hôte dans le format traité. La représentation réseau conserve ses 78 caractéristiques et ne renseigne pas les champs textuels communs. Apache est synthétique, `N=1`, et passe par `fallback`. Aucune préservation brute universelle n’est démontrée.

## 9. Pipeline multi-source multi-agent

Le run `multisource_cnp_20260910T095810Z` soumet 1 401 unités réelles au `ContractNetCoordinator` : 200 par source pour Windows, Linux/auth, Wazuh, syslog, HDFS, BGL et CICIDS, plus l’unique ligne Apache. Les 1 401 `task_id`, 1 401 `contract_id` et 1 401 couples source/index sont uniques.

Toutes les unités sont parsées, normalisées, routées et évaluées par le détecteur candidat léger. Il n’y a aucune erreur, aucune réaffectation et un fallback Apache. La latence moyenne est `0,064334 s` et le p95 `0,167830 s`. Le CNP produit 11 408 messages : 1 401 CFP, 1 601 PROPOSE, 2 602 REFUSE, 1 401 AWARD, 200 REJECT, 1 401 ACCEPT, 1 401 RESULT et 1 401 FEEDBACK. Chaque message porte le même run et exactement les champs `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`.

| Source | Agent majoritaire | Tâches | Propositions | Refus | Route modèle | Succès | Latence moyenne |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| Windows | agent-system | 200 | 400 | 200 | isolation_forest_windows_local | 200 | 0,070590 s |
| Linux/auth | agent-security | 200 | 200 | 400 | random_forest_linux_auth | 200 | 0,031836 s |
| Wazuh | agent-security | 200 | 200 | 400 | isolation_forest_wazuh | 200 | 0,155286 s |
| Syslog | agent-system | 200 | 200 | 400 | isolation_forest_linux_colab | 200 | 0,019137 s |
| Apache | agent-network | 1 | 1 | 2 | fallback | 1 | 0,020198 s |
| HDFS | agent-system | 200 | 200 | 400 | isolation_forest_hdfs_colab | 200 | 0,036222 s |
| BGL | agent-system | 200 | 200 | 400 | isolation_forest_bgl_colab | 200 | 0,040811 s |
| CICIDS | agent-network | 200 | 200 | 400 | random_forest_network_cicids | 200 | 0,096674 s |

Le routeur recommande les artefacts indiqués dans le tableau. La détection effectivement exécutée dans ce replay est `e2e_lightweight_candidate_rule_v1`, pas l’inférence de chacun de ces modèles stockés. Les 122 anomalies et deux incidents sont des candidats heuristiques ; ils ne constituent ni une accuracy ni une vérité terrain construite.

## 10. Dataset externe éventuel

Statut : **COMPLETED**. Le run `external_csecicids2018_20260910T230136Z` utilise deux objets CSE-CIC-IDS2018 téléchargés directement depuis le bucket AWS officiel. Le 15 février 2018 sert exclusivement à l’apprentissage : `996 077` flux Benign, `41 508` GoldenEye et `10 990` Slowloris. Le test du 16 février contient `446 772` flux Benign, `139 890` SlowHTTPTest et `461 912` Hulk. Un en-tête répété du test est écarté.

Les 78 caractéristiques numériques communes excluent le label, le timestamp et les identifiants textuels. Cinq graines tirent sans remise 10 000 observations par classe dans des pools parents figés de 50 000 par classe. Le seuil `0,5` et les hyperparamètres sont fixés avant le test.

| Modèle | N | F1 moyen | Écart-type F1 | PR-AUC | MCC | Rappel | FPR |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RandomForest | 5 | 0,401375 | 0,198722 | 0,721546 | 0,018009 | 0,419240 | 0,447880 |
| LogisticRegression | 5 | 0,999212 | 0,001316 | 0,999358 | 0,998424 | 1,000000 | 0,001580 |

RandomForest varie fortement selon la graine, avec un F1 compris entre `0,129605` et `0,622379`. LogisticRegression reste entre `0,996860` et `0,999850`.

L’analyse exploratoire post hoc `external_csecicids2018_sensitivity_20260910T231423Z` mesure les vecteurs répétés. Les pools contiennent `96 150/100 000` vecteurs uniques dans le train et `75 675/100 000` dans le test, sans vecteur exact commun aux deux journées et sans conflit de labels. Après déduplication des deux partitions, les F1 moyens valent `0,998863` pour LogisticRegression et `0,547226` pour RandomForest. Les répétitions internes ne suffisent donc pas à expliquer la performance linéaire.

La conclusion méthodologique « LogisticRegression dépasse RandomForest sous ce holdout » se retrouve sur un dataset officiel indépendant de CICIDS2017. En revanche, aucun poids appris sur CICIDS2017 n’est transféré : le transfert direct inter-datasets reste **NON DÉMONTRÉ**.

## 11. Statistiques

Les intervalles de confiance sont calculés pour CICIDS2017 et CSE-CIC-IDS2018, où `N=5`. Ils utilisent la moyenne, l’écart-type d’échantillon et l’approximation normale `1,96 × s/√N`. Les répétitions partagent dans les deux cas des pools parents et ne constituent pas des acquisitions indépendantes. HDFS, BGL, routeur, multiformat et CNP sont des runs uniques : aucun IC n’est rapporté. Les résumés stochastiques incluent moyenne, écart-type d’échantillon, médiane, minimum, maximum et IC 95 %.

## 12. Résultats négatifs

- Le RandomForest CICIDS ne conserve pas son score aléatoire en holdout temporel ; son rappel moyen tombe à `0,280620`.
- LogisticRegression améliore le F1 temporel mais porte le FPR moyen à `0,039360`.
- Le routeur open-set ne rejette aucune des trois sources inconnues.
- BGL ne contient aucune anomalie dans le groupe de templates connus du test.
- La complétude Wazuh est nulle pour le timestamp dans l’échantillon courant.
- Apache ne fournit qu’une ligne synthétique.
- Le replay CNP n’exécute pas les modèles entraînés recommandés par le routeur ; il exécute une règle candidate légère.
- RandomForest est très instable sur le holdout CSE-CIC-IDS2018 : F1 moyen `0,401375`, écart-type `0,198722` et FPR moyen `0,447880`.
- `graphify update .` échoue avec `[WinError 5] Accès refusé` après extraction.

## 13. Limites

Les campagnes restent locales et ne simulent pas un SOC industriel. Plusieurs sources partagent un même environnement. Les pools CICIDS sont équilibrés et les cinq graines partagent un parent commun. HDFS bloc repose sur un sous-échantillon stratifié dont le test ne contient que 29 blocs anormaux. L’identité officielle de BGL et CICIDS demeure incomplète. CSE-CIC-IDS2018 n’est évalué que sur deux journées et quatre sous-scénarios DoS ; les échantillons équilibrés ne reproduisent pas la prévalence opérationnelle. Son analyse de déduplication est post hoc. Les métriques de parsing ne garantissent ni fidélité sémantique parfaite ni conservation intégrale du brut. Le CNP local démontre des décisions et traces, pas une tolérance aux pannes supplémentaire ni un gain de débit.

## 14. Impact sur H1–H5

| Hypothèse | Impact de cette phase | Statut recommandé |
| --- | --- | --- |
| H1 | HDFS/BGL rejoignent le pipeline et 7 001/7 001 unités sont normalisées, mais la complétude et le brut ne sont pas universels | PARTIELLEMENT SOUTENUE |
| H2 | 1 401 décisions CNP multi-source sont traçables avec offres et refus ; aucune nouvelle preuve de gain de débit ou de robustesse aux pannes | PARTIELLEMENT SOUTENUE |
| H3 | Les familles connues sont reconnues sur 31 fichiers, mais l’open-set échoue 3/3 et les neuf groupes limitent l’indépendance | PARTIELLEMENT SOUTENUE |
| H4 | Les modèles légers sont informatifs sous protocoles stricts sur CICIDS2017 et CSE-CIC-IDS2018, y compris par l’instabilité négative du RandomForest ; utilité humaine et opérationnelle non évaluées | PARTIELLEMENT SOUTENUE |
| H5 | Cette phase n’isole aucun effet causal supplémentaire de la mémoire | PARTIELLEMENT SOUTENUE, inchangée |

## 15. Impact sur QR1–QR6

| Question | Impact de cette phase | Niveau recommandé |
| --- | --- | --- |
| QR1 | La voie commune couvre désormais HDFS/BGL, avec complétude détaillée par champ | RÉPONSE PARTIELLE renforcée |
| QR2 | Les agents spécialisés prennent 1 401 décisions sur huit sources avec audit CNP complet | RÉPONSE PARTIELLE renforcée |
| QR3 | Le routage fichier sans chunks est fort sur familles connues, mais le rejet inconnu est nul | RÉPONSE PARTIELLE |
| QR4 | Aucun test utilisateur ou résultat nouveau | RÉPONSE PARTIELLE, inchangée |
| QR5 | Aucun gain causal de mémoire nouveau | RÉPONSE PARTIELLE, inchangée |
| QR6 | Protocoles gelés, tests, hashes, résultats négatifs et onze figures renforcent la reproductibilité | RÉPONSE FORTE dans le périmètre laboratoire |

## 16. Affirmations désormais soutenables

- HDFS a été évalué au niveau `block_id` avec partitions disjointes et sélection sur validation.
- Drain3 n’a été ajusté que sur le train dans la campagne HDFS.
- Le F1 BGL observé se situe entièrement sur le groupe de templates inconnus, mais une baseline de nouveauté pure est très inférieure à Histogram.
- CICIDS présente une forte sensibilité au protocole ; LogisticRegression surpasse RandomForest en F1 temporel dans les deux candidats testés.
- Le routeur reconnaît toutes les familles connues du corpus de 31 fichiers, sous neuf groupes de provenance.
- Les adaptateurs courants parsèrent et normalisent les 7 001 unités sélectionnées, dont HDFS/BGL.
- Les vrais agents CNP ont traité 1 401 unités multi-source avec des offres, refus, attributions et résultats auditables.
- Sur le holdout officiel CSE-CIC-IDS2018 du 15 vers le 16 février, LogisticRegression surpasse RandomForest parmi les deux candidats testés ; cette observation résiste à une analyse exploratoire sans vecteurs répétés.

## 17. Affirmations toujours non démontrées

- Généralisation industrielle ou SOC : **NON DÉMONTRÉ**.
- Rejet fiable de sources inconnues par le routeur : **NON DÉMONTRÉ**.
- Transfert direct des poids appris sur CICIDS2017 vers CSE-CIC-IDS2018 : **NON DÉMONTRÉ**.
- Généralisation à l’ensemble des attaques de CSE-CIC-IDS2018 : **NON DÉMONTRÉ**.
- Préservation brute universelle et complétude universelle du schéma : **NON DÉMONTRÉ**.
- Gain prédictif systématique du routage : **NON DÉMONTRÉ**.
- Gain de débit, haute disponibilité ou tolérance aux pannes apportés par ce replay CNP : **NON DÉMONTRÉ**.
- Inférence bout en bout des modèles entraînés sur les 1 401 unités : **NON DÉMONTRÉ**.

## 18. Artefacts

Les configurations sont dans `experiments/phase_dataset_strengthening/configs/`, les résultats unitaires dans `raw/`, les données préparées dans `processed/`, les résumés dans `aggregated/`, les onze figures dans `figures/`, les rapports HDFS/BGL/CSE-CIC-IDS2018 dans `reports/`, les cartes dans `docs/datasets/` et les ledgers append-only dans `experiments/phase_dataset_strengthening/LEDGER.csv` et `state/EXPERIMENT_LEDGER.csv`.

La matrice claim–evidence est `dataset_strengthening_claim_evidence_matrix.md`. La validation machine est `aggregated/final_artifact_validation.json`.

## 19. Hashes

Le manifeste `experiments/phase_dataset_strengthening/manifests/SHA256_MANIFEST.json` contient les SHA-256 des configurations, scripts, datasets employés, splits, résultats bruts, agrégats, figures et rapports. Le manifeste est régénéré après ce rapport afin d’inclure sa version finale.

## 20. Commandes exactes

```powershell
.venv-hdfs-bgl\Scripts\python.exe -m pytest tests\test_dataset_strengthening.py -q
.venv-hdfs-bgl\Scripts\python.exe scripts\run_hdfs_block_strengthening.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_bgl_known_unknown_strengthening.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_cicids_temporal_strengthening.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_router_independent_strengthening.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_multiformat_balanced_strengthening.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_multisource_cnp_e2e_strengthening.py --workers 1
.venv-hdfs-bgl\Scripts\python.exe scripts\run_external_csecicids2018_strengthening.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_external_csecicids2018_sensitivity.py
.venv-hdfs-bgl\Scripts\python.exe scripts\finalize_dataset_strengthening.py
```

Les deux objets externes ont été récupérés sans authentification depuis le
bucket officiel avec `curl.exe -L --fail --retry 3 --continue-at -`, vers les
chemins suivants :

```text
data/raw/external/CSE-CIC-IDS2018/Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv
data/raw/external/CSE-CIC-IDS2018/Friday-16-02-2018_TrafficForML_CICFlowMeter.csv
```

Les URL exactes, `Content-Length`, ETag multipart et SHA-256 sont conservés
dans `configs/external_csecicids2018_protocol.json` et dans le manifeste du
run. Les données brutes sont exclues de Git en raison de leur taille.

Dans cette session, les commandes ont été préfixées par `rtk` conformément aux instructions du dépôt.

## 21. Recommandations de modification du mémoire

Le mémoire ne doit être modifié qu’à partir des artefacts ci-dessus. Le chapitre 5 devrait distinguer clairement les résultats historiques des nouveaux protocoles, ajouter la granularité bloc HDFS, la décomposition BGL, le holdout temporel CICIDS, le holdout CSE-CIC-IDS2018, `N=31 fichiers / 9 groupes` pour le routeur, les couvertures par source et le replay CNP. La campagne externe doit être présentée comme une comparaison méthodologique sur deux journées DoS, jamais comme un transfert direct de modèle ni comme une généralisation industrielle. Les chapitres 3 et 8 devraient préciser que l’enveloppe CNP transporte ses métadonnées dans `payload`, que le détecteur du replay est une règle candidate et que la marge du routeur n’est pas calibrée. Les annexes devraient référencer les cartes, manifests, commandes et hashes. Le résumé et la conclusion ne doivent ni présenter ces résultats comme industriels ni transformer des anomalies candidates en vérité terrain.

| Critique du jury | Avant | Nouvelle action | Résultat | Après |
| --- | --- | --- | --- | --- |
| HDFS event vs block | critique forte | évaluation block-level, Drain3 train-only, sélection validation | F1 bloc test 0,892308 ; blocs disjoints | CORRIGÉ |
| BGL templates inconnus | interprétation faible | groupes known/unknown et baseline de nouveauté | 89,8081 % inconnus ; tous les TP dans unknown ; baseline F1 0,277885 | PARTIELLEMENT CORRIGÉ |
| CICIDS généralisation | 2 protocoles | holdout temporel lundi–jeudi vers vendredi | RF 0,437429 ; LR 0,556615 sur cinq graines corrélées | PARTIELLEMENT CORRIGÉ |
| routeur pseudo-réplication | 9 sources/81 chunks | 31 fichiers, 9 groupes, sans signal de chemin | known accuracy 1,0 ; rejet open-set 0,0 | PARTIELLEMENT CORRIGÉ |
| multiformat incomplet | 5 001/7 001 | adaptateurs HDFS/BGL et couverture par source | 7 001/7 001 ; Apache N=1 ; complétude variable | PARTIELLEMENT CORRIGÉ |
| pipeline en silos | campagnes séparées | E2E multi-source CNP | 1 401/1 401 succès, mais détecteur candidat plutôt que modèles routés | PARTIELLEMENT CORRIGÉ |
| validité externe | limitée | deux objets CSE-CIC-IDS2018 officiels, jours/scénarios disjoints | LR F1 0,999212 ; RF F1 0,401375 ; aucune copie inter-jour exacte | PARTIELLEMENT CORRIGÉ |
