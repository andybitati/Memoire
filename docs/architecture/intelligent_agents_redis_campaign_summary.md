# Campagne Redis Agents Intelligents

Date: 2026-07-17T14:56:23.569586+00:00

## Resultat

- Run: `redis-campaign-20260717145602`
- Workers: `3`
- Taches enfilees: `12`
- Taches terminees: `12`
- Taches terminees uniques: `12`
- Taches echouees: `0`
- Pannes simulees avant ack: `1`
- Pending apres campagne: `0`
- Perte estimee: `0`
- Debit: `0.573` taches/s
- Latence p95/p99: `2.3147` / `2.3336` s

## Repartition

Par agent:

```json
{
  "redis-recovery-agent": 1,
  "redis-agent-1": 2,
  "redis-agent-2": 5,
  "redis-agent-3": 4
}
```

Par type de tache:

```json
{
  "parse.logs": 4,
  "route.model": 4,
  "discover.logs": 4
}
```

## Interpretation

Cette campagne apporte une preuve executable que les agents Logminer peuvent fonctionner comme workers distribues: ils partagent un stream Redis, publient leurs decisions et recuperent une tache abandonnee avant acquittement.
