# Fermeture des incertitudes factuelles P0

Périmètre : vérification directe du dépôt, du mémoire LaTeX et des artefacts présents au 7 septembre 2026. Aucune section du mémoire n'a été réécrite et aucune donnée expérimentale n'a été créée.

## 1. Campagnes multi-VM

### FAIT VÉRIFIÉ

Trois campagnes multi-VM achevées disposent d'un artefact final identifiable : une campagne équilibrée, une campagne de panne/reprise et une campagne d'endurance ciblée à une heure. Le script générique `run_vbox_redis_validation.ps1` décrit un protocole de prévalidation, mais aucun résultat final distinct ne prouve qu'une quatrième campagne issue de ce script ait été menée à terme.

La campagne d'une heure est celle à retenir comme preuve principale de fonctionnement multi-VM en laboratoire. La campagne de panne/reprise est une preuve complémentaire du mécanisme de récupération. La campagne équilibrée est un contrôle fonctionnel court.

### PREUVE

- Les trois JSON ont des `run_id` distincts et des streams Redis isolés.
- La campagne équilibrée attribue des tâches terminées aux deux identités de workers, Debian et Ubuntu.
- La campagne de reprise relie une tâche récupérée à une panne simulée avant acquittement.
- La campagne d'une heure conserve les compteurs du groupe Redis : 525 entrées, 525 entrées lues, lag final nul et pending final nul.
- Pour cette dernière campagne, les événements de fin conservés dans la fenêtre Redis ne couvrent pas tout le run : 285 événements de complétion, correspondant à 276 tâches uniques, restent visibles. Ils ne suffisent pas à prouver 525 exécutions réussies ; ils prouvent seulement qu'aucun échec n'est visible dans la fenêtre conservée. Les 525 tâches sont prouvées comme lues et acquittées par le groupe, pas comme 525 succès applicatifs individuellement tracés.

### FICHIER/SCRIPT/ARTEFACT

- `scripts/run_vbox_redis_balanced_campaign.ps1`
- `scripts/run_vbox_redis_recovery_campaign.ps1`
- `scripts/run_vbox_redis_1h_campaign.ps1`
- `scripts/summarize_vbox_redis_1h_campaign.py`
- `scripts/run_vbox_redis_validation.ps1`
- `docs/architecture/redis_vm_distributed_protocol.md`
- `docker-compose.redis.yml`
- `data/processed/vbox_redis_balanced_campaign.json`
- `data/processed/vbox_redis_recovery_campaign.json`
- `data/processed/vbox_redis_1h_campaign.json`
- copies de preuve dans `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/`
- tableaux `docs/memoire/tables/table_vbox_redis_*_campaign.md`

### VALEUR OU CONFIGURATION

Configuration commune vérifiée :

- hôte : machine Windows exécutant PowerShell, VirtualBox et Docker ;
- invités : VM nommées `Debian` et `Ubuntu`, en NAT VirtualBox ;
- accès Redis depuis les invités : `redis://10.0.2.2:6379/0` ;
- accès Redis depuis l'hôte : `redis://localhost:6379/0` ;
- Redis : conteneur `logminer-redis`, image `redis:7-alpine`, port `6379`, AOF activé, `appendfsync everysec`, mémoire maximale 512 MB et politique `noeviction` ;
- groupe : `logminer-intelligent-agents` ;
- parallélisme dans chaque worker multi-VM : `--max-parallel-tasks 1`.

Version exacte de Windows et versions exactes des distributions Debian et Ubuntu :

INFORMATION À VÉRIFIER.

| Campagne | Run et durée | Tâches | Workers réellement visibles | Résultat vérifié |
| --- | --- | ---: | --- | --- |
| Équilibrée | `redis-vbox-balanced-20260722145314`; durée observée non enregistrée | 12, soit 4 `discover.logs`, 4 `parse.logs`, 4 `route.model` | `debian-worker-1` : 8; `ubuntu-worker-1` : 4 | 12 terminées, 12 uniques, 0 échec, 0 pending |
| Panne/reprise | `redis-vbox-recovery-20260722150924`; durée observée non enregistrée | 3, soit une tâche de chaque type | `debian-crash-worker` prend une tâche puis s'arrête avant ACK; `ubuntu-recovery-worker` termine les 3 | 1 panne simulée, 1 tâche prise avant panne, 1 récupérée, 3 terminées, 0 échec, 0 pending |
| Endurance multi-VM | `redis-vbox-1h-20260722153650`; cible 3 600 s, drain prévu 120 s; durée réelle finale non conservée | 175 itérations × 3 tâches = 525 | `debian-worker-1h` : 128 événements visibles; `ubuntu-worker-1h` : 116; relances `debian-worker-1h-r2` : 19 et `ubuntu-worker-1h-r2` : 22 | 525 entrées lues et acquittées par le groupe; lag 0; pending 0; 285 complétions/276 tâches uniques encore visibles; 0 échec visible dans cette fenêtre |

Durée réellement observée des campagnes équilibrée et panne/reprise, ainsi que durée réelle de bout en bout de la campagne ciblée à une heure :

INFORMATION À VÉRIFIER.

Protocole exact transmissible pour le chapitre 5, sous forme de paramètres expérimentaux :

