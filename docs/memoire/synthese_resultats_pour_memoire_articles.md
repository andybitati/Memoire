# Synthese Des Resultats Pour Memoire Et Articles

Date: 2026-06-03

Ce document rassemble les resultats consolidables dans le memoire et dans les
articles. Les figures vectorielles correspondantes sont dans
`docs/memoire/figures/`; les tableaux prets a reprendre sont dans
`docs/memoire/tables/`.

## Figures Generees

| Figure | Fichier | Usage recommande |
| --- | --- | --- |
| Architecture logique Logminer | `docs/memoire/figures/fig_architecture_logminer.svg` | Chapitre 3, article architecture multi-agents |
| Comparaison F1 validations | `docs/memoire/figures/fig_validation_selection_f1.svg` | Chapitre 5, article evaluation |
| Modeles supervises | `docs/memoire/figures/fig_supervised_models_f1.svg` | Resultats Linux/auth, CICIDS, UNSW |
| Latence quasi temps reel | `docs/memoire/figures/fig_realtime_workflow_latency.svg` | Objectifs 4 et 7 |
| Robustesse multi-format | `docs/memoire/figures/fig_robustness_multiformat.svg` | Objectifs 1, 6 et 7 |
| Portefeuille des modeles | `docs/memoire/figures/fig_model_portfolio_scale.svg` | Methodologie, choix multi-modeles |
| Faux positifs par famille | `docs/memoire/figures/fig_false_positive_rates.svg` | Chapitre 5, discussion des alertes |
| Recouvrement Wazuh / Logminer | `docs/memoire/figures/fig_wazuh_logminer_overlap.svg` | Comparaison outils standards |
| Campagne CPU/RAM multi-cycles | `docs/memoire/figures/fig_resource_campaign_multicycle.svg` | Evaluation ressources, article evaluation |
| Ablation routage familial | `docs/memoire/figures/fig_family_routing_ablation.svg` | Article 1: contribution scientifique |

Tableaux associes:

- `docs/memoire/tables/table_resultats_principaux.md`;
- `docs/memoire/tables/table_datasets_scenarios.md`;
- `docs/memoire/tables/table_realtime_benchmark.md`;
- `docs/memoire/tables/table_resource_snapshot.md`;
- `docs/memoire/tables/table_comparaison_outils_standards.md`;
- `docs/memoire/tables/table_false_positives.md`;
- `docs/memoire/tables/table_fail2ban_like_baseline.md`;
- `docs/memoire/tables/table_wazuh_logminer_summary.md`;
- `docs/memoire/tables/table_wazuh_logminer_overlap.md`;
- `docs/memoire/tables/table_resource_campaign_multicycle.md`;
- `docs/memoire/tables/table_intelligent_redis_long_campaign.md`;
- `docs/memoire/tables/table_intelligent_agents_ablation.md`;
- `docs/memoire/tables/table_intelligent_agents_resources.md`;
- `docs/memoire/tables/table_family_routing_ablation.md`;
- `docs/memoire/tables/table_family_routing_operational_ablation.md`.

## Resultat Global

Le prototype Logminer valide une architecture multi-agents modulaire capable de
traiter des journaux heterogenes, de les normaliser dans un schema commun, de
router chaque source vers un modele adapte, puis de produire des anomalies
candidates et des incidents correles exploitables dans un dashboard. Les
resultats les plus directement mesurables concernent les familles de donnees
supervisees Linux/auth, CICIDS et UNSW-NB15, mais ces scores restent
exploratoires tant qu'ils ne sont pas reproduits avec un split temporel ou par
scenario. Les preuves les plus solides pour le prototype concernent la
robustesse du pipeline multi-format, la tracabilite, la campagne Redis locale
et la reproductibilite des artefacts.

Le systeme doit etre presente comme un prototype local avance et extensible:
la V1 CLI constitue le socle stable, la V2 FastAPI apporte l'interaction par
services REST, et Redis Streams est deja integre comme bus evenementiel
optionnel pour tracer les workflows agents. Cette brique prepare une
distribution multi-machine, mais elle ne prouve pas encore une scalabilite SOC.
MQTT reste une perspective pour des collecteurs plus proches de l'IoT ou du
temps reel.

Tableau a reprendre pour le chapitre architecture:

- `docs/memoire/tables/table_redis_streams_integration.md`.
- `docs/memoire/tables/table_mqtt_integration.md`.
- `docs/memoire/tables/table_scalability_redis_smoke.md` pour le memoire ou
  l'article 2, pas comme resultat central de l'article 1.

Regle de frontiere:

- `docs/memoire/frontiere_article1_article2_scalabilite.md`.

## Protocole Experimental

