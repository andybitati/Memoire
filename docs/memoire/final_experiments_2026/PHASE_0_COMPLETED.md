# PHASE 0 COMPLETED

Objectif: Initialiser une infrastructure expérimentale isolée, reprenable et traçable ; figer l'environnement et l'identité locale des datasets prioritaires.

Protocole: Relevé du commit Git et de l'environnement Python, inventaire ciblé des sources nécessaires aux phases 1 à 3, calcul SHA-256 par lecture binaire, comptage des observations, extraction des classes CSV, création d'un registre append-only et validation du runner en dry-run.

Runs prévus: Aucun run scientifique en phase 0.

Runs terminés: Aucun run scientifique ; trois contrôles techniques réussis (gel environnement, manifeste, dry-run des 30 runs de phase 1).

Runs échoués: Aucun run scientifique. Un premier passage du manifeste a échoué sur le champ physique CICIDS ` Label`; l'erreur a été corrigée et la passe complète a réussi.

Résultats principaux:

- Commit gelé : `37bccf083f3c8e92a11377cf758cf1e9e183dee9`.
- Checkpoint Git de phase : `4db70f0` (`experiment: freeze final environment`).
- Environnement : Windows `10.0.26200`, Python `3.11.9`, 4 cœurs physiques, 8 processeurs logiques, 8 425 529 344 octets de RAM.
- Versions : scikit-learn `1.7.2`, pandas `2.3.2`, NumPy `2.2.3`, SciPy `1.16.1`.
- Manifeste : 11 fichiers, soit 8 CICIDS2017, 2 HDFS et 1 BGL.
- Tous les fichiers manifestés ont un SHA-256 valide et des dimensions positives.
- L'archive ambiguë historiquement liée au F1 `0,999965` est absente du manifeste final.

Résultat négatif éventuel: Drain3 n'est pas installé dans l'interpréteur actif ; le serveur Redis et le GPU ne sont pas caractérisés. `graphify update .` reste bloqué par `[WinError 5] Accès refusé`.

Artefacts:

- `environment_final_experiments.json`
- `dataset_manifest_final.csv`
- `configs/cicids_final_protocol.json`
- `state/EXPERIMENT_LEDGER.csv`
- `state/ARTIFACT_INDEX.json`
- `scripts/run_final_experiments.py`

Problèmes: Voir `state/ERRORS_AND_BLOCKERS.md`, entrées E0001 à E0004.

Conclusion scientifique: Les fichiers locaux nécessaires aux campagnes prioritaires sont identifiés par hash. Ces hashes prouvent l'identité des copies locales, pas leur provenance officielle, qui reste `INFORMATION À VÉRIFIER.`.

Impact probable sur le mémoire: Les futures valeurs devront référencer le manifeste, le commit, le protocole figé et les artefacts unitaires. Aucune valeur nouvelle n'est encore autorisée comme résultat expérimental.