1. Lancer Redis sur l'hôte Windows avec `docker-compose.redis.yml` et vérifier `PING`.
2. Vérifier que les VM `Debian` et `Ubuntu` sont actives, avec Guest Additions au niveau requis par `guestcontrol`, et qu'elles accèdent au même Redis par `10.0.2.2:6379` en NAT.
3. Isoler le run avec `run_id=redis-vbox-1h-20260722153650`, `task_stream=logminer:agent_tasks:vbox_1h:20260722153650` et le groupe `logminer-intelligent-agents`.
4. Démarrer un worker par VM avec une durée configurée de `DurationSec + DrainSec = 3 720 s`, `block-ms=1000`, `claim-idle-ms=1000` et un parallélisme de 1.
5. Pendant une fenêtre cible de 3 600 s, enfiler toutes les 15 s un lot de trois tâches (`discover.logs`, `parse.logs`, `route.model`) depuis l'hôte Windows. Le run observé a produit 175 lots, soit 525 entrées.
6. Prévoir un drain final de 120 s. Des relances supervisées ont été nécessaires après des interruptions de `guestcontrol`; les identités suffixées `-r2` doivent être mentionnées.
7. Vérifier avec `XINFO GROUPS`, `XLEN` et `XPENDING` le nombre d'entrées lues, le lag et les pending. Conserver séparément les événements `agent.task.completed` et `agent.task.failed`, car la fenêtre d'événements peut être tronquée.
8. Rapporter strictement : 525 entrées enfilées, lues et acquittées par le groupe; lag final 0; pending final 0; pas « 525 succès applicatifs ».

Cohérence documentaire :

- résumé français et abstract (`main.tex:218`, `main.tex:252`) : cohérents avec l'artefact, car ils parlent de 525 entrées lues, lag nul et pending nul ;
- chapitre 5 : incohérent par omission, car il ne présente que la campagne locale Redis de six heures et désigne encore celle-ci comme principale validation distribuée locale ;
- chapitre 8, fichier source `chapitre7_reproductibilite_deploiement.tex:235-241` : exact pour la campagne locale de six heures, mais devenu incomplet/contradictoire pour l'état final du projet, puisqu'il présente les VM uniquement comme préparation future ;
- annexes (`annexes.tex:208`) : formulation générique compatible avec les preuves, mais sans protocole, run_id ni artefacts ;
- conclusion (`chapitre6_conclusion.tex:71`) et tableau des menaces (`chapitre6_approfondissements_scientifiques.tex:159-160`) : doivent distinguer la validation multi-VM de laboratoire déjà exécutée de la validation physique, sécurisée ou industrielle qui reste future.

### STATUT

EXÉCUTÉ — RETENABLE COMME PREUVE MULTI-VM DE LABORATOIRE, AVEC LIMITES.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Une campagne supervisée d'une heure cible a utilisé deux VM VirtualBox, Debian et Ubuntu, connectées à un Redis unique sur l'hôte Windows. Le groupe Redis a lu et acquitté 525 entrées, avec lag et pending finaux nuls. Des relances supervisées ont été nécessaires. Une campagne distincte a observé la reprise d'une tâche prise par Debian avant panne et terminée ensuite par Ubuntu.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- que les 525 tâches ont toutes produit un succès applicatif individuellement conservé ;
- que la durée réelle était exactement 3 600 secondes ;
- que les campagnes démontrent de la scalabilité, de la haute disponibilité ou un déploiement SOC industriel ;
- qu'elles couvrent les partitions réseau, la sécurité du bus, la réplication Redis ou des pannes multiples ;
- les versions exactes des trois systèmes d'exploitation sans nouvelle preuve.

### ACTION À TRANSMETTRE À LUNA

Insérer au chapitre 5 la campagne d'une heure comme preuve principale multi-VM de laboratoire, puis la campagne panne/reprise comme contrôle complémentaire. Ajouter les paramètres ci-dessus et les trois JSON aux annexes. Aligner le chapitre 8 et la conclusion sur cette chronologie. Conserver le vocabulaire « lues et acquittées » pour 525, et non « toutes terminées avec succès ».

## 2. Score 0,999965

### FAIT VÉRIFIÉ

La valeur exacte `0.999965` est produite par `data/random_forest_unsw_80_20_metrics.csv` et répétée dans `data/random_forest_unsw_80_20_resume.txt`. Le script correspondant est `kaggle_unsw_random_forest_80_20.txt`.

Le dataset réellement lu n'est pas l'UNSW-NB15 officiel : le script attend dix fichiers nommés `DrDoS_*`, `UDPLag_data_2_0_per.csv` et `syn_data.csv`. L'archive du dépôt s'appelle `UNSWNB15.zip`, mais son contenu correspond à un sous-ensemble dérivé/échantillonné de fichiers au format CIC-DDoS2019. Les fichiers UNSW-NB15 au format Parquet présents ailleurs dans le dépôt ne sont jamais lus par ce script.

La provenance officielle de l'archive, son URL source, sa licence, son checksum d'origine et la transformation ayant créé les suffixes `_1_per`, `_2_0_per`, `_1_3_per` ou `_5_per` ne sont pas documentés.

INFORMATION À VÉRIFIER.

### PREUVE

- `UNSWNB15.zip` contient exactement dix membres : `DrDoS_DNS`, `DrDoS_LDAP`, `DrDoS_MSSQL`, `DrDoS_NTP`, `DrDoS_NetBIOS`, `DrDoS_SNMP`, `DrDoS_SSDP`, `DrDoS_UDP`, `UDPLag` et `syn`.
- Le script fixe explicitement cette liste aux lignes 61-72 et construit le label avec `Label != BENIGN`.
- Les Parquet `UNSW_NB15_training-set.parquet` et `UNSW_NB15_testing-set.parquet` ne figurent pas dans le protocole ayant produit `0.999965`.
- L'artefact modèle confirme 82 caractéristiques et les paramètres du RandomForest.

### FICHIER/SCRIPT/ARTEFACT

