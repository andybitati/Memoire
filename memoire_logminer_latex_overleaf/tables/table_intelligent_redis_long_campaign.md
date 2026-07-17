# Campagne Redis Longue Agents Intelligents

| Indicateur | Valeur |
| --- | ---: |
| Run Redis | `redis-campaign-20260717161257` |
| Taches enfilees | 150 |
| Taches terminees | 150 |
| Taches uniques terminees | 150 |
| Echecs | 0 |
| Panne simulee avant ack | 1 |
| Pending final | 0 |
| Perte estimee | 0 |
| Duree observee depuis les evenements Redis | 102.4202 s |
| Debit observe | 1.4646 taches/s |
| Latence p95 par tache | 5.3567 s |
| Latence p99 par tache | 8.2873 s |

## Repartition Par Agent

| Agent | Taches terminees |
| --- | ---: |
| redis-recovery-agent | 1 |
| redis-agent-1 | 46 |
| redis-agent-2 | 62 |
| redis-agent-3 | 41 |

## Repartition Par Type

| Type de tache | Taches terminees |
| --- | ---: |
| parse.logs | 50 |
| route.model | 50 |
| discover.logs | 50 |

Note: ce resume a ete reconstruit depuis les evenements Redis apres expiration du timeout interne du script pilote. Les workers ont termine la campagne; Redis indique 150 taches uniques terminees, aucun echec et aucun pending final.
