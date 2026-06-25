# Evolution V1 CLI Vers V2 FastAPI/Redis

Ce document fixe la strategie retenue apres stabilisation des modeles. Les trois
versions appartiennent au perimetre du memoire, mais elles n'ont pas le meme
role de risque:

- **V1**: prototype local stable, pilote par CLI et fichiers CSV; c'est le
  socle de secours si les evolutions suivantes deviennent instables;
- **V2**: exposition progressive des agents par FastAPI, compatible avec la V1;
- **V3**: orchestration evenementielle. Redis Streams est maintenant integre
  comme bus optionnel de la V2 pour les jobs persistants; MQTT est ajoute comme
  bus pub/sub optionnel pour collecteurs et notifications temps reel.

## V1 - Prototype CLI Stable

La V1 est la version a defendre quoi qu'il arrive dans le memoire. Elle repose
sur des commandes reproductibles et des artefacts locaux:

```text
logs / CSV / Parquet
  -> parsing / normalisation
  -> routeur multi-modeles
  -> detection
  -> correlation
  -> dashboard / CSV incidents
```

Composants principaux:

```text
src/logminer/pipeline.py
src/logminer/agents/model_router.py
src/logminer/agents/detector.py
src/logminer/agents/correlator.py
src/logminer/agents/orchestrator.py
web/dashboard/
models/*.joblib
```

La V1 est prioritaire car elle est:

- reproductible sans serveur;
- compatible avec les datasets locaux et les notebooks cloud;
- simple a demontrer pendant la soutenance;
- deja validee sur plusieurs familles de journaux.
- utilisable comme retour arriere si une evolution FastAPI/Redis crashe.

## Commandes CLI V1

Router une source sans lancer la detection:

```powershell
python src\logminer\agents\model_router.py -i data\raw\Datasets\linux_auth_logs_labeled.csv --sep auto
```

Lancer detection et correlation avec le modele choisi:

```powershell
python src\logminer\agents\model_router.py `
  -i data\raw\Datasets\linux_auth_logs_labeled.csv `
  --sep auto `
  --detect
```

Parser un log brut vers le schema Logminer:

```powershell
python -c "import sys; sys.path.insert(0, r'src\logminer'); import pipeline; print(pipeline.run_pipeline(r'examples\windows_event_sample.xml', r'data\processed', 'windows_events.csv', debug=True))"
```

Executer l'orchestrateur local:

```powershell
python src\logminer\agents\orchestrator.py `
  -i examples\windows_event_sample.xml `
  --parsed-name orchestrated_windows.csv `
  --anomalies-name orchestrated_anomalies.csv `
  --incidents-name orchestrated_incidents.csv
```

Ouvrir le dashboard local:

```powershell
streamlit run src\logminer\agents\dashboard.py
```

## V2 - Services FastAPI

FastAPI servira a exposer les agents sous forme de services HTTP, sans changer
la logique metier deja stabilisee en V1. La premiere version locale est
maintenant disponible et testable.

Le premier squelette V2 est implemente dans:

```text
src/logminer/api.py
docs/architecture/v2_fastapi.md
```

Endpoints deja disponibles:

```text
GET  /health
GET  /redis/health
GET  /events
GET  /models
POST /route
POST /parse
POST /detect
POST /correlate
POST /run
```

Endpoints a ajouter si la V2 doit gerer un historique de runs:

```text
GET  /runs/{run_id}
GET  /runs/{run_id}/anomalies
GET  /runs/{run_id}/incidents
```

Flux cible:

```text
Dashboard / client
  -> FastAPI
  -> orchestrateur
  -> parseur / routeur / detecteur / correlateur
  -> stockage CSV ou base locale
  -> Redis Streams si `use_redis=true`
```

La V2 devra conserver la compatibilite avec les commandes CLI: l'API ne doit
pas dupliquer la logique, mais appeler les fonctions deja testees.

## V3 Possible - Redis Streams Et MQTT

Redis Streams est introduit comme bus optionnel deja disponible dans le
prototype. MQTT est aussi disponible pour des collecteurs plus proches de l'IoT
ou du temps reel. Ces bus deviennent utiles pour:

- plusieurs collecteurs en parallele;
- traitement quasi temps reel;
- file d'evenements persistante;
- agents deployes sur plusieurs machines;
- reprise apres incident.

Dans cette version, le bus JSONL local de la V1 peut devenir un bus
evenementiel persistant. Le prototype Redis Streams publie deja ces familles
d'evenements dans un Stream:

```text
collector.events
parser.completed
detection.completed
correlation.completed
incident.created
```

Configuration Redis locale:

```powershell
docker compose -f docker-compose.redis.yml up -d
$env:LOGMINER_REDIS_URL="redis://localhost:6379/0"
$env:LOGMINER_REDIS_STREAM="logminer:events"
```

Configuration MQTT locale:

```powershell
docker compose -f docker-compose.mqtt.yml up -d
$env:LOGMINER_MQTT_HOST="localhost"
$env:LOGMINER_MQTT_TOPIC_PREFIX="logminer/events"
```

## Decision Actuelle

La redaction conserve la V1 stable comme socle, mais Redis Streams peut etre
integre au memoire maintenant comme extension concrete et testable de la V2.
La regle est de ne jamais casser la V1: chaque evolution V2/V3 doit etre
ajoutee par-dessus la chaine CLI deja validee. La file `logminer:jobs`, les
consumer groups et le worker Redis augmentent deja la scalabilite du prototype.
La scalabilite multi-machine, les retries avances, la dead-letter queue et le
back-pressure restent des evaluations operationnelles a mener separement.
