# Roadmap Des Objectifs 3 A 7

Ce document complete les objectifs deja traites ou en cours:

- objectif 1: collecte, parsing et normalisation des journaux;
- objectif 2: detection d'anomalies et comparaison des approches statistiques/IA;

Les objectifs 3 a 7 ci-dessous servent de feuille de route pour terminer le
prototype et transformer les resultats techniques en memoire defendable.

## Vue Synthese

| Objectif | Theme | Etat actuel | Priorite |
| --- | --- | --- | --- |
| Objectif 3 | Architecture multi-agents | Tres avance | Haute |
| Objectif 4 | Correlation contextuelle et gestion des incidents | Prototype fonctionnel avance | Haute |
| Objectif 5 | Visualisation, supervision et exploitation humaine | Prototype fonctionnel | Moyenne |
| Objectif 6 | Evaluation experimentale complete et entrainement cloud/local | Tres avance | Haute |
| Objectif 7 | Redaction, discussion et perspectives | Phase de redaction a demarrer | Haute |

## Etat General Au 01/06/2026

Le prototype technique est maintenant suffisamment avance pour commencer la
redaction du memoire sur les parties deja realisees. Le projet dispose:

- d'un pipeline de parsing et normalisation multi-sources;
- d'une architecture multi-agents locale;
- d'un routeur multi-modeles par famille de journaux;
- de modeles sauvegardes pour Windows, Linux/auth, Linux/syslog, Wazuh/SIEM,
  CICIDS, UNSW, HDFS, BGL et fallback;
- d'un registre des modeles dans `docs/model_training/model_registry.md`;
- d'experimentations quantitatives sur plusieurs datasets labellises et non
  labellises.

La priorite change donc: il faut maintenant transformer les resultats techniques
en chapitres de memoire, tableaux, figures et discussion critique.

## Strategie De Stabilisation

Le travail est organise en deux versions:

| Version | Objectif | Etat |
| --- | --- | --- |
| V1 - Prototype CLI stable | Conserver une chaine locale reproductible par commandes: parsing, routage, detection, correlation, dashboard et modeles `.joblib` | Socle de secours et version defendable si les evolutions suivantes echouent |
| V2 - Services FastAPI | Exposer les agents avec FastAPI tout en reutilisant la logique CLI stable | API locale disponible; Redis optionnel amorce |
| V3 - Bus Redis/MQTT | Ajouter une file d'evenements pour rapprocher le prototype d'un fonctionnement distribue ou temps reel | Redis Streams integre comme premiere brique; MQTT reste optionnel |

La V1 ne doit pas etre fragilisee par l'ajout premature d'une API. Elle sert de
base de repli pour la soutenance et de point stable pour la redaction. Les V2 et
V3 restent bien dans le perimetre du memoire, mais elles doivent etre developpees
par-dessus la V1 sans casser la chaine CLI deja validee.

## Objectif 3 - Architecture Multi-Agents

But:

> Concevoir une architecture modulaire ou chaque agent est responsable d'une
> etape: collecte, parsing, normalisation, detection, correlation et
> visualisation.

Ce qui existe deja:

- `docs/architecture/README.md`;
- bus local JSONL avec `src/logminer/agents/bus.py`;
- orchestrateur local `src/logminer/agents/orchestrator.py`;
- agents parseur, detecteur, correlateur et visualiseur;
- presentation humaine du flux agents dans le dashboard;
- explication LLM/local des resultats dans le dashboard.
- routeur multi-modeles `src/logminer/agents/model_router.py`;
- registre des modeles entraines et reutilisables;
- separation des familles `windows`, `wazuh`, `network_cicids`, `network`,
  `linux_auth`, `linux`, `hdfs`, `bgl` et `fallback`.

Ce qui manque encore pour la V1:

- formaliser les messages agents comme contrat stable.
- formaliser l'agent explicateur et l'agent superviseur comme roles
  architecturaux inspires des architectures IDS multi-agents.

Ce qui passe en V2/V3:

- exposer les agents comme services FastAPI;
- remplacer ou completer le bus JSONL local par Redis/MQTT;
- definir un deploiement distribue cloud/local.

Livrables attendus:

- architecture cible dans le memoire;
- diagrammes logique et sequence;
- specification des messages agents;
- choix justifie entre prototype local et services distribues.

## Objectif 4 - Correlation Contextuelle

But:

> Regrouper les anomalies isolees en incidents exploitables a partir du temps,
> de la source, de la machine, de l'utilisateur, de la categorie et de la
> severite.

Ce qui existe deja:

- `src/logminer/agents/correlator.py`;
- production de `data/processed/incidents.csv`;
- regroupement par fenetre temporelle;
- resume humain court par incident;
- priorite d'incident (`priority`), score explicable (`priority_score`) et
  justification (`rationale`);
- regroupement plus lisible des incidents reseau avec `proto` et `dst_port`;
- affichage des incidents dans le dashboard.

Ce qui manque encore:

- enrichir les regles de correlation;
- relier un incident a ses anomalies sources;
- documenter les limites de la correlation actuelle.

Livrables attendus:

- `incidents.csv` enrichi avec priorite et justification;
- section memoire sur la correlation;
- exemples d'incidents interpretes.

## Objectif 5 - Visualisation Et Supervision

But:

> Fournir une interface permettant a un analyste de comprendre les evenements,
> les anomalies, les incidents et la communication entre agents.

Ce qui existe deja:

