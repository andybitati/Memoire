# Matrice claim–evidence — renforcement des datasets

| Claim | Dataset | Protocole | Preuve | Limite | Statut |
| --- | --- | --- | --- | --- | --- |
| L’évaluation HDFS est alignée sur le bloc | HDFS_v1 | split block_id 60/20/20, Drain3 train-only, agrégateur choisi sur validation | F1 test bloc `0.892308` ; intersections vides ; hash Drain3 inchangé | 2 000 blocs test dont 29 positifs ; non équivalent à l’ancien événementiel | SOUTENU |
| La nouveauté de template explique une partie mais pas toute la performance BGL | BGL | ALL/KNOWN/UNKNOWN + UnknownTemplateBaseline | inconnus `89.8081%` ; F1 baseline `0.277885` vs Histogram `0.913698` | aucune anomalie dans KNOWN_TEMPLATE ; copie locale non prouvée bit à bit | PARTIELLEMENT SOUTENU |
| CICIDS généralise imparfaitement au vendredi | CICIDS2017 | lundi–jeudi train, vendredi test, cinq graines | F1 RF `0.437429` ; LR `0.556615` | pools équilibrés ; graines corrélées par pool parent ; copie officielle exacte non démontrée | SOUTENU |
| Le routeur reconnaît les familles connues sur des fichiers non chunkés | 31 fichiers / 9 groupes | une observation par fichier, aucun signal de chemin | known accuracy `1.000000` ; 0 erreur | dépendance intra-groupe ; open-set rejection `0.000000` | PARTIELLEMENT SOUTENU |
| HDFS/BGL passent par le pipeline multiformat commun | 8 sources | maximum 1 000/source sans duplication | 7 001/7 001 parsées et normalisées ; HDFS/BGL 1 000/1 000 | Apache N=1 synthétique ; complétude variable ; pas de préservation brute universelle | SOUTENU |
| Les vrais agents CNP traitent plusieurs familles avec une trace unitaire | 8 sources | 1 401 tâches CNP déterministes | `1401` entrées, `0` erreur, 11 408 messages à 7 champs | détecteur candidat heuristique ; aucune vérité terrain prédictive fabriquée | SOUTENU |
| Les conclusions réseau se transfèrent à un dataset officiel externe | Dataset externe | nouveau téléchargement officiel requis | aucune campagne | Parquet locaux non admissibles comme preuve indépendante | NON ÉVALUÉ |