- `data/random_forest_unsw_80_20_metrics.csv`
- `data/random_forest_unsw_80_20_resume.txt`
- `kaggle_unsw_random_forest_80_20.txt`
- `data/raw/Datasets/UNSWNB15.zip`
- `data/raw/Datasets/UNSWNB15/`
- `models/random_forest_network_unsw_80_20_sampled.joblib`
- `docs/model_training/random_forest_unsw_80_20_analysis.md`
- copie du CSV dans `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/`

### VALEUR OU CONFIGURATION

- split : masque pseudo-aléatoire par ligne dans chaque chunk, probabilité train 0,80, générateur NumPy graine 42 ; ce n'est ni un holdout temporel ni un holdout par fichier/famille ;
- apprentissage : sous-échantillon du train visant 50 000 normales et 50 000 attaques, mais artefact réel de 75 182 lignes, soit 25 182 normales et 50 000 attaques ;
- test : 1 474 193 lignes ; vérité terrain calculable depuis la matrice de confusion : 1 473 023 attaques et 1 170 lignes bénignes ;
- modèle : `RandomForestClassifier`, 50 arbres, profondeur maximale 15, `min_samples_leaf=2`, `max_features=sqrt`, `class_weight=balanced`, graine 42, `n_jobs=2` ;
- caractéristiques : 82 variables numériques de flux CICFlowMeter ; suppression de `Label`, `label`, `Flow ID`, IP source/destination, `Timestamp`, `Unnamed: 0` et `dataset` ;
- métriques : précision 0,999999, rappel 0,999932, F1 0,999965, exactitude 0,999931, spécificité 0,998291, TP 1 472 923, FP 2, FN 100, TN 1 168 ;
- validation : aucun ensemble de validation distinct.

### STATUT

VALEUR REPRODUITE PAR UN ARTEFACT, MAIS PROVENANCE DATASET NON DÉMONTRÉE — À SUPPRIMER DU MÉMOIRE.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Un artefact historique interne rapporte F1 = 0,999965 après une partition aléatoire par ligne sur dix fichiers DDoS dérivés/compatibles CIC-DDoS2019. Le nom `UNSWNB15` utilisé pour l'archive, le modèle et le CSV est erroné ou, au minimum, trompeur.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- que le score provient d'UNSW-NB15 ;
- que le score provient du jeu CIC-DDoS2019 officiel non transformé ;
- que le protocole démontre une généralisation à des familles, captures ou périodes inédites ;
- que le dataset est traçable jusqu'à une source publique précise.

### ACTION À TRANSMETTRE À LUNA

Supprimer `0,999965` du résumé, du Mokuse, de l'abstract, du chapitre 5, du chapitre 6 scientifique, des tableaux de faux positifs et de toute figure/table secondaire. Ne pas le réattribuer à UNSW-NB15 ni au CIC-DDoS2019 officiel. Conserver, si nécessaire, uniquement une note de traçabilité interne hors résultats scientifiques.

## 3. Contrat `AgentMessage`

### FAIT VÉRIFIÉ

Le contrat métier réellement implémenté contient exactement sept champs : `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`. Il ne contient ni `event_id`, ni `message_id`, ni `metadata`.

### PREUVE

La dataclass `AgentMessage` est définie dans `src/logminer/agents/bus.py:29-39`. Les implémentations JSONL, Redis et MQTT construisent cette même dataclass. L'identifiant généré par Redis Streams existe au niveau du transport, mais n'est pas un champ d'`AgentMessage`.

### FICHIER/SCRIPT/ARTEFACT

- `src/logminer/agents/bus.py:29-39`
- JSONL : `src/logminer/agents/bus.py:61-102`
- Redis événements : `src/logminer/agents/bus.py:105-200`
- enveloppe des jobs Redis : `src/logminer/agents/bus.py:202-318`
- MQTT : `src/logminer/agents/bus.py:339-407`
- copie de preuve : `docs/memoire/pack_redaction_final/09_code_et_scripts_preuves/bus.py`
- texte à corriger : `memoire_logminer_latex_overleaf/chapters/chapitre3_modele_propose.tex:436-450`

### VALEUR OU CONFIGURATION

Structure exacte à présenter au §3.14 :

| Champ métier | Type | Défaut / production | Sens vérifié |
| --- | --- | --- | --- |
| `run_id` | `str` | fourni par le bus ou UUID hexadécimal au démarrage du bus | corrélation d'une exécution ; ce n'est pas l'identifiant unique d'un événement |
| `source` | `str` | requis à `publish` | composant/agent émetteur |
| `target` | `str` | requis à `publish` | composant/agent destinataire |
| `message_type` | `str` | requis à `publish` | nature du message |
| `payload` | `Dict[str, Any]` | `{}` | contenu applicatif extensible |
| `status` | `str` | `"ok"` | statut applicatif |
| `timestamp` | `str` | `datetime.now(timezone.utc).isoformat()` | date UTC ISO 8601 de création du message |

Distinction avec les transports :

- JSONL : sérialisation de `asdict(AgentMessage)` sur une ligne ; aucune enveloppe supplémentaire et aucun identifiant d'événement ajouté.
- Redis, stream d'événements : les sept champs sont stockés comme champs Redis, avec `payload` sérialisé en JSON. `XADD` crée un identifiant natif de stream, mais la méthode `publish` ne le retourne pas et `read` le jette.
- Redis, stream de tâches/jobs : enveloppe différente de `AgentMessage`, composée au stockage de `run_id`, `job_type`, `payload`, `status=queued`, `created_at`; la lecture ajoute `stream` et l'`id` Redis, puis éventuellement `claimed=true`. Cet `id` sert à `XACK`.
- MQTT : les sept champs sont publiés en JSON sur le topic `logminer/events/<target>/<message_type>`, avec QoS configurable, valeur par défaut 1. Aucun historique n'est relu par `read()`.
- Les éventuelles informations supplémentaires sont libres dans `payload`. Aucun sous-champ `metadata` n'est garanti par le contrat.

