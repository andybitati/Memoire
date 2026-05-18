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

Reste a rediger:

- contexte;
- problematique;
- objectifs 1 a 7;
- methodologie generale.

## Chapitre 2 - Etat De L'Art

Objectifs couverts:

- objectif 2: approches de detection d'anomalies.

Elements disponibles:

- `docs/references/nistspecialpublication800-92.pdf`;
- `docs/references/rfc5424.txt.pdf`;
- `docs/references/Deep Learning for Anomaly Detection in Log Data.pdf`;
- `docs/anomaly_detection/README.md`.

Reste a rediger:

- journalisation et formats de logs;
- SIEM et supervision;
- detection statistique;
- machine learning non supervise;
- deep learning pour logs;
- architectures multi-agents.

## Chapitre 3 - Methodologie Et Architecture Proposee

Objectifs couverts:

- objectif 1: collecte, parsing, normalisation;
- objectif 3: architecture multi-agents.

Elements disponibles:

- `docs/architecture/README.md`;
- `src/logminer/pipeline.py`;
- `src/logminer/agents/bus.py`;
- `src/logminer/agents/orchestrator.py`.

Reste a rediger:

- schema general du systeme;
- role de chaque agent;
- contrat de donnees normalisees;
- choix du bus JSONL pour le prototype;
- justification de la modularite.

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

Reste a rediger:

- structure du code;
- choix techniques;
- exemples de commandes;
- limites d'implementation.

## Chapitre 5 - Experimentations Et Resultats

Objectifs couverts:

- objectif 6: evaluation experimentale.

Elements disponibles:

- `data/processed/model_comparison.csv`;
- `data/processed/validation_hdfs_metrics.csv`;
- `data/processed/validation_bgl_metrics.csv`;
- `data/processed/validation_summary.csv`;
- scripts de preparation et synthese.

Reste a rediger:

- protocole experimental;
- description des datasets Windows, HDFS et BGL;
- tableaux precision, recall, F1;
- analyse comparative des modeles;
- interpretation des performances.

## Chapitre 6 - Discussion

Objectifs couverts:

- objectif 7: discussion et limites.

Elements disponibles:

- limites connues des echantillons equilibres;
- difference de performance HDFS/BGL;
- contraintes Windows et droits administrateur;
- prototype local non encore distribue via FastAPI/Redis.

Reste a rediger:

- forces du prototype;
- limites experimentales;
- limites de generalisation;
- limites de performance;
- ameliorations possibles.

## Chapitre 7 - Conclusion Et Perspectives

Objectifs couverts:

- objectif 7: conclusion finale.

Reste a rediger:

- bilan objectif par objectif;
- contribution principale;
- perspectives: FastAPI, Redis/MQTT, temps reel, datasets reseau,
  enrichissement des features, integration SOC/SIEM.

## Tableau De Suivi Des Objectifs

| Objectif | Statut | Preuve actuelle | Prochaine action |
| --- | --- | --- | --- |
| 1. Collecter, parser et normaliser | Avance | `windows_copies_pipeline.csv` | Stabiliser autres parseurs |
| 2. Detecter et comparer les anomalies | Tres avance | `validation_summary.csv` | Elargir validation |
| 3. Concevoir l'architecture multi-agents | Avance | `docs/architecture/README.md` | FastAPI optionnel |
| 4. Correler les anomalies en incidents | Partiel | `incidents.csv` | Priorite et justification |
| 5. Visualiser et superviser | Partiel avance | `web/dashboard` | Vue detail incident |
| 6. Evaluer experimentalement | Partiel avance | HDFS/BGL metrics | Split train/test, reseau |
| 7. Rediger et discuter | Debut | docs existantes | Redaction chapitre par chapitre |

