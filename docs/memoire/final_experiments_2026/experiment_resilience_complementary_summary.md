# Résilience complémentaire — décision GO/NO-GO

## Objectif

Déterminer si une nouvelle campagne Redis apporterait une preuve distincte des campagnes multi-VM et panne/reprise déjà disponibles.

## Preuve existante auditée

- Campagne: `redis-vbox-recovery-20260722150924`.
- Infrastructure: hôte Windows, VM Debian de panne, VM Ubuntu de reprise, Redis unique sur l'hôte.
- Flux: trois tâches de démonstration (`discover.logs`, `parse.logs`, `route.model`).
- Injection: le worker Debian lit une tâche, publie `agent.simulated_crash`, puis quitte avec le code 2 avant traitement et avant ACK.
- Reprise: après 150 ms, le worker Ubuntu utilise la réclamation des messages pending (`XAUTOCLAIM`, seuil configuré à 1 ms), traite les trois tâches puis les acquitte.
- Observation: 3 tâches enfilées, 3 événements de fin, 3 identifiants de tâche uniques, 0 échec, 1 tâche lue avant panne, 1 tâche reprise, pending final 0.

## Scénario nouveau envisagé

Une panne après traitement mais avant ACK mesurerait une propriété nouvelle: retraitement éventuel, doublons applicatifs et besoin d'idempotence. Le runtime publie actuellement l'événement de fin dans `execute_task`, puis appelle `source.acknowledge` dans `run_once`; cette fenêtre existe donc dans le code.

## Décision

`NO-GO — SKIPPED`.

Le scénario nouveau nécessiterait une injection de panne supplémentaire au point exact entre effet applicatif et ACK, ainsi qu'un Redis accessible. Lors de l'audit, Docker Desktop n'était pas démarré et aucun service ne répondait sur `localhost:6379`. Démarrer l'infrastructure ou modifier le runtime uniquement pour produire une campagne optionnelle n'est pas une exécution naturelle dans l'état courant. Les anciennes preuves ne sont pas relancées pour augmenter artificiellement le volume.

## Ce qui est soutenu

- Reprise multi-VM de laboratoire après sortie contrôlée d'un worker ayant lu une tâche avant traitement et ACK.
- La tâche pending observée est ensuite traitée par un autre worker.
- Les trois identifiants de tâche ont un événement de fin unique dans cette campagne et le pending final vaut zéro.

## Ce qui n'est pas soutenu

- Panne après traitement mais avant ACK.
- Absence générale de doublons ou garanties d'idempotence des effets applicatifs.
- Mesure du temps de reprise.
- Lag final de cette campagne de trois tâches.
- Tolérance à une interruption Redis.
- Haute disponibilité, scalabilité industrielle ou validation SOC opérationnelle.

## Artefacts audités

- `scripts/run_vbox_redis_recovery_campaign.ps1`.
- `scripts/logminer_intelligent_agent_worker.py`.
- `src/logminer/agents/intelligent_runtime.py`.
- `src/logminer/agents/bus.py`.
- `data/processed/vbox_redis_recovery_campaign.json`.
- `docs/memoire/tables/table_vbox_redis_recovery_campaign.md`.

