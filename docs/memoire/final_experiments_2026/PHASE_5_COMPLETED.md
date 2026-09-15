# PHASE 5 COMPLETED

Objectif: Évaluer fonctionnellement les formats réellement disponibles sans confondre parsing, normalisation et routage.

Protocole: Huit voies figées, sources hashées, premiers événements sans duplication, maximum 1 000 par format. Les parseurs du pipeline courant sont utilisés pour Windows, syslog, Apache, HDFS et BGL ; les adaptateurs existants sont utilisés pour Linux/auth, Wazuh et flux réseau tabulaires.

Runs prévus: 8.

Runs terminés: 8.

Runs échoués: 0 erreur d'infrastructure ; deux résultats fonctionnels négatifs complets sont conservés.

Résultats principaux:

- 7 001 événements lus, 5 001 parsés/normalisés, 2 000 perdus.
- Windows, Linux/auth, Wazuh, syslog et flux réseau: 1 000/1 000.
- Apache: 1/1 seulement, sur fixture synthétique.
- HDFS et BGL: 0/1 000 chacun bien que `detect_kind` identifie correctement les fichiers.
- Les quatre CSV obligatoires, huit JSON, un tableau et une figure sont valides.
- La reprise idempotente saute les huit expériences terminées.

Résultat négatif éventuel:

- Les parseurs de pipeline HDFS/BGL sont non fonctionnels (`Parser.parse` vide), indépendamment du pipeline strict expérimental de phase 3.
- La conversion temporelle Wazuh produit 0 % de timestamps non vides sur ce préfixe de 1 000 lignes.
- Le schéma commun n'est pas complet pour Linux/auth et les flux réseau.
- La ligne brute complète n'est pas conservée de façon générale : Windows et syslog obtiennent 0 % selon le test exact.

Artefacts:

- `configs/multiformat_validation_protocol.json`.
- `scripts/run_multiformat_validation.py`.
- `data/processed/final_experiments_2026/multiformat_validation_{raw,summary}.csv`.
- `data/processed/final_experiments_2026/multiformat_field_completeness.csv`.
- `data/processed/final_experiments_2026/multiformat_failures.csv`.
- `tables/validation_multiformat.md`.
- `figures/validation_multiformat.png`.

Problèmes:

- Wazuh émet un avertissement d'inférence de format temporel.
- HDFS émet aussi un `SyntaxWarning` dans du code de décompilation incomplet ; aucun parseur n'est corrigé pendant l'expérience figée.
- Apache est trop petit pour soutenir autre chose qu'un test de fonctionnement élémentaire.

Conclusion scientifique: `VALIDATION FONCTIONNELLE MULTIFORMAT PARTIELLE`. Six voies produisent des sorties, mais seules cinq ont 1 000 événements et la complétude de schéma varie. HDFS/BGL échouent complètement dans le pipeline courant. Aucune robustesse universelle et aucune conservation universelle du brut ne sont démontrées.

Impact probable sur le mémoire: Remplacer toute affirmation générale de robustesse multiformat ou de conservation systématique du message original par les résultats par format et leurs limites. Distinguer le pipeline courant HDFS/BGL des lecteurs stricts expérimentaux de phase 3.

