# LIVRABLE C — Intégrité des données et validité interne

Agent C, chantier « Refonte 150 pages », 2026-11-05. Aucun `.tex`, script, donnée ni artefact n'a été modifié. Contrôles effectués : lecture du code, `git log`, empreintes SHA-256 et comptage des lignes. Deux scripts de diagnostic en lecture seule ont été écrits dans le scratchpad de la session, hors du dépôt : `cicids_sample_composition.py` et `csecic_check.py`.

## 0. Constats majeurs, par ordre de gravité

1. **Défaut nouveau et grave : les protocoles CICIDS2017 « holdout par scénario » sont entraînés sur un seul fichier.** `collect_network_sample` (`scripts/evaluate_supervised_strict_splits.py`, l. 229–277) parcourt les fichiers dans l'ordre alphabétique et prend les premières lignes (`head`) jusqu'au plafond. Ce plafond est de 8 000 lignes par classe, lues dans au plus deux blocs de 100 000 lignes par fichier. Le plafond est donc atteint dans le premier fichier lu. Composition reconstituée avec la même logique (script `cicids_sample_composition.py`, sans modèle) :
   - graine 42, DDoS tenu à l'écart : entraînement = 8 000 BENIGN + 8 000 PortScan, tous issus de `Friday-…-PortScan` ;
   - graines 43 à 46, autres scénarios tenus à l'écart : entraînement = 8 000 BENIGN + 8 000 attaques, tirés de `Friday-…-DDos` (DDoS, ou PortScan quand DDoS est le test) ;
   - les tests sont conformes au texte : 4 000 + 4 000 (DDoS, PortScan), 4 000 + 1 966 (Bot), 4 000 + 32 (Infiltration), 4 000 + 2 180 (WebAttacks).

   Le protocole décrit au mémoire (« chacune des graines tient hors entraînement un scénario différent ») laisse entendre que l'entraînement couvre tous les autres scénarios. En réalité, il compare **un seul scénario d'entraînement à un scénario de test**. C'est le même défaut de sélection par premières lignes que celui qui a fait écarter E-H3b.

   Résultats touchés :
   - le tableau des cinq candidats (`tab:cicids-candidats` : LR 0,2337, RF 0,1578…), produit par `scripts/evaluate_cicids_model_candidates.py` ;
   - le **F1 de 0,1577 du Random Forest en holdout par scénario**, produit par `scripts/run_final_experiments.py::load_holdout`, l. 304–325 (même fonction, mêmes plafonds) ;
   - leurs reprises dans le résumé, l'abstract, le bokuse (`main.tex` l. 280, 305 et suivantes), la conclusion (QR6, `chapitre6_conclusion.tex` l. 38), le tableau 4.15 (comparaison aux règles simples), la figure `fig_cicids_protocol_comparison` et la discussion.

   La sélection ne dépend pas de la graine : les « 25 évaluations » se réduisent donc à cinq couples entraînement/test, répétés avec cinq graines de modèle.

   Restent sains : le protocole temporel (`run_cicids_temporal_strengthening.py`, réservoir aléatoire `__priority`), l'Isolation Forest (`revision_reports/agent_6/scripts/run_cicids_isolation_forest_temporal.py`, mêmes pools temporels) et la séparation aléatoire (`load_random_control`). Cette dernière prend les premières lignes, mais de **chaque** fichier, si bien que tous les scénarios sont représentés.

   **Ce que le constat ne change pas** : la comparaison au « tout positif » sur le même test reste valable en tant que comparaison sur ce test. La lecture « le score dépend du protocole » reste qualitativement vraie, et elle est même renforcée. En revanche, l'ampleur de la chute de 0,9951 à 0,1577 mesure un transfert entre un scénario et un autre, non entre « tous les autres scénarios » et un scénario. Ce n'est donc pas le protocole annoncé.

2. **E-H3B-STRICT-HOLDOUT n'est pas touchée par le chargeur fautif**, malgré l'empreinte d'origine dans son manifeste (vérification demandée par le coordinateur ; détail au §2.2).

3. **CSE-CIC-IDS2018 : fichiers non coupés en fin de ligne, mais plafonnés à exactement 2²⁰ lignes physiques**, d'où la limite d'Excel (§3).

