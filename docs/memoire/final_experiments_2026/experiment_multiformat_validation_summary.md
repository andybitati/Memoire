# EXPERIMENT MULTIFORMAT VALIDATION — SUMMARY

Objectif: Remplacer le smoke test historique de quelques lignes par une validation fonctionnelle mesurée des voies de parsing ou de préparation réellement présentes dans le dépôt.

Protocole: Configuration figée dans `configs/multiformat_validation_protocol.json` avant exécution. Pour chaque source, le runner vérifie le SHA-256, prend les premiers événements en ordre source, sans duplication, avec une limite de 1 000, puis utilise la voie de code existante. Apache utilise tout le fixture disponible, soit une seule ligne synthétique existante. Le routage réel est exclu et réservé à la phase 6.

Nombre de runs prévus: 8 formats/adaptateurs.

Nombre terminé: 8/8.

Nombre échoué par l'infrastructure: 0.

## Comptabilité globale

- `N_brut = N_lu = 7 001`.
- `N_parse = N_normalise = 5 001`.
- `N_erreur = N_perdu = 2 000`.
- Invariant vérifié pour chaque format : `N_brut = N_normalise + N_perdu`.
- Huit JSON par format, 7 001 lignes de détail, 56 mesures de complétude et 2 000 échecs sont lisibles.
- Une seconde exécution `--resume` a retourné huit fois `SKIPPED_ALREADY_COMPLETED`.

## Résultats par format

| Format | N brut | N parsé | N normalisé | Erreurs | Perdus | Taux |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Windows Event | 1 000 | 1 000 | 1 000 | 0 | 0 | 1,000 |
| Linux/auth tabulaire | 1 000 | 1 000 | 1 000 | 0 | 0 | 1,000 |
| Wazuh/Elastic CSV | 1 000 | 1 000 | 1 000 | 0 | 0 | 1,000 |
| Syslog Linux | 1 000 | 1 000 | 1 000 | 0 | 0 | 1,000 |
| Apache access | 1 | 1 | 1 | 0 | 0 | 1,000 |
| HDFS | 1 000 | 0 | 0 | 1 000 | 1 000 | 0,000 |
| BGL | 1 000 | 0 | 0 | 1 000 | 1 000 | 0,000 |
| Flux réseau tabulaires | 1 000 | 1 000 | 1 000 | 0 | 0 | 1,000 |

## Détection de type

- Les cinq voies passant par `detect_kind` correspondent toutes au type attendu : Windows=`win_event`, syslog=`syslog`, Apache=`apache`, HDFS=`hdfs`, BGL=`bgl`.
- Cette concordance sur cinq fichiers ne mesure pas l'exactitude du routeur de modèles réel.
- Linux/auth, Wazuh et flux réseau utilisent des adaptateurs tabulaires dédiés ; la détection de fichier est non applicable.

## Résultats négatifs et complétude

- HDFS et BGL sont correctement identifiés mais produisent zéro événement, car les méthodes `Parser.parse` actuelles dans `src/logminer/parsers/hdfs.py` et `bgl.py` sont des stubs `pass` issus de la récupération incomplète. Les parseurs stricts expérimentaux de phase 3 ne remplacent pas ce code de pipeline.
- Wazuh normalise 1 000 lignes, mais la complétude `timestamp` vaut 0 : le format local `Oct 20, 2023 @ ...` n'est pas reconnu par l'appel générique `pd.to_datetime` pendant ce run. `source=99,9 %`, `message=94,3 %`, et `host/family/category/severity=100 %`.
- Windows: timestamp/source/host/family/category à 100 %, severity à 99,9 % et message à 97,9 %.
- Syslog: les sept champs mesurés sont présents à 100 %.
- Linux/auth tabulaire: timestamp/source/host/message à 100 %, mais family/category/severity ne sont pas produits par la voie de préparation ML.
- Flux réseau tabulaires: la préparation de 78 caractéristiques et du label réussit, mais aucun des sept champs d'événement communs n'est produit ; leur complétude est 0 %.
- Apache: tous les champs sauf host sont présents, mais `N=1` rend ce résultat uniquement fonctionnel.
- HDFS/BGL: la complétude n'est pas calculable en l'absence de ligne normalisée.

## Conservation du message original

- Linux/auth: 1 000/1 000 valeurs `comment` testables sont conservées à l'identique.
- Wazuh: 1 000/1 000 valeurs `_source.full_log` testables sont conservées à l'identique ; certaines sont blanches après trim, ce qui explique une complétude `message` de 94,3 %.
- Apache: 1/1 ligne brute est conservée dans `message`.
- Windows: 0/1 000 événements XML complets sont conservés tels quels ; `message` est une reconstruction depuis EventData/UserData/RenderingInfo.
- Syslog: 0/1 000 lignes complètes sont conservées telles quelles ; `message` ne contient que le corps extrait.
- HDFS/BGL: 0/1 000, faute de sortie.
- Flux réseau tabulaires: propriété non applicable, aucune colonne de message brut.

Conclusion scientifique: La phase 5 démontre une validation fonctionnelle locale de six voies de préparation, avec volumes substantiels pour cinq d'entre elles, mais révèle deux échecs complets du pipeline courant (HDFS/BGL) et plusieurs lacunes de schéma. Elle ne démontre ni robustesse universelle, ni conservation générale de la ligne originale, ni qualité du routeur réel.

Limites:

- Un seul fichier et un seul préfixe de source par format ; absence de variété intra-format.
- Les premiers 1 000 événements ne constituent pas un échantillon aléatoire.
- Apache repose sur un fixture synthétique d'une seule ligne.
- Les adaptateurs tabulaires et le pipeline texte ne produisent pas exactement le même schéma intermédiaire.
- L'identité locale est vérifiée par hash, mais la provenance officielle des datasets reste `INFORMATION À VÉRIFIER.`.

Artefacts:

- `configs/multiformat_validation_protocol.json`.
- `data/processed/final_experiments_2026/phase_5/e5_multiformat_*.json`.
- `data/processed/final_experiments_2026/multiformat_validation_raw.csv`.
- `data/processed/final_experiments_2026/multiformat_validation_summary.csv`.
- `data/processed/final_experiments_2026/multiformat_field_completeness.csv`.
- `data/processed/final_experiments_2026/multiformat_failures.csv`.
- `tables/validation_multiformat.md`.
- `figures/validation_multiformat.png`.

