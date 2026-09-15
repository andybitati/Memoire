# Analyse d’écart vers un système multi-agents autonome léger

Date de l’audit : 2026-09-09  
Périmètre : implémentation Logminer, scripts d’exécution locale et Redis, scripts multi-VM, artefacts expérimentaux présents dans le dépôt.

## Conclusion de l’audit

Logminer contient déjà des agents logiciels multi-tâches, un contrat de message stable, une mémoire locale, des heartbeats et deux transports opérationnels, JSONL et Redis Streams. Cette base ne constitue toutefois pas encore un protocole d’allocation décentralisée de type Contract Net. En mode Redis, un groupe de consommateurs attribue de fait chaque entrée au premier consommateur qui la lit; il n’y a ni appel à propositions adressé à plusieurs agents, ni comparaison de propositions, ni attribution fondée sur une utilité calculée localement.

Le superviseur historique choisit lui-même une source de données et exécute le workflow. Il assure donc davantage une orchestration impérative qu’un rôle limité au registre, à la santé, à l’audit et à la reprise. La transformation demandée doit conserver ce workflow pour les comparaisons, tout en ajoutant un chemin multi-agents autonome séparé et mesurable.

## Invariants à préserver

- `AgentMessage` garde exactement les champs `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`.
- Les identifiants techniques de Redis Streams restent des propriétés de l’enveloppe Redis; ils ne deviennent pas des champs du contrat métier.
- Les métadonnées de négociation, d’idempotence et d’expérience sont placées dans `payload`.
- Les anciens résultats et scripts restent intacts; les nouveaux artefacts sont écrits sous `experiments/phase_multi_agent/`.
- Aucune affirmation relative à une exécution multi-VM autonome n’est recevable avant une campagne effectivement exécutée sur Debian et Ubuntu.

## État vérifié et modifications requises

| Propriété attendue | État actuel vérifié | Manque constaté | Modification requise |
|---|---|---|---|
| Contrat `AgentMessage` | Dataclass à sept champs dans `src/logminer/agents/bus.py`; sérialisation identique en JSONL et Redis. | Aucun manque sur le contrat. | Ne modifier ni les champs ni leur ordre logique; placer les données CNP dans `payload`. |
| Agents multi-capacités | `MultiTaskIntelligentAgent` accepte plusieurs `AgentCapability` et plusieurs handlers. Le worker Redis déclare cinq capacités qui se recouvrent entre instances. | L’état de charge, la santé, la disponibilité de modèle et les dépendances ne sont pas explicites dans la décision. | Ajouter un état local explicite et un instantané publié dans les heartbeats. |
| Cycle agent | `can_handle`, `score_task`, `choose_tasks`, `execute_task`, `heartbeat` existent. | Les méthodes demandées `perceive`, `evaluate`, `compute_bid`, `propose`, `refuse`, `accept`, `learn` ne sont pas séparées. | Introduire ces opérations sans supprimer l’API historique. |
| Allocation des tâches | `RedisTaskSource.fetch` lit un groupe Redis et filtre les tâches compatibles après livraison. | Aucun appel concurrent à propositions; le premier consommateur réserve l’entrée. | Ajouter un coordinateur Contract Net léger qui diffuse `CFP`, collecte `PROPOSE`/`REFUSE`, envoie `AWARD`/`REJECT`, puis reçoit `ACCEPT`, `RESULT`/`FAIL` et émet `FEEDBACK`. |
| Autonomie de la décision | Chaque agent calcule actuellement un score de priorité pour ses propres tâches. | Le score n’est ni normalisé ni comparable entre agents et n’utilise pas les poids imposés. | Calculer localement une utilité bornée à partir de capacité, historique, modèle, disponibilité, charge et latence. |
| Politique configurable | La formule de `score_task` est codée en dur. | Aucun fichier de poids ni seuil de refus configurable. | Ajouter une configuration JSON versionnée avec les poids 0,30 / 0,20 / 0,20 / 0,15 / 0,10 / 0,05 et documenter qu’ils ne sont pas optimisés. |
| Refus explicites | Une tâche incompatible est ignorée ou reçoit un score sentinelle. | Aucun message `REFUSE` et aucun motif standardisé. | Implémenter `capability_missing`, `model_missing`, `agent_overloaded`, `agent_unhealthy`, `low_expected_utility`, `dependency_unavailable`. |
| Mémoire décisionnelle | `AgentMemory` mémorise succès, erreurs, durées, tâches terminées et décisions. | La fiabilité est `s/(s+f)` après la première observation; l’ablation mémoire OFF n’est pas un mode explicite. | Utiliser `(s+1)/(s+f+2)` et ajouter un commutateur mémoire ON/OFF contrôlé. |
| Charge et disponibilité | `max_parallel_tasks` existe. | Pas de compteur protégé des tâches actives ni de disponibilité normalisée. | Suivre `active_tasks`, calculer la charge et refuser lorsque la capacité locale est épuisée. |
| Modèles et dépendances | Les handlers peuvent échouer si une ressource manque. | Leur disponibilité n’intervient pas avant l’attribution. | Déclarer modèles et dépendances requis dans le payload et vérifier leur disponibilité lors de l’évaluation. |
| Idempotence | `completed_tasks` évite seulement de favoriser une tâche déjà vue dans la mémoire locale. | Aucun verrou persistant partagé; un autre agent peut répéter l’effet après reprise. | Ajouter un registre SQLite transactionnel indexé par `idempotency_key`, consulté avant l’effet et marqué après succès. |
| Reprise Redis | `XAUTOCLAIM`, `XPENDING` et ACK après exécution sont présents. | Le scénario existant simule un crash après lecture et avant traitement, pas après effet persistant et avant ACK. | Ajouter une expérience contrôlée post-traitement/pré-ACK avec reprise par un second agent et vérification d’un effet unique. |
| Supervision | `supervisor_agent.py` perçoit, sélectionne une source, décide puis exécute le workflow; les agents publient des heartbeats. | Le superviseur historique demeure l’orchestrateur de calcul. | Conserver ce chemin comme architecture centralisée de comparaison; ajouter un superviseur CNP limité au registre, à la santé, à l’audit, à la temporisation et à la reprise. |
| Mesure des messages | Les événements sont publiés sur le bus. | Aucun compteur CNP consolidé par type et par tâche. | Produire les compteurs `CFP`, `PROPOSE`, `REFUSE`, `AWARD`, `REJECT`, `ACCEPT`, `RESULT`, `FAIL`, `FEEDBACK` et messages/tâche. |
| Équité | Les campagnes existantes mesurent certaines répartitions de travailleurs. | Pas de charge par agent associée au CNP ni d’indice de Jain systématique. | Mesurer tâches, temps de charge et indice de Jain pour chaque répétition. |
| Comparaison A/B/C/D | Des scripts comparent monolithe et agents ou réalisent des campagnes Redis. | Aucun protocole unique ne compare A monolithe, B workers centralisés, C autonome mémoire OFF, D autonome mémoire ON sur des charges appariées. | Ajouter une campagne dédiée avec les mêmes charges et graines pour les quatre architectures. |
| Ablation mémoire | Une mémoire existe et influence `score_task`. | Pas d’expérience ON/OFF isolant son effet. | Ajouter une campagne appariée et rapporter répartition, erreurs, latences, utilité et messages. |
| Adaptation temporelle | Les historiques de succès et durée sont persistés. | Aucun workload en deux phases ni courbe d’utilité temporelle. | Construire une campagne où la spécialisation utile change entre deux phases et tracer l’utilité des agents. |
| Pipeline bout en bout | Les handlers couvrent découverte, parsing, routage, détection et corrélation. | Aucun protocole CNP bout en bout avec identifiant `end_to_end_run_id` et preuve de passage entre étapes. | Ajouter un scénario dédié et conserver les messages et sorties de chaque étape. |
| Multi-VM | Des scripts VirtualBox/Redis et des artefacts de workers existent. | Les VM exécutent des consommateurs Redis; les preuves disponibles ne montrent pas une négociation CNP entre agents autonomes. | Ne pas requalifier les campagnes historiques. Préparer puis exécuter ultérieurement une campagne Debian/Ubuntu utilisant le nouveau protocole. |
| Statistiques | Plusieurs scripts produisent des CSV et résumés. | Le nouveau protocole n’a aucun résultat ni intervalle de confiance. | Calculer moyenne, écart-type, médiane, min, max et IC à 95 % sur les répétitions réellement exécutées. |
| Traçabilité | Le dépôt contient des rapports et artefacts historiques. | Pas de manifeste append-only ni de sommes SHA-256 pour la nouvelle phase. | Créer un journal append-only et un manifeste SHA-256 sous `experiments/phase_multi_agent/manifests/`. |