4. **Le préenregistrement est vérifié dans l'ordre des commits locaux.** En revanche, aucun commit de protocole n'a été poussé vers le dépôt distant : aucune ancre externe n'existe (§7).

## 1. Classement des reproches du périmètre

| Reproche | Classement | Preuve |
|---|---|---|
| L1 §B.3 / L2 §2.2 — contamination d'E-H3b | **Fondé, déjà traité dans le texte** (E-H3b écartée, `chapitre5_resultats.tex` « La comparaison E-H3b… n'est pas retenue » ; `chapitre6_approfondissements_scientifiques.tex` l. 21). **L'audit demandé n'a pas été fait** ; le présent audit montre que le même défaut touche CICIDS2017 (§0.1) | §2 |
| L2 §2.2 et §3.7 — autres campagnes non auditées | **Fondé** : le texte l'avoue (`chapitre6_approfondissements_scientifiques.tex` l. 21, « Les autres campagnes n'ont pas fait l'objet d'un audit de code aussi poussé ») ; l'audit confirme qu'au moins une autre campagne est touchée | §2 |
| L2 §2.2 — CSE-CIC-IDS2018 peut-être tronqué | **Fondé** : 1 048 576 lignes physiques dans chaque fichier, soit 2²⁰ | §3 |
| L2 §2.2 — CICIDS2017 non corrigé, en connaissance de cause | **Fondé** sur le choix (`chapitre5_resultats.tex` l. 58) ; **le choix est défendable s'il est justifié** | §4 |
| L2 §2.2 — « mêmes données corrigées » (p. 103) | **Partiellement fondé** : la phrase vise le chargement **sans fuite** d'E-H3B-STRICT, et non la correction d'Engelen et al. L'incohérence n'est que lexicale, mais réelle pour le lecteur | §4 |
| L2 §2.2 et §3.9 — BGL dégénéré, chemins multiples | **Fondé, en partie déjà traité** : la dégénérescence et la conception a posteriori de G sont écrites (l. 233–296). Restent : le tableau 4.5 dans le corps du texte, sa légende « test et seuil indépendants » (trompeuse) et G cité ailleurs comme résultat | §5 |
| L2 §2.2 — graines HDFS fictives | **Déjà traité pour l'essentiel** (l. 192 : « les cinq graines ne constituent pas cinq observations indépendantes »). Restent : « moyenne des graines » (légende `fig:hdfs-event-bloc`, « F1 moyen 0,868373 » d'E-H4) et la précision incohérente « [0,8568 ; 0,879493] » | §6 |
| L2 §2.2 — 6 000 blocs, 1,7 %, sans justification | **Partiellement traité** (l. 192 : « paramètre du protocole, non le résultat d'un calcul ») ; la raison du choix n'est pas donnée | §6 |
| L2 §2.2 — prévalence test 1,46 % contre validation 3,48 % | **Déjà traité** (l. 172 : effet de l'ordre chronologique) ; l'effet sur le F1 n'est pas discuté | §6 |
| L1 §E.2 / L2 §2.2 — préenregistrement auto-certifié | **Fondé** sur l'absence de registre externe ; **inexact** si l'on entend que les critères ont été fixés après coup : l'ordre des commits est vérifié | §7 |
| L1 §E.1 — mesures corrélées dans E-H3B-STRICT | **Partiellement fondé** : l'IC apparié est calculé par famille ; il faut vérifier et écrire quelle est l'unité de rééchantillonnage | §7 bis |
| L2 §2.2 — absence de correction pour comparaisons multiples | **Fondé** (hors cœur de périmètre ; à coordonner avec l'Agent B) | §7 bis |
| L2 §2.2 — routeur partiellement circulaire | **Déjà déclaré** (`chapitre4_implementation.tex` l. 34) ; la conséquence n'est pas tirée en §4.7 | §8 |
| L2 §2.2 — corrélation en circuit fermé | **Déjà déclaré** (`chapitre5_resultats.tex` l. 796) | §8 |

## 2. Audit du pipeline de préparation

### 2.1 Inventaire des chargeurs (campagnes citées au mémoire)

| Campagne / résultat | Chargeur (chemin, fonction) | Cible ou dérivée parmi les variables ? | Sélection | Verdict |
|---|---|---|---|---|
| CICIDS2017, cinq candidats (`tab:cicids-candidats`) | `scripts/evaluate_cicids_model_candidates.py` → `evaluate_supervised_strict_splits.collect_network_sample` | Non : `DROP_COLUMNS` retire `label`, `flow id`, IP, `timestamp` | **Premières lignes, premier fichier atteint** | **Défaut de sélection (§0.1)** |
| CICIDS2017, holdout RF 0,1577 (25 év.) | `scripts/run_final_experiments.py::load_holdout` → idem | Non | **Idem** | **Défaut de sélection** |
| CICIDS2017, séparation aléatoire 0,9951 | `run_final_experiments.py::load_random_control` | Non | Premières lignes **de chaque fichier** (2 blocs), puis tirage | Acceptable ; à déclarer (pool non uniforme dans chaque fichier) |
| CICIDS2017, temporel | `scripts/run_cicids_temporal_strengthening.py` (pool `__priority`, `seed_sample`) | Non (`_network_features`) | Réservoir aléatoire | Sain |
| CICIDS2017, Isolation Forest | `revision_reports/agent_6/scripts/run_cicids_isolation_forest_temporal.py` | Non (`META` exclu) | Pools temporels | Sain |
| CSE-CIC-IDS2018 | `scripts/run_external_csecicids2018_strengthening.py::build_priority_pool` ; audit `revision_reports/agent_4/scripts/csecic_shortcut_audit.py` | Non : `label`, `timestamp`, IP retirés ; en-têtes répétés retirés (`header_mask`) | Réservoir aléatoire | Sain ; `Dst Port` conservé (raccourci documenté) |
| E-H3B-STRICT-HOLDOUT | `revision_reports/chantier_20261105/agent_4/run_e_h3b_strict.py::prepare_linux/prepare_cicids/prepare_unsw`, `load_all` | Non : `prepare_unsw` retire `label` et `attack_cat` du résumé numérique ; `COMMON_FEATURES` ne contient ni `target` ni `category` | Fichiers lus **en entier**, tirage `frame.sample` par graine dérivée | Sain |
| E-H3b (écartée) | `scripts/run_family_routing_ablation.py` à `27deb22` | **Oui** (UNSW) | Premières lignes | Invalide, déjà déclaré |
| Linux/auth (modèle principal) | `scripts/train_linux_auth_model.py` | Non ; mais `status` et `service` sont candidats à servir de mandataires de l'étiquette (jeu synthétique ?) | `sample` aléatoire | À contrôler (test T5 ci-dessous) |
| HDFS | `scripts/run_hdfs_block_strengthening.py::load_labels`, partition par première apparition | Étiquette jointe par `block_id`, absente des scores | Tirage stratifié de 6 000 blocs | Sain |
| BGL | `scripts/run_bgl_known_unknown_strengthening.py` ; `revision_reports/agent_4/scripts/bgl_second_protocol.py` | Le score utilise la sévérité, **corrélée à l'étiquette par construction de BGL** : voir §5 | Contigu | Sain sur la fuite ; dégénéré sur le fond |

### 2.2 E-H3B-STRICT-HOLDOUT : quel chargeur a réellement tourné ?

| Élément | Valeur |
|---|---|
| `source_script` du manifeste (`experiments/phase_revision_20261105/E-H3B-STRICT-HOLDOUT/MANIFEST_SHA256.csv`) | `8de67257…` = `scripts/run_family_routing_ablation.py` d'origine, en CRLF (version fautive, avant `786919b`) |
| Contenu à `27deb22` | même contenu, en LF (`cf71fdde…`), selon l'écart consigné au registre |
| Après `786919b` | seules changent `load_linux_auth`, `load_cicids` et `load_unsw`, avec l'ajout de `_seeded_selection` (diff à partir de la l. 109). `COMMON_NUMERIC`, `COMMON_CATEGORICAL`, `COMMON_FEATURES` (l. 35–51), `_numeric_summary` (l. 99), `make_model`, `_metric_row` et `_positive_scores` sont inchangés |
| Runner (`run_e_h3b_strict.py`, empreinte du protocole `2a02354f…`) | conforme à l'empreinte enregistrée (vérifié, normalisation LF) |
| Ce que le runner appelle hors `--smoke` | `source._numeric_summary`, `source.COMMON_FEATURES/NUMERIC/CATEGORICAL`, `source.make_model`, `source._metric_row`, `source._positive_scores`. Les chargeurs `source.load_*` ne sont appelés **qu'en mode `--smoke`** (l. 312, 321, 328 : contrôle d'équivalence des variables) |
| Chargement effectif | `load_all` : lecture complète de linux_auth, des 8 CSV CICIDS et des deux parquet UNSW ; `prepare_unsw` exclut `label` et `attack_cat` du résumé numérique |

**Conclusion** : la campagne stricte a importé le fichier d'origine, mais n'en a exécuté aucune fonction fautive. L'empreinte d'origine figure au manifeste parce que le runner charge ce module pour ses fonctions communes. Celles-ci sont identiques avant et après le correctif. **Ses résultats (§4.8, `tab:e-h3b-family-models`, QR3, tableau 7.1, résumés) ne sont pas touchés.**

Réserve résiduelle, à écrire : sur Linux/auth, `status` et `service` font partie des variables, ce qui peut expliquer l'écart de la catégorie `port_scan` (0,7100 contre 0,0675). Ce n'est pas une fuite de la cible, mais c'est un mandataire possible, à contrôler par le test T5.

### 2.3 Suite de tests anti-fuite proposée

Dossier `tests/data_integrity/`, exécutable par `pytest` sur un échantillon réduit (option `--sample`, quelques minutes) :

| Fichier | Assertions |
|---|---|
| `test_no_target_in_features.py` | Pour chaque chargeur du §2.1 : aucune colonne de `X` ne porte un nom de l'ensemble {`label`, `target`, `attack_cat`, `category`, `anomaly_label`, `subcategory`, `event`} ; `X.columns` ∩ `y.name` = ∅. Pour les résumés agrégés (`numeric_*`) : recalcul après permutation de la colonne cible du brut, puis assertion `np.allclose(X_avant, X_apres)` (un résumé qui dépend de la cible bouge) |
| `test_single_feature_leakage.py` | Pour chaque variable seule : AUC de validation < 0,99, sauf liste blanche justifiée (`Dst Port` sur CSE-CIC, sévérité sur BGL), chaque exception étant consignée avec sa raison |
| `test_sampling_coverage.py` | Pour un holdout par scénario : l'ensemble d'entraînement contient des lignes d'**au moins k = n_fichiers − 1** fichiers sources, et la part de chaque fichier est supérieure à un plancher fixé ; échoue sur `collect_network_sample` actuel |
| `test_seed_changes_selection.py` | Deux graines différentes donnent des index sélectionnés différents (Jaccard < 0,9) ; échoue sur une sélection par premières lignes |
| `test_split_disjoint.py` | Entraînement, validation et test disjoints par identifiant (`block_id`, ligne source, `__source_row`) ; parseur HDFS/BGL : empreinte de l'état identique avant et après inférence |
| `test_label_permutation.py` | Avec étiquettes d'entraînement permutées, F1 de test ≤ F1 du tout positif + 0,02 (le contrôle existe déjà pour CSE-CIC : `run_final_csecicids2018_lr_forensic.py::permute_training_labels`) |

**Phrase pour le mémoire** (chapitre 5, à la place de « Les autres campagnes n'ont pas fait l'objet d'un audit de code aussi poussé ») :
- si l'audit et les tests sont faits et passent, après correction et réexécution de CICIDS : « Les chargeurs de toutes les campagnes citées ont été audités ; des tests automatisés vérifient l'absence de l'étiquette et de ses dérivées parmi les variables, la couverture des fichiers sources et la dépendance de l'échantillon à la graine (annexe A). L'audit a révélé une sélection par premières lignes dans le holdout par scénario de CICIDS2017, corrigée et réexécutée ; les résultats antérieurs ne sont plus utilisés. »
- s'ils ne sont pas faits : « Un audit des chargeurs a établi l'absence de l'étiquette parmi les variables pour les campagnes citées. Il a aussi montré que le holdout par scénario de CICIDS2017 n'entraîne le modèle que sur un seul fichier, celui des attaques DDoS ou PortScan : ses scores mesurent un transfert d'un scénario vers un autre. Aucun test automatisé ne protège ces chargeurs contre une régression. »

Dans les deux cas, corriger la description du protocole en §4.2. Formulation proposée : « l'entraînement retient les 8 000 premières lignes de chaque classe rencontrées dans l'ordre des fichiers, soit, en pratique, un seul scénario d'attaque (DDoS, ou PortScan lorsque DDoS est évalué) ».

## 3. CSE-CIC-IDS2018

Contrôle local (`data/raw/external/CSE-CIC-IDS2018/`, script `csecic_check.py`) :

| Fichier | Octets | SHA-256 | Lignes physiques | Lignes de données | En-têtes répétés | Champs | Fin |
|---|---|---|---|---|---|---|---|
| `Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv` | 375 945 899 | `fa2947a8…c9c4b` | **1 048 576** | 1 048 575 | 0 | 80 partout | ligne complète, saut final |
| `Friday-16-02-2018_TrafficForML_CICFlowMeter.csv` | 333 723 605 | `1a4919fa…5d8b` | **1 048 576** | 1 048 574 | 1 | 80 partout | ligne complète, saut final |

Étiquettes : 15 février : Benign 996 077, GoldenEye 41 508, Slowloris 10 990. 16 février : Benign 446 772, SlowHTTPTest 139 890, Hulk 461 912.

Lecture : 1 048 576 lignes physiques valent exactement 2²⁰, le nombre maximal de lignes d'une feuille Excel. Aucune ligne n'est coupée. La troncature est donc probable **à la ligne près**, mais elle peut venir de la distribution officielle elle-même : il est souvent signalé que plusieurs CSV « Processed Traffic Data for ML Algorithms » publiés ont ce même plafond. Ce point n'a pas été vérifié ici, et ne doit pas être écrit au mémoire sans contrôle.

Procédure de vérification (à faire par l'auteur, sans télécharger les fichiers) :
1. `aws s3 ls --no-sign-request "s3://cse-cic-ids2018/Processed Traffic Data for ML Algorithms/"` liste les tailles des fichiers officiels.
2. Comparer les tailles officielles des fichiers du 15 et du 16 février aux 375 945 899 et 333 723 605 octets locaux.
3. Si les tailles sont égales, le fichier local est identique à la distribution officielle, qui est elle-même plafonnée. Si elles diffèrent, la copie locale est tronquée.
4. Consigner le résultat (date, commande, tailles) dans l'annexe A.

**Recommandation tranchée** : conserver §4.6 **seulement** si les tailles concordent, et le réduire à deux pages au plus (protocole, raccourci `Dst Port`, échec du RF). Les sous-sections « Coefficients et scores mono-feature » et « Ablation et permutation » passent alors en annexe. Formulation : « les deux fichiers sont identiques à ceux de la distribution officielle, qui compte 2²⁰ lignes physiques pour ces journées ; le corpus peut donc ne pas contenir tout le trafic des journées ». Si les tailles diffèrent, ou si la vérification n'est pas faite avant le dépôt : **retirer §4.6** et la ligne CSE-CIC du tableau 4.15, puis récrire H4 sur trois jeux.

Passages concernés en cas de retrait :
- `chapitre5_resultats.tex` l. 342–450 (§4.6 entier) et la ligne CSE-CIC de `tab:` comparaison aux règles simples (§4.15) ;
- `main.tex` l. 280–286 (résumé), abstract (l. ~305), bokuse l. 367 et 409 ;
- `chapitre1_introduction.tex` l. 135 (QR6, « quatre jeux publics »), 230 et 234 ;
- `chapitre2_etat_art.tex` (4 occurrences, à vérifier une à une) ;
- `chapitre6_approfondissements_scientifiques.tex` l. 19, 30 et 62 ; `limites_consolidees.tex` l. 8 et 11 ;
- `chapitre6_discussion.tex` l. 12, 18, 20 et 162 ;
- `chapitre6_conclusion.tex` l. 48 et 80 (« quatre jeux »), 81 et 116 ;
- `chapitre7_reproductibilite_deploiement.tex` l. 24 et 78 ; `annexes.tex` (5 occurrences, matrice A.2).

L'effet sur H4 est faible : le statut « non tranchée, supériorité infirmée » repose aussi sur CICIDS temporel, HDFS et BGL. Il faudrait seulement passer de « quatre jeux » à « trois jeux ».

## 4. CICIDS2017 non corrigé

- Le choix est écrit (`chapitre5_resultats.tex` l. 58). Le mémoire n'explique pas **pourquoi** les CSV d'origine sont utilisés. Justification proposée, si elle est exacte : « Les CSV d'origine sont conservés afin de rester comparable aux travaux qui les utilisent ; les défauts recensés par Engelen et al. et Lanvin et al. (étiquetage, flux dupliqués, attaques mal datées) affectent surtout la séparation aléatoire, que ce travail n'utilise pas comme estimation de la performance. » Sinon, déclarer la limite sans justification.
- « mêmes données corrigées » (`chapitre5_resultats.tex` l. 494) → remplacer par : « sur les mêmes données, chargées sans la fuite de l'étiquette ». Le mot « corrigé » doit être réservé, partout, à la version d'Engelen et al.
- À ajouter en §5 (validité) : le choix des CSV non corrigés s'ajoute au défaut de sélection du §0.1 ; les deux portent sur les mêmes résultats.

## 5. BGL : requalification

État du texte : la dégénérescence est décrite (l. 245) et la conception a posteriori de G est avouée (paragraphe « Ces huit variantes ont été explorées sans plan préalable… »). Le reproche porte maintenant sur la **place** de ces éléments et sur un intitulé trompeur.

Propositions :
1. **Protocole principal** : le présenter comme un **résultat négatif sur le détecteur**, et non comme une performance. Formulation : « Sur ce protocole, l'entraînement ne contient que des événements de sévérité INFO ; le seuil retenu sur la validation est le score maximal possible, si bien qu'Histogram applique exactement la règle « sévérité absente de l'entraînement ». Le F1 de 0,9137 mesure cette règle, et non une capacité de détection apprise. » La ligne BGL du tableau 4.15 se lit alors « Histogram = règle de sévérité », sans écart à commenter.
2. **Tableau 4.5 et protocole G** : déplacer le tableau en annexe, sous un titre explicite : « Variantes exploratoires BGL, conçues après observation du test ». Corriger la légende actuelle, « test et seuil indépendants », qui est fausse au sens méthodologique : le seuil est choisi sur la validation, mais le choix de la variante dépend du test. Nouvelle légende : « seuil choisi sur validation ; variantes explorées sans plan préalable, après lecture du test ».
3. Dans le corps du texte, garder une seule phrase : « Huit variantes exploratoires (annexe A.x), dont une conçue après observation du test, font varier le F1 de 0,5985 à 0,9419 : aucune valeur unique ne résume BGL, et aucune variante ne remplace le protocole principal. »
4. Ne citer G **nulle part** comme résultat : vérifier le résumé, la conclusion et la matrice A.2. Les seules valeurs admissibles sont celles d'un diagnostic de mécanisme (« lorsque la famille ciod est connue… »).
5. Ne pas créer de nouveau protocole BGL : il serait lui aussi conçu après lecture du test.

## 6. HDFS : graines et incertitude

1. Partout où figure « moyenne des graines 42 à 46 » ou « F1 moyen 0,868373 » (légende `fig:hdfs-event-bloc`, E-H4, résumés, A.2), écrire : « F1 0,8684, identique pour les cinq graines ». Les graines ne changent que l'échantillon d'ajustement du parseur ; elles ne constituent **qu'une seule observation** du test.
2. IC : formule unique, « intervalle bootstrap à 95 % sur les blocs de test : [0,8568 ; 0,8795] ». Remplacer `[0{,}8568\,;\,0{,}879493]` (l. 188), `[0{,}7491\,;\,0{,}784932]` et `[0{,}8000\,;\,0{,}961039]` (l. 192) par quatre décimales (coordination avec l'Agent E).
3. **Les 6 000 blocs** : le texte dit déjà « paramètre du protocole, non le résultat d'un calcul ». Ajouter la seule raison vérifiable, si elle est exacte : la taille d'ajustement de Drain3 a été bornée pour des raisons de temps de calcul. Sinon, écrire que la sensibilité du résultat à cette taille n'a pas été évaluée. C'est une expérience non faite, à déclarer.
4. **Prévalence** : ajouter une phrase. Le F1 dépend de la prévalence : à précision et rappel égaux, une prévalence de 1,46 % au test, contre 3,48 % en validation, abaisse mécaniquement la précision. Le seuil choisi en validation n'est donc pas optimal pour le test, et l'écart entre les deux prévalences est un facteur à part entière de la précision de 0,7674.

## 7. Préenregistrement : vérification de l'antériorité

Commits (heure locale UTC+1) comparés aux exécutions (registre `PROTOCOLES_PREENREGISTRES.md`, UTC) et aux dates des fichiers :

| Protocole | Commit (UTC) | Début d'exécution (UTC) | Antériorité | Runner : empreinte du protocole contre fichier actuel |
|---|---|---|---|---|
| E-H4 | `5dc8cbc` 12:30:54 | 12:33 (tentative arrêtée) ; 13:06:17 (retenue) | OK | Diffère (`83ce9265…`), car le runner a été corrigé deux fois après le commit ; écarts consignés au registre (clés JSON) ; critère inchangé |
| E-H3b | `3c86587` 12:31:52 | artefacts 12:42 | OK | Conforme |
| E-H5 | `658e639` 14:40:46 | 14:42:28 | OK | Conforme |
| E-CNP | `472d5e7` 14:40:52 | 14:50:21 | OK | Conforme |
| E-CNP-LL | `6db45dd` 15:39:26 | 15:40:00 | OK (34 s) | Conforme |
| E-H3B-STRICT | `8876861` 15:39:43 | 15:48:14 | OK | Conforme |

Faits à déclarer :
- Les runners n'ont été **commités qu'après** les exécutions (`27deb22`, 16:27 UTC). Leur contenu antérieur est garanti seulement par l'empreinte inscrite dans le protocole commité, et elle concorde, sauf pour E-H4, dont les corrections sont documentées.
- **Aucun commit de protocole n'est présent sur le dépôt distant** (`git branch -r --contains 8876861` ne renvoie rien ; `origin/main` est à `35da3a9`). Les horodatages sont ceux de la machine de l'auteur, sans ancre externe.
- E-CNP-LL et E-H3B-STRICT ont été conçus après lecture d'E-CNP et d'E-H3b. Tous les protocoles datent du 5 novembre 2026.
- `scripts/run_family_routing_ablation.py` a été modifié après exécution (`786919b`) ; c'est documenté au registre.
- E-H3b était préenregistrée **et** fautive : le préenregistrement protège les critères, non la justesse du code.

Formulation à retenir (déclaration IA, introduction, chapitre 5) :
« Six protocoles complémentaires (E-H3b, E-H3b stricte, E-H4, E-H5, E-CNP et E-CNP au moindre chargé) ont été rédigés, assortis de l'empreinte de leur programme, puis versionnés dans le dépôt local avant leur exécution ; l'ordre des commits et des exécutions est vérifiable dans l'historique. Ce versionnement n'est pas un préenregistrement auprès d'un registre externe : il ne garantit ni l'absence de commits antérieurs non publiés, ni la justesse du code. Deux de ces protocoles ont été conçus après lecture de résultats antérieurs. Les hypothèses H1 à H5 et leurs grandeurs de décision n'ont pas été préenregistrées. »

Proposition à l'auteur, qui ne coûte rien : pousser la branche vers le dépôt distant **dès maintenant**. Cela ne rend pas antérieurs des commits déjà faits, mais cela fige l'historique avant la soutenance. Ne pas écrire que les protocoles ont été « publiés » avant exécution.

### 7 bis. Corrélation des mesures et comparaisons multiples

- E-H3B-STRICT : préciser l'unité du rééchantillonnage de l'IC apparié (graine ? catégorie × graine ?). Si les 18 catégories × 5 graines sont traitées comme indépendantes, l'IC est trop étroit, et il faut l'écrire. Vérification à faire dans `run_e_h3b_strict.py`, fonction de l'IC, avant intégration.
- Comparaisons multiples : E-H5 (3 niveaux), E-CNP et E-CNP-LL (4 scénarios × 2 ou 3 contrastes) et E-H3B-STRICT (3 familles) sont des règles de décision **préfixées** à IC 95 % non corrigés. Écrire une seule fois, au chapitre 5 : « les intervalles ne sont pas corrigés pour la multiplicité ; avec une vingtaine de contrastes, environ un intervalle à 95 % peut exclure zéro par hasard. Les décisions défavorables, plus nombreuses, n'en sont pas affectées ; les décisions favorables isolées (E-H5 à p = 0,9) doivent être lues avec cette réserve. » Calcul et éventuelle correction de Holm : Agent B.

## 8. Routeur et corrélation : formulation honnête

- **Routeur** (§4.7 et limites), à ajouter : « Pour les journaux texte, les scores du routeur reprennent les colonnes `dataset` et `subtype` du parseur de format : le rejet de 20 inconnus sur 20 mesure donc en partie la capacité du parseur à ne pas reconnaître un format, et non une décision indépendante. La calibration repose sur trois fichiers inconnus ; l'intervalle de Clopper-Pearson sur le rejet, [0,292 ; 1] à la calibration, en reflète la faiblesse. » Vérifier dans l'artefact `agent5_router_open_set_20261104T145601Z` la borne pour 20/20 sur l'ensemble étendu avant de la citer.
- **Corrélation** : la déclaration actuelle (l. 796) suffit. La déplacer dans la section unique des limites, garder au corps une demi-phrase (« évaluée en circuit fermé, voir § limites ») et retirer de la conclusion et des résumés toute précision de corrélation (0,9884) présentée sans cette réserve.

## 9. Effet sur le volume

| Action | Pages |
|---|---|
| §4.6 CSE-CIC réduit à 2 p. (ou retiré) | −4 (−6 si retrait) |
| Tableau 4.5 et paragraphes G vers l'annexe | −1,0 au corps, +0,7 en annexe |
| §4.2 : description du protocole et réserve d'audit | +0,3 |
| §5 : audit, multiplicité, préenregistrement (en remplacement de phrases existantes) | +0,3 |
| HDFS, routeur, corrélation (reformulations à volume constant ; corrélation renvoyée aux limites) | −0,2 |
| **Net** | **≈ −4 p. (−6 avec retrait de §4.6)** |

Si les tests et la réexécution du holdout CICIDS sont faits, il faut compter +0,5 p. en annexe (description des tests) et réécrire le §4.2 avec les nouveaux chiffres. Je n'en fournis aucun : rien n'a été exécuté.

=== PASSATION ===
Agent : C — Intégrité des données et validité interne
Statut : terminé
Livrable : `revision_reports/refonte_150p/agent_C/LIVRABLE_C.md`
Constats décisifs :
1. Holdout par scénario CICIDS2017 (tableau des cinq candidats et RF 0,1577) entraîné sur les premières lignes d'un seul fichier (DDoS, ou PortScan) : défaut de même nature qu'E-H3b, non encore déclaré ; il touche le chiffre phare des résumés et QR6.
2. E-H3B-STRICT non touchée : le chargeur fautif est importé mais seules des fonctions inchangées par `786919b` sont exécutées.
3. CSE-CIC-IDS2018 : 2²⁰ lignes physiques par fichier ; vérifier les tailles sur S3, sinon retirer §4.6.
4. Préenregistrement : antériorité vérifiée dans l'historique local, aucune ancre distante.
Questions à l'auteur : (a) réexécuter le holdout CICIDS avec un tirage couvrant tous les scénarios, avant soutenance, ou déclarer le défaut ? (b) vérifier les tailles CSE-CIC sur S3 ? (c) pousser la branche vers `origin` ?
Pour l'Agent B : l'Infiltration (32 attaques) et le seuil par défaut s'ajoutent au défaut de sélection ; toute recalibration CICIDS doit partir d'un échantillonnage corrigé. L'IC d'E-H3B-STRICT est à vérifier (unité de rééchantillonnage).
Pour les Agents A et E : le 0,9951 → 0,1577 des résumés et de QR6 doit être requalifié (transfert d'un scénario vers un autre).
Ne pas faire : ne citer aucun chiffre de remplacement tant qu'aucune réexécution n'a eu lieu.
=== FIN PASSATION ===
