# Plan De Travail Du Memoire

Titre provisoire:

> Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et
> Reseaux a l'aide d'Agents Intelligents Multi-Taches

Ce plan relie les objectifs techniques du projet aux chapitres du memoire.

## Chapitre 1 - Introduction Generale

Objectifs couverts:

- presenter le contexte de la journalisation systeme et reseau;
- expliquer la difficulte de detecter manuellement les anomalies;
- introduire l'interet d'une approche multi-agents;
- formuler la problematique, les hypotheses et les objectifs.

Elements disponibles:

- titre et sujet du TFE;
- prototype Logminer;
- pipeline de collecte et d'analyse.
- architecture multi-agents deja implementee;
- plusieurs familles de journaux exploitees: Windows, Linux, Wazuh, HDFS, BGL,
  UNSW et CICIDS.

Reste a rediger:

- contexte;
- problematique;
- objectifs 1 a 7;
- methodologie generale.

Priorite de redaction:

- expliquer pourquoi la detection manuelle dans des journaux heterogenes est
  difficile;
- presenter l'hypothese centrale: une architecture multi-agents avec modeles
  specialises par famille de logs ameliore l'exploitation des anomalies;
- annoncer les contributions: pipeline Logminer, routeur multi-modeles,
  correlation, dashboard et evaluation multi-datasets.

## Chapitre 2 - Etat De L'Art

Objectifs couverts:

- objectif 2: approches de detection d'anomalies.

Elements disponibles:

- `docs/references/nistspecialpublication800-92.pdf`;
- `docs/references/rfc5424.txt.pdf`;
- `docs/references/Deep Learning for Anomaly Detection in Log Data.pdf`;
- `docs/memoire/References_et_ressources_memoire_ANDY_BITATI.pdf`;
- `docs/memoire/exploitation_references.md`;
- `docs/anomaly_detection/README.md`.

Reste a rediger:

- journalisation et formats de logs;
- SIEM et supervision;
- detection statistique;
- machine learning non supervise;
- deep learning pour logs;
- architectures multi-agents.

Priorite de redaction:

- rediger d'abord les sections directement utiles au prototype:
  journalisation, SIEM/Wazuh, detection d'anomalies, Isolation Forest,
  RandomForest, architectures multi-agents;
- garder le deep learning comme comparaison et perspective, sans en faire le
  coeur du prototype.

## Chapitre 3 - Methodologie Et Architecture Proposee

Objectifs couverts:

- objectif 1: collecte, parsing, normalisation;
- objectif 3: architecture multi-agents.

Elements disponibles:

- `docs/architecture/README.md`;
- `docs/memoire/exploitation_references.md`;
- `src/logminer/pipeline.py`;
- `src/logminer/agents/bus.py`;
- `src/logminer/agents/orchestrator.py`.
- `src/logminer/agents/model_router.py`;
- registre des modeles dans `docs/model_training/model_registry.md`.

Reste a rediger:

- schema general du systeme;
- role de chaque agent;
- contrat de donnees normalisees;
- choix du bus JSONL pour le prototype;
- justification de la modularite.

Elements a presenter:

- flux general: collecte -> parsing -> normalisation -> routage modele ->
  detection -> correlation -> visualisation;
- agents: collecteur, parseur, normaliseur, routeur, detecteur, correlateur,
  visualiseur, explicateur/superviseur en perspective;
- contrat CSV commun: `timestamp_iso`, `severity`, `event`, `source`, `host`,
  `user`, `src_ip`, `dst_ip`, `category`, `message`;
- strategie multi-modeles par famille de logs.

## Chapitre 4 - Implementation Du Prototype

Objectifs couverts:

- objectif 1: implementation pipeline;
- objectif 2: implementation detection;
- objectif 4: correlation contextuelle;
- objectif 5: visualisation.

Elements disponibles:

- collecteur Windows;
- parseur Windows Event;
- normalisation;
- features ML;
- detecteurs;
- correlateur;
- dashboards Streamlit et web.
- scripts de preparation Linux/auth, Wazuh et CICIDS;
- routeur multi-modeles;
- artefacts `.joblib` sauvegardes;
- Git LFS pour le modele Linux/auth.

Reste a rediger:

- structure du code;
- choix techniques;
- exemples de commandes;
- limites d'implementation.

Sections recommandees:

1. Structure du projet et dossiers principaux.
2. Pipeline de normalisation Logminer.
3. Extraction/collecte Windows et traitement des datasets bruts.
4. Construction des features ML.
5. Routeur multi-modeles.
6. Entrainement et sauvegarde des modeles.
7. Correlation et priorisation des incidents.
8. Dashboard et exploitation humaine.

## Chapitre 5 - Experimentations Et Resultats

Objectifs couverts:

- objectif 6: evaluation experimentale.

Elements disponibles:

- `data/processed/model_comparison.csv`;
- `data/processed/validation_hdfs_metrics.csv`;
- `data/processed/validation_bgl_metrics.csv`;
- `data/processed/validation_summary.csv`;
- scripts de preparation et synthese.
- sauvegarde de modeles avec `joblib` pour entrainement cloud.
- `docs/model_training/model_registry.md`;
- `docs/model_training/random_forest_unsw_80_20_analysis.md`;
- `data/processed/random_forest_linux_auth_metrics.csv`;
- `data/processed/random_forest_network_cicids_metrics.csv`;
- resultats Wazuh dans `data/processed/wazuh_months_anomalies.csv`;
- modele RandomForest UNSW/CIC-DDoS;
- modele RandomForest CICIDS2017;
- modele RandomForest Linux/auth;
- modele Isolation Forest Wazuh;
- modeles Isolation Forest HDFS, BGL, Windows, Linux et fallback.