- dashboard Streamlit;
- dashboard web responsive dans `web/dashboard`;
- statistiques globales;
- tableaux evenements/anomalies;
- incidents correles;
- flux agents lisible;
- synthese des validations ML.
- panneau d'explication analyste avec LLM optionnel et repli local.

Ce qui manque encore:

- ajouter une vue detail incident;
- afficher les anomalies sources d'un incident;
- ajouter des filtres temporels;
- exposer les performances des modeles sous forme de tableau dedie;
- relier l'explication aux incidents, aux scores et aux agents contributeurs;
- verifier l'ergonomie sur plusieurs tailles d'ecran.

Livrables attendus:

- captures d'ecran pour le memoire;
- scenario de demonstration;
- section memoire sur l'exploitation humaine du prototype.

## Objectif 6 - Evaluation Experimentale

But:

> Evaluer le systeme sur plusieurs sources de journaux et mesurer la qualite de
> detection avec des indicateurs quantitatifs.

Ce qui existe deja:

- validation HDFS;
- validation BGL;
- validation Windows simule;
- `precision`, `recall`, `f1`;
- `accuracy`, `specificity`;
- matrice de confusion `tp/fp/fn/tn`;
- synthese `data/processed/validation_summary.csv`;
- sauvegarde de modele `joblib` via `src/logminer/agents/detector.py`.
- entrainement cloud Google Colab sur donnees Drive;
- modele `models/isolation_forest_colab.joblib` recupere localement;
- inference locale validee sur `data/processed/windows_copies_pipeline.csv`;
- correlation des anomalies Colab en `data/processed/incidents_from_colab_model.csv`.
- inference administrateur sur `Security.evtx`: `32583` evenements, `203`
  anomalies candidates, `87` incidents correles;
- test reseau initial sur `outside_tcp_dump_part001.csv`: `100000` evenements,
  `0` anomalie avec le modele Colab generaliste, puis `1998` anomalies et `22`
  incidents avec un Isolation Forest local dedie.
- modele RandomForest reseau UNSW/CIC-DDoS avec split 80/20:
  F1-score `0.999965`;
- modele RandomForest CICIDS/MachineLearningCVE:
  F1-score `0.997163`;
- modele RandomForest Linux/auth:
  F1-score interne `0.916602`;
- modele Isolation Forest Wazuh/SIEM:
  `122563` evenements normalises et `3676` anomalies candidates;
- registre des artefacts et modeles dans
  `docs/model_training/model_registry.md`;
- sauvegarde des nouveaux modeles dans GitHub, avec Git LFS pour le modele
  Linux/auth.

Ce qui manque encore:

- consolider les resultats dans un tableau final unique;
- distinguer clairement les evaluations supervisees et non supervisees;
- documenter les limites du transfert entre datasets, par exemple UNSW vers
  CICIDS;
- comparer les temps d'execution et la complexite;
- ajouter une mesure operationnelle de faux positifs par periode lorsque les
  timestamps le permettent;
- interpreter les ecarts entre HDFS et BGL.

Resultat cloud principal du 29/05/2026:

```text
Environnement: Google Colab + Google Drive
Modele: Isolation Forest
Evenements d'entrainement: 287862
Colonnes: 79
Contamination: 0.02
Anomalies cloud: 5754
Inference locale Windows: 61313 evenements, 81 anomalies
Correlation locale: 71 incidents
```

Livrables attendus:

- tableaux de resultats;
- artefacts modeles reutilisables;
- interpretation des meilleurs modeles;
- discussion sur les limites experimentales.

## Objectif 7 - Redaction, Discussion Et Perspectives

But:

> Transformer le prototype, les resultats et les limites en memoire complet:
> methodologie, implementation, experimentations, discussion et perspectives.

Ce qui existe deja:

- documentation objectif 2;
- documentation objectif 3;
- references bibliographiques dans `docs/references`;
- exploitation du document de cadrage dans `docs/memoire/exploitation_references.md`;
- resultats experimentaux dans `data/processed`.
- plan de memoire dans `docs/memoire/plan.md`;
- registre des modeles dans `docs/model_training/model_registry.md`;
- documentation des entrainements dans `docs/model_training/README.md`.

Ce qui manque encore:

- chapitre d'etat de l'art;
- chapitre methodologie;
- chapitre implementation;
- chapitre resultats;
- chapitre discussion;
- conclusion et perspectives;
- integration propre des references.
- discussion critique sur les limites des datasets, des LLMs et du deploiement
  distribue.

Livrables attendus:

- `docs/memoire/plan.md`;
- tableaux et figures prets a inserer;
- sections redigees progressivement.

## Ordre De Travail Recommande

1. Stabiliser et documenter la V1 CLI existante comme point de sauvegarde.
2. Rediger le chapitre 1: introduction, contexte, problematique, objectifs.
3. Rediger le chapitre 3: methodologie et architecture multi-agents.
4. Rediger le chapitre 4: implementation du prototype Logminer V1.
5. Rediger le chapitre 5: experimentations et resultats, avec les tableaux de
   modeles.
6. Consolider la V2 FastAPI + Redis locale, en conservant la compatibilite CLI.
7. Completer le chapitre 2: etat de l'art, en l'appuyant sur les references
   deja rassemblees.
8. Rediger le chapitre 6: discussion critique, limites et evolution V2/V3.
9. Finaliser le chapitre 7: conclusion et perspectives.
10. En parallele: capturer le dashboard et produire les figures/tableaux finaux.
