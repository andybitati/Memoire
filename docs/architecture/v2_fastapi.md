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

## Endpoints

| Endpoint | Role |
| --- | --- |
| `GET /health` | Verifier que l'API repond |
| `GET /models` | Lister les familles de modeles et leurs artefacts |
| `POST /route` | Identifier la famille de logs et le modele choisi |
| `POST /parse` | Parser un log brut vers un CSV Logminer |
| `POST /detect` | Lancer detection + correlation sur un CSV/Parquet |
| `POST /correlate` | Rejouer uniquement la correlation sur un CSV d'anomalies |
| `POST /run` | Lancer parsing optionnel, routage, detection et correlation |

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

## Lien Avec La V1

La V2 appelle les fonctions deja utilisees par la CLI:

```text
route_model()
run_routed_detection()
correlate_anomalies()
run_pipeline()
```

La logique metier reste donc partagee avec la V1. Si l'API devient instable, la
chaine CLI reste utilisable pour la soutenance et les experimentations.