Existence d'un identifiant métier unique d'événement dans `AgentMessage` :

INFORMATION À VÉRIFIER.

L'implémentation inspectée n'en contient aucun ; seule l'enveloppe de job Redis expose son identifiant de transport.

### STATUT

IMPLÉMENTÉ ET VÉRIFIÉ — DESCRIPTION DU MÉMOIRE NON CONFORME.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Les bus JSONL, Redis et MQTT partagent une enveloppe métier à sept champs. `run_id` corrèle les messages d'un run. Redis ajoute ses propres identifiants de stream et mécanismes de groupe/ACK pour les jobs.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- qu'`AgentMessage` possède un identifiant unique d'événement ;
- qu'il contient un champ `metadata` distinct ;
- que `run_id` identifie un événement individuel ;
- que les enveloppes Redis de jobs et `AgentMessage` sont le même objet.

### ACTION À TRANSMETTRE À LUNA

Remplacer au §3.14 la structure conceptuelle à six champs par la table exacte à sept champs. Ajouter `target` et `status`, retirer `identifiant d'événement`, `famille probable` et `metadata` des champs obligatoires, puis séparer explicitement contrat métier et enveloppes Redis/MQTT.

## 4. Drain3 HDFS/BGL

### FAIT VÉRIFIÉ

Les détecteurs d'`evaluate_sequence_split.py` sont bien ajustés sur la matrice d'entraînement puis appliqués à la matrice de test. En revanche, Drain3 n'est pas ajusté uniquement sur l'entraînement : les CSV train et test sont enrichis par deux exécutions séparées de `sequence_window.py`, chacune instanciant un nouveau `TemplateMiner` et apprenant ses clusters sur sa propre partition.

Les fréquences et ratios de templates (`seq_template_frequency`, `seq_template_ratio`, rareté) sont en outre calculés sur la totalité de la partition en cours. Pour le test, cela utilise la distribution globale du test afin de construire les caractéristiques de chaque ligne. La revendication « Drain3 ajusté sur train puis appliqué à test » n'est donc pas soutenue.

### PREUVE

- `drain3_templates` crée `TemplateMiner(config=config)` à chaque appel, puis appelle `add_log_message` sur toutes les lignes reçues.
- Les commandes du README lancent séparément l'enrichissement de `validation_*_train.csv` et `validation_*_test.csv`.
- Les artefacts confirment des espaces Drain3 indépendants : HDFS a des identifiants 1-20 dans train et 1-14 dans test ; BGL 1-6 dans train et 1-9 dans test.
- Sur quatre messages BGL identiques présents des deux côtés, trois reçoivent des identifiants de cluster différents, preuve directe que les identifiants ne viennent pas d'un mineur entraîné commun.
- `template_totals = templates.value_counts()` est calculé sur toute la partition avant le parcours des fenêtres.

### FICHIER/SCRIPT/ARTEFACT

- `src/logminer/features/drain_templates.py`
- `src/logminer/features/sequence_windows.py`
- `src/logminer/agents/sequence_window.py`
- `src/logminer/features/event_features.py`
- `scripts/prepare_validation_dataset.py`
- `scripts/split_validation_dataset.py`
- `scripts/evaluate_sequence_split.py`
- `data/processed/validation_hdfs_split_summary.csv`
- `data/processed/validation_bgl_split_summary.csv`
- `data/processed/validation_hdfs_{train,test}_sequence_drain3.csv`
- `data/processed/validation_bgl_{train,test}_sequence_drain3.csv`
- `data/processed/validation_hdfs_drain3_train_test_metrics.csv`
- `data/processed/validation_bgl_drain3_train_test_metrics.csv`
- `data/processed/validation_hdfs_bgl_drain3_train_test_summary.csv`

### VALEUR OU CONFIGURATION

Préparation et splits :

- jeux de travail : 6 000 lignes HDFS et 6 000 lignes BGL, volontairement équilibrées à 3 000 normales / 3 000 anormales lors de la préparation ;
- HDFS : `stratified_group_chronological`, train 4 799 (2 400/2 399), test 1 201 (600/601), 568 blocs train, 227 blocs test, aucun `block_id` commun ;
- BGL : `stratified_chronological`, train 4 800 (2 400/2 400), test 1 200 (600/600) ;
- aucun ensemble de validation distinct ;
- les splits ne sont pas globalement chronologiques : les intervalles train/test se recouvrent, car la séparation chronologique est effectuée séparément par classe ;
- fenêtre : 30 minutes ; contexte HDFS par hôte et bloc/source/composant ; contexte BGL par hôte/source et composant/source ;
- méthode enregistrée dans les quatre artefacts : `drain3`, donc pas le fallback Drain-like pour ces fichiers ;
- seuil Drain-like 0,5 non applicable à Drain3 officiel ici : Drain3 utilise sa configuration par défaut, sans configuration persistée dans l'artefact ;
- quota d'anomalies : taux positif du train, soit environ 0,499896 pour HDFS et 0,5 pour BGL, borné entre 0,001 et 0,5 ;
- décision : classement global des scores du test et sélection des `round(N_test × quota)` meilleurs, soit exactement 600 prédictions positives dans chaque test ; il n'existe pas de seuil de score gelé sur validation ;
- modèles : IsolationForest (200 arbres, graine 42, `n_jobs=1`), z-score après StandardScaler appris sur train, bornes IQR apprises sur train, histogramme de champs appris sur train, autoencodeur `MLPRegressor` et moyenne de rangs ;
- résultats HDFS : histogramme F1 0,652789 (TP 392, FP 208, FN 209, TN 392) ; IsolationForest F1 0,637802 (TP 383, FP 217, FN 218, TN 383) ;
- résultats BGL : IsolationForest F1 1,000000 (TP 600, FP 0, FN 0, TN 600) ; autres méthodes retenues F1 0,973333 (TP 584, FP 16, FN 16, TN 584).

