# Préparation de la soutenance — campagnes assistées par IA

Document hors manuscrit, établi selon la décision C4(d). Il sert à préparer une réponse
précise sur la part de l'auteur, la part automatisée et la maîtrise des protocoles. Il ne
doit pas être copié dans le mémoire sous forme d'historique des campagnes.

## 1. Position générale à tenir

La réponse la plus solide est factuelle : des agents d'IA ont proposé ou adapté des
protocoles complémentaires, écrit des scripts, exécuté les campagnes dans l'environnement
de l'auteur, agrégé les sorties et préparé des corrections. L'auteur a autorisé ces travaux,
a arrêté le contenu final et demeure responsable des résultats présentés. Cette validation
finale ne dispense pas de démontrer en soutenance la compréhension de chaque protocole.

Ne pas revendiquer un préenregistrement pour les campagnes ci-dessous. Les identifiants et
artefacts montrent des exécutions du 4 novembre 2026, tandis que le PDF examiné a été
compilé le 5 novembre 2026. Aucun document versionné antérieur aux exécutions, fixant les
comparateurs, métriques et critères de décision, n'a été retrouvé. Certains scripts ont
écrit un fichier de paramètres avant leur propre phase d'évaluation ; cela améliore la
traçabilité interne, mais ne constitue pas un préenregistrement indépendant du protocole.

## 2. Inventaire campagne par campagne

### 2.1 HDFS principal sur le test complet

- **Identifiants :** `agent2_hdfs_full_20261104T131314Z` et réplication
  `agent2_hdfs_full_20261104T134240Z` ; IC bloc
  `agent2_hdfs_full_20261104T131314Z__test_block_ci`.
- **Preuves :** `experiments/phase_revision_20261104/agent_2_hdfs/` ; script
  `revision_reports/agent_2/run_hdfs_full_test_multiseed.py` ; calcul des IC
  `revision_reports/agent_2/hdfs_full_confidence_intervals.py`.
- **Éléments préexistants attribuables au travail de l'auteur :** corpus et labels HDFS,
  pipeline Drain3/Histogram, partition par première apparition et artefact de partition
  `ds_hdfs_block_20260910T081756Z` présents dans le dépôt.
- **Part automatisée :** extension de l'évaluation aux partitions complètes, exécution des
  cinq graines, réplication, calcul des intervalles et rédaction de l'interprétation.
- **Résultat à connaître :** 115 013 blocs de test, 1 679 positifs ; TP 1 679, FP 509,
  FN 0 ; F1 0,868373, IC bootstrap [0,856771 ; 0,879493]. Les cinq graines produisent la
  même matrice de confusion ; les états Drain3 ont la même empreinte entre les deux
  exécutions.
- **Questions probables du jury :** pourquoi seulement 6 000 blocs pour ajuster Drain3 ?
  pourquoi la variance entre graines est-elle nulle ? pourquoi l'IC porte-t-il sur les
  blocs et non sur les graines ? pourquoi 0,892308 n'est-il pas le résultat principal ?
- **Démonstration de maîtrise attendue :** expliquer la partition 60/20/20, le gel du
  parseur, le choix de l'agrégateur et du seuil sur validation, puis distinguer test complet
  et échantillon distribué de 2 000 blocs.

### 2.2 BGL

- **Identifiants principaux :** `agent4_bgl_second_protocol_20261104T142629Z`,
  `agent4_bgl_contiguous_horizon_20261104T145740Z`,
  `agent4_bgl_known_template_diag_20261104T143926Z`,
  `agent4_bgl_anomaly_family_map_20261104T144946Z` et contrôle Drain3
  `agent4_bgl_drain_match_check_20261104T145500Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_4_bgl/` pour le protocole R0
  et ses variantes B--E ; artefacts complémentaires sous
  `revision_reports/agent_4/artifacts/bgl/` ; scripts sous
  `revision_reports/agent_4/scripts/`.
- **Éléments préexistants attribuables au travail de l'auteur :** corpus BGL, parseur,
  détecteur Histogram et protocole publié `ds_bgl_known_unknown_20260910T082706Z`.
