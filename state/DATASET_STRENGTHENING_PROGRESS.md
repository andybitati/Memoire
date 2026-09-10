# État de la mission — renforcement scientifique des datasets

Dernière mise à jour : 2026-09-10.

## Étapes terminées

- Audit préalable : `docs/DATASET_STRENGTHENING_GAP_ANALYSIS.md`.
- Protocole général gelé avant exécution.
- Implémentation des campagnes HDFS, BGL, CICIDS temporel, routeur indépendant,
  multiformat équilibré et replay multi-source CNP.
- Parseurs légers HDFS et BGL raccordés au pipeline commun.
- Quatorze garde-fous automatiques exécutés après les campagnes : **14/14 réussis**.
- Preuve JUnit : `experiments/phase_dataset_strengthening/logs/pre_experiment_tests.xml`.
- Preuve JUnit finale :
  `experiments/phase_dataset_strengthening/logs/final_dataset_strengthening_tests.xml`.
- Dry-runs validés : CICIDS (78 features, 5 seeds), routeur (31 fichiers,
  9 groupes), multiformat (8 sources), CNP E2E (7 champs `AgentMessage`).
- HDFS block-level : run `ds_hdfs_block_20260910T081756Z`, 575 061 blocs
  répartis sans intersection, Drain3 train-only vérifié par hash, agrégateur
  `mean` choisi sur validation, F1 test bloc `0,8923076923`.
- BGL known/unknown : run `ds_bgl_known_unknown_20260910T082706Z`, taux de
  templates inconnus `0,8980811734`, F1 Histogram `0,9136975455`, F1
  `UnknownTemplateBaseline` `0,2778848006`; tous les vrais positifs Histogram
  sont dans le groupe inconnu, tandis que la baseline produit 14 994 faux
  positifs.
- CICIDS temporal holdout : run `cicids_temporal_20260910T083015Z`, 78
  caractéristiques, fichiers lundi--jeudi train et vendredi test, cinq graines
  sur un pool parent figé. F1 moyen RandomForest `0,4374291751`, F1 moyen
  LogisticRegression `0,5566145428`. Les dates et jours servent uniquement au
  split. Les échantillons sont équilibrés et les graines restent corrélées par
  leur pool parent commun; cette limite doit être conservée.
- Routeur indépendant : le premier run `router_independent_20260910T092757Z`
  conserve l’échec des huit fichiers CICIDS causé par les espaces des en-têtes.
  Après deux corrections et 14/14 tests réussis, le run final
  `router_independent_20260910T094257Z` traite 31 fichiers, 9 groupes et zéro
  erreur. Accuracy `0,9032258065`, macro-F1 `0,7777777778`, accuracy des
  familles connues `1,0`. Les trois sources open-set sont toutes routées
  `network`; leur taux de rejet est `0,0`. La marge est un score heuristique,
  pas une probabilité calibrée.
- Multiformat équilibré : le premier run a révélé que les colonnes standard
  vides biaisaient le routage BGL vers Windows. Ce run est conservé. Après
  correction, le run final `multiformat_balanced_20260910T094422Z` lit, parse
  et normalise `7001/7001` unités sans duplication ni perte : 1000 pour chaque
  source sauf Apache (`N=1`, fixture synthétique). HDFS et BGL atteignent chacun
  `1000/1000`. Le routage de lot final identifie BGL correctement. Les taux de
  complétude restent propres à chaque famille et ne démontrent pas une
  préservation brute universelle.
- Replay multi-source CNP : run `multisource_cnp_20260910T095810Z`, `1401`
  unités lues, normalisées, routées et évaluées sans erreur; `122` candidats
  et `2` incidents heuristiques ont été produits. Les `11 408` messages
  respectent exactement les sept champs du contrat `AgentMessage` et partagent
  un seul `run_id`. La détection exécutée est la règle légère
  `e2e_lightweight_candidate_rule_v1`; ce replay ne constitue donc pas une
  évaluation prédictive des artefacts de modèles recommandés par le routeur.
- Cartes de données, matrice revendication--preuve, rapport final, validation
  automatique, dix figures et manifeste SHA-256 produits.
- Validation finale : les six campagnes prioritaires satisfont tous les
  contrôles; `all_six_priority_campaigns_valid = true`.
- Dataset externe optionnel : **NON EXÉCUTÉ**. Le transfert vers un jeu externe
  officiel supplémentaire reste **NON DÉMONTRÉ**.
- Contrôle UTF-8 ciblé des livrables et artefacts textuels : aucun fichier
  invalide et aucun motif de mojibake détecté.

## Incident d’outillage conservé

`graphify update .` a échoué après l’extraction avec `[WinError 5] Accès refusé`.
Cet échec d’indexation ne modifie ni le code expérimental ni les données.

## Prochaine action exacte

Transmettre à la phase de rédaction uniquement les recommandations et les
preuves validées du rapport final. Ne pas présenter le replay CNP comme une
évaluation prédictive et ne pas revendiquer de transfert externe.

Le mémoire `ARIEL_LOGMINER_MEMOIRE_FINAL` n’a pas été modifié par cette mission.
