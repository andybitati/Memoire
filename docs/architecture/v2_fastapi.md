# V2 FastAPI

La V2 expose les agents Logminer sous forme d'API REST locale, tout en gardant
la V1 CLI comme socle stable.

## Lancer Le Serveur

Installer les dependances:

```powershell
python -m pip install -r requirements.txt
```

Demarrer l'API:

```powershell
python -m uvicorn src.logminer.api:app --host 127.0.0.1 --port 8000
```

Documentation interactive:

```text
http://127.0.0.1:8000/docs
```

## Lancer Redis

Redis est optionnel: sans Redis, les endpoints FastAPI classiques continuent de
fonctionner. Pour activer le bus evenementiel:

```powershell
docker compose -f docker-compose.redis.yml up -d
```

Sur Windows, Docker Desktop peut demander l'activation de la plateforme de
machine virtuelle. Si le message `Virtual Machine Platform not enabled`
apparait, lancer PowerShell en administrateur:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

Puis redemarrer Windows avant de relancer Docker Desktop.

Variables disponibles:

```powershell
$env:LOGMINER_REDIS_URL="redis://localhost:6379/0"
$env:LOGMINER_REDIS_STREAM="logminer:events"
```

## Agent Runtime Docker

La V2 prevoit un agent runtime charge de faciliter le travail de
l'administrateur. Son role est de verifier la presence de Docker, de tenter de
lancer Docker Desktop sur Windows lorsque c'est possible, puis de demarrer les
services Logminer declares dans `docker-compose.redis.yml`.

Endpoints associes:

| Endpoint | Role |
| --- | --- |
| `GET /runtime/status` | Lire l'etat Docker sans action |
| `POST /runtime/prepare` | Preparer Docker et lancer les services Compose |

Exemple:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/runtime/prepare `
  -ContentType "application/json" `
  -Body '{"start_desktop":true,"wait_seconds":45}'
```

Limite volontaire: l'agent ne contourne pas les droits de la machine. Si Docker
Desktop, WSL2 ou la plateforme de machine virtuelle demandent une action
administrateur, l'agent le signale et laisse l'administrateur appliquer la
correction.

## Autorisation Des Journaux Sensibles

Certains journaux, par exemple `Security.evtx` sous Windows, exigent des droits
administrateur. La V2 introduit un agent d'autorisation privilegiee qui demande
une validation via le mecanisme natif du systeme, par exemple l'invite UAC sous
Windows.

Principe important: Logminer ne demande pas et ne stocke jamais le mot de passe
administrateur. L'administrateur valide l'action dans la fenetre securisee du
systeme d'exploitation. Si l'autorisation est acceptee, le script de collecte
exporte les journaux sensibles vers `data/raw/windows_events_admin`, puis les
agents standards peuvent les examiner.

Endpoint associe:

| Endpoint | Role |
| --- | --- |
| `POST /collect/windows/privileged` | Demander une collecte Windows elevee via UAC |

Exemple:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/collect/windows/privileged `
  -ContentType "application/json" `
  -Body '{"days":2,"copy_logs":["Application","System","Security"]}'
```

Cette approche garde une trace claire de l'intention dans Redis/JSONL, tout en
laissant le controle final a l'administrateur systeme et reseau.

## Endpoints

| Endpoint | Role |
| --- | --- |
| `GET /health` | Verifier que l'API repond |
| `GET /runtime/status` | Verifier Docker sans lancer de service |
| `POST /runtime/prepare` | Demarrer Docker/Compose lorsque c'est possible |
| `GET /redis/health` | Verifier la connexion au serveur Redis |
| `GET /events` | Lire les evenements publies dans Redis |
| `GET /models` | Lister les familles de modeles et leurs artefacts |
| `POST /collect/discover` | Decouvrir automatiquement les journaux candidats |
| `POST /collect/windows/privileged` | Demander l'autorisation admin pour les journaux sensibles |
| `POST /route` | Identifier la famille de logs et le modele choisi |
| `POST /parse` | Parser un log brut vers un CSV Logminer |
| `POST /detect` | Lancer detection + correlation sur un CSV/Parquet |
| `POST /correlate` | Rejouer uniquement la correlation sur un CSV d'anomalies |
| `POST /run` | Lancer parsing optionnel, routage, detection et correlation |
| `POST /run/discovered` | Lancer collecte locale, routage, detection et correlation |

## Exemple De Routage

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/route `
  -ContentType "application/json" `
  -Body '{"input_path":"data/raw/Datasets/linux_auth_logs_labeled.csv","sep":"auto"}'
```

## Exemple D'execution Complete

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/run `
  -ContentType "application/json" `
  -Body '{"input_path":"data/raw/Datasets/linux_auth_logs_labeled.csv","sep":"auto","parse_if_needed":false}'
```

## Exemple Avec Redis

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/run `
  -ContentType "application/json" `
  -Body '{"input_path":"data/raw/Datasets/linux_auth_logs_labeled.csv","sep":"auto","parse_if_needed":false,"use_redis":true,"run_id":"demo-linux-auth"}'

Invoke-RestMethod `
  -Method Get `
  -Uri "http://127.0.0.1:8000/events?run_id=demo-linux-auth"
```

## Exemple De Correlation Seule

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/correlate `
  -ContentType "application/json" `
  -Body '{"input_path":"data/processed/api_linux_auth_anomalies.csv","output":"data/processed/api_linux_auth_incidents.csv","sep":"auto"}'
```

## Principe De Securite

La V2 accepte des chemins locaux, pas des uploads publics. Elle est donc prevue
pour un usage local/laboratoire. Une future version exposee sur reseau devra
ajouter:

- authentification;
- restriction des chemins autorises;
- quotas de taille;
- execution asynchrone;
- journalisation des appels.
- protection de Redis par mot de passe ou reseau prive.

## Lien Avec La V1

La V2 appelle les fonctions deja utilisees par la CLI:

```text
route_model()
run_routed_detection()
correlate_anomalies()
run_pipeline()
RedisMessageBus()
```

La logique metier reste donc partagee avec la V1. Si l'API devient instable, la
chaine CLI reste utilisable pour la soutenance et les experimentations.

## Role De Redis Dans Le Memoire

Redis sert de bus evenementiel entre les agents. Dans cette implementation, les
evenements sont publies dans un Stream Redis (`logminer:events` par defaut):

```text
workflow.started
parsing.started
parsing.completed
detection.started
detection.completed
correlation.started
correlation.completed
workflow.completed
```

Ce choix permet de montrer le passage d'un prototype local vers une architecture
plus distribuee, sans retirer la version CLI stable.