Configuration Drain3 exacte de la bibliothèque et version exacte utilisée lors du run :

INFORMATION À VÉRIFIER.

### STATUT

ÉVALUÉ, MAIS PROTOCOLE NON INDÉPENDANT — À DÉCLASSER EN EXPÉRIENCE EXPLORATOIRE.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Sur une partition locale équilibrée, les détecteurs ont été ajustés sur une matrice train et scorés sur une matrice test enrichie séparément avec Drain3 et des fenêtres de 30 minutes. Les valeurs HDFS et BGL ci-dessus ont été observées dans ce protocole précis.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- que Drain3 a été ajusté exclusivement sur train puis gelé pour test ;
- qu'il existe un train/validation/test ;
- que le split BGL est chronologique global ;
- que les caractéristiques de test sont indépendantes de la distribution complète du test ;
- que le seuil a été fixé sans connaissance des labels d'entraînement ou sur un jeu de validation indépendant ;
- que F1 = 1 sur BGL démontre une généralisation.

### ACTION À TRANSMETTRE À LUNA

Corriger les §5.10-5.11 et la discussion : ne plus qualifier ces résultats de référence principale « Drain3 train-test » au sens d'un extracteur gelé. Les présenter comme une expérience exploratoire avec détecteurs train→test mais extraction Drain3 indépendante/transductive. Pour fermer scientifiquement ce point, il faudra une nouvelle expérience, hors présente mission, avec un mineur Drain3 persistant ajusté sur train, un seuil fixé sur validation et un test entièrement gelé.

## 5. Unités CPU/RAM

### FAIT VÉRIFIÉ

Les unités du benchmark monolithique/agents sont établissables. Les valeurs CPU 121,339, 165,746 et 117,598 ne sont pas des pourcentages de la machine. Elles sont des pourcentages d'un cœur logique équivalent : 100 correspond à l'occupation moyenne d'un cœur logique, et une valeur supérieure à 100 est possible en exécution multithread/multiprocessus.

La RAM est une somme d'ensembles résidents (`RSS`) du processus racine et de ses enfants, divisée par `1024²`. L'unité mathématique est donc le MiB, même si les colonnes sont nommées `MB`.

### PREUVE

- CPU moyen contrôlé : somme des temps CPU utilisateur+système du processus et de ses enfants, divisée par le temps mur, puis multipliée par 100 (`run_controlled_monolith_vs_agents.py:198-206, 220-245`).
- CPU instantané maximal : somme des `proc.cpu_percent()` du même arbre (`:235-242`).
- RAM : somme des `memory_info().rss / 1024 / 1024` (`:235-239`).
- fréquence d'échantillonnage par défaut : 0,1 s.
- La campagne multicycle séparée normalise explicitement `cpu_equiv_core_percent / logical_cpus`; l'artefact enregistre 8 processeurs logiques.

### FICHIER/SCRIPT/ARTEFACT

- `scripts/run_controlled_monolith_vs_agents.py`
- `data/processed/controlled_monolith_vs_agents.csv`
- `docs/memoire/tables/table_controlled_monolith_vs_agents.md`
- `scripts/consolidate_controlled_architecture_tables.py`
- `src/logminer/agents/resource_monitor.py`
- `scripts/run_resource_campaign.py`
- `data/processed/resource_campaign.csv`
- `scripts/run_parallel_resource_campaign.py`
- `data/processed/parallel_resource_campaign.csv`

### VALEUR OU CONFIGURATION

| Mode | Tâches | Temps | Débit | CPU moyen, % d'un cœur équivalent | RAM RSS maximale, MiB | Échantillons |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Monolithique | 60/60 | 36,6815 s | 1,6357 tâche/s | 121,339 | 189,074 | 314 |
| Agents | 60/60 | 38,1803 s | 1,5715 tâche/s | 165,746 | 234,777 | 315 |
| Agents avec reprise | 60/60 | 39,3000 s | 1,5267 tâche/s | 117,598 | 189,395 | 335 |

Autres tableaux :

- campagne API 30 cycles : `cpu_equiv_core_percent` est la somme des pourcentages de processus ; `cpu_machine_percent` est cette valeur divisée par 8 processeurs logiques ; les 7,45 % et 0,41 % du chapitre 5 sont des moyennes de 30 snapshots effectués après chaque workflow, pas des moyennes temporelles continues pendant le workflow ;
- campagne parallèle 5 cycles : `cpu_machine_max` est le pic du processus courant divisé par 8 ; 17,1725 % est la moyenne des cinq pics de cycle ; 176,89 est la moyenne des cinq maxima RSS du processus, en MiB.

### STATUT

UNITÉS VÉRIFIÉES — VALEURS CONSERVABLES APRÈS RELABELLISATION.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Dans le benchmark contrôlé, le mode agents est légèrement plus lent et mobilise davantage de CPU équivalent et de RSS maximale que le mode monolithique sur 60 tâches. Les mesures décrivent l'arbre des processus de test sur cette machine et cette exécution.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- que 121,339 ou 165,746 représentent le pourcentage total de la machine ;
- que les valeurs `MB` sont des mégaoctets décimaux ;
- que les snapshots post-workflow de la campagne 30 cycles sont une intégrale temporelle de la charge ;
- que ces mesures sont indépendantes du matériel et de la charge concurrente.

