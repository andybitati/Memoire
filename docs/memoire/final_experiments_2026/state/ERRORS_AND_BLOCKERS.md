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

## E0008 — Conflit de dépendance Drain3 dans l'environnement partagé

Error: `drain3==0.9.11` impose `cachetools==4.2.1`, incompatible avec `streamlit==1.57.0` qui exige `cachetools>=5.5,<8`.

Command: `rtk python -m pip install drain3==0.9.11`

Short traceback: Installation réussie avec avertissement du résolveur pip sur l'incompatibilité Streamlit/cachetools.

Probable cause: Métadonnées de dépendance strictes et anciennes de Drain3 0.9.11.

Already attempted: Drain3 retiré de l'environnement global ; cachetools 7.1.2 restauré ; `pip check` global sans erreur. Venv `.venv-final-experiments` créé avec `--system-site-packages`; Drain3 et cachetools 4.2.1 installés localement. Import et premier cluster Drain3 réussis.

Current status: RESOLVED WITH ISOLATION — l'environnement global n'est pas dégradé ; le venv dédié exécute Drain3. Le venv n'est pas destiné à exécuter Streamlit.

Next action: Utiliser exclusivement `.venv-final-experiments/Scripts/python.exe` pour la phase 3 et enregistrer versions/configuration dans les artefacts.

## E0009 — Échec SSL pendant l'installation Drain3 dans le venv

Error: `SSLCertVerificationError: unable to get local issuer certificate`.

Command: `rtk .\.venv-final-experiments\Scripts\python.exe -m pip install drain3==0.9.11`

Short traceback: Cinq tentatives HTTPS vers PyPI, puis `No matching distribution found` car l'index n'était pas accessible.

Probable cause: Chaîne de certificats du contexte d'exécution.

Already attempted: Installation du wheel Drain3 présent dans le cache local avec `--no-deps`; installation de cachetools 4.2.1 dans le venv avec hôtes explicitement autorisés.

Current status: RESOLVED — Drain3 0.9.11 importable et opérationnel dans le venv.

Next action: Aucune, sauf recréation future du venv à partir des versions consignées.

## E0010 — Durées phase 3 non attribuables par méthode

Error: `fit_score_time_sec` du premier run de chaque seed incluait la construction mutualisée des scores de toutes les méthodes ; les runs suivants utilisaient le cache.

Command: `run_strict_sequence_experiments.py --resume --dataset hdfs`

Short traceback: Aucun échec ; défaut sémantique détecté lors de l'inspection du résumé.

Probable cause: Optimisation du runner par cache `scores_by_seed` alors que le chronomètre était attaché au run courant.

Already attempted: Champ retiré des CSV et résumés ; les anciens champs JSON HDFS restent traçables mais ne seront pas interprétés. Les nouveaux JSON indiquent explicitement la portée du chronométrage et `comparable_across_methods=false`.

Current status: RESOLVED BY EXCLUSION — aucune métrique prédictive n'est affectée.

Next action: Ne citer aucun temps par méthode pour HDFS/BGL dans le mémoire.

## E0011 — Affichage console de la préparation phase 4

Error: `UnicodeEncodeError` lors du `print(json.dumps(..., ensure_ascii=False))` final.

Command: `rtk python scripts/prepare_model_update_e2e.py`

Short traceback: Le codec console `cp1252` ne peut pas encoder `\ufffd` présent dans une métadonnée de chemin source.

Probable cause: Encodage de la console Windows, pas les fichiers UTF-8 écrits.

Already attempted: Validation directe de `model_update_preparation.json`, du bundle, du CSV d'évaluation et des trois modèles courants ; tous présents, lisibles et hashés. Les candidats sont encore absents. Affichage corrigé avec `ensure_ascii=True` sans relancer la préparation.

Current status: RESOLVED — aucune donnée expérimentale perdue ou corrompue.

Next action: Ne pas relancer la préparation ; exécuter directement la boucle end-to-end sur les artefacts validés.

## E0008 — Conflit de dépendance Drain3 dans l'environnement partagé

Error: `drain3==0.9.11` impose `cachetools==4.2.1`, incompatible avec `streamlit==1.57.0` qui exige `cachetools>=5.5,<8`.

Command: `rtk python -m pip install drain3==0.9.11`

Short traceback: Installation réussie avec avertissement du résolveur pip sur l'incompatibilité Streamlit/cachetools.

Probable cause: Métadonnées de dépendance strictes et anciennes de Drain3 0.9.11.

Already attempted: Drain3 retiré de l'environnement global ; cachetools 7.1.2 restauré ; `pip check` global sans erreur. Venv `.venv-final-experiments` créé avec `--system-site-packages`; Drain3 installé depuis le wheel local et cachetools 4.2.1 installé localement. Import et premier cluster Drain3 réussis.

Current status: RESOLVED WITH ISOLATION — l'environnement global n'est pas dégradé ; le venv dédié exécute Drain3. Le venv n'est pas destiné à exécuter Streamlit.

Next action: Utiliser exclusivement `.venv-final-experiments/Scripts/python.exe` pour la phase 3 et enregistrer versions/configuration dans les artefacts.

## E0009 — Échec SSL pendant l'installation Drain3 dans le venv

Error: `SSLCertVerificationError: unable to get local issuer certificate`.

Command: `rtk .\.venv-final-experiments\Scripts\python.exe -m pip install drain3==0.9.11`

Short traceback: Cinq tentatives HTTPS vers PyPI, puis `No matching distribution found` car l'index n'était pas accessible.

Probable cause: Chaîne de certificats du contexte d'exécution.

Already attempted: Installation du wheel Drain3 présent dans le cache local avec `--no-deps`; installation de cachetools 4.2.1 dans le venv avec hôtes explicitement autorisés.

Current status: RESOLVED — Drain3 0.9.11 importable et opérationnel dans le venv.

Next action: Aucune, sauf recréation future du venv à partir des versions consignées.
