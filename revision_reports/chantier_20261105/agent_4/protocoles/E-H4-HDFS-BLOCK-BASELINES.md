# Protocole préenregistré — E-H4-HDFS-BLOCK-BASELINES

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit C13-proc**.

## Question

Sur la partition chronologique HDFS 60/20/20 déjà gelée, le détecteur Histogram au niveau `block_id` dépasse-t-il des règles simples évaluées sur exactement les mêmes 115 013 blocs de test ? Cette expérience ne fixe pas rétroactivement le budget de H4 et ne peut donc pas valider H4 dans son ensemble.

## Entrées gelées

- Journal : `data/raw/Datasets/HDFS_1/HDFS.log`.
- Étiquettes : `data/raw/Datasets/HDFS_1/anomaly_label.csv`.
- Partition : `experiments/phase_dataset_strengthening/processed/ds_hdfs_block_20260910T081756Z__hdfs_full_block_partitions.txt.gz` ; ordre par première occurrence, 60/20/20.
- Résultat de référence : `experiments/phase_revision_20261104/agent_2_hdfs/agent2_hdfs_full_20261104T134240Z__result.json`.
- États Drain3 des graines 42 à 46 : chemins et empreintes déclarés dans ce résultat ; le programme doit refuser l'exécution si une empreinte diffère.
- Programme : `revision_reports/chantier_20261105/agent_4/run_e_h4_hdfs_baselines.py`, SHA-256 `0bc6dbdf405e64aabdbf7e7ded86ced9335a241beb24c94a3822df0f6753082a`.

## Comparateurs

1. `all_positive` : chaque bloc est déclaré anormal.
2. `any_unseen_template` : un bloc est anormal s'il contient au moins un événement qu'aucun cluster de l'état Drain3 gelé de la graine ne reconnaît.
3. `template_only_mean_surprisal` : moyenne, par bloc, de `-ln(max(n_t,1)/N)`, où `n_t` est la fréquence du template parmi les événements normaux des 6 000 blocs d'entraînement de la graine et `N` leur nombre total ; le seuil maximise le F1 sur les 115 012 blocs de validation, avec départage par FPR minimal puis seuil maximal.
4. `histogram_source_result` : résultat principal déjà gelé, qui moyenne les surprises du template, de la source et de la sévérité ; aucun réajustement.

## Taille, graines et unité

- Unité : `block_id`, identique à l'unité de la vérité terrain.
- Entraînement de référence : 6 000 blocs stratifiés par graine.
- Validation : 115 012 blocs complets.
- Test : 115 013 blocs complets, dont 1 679 positifs selon l'artefact source.
- Graines : 42, 43, 44, 45 et 46.

## Métrique et critère numérique

- Métrique primaire : F1 de test au niveau bloc, moyenne des cinq graines.
- Métriques secondaires : précision, rappel, FPR et matrice de confusion.
- Critère fixé avant exécution : le résultat Histogram dépasse les baselines simples si son F1 moyen excède d'au moins `0,01` celui de la meilleure des trois baselines simples. Une marge inférieure conduit à « avantage prédictif non établi » ; une baseline supérieure conduit à « résultat dominé par une règle simple ».
- Les cinq graines sont toutes rapportées, même si leurs décisions sont identiques.

## Analyse prévue

Le seuil du comparateur de surprise est choisi exclusivement sur validation, puis gelé. Le test n'intervient ni dans la définition des règles ni dans le choix du seuil. Les résultats sont rapportés sans changer les comparateurs ou le critère après lecture des sorties. Le résultat ne sera pas comparé directement aux F1 publiés sous d'autres partitions.

## Commande

Depuis la racine du dépôt :

```powershell
.venv-hdfs-bgl\Scripts\python.exe revision_reports\chantier_20261105\agent_4\run_e_h4_hdfs_baselines.py
```

## Artefacts attendus

Dossier `experiments/phase_revision_20261105/E-H4-HDFS-BLOCK-BASELINES/` :

- `metrics_by_seed.csv` ;
- `summary.json` ;
- `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
