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

Current status: OPEN — échec reproduit après la modification du runner de phase 2 le 2026-09-08 ; le runner et les expériences restent exécutables.

Next action: Ne plus retenter à chaque batch ; retenter uniquement après une modification de code majeure et conserver le graphe existant pour les requêtes.

## E0004 — Résolution du champ CICIDS ` Label`

Error: Le premier calcul du manifeste a échoué avec `Usecols do not match columns`.

Command: `rtk python scripts/run_final_experiments.py --phase 0`

Short traceback: `ValueError: ... columns expected but not found: ['Label']`.

Probable cause: Le nom physique de la colonne dans les fichiers CICIDS est `' Label'` avec un espace initial ; l'en-tête normalisé avait supprimé cet espace avant le passage à pandas.

Already attempted: Comparaison de l'en-tête normalisé à `Label`.

Current status: RESOLVED IN CODE — la sélection compare désormais les noms normalisés tout en conservant le nom physique.

Next action: Relancer la phase 0 ; l'environnement déjà écrit peut être régénéré sans perte.

## E0005 — Écriture Git initialement refusée par le bac à sable

Error: Création de `.git/index.lock` refusée lors du premier `git add`.

Command: `rtk git add -- scripts/run_final_experiments.py docs/memoire/final_experiments_2026`

Short traceback: `fatal: Unable to create '.git/index.lock': Permission denied`.

Probable cause: Le dossier `.git` est en lecture seule dans le bac à sable standard.

Already attempted: Commande dans le bac à sable, puis même commande avec autorisation explicite.

Current status: RESOLVED — checkpoint `4db70f0` créé, limité aux douze fichiers de phase 0.

Next action: Demander l'autorisation d'écriture Git uniquement aux checkpoints ultérieurs.

## E0006 — Cache Python verrouillé

Error: `py_compile` n'a pas pu remplacer le fichier `.pyc` de `run_final_experiments.py`.

Command: `rtk python -m py_compile scripts/run_final_experiments.py`

Short traceback: `[WinError 5] Accès refusé: ...run_final_experiments.cpython-311.pyc...`.

Probable cause: Fichier `__pycache__` verrouillé ou non inscriptible.

Already attempted: Compilation directe ; l'import réel du module et le dry-run ont ensuite réussi.

Current status: OPEN NON BLOQUANT — le source s'importe et s'exécute correctement.

Next action: Ne pas supprimer le cache ; utiliser l'import/dry-run comme contrôle et réévaluer uniquement si l'exécution échoue.

## E0007 — HistGradientBoosting bloqué par les pipes du bac à sable

Error: Les cinq fits DDoS de HistGradientBoosting échouent lors de la création du pool de threads interne.

Command: `rtk python scripts/run_final_experiments.py --resume --phase 2 --scenario DDoS --model HistGradientBoosting`

Short traceback: `PermissionError: [WinError 5] Accès refusé` dans `multiprocessing.connection.Pipe`, appelé par joblib puis `_BinMapper.fit_transform`.

Probable cause: Restriction du bac à sable Windows sur les pipes utilisés par le backend de threads de joblib.

Already attempted: Cinq seeds dans le bac à sable ; toutes ont produit le même type d'échec. Aucun artefact de résultat n'a été créé.

Current status: RESOLVED — relance hors bac à sable réussie pour les cinq seeds, protocole inchangé ; échecs initiaux conservés.

Next action: Utiliser directement l'exécution autorisée hors bac à sable pour les futurs batches HistGradientBoosting.
