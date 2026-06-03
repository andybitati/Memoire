# Pack Articles Scientifiques Selon Le Document Directeur

Date: 2026-06-03

Source: section "Articles scientifiques issus du memoire" du document
directeur extrait dans `docs/memoire/document_directeur_extrait.txt`.

Le document directeur prevoit un cheminement en deux articles:

1. Article 1 pour une conference IEEE, type IJCNN, ICMLA ou AICCSA.
2. Article 2 pour IEEE Access, plus approfondi, oriente architecture
   distribuee, scalabilite, resilience et evaluation experimentale.

Les propositions ci-dessous respectent ce cheminement et l'adaptent aux
resultats reellement disponibles dans le depot.

## Cheminement Officiel

| Periode directeur | Article | Orientation | Livrable |
| --- | --- | --- | --- |
| Mois 6, S23-S24 | Article 1 conference IEEE | Systeme IA + tests | Article pret a soumettre |
| Mois 7, S25-S26 | Article 2 IEEE Access | Architecture distribuee + resilience | Article 2 + memoire pre-final |

## Article 1 - Conference IEEE

Destination visee:

- IJCNN;
- ICMLA;
- AICCSA;
- autre conference IEEE proche: IA appliquee, cybersecurite, systemes
  intelligents.

Titre directeur:

> Distributed Intelligent Agents for Anomaly Detection in System Logs: A
> Lightweight Cybersecurity Framework for SMEs

Titre francais detaille du directeur:

> Conception d'un Systeme Multi-Agents Legers pour la Detection Autonome
> d'Anomalies dans les Journaux Systemes : Une Approche IA Distribuee pour la
> Cybersecurite

Titre recommande avec les resultats actuels:

> Logminer: A Lightweight Multi-Agent Framework for Anomaly Detection in
> Heterogeneous System and Network Logs

Mots-cles:

- anomaly detection;
- log parsing;
- AI agents;
- cyber-audit;
- lightweight AI;
- system monitoring;
- multi-agent architecture;
- cybersecurity.

### Questions De Recherche

Questions du document directeur, adaptees au prototype:

1. Quelle est la performance d'un systeme multi-agents IA pour la detection
   d'anomalies dans des journaux heterogenes?
2. Comment repartir efficacement les taches entre agents autonomes?
3. Quels modeles IA legers conviennent aux environnements a ressources
   limitees?
4. Le systeme peut-il etre adaptatif par routage et specialisation des modeles?
5. Quel est l'impact du volume et du format des logs sur la detection?
6. Comment le systeme se compare-t-il prudemment aux outils traditionnels?

### Contribution A Defendre

- architecture multi-agents locale et modulaire;
- agents collecteur, parseur, routeur, detecteur, correlateur, visualiseur et
  audit;
- normalisation multi-format;
- routage multi-modeles selon la famille de logs;
- dashboard interactif avec validation/rejet et audit trail;
- evaluation initiale sur logs publics, reels et robustesse multi-format.

### Abstract Recommande

> This paper presents Logminer, a lightweight multi-agent framework for
> autonomous anomaly detection in heterogeneous system and network logs. The
> proposed system decomposes the workflow into specialized agents for
> collection, parsing, normalization, model routing, anomaly detection,
> correlation and visualization. Several lightweight machine learning models are
> integrated according to log families, including supervised Random Forests and
> unsupervised Isolation Forest models. Experiments on Windows, Linux/auth,
> Wazuh, HDFS, BGL, CICIDS and UNSW/CIC-DDoS data show that the approach is
> feasible on a local infrastructure while preserving modularity and analyst
> interaction through a web dashboard. The paper discusses the limits of
> non-supervised anomaly candidates, local distribution and comparison with
> standard tools.

### Structure Detaillee

1. Introduction
   - contexte: surcharge des logs, besoin d'autonomie;
   - limites des approches traditionnelles;
   - objectifs et contributions.
2. Related Work
   - detection d'anomalies dans les logs;
   - methodes classiques vs IA;
   - systemes multi-agents en cybersecurite;
   - outils standards: fail2ban, OSSEC, Wazuh.
3. Proposed Multi-Agent Architecture
   - definition des agents;
   - architecture logique et technique;
   - flux de donnees et coordination agentique;
   - V1 CLI, V2 FastAPI, Redis optionnel.
4. Implementation
   - Python, FastAPI, scikit-learn, dashboard web;
   - role des scripts et modules;
   - normalisation et routage multi-modeles.
5. Case Study and Initial Evaluation
   - datasets utilises;
   - resultats de detection;
   - faux positifs;
   - charge CPU/RAM initiale ou multi-cycles courte.