- **Part automatisée :** reproduction du protocole, exploration de variantes temporelles,
  diagnostic des templates connus et cartographie des familles d'anomalies.
- **Résultat à connaître :** l'unité est l'événement, non une fenêtre. Dans le protocole
  principal, le seuil vaut `ln(49 999)` et la décision coïncide exactement avec la règle
  « sévérité absente de l'entraînement normal » : F1 0,913698, TP 2 885, FP 545, FN 0.
  Le protocole contigu G atteint 0,941927, mais a été conçu après exploration des résultats
  et doit rester exploratoire.
- **Questions probables :** qu'apprend Histogram ? pourquoi la règle de sévérité donne-t-elle
  la même décision ? en quoi le protocole G est-il post hoc ? pourquoi la couverture des
  templates dépend-elle autant de la proximité temporelle ?
- **Démonstration attendue :** dériver le score Histogram, expliquer le compte plancher pour
  une valeur inconnue et reconnaître que le résultat principal ne prouve pas une détection
  comportementale profonde.

### 2.3 Audit CSE-CIC-IDS2018

- **Identifiant :** `agent4_csecic_shortcut_20261104T144738Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_4_csecic/` ; script
  `revision_reports/agent_4/scripts/csecic_shortcut_audit.py`.
- **Éléments préexistants attribuables au travail de l'auteur :** deux fichiers locaux des
  15 et 16 février, pipeline LR/RF et résultats inter-journées déjà présents.
- **Part automatisée :** audit d'intégrité, ablations, règle `Dst Port < 1024`, sens inverse
  et calculs à prévalence observée.
- **Résultat à connaître :** `Dst Port < 1024` seul atteint F1 0,999720 dans le sens publié.
  Le transfert inverse donne environ 0,234 pour la régression logistique et 0,40 pour le
  Random Forest. Les fichiers locaux totalisent chacun 2^20−1 lignes sous l'en-tête ; le
  second contient un en-tête répété, ce qui rend la troncature probable mais non démontrée.
- **Questions probables :** pourquoi deux journées seulement ? comment distinguer artefact
  de collecte et signal d'attaque ? les fichiers sont-ils intègres ?
- **Démonstration attendue :** présenter cette section comme un audit de fragilité du jeu
  et non comme une validation générale d'un détecteur d'intrusions.

### 2.4 Routeur open-set étendu

- **Identifiant :** `agent5_router_open_set_20261104T145601Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_5_router_open_set/` ; script
  `revision_reports/agent_5/scripts/agent5_router_open_set_extended.py`.
- **Éléments préexistants attribuables au travail de l'auteur :** routeur, adaptateurs,
  politique gelée et 31 sources de calibration du run de référence.
- **Part automatisée :** inventaire de 37 fichiers supplémentaires, configuration des
  catégories connues/inconnues, rejeu, IC de Clopper--Pearson et diagnostic des colonnes
  ajoutées par les adaptateurs.
- **Résultat à connaître :** 20/20 inconnus rejetés et 3/46 connus rejetés à tort en mode
  pipeline. Les fichiers partageant un schéma ne sont pas indépendants ; deux paires parmi
  les 28 entrées connues initiales sont des doublons binaires. Sans `dataset`, `subtype` et
  `filepath`, le taux de faux rejet passe à 5/46.
- **Questions probables :** le seuil a-t-il été recalibré ? pourquoi des sources connues
  sont-elles rejetées ? le routeur reconnaît-il vraiment la structure brute ?
- **Démonstration attendue :** expliquer la politique gelée, le rôle du fallback et la
  différence entre rejet de sources inconnues et bonne orientation des sources acceptées.

### 2.5 Panne appariée et H2

- **Identifiant :** `agent3_paired_failure_abcd_20261104T141803Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_3_distribution/` ; script
  `revision_reports/agent_3/run_paired_failure_abcd.py`.
- **Éléments préexistants attribuables au travail de l'auteur :** architectures A--D,
  coordinateur Contract Net et magasins d'idempotence du prototype.
- **Part automatisée :** construction de la charge appariée, injection de panne et exécution
  des six bras A, B, C, D, A+I et B+I.
