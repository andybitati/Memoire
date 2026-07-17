# Preuve Redis Des Agents Intelligents Distribues

Date: 2026-07-17

Cette note documente la premiere validation distribuee locale de la branche
`version_3`.

## Objectif

Verifier que plusieurs agents/processus peuvent consommer un meme flux de
taches via Redis Streams, publier leurs heartbeats et executer des competences
differentes.

## Environnement

- Redis lance via `docker-compose.redis.yml`.
- Stream evenements: `logminer:events`.
- Stream taches: `logminer:agent_tasks`.
- Groupe agents: `logminer-intelligent-agents`.
- Deux consumers: `worker-1` et `worker-2`.

## Commandes Executees

```powershell
docker compose -f docker-compose.redis.yml up -d

python scripts\logminer_intelligent_agent_worker.py `
  --enqueue-demo `
  --consumer worker-1 `
  --agent-id redis-agent-1 `
  --cycles 1

python scripts\logminer_intelligent_agent_worker.py `
  --consumer worker-2 `
  --agent-id redis-agent-2 `
  --cycles 1
```

Verification API directe:

```powershell
python -B -c "import sys, json; sys.path.insert(0, r'src\logminer'); import api; print(json.dumps(api.agents_status(count=1000), ensure_ascii=False, indent=2))"
```

## Resultat Observe

Trois taches ont ete publiees dans Redis:

- `discover.logs`;
- `parse.logs`;
- `route.model`.

Repartition observee:

| Agent | Taches executees | Types |
| --- | ---: | --- |
| `redis-agent-1` | 1 | `route.model` |
| `redis-agent-2` | 2 | `parse.logs`, `discover.logs` |

Toutes les taches observees se sont terminees avec le statut `ok`.

## Preuve De Capacites

L'endpoint logique `/agents/status` reconstruit l'etat a partir de
`agent.heartbeat`, `agent.task.started` et `agent.task.completed`.

Les agents publient les capacites suivantes:

- `perception` -> `discover.logs`;
- `parser` -> `parse.logs`;
- `router` -> `route.model`;
- `detector` -> `detect.anomalies`;
- `correlator` -> `correlate.incidents`.

## Conclusion

Cette validation prouve une distribution locale effective par bus partage:
plusieurs consumers Redis distincts traitent des taches differentes et publient
leur etat. Elle ne prouve pas encore un deploiement multi-machine, mais elle
depasse la simple decomposition logique locale.

## Prochaines Validations

1. Lancer les deux workers dans deux terminaux separes pendant une campagne
   plus longue.
2. Ajouter un scenario de panne avant acquittement Redis.
3. Mesurer pending jobs, reprise, debit, p95/p99 et erreurs.
4. Tester les workers sur deux machines ou une machine + VM.
