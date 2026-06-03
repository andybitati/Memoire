# Etat Des Lieux Technique Face Au Document Directeur

Date: 2026-06-03

Perimetre: exigences techniques et experimentales uniquement. La redaction du
memoire, la mise en forme des chapitres et les corrections stylistiques ne sont
pas evaluees ici.

Document directeur:

- `docs/memoire/Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et Reseaux a l'aide d'Agents Intelligents Multi-Taches.pdf`

## Synthese Courte

Le travail est techniquement tres avance. Les sept objectifs du document
directeur ont une implementation ou une preuve locale. Le prototype couvre la
collecte, le parsing, la normalisation, la detection IA, le routage
multi-modeles, la correlation, le dashboard interactif, les validations
quantitatives et les premiers benchmarks de latence/ressources.

Les principaux manques ne sont plus structurels. Ils concernent surtout:

- la capture finale du dashboard pour preuve visuelle;
- une campagne CPU/RAM plus longue et statistique si l'evaluation finale doit
  depasser l'instantane deja produit;
- les faux positifs par periode quand les timestamps/labels ligne par ligne le
  permettent;
- la preuve d'une distribution multi-machine reelle, encore plutot perspective;
- la comparaison operationnelle stricte avec execution reelle de fail2ban,
  OSSEC ou Wazuh, si elle est exigee.

Depuis la derniere mise a jour, une comparaison scientifiquement prudente avec
les outils standards a ete ajoutee:

- baseline experimentale `fail2ban_like_rules` sur Linux/auth labellise;
- recouvrement Wazuh / Logminer sur exports Wazuh disponibles;
- comparaison fonctionnelle OSSEC/fail2ban/Wazuh;
- note methodologique: `docs/memoire/comparaison_scientifique_outils_standards.md`.

La campagne CPU/RAM multi-cycles est egalement executee:

- script: `scripts/run_resource_campaign.py`;
- protocole: `docs/memoire/protocole_campagne_cpu_ram_multicycles.md`;
- sorties produites: `data/processed/resource_campaign.csv`,
  `docs/memoire/tables/table_resource_campaign_multicycle.md`,
  `docs/memoire/figures/fig_resource_campaign_multicycle.svg`.
- resultat court: 30 cycles OK, 8 537 lignes par cycle, workflow moyen
  9.3300 s, workflow max 21.6007 s.

## Tableau Global

| Objectif directeur | Exigence technique | Etat | Preuves locales | Reste technique |
| --- | --- | --- | --- | --- |
| 1. Logs | Identifier, categoriser, parser et normaliser les journaux | Tres avance | Parseurs multi-format, schema commun, pipeline, taxonomie | Ajouter davantage d'exemples bruts -> normalises |
| 2. Detection | Comparer methodes classiques, statistiques et IA | Tres avance | `validation_summary.csv`, comparateur, baselines, modeles IA | Consolider faux positifs par periode |
| 3. Multi-agents | Concevoir agents specialises et communication | Avance | Agents Python, bus JSONL, FastAPI, Redis optionnel, diagrammes | Distribution multi-machine non encore prouvee |
| 4. IA legere temps reel | Integrer modeles legers et workflow quasi temps reel | Avance | `.joblib`, routeur, benchmark temps reel | Optimiser latence et verifier adaptation continue |
| 5. Dashboard | Visualiser, filtrer, interagir avec alertes | Avance | Dashboard web/Streamlit, decisions, audit, graphiques temps reel | Captures finales desktop/mobile |
| 6. Tests varies | Tester logs simules, reels et publics | Tres avance | Windows, Wazuh, Linux/auth, HDFS, BGL, CICIDS, UNSW, robustesse, comparaison operationnelle | Execution reelle fail2ban/OSSEC/Wazuh si demandee |
| 7. Evaluation | Mesurer precision, rappel, F1, latence, charge, extensibilite | Avance | Metriques supervisees, validations, benchmark, ressources API, faux positifs | Moyennes CPU/RAM sur plusieurs cycles, tests panne agent |