- **Résultat à connaître :** sur dix répétitions, A et B dupliquent chacun l'effet dix fois ;
  C et D zéro fois. Les ablations A+I et B+I ont aussi zéro doublon. La campagne est en
  processus local, pas sur Redis ni sur machines virtuelles.
- **Questions probables :** que teste réellement H2 ? le gain vient-il du Contract Net ?
  la latence de détection de panne est-elle incluse ?
- **Démonstration attendue :** reconnaître que le résultat établit l'effet du magasin
  d'idempotence, transposable aux architectures A et B, et non un avantage spécifique de
  la négociation multi-agent.

### 2.6 Saturation multi-VM

- **Identifiant :** `agent3_saturation_multivm_20261104T142325Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_3_distribution/` ; script
  `revision_reports/agent_3/run_saturation_multivm.py`.
- **Éléments préexistants attribuables au travail de l'auteur :** topologie Redis/VM,
  agents Debian et Ubuntu, scores HDFS figés.
- **Part automatisée :** producteur en boucle ouverte, 32 coordinateurs concurrents,
  paliers de charge et agrégation des latences.
- **Résultat à connaître :** coude entre 8 et 16 tâches/s ; plafond observé entre 8,4 et
  15,0 tâches/s ; 3 échecs sur 11 430 tâches soumises. La seconde VM ne relève pas la
  capacité observée. Le plan exécuté comporte trois répétitions et des paliers 1--64
  tâches/s, différents du fichier `PROTOCOL_CONFIG.json`.
- **Questions probables :** pourquoi l'écart au plan ? où se situe le goulot ? pourquoi
  l'endurance à 0,5 tâche/s ne prouve-t-elle pas la capacité ?
- **Démonstration attendue :** distinguer charge offerte et débit soutenu, expliquer la
  mesure de latence depuis l'instant planifié et dire que le goulot n'est pas isolé.

### 2.7 Détection HDFS distribuée

- **Identifiant :** `hdfs_multivm_cnp_20261104T135345Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_3_distribution/` ; scripts
  `revision_reports/agent_3/run_hdfs_multivm.py`, `hdfs_redis_agent.py` et
  `start_hdfs_agents.ps1`.
- **Éléments préexistants attribuables au travail de l'auteur :** scores de 2 000 blocs du
  protocole HDFS, coordinateur Redis et agents des deux VM.
- **Part automatisée :** orchestration des VM, envoi des tâches, contrôle d'équivalence et
  agrégation des métriques.
- **Résultat à connaître :** 2 000/2 000 tâches terminées ; F1 0,892308 identique au calcul
  centralisé ; Debian 2 000, Ubuntu 0. Les VM reçoivent des scores déjà calculés et appliquent
  le seuil ; elles ne rejouent ni Drain3 ni Histogram. Les utilités sont égales à 0,845 et
  le départage lexicographique favorise Debian.
- **Questions probables :** qu'est-ce qui est réellement distribué ? pourquoi Ubuntu ne
  reçoit-elle rien ? cette campagne établit-elle un équilibrage ?
- **Démonstration attendue :** limiter la conclusion à l'intégrité du passage par la chaîne
  de décision distribuée.

### 2.8 Isolation Forest de contrôle

- **Identifiants :** `agent6_cicids_iforest_20261104T141904Z` et agrégation en lecture
  seule `agent6_strict_e3_aggregate_20261104T143019Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_6_iforest_baselines/` ; scripts
  `revision_reports/agent_6/scripts/run_cicids_isolation_forest_temporal.py` et
  `aggregate_strict_e3_unsupervised.py`.
- **Éléments préexistants attribuables au travail de l'auteur :** pools temporels figés,
  résultats LR/RF et runs stricts HDFS/BGL.
- **Part automatisée :** entraînement Isolation Forest sur le bénin, comparaison de deux
  règles de seuil, agrégation et comparaison aux baselines.
- **Résultat à connaître :** F1 moyen 0,115719 avec seuil quantile 99 % du bénin et
  0,521436 avec seuil maximisant le F1 de validation ; les deux restent sous la règle
  « tout attaque » à 0,666667 sur le test équilibré. La seconde calibration utilise des
  labels d'attaque et est donc semi-supervisée.
