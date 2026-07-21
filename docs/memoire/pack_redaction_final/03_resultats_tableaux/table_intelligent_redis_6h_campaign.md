# Campagne Redis Endurance 6h Agents Intelligents

| Indicateur | Valeur |
| --- | ---: |
| Debut | `2026-07-20T11:18:03.316376+00:00` |
| Fin | `2026-07-20T17:18:17.172766+00:00` |
| Duree cible | 21600 s |
| Duree observee | 21613.8566 s |
| Iterations terminees | 709 |
| Iterations echouees | 0 |
| Taches enfilees | 8508 |
| Taches uniques terminees | 8508 |
| Echecs de taches | 0 |
| Pannes simulees avant ack | 709 |
| Pending final cumule | 0 |
| Perte estimee cumulee | 0 |
| Debit observe | 0.3936 taches/s |
| Latence p95 | 5.9879 s |
| Latence p99 | 8.7987 s |

## Repartition Par Agent

| Agent | Taches terminees |
| --- | ---: |
| `redis-agent-1` | 2654 |
| `redis-agent-2` | 2602 |
| `redis-agent-3` | 2543 |
| `redis-recovery-agent` | 709 |

## Repartition Par Type

| Type de tache | Taches terminees |
| --- | ---: |
| `discover.logs` | 2836 |
| `parse.logs` | 2836 |
| `route.model` | 2836 |

Note: cette table est mise a jour apres chaque iteration du run d'endurance.

Conditions: le run a ete execute depuis l'hote Windows avec Redis Docker
`logminer-redis` expose sur `localhost:6379`. Les VM VirtualBox `Debian` et
`Ubuntu` etaient lancees pendant l'experience, en NAT simple; elles documentent
le contexte de preparation multi-machine, mais le bus Redis utilise par cette
campagne etait local a l'hote. La conclusion revendique une distribution locale
multi-processus avec endurance, pas encore une validation SOC multi-machine.
