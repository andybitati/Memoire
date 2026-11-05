# Reponse Aux Critiques - Article 1

Date: 2026-06-03

Objet: correction des faiblesses identifiees dans le premier article
`Logminer: A Lightweight Multi-Agent Framework for Family-Aware Multi-Model
Anomaly Detection in Heterogeneous Logs`.

## 1. Ablation Du Routage Familial

Résultats retirés : ils provenaient d'un script comportant une fuite de l'étiquette sur UNSW et une sélection par premières lignes réduisant CICIDS aux DDoS. Comparaison valide : `experiments/phase_revision_20261105/E-H3B-STRICT-HOLDOUT/`, section `sec:e-h3b` du mémoire.

## 2. Ambiguite Du Terme Multi-Agent

Critique traitee:

> Les agents peuvent etre percus comme des microservices/modules orchestres.

Correction de positionnement:

> In this work, the term agent is used in an architectural and software
> engineering sense: each agent owns a specialized role, exposes or consumes
> messages, can be executed independently in the local prototype, and contributes
> to a coordinated detection workflow. The prototype does not claim cognitive
> agency, negotiation, FIPA compliance or reinforcement-learning-based
> cooperation.

Formulation plus mesuree:

> Logminer is a modular agent-oriented architecture rather than a fully
> cognitive multi-agent system. Its agentic contribution lies in specialization,
> explicit communication contracts, routing decisions and coordinated execution
> across collection, parsing, detection, correlation and visualization.

## 3. HDFS/BGL Et Logs Sequentiels

Critique traitee:

> HDFS obtient un F1 faible et les logs sequentiels/textuels exigent souvent
> des approches type Drain, DeepLog ou LogAnomaly.

Correction de conclusion:

> The HDFS results show the structural limits of lightweight row-level features
> on distributed-system logs, where event order and textual templates are
> central. For such logs, Logminer should be extended with a semantic parsing
> agent, e.g. Drain-like templates, and temporal windows before detection.

Nuance a ajouter:

> The current lightweight strategy is suitable as a deployable baseline and
> routing framework, but it is insufficient as a state-of-the-art sequential log
> detector for HDFS-like systems.

## 4. Fallback Model

Clarification a inserer:

> The fallback model is selected when the router cannot assign a source to a
> known family with sufficient evidence from file type, column names, marker
> tokens or sample values. It is not intended to maximize performance; it
> preserves graceful degradation by avoiding silent failure on unknown formats.
> Its outputs should be treated as low-confidence anomaly candidates.

## 5. Volumetrie Et Passage A L'Echelle

Critique traitee:

> Les cycles de 8 537 lignes sont faibles pour un SOC.

Correction:

> The reported benchmark validates local quasi-real-time feasibility, not SOC
> production throughput. Routing is based on a bounded sample of rows and a
> fixed set of family scores; its cost is approximately O(k x c x s), where k is
> the number of families, c the number of inspected columns and s the sampled
> rows. The expensive step remains model inference, not routing.

Formulation mesuree:

> Scaling to production SOC workloads requires distributed ingestion, batched
> inference and queue-based deployment, which are outside the validated scope of
> the current prototype.

## 6. Figures En Anglais

Correction apportee:

- les titres et sous-titres des SVG ont ete traduits en anglais;
- les exports PNG/PDF ont ete regeneres;
- les figures article sont disponibles dans `docs/memoire/figures_exports/`.

## Verdict

Les critiques sont resolubles. La correction la plus importante est d'ajouter
les deux tableaux d'ablation et de reduire la force de la conclusion:

- ne pas affirmer que le routage familial gagne toujours;
- affirmer qu'il fournit une specialisation controlee, utile surtout lorsque les
  familles necessitent des espaces de features differents;
- presenter HDFS comme limite structurelle et perspective semantique/sequentielle.


