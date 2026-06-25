# Reponse Aux Remarques Reviewers - Article 1, Round 2

## Position Sur Les Agents

Logminer evolue maintenant vers de vrais agents au sens operationnel borne. Un `SupervisorAgent` a ete ajoute avec une boucle perception -> etat -> decision -> action: observation des sources et ressources locales, choix d'une source candidate, adaptation de `sample_rows`, `window_minutes` et `max_mb`, execution parsing/routage/detection/correlation, publication bus et audit.

Position recommandee pour l'article: conserver `multi-agent software architecture` et parler de `bounded supervisor autonomy`. Eviter de presenter le prototype comme un systeme cognitif, FIPA, RL ou LLM-agent.

Preuve ajoutee:

- code: `src/logminer/agents/supervisor_agent.py`;
- API: `POST /supervisor/cycle`;
- campagne: `scripts/run_supervisor_campaign.py`;
- tableau: `docs/memoire/tables/table_supervisor_campaign.md`;
- resultats: 5 cycles OK, 5 sources explorees, routes `fallback` et `linux`, adaptation de `sample_rows` a 300 pour l'entree corrompue, fenetre portee a 20 minutes apres fallback frequent.

## Reviewer 1

### Complexite Et Passage A L'echelle

Action realisee:

- instrumentation de `src/logminer/agents/model_router.py` avec `route_sec`, `detect_sec`, `correlate_sec`;
- propagation des timings dans `src/logminer/api.py`;
- ajout des colonnes dans `scripts/benchmark_realtime_workflow.py` et `scripts/run_resource_campaign.py`;
- tableau produit: `docs/memoire/tables/table_agent_timing_profile.md`.

Resultat local sur 8 537 lignes Windows normalisees:

- routeur: 0.0449 s, soit 0.9 % du temps routeur+detecteur+correlateur;
- detecteur: 4.3460 s, soit 91.3 %;
- correlateur: 0.3678 s, soit 7.7 %.

Texte a ajouter:

> A direct profiling run on 8,537 normalized Windows events shows that the router accounts for 0.9% of the measured routing-detection-correlation time, while model inference accounts for 91.3% and correlation for 7.7%. This supports the claim that the router is not the dominant local bottleneck. The revised prototype now adds Redis Streams queued execution: FastAPI can enqueue workflows into `logminer:jobs`, and external workers consume them through Redis consumer groups. This decouples request handling from inference at prototype level. A production SOC deployment would still require tested back-pressure, retry policies, dead-letter handling, security hardening and longer stress campaigns.

### HDFS Et Logs Sequentiels

Clarification a ajouter:

> The absence of temporal-window features for HDFS is not a limitation of the normalizer schema itself, which can carry timestamps, event identifiers and raw messages. It is a deliberate lightweight design constraint of this first prototype: row-level features were used to keep inference simple and comparable across families. The high HDFS false positive rate shows that this choice is insufficient for distributed-system logs. A stronger HDFS agent should extract templates and temporal windows before detection.

### Figures

Action realisee:

- titres et sous-titres des figures SVG convertis en anglais;
- exports PDF disponibles dans `docs/memoire/figures_exports/` et copies article dans `logminer_article1_latex_draft/figures/`.

### Fallback

Action realisee:

- correction du routeur pour envoyer les enregistrements `unknown`/corrompus vers `fallback`;
- quantification dans `docs/memoire/tables/table_fallback_corrupt_behavior.md`.

Resultat:

- `corrupt_incomplete.log`: 2 lignes conservees, route `fallback`, 0 anomalie candidate, 0 incident.

## Reviewer 2

### Innovation Scientifique

Position renforcee:

La contribution n'est pas un nouvel algorithme ML, mais une strategie d'orchestration analytique testable: specialisation controlee par famille, unification des sorties supervisees/non supervisees et correlation interpretable. Il faut presenter l'article comme contribution systeme/evaluation, pas comme innovation algorithmique pure.

### Ablation Conceptuelle

Limite reconnue:

L'ablation operationnelle melange routage, features specialisees et modeles specialises. Le papier doit donc distinguer:

- ablation commune: isole le routage sous representation minimale commune;
- ablation operationnelle: mesure la configuration complete de specialisation;
- travail futur: ablation factorielle `routing only`, `features only`, `model only`, `full`.

Texte recommande:

> The operational ablation should not be interpreted as isolating routing alone. It evaluates the complete specialization package: routing, compatible feature space and family-specific detector. The controlled common-space ablation isolates the routing decision under a shared representation and shows that routing alone does not guarantee superior F1.

### Terme Agentic

Action recommandee:

- retirer `agentic` des formulations fortes;
- garder `multi-agent software architecture` avec une definition stricte;
- presenter le `SupervisorAgent` comme autonomie bornee et explicable, non comme agent cognitif general.

### Correlation

Clarification:

Le correlateur est explicable et regroupe par fenetre temporelle, host, user, source, category/subcategory, protocole et port destination. La priorite combine volume, severite, diversite d'evenements, categorie de securite et profondeur du score d'anomalie.

Il faut toutefois dire clairement que la correlation n'est pas la contribution algorithmique principale.