- **Questions probables :** pourquoi PR-AUC et F1 racontent-ils des histoires différentes ?
  quelle règle est réellement non supervisée ?
- **Démonstration attendue :** distinguer apprentissage du score, calibration du seuil et
  unité d'analyse.

### 2.9 Corrélation étendue

- **Identifiants :** `agent5_correlation_20261104T141916Z` et sensibilité descriptive
  `agent5_correlation_gapsens_20261104T143159Z`.
- **Preuves :** `experiments/phase_revision_20261104/agent_5_correlation/` et
  `agent_5_correlation_gapsens/` ; scripts sous `revision_reports/agent_5/scripts/`.
- **Éléments préexistants attribuables au travail de l'auteur :** corrélateur
  `correlate_anomalies`, fenêtre de 15 minutes, sept clés et petit corpus initial.
- **Part automatisée :** générateur synthétique à 20 graines, scénarios à clés stables et
  multi-étapes, baselines fenêtre seule et hôte+fenêtre, bootstrap et analyse de sensibilité.
- **Résultat à connaître :** sur S1, précision 0,9884 et rappel 0,5973 pour les sept clés.
  Sur S2, la baseline hôte+fenêtre atteint F1 0,7268 contre 0,6496 pour le corrélateur,
  meilleure sur 20/20 graines. Le corpus est synthétique et construit en circuit fermé.
- **Questions probables :** pourquoi la règle complète perd-elle du rappel ? les paires
  sont-elles indépendantes ? une vérité terrain réelle existe-t-elle ?
- **Démonstration attendue :** expliquer la fragmentation par fenêtre et catégorie, le choix
  d'un bootstrap sur les graines et l'absence de validation externe.

## 3. Vérifications pratiques avant la soutenance

1. Recalculer au moins une métrique de chaque campagne à partir du CSV/JSON correspondant,
   sans se limiter au tableau du mémoire.
2. Savoir localiser le script, l'entrée, les paramètres, la sortie et la ligne de la matrice
   de preuves pour chacun des neuf groupes ci-dessus.
3. Vérifier le manifeste avec SHA-256 et être capable d'expliquer ce qu'une empreinte prouve
   et ne prouve pas.
4. Préparer une démonstration courte des trois cas les plus sensibles : HDFS complet, règle
   de sévérité BGL et panne appariée avec ablations A+I/B+I.
5. Ne pas confondre « exécuté dans l'environnement de l'auteur », « vérifié par l'auteur »
   et « reproduit indépendamment par un tiers ».
6. Si le dépôt public n'est pas archivé avec une URL ou un DOI stable, le dire et remettre
   au jury un paquet versionné contenant scripts, artefacts, manifeste et instructions.

## 4. Formulation courte recommandée

> J'ai utilisé des assistants d'IA pour auditer le dépôt, proposer et exécuter des campagnes
> complémentaires et préparer des corrections. Les scripts et sorties sont conservés avec
> des identifiants et des empreintes. Je ne présente pas ces campagnes comme préenregistrées
> et aucune reproduction indépendante complète n'est revendiquée. Je reste responsable des
> résultats retenus et je peux expliquer, localiser et recalculer chaque preuve citée.

## Campagnes préenregistrées du chantier (ajout de la reprise)

| Campagne | Part automatisée | À vérifier par l'auteur avant la soutenance |
|---|---|---|
| E-H3b, E-H4 | Protocoles, runners et exécution : Copilot SDK. Rejeu de contrôle : Claude Code | Savoir expliquer le split aléatoire d'E-H3b et les deux tentatives techniques d'E-H4 |
| E-H5, E-CNP | Protocoles, runner, exécution et analyse : Claude Code | Relancer au moins un scénario ; savoir expliquer pourquoi H5 change de statut et pourquoi l'avantage de Contract Net n'isole pas la négociation |
| E-CNP-LEAST-LOADED, E-H3B-STRICT-HOLDOUT | Protocoles, runners, exécution et analyse : Claude Code | Savoir expliquer pourquoi E-H3b n'est plus retenue (fuite UNSW, CICIDS réduit aux DDoS), et assumer que la négociation n'apporte aucun avantage établi dans un seul processus |