6. Evaluation and Discussion
   - interpretation des performances;
   - avantages de la modularite;
   - comparaison prudente avec outils standards;
   - limites.
7. Conclusion and Future Work
   - synthese;
   - ouverture vers LLM, IoT, distribution multi-machine, apprentissage actif.

### Figures Et Tableaux A Utiliser

Figures:

- `fig_architecture_logminer.svg`;
- `fig_model_portfolio_scale.svg`;
- `fig_robustness_multiformat.svg`;
- `fig_supervised_models_f1.svg`;
- `fig_false_positive_rates.svg`.

Tableaux:

- `table_datasets_scenarios.md`;
- `table_resultats_principaux.md`;
- `table_false_positives.md`;
- `table_comparaison_outils_standards.md`;
- `table_operational_tool_comparison.md`.

### Resultats A Citer

| Element | Valeur |
| --- | --- |
| Linux/auth | RandomForest, F1 = 0.916602 |
| CICIDS2017 | RandomForest, F1 = 0.997163 |
| UNSW/CIC-DDoS | RandomForest, F1 = 0.999965 |
| Wazuh | 122 563 evenements, 3 676 anomalies candidates |
| Robustesse | Apache, CEF/LEEF, CloudTrail, Linux auth, log incomplet conserve |
| Dashboard | alertes, filtres, timeline/heatmap, decisions, audit, CPU/RAM |

### Prudence Scientifique

- parler d'anomalies candidates pour les sorties non supervisees;
- ne pas affirmer une superiorite generale sur les outils traditionnels;
- presenter la comparaison fail2ban-like comme baseline rule-based, pas comme
  fail2ban officiel;
- formuler l'adaptation comme routage multi-modeles et specialisation locale,
  pas comme auto-apprentissage continu complet.

## Article 2 - IEEE Access

Destination visee:

- IEEE Access, revue indexee open access;
- format plus long, plus technique, plus experimental.

Titre directeur:

> Adaptive Multi-Agent AI Framework for Real-Time Log Anomaly Detection in
> Distributed Systems

Titre francais detaille du directeur:

> Detection Adaptative et Scalabilite dans un Systeme Multi-Agent pour l'Audit
> Securitaire des Journaux Systemes : Evaluation Approfondie et Deploiement
> Experimental

Titre recommande avec les resultats actuels:

> Adaptive Multi-Agent Log Anomaly Detection with Lightweight Models:
> Experimental Evaluation, Robustness and Resource Analysis

Mots-cles:

- multi-agent system;
- adaptive AI;
- log anomaly detection;
- unsupervised learning;
- intelligent security framework;
- real-time monitoring;
- scalability;
- resilience.

### Questions De Recherche

Questions du document directeur, adaptees aux preuves disponibles:

1. Quels modeles IA legers sont les plus efficaces pour la detection
   d'anomalies dans les logs?
2. Le systeme peut-il s'adapter a de nouvelles sources par detection de format
   et routage multi-modeles?
3. Quelles performances obtient-on sur differents jeux de donnees publics,
   reels, simules ou bruites?
4. Quel est le niveau de scalabilite observable dans un environnement
   multi-source local?
5. Comment se comporte le systeme sous contraintes: surcharge, logs incomplets,
   erreurs syntaxiques et resilience agentique?
6. Quel est le gain ou la complementarite par rapport aux outils traditionnels?

### Contribution A Defendre

- evaluation approfondie multi-datasets;
- comparaison de modeles classiques, statistiques et IA legere;
- analyse des faux positifs;
- benchmark quasi temps reel;
- campagne CPU/RAM multi-cycles de 30 cycles;
- robustesse sur logs incomplets et multi-format;
- discussion de la scalabilite et de la resilience.

### Abstract Recommande

> This article presents an in-depth evaluation of Logminer, a lightweight
> multi-agent framework for anomaly detection in heterogeneous system and
> network logs. The system integrates specialized agents and lightweight
> machine learning models to parse, normalize, route, detect and correlate log
> events. The evaluation covers supervised datasets such as Linux/auth,
> CICIDS2017 and UNSW/CIC-DDoS, as well as unsupervised or semi-structured
> sources including Wazuh, HDFS, BGL and Windows logs. The best supervised
> results reach F1-scores of 0.916602 on Linux/auth, 0.997163 on CICIDS2017 and
> 0.999965 on UNSW/CIC-DDoS. A 30-cycle resource campaign reports an average
> workflow time of 9.3300 seconds for 8,537 log lines per cycle, while CPU and
> memory are monitored per agent. The discussion addresses robustness,
> scalability, false positives, non-supervised anomaly candidates and the
> complementarity with fail2ban, OSSEC and Wazuh.