## Objectif 1 - Logs, Parsing Et Normalisation

Exigences du document directeur:

- identifier les formats courants: syslog, Windows Event Log, Apache, etc.;
- creer un module de parsing multi-format;
- normaliser les evenements pour traitement unifie;
- produire une taxonomie de logs.

Etat actuel:

- Conforme techniquement.
- Le pipeline Logminer detecte et parse plusieurs familles: Windows Event,
  syslog/Linux, Apache, HDFS, BGL, CEF/LEEF, CloudTrail, JSONL, tcpdump texte,
  pcap et formats inconnus conserves.
- Le schema commun est centralise dans `src/logminer/schema/columns.py`.
- La detection de format est dans `src/logminer/detectors/file_detector.py`.
- Le pipeline principal est dans `src/logminer/pipeline.py`.
- La taxonomie existe dans `docs/memoire/taxonomie_journaux.md`.
- Le controle robustesse montre que les logs incomplets peuvent etre conserves
  en `unknown` au lieu de casser le workflow.

Niveau: 90%.

Reste technique:

- enrichir les exemples bruts -> normalises;
- ajouter eventuellement plus de cas applicatifs type Nginx/MySQL si souhaite,
  mais ce n'est pas bloquant.

## Objectif 2 - Techniques De Detection D'Anomalies

Exigences du document directeur:

- comparer seuils, regles, statistiques, ML et deep learning leger;
- definir precision, rappel, F1-score;
- justifier les modeles legers.

Etat actuel:

- Conforme techniquement.
- Methodes presentes: regles/baselines, z-score, IQR, histogramme, entropie,
  Isolation Forest, k-Means, One-Class SVM, LOF, Autoencoder MLP et LSTM
  experimental.
- Les resultats sont consolides dans:
  - `data/processed/validation_summary.csv`;
  - `data/processed/validation_selection_summary.csv`;
  - `data/processed/validation_hdfs_metrics.csv`;
  - `data/processed/validation_bgl_metrics.csv`;
  - `data/processed/validation_simulated_windows_metrics.csv`.
- Les figures sont produites dans `docs/memoire/figures/`.

Resultats cles:

- BGL: meilleurs scores autour de F1 = 0.994333.
- HDFS: meilleurs scores autour de F1 = 0.599333 a 0.600333.
- Windows simule: certains modeles atteignent F1 = 1.0 dans un scenario
  controle.

Niveau: 88%.

Reste technique:

- eviter de sur-vendre le deep learning: il est experimental;
- faux positifs deja consolides par dataset dans
  `docs/memoire/tables/table_false_positives.md`;
- faux positifs par periode seulement si les donnees labelisees conservent un
  timestamp ligne par ligne exploitable.

## Objectif 3 - Architecture Multi-Agents Distribuee

Exigences du document directeur:

- definir agents collecteur, parseur, detecteur, correlateur, visualiseur;
- definir les flux de communication;
- prototyper une architecture modulaire;
- utiliser REST, pub/sub, sockets ou bus equivalent.

Etat actuel:

- Conforme pour un prototype local modulaire.
- Agents disponibles dans `src/logminer/agents/`:
  - collecteur;
  - parseur;
  - detecteur;
  - correlateur;
  - orchestrateur;
  - routeur modele;
  - runtime;
  - privilege;
  - audit;
  - dashboard.
- Communication:
  - bus JSONL local;
  - FastAPI V2;
  - Redis Streams optionnel;
  - contrat de message dans `docs/architecture/message_contract.md`.
- Diagrammes Mermaid ajoutes dans `docs/architecture/diagrammes_memoire.md`.
- Figure SVG d'architecture: `docs/memoire/figures/fig_architecture_logminer.svg`.

Niveau: 82%.

Reste technique:

- prouver un deploiement multi-machine reel si on veut soutenir le mot
  "distribue" au sens strict;
- sinon, presenter la distribution comme logique/agentique avec extension
  FastAPI/Redis.

