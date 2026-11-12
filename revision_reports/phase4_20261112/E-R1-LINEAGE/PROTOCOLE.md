# Protocole préenregistré — E-R1-LINEAGE

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit du protocole**.

## Question

L'exigence R1 demande que chaque unité des formats retenus soit lue, émise dans le schéma commun **et rattachée à sa source**. Le mémoire établit la lecture et l'émission, mais indique que le rattachement unité par unité n'a pas été mesuré : la campagne multiformat associe la ligne normalisée à l'unité brute par sa position, non par un identifiant. Ce protocole vérifie le rattachement par identifiant, du fichier source au résultat, y compris après reprise. Il répond à une remarque du jury (quatrième retour, 2026-11-12).

## Sondage préalable déclaré

Avant la rédaction, un sondage de 50 unités par source a inspecté **les colonnes** produites par les adaptateurs (non les taux) : les sources passant par le pipeline (Windows EVTX, syslog, Apache, HDFS, BGL) et Wazuh portent `filepath` et `lineno` ou `recno` ; les chemins de préparation de Linux/auth et des flux CICIDS2017 n'en portent aucun ; pour les sources du pipeline, `filepath` désigne l'extrait constitué par la campagne. Un essai technique (20 unités par source, répertoire temporaire) a vérifié l'exécution sans afficher de taux.

## Programmes, données et sources

- Runner : `revision_reports/phase4_20261112/E-R1-LINEAGE/run_e_r1_lineage.py`.
- Réutilisés **sans modification** : adaptateurs de `scripts/run_multiformat_validation.py` ; chaîne multi-source `scripts/run_multisource_cnp_e2e_strengthening.py` (chargement des unités, `real_handler`, `build_agents`) ; `ContractNetCoordinator`, `MultiTaskIntelligentAgent`, `SQLiteIdempotencyStore`.
- Sources et limites : protocole multiformat gelé `experiments/phase_dataset_strengthening/configs/multiformat_balanced_protocol.json` (huit sources, au plus 1 000 unités chacune). Empreintes des fichiers sources inscrites au résumé.

## Partie A — émission dans le schéma commun

Pour chaque source, les lignes normalisées sont produites par l'adaptateur de la campagne multiformat. Une unité est **rattachée** si une ligne normalisée et une seule porte un localisateur (`filepath` non vide et `lineno`, ou `recno` pour EVTX) qui :

1. désigne le fichier d'origine ou l'extrait de la campagne, dont la n-ième ligne est par construction la n-ième unité non vide du fichier d'origine (la cible du localisateur est rapportée séparément) ;
2. tombe dans l'intervalle des unités ;
3. pointe une unité dont le contenu correspond, relu indépendamment dans le fichier d'origine : identifiant d'événement égal (EVTX), message normalisé contenu dans la ligne brute (texte), message égal ou inclus dans `_source.full_log` (Wazuh).

Une source passe la partie A si toutes ses unités sont rattachées et qu'aucune ligne normalisée n'est en excès.

## Partie B — chaîne de bout en bout avec reprise

Toutes les unités (au plus 1 000 par source) deviennent des tâches Contract Net exécutées dans un seul processus par les trois agents de la chaîne multi-source, avec un magasin d'idempotence SQLite partagé. Pour chaque source, l'exécution de la 10e unité (la 1re si la source en compte moins de 10) tombe en panne **après** l'effet et l'enregistrement dans le magasin, **avant** l'émission du résultat ; le coordinateur réattribue la tâche. Les effets sont comptés par clé d'idempotence. Une unité est rattachée si :

1. sa tâche se termine avec un résultat `ok` ;
2. le résultat renvoie la même source et le même indice d'unité que la tâche ;
3. cet indice désigne, dans le fichier d'origine relu indépendamment, une unité dont l'empreinte est égale à celle de l'unité transmise ;
4. l'effet n'a été produit qu'une fois.

Une source passe la partie B si toutes ses unités sont rattachées, y compris l'unité en panne.

## Décision

- `R1_rattachement_verifie` : les huit sources passent A et B.
- `R1_rattachement_partiel` : au moins une source échoue ; les sources en échec et le motif (partie, critère) sont nommés.

## Partie C, descriptive et hors décision

Nombre d'anomalies candidates de la chaîne, présence d'un indice d'unité dans ces lignes, possibilité de les rattacher à une unité par l'identifiant de tâche, et présence d'un identifiant d'unité ou de tâche dans la sortie du corrélateur.

## Conséquences préfixées

- `R1_rattachement_verifie` : R1 passe de « partiellement satisfaite » à « satisfaite » pour les formats retenus.
- `R1_rattachement_partiel` : R1 reste partiellement satisfaite ; le mémoire dit précisément quelles sources et quel niveau (ligne normalisée, résultat) perdent le rattachement. Aucune correction du code n'est faite dans ce protocole ; une correction éventuelle ferait l'objet d'un protocole distinct.

## Portée

Huit sources locales, au plus 1 000 unités chacune ; exécution dans un seul processus ; une panne par source. Le protocole ne vérifie pas le rattachement dans l'exécution répartie Redis, ni à travers la corrélation en incidents (décrite en partie C seulement).

## Commande après commit

```powershell
$env:PYTHONIOENCODING='utf-8'; .venv\Scripts\python.exe revision_reports\phase4_20261112\E-R1-LINEAGE\run_e_r1_lineage.py
```

Artefacts attendus dans `experiments/phase_revision_20261112/E-R1-LINEAGE/` : `summary.json`, `part_b_units.csv`, `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