Les experiences sont organisees autour de quatre familles de donnees:

1. Journaux reels locaux: Windows Event/Security, Wazuh, Linux/auth.
2. Datasets publics de logs systemes: HDFS et BGL.
3. Datasets reseau labellises: CICIDS2017/MachineLearningCVE et
   UNSW-NB15.
4. Scenarios synthetiques ou controles: Windows simule, logs corrompus et
   multi-formats Apache/CEF/CloudTrail/Linux auth.

Les donnees brutes sont parsees et normalisees par Logminer. Les sources
labellisees permettent une evaluation par precision, rappel, F1-score,
accuracy, specificity et matrice de confusion. Les sources non labellisees
produisent des anomalies candidates, qui doivent etre interpretees par un
analyste ou par l'agent correlateur.

## Resultats Quantitatifs Principaux

| Famille | Modele | Resultat |
| --- | --- | --- |
| Linux/auth | RandomForest supervise | F1 = 0.916602 |
| CICIDS2017 | RandomForest supervise | F1 = 0.997163 |
| UNSW-NB15 | RandomForest supervise | F1 = 0.999965, resultat exploratoire a revalider |
| Wazuh | Isolation Forest | 122 563 evenements, 3 676 anomalies candidates |
| BGL | Selection validation | F1 autour de 0.994333 |
| HDFS | Selection validation | F1 autour de 0.599333 a 0.600333 |
| Windows simule | Isolation Forest / baseline | F1 = 1.0 en scenario controle |

Interpretation:

- Les resultats supervises sont forts, mais ils dependent de la compatibilite
  du schema et de la distribution d'entrainement.
- Les tres hauts scores reseau doivent etre discutes avec prudence, car les
  datasets peuvent etre desequilibres ou separer fortement les classes.
- HDFS montre que certains logs sequentiels restent difficiles avec des
  features legeres; c'est un bon argument pour presenter le deep learning comme
  perspective ou comparaison experimentale.
- Les anomalies non supervisees ne prouvent pas une intrusion: elles signalent
  des evenements rares ou atypiques a analyser.

## Benchmark Quasi Temps Reel

Benchmark execute via `scripts/benchmark_realtime_workflow.py` sur l'endpoint
FastAPI `/run/discovered`, avec 10 cycles, intervalle de 2 secondes et
`max_mb=5`.

Resultats:

- 10 cycles termines avec statut `ok`;
- 8 537 lignes analysees par cycle;
- latence workflow minimale: 3.1672 s;
- latence workflow moyenne: 8.2012 s;
- latence workflow maximale: 15.3289 s.

Formulation recommandee:

> Le prototype atteint un fonctionnement quasi temps reel local sur des cycles
> courts de collecte et d'analyse. Les latences observees varient selon la
> charge et le modele route, avec une moyenne d'environ 10,65 secondes sur cinq
> cycles et 8 537 lignes par cycle. Ces resultats valident la faisabilite d'une
> boucle interactive, tout en laissant l'optimisation de la latence et la
> distribution multi-machine comme perspectives d'industrialisation.

Une campagne CPU/RAM multi-cycles a ete executee via
`scripts/run_resource_campaign.py` sur l'endpoint FastAPI `/run/discovered`,
avec 30 cycles, intervalle de 2 secondes et `max_mb=5`.

Resultats:

- 30 cycles termines;
- 8 537 lignes analysees par cycle;
- latence moyenne workflow: 9.3300 s;
- latence maximale workflow: 21.6007 s;
- API / Orchestrateur: CPU moyen 59.61% equivalent coeur, CPU machine moyen
  7.45%, RAM moyenne 187.82 MB;
- Processus Logminer: CPU moyen 3.26% equivalent coeur, CPU machine moyen
  0.41%, RAM moyenne 495.41 MB.

Le tableau final est dans
`docs/memoire/tables/table_resource_campaign_multicycle.md` et la figure
associee dans `docs/memoire/figures/fig_resource_campaign_multicycle.svg`.

## Campagne Parallele CPU/RAM

Une campagne complementaire a ete executee via
`scripts/run_parallel_resource_campaign.py` sans serveur FastAPI. Elle mesure
le mode parallele de `model_compare` avec 3 workers sur 500 evenements
synthetiques labelises par cycle.

Resultats:

- 5 cycles termines;
- 500 evenements analyses par cycle;
- 3 workers paralleles;
- duree moyenne workflow: 3.6232 s;
- duree maximale workflow: 6.0172 s;
- CPU machine maximal moyen: 17.1725%;
- RAM maximale moyenne: 176.89 MB.

