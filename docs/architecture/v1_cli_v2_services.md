# Evolution V1 CLI Vers V2 FastAPI/Redis

Ce document fixe la strategie retenue apres stabilisation des modeles. Les trois
versions appartiennent au perimetre du memoire, mais elles n'ont pas le meme
role de risque:

- **V1**: prototype local stable, pilote par CLI et fichiers CSV; c'est le
  socle de secours si les evolutions suivantes deviennent instables;
- **V2**: exposition progressive des agents par FastAPI, a integrer au memoire
  si elle reste compatible avec la V1;
- **V3**: orchestration evenementielle avec Redis/MQTT si le temps reel devient
  necessaire et si le calendrier le permet.

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
la logique metier deja stabilisee en V1.

Endpoints cibles:

```text
GET  /health
GET  /models
POST /route
POST /parse
POST /detect
POST /correlate
POST /run
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
```

La V2 devra conserver la compatibilite avec les commandes CLI: l'API ne doit
pas dupliquer la logique, mais appeler les fonctions deja testees.

## V3 Possible - Redis Ou MQTT

Redis ou MQTT deviennent utiles si le prototype evolue vers:

- plusieurs collecteurs en parallele;
- traitement quasi temps reel;
- file d'evenements persistante;
- agents deployes sur plusieurs machines;
- reprise apres incident.

Dans cette version, le bus JSONL local de la V1 devient un bus evenementiel:

```text
collector.events
parser.completed
detection.completed
correlation.completed
incident.created
```

## Decision Actuelle

La redaction commence sur la V1 stable, mais FastAPI/Redis restent des objectifs
du memoire. La regle est de ne jamais casser la V1: chaque evolution V2/V3 doit
etre ajoutee par-dessus la chaine CLI deja validee, ou rester documentee comme
prototype partiel si elle n'est pas suffisamment stable.
