# Roadmap Alignee Sur Le Document Directeur

Ce document suit la numerotation officielle du PDF directeur:

`docs/memoire/Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et Reseaux a l'aide d'Agents Intelligents Multi-Taches.pdf`

La roadmap interne doit rester subordonnee a ce document. La correlation n'est
donc plus un objectif autonome: elle est traitee comme un role d'agent dans
l'objectif 3 et comme une fonctionnalite exploitee dans le dashboard.

## Vue Synthese

| Objectif | Theme directeur | Etat actuel | Priorite |
| --- | --- | --- | --- |
| Objectif 1 | Identifier, categoriser et structurer les journaux systemes et reseaux | Tres avance | Haute |
| Objectif 2 | Etudier et comparer les approches de detection d'anomalies | Tres avance | Haute |
| Objectif 3 | Concevoir une architecture distribuee et modulaire d'agents IA specialises | Conforme prototype, distribution multi-machine a discuter | Haute |
| Objectif 4 | Integrer des modeles IA legers pour une detection adaptative et quasi temps reel | Conforme prototype | Haute |
| Objectif 5 | Developper un dashboard visuel interactif pour explorer les anomalies | Conforme prototype | Haute |
| Objectif 6 | Tester sur logs simules, reels et jeux de donnees publics | Tres avance | Haute |
| Objectif 7 | Evaluer precision, rappel, F1, latence, charge et extensibilite | Conforme prototype, industrialisation a discuter | Haute |

## Etat General Au 02/06/2026

Le prototype technique est suffisamment avance pour alimenter les chapitres de
conception, implementation et evaluation. Le projet dispose deja:

- d'un pipeline de parsing et normalisation multi-sources;
- d'une architecture agents locale avec API FastAPI, bus JSONL et Redis
  optionnel;
- d'un routeur multi-modeles par famille de journaux;
- de modeles sauvegardes pour Windows, Wazuh, Linux/auth, Linux/syslog, CICIDS,
  UNSW, HDFS, BGL et fallback;
- d'un dashboard web et d'un dashboard Streamlit;
- d'experimentations quantitatives sur datasets labellises et non labellises.

La priorite devient la mise en conformite avec le document directeur: chaque
fonctionnalite doit pouvoir etre rattachee a l'un des sept objectifs officiels.

## Strategie De Stabilisation

| Version | Role | Etat |
| --- | --- | --- |
| V1 - Prototype CLI stable | Chaine reproductible: parsing, detection, correlation, dashboard et modeles `.joblib` | Socle de soutenance |
| V2 - Services FastAPI | Exposer les agents via REST tout en reutilisant la V1 | Disponible localement |
| V3 - Bus Redis/MQTT | Rapprocher le prototype d'un fonctionnement distribue/quasi temps reel | Redis Streams amorce, MQTT optionnel |

La V1 reste le filet de securite. FastAPI, Redis et les evolutions temps reel
doivent renforcer la demonstration sans rendre la chaine CLI instable.

## Objectif 1 - Logs, Parsing Et Normalisation

But directeur:

> Identifier, categoriser et structurer les differents types de journaux
> systemes et reseaux pertinents pour l'analyse de securite.

Ce qui existe deja:

- parseurs Windows Event, syslog, Apache, HDFS, BGL, CEF/LEEF, CloudTrail,
  JSONL, tcpdump texte et pcap;
- detection de format dans `src/logminer/detectors/file_detector.py`;
- pipeline de normalisation dans `src/logminer/pipeline.py`;
- schema commun dans `src/logminer/schema/columns.py`;
- collecte Windows via `scripts/collect_windows_events.ps1`;
- normalisation Wazuh, Linux/auth et reseau;
- taxonomie prete a integrer dans `docs/memoire/taxonomie_journaux.md`.

Ce qui manque encore:

- documenter les limites des formats incomplets ou corrompus;
- ajouter quelques exemples bruts -> normalises en annexe.

Livrables attendus:

- tableau de typologie des journaux;
- schema de normalisation;
- exemples de parsing multi-format.

## Objectif 2 - Comparaison Des Techniques D'Anomalie

But directeur:

> Etudier, comparer et choisir des approches classiques et intelligentes pour la
> detection d'anomalies dans les journaux.

Ce qui existe deja:

- documentation comparative dans `docs/anomaly_detection/README.md`;
- methodes statistiques et heuristiques: z-score, histogramme, entropie;
- methodes IA legeres: Isolation Forest, k-Means, One-Class SVM, LOF,
  Autoencoder MLP, LSTM TensorFlow/PyTorch experimental;
- metriques precision, recall, F1, accuracy, specificity, temps et memoire;
- synthese `data/processed/validation_summary.csv`.

Ce qui manque encore:

- consolider une grille comparative finale;
- distinguer clairement modeles supervises, non supervises et deep learning
  experimental;
- justifier pourquoi les modeles legers sont privilegies pour les machines non
  specialisees.

Livrables attendus:

- tableau comparatif des approches;
- justification des modeles retenus;
- definition des metriques utilisees.

## Objectif 3 - Architecture Multi-Agents Distribuee

But directeur:

> Concevoir une architecture distribuee et modulaire basee sur des agents IA
> specialises pour la surveillance et l'analyse des logs.

Ce qui existe deja:

- agents collecteur, parseur, detecteur, correlateur, visualiseur,
  orchestrateur, routeur, runtime et privilege;
- bus local JSONL dans `src/logminer/agents/bus.py`;
- Redis Streams optionnel pour les evenements agents;
- contrat formel de messages agents dans `docs/architecture/message_contract.md`;
- API FastAPI V2 dans `src/logminer/api.py`;
- dashboard affichant flux agents, audit et etat des services;
- correlation contextuelle dans `src/logminer/agents/correlator.py`.

Ce qui manque encore:

- produire des captures ou schemas finaux de composants et de sequence pour le
  document imprime;
- expliciter dans la redaction ce qui est distribue localement aujourd'hui et
  ce qui reste une perspective multi-machine.

Livrables attendus:

- diagrammes UML ou schemas equivalents;
- specification des agents et de leurs entrees/sorties;
- protocole d'interaction REST, JSONL et Redis.

## Objectif 4 - IA Legere, Adaptative Et Quasi Temps Reel

But directeur:

> Integrer des modeles d'intelligence artificielle legers pour la detection
> d'anomalies dans les flux de logs en temps quasi reel.

Ce qui existe deja:

- Isolation Forest pour Windows, Wazuh, HDFS, BGL, Linux/syslog et fallback;
- RandomForest supervise pour Linux/auth, CICIDS et UNSW/CIC-DDoS;
- routeur multi-modeles dans `src/logminer/agents/model_router.py`;
- artefacts `.joblib` dans `models/`;
- registre dans `docs/model_training/model_registry.md`;
- workflow autonome via FastAPI et dashboard;
- rafraichissement dashboard toutes les 5 secondes avec relance automatique du
  workflow lorsqu'aucune analyse n'est deja en cours;
- benchmark `scripts/benchmark_realtime_workflow.py` pour mesurer la latence de
  cycles quasi temps reel et produire
  `data/processed/realtime_workflow_benchmark.csv`.

Ce qui manque encore:

- integrer les valeurs du benchmark final dans le chapitre d'evaluation;
- eviter de presenter les modeles non supervises comme preuves d'attaque:
  ce sont des anomalies candidates.

Livrables attendus:

- tableau des modeles par famille de logs;
- benchmark de detection locale;
- explication des limites de l'adaptation automatique.

## Objectif 5 - Dashboard Visuel Interactif

But directeur:

> Developper une interface utilisateur visuelle permettant d'explorer les
> anomalies detectees de facon comprehensible.

Ce qui existe deja:

- dashboard Streamlit dans `src/logminer/agents/dashboard.py`;
- dashboard web dans `web/dashboard`;
- vues globale, resultats et technique;
- statistiques evenements, anomalies et incidents;
- tableaux incidents, anomalies candidates et evenements normalises;
- filtres par hote, severite, categorie, source et recherche texte;
- section d'analyse temporelle avec timeline et heatmap;
- auto-refresh temps reel toutes les 5 secondes au plus, couple a l'analyse
  automatique;
- flux agents, Redis, audit, ressources et validation modeles;
- explication analyste locale/LLM optionnelle;
- validation, rejet et reclassement d'alertes avec journal d'audit;
- vue detail incident reliant fenetre, contexte, justification et anomalies
  sources probables;
- export CSV des anomalies, evenements et details incident depuis l'interface.

Ce qui manque encore:

- verifier l'ergonomie sur captures desktop et mobile.

Livrables attendus:

- captures dashboard;
- scenario de demonstration;
- description des interactions utilisateur.

## Objectif 6 - Tests Sur Donnees Variees

But directeur:

> Tester le systeme sur des jeux de donnees varies: logs simules, journaux
> reels et attaques connues.

Ce qui existe deja:

- journaux Windows locaux et Security.evtx admin;
- Wazuh/SIEM;
- HDFS et BGL;
- CICIDS2017 / MachineLearningCVE;
- UNSW / CIC-DDoS;
- Linux/auth;
- scripts de preparation et injection d'anomalies;
- resultats non supervises et supervises;
- controle `scripts/run_robustness_scalability_checks.py` sur plusieurs formats
  synthetiques et sur un log corrompu/incomplet.

Ce qui manque encore:

- documenter clairement les scenarios testes;
- ajouter ou cadrer la comparaison avec fail2ban, OSSEC ou Wazuh;
- distinguer tests reels, simules, injectes et datasets publics.

Livrables attendus:

- tableau des datasets;
- protocole experimental;
- comparaison qualitative avec outils standards.

## Objectif 7 - Evaluation Globale

But directeur:

> Evaluer globalement les performances, la latence, la precision et la capacite
> d'extension du systeme multi-agents IA developpe.

Ce qui existe deja:

- precision, recall, F1, accuracy, specificity et matrices de confusion;
- duree et pic memoire dans les validations;
- latence par workflow dans les reponses FastAPI et le dashboard;
- monitoring CPU/RAM par agent Logminer via l'API et le dashboard;
- benchmark quasi temps reel exportable par
  `scripts/benchmark_realtime_workflow.py`;
- controle robustesse/scalabilite exportable par
  `scripts/run_robustness_scalability_checks.py`;
- resultats principaux:
  - Linux/auth: F1 `0.916602`;
  - CICIDS: F1 `0.997163`;
  - UNSW/CIC-DDoS: F1 `0.999965`;
  - Wazuh: `122563` evenements, `3676` anomalies candidates.

Ce qui manque encore:

- consolider les mesures de latence par agent et par workflow dans le tableau
  final du memoire;
- ajouter faux positifs par periode lorsque les timestamps/labels le permettent;
- cadrer l'arret volontaire d'un agent comme limite/perspective
  d'industrialisation.

Livrables attendus:

- tableau complet de performances;
- analyse CPU/RAM par agent et latence;
- discussion des limites et recommandations d'industrialisation.

## Ordre De Travail Recommande

1. Harmoniser `docs/memoire/plan.md` avec les sept objectifs directeurs.
2. Regenerer les incidents avec le correlateur actuel pour inclure priorite et
   justification.
3. Produire les captures du dashboard objectif 5: timeline/heatmap,
   auto-refresh 5 secondes, decisions analyste, details et exports.
4. Executer le benchmark de latence par workflow pour l'objectif 7.
5. Rediger chapitre 3: architecture agents, communication et correlation.
6. Rediger chapitre 4: implementation technique et dashboard.
7. Rediger chapitre 5: evaluation, datasets, metriques et limites.
8. Completer chapitre 2 avec la grille comparative des techniques.
9. Finaliser discussion, conclusion et perspectives.