### ACTION À TRANSMETTRE À LUNA

Dans le tableau monolithique/agents du chapitre 5, renommer `CPU moy.` en `CPU moyen (% d'un cœur logique équivalent)` et `RAM max.` en `RSS max. (MiB)`. Ajouter la méthode d'échantillonnage. Maintenir séparées les colonnes CPU équivalent et CPU machine des autres campagnes.

## 6. Mise à jour contrôlée des modèles

### FAIT VÉRIFIÉ

L'orchestrateur de mise à jour existe dans le code : export du feedback, exécution d'une commande d'entraînement par famille, évaluation courant/candidat, calcul du delta, décision `candidate_better` ou `kept_current`, promotion optionnelle avec sauvegarde et audit.

Une seule exécution est prouvée : un `dry-run` du 31 juillet 2026. Il a exporté zéro ligne de feedback et n'a exécuté aucun entraînement, aucune comparaison de score, aucune promotion et aucun rejet empirique.

### PREUVE

- rapport `generated_at=2026-07-31T09:40:19.464809+00:00`, `dry_run=true`, `promote=false`, `feedback_rows=0` ;
- neuf résultats, tous `status=dry_run`, avec `current_score=null`, `candidate_score=null`, `delta=null`, `promoted=false` ;
- aucune arborescence `models/candidates/` ou `models/backups/` ;
- aucun `monthly_retraining_report.json` d'exécution réelle ni `monthly_retraining_task.log` ;
- entrée d'audit `models.monthly_retraining` correspondant exactement au dry-run.

Installation effective de la tâche planifiée Windows :

INFORMATION À VÉRIFIER.

### FICHIER/SCRIPT/ARTEFACT

- `scripts/monthly_model_retraining.py`
- `scripts/run_monthly_retraining.ps1`
- `scripts/install_monthly_retraining_task.ps1`
- `docs/model_training/monthly_retraining_plan.example.json`
- `docs/model_training/monthly_retraining.md`
- `data/processed/monthly/monthly_retraining_dry_run_report.json`
- `data/processed/monthly_feedback_labels.csv`
- `data/processed/logminer_audit.jsonl`, action `models.monthly_retraining`

### VALEUR OU CONFIGURATION

- neuf familles planifiées : Windows, Wazuh, CICIDS réseau, réseau générique, Linux/auth, Linux, HDFS, BGL et fallback ;
- métriques : F1 si labels disponibles, sinon `stability_score` ;
- `min_delta` : 0,001 pour les familles au F1, 0,01 pour les familles au score de stabilité ;
- la promotion nécessite simultanément `delta >= min_delta` et l'option `--promote` ;
- en cas de promotion, copie de l'ancien modèle vers `models/backups/`, puis copie du candidat vers le chemin courant ;
- le dry-run ne valide que le chargement du plan, l'expansion des commandes, l'export vide et l'écriture du rapport/audit.

### STATUT

- code d'orchestration : IMPLÉMENTÉ ;
- chargement du plan et génération du rapport : TESTÉ EN DRY-RUN ;
- entraînement des candidats : NON ÉVALUÉ ;
- comparaison courant/candidat : NON ÉVALUÉ ;
- promotion réelle : NON ÉVALUÉ ;
- rejet réel avec maintien du modèle courant : NON ÉVALUÉ ;
- exécution mensuelle planifiée : PERSPECTIVE tant que son installation n'est pas prouvée.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Le dépôt contient une procédure contrôlée et auditable prévue pour comparer un candidat au modèle courant avant une promotion optionnelle. Le plan a été chargé avec succès lors d'un dry-run couvrant neuf familles.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- qu'un candidat a été entraîné par cette boucle ;
- qu'une comparaison courant/candidat a réellement été exécutée ;
- qu'une promotion ou un rejet a été observé ;
- que les décisions analyste ont déjà enrichi un entraînement, puisque l'export prouvé contient zéro ligne ;
- que la tâche mensuelle est installée et s'exécute automatiquement.

### ACTION À TRANSMETTRE À LUNA

Déclasser les formulations du résumé, des chapitres 3, 4 et 8 : employer « procédure implémentée et vérifiée en dry-run », pas « chaque nouvelle version est comparée puis promue ». Présenter le diagramme promotion/rejet comme logique implémentée mais non évaluée de bout en bout.

## 7. Ablation du routage

### FAIT VÉRIFIÉ

L'expérience contrôlée compare un RandomForest global à trois RandomForest spécialisés par famille, avec exactement le même espace de caractéristiques, les mêmes hyperparamètres, les mêmes splits et les mêmes graines. Elle utilise la famille connue pour choisir le modèle spécialisé ; elle n'évalue pas les erreurs du routeur réel.

Elle ne montre aucun gain prédictif systématique : le modèle spécialisé est très légèrement meilleur sur CICIDS2017, mais moins bon sur Linux/auth et UNSW-NB15. Les écarts sont faibles.

### PREUVE

Le CSV contient 30 lignes : 5 graines × 3 familles × 2 variantes. Le script entraîne le modèle global sur la concaténation des trains puis un modèle par groupe `family`; le test de chaque famille est identique entre variantes.

### FICHIER/SCRIPT/ARTEFACT