## Objectif 4 - Modeles IA Legers Et Quasi Temps Reel

Exigences du document directeur:

- integrer des modeles IA legers;
- fonctionner sur machines non specialisees;
- permettre detection quasi temps reel;
- benchmarker les performances.

Etat actuel:

- Conforme prototype.
- Artefacts dans `models/`:
  - Isolation Forest Windows;
  - Isolation Forest Wazuh;
  - Isolation Forest HDFS/BGL/Linux/fallback;
  - RandomForest Linux/auth;
  - RandomForest CICIDS;
  - RandomForest UNSW/CIC-DDoS.
- Routeur multi-modeles: `src/logminer/agents/model_router.py`.
- Registre: `docs/model_training/model_registry.md`.
- Benchmark quasi temps reel produit:
  - `data/processed/realtime_workflow_benchmark.csv`;
  - 5 cycles OK;
  - 8 537 lignes par cycle;
  - latence moyenne workflow: 10.6473 s;
  - min: 3.0865 s;
  - max: 19.8163 s.

Niveau: 84%.

Reste technique:

- optimiser les cycles les plus lents;
- formaliser ce qui est vraiment adaptatif: routage multi-modeles oui,
  auto-apprentissage continu pas encore complet.

## Objectif 5 - Dashboard Visuel Interactif

Exigences du document directeur:

- interface web simple;
- affichage logs, alertes, statistiques temporelles;
- filtres par source/type/gravite;
- validation/rejet/reclassement d'alertes;
- graphiques temps reel, heatmap, timeline.

Etat actuel:

- Conforme prototype.
- Dashboard Streamlit: `src/logminer/agents/dashboard.py`.
- Dashboard web: `web/dashboard`.
- Fonctionnalites presentes:
  - vues Vue d'ensemble, Resultats, Technique;
  - filtres par host, severity, category, source, recherche texte;
  - incidents correles;
  - detail incident;
  - decisions analyste avec audit;
  - export CSV;
  - explication locale/LLM optionnelle;
  - ressources CPU/RAM par agent;
  - graphiques temps reel ajoutes;
  - correction CPU: distinction CPU equivalent coeur et CPU machine normalise;
  - correction timeline/heatmap: extraction timestamps Apache/Wazuh/ISO.

Niveau: 86%.

Reste technique:

- produire captures desktop/mobile finales;
- verifier visuellement que la heatmap se remplit apres `Ctrl+F5` et nouveau
  refresh;
- eventuellement ajouter une vraie serie "nouveaux evenements par intervalle"
  si les sources de logs evoluent pendant la demo.

## Objectif 6 - Tests Sur Donnees Variees

Exigences du document directeur:

- logs simules;
- logs reels;
- datasets publics;
- attaques connues;
- comparaison avec fail2ban, OSSEC, Wazuh.

Etat actuel:

- Tres avance.
- Sources exploitees:
  - Windows Event/Application/System/Security;
  - Wazuh;
  - Linux/auth;
  - HDFS;
  - BGL;
  - CICIDS2017 / MachineLearningCVE;
  - UNSW / CIC-DDoS;
  - Windows simule;
  - logs robustesse Apache, CEF/LEEF, CloudTrail, Linux auth, log incomplet.
- Tableau produit:
  - `docs/memoire/tables/table_datasets_scenarios.md`.
- Robustesse:
  - `data/processed/robustness_scalability_report.csv`.
- Comparaison operationnelle:
  - `docs/memoire/tables/table_comparaison_outils_standards.md`;
  - `docs/memoire/tables/table_operational_tool_comparison.md`;
  - `docs/memoire/tables/table_fail2ban_like_baseline.md`;
  - `docs/memoire/tables/table_wazuh_logminer_summary.md`;
  - `docs/memoire/tables/table_wazuh_logminer_overlap.md`;
  - `docs/memoire/figures/fig_wazuh_logminer_overlap.svg`.

Niveau: 88%.

Reste technique:

