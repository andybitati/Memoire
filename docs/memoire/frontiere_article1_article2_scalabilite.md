# Frontiere Article 1 / Article 2 - Redis Streams Et Scalabilite

## Regle De Separation

Article 1 peut mentionner Redis Streams uniquement comme une brique
d'implementation qui confirme que l'architecture n'est pas enfermee dans une
execution HTTP synchrone. Il ne doit pas utiliser Redis, les workers ou le smoke
test queue comme contribution experimentale principale.

Article 2 recupere tout ce qui releve de l'operationnel:

- comportement de la file `logminer:jobs`;
- workers Redis et consumer groups;
- usage MQTT pour collecteurs legers et pub/sub temps reel;
- jobs pending et reprise apres arret worker;
- latence queuee;
- campagne CPU/RAM;
- stress, resilience, back-pressure, retries et dead-letter queue;
- discussion multi-machine ou SOC leger.

## Formulation Pour Article 1

> Redis Streams is implemented as an optional queued-execution path, but the
> present article does not evaluate queue throughput, worker scaling or
> fault-recovery behavior. These aspects are reserved for the companion
> operational evaluation.

## Formulation Pour Article 2

> Building on the routing architecture introduced in the first article, this
> article evaluates operational behavior, including resource usage, robustness,
> queued execution with Redis Streams, worker-based processing and remaining
> back-pressure limits.

## Donnees A Ne Pas Mettre Comme Resultats Dans Article 1

- `table_scalability_redis_smoke.md`;
- `table_mqtt_integration.md` comme resultat experimental central;
- temps de queue Redis;
- debit MQTT ou comparaison Redis/MQTT;
- comparaison nombre de workers;
- reprise pending;
- tests d'arret worker;
- CPU/RAM multi-cycles detailles;
- stress ou charge multi-source.

Ces elements peuvent apparaitre dans le memoire et dans l'article 2, pas comme
preuve centrale de l'article 1.
