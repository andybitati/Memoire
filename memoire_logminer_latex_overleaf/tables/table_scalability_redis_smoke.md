| Verification | Resultat observe | Interpretation |
| --- | --- | --- |
| Redis local | `redis://localhost:6379/0` repond avec `ping=True` | Le bus evenementiel est disponible via Docker Compose |
| Enqueue API | `/run/queued` a cree le job `1780649170729-0` pour `run_id=scale-redis-smoke` | L'API peut accepter un workflow sans executer l'inference dans la requete |
| Worker Redis | `scripts/logminer_redis_worker.py --once --consumer scale-smoke-worker --claim-idle-ms 300000` termine avec code 0 | Un worker externe peut consommer et traiter le job |
| Evenements traces | `workflow.queued`, `workflow.worker.started`, `workflow.started`, `detection.started`, `workflow.completed`, `workflow.worker.completed` | Les transitions principales sont observables dans Redis Streams |
| Pending jobs | `pending=0` apres execution | Le job a ete acquitte dans le consumer group |
| Artefacts produits | `api_scale-redis-smoke_anomalies.csv`, `api_scale-redis-smoke_incidents.csv` | Le mode queue produit les memes familles d'artefacts que le workflow direct |
