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
| Objectif 6 | Evaluation experimentale complete et entrainement cloud | Validation initiale faite | Haute |
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
- presentation humaine du flux agents dans le dashboard.

Ce qui manque encore:

- exposer les agents comme services FastAPI si necessaire;
- definir une strategie de deploiement cloud/local;
- documenter le versionnement des modeles et des donnees;
- formaliser les messages agents comme contrat stable.

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
- affichage des incidents dans le dashboard.

Ce qui manque encore:

- enrichir les regles de correlation;
- ajouter un score de priorite d'incident;
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

Ce qui manque encore:

- ajouter une vue detail incident;
- afficher les anomalies sources d'un incident;
- ajouter des filtres temporels;
- exposer les performances des modeles sous forme de tableau dedie;
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
- `precision`, `recall`, `f1`;
- `accuracy`, `specificity`;
- matrice de confusion `tp/fp/fn/tn`;
- synthese `data/processed/validation_summary.csv`;
- sauvegarde de modele `joblib` via `src/logminer/agents/detector.py`.

Ce qui manque encore:

- evaluer des echantillons plus grands;
- ajouter un split train/test lorsque le modele le permet;
- tester un dataset reseau, par exemple `outside_tcp_dump` ou UNSW-NB15;
- entrainer les modeles principaux sur le cloud avec les datasets complets;
- versionner les artefacts `models/*.joblib`;
- comparer les temps d'execution et la complexite;
- interpreter les ecarts entre HDFS et BGL.

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

Livrables attendus:

- `docs/memoire/plan.md`;
- tableaux et figures prets a inserer;
- sections redigees progressivement.

## Ordre De Travail Recommande

1. Finaliser objectif 4: enrichir la correlation et la priorisation des incidents.
2. Finaliser objectif 5: rendre le dashboard demonstrable et capturable.
3. Finaliser objectif 6: entrainer sur le cloud, sauvegarder les modeles joblib et stabiliser les tableaux.
4. Finaliser objectif 7: construire le plan detaille puis rediger chapitre par chapitre.
