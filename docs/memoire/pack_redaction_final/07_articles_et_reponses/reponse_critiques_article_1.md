# Reponse Aux Critiques - Article 1

Date: 2026-06-03

Objet: correction des faiblesses identifiees dans le premier article
`Logminer: A Lightweight Multi-Agent Framework for Family-Aware Multi-Model
Anomaly Detection in Heterogeneous Logs`.

## 1. Ablation Du Routage Familial

Critique traitee:

> L'article defend le routage familial, mais les resultats d'ablation manquent.

Correction apportee:

- script reproductible: `scripts/run_family_routing_ablation.py`;
- donnees brutes: `data/processed/family_routing_ablation.csv`;
- tableau controle: `docs/memoire/tables/table_family_routing_ablation.md`;
- tableau operationnel: `docs/memoire/tables/table_family_routing_operational_ablation.md`;
- figure: `docs/memoire/figures/fig_family_routing_ablation.svg`;
- exports article: `docs/memoire/figures_exports/fig_family_routing_ablation.png`
  et `.pdf`.

Interpretation recommandee:

> The controlled common-space ablation shows that routing alone does not
> automatically outperform a monolithic classifier when all families are forced
> into the same minimal feature space. However, the operational comparison shows
> that the full family-aware configuration improves Linux/auth and UNSW results
> and remains close on CICIDS, where the global common baseline is already near
> saturation. Therefore, the contribution should be framed as controlled
> specialization and feature/model compatibility, not as a universal guarantee
> of higher F1 on every dataset.

Phrase a inserer:

> The proposed strategy aims to limit confusion induced by heterogeneous log
> formats and distributions. This hypothesis is evaluated against a monolithic
> common-feature baseline and complemented by an operational comparison with
> family-specific configurations.

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


