# Campagne Multi-Cycles SupervisorAgent

| Indicateur | Valeur |
| --- | --- |
| Cycles | 5 |
| Cycles OK | 5 |
| Familles routees | fallback, linux |
| Sources choisies | cef.log, cloudtrail.jsonl, apache_access.log, linux_auth.log, corrupt_incomplete.log |
| Duree moyenne | 5.8199 s |

| Cycle | Source | Famille | Decision | Statut | Duree s |
| --- | --- | --- | --- | --- | --- |
| 1 | `cef.log` | fallback | sample=1000, window=15, max_mb=1 | ok | 5.9844 |
| 2 | `cloudtrail.jsonl` | fallback | sample=1000, window=15, max_mb=1 | ok | 6.4919 |
| 3 | `apache_access.log` | fallback | sample=1000, window=15, max_mb=1 | ok | 8.9842 |
| 4 | `linux_auth.log` | linux | sample=1000, window=20, max_mb=1 | ok | 3.9901 |
| 5 | `corrupt_incomplete.log` | fallback | sample=300, window=20, max_mb=1 | ok | 3.6491 |
