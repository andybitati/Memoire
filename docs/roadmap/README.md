# Roadmap Des Objectifs 3 A 7

Ce document complete les objectifs deja traites ou en cours:

- objectif 1: collecte, parsing et normalisation des journaux;
- objectif 2: detection d'anomalies et comparaison des approches statistiques/IA;

Les objectifs 3 a 7 ci-dessous servent de feuille de route pour terminer le
prototype et transformer les resultats techniques en memoire defendable.

## Vue Synthese

| Objectif | Theme | Etat actuel | Priorite |
| --- | --- | --- | --- |
| Objectif 3 | Architecture multi-agents | Avance | Haute |
| Objectif 4 | Correlation contextuelle et gestion des incidents | Prototype fonctionnel | Haute |
| Objectif 5 | Visualisation, supervision et exploitation humaine | Prototype fonctionnel | Haute |
| Objectif 6 | Evaluation experimentale complete et entrainement cloud | Entrainement Colab valide | Haute |
| Objectif 7 | Redaction, discussion et perspectives | A structurer | Haute |

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

Ce qui manque encore:

- exposer les agents comme services FastAPI si necessaire;
- definir une strategie de deploiement cloud/local;
- documenter le versionnement des modeles et des donnees;
- formaliser les messages agents comme contrat stable.
- formaliser l'agent explicateur et l'agent superviseur comme roles
  architecturaux inspires des architectures IDS multi-agents.

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
- distinguer incident faible, moyen, critique;
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

Ce qui manque encore:

- evaluer des echantillons plus grands;
- ajouter un split train/test lorsque le modele le permet;
- exploiter UNSW-NB15 lorsque le telechargement sera termine;
- elargir les tests `outside_tcp_dump` a plus de lignes et a un meilleur
  enrichissement semantique reseau;
- entrainer ou comparer d'autres modeles principaux sur le cloud si necessaire;
- documenter le versionnement des artefacts `models/*.joblib`;
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

Ce qui manque encore:

- plan detaille du memoire;
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

1. Finaliser objectif 4: enrichir la correlation, la priorisation et les causes probables.
2. Finaliser objectif 5: rendre le dashboard demonstrable, explicable et capturable.
3. Finaliser objectif 6: entrainer sur le cloud, sauvegarder les modeles joblib et stabiliser les tableaux.
4. Finaliser objectif 7: rediger chapitre par chapitre en s'appuyant sur `docs/memoire/exploitation_references.md`.
