# État de la mission — renforcement scientifique des datasets

Dernière mise à jour : 2026-09-10.

## Étapes terminées

- Audit préalable : `docs/DATASET_STRENGTHENING_GAP_ANALYSIS.md`.
- Protocole général gelé avant exécution.
- Implémentation des campagnes HDFS, BGL, CICIDS temporel, routeur indépendant,
  multiformat équilibré et replay multi-source CNP.
- Parseurs légers HDFS et BGL raccordés au pipeline commun.
- Douze garde-fous automatiques exécutés avant les campagnes : **12/12 réussis**.
- Preuve JUnit : `experiments/phase_dataset_strengthening/logs/pre_experiment_tests.xml`.
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

## Incident d’outillage conservé

`graphify update .` a échoué après l’extraction avec `[WinError 5] Accès refusé`.
Cet échec d’indexation ne modifie ni le code expérimental ni les données.

## Prochaine action exacte

Exécuter `scripts/run_router_independent_strengthening.py`, valider ses
artefacts et sa méthodologie, puis seulement passer au multiformat équilibré.

Le mémoire `ARIEL_LOGMINER_MEMOIRE_FINAL` n’a pas été modifié par cette mission.
