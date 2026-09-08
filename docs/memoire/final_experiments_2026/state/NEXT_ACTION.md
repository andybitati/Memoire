# NEXT ACTION

Phase: PHASE 6

Experiment: Évaluation du routeur réel — audit et protocole

Last completed step: PHASE 5 complète, huit runs et quatre CSV validés, figure inspectée, reprise idempotente vérifiée.

Next exact step: Identifier l'API réellement utilisée pour attribuer une famille/modèle, les règles, la confiance et le fallback ; construire uniquement ensuite le corpus de vérité terrain.

Command to run: `rtk graphify query "Où le routeur réel attribue-t-il une famille ou un modèle à un événement, avec quelles règles, confiance et fallback ?"`

Expected output: Sous-graphe ciblé vers l'implémentation réellement appelée et ses points d'entrée, distinct du simple `detect_kind` de phase 5.

Files that must be read: fichiers du routeur révélés par Graphify, appels depuis les agents/runtime, configurations de modèles.

Files that DO NOT need to be reread: mémoire LaTeX complet, artefacts CICIDS unitaires, artefacts HDFS/BGL phase 3, modèles phase 4, anciens rapports éditoriaux et multi-VM.

Success criterion: Une définition exacte du routeur réel et un corpus où `true_family` provient de la source, sans réutiliser la famille prédite comme vérité terrain.

If failure: Classer l'exactitude du routeur comme NON ÉVALUÉE et documenter précisément l'absence d'API ou de vérité terrain ; ne pas substituer l'ablation D005.