- eventuellement lancer un test reel fail2ban/OSSEC/Wazuh si une preuve
  d'execution externe est exigee;
- ne pas presenter la baseline fail2ban-like comme une execution officielle de
  fail2ban.

## Objectif 7 - Evaluation Globale

Exigences du document directeur:

- precision;
- rappel;
- F1-score;
- latence;
- CPU/RAM;
- scalabilite;
- resilience.

Etat actuel:

- Avance.
- Resultats supervises:
  - Linux/auth: F1 = 0.916602;
  - CICIDS: F1 = 0.997163;
  - UNSW/CIC-DDoS: F1 = 0.999965.
- Resultats non supervises:
  - Wazuh: 122 563 evenements, 3 676 anomalies candidates;
  - BGL/HDFS/Windows simule avec validations.
- Latence:
  - benchmark quasi temps reel produit.
- CPU/RAM:
  - endpoint `/resources`;
  - dashboard ressources par agent;
  - distinction CPU equivalent coeur et CPU machine normalise.
  - script multi-cycles dans `scripts/run_resource_campaign.py`.
  - campagne 30 cycles produite dans `data/processed/resource_campaign.csv`.
  - tableau: `docs/memoire/tables/table_resource_campaign_multicycle.md`.
  - figure: `docs/memoire/figures/fig_resource_campaign_multicycle.svg`.
- Faux positifs:
  - `docs/memoire/tables/table_false_positives.md`.
- Resilience/degradation:
  - `docs/memoire/tables/table_resilience_agent.md`.
- Robustesse:
  - logs corrompus/incomplets conserves;
  - controle multi-format.

Niveau: 80%.

Reste technique:

- completer par une campagne encore plus longue uniquement si un article exige
  des intervalles de confiance ou une analyse de variance plus poussee;
- tests de panne agent ou arret volontaire en conditions controlees;
- faux positifs par periode uniquement si timestamps/labels disponibles;
- scalabilite multi-source plus explicite.

## Exigences Techniques Actuellement Satisfaites

- Parsing multi-format: oui.
- Normalisation commune: oui.
- Detection classique/statistique/IA: oui.
- Modeles legers sauvegardes: oui.
- Routage multi-modeles: oui.
- Agents specialises: oui.
- Communication agentique locale: oui.
- FastAPI V2: oui.
- Redis optionnel: oui.
- Dashboard interactif: oui.
- Decisions analyste/audit: oui.
- Timeline/heatmap: oui, avec correction timestamp cote dashboard.
- Graphiques temps reel: oui.
- Benchmark latence: oui.
- Mesure CPU/RAM: oui.
- Tests datasets publics/reels/simules: oui.
- Robustesse logs incomplets: oui.
- Figures et tableaux techniques: oui.
- Faux positifs par dataset: oui.
- Comparaison operationnelle outils standards: oui.
- Verification assets articles: oui, dans
  `docs/memoire/verification_assets_articles.md`.

## Exigences Techniques Encore Partiellement Couvertes

- Distribution multi-machine: partielle.
- Auto-apprentissage continu: partiel.
- Comparaison stricte fail2ban/OSSEC/Wazuh: partielle.
- Scalabilite longue duree: partielle.
- Resilience par arret d'agent: partielle.
- Faux positifs par periode: partiel, car les metriques disponibles sont
  agregees pour plusieurs datasets.
- Captures dashboard finales: a produire.

## Verdict Technique

Le prototype est suffisamment avance pour soutenir la contribution technique du
memoire. Il couvre le coeur du document directeur: agents specialises,
normalisation multi-format, detection IA legere, dashboard interactif et
evaluation multi-datasets.

La position la plus solide pour la soutenance est:

> Logminer est un prototype multi-agents local, modulaire et extensible,
> validant la faisabilite d'une detection d'anomalies sur journaux heterogenes
> avec routage multi-modeles, correlation, dashboard et premieres mesures de
> latence/ressources. Le deploiement multi-machine, l'auto-apprentissage continu
> et l'industrialisation SOC restent des perspectives techniques.
