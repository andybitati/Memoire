# NEXT ACTION

Phase: PHASE 8

Experiment: Corrélation d'incidents synthétique — audit GO/NO-GO

Last completed step: PHASE 7 clôturée `SKIPPED` après audit de la preuve avant traitement/ACK et constat d'indisponibilité Redis.

Next exact step: Identifier l'algorithme de corrélation réellement implémenté, ses entrées/sorties et les tests ou artefacts existants; décider si une vérité terrain synthétique contrôlée peut être figée sans adapter le protocole aux sorties.

Command to run: `rtk graphify query "Où la corrélation d'incidents est-elle implémentée, quelles règles utilise-t-elle et quels tests ou artefacts la couvrent ?"`

Expected output: Sous-graphe ciblé des fonctions, règles, seuils, tests et sorties de corrélation permettant une décision RUN ou SKIPPED.

Files that must be read: Fichiers révélés par Graphify pour la corrélation et leurs tests directs; D001–D027 si une conclusion semble contradictoire.

Files that DO NOT need to be reread: mémoire complet, artefacts CICIDS unitaires, JSON HDFS/BGL, modèles phase 4 et anciens rapports multi-VM.

Success criterion: Pré-spécifier une vérité terrain et des métriques pairwise propres avant toute exécution, ou documenter précisément pourquoi la phase optionnelle est `SKIPPED`.

If failure: Ne pas créer une validation SOC artificielle; classer la phase `SKIPPED` et conserver le statut `NON ÉVALUÉ`.

