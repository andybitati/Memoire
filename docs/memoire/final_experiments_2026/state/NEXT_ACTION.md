# NEXT ACTION

Phase: PHASE 7

Experiment: Résilience complémentaire — audit GO/NO-GO

Last completed step: PHASE 6 complète, 81/81 fichiers routés, matrice inspectée et reprise idempotente validée.

Next exact step: Inventorier les campagnes panne/reprise existantes et déterminer si un nouveau scénario apporte une information distincte de D002.

Command to run: `rtk graphify query "Quelles campagnes Redis de panne, reprise, pending, ACK, doublons et pertes existent déjà et quels artefacts les prouvent ?"`

Expected output: Sous-graphe ciblé des scripts et preuves existantes permettant une décision RUN ou SKIPPED justifiée.

Files that must be read: scripts de campagnes Redis/résilience révélés par Graphify et leurs résumés/artefacts existants.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, artefacts HDFS/BGL phase 3, modèles phase 4, anciens rapports éditoriaux et multi-VM.

Success criterion: Lancer uniquement un scénario qui mesure une propriété non déjà démontrée ; sinon enregistrer SKIPPED avec justification et passer à la phase 8.

If failure: Ne pas relancer les campagnes existantes pour produire du volume ; classer la phase optionnelle SKIPPED si aucune preuve nouvelle sûre n'est accessible.
