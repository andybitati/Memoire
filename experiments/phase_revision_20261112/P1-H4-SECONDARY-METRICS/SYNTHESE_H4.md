# Analyse secondaire de H4 (non préenregistrée), 2026-11-12

Objet : répondre au relecteur (F1 au seuil par défaut contre « tout positif » sur tests
équilibrés ; références construites en regardant le test). Aucune décision préenregistrée
n'est modifiée. Toutes les valeurs proviennent des fichiers cités.

| Jeu, protocole | Référence (statut) | F1 modèle / réf. | MCC modèle (réf.) | PR-AUC modèle (prévalence) | Source |
|---|---|---|---|---|---|
| CICIDS2017, holdout par scénario | Tout positif (fixée a priori, préenregistrée) | 0,157 à 0,287 / 0,4737 | 0,109 à 0,183 en moyenne (0) ; ≤ 0 sur PortScan et Infiltration pour tous les modèles | > prévalence pour 25/25 couples modèle × scénario | `phase_revision_20261105/E-CICIDS-HOLDOUT-FIX/metrics.csv` ; `cicids_holdout_secondary_by_*.csv` |
| CICIDS2017, lun.–jeu. → ven. | Tout positif (a priori) | LR 0,5566 ; RF 0,4374 / 0,6667 | LR 0,4363 ; RF 0,3991 (0) | LR 0,8714 ; RF 0,8308 (0,5) | `phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv` |
| HDFS, bloc, test complet | Surprise moyenne des templates (apprise sur le normal, seuil calibré : **modèle léger**) | Histogram 0,868373 / 0,872434 | 0,874026 / 0,877713 | non enregistrée | `phase_revision_20261105/E-H4-HDFS-BLOCK-BASELINES/metrics_by_seed.csv` ; `hdfs_block_mcc_summary.csv` |
| HDFS, idem | Meilleure règle triviale : any_unseen_template | 0,868373 / 0,019076 | 0,874026 / 0,092935 | — | idem |
| BGL, événement, protocole principal R0 | Sévérité absente du train (**construite après lecture du test**) | 0,913698 / 0,913698 | Histogram 0,902319 | 0,841108 (0,1449 = 2 885/19 908) | `phase_revision_20261104/agent_4_bgl/agent4_bgl_second_protocol_20261104T142629Z__result.json`, `…__group_metrics.csv` |
| CSE-CIC-IDS2018, 15 → 16, prévalence observée | Dst Port < 1024 (**construite après lecture du test**) | LR 0,994345 / 0,999728 | LR 0,9868 (règle 0,9994) | LR 0,9997 (0,5714) | `phase_revision_20261104/agent_4_csecic/agent4_csecic_shortcut_20261104T144738Z__printed_summary.txt` |
| CSE-CIC-IDS2018, 15 → 16, sans Dst Port | — | LR 0,728397 (tout positif ≈ 0,7273) | LR 0,0584 | LR 0,3749 (0,5714) | idem |
| CSE-CIC-IDS2018, 16 → 15 | Dst Port < 1024 : 0,121517 ; tout positif ≈ 0,095 (2p/(1+p), p = 0,0499) | LR 0,234195 | LR 0,2292 (règle 0,1246) | LR 0,1408 (0,0499) | idem |

Constats :
1. CICIDS2017 temporel : la réfutation en F1 tient à la prévalence (test équilibré) ; en MCC et
   PR-AUC, les deux modèles dépassent nettement la référence triviale.
2. CICIDS2017 par scénario : la décision préenregistrée (F1) est confirmée par le MCC sur 2 à 3
   scénarios sur 5 ; la PR-AUC montre une information de classement réelle, mais le seuil appris
   ne se transfère pas à une attaque inconnue.
3. HDFS : l'issue dépend du statut de la référence (règle ou modèle léger).
4. BGL et CSE-CIC-IDS2018 (15 → 16) : références construites après lecture du test, donc non
   probantes. Sur CSE-CIC, le succès de LR tient au port de destination (artefact de la
   journée du 16) : sans cette variable, LR est au niveau de « tout positif ».
5. CSE-CIC 16 → 15 : LR dépasse les deux références triviales en F1 et en MCC, avec des scores
   faibles (F1 0,234).

F1 à seuil calibré : impossible sans réexécution (scores par ligne non conservés).
