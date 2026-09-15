# Audit préalable — renforcement scientifique des datasets

Date de l’audit : 2026-09-09  
État : **PHASE 0 TERMINÉE — AUCUNE NOUVELLE EXPÉRIENCE EXÉCUTÉE**

## 1. Périmètre et règles

Cet audit précède toute modification de code ou nouvelle expérience. Il s’appuie sur les
copies locales, les manifestes, les configurations gelées, les scripts et les artefacts déjà
produits. Le mémoire n’a pas été modifié.

Les nouvelles campagnes doivent conserver séparément les anciens résultats et utiliser des
identifiants de run propres. Une performance élevée n’est pas un critère de réussite : le but
est d’aligner l’unité statistique, la vérité terrain et la portée de l’affirmation.

## 2. Tableau des écarts

| Dataset/source | Évaluation actuelle | Problème scientifique | Nouvelle expérience | Priorité |
| --- | --- | --- | --- | ---: |
| HDFS | Drain3 train-only, fenêtres causales, décision événementielle sur 20 000 événements test ; F1 Histogram `0,269307` | La vérité est attachée au `block_id`, pas à chaque ligne ; l’unité de prédiction n’est pas alignée sur l’unité de vérité | Split sans recouvrement de blocs, scores événementiels puis agrégation maximum/moyenne/proportion, sélection complète sur validation | 1 |
| BGL | Drain3 train-only ; test de 19 908 événements ; F1 Histogram `0,913698` | `89,8081 %` des événements test ne correspondent à aucun template du train ; la nouveauté peut expliquer une part importante du score | Groupes ALL/KNOWN/UNKNOWN et baseline `UnknownTemplateBaseline` | 2 |
| CICIDS2017 | Split aléatoire stratifié et holdout de cinq scénarios | Absence de mesure explicite de généralisation d’un jour antérieur vers un jour ultérieur | Holdout temporel par fichiers/jours, RandomForest et LogisticRegression, cinq graines | 3 |
| Corpus routeur | 81 chunks issus de neuf sources, 80/81 corrects | Les 81 chunks ne sont pas 81 réplications indépendantes ; risque de pseudo-réplication | Une observation principale par fichier/source originale, `source_group`, cas open-set et rejet inconnu | 4 |
| Multiformat | 7 001 unités lues, 5 001 normalisées | Résultat global dominé par les sources réussies ; HDFS et BGL produisent 0/1 000 ; Apache n’a qu’une ligne | Couverture par source, N réel, adaptateurs HDFS/BGL, complétude, pertes et fallback | 5 |
| Multi-source E2E | Pipeline multi-agent 8/8 sur une seule entrée Windows | Les formats et les agents sont encore évalués principalement dans des campagnes séparées | Replay multi-source avec vrais agents CNP, identifiants unitaires et traces d’offres/refus/attribution | 6 |
| Dataset externe | Parquet locaux attribués à UNSW-NB15, identité officielle non démontrée | Validité externe réseau limitée et provenance insuffisante pour une nouvelle preuve indépendante | Optionnel après les six campagnes : un téléchargement officiel, nouveau hash et protocole léger | 7 |

## 3. Inventaire vérifié

### 3.1 HDFS

- Données : `data/raw/Datasets/HDFS_1/HDFS.log`.
- Taille : `1 577 982 906` octets ; `11 175 629` lignes.
- SHA-256 : `0783096174d7832c618337f9609e06e04abd86ddd7089b3c12b407e63bfebc52`.
- Labels : `data/raw/Datasets/HDFS_1/anomaly_label.csv`.
- Taille des labels : `18 637 554` octets ; `575 061` blocs.
- SHA-256 labels : `1c711ed6c8848fc3243fb4d092f172f31d128c8a6ec7f26ebba72ab931885ed8`.
- Provenance : correspondances SHA-256 exactes avec les fichiers extraits de l’archive
  HDFS_v1 Loghub/Zenodo dont le MD5 publié a été vérifié.
- Format : ligne de log brute ; `block_id` extrait du message.
- Granularité de la vérité : bloc/trace.
- Unité actuelle de prédiction : événement.
- Préparation actuelle : 50 000 événements train, 20 000 validation et 20 000 test ; aucun
  chevauchement de bloc observé dans ces trois échantillons.
- Drain3 : version 0.9.11, 13 clusters, apprentissage train uniquement, `match()` uniquement
  sur validation/test ; état SHA-256
  `18bc825effd29a8c4cd957d41d9a4502a2e47f905738dd6b193017056905ebd2`.
- Limite principale : l’ancien résultat reste événementiel malgré les labels au bloc.

### 3.2 BGL

- Données : `data/raw/Datasets/BGL/BGL.log`.
- Taille : `743 185 031` octets ; `4 747 963` lignes.
- SHA-256 : `666130b15ef44eb32fd02bd053e6c6e007c37696b5e7e8b9d8e45b729876a5d2`.
- Provenance : source publique Loghub identifiée ; identité binaire de la copie locale avec
  le fichier public **NON DÉMONTRÉE**.
- Granularité de la vérité et de la prédiction : ligne de log.
- Préparation actuelle : 49 999 événements train, 17 764 validation, 19 908 test.
- Drain3 : version 0.9.11, 7 clusters, train-only, état SHA-256
  `43ef590469a379daf21f7b644b3fc2592ca66e74643353254e60659baf27db82`.
- Taux de templates inconnus : validation `84,3673 %`, test `89,8081 %`.
- Limite principale : le F1 élevé peut refléter principalement la nouveauté structurelle.