Le tableau est dans
`docs/memoire/tables/table_parallel_resource_campaign.md` et la figure
associee dans `docs/memoire/figures/fig_parallel_resource_campaign.svg`.
Ces mesures doivent etre presentees comme une validation locale du mode
multi-worker, et non comme une preuve de debit SOC industriel.

## Campagne Redis Agents Intelligents

Une campagne longue Redis a ete executee avec trois workers principaux, un
worker de reprise et une panne volontaire avant acquittement. Le run retenu
pour le memoire est `redis-campaign-20260717161257`.

Resultats:

- 150 taches enfilees;
- 150 taches uniques terminees;
- 0 echec;
- 0 tache pending en fin de campagne;
- 0 perte estimee;
- 1 panne simulee avant `ack`, reprise par `redis-recovery-agent`;
- duree observee depuis les evenements Redis: 102.4202 s;
- debit observe: 1.4646 taches/s;
- latence p95/p99 par tache: 5.3567 s / 8.2873 s.

Le tableau final est dans
`docs/memoire/tables/table_intelligent_redis_long_campaign.md`.

Formulation recommandee:

> La campagne Redis longue montre que les agents intelligents Logminer peuvent
> se repartir des taches heterogenes dans plusieurs processus, publier leurs
> decisions et recuperer une tache abandonnee avant acquittement. Dans le run
> retenu, les 150 taches ont ete terminees sans echec ni pending final. La
> preuve reste locale et multi-processus; le deploiement multi-machine est une
> perspective experimentale distincte.

## Robustesse Multi-Format

Le controle `scripts/run_robustness_scalability_checks.py` valide le parsing
sur cinq entrees: Apache, CEF/LEEF, CloudTrail, Linux auth et un log
corrompu/incomplet. Le pipeline produit un CSV unique avec 6 lignes normalisees
en 0.1242 seconde. Le log incomplet est conserve avec le statut `kept_unknown`,
ce qui evite la perte silencieuse d'information.

Formulation recommandee:

> La robustesse du pipeline repose sur une strategie conservatrice: les formats
> connus sont normalises par des parseurs specialises, tandis que les lignes
> incompletes ou inconnues sont conservees sous une categorie generique. Cette
> approche privilegie la tracabilite et evite qu'un format non reconnu provoque
> une rupture du workflow.

## Comparaison Qualitative Avec Outils Standards

Logminer ne remplace pas directement fail2ban, OSSEC ou Wazuh. Son role est
plutot complementaire:

- fail2ban est efficace pour des reactions operationnelles simples, par exemple
  bloquer une IP apres des echecs repetes;
- OSSEC/Wazuh fournit un socle HIDS/SIEM mature, riche en regles, agents et
  decodage;
- Logminer apporte une couche analytique modulaire: routage par famille de
  journaux, modeles IA legers, correlation contextuelle, exploration dashboard
  et anomalies candidates.

Phrase defensive pour le memoire:

> La comparaison montre que Logminer doit etre compris comme un complement
> analytique aux outils standards. La solution ne cherche pas a remplacer un
> HIDS/SIEM mature, mais a ajouter une detection adaptative et interpretable
> sur des journaux heterogenes, avec des modeles specialises et une
> visualisation centree analyste.

## Ablation Du Routage Familial

L'article doit integrer l'ablation du routage familial pour soutenir la
contribution scientifique. Deux niveaux sont disponibles:

- ablation controlee: baseline globale et modeles specialises forces dans le
  meme espace de features commun minimal;
- ablation operationnelle: baseline globale commune comparee aux configurations
  specialisees completes.

Resultat a formuler prudemment:

> Le routage familial ne garantit pas un gain F1 universel sur chaque famille.
> Il apporte surtout une specialisation controlee, utile lorsque les familles de
> logs exigent des espaces de features et des modeles differents. L'ablation
> operationnelle montre un gain net sur Linux/auth, un gain leger sur UNSW, et
> un resultat comparable sur CICIDS ou la baseline globale est deja proche de
> la saturation.

Phrase de reponse a ELK:

> Une pile ELK fournit principalement ingestion, indexation, recherche,
> stockage et visualisation. Logminer se positionne comme une couche analytique:
> selection dynamique du modele selon la famille de journaux, unification des
> sorties supervisees/non supervisees en anomalies candidates et correlation en
> incidents interpretables.

Clarification multi-agent:

> Le terme agent est utilise au sens architectural: agents logiciels
> specialises, communicants et coordonnes. Le prototype ne revendique pas encore
> des agents cognitifs autonomes, de negotiation FIPA ou de reinforcement
> learning cooperatif.

## Legendes Pretes A Inserer

Figure architecture:

> Architecture logique du prototype Logminer. Les journaux heterogenes sont
> collectes, parses, normalises, routes vers un modele specialise, puis
> transformes en anomalies candidates et incidents correles consultables dans
> le dashboard.