- `scripts/run_family_routing_ablation.py`
- `data/processed/family_routing_ablation.csv`
- `docs/memoire/tables/table_family_routing_ablation.md`
- `docs/memoire/figures/fig_family_routing_ablation.{svg,png}`
- copie CSV : `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/family_routing_ablation.csv`
- tableau opérationnel confondu : `docs/memoire/tables/table_family_routing_operational_ablation.md`
- copies actuellement divergentes dans `memoire_logminer_latex_overleaf/tables/`

### VALEUR OU CONFIGURATION

- datasets : `linux_auth_logs_labeled.csv`; huit CSV CICIDS2017 `MachineLearningCVE`; fichiers officiels locaux `UNSW_NB15_training-set.parquet` et `UNSW_NB15_testing-set.parquet`, concaténés avant sous-échantillonnage ;
- volume : jusqu'à 6 000 lignes par classe et famille, donc 12 000 lignes par famille ; split stratifié aléatoire 75/25 par famille ; 3 000 lignes de test par famille, équilibrées 1 500/1 500 ;
- graines : 42, 43, 44, 45, 46 ;
- espace commun : 12 numériques (`duration`, ports, paquets, octets, taux, tentatives, heure, jour, moyenne/écart-type/max/ratio non nul) et 4 catégorielles (`protocol`, `service`, `state`, `status`) ;
- prétraitement : imputation médiane + StandardScaler pour le numérique, imputation du mode + OneHotEncoder `handle_unknown=ignore`, `min_frequency=5` pour le catégoriel ;
- modèle des deux variantes : RandomForest 120 arbres, profondeur 22, `min_samples_leaf=2`, `class_weight=balanced`, `n_jobs=1`, graine du run ;
- métriques : exactitude, précision, rappel, F1, PR-AUC, MCC, FPR, FP/1 000 et matrice de confusion.

| Famille | F1 global | F1 spécialisé | Delta spécialisé-global | Lecture |
| --- | ---: | ---: | ---: | --- |
| CICIDS2017 | 0,999132 | 0,999333 | +0,000201 | avantage spécialisé minime |
| Linux/auth | 0,819404 | 0,816354 | -0,003050 | modèle global légèrement meilleur |
| UNSW-NB15 | 0,992214 | 0,991950 | -0,000264 | modèle global légèrement meilleur |

La « comparaison opérationnelle » n'est pas une ablation contrôlée : elle rapproche le modèle global minimal de modèles historiques employant d'autres caractéristiques, d'autres splits et parfois d'autres volumes. Elle ne permet pas d'attribuer son delta au routage. De plus, les copies divergent : le tableau généré depuis le CSV courant donne Linux/auth global 0,819404 et CICIDS global 0,999132, tandis que la copie LaTeX opérationnelle contient 0,819388 et 0,998887.

Commande exacte historiquement invoquée pour produire le CSV à cinq graines :

INFORMATION À VÉRIFIER.

La configuration effective est toutefois récupérable du CSV et implique l'option `--seeds 42,43,44,45,46`, car le défaut du script seul n'exécute qu'une graine.

### STATUT

ÉVALUÉ — AUCUN GAIN PRÉDICTIF SYSTÉMATIQUE ; ROUTEUR RÉEL NON TESTÉ PAR CETTE ABLATION.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Avec un espace commun et des modèles identiques, spécialiser l'entraînement par famille ne produit pas de supériorité systématique sur les trois familles testées. L'intérêt démontré du routage reste architectural : permettre des pipelines et caractéristiques différents selon la famille.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- que le routage spécialisé améliore systématiquement la prédiction ;
- que cette expérience mesure l'exactitude du routeur de fichiers/événements ;
- que les deltas de la comparaison opérationnelle sont causés par le routage seul ;
- que les résultats s'étendent à d'autres familles ou splits.

### ACTION À TRANSMETTRE À LUNA

Intégrer au chapitre 5 uniquement l'ablation contrôlée issue de `family_routing_ablation.csv`, avec les trois paires de F1 et la conclusion négative explicite. Ne pas utiliser le tableau opérationnel comme preuve causale. Régénérer ou supprimer les copies divergentes du tableau opérationnel.

## 8. Logistic Regression à 0,233670

### FAIT VÉRIFIÉ

`LogisticRegression` est bien le meilleur des cinq candidats testés selon le F1 moyen sur les cinq holdouts CICIDS2017 : 0,233669816, arrondi à 0,233670. Il n'est pas le meilleur selon toutes les métriques : `HistGradientBoosting` a le PR-AUC moyen le plus élevé (0,569002), et RandomForest produit beaucoup moins de faux positifs en moyenne (0,2 contre 40,0).

### PREUVE

Le CSV détaillé comporte 25 lignes : cinq modèles sur cinq couples graine/fichier tenu hors apprentissage. Le résumé trie par F1 moyen décroissant et place LogisticRegression en tête.

### FICHIER/SCRIPT/ARTEFACT

- `scripts/evaluate_cicids_model_candidates.py`
- fonctions de collecte/features : `scripts/evaluate_supervised_strict_splits.py`
- `data/processed/cicids_model_candidates_metrics.csv`
- `data/processed/cicids_model_candidates_summary.csv`
- `docs/memoire/tables/table_cicids_model_candidates.md`
- copies de preuve dans `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/`

### VALEUR OU CONFIGURATION

