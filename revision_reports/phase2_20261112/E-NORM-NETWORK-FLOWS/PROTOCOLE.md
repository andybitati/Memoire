# Protocole préenregistré : E-NORM-NETWORK-FLOWS

Rédigé le 2026-11-12 et versionné **avant** l'exécution.

## 1. Question

La campagne multiformat mesure, pour les flux réseau tabulaires, 0 champ standard rempli
sur 7. Un relecteur et la vérification du code (`scripts/run_multiformat_validation.py:248`)
montrent que la voie des flux ne projetait aucune colonne vers le schéma, alors que
CSE-CIC-IDS2018 contient un horodatage, un port de destination et un protocole. Avec un
adaptateur qui projette les colonnes présentes, quelle part du schéma les flux
remplissent-ils, et qu'est-ce qui manque vraiment dans les données ?

## 2. Dispositif

- Adaptateur : `src/logminer/normalizers/network_flow.py` (`normalize_flows`), testé par
  `tests/test_network_flow_normalizer.py` (4 tests). Projection : port de destination,
  port source, IP source et destination, protocole, octets émis, horodatage (converti en
  ISO, jour en premier) ; `dataset` et `subtype = network_flow` fixés par l'adaptateur,
  comme le font les parseurs des autres formats. L'étiquette n'est jamais projetée.
- Runner : `run_e_norm_network_flows.py` (empreinte au registre).
- Données : tous les CSV locaux, 8 fichiers CICIDS2017 MachineLearningCVE et 2 fichiers
  CSE-CIC-IDS2018 (15 et 16 février) ; 1 000 premières lignes par fichier, comme la
  campagne d'origine. Empreintes inscrites au manifeste.

## 3. Mesures

Par fichier, taux de remplissage de deux ensembles de sept champs :
- **journal** (ceux de la campagne d'origine) : horodatage, source, hôte, famille,
  catégorie, sévérité, message ;
- **réseau** : `timestamp_iso`, `src_ip`, `src_port`, `dst_ip`, `dst_port`, `proto`,
  `bytes_sent`.
Contrôle : aucune valeur de l'étiquette ne doit apparaître dans un champ normalisé.

## 4. Prédiction et règle de décision (fixées avant exécution)

Nombre de champs remplis à 100 %, d'après les en-têtes des fichiers :
- CICIDS2017 : journal 1 (famille), réseau 2 (`dst_port`, `bytes_sent`) ;
- CSE-CIC-IDS2018 : journal 2 (horodatage, famille), réseau 4 (`timestamp_iso`,
  `dst_port`, `proto`, `bytes_sent`).
Si chaque fichier est conforme et sans fuite d'étiquette → `lacune_d_adaptateur_comblee` :
le score nul tenait à l'adaptateur, et les champs restés vides (IP, port source, sévérité,
message) manquent dans les données. Sinon → `a_examiner`, rapporté tel quel.

## 5. Conséquences préfixées

Le manuscrit remplace « aucun champ pour les flux » par les taux mesurés avec l'adaptateur,
distingue ce qui manque dans les données de ce que l'adaptateur ne projetait pas, et conserve
le résultat d'origine comme mesure de la voie antérieure.

## 6. Portée

Mesure de remplissage, non de fidélité sémantique ni de détection. Le champ « famille » est
rempli par construction de l'adaptateur. Aucun incident n'est corrélé entre sources.
