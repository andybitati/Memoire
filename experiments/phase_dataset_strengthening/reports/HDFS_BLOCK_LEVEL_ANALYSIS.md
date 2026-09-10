# HDFS — évaluation au niveau block_id

- Run : `ds_hdfs_block_20260910T081756Z`
- Blocs observés : `575061` ; partitions 60/20/20 : `{'train': 345036, 'validation': 115012, 'test': 115013}`.
- Blocs sélectionnés : `{'train': 6000, 'validation': 2000, 'test': 2000}`.
- Événements sélectionnés : `{'train': 126368, 'validation': 37153, 'test': 30948}`.
- Intersections train/validation/test : vides.
- Drain3 : `126368` appels train, `0` mise à jour validation/test.
- Seuil événementiel choisi sur validation : `3.181118253`.
- F1 événementiel sur ce test : `0.213115`.
- Agrégateur bloc retenu sur validation : `mean` ; seuil `1.272942934`.
- F1 bloc sur test gelé : `0.892308`.

L’ancien F1 événementiel `0,269307` reste un résultat d’un autre protocole. Il n’est pas traité comme un benchmark équivalent.