- dataset : CICIDS2017, répertoire `data/raw/Datasets/MachineLearningCSV/MachineLearningCVE` ;
- split : holdout d'un fichier/scénario complet, sans ce fichier dans le train ;
- graines et scénarios : 42 DDoS, 43 PortScan, 44 Bot, 45 Infiltration, 46 WebAttacks ; la graine détermine aussi le modèle et le mélange de l'échantillon ;
- train : 16 000 lignes par run, 8 000 bénignes et 8 000 attaques, issues des autres fichiers ;
- test : maximum 4 000 lignes par classe dans les deux premiers chunks de 100 000 du fichier tenu à l'écart ; tailles 8 000, 8 000, 5 966, 4 032 et 6 180, moyenne 6 435,6 ;
- caractéristiques : 78 colonnes numériques CICFlowMeter ; suppression de label, index, Flow ID, IP source/destination, Timestamp et SimillarHTTP ; valeurs non numériques converties, infinis remplacés, valeurs bornées à ±1e12 ;
- candidats : RandomForest, ExtraTrees, HistGradientBoosting, LogisticRegression avec StandardScaler, SGDClassifier logistique avec StandardScaler ;
- LogisticRegression : `max_iter=1000`, `class_weight=balanced`, solveur `lbfgs`, graine du run ;
- métriques : précision, rappel, F1, exactitude, PR-AUC, MCC, TN/FP/FN/TP et durée ;
- résultat LogisticRegression : précision moyenne 0,402899, rappel 0,189932, F1 moyen 0,233670, écart-type inter-holdouts 0,312455, PR-AUC 0,458829, MCC 0,186858, 40 FP et 1 963,2 FN en moyenne, durée moyenne 0,3663 s ;
- F1 par holdout LogisticRegression : 0,720357 (DDoS), 0,000497 (PortScan), 0 (Bot), 0,372881 (Infiltration), 0,074614 (WebAttacks) ;
- aucune validation séparée et aucun réglage d'hyperparamètres documenté sur une validation indépendante ;
- l'écart-type agrège des scénarios différents, pas cinq répétitions du même holdout.

### STATUT

ÉVALUÉ — MEILLEUR PAR F1 MOYEN PARMI CINQ CANDIDATS TESTÉS, MAIS TRÈS INSTABLE SELON LE SCÉNARIO.

### CE QUE LE MÉMOIRE PEUT AFFIRMER

Dans cette comparaison limitée à cinq candidats scikit-learn, LogisticRegression obtient le meilleur F1 moyen, 0,233670, sur cinq holdouts de fichiers/scénarios CICIDS2017. Ce résultat reste faible et très dispersé ; il ne résout pas la généralisation inter-scénarios.

### CE QUE LE MÉMOIRE NE PEUT PAS AFFIRMER

- que LogisticRegression est le meilleur modèle en général ;
- qu'il est meilleur selon PR-AUC ou faux positifs ;
- que les cinq graines sont cinq répétitions indépendantes d'un même scénario ;
- que le modèle détecte correctement Bot ou PortScan ;
- que l'expérience possède un ensemble de validation distinct.

### ACTION À TRANSMETTRE À LUNA

Pour le chapitre 5, intégrer le dataset, les cinq fichiers tenus à l'écart, les plafonds train/test, les 78 caractéristiques, les cinq candidats, les métriques complètes et les résultats par scénario. Qualifier LogisticRegression de « meilleur F1 moyen parmi les cinq candidats testés », jamais de « meilleur modèle » sans restriction.

## Table de clôture

| ÉLÉMENT | STATUT FINAL | PREUVE | SECTION À CORRIGER |
| --- | --- | --- | --- |
| Campagne multi-VM d'une heure | RETENABLE, preuve de laboratoire avec limites | `vbox_redis_1h_campaign.json`; script et checkpoints Redis | Résumé cohérent; ajouter au ch. 5; aligner ch. 8, ch. 6 scientifique, conclusion et annexes |
| Campagne multi-VM équilibrée | EXÉCUTÉE, contrôle court | `vbox_redis_balanced_campaign.json` | Annexe/protocole complémentaire |
| Campagne multi-VM panne/reprise | EXÉCUTÉE, preuve complémentaire de récupération | `vbox_redis_recovery_campaign.json` | Ch. 5 et annexes |
| Score 0,999965 | SUPPRESSION RECOMMANDÉE | `random_forest_unsw_80_20_metrics.csv`; archive `UNSWNB15.zip` à contenu DrDoS sans provenance officielle | Résumés FR/Lingala/EN, ch. 5, ch. 6 scientifique, tableaux/figures |
| Contrat `AgentMessage` | IMPLÉMENTÉ, description actuelle fausse | `src/logminer/agents/bus.py:29-39` | §3.14 et toute figure de contrat |
| Drain3 HDFS/BGL | ÉVALUÉ MAIS NON INDÉPENDANT; EXPLORATOIRE | scripts d'enrichissement séparés, CSV train/test Drain3, métriques | Ch. 5 §HDFS/BGL, résumé, ch. 6 scientifique et conclusion |
| CPU/RAM monolithique-agents | UNITÉS ÉTABLIES; RELABELLER | `run_controlled_monolith_vs_agents.py`; CSV contrôlé | Tableau et méthode ch. 5 |
| Mise à jour contrôlée | IMPLÉMENTÉE; TESTÉE EN DRY-RUN; NON ÉVALUÉE DE BOUT EN BOUT | `monthly_retraining_dry_run_report.json`, zéro feedback, aucun candidat/backup | Résumé, ch. 3, ch. 4, ch. 6 et ch. 8 |
| Ablation du routage | ÉVALUÉE; PAS DE GAIN SYSTÉMATIQUE; ROUTEUR RÉEL NON TESTÉ | `family_routing_ablation.csv` | Ajouter au ch. 5; conserver la nuance ch. 6; corriger tableaux divergents |
| LogisticRegression 0,233670 | VÉRIFIÉE, meilleure uniquement par F1 moyen parmi cinq candidats | CSV détaillé et résumé des candidats | Compléter le ch. 5; maintenir les réserves dans résumé/discussion |