Figure validation F1:

> Comparaison des meilleurs detecteurs par dataset de validation. Les resultats
> soulignent la variabilite selon les familles de logs: BGL et Windows simule
> obtiennent de tres bons scores, tandis que HDFS reste plus difficile avec des
> features legeres.

Figure modeles supervises:

> Performances des modeles supervises RandomForest sur Linux/auth, CICIDS2017
> et UNSW-NB15. Les scores eleves valident surtout l'integration de modeles
> supervises par famille dans le prototype. Leur generalisation doit etre
> revalidee avec des partitions temporelles ou par scenarios d'attaque.

Figure latence:

> Latence du workflow quasi temps reel execute via FastAPI. Chaque cycle lance
> la decouverte d'une source, la detection routee et la correlation, puis
> retourne les chemins de sortie et compteurs au dashboard.

Figure robustesse:

> Controle de robustesse du parsing multi-format. Le pipeline traite des logs
> Apache, CEF/LEEF, CloudTrail, Linux auth et conserve les entrees corrompues ou
> inconnues sans interrompre le workflow.

Figure portefeuille:

> Portefeuille de modeles Logminer. Les artefacts couvrent plusieurs familles:
> Windows, Wazuh, Linux/auth, reseau, HDFS, BGL et fallback. L'echelle
> logarithmique rend comparables les volumes tres differents.

Figure faux positifs:

> Taux de faux positifs observes par famille de donnees et modele. Cette figure
> permet de discuter la charge analytique produite par les alertes candidates,
> au-dela des seuls scores globaux de precision, rappel et F1-score.

Figure Wazuh / Logminer:

> Recouvrement entre groupes d'evenements Wazuh exportes et anomalies
> candidates detectees par Logminer. La figure illustre la complementarite
> entre une couche SIEM reglee et une analyse non supervisee orientee rarete.

Figure campagne CPU/RAM:

> Evolution de la charge CPU/RAM observee pendant 30 cycles d'analyse via
> FastAPI. La mesure distingue le CPU equivalent coeur du CPU normalise sur la
> machine afin d'eviter une interpretation erronee des valeurs superieures a
> 100% sur les processus multi-coeurs.

## Captures Dashboard A Produire

Captures recommandees pour le memoire:

1. Vue globale: compteurs evenements, anomalies, incidents.
2. Vue resultats: tableau d'anomalies candidates avec filtres.
3. Timeline/heatmap: analyse temporelle.
4. Detail incident: justification, anomalies sources, priorite.
5. Decisions analyste: validation, rejet ou reclassement.
6. Vue technique: flux agents, audit, ressources CPU/RAM, modeles.
7. Export CSV: preuve de recuperation des resultats.

Scenario de demonstration:

1. Lancer FastAPI: `python -m uvicorn src.logminer.api:app --host 127.0.0.1 --port 8000`.
2. Lancer le dashboard web: `cd web/dashboard` puis `node server.mjs`.
3. Ouvrir `http://127.0.0.1:5173`.
4. Declencher ou attendre l'analyse automatique.
5. Filtrer les anomalies par severite/source.
6. Ouvrir un incident, lire la justification, puis enregistrer une decision.
7. Montrer la trace dans l'audit et exporter les resultats.

## Limites A Presenter Clairement

- La distribution est prouvee au niveau logique et service local; le
  deploiement multi-machine reste une perspective.
- Les modeles non supervises detectent surtout la rarete ou l'ecart au
  comportement appris; leurs sorties sont des anomalies candidates.
- L'auto-apprentissage continu n'est pas encore complet: le systeme est plutot
  adaptatif par routage multi-modeles et par specialisation des artefacts.
- Les performances supervisees sont dependantes des datasets et doivent etre
  interpretees en tenant compte du desequilibre et de la compatibilite des
  schemas.
- La latence quasi temps reel est acceptable pour une demonstration locale,
  mais demande optimisation pour une production SOC.
- Les resultats HDFS montrent la limite des features legeres ligne par ligne
  pour les logs de systemes distribues. Une extension Drain-like, templates de
  logs ou fenetres temporelles est necessaire pour rivaliser avec les approches
  sequentielles type DeepLog/LogAnomaly.

## Contribution A Mettre En Avant

La contribution principale du travail est l'integration coherente de quatre
briques: normalisation multi-format, architecture d'agents specialises, routage
multi-modeles par famille de journaux et dashboard interpretable. Cette
combinaison permet de passer de journaux heterogenes a des incidents
priorisables, tout en gardant une architecture assez legere pour une PME, une
universite ou une administration locale.
