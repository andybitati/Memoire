| Brique | Etat dans Logminer | Preuve locale | Limite a declarer |
| --- | --- | --- | --- |
| Bus JSONL local | Stable, append-only, reproductible sans service externe | `src/logminer/agents/bus.py`, `data/processed/agent_messages.jsonl` | Suffisant pour prototype local, pas pour workers distribues |
| Redis Streams | Integre comme bus evenementiel optionnel pour FastAPI et les agents | `RedisMessageBus`, `/redis/health`, `/events`, `docker-compose.redis.yml`, `use_redis=true`, campagne endurance 6h | Valide localement sur 8508 taches agents et 709 reprises; pas encore valide comme couche d'ingestion SOC multi-machine sous forte charge |
| File de jobs | Integree pour decoupler API et inference | `/run/queued`, `logminer:jobs`, `scripts/logminer_redis_worker.py` | Les chemins de donnees doivent etre partages entre API et workers |
| Consumer groups | Integres pour repartir les jobs entre plusieurs workers | `read_group_jobs`, `ack_job`, `/redis/pending` | Les retries avances et la dead-letter queue restent a formaliser |
| Reprise pending | Integree pour recuperer des jobs non acquittes apres panne worker | `claim_stale_jobs`, `--claim-idle-ms`, `redis-recovery-agent` | Validee localement par 709 reprises; le seuil d'inactivite doit etre calibre selon la duree normale d'inference |
| Contrat de message | Commun entre JSONL et Redis Streams | `docs/architecture/message_contract.md` | Schema a versionner si plusieurs machines publient en parallele |
| Degradation | Le workflow reste utilisable sans Redis | bus JSONL/CSV, endpoints FastAPI sans `use_redis` | Redis indisponible reduit l'observabilite evenementielle, pas la chaine CLI |
| Perspective | Retries avances, dead-letter queue, back-pressure et tests de charge | cite en limites et travaux futurs | A evaluer dans l'article 2 ou une campagne operationnelle |
