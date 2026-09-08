# NEXT ACTION

Phase: PHASE 5

Experiment: Validation multiformat étendue — conception du protocole

Last completed step: PHASE 4 complète, 3/3 décisions exécutées et intégrité vérifiée ; figure inspectée.

Next exact step: Inventorier les sources réelles utilisables, définir pour chaque format l'unité brute et la limite de 500 à 1 000 événements, puis figer la configuration avant exécution.

Command to run: `rtk graphify explain "détection et pipeline de parsing multiformat"`

Expected output: Sous-graphe ciblé permettant de relier détecteur, parseurs, normalisation et schéma sans rescanner le dépôt.

Files that must be read: `src/logminer/detectors/file_detector.py`, `src/logminer/pipeline.py`, `src/logminer/io/csv_writer.py`, parseurs sélectionnés et sources locales candidates.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, artefacts HDFS/BGL phase 3, modèles phase 4, anciens rapports éditoriaux et multi-VM.

Success criterion: Une configuration phase 5 figée qui n'inclut que des formats avec parseur et source démontrables, sépare parsing/normalisation/routage et prévoit les quatre CSV exigés.

If failure: Exclure le format concerné ou utiliser tout le volume réellement disponible en documentant la limite ; ne jamais fabriquer un corpus présenté comme réel.
