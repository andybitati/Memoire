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

Tableaux associes:

- `docs/memoire/tables/table_resultats_principaux.md`;
- `docs/memoire/tables/table_datasets_scenarios.md`;
- `docs/memoire/tables/table_realtime_benchmark.md`;
- `docs/memoire/tables/table_resource_snapshot.md`;
- `docs/memoire/tables/table_comparaison_outils_standards.md`.

## Resultat Global

Le prototype Logminer valide une architecture multi-agents modulaire capable de
traiter des journaux heterogenes, de les normaliser dans un schema commun, de
router chaque source vers un modele adapte, puis de produire des anomalies
candidates et des incidents correles exploitables dans un dashboard. Les
resultats les plus solides concernent les familles de donnees supervisees
Linux/auth, CICIDS et UNSW/CIC-DDoS, ainsi que la robustesse du pipeline
multi-format.

Le systeme doit etre presente comme un prototype local avance et extensible:
la V1 CLI constitue le socle stable, la V2 FastAPI apporte l'interaction par
services REST, et Redis/MQTT restent une trajectoire d'industrialisation vers
une distribution multi-machine.

## Protocole Experimental

Les experiences sont organisees autour de quatre familles de donnees:

1. Journaux reels locaux: Windows Event/Security, Wazuh, Linux/auth.
2. Datasets publics de logs systemes: HDFS et BGL.
3. Datasets reseau labellises: CICIDS2017/MachineLearningCVE et
   UNSW/CIC-DDoS.
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
| UNSW/CIC-DDoS | RandomForest supervise | F1 = 0.999965 |
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
FastAPI `/run/discovered`, avec 5 cycles, intervalle de 2 secondes et
`max_mb=5`.

Resultats:

- 5 cycles termines avec statut `ok`;
- 8 537 lignes analysees par cycle;
- latence workflow minimale: 3.0865 s;
- latence workflow moyenne: 10.6473 s;
- latence workflow maximale: 19.8163 s.

Formulation recommandee:

> Le prototype atteint un fonctionnement quasi temps reel local sur des cycles
> courts de collecte et d'analyse. Les latences observees varient selon la
> charge et le modele route, avec une moyenne d'environ 10,65 secondes sur cinq
> cycles et 8 537 lignes par cycle. Ces resultats valident la faisabilite d'une
> boucle interactive, tout en laissant l'optimisation de la latence et la
> distribution multi-machine comme perspectives d'industrialisation.

Un instantane ressources a aussi ete archive dans
`data/processed/resource_snapshot_20260603.json` et resume dans
`docs/memoire/tables/table_resource_snapshot.md`. Il montre que l'API expose
deja une mesure CPU/RAM des processus Logminer, utile comme preuve de
monitoring. Pour un tableau scientifique final, il faudra idealement repeter
la mesure pendant plusieurs cycles et rapporter moyenne, maximum et ecart-type.

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
> et UNSW/CIC-DDoS. Les scores eleves valident l'interet de modeles specialises
> par famille, sous reserve de compatibilite des schemas.

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

## Contribution A Mettre En Avant

La contribution principale du travail est l'integration coherente de quatre
briques: normalisation multi-format, architecture d'agents specialises, routage
multi-modeles par famille de journaux et dashboard interpretable. Cette
combinaison permet de passer de journaux heterogenes a des incidents
priorisables, tout en gardant une architecture assez legere pour une PME, une
universite ou une administration locale.
