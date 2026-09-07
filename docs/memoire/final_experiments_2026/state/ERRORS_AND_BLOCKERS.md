# ERRORS AND BLOCKERS

## E0001 — Interpolation PowerShell pendant l'inventaire

Error: Les expressions `$_` ont été consommées par l'enveloppe PowerShell avant d'atteindre la commande interne.

Command: Inventaire récursif avec `Where-Object` et regroupement par répertoire.

Short traceback: `.Length : Le terme « .Length » n'est pas reconnu`.

Probable cause: Double interprétation de la chaîne transmise à `rtk powershell -Command`.

Already attempted: Une commande de regroupement et une commande de filtrage.

Current status: RESOLVED — aucune écriture ni altération de données ; reprise avec des commandes sans variable de pipeline.

Next action: Utiliser `rg --files` et des sélections PowerShell directes sans `$_`.

## E0002 — Dépendance Drain3 absente de l'interpréteur actif

Error: `importlib.metadata.PackageNotFoundError: drain3` lors du premier relevé d'environnement.

Command: Inspection Python des versions installées.

Short traceback: `No package metadata was found for drain3`.

Probable cause: Les dépendances HDFS/BGL sont volontairement séparées dans `requirements-hdfs-bgl.txt`.

Already attempted: Détection directe par `importlib.metadata.version`.

Current status: OPEN — n'empêche pas les phases CICIDS 1 et 2.

Next action: Préparer un environnement dédié avant la phase 3 ; ne pas installer avant d'avoir figé l'environnement courant.

## E0003 — Mise à jour Graphify refusée

Error: Reconstruction du graphe refusée par Windows.

Command: `rtk graphify update .`

Short traceback: `[WinError 5] Accès refusé`.

Probable cause: Un artefact Graphify est verrouillé ou non inscriptible dans le contexte courant.

Already attempted: Une mise à jour après ajout du runner.

Current status: OPEN — le runner et les expériences restent exécutables ; le graphe existant a été utilisé pour l'inventaire initial.

Next action: Retenter après la phase 0 ou documenter durablement si le verrou persiste.

## E0004 — Résolution du champ CICIDS ` Label`

Error: Le premier calcul du manifeste a échoué avec `Usecols do not match columns`.

Command: `rtk python scripts/run_final_experiments.py --phase 0`

Short traceback: `ValueError: ... columns expected but not found: ['Label']`.

Probable cause: Le nom physique de la colonne dans les fichiers CICIDS est `' Label'` avec un espace initial ; l'en-tête normalisé avait supprimé cet espace avant le passage à pandas.

Already attempted: Comparaison de l'en-tête normalisé à `Label`.

Current status: RESOLVED IN CODE — la sélection compare désormais les noms normalisés tout en conservant le nom physique.

Next action: Relancer la phase 0 ; l'environnement déjà écrit peut être régénéré sans perte.
