# Campagne Redis Agents Intelligents

Date: 2026-07-17

## Resultat

- Run court valide: `redis-campaign-20260717145602`
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

## Campagne Longue Retenue Pour Le Memoire

Run: `redis-campaign-20260717161257`

| Indicateur | Valeur |
| --- | ---: |
| Taches enfilees | 150 |
| Taches uniques terminees | 150 |
| Echecs | 0 |
| Panne simulee avant ack | 1 |
| Pending final | 0 |
| Perte estimee | 0 |
| Duree observee depuis Redis | 102.4202 s |
| Debit observe | 1.4646 taches/s |
| Latence p95 | 5.3567 s |
| Latence p99 | 8.2873 s |

Repartition: `redis-agent-1` a termine 46 taches, `redis-agent-2` 62,
`redis-agent-3` 41 et `redis-recovery-agent` 1 tache abandonnee par le worker
de panne. Les trois types de taches sont equilibres: 50 `parse.logs`, 50
`route.model` et 50 `discover.logs`.

Cette campagne longue est suffisante pour soutenir la revendication du memoire
sur la distribution locale multi-processus, la tolerance a une panne avant
acquittement et la conservation des taches sans perte observee.