## Sources de preuve consultées

- `src/logminer/agents/bus.py` : contrat `AgentMessage`, bus JSONL, Redis Streams, groupes, ACK, pending et reprise par `XAUTOCLAIM`.
- `src/logminer/agents/intelligent_runtime.py` : capacités, tâches, mémoire, sélection locale, exécution, heartbeat et source Redis.
- `src/logminer/agents/supervisor_agent.py` : sélection centralisée de la source, décision et exécution du workflow.
- `scripts/logminer_intelligent_agent_worker.py` : cinq handlers par agent, consommation Redis et simulation de crash avant traitement.
- `scripts/run_intelligent_agents_ablation.py`, `scripts/run_intelligent_agents_campaign.py`, `scripts/run_intelligent_redis_campaign.py`, `scripts/run_intelligent_redis_endurance_campaign.py` : campagnes antérieures, sans cycle Contract Net complet.
- `scripts/run_controlled_monolith_vs_agents.py` : comparaison historique monolithe/agents, distincte de la future comparaison A/B/C/D.
- `scripts/run_vbox_redis_1h_campaign.ps1`, `scripts/run_vbox_redis_balanced_campaign.ps1`, `scripts/run_vbox_redis_recovery_campaign.ps1`, `scripts/run_vbox_redis_validation.ps1` : orchestration multi-VM Redis historique.
- Graphe `graphify-out/graph.json`, interrogé sur le routage, la mémoire, la supervision, la reprise et les expériences existantes.

## Ordre d’implémentation retenu

1. Ajouter les primitives de politique locale, d’état et de négociation sans modifier `AgentMessage`.
2. Ajouter l’idempotence persistante et les tests du scénario post-traitement/pré-ACK.
3. Ajouter des tests unitaires du protocole et de l’ablation mémoire.
4. Construire la campagne A/B/C/D, l’adaptation en deux phases et le pipeline bout en bout.
5. Exécuter localement les répétitions, agréger les mesures et générer les figures à partir des seuls résultats produits.
6. Documenter l’architecture et les résultats, puis préparer séparément la campagne multi-VM autonome.

Cette analyse constitue l’état de référence antérieur aux modifications du noyau multi-agents.
