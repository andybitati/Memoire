# Comparaison Controlee Monolithique Vs Agents

| Mode | Taches | Echecs | Duree s | Debit t/s | Latence moy. | Latence p95 | CPU moy. | CPU max | RAM max MB | Reprises | Pending final |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| monolith | 60/60 | 0 | 36.6815 | 1.6357 | 0.6114 | 1.8447 | 121.339 | 121.339 | 189.074 | 0 | 0 |
| agents | 60/60 | 0 | 38.1803 | 1.5715 | 1.8053 | 5.7703 | 165.746 | 165.746 | 234.777 | 0 | 0 |
| agents_failure_recovery | 60/60 | 0 | 39.3000 | 1.5267 | 0.6462 | 1.9336 | 117.598 | 117.598 | 189.395 | 1 | 0 |

Note: les modes executent les memes types de taches et le meme volume sur le meme poste. La variante avec panne simule une tache non acquittee puis une reprise controlee.