### 3.3 CICIDS2017

- Données : huit CSV sous
  `data/raw/Datasets/MachineLearningCSV/MachineLearningCVE/`.
- Format : 79 colonnes, soit 78 variables numériques et `Label` dans le protocole courant.
- Provenance : noms, dimensions, structure et archive locale fortement concordants avec
  CICIDS2017 ; identité binaire avec un téléchargement officiel **NON DÉMONTRÉE**.
- Prétraitement actuel : non-finis vers zéro, écrêtage `[-1e12, 1e12]`, suppression du label ;
  `StandardScaler` dans le pipeline train-only des modèles linéaires.
- Protocoles existants : random stratifié, puis fichier/scénario tenu hors entraînement.
- Résultats conservés : RandomForest random `0,995142` ; holdout macro `0,157744` ;
  LogisticRegression meilleur F1 macro parmi cinq candidats `0,233670`.
- Temporalité disponible : jours encodés par les noms de fichiers, du lundi au vendredi.
- Limite principale : aucune campagne n’entraîne explicitement sur les jours antérieurs pour
  tester sur le vendredi tenu hors entraînement.

### 3.4 Routeur

- Script : `scripts/run_router_evaluation.py`.
- Décision : scores heuristiques explicables dans `src/logminer/agents/model_router.py`.
- Marge : différence entière entre les deux meilleurs scores ; ce n’est pas une probabilité
  calibrée.
- Corpus actuel : neuf sources transformées en 81 fichiers/chunks, généralement dix chunks
  par source.
- Résultat actuel : 80/81, exactitude `0,987654`, F1 macro `0,883598`.
- Unité indépendante honnête : au plus neuf sources dans cette campagne, avec Apache
  synthétique N=1 et plusieurs sources partageant un même environnement.
- Limite principale : les chunks d’une même source ne sont pas indépendants.

### 3.5 Multiformat

- Script : `scripts/run_multiformat_validation.py`.
- Sources : Windows EVTX, Linux/auth, Wazuh, Linux_2k/syslog, Apache, HDFS, BGL et CICIDS.
- Sélection : premiers enregistrements, maximum 1 000, aucune duplication.
- Résultat : `7 001` unités lues, `5 001` parsées/normalisées, `2 000` perdues.
- HDFS : 0/1 000 ; BGL : 0/1 000.
- Cause technique confirmée : `src/logminer/parsers/hdfs.py` et `bgl.py` sont des sources
  décompilées incomplètes dont `Parser.parse()` n’exécute aucun traitement utile.
- Apache : fixture synthétique d’une ligne seulement.
- Limite principale : la somme globale masque la couverture nulle de deux sources.

### 3.6 Replay bout en bout

- Run existant : `e2e-ma_20260909T160812Z_34016`.
- Résultat : huit étapes terminées, une entrée Windows, zéro erreur et zéro fallback.
- Architecture : vrais agents CNP dans le harnais local.
- Limite principale : N=1, une seule famille ; aucune vérité terrain prédictive.

### 3.7 Source réseau externe éventuelle

- Deux Parquet locaux portent les effectifs officiels UNSW-NB15 : 175 341 train et 82 332
  test, avec 36 colonnes.
- Leur transformation et leur identité exacte avec les CSV officiels ne sont pas démontrées.
- L’archive historique `UNSWNB15.zip` contient des fichiers DrDoS/UDPLag/SYN et reste exclue.
- Une campagne externe future exige un nouveau téléchargement officiel, un nouveau SHA-256
  et une provenance séparée. Elle ne peut commencer qu’après les six campagnes prioritaires.

## 4. Artefacts existants à préserver

- `data/processed/final_experiments_2026/phase_3/` : préparation HDFS/BGL et résultats stricts.
- `data/processed/final_experiments_2026/phase_5/` : sorties multiformat historiques.
- `data/processed/final_experiments_2026/phase_6/` : corpus dérivé du routeur.
- `docs/memoire/final_experiments_2026/state/EXPERIMENT_LEDGER.csv` : ledger historique
  append-only.
- `experiments/phase_multi_agent/` : résultats Contract Net à ne pas recalculer.
- `ARIEL_LOGMINER_MEMOIRE_FINAL/evidence/data_traceability/` : décisions de provenance.

## 5. Décisions avant implémentation

1. Les résultats historiques ne seront ni remplacés ni renommés.
2. Les nouvelles sorties seront isolées sous `experiments/phase_dataset_strengthening/`.
3. HDFS sera évalué au bloc à partir de scores événementiels, avec choix de l’agrégateur et
   des seuils sur validation uniquement.
4. BGL utilisera les identifiants de templates issus de Drain3 gelé ; `0` signifie inconnu.
5. CICIDS utilisera les jours/fichiers uniquement pour le split, jamais comme variables.
6. Le routeur rapportera deux niveaux : observations fichier et groupes de provenance.
7. Les adaptateurs HDFS/BGL seront réparés avant la nouvelle campagne multiformat.
8. Le replay multi-source utilisera `ContractNetCoordinator` et les sept champs inchangés de
   `AgentMessage`.
9. Aucun intervalle de confiance ne sera produit pour N=1.
10. Le dataset réseau externe reste optionnel et subordonné à la clôture des six campagnes.

## 6. Statut de sortie de phase

Audit préalable : **TERMINÉ**.  
Mémoire modifié : **NON**.  
Nouvelles expériences exécutées : **NON**.  
Prochaine étape autorisée : conception et gel des protocoles, puis implémentation et tests.