Reste a rediger:

- protocole experimental;
- description des datasets Windows, Linux/auth, Wazuh, HDFS, BGL, UNSW et
  CICIDS;
- tableaux precision, recall, F1;
- protocole d'entrainement cloud et reutilisation locale des modeles;
- analyse comparative des modeles;
- interpretation des performances.
- ajout des faux positifs par periode lorsque les timestamps et labels sont
  disponibles.

Tableau de resultats a construire:

| Famille | Dataset | Modele | Type | Resultat principal |
| --- | --- | --- | --- | --- |
| Windows | Security/Application/System | Isolation Forest | Non supervise | anomalies et incidents correles |
| Wazuh | January/October/December exports | Isolation Forest | Non supervise | 122563 evenements, 3676 anomalies |
| Linux/auth | linux_auth_logs_* | RandomForest | Supervise | F1 interne 0.916602 |
| CICIDS | MachineLearningCVE | RandomForest | Supervise | F1 0.997163 |
| UNSW/CIC-DDoS | UNSWNB15/CIC-DDoS | RandomForest | Supervise | F1 0.999965 |
| HDFS | HDFS logs | Isolation Forest | Non supervise | validation existante |
| BGL | BlueGene/L | Isolation Forest | Non supervise | validation existante |

Point important:

- separer clairement les resultats supervises, ou les labels permettent une
  evaluation precision/recall/F1, et les resultats non supervises, ou les
  anomalies sont des candidats a interpreter.

## Chapitre 6 - Discussion

Objectifs couverts:

- objectif 7: discussion et limites.

Elements disponibles:

- limites connues des echantillons equilibres;
- difference de performance HDFS/BGL;
- contraintes Windows et droits administrateur;
- prototype local non encore distribue via FastAPI/Redis.
- transfert difficile entre datasets reseau, par exemple UNSW vers CICIDS;
- faux positifs observes sur Linux/auth selon la distribution;
- necessite d'un routeur multi-modeles pour eviter les confusions de formats;
- dependance aux labels pour les modeles supervises;
- limites des modeles non supervises qui detectent la rarete plus que
  l'attaque prouvee.

Reste a rediger:

- forces du prototype;
- limites experimentales;
- limites de generalisation;
- limites de performance;
- ameliorations possibles.

Angles de discussion:

- l'approche multi-modeles est plus pertinente qu'un modele global unique;
- les performances tres elevees sur certains datasets doivent etre interpretees
  avec prudence a cause du desequilibre et de la distribution des donnees;
- Wazuh fournit une couche SIEM riche, mais les alertes non supervisees restent
  des signaux candidats;
- le prototype est local et modulaire, mais peut evoluer vers FastAPI, Redis ou
  MQTT pour un deploiement distribue.

## Chapitre 7 - Conclusion Et Perspectives

Objectifs couverts:

- objectif 7: conclusion finale.

Reste a rediger:

- bilan objectif par objectif;
- contribution principale;
- perspectives: FastAPI, Redis/MQTT, temps reel, datasets reseau,
  enrichissement des features, integration SOC/SIEM.

Message final a faire ressortir:

- le travail propose une architecture autonome et modulaire de detection
  d'anomalies;
- la contribution principale est le couplage entre agents specialises,
  normalisation commune, routage par famille de journaux et modeles adaptes;
- les resultats montrent une faisabilite technique sur des sources heterogenes,
  tout en laissant ouvertes les questions de generalisation, de temps reel et
  d'integration SOC.

## Tableau De Suivi Des Objectifs

| Objectif | Statut | Preuve actuelle | Prochaine action |
| --- | --- | --- | --- |
| 1. Collecter, parser et normaliser | Tres avance | Pipeline Logminer, Windows, Wazuh, Linux/auth, reseau | Rediger methodologie |
| 2. Detecter et comparer les anomalies | Tres avance | Modeles joblib, registres, metriques supervisees | Consolider tableaux |
| 3. Concevoir l'architecture multi-agents | Tres avance | `docs/architecture/README.md`, bus, orchestrateur, routeur | Rediger chapitre 3 |
| 4. Correler les anomalies en incidents | Avance | `correlator.py`, incidents, priorites | Documenter limites |
| 5. Visualiser et superviser | Avance | `web/dashboard`, Streamlit, explication locale/LLM | Captures et scenario demo |
| 6. Evaluer experimentalement | Tres avance | HDFS, BGL, Windows, UNSW, CICIDS, Linux/auth, Wazuh | Tableau final et analyse |
| 7. Rediger et discuter | A demarrer maintenant | Plan, docs, resultats, references | Redaction chapitre par chapitre |

## Ordre De Redaction A Partir De Maintenant

1. Chapitre 1 - Introduction generale.
2. Chapitre 3 - Methodologie et architecture, car la matiere est deja claire.
3. Chapitre 4 - Implementation du prototype.
4. Chapitre 5 - Experimentations et resultats.
5. Chapitre 6 - Discussion.
6. Chapitre 2 - Etat de l'art, a consolider avec les references.
7. Chapitre 7 - Conclusion et perspectives.