### Structure Detaillee

1. Introduction
   - probleme: surcharge, bruit, heterogeneite;
   - objectif: audit intelligent, modulaire, scalable;
   - contributions de l'article.
2. Proposed Multi-Agent System
   - architecture complete;
   - agents et responsabilites;
   - logique d'adaptation locale;
   - synchronisation, message passing, FastAPI, bus JSONL, Redis optionnel.
3. Evaluation Methodology
   - datasets: Windows, Wazuh, Linux/auth, HDFS, BGL, CICIDS, UNSW/CIC-DDoS;
   - metriques: precision, rappel, F1-score, faux positifs, latence, CPU/RAM;
   - cas robustesse: logs incomplets, formats multiples;
   - cas surcharge: 30 cycles `/run/discovered`;
   - limites de comparaison outils.
4. Experimental Results
   - comparaison des modeles IA;
   - resultats supervises;
   - anomalies candidates non supervisees;
   - faux positifs;
   - latence;
   - campagne CPU/RAM;
   - recouvrement Wazuh/Logminer.
5. Deep Discussion
   - scalabilite observee;
   - robustesse en cas d'erreur syntaxique ou source inconnue;
   - resilience agentique: preuve partielle, perspective pour panne agent;
   - integration avec outils tiers: Wazuh, Elastic/Kibana en perspective;
   - limites de generalisation.
6. Perspectives
   - LLM pour explication semantique;
   - deploiement universite/PME;
   - apprentissage actif;
   - distribution multi-machine;
   - MITRE ATT&CK.
7. Conclusion
   - synthese des performances;
   - feuille de route d'industrialisation.

### Figures Et Tableaux A Utiliser

Figures:

- `fig_architecture_logminer.svg`;
- `fig_validation_selection_f1.svg`;
- `fig_supervised_models_f1.svg`;
- `fig_false_positive_rates.svg`;
- `fig_realtime_workflow_latency.svg`;
- `fig_resource_campaign_multicycle.svg`;
- `fig_robustness_multiformat.svg`;
- `fig_wazuh_logminer_overlap.svg`.

Tableaux:

- `table_resultats_principaux.md`;
- `table_datasets_scenarios.md`;
- `table_realtime_benchmark.md`;
- `table_realtime_benchmark_detailed.md`;
- `table_resource_campaign_multicycle.md`;
- `table_false_positives.md`;
- `table_resilience_agent.md`;
- `table_fail2ban_like_baseline.md`;
- `table_wazuh_logminer_summary.md`;
- `table_wazuh_logminer_overlap.md`.

### Resultats A Citer

| Mesure | Valeur |
| --- | --- |
| Linux/auth RandomForest | F1 = 0.916602 |
| CICIDS2017 RandomForest | F1 = 0.997163 |
| UNSW/CIC-DDoS RandomForest | F1 = 0.999965 |
| Wazuh non supervise | 122 563 evenements, 3 676 anomalies candidates |
| Benchmark temps reel | 5 cycles, latence moyenne 10.6473 s |
| Campagne ressources | 30 cycles, workflow moyen 9.3300 s |
| API / Orchestrateur | CPU machine moyen 7.45%, RAM moyenne 187.82 MB |
| Processus Logminer | CPU machine moyen 0.41%, RAM moyenne 495.41 MB |

### Menaces A La Validite

- les mesures CPU/RAM sont locales;
- la scalabilite multi-machine n'est pas encore prouvee strictement;
- la resilience par arret volontaire d'agent reste partielle;
- les anomalies non supervisees ne sont pas des attaques confirmees;
- la baseline fail2ban-like n'est pas une execution officielle de fail2ban;
- OSSEC est une reference fonctionnelle, pas une execution directe.

## Elements Transversaux Prets

- pack memoire: `docs/memoire/pack_redaction_memoire.md`;
- synthese resultats: `docs/memoire/synthese_resultats_pour_memoire_articles.md`;
- fiche reproductibilite: `docs/memoire/fiche_reproductibilite_experimentale.md`;
- tableaux: `docs/memoire/tables/`;
- figures: `docs/memoire/figures/`;
- protocole CPU/RAM: `docs/memoire/protocole_campagne_cpu_ram_multicycles.md`;
- comparaison outils: `docs/memoire/comparaison_scientifique_outils_standards.md`.

## Checklist Avant Soumission

- completer les captures dashboard finales;
- convertir les figures SVG en PNG/PDF selon le template;
- completer modele CPU/RAM totale dans la fiche reproductibilite;
- ajouter commit Git ou archive experimentale;
- separer clairement supervise et non supervise;
- declarer les menaces a la validite;
- verifier le format IEEE des references.

