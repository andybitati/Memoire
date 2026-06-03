# Protocole Campagne CPU/RAM Multi-Cycles

Objectif: produire une preuve experimentale de l'objectif 7 sur plusieurs
cycles d'analyse, au lieu d'un simple instantane CPU/RAM.

## Precondition

L'API FastAPI Logminer doit deja etre lancee:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.logminer.api:app --host 127.0.0.1 --port 8000
```

Verifier:

```powershell
Invoke-WebRequest -UseBasicParsing -Uri http://127.0.0.1:8000/health
```

## Commande Recommandee

Campagne courte pour demonstration:

```powershell
.\.venv\Scripts\python.exe scripts\run_resource_campaign.py --cycles 5 --interval-sec 2 --max-mb 5
```

Campagne plus solide pour memoire/article:

```powershell
.\.venv\Scripts\python.exe scripts\run_resource_campaign.py --cycles 30 --interval-sec 2 --max-mb 5
```

## Sorties

Le script produit:

- `data/processed/resource_campaign.csv`;
- `docs/memoire/tables/table_resource_campaign_multicycle.md`;
- `docs/memoire/figures/fig_resource_campaign_multicycle.svg`.

## Colonnes Mesurees

- `cycle`;
- `workflow_sec`;
- `input_rows`;
- `anomalies_rows`;
- `incidents_rows`;
- `agent`;
- `cpu_equiv_core_percent`;
- `cpu_machine_percent`;
- `memory_mb`;
- `logical_cpus`.

## Interpretation

- `cpu_equiv_core_percent`: CPU cumule en equivalent coeur. Une valeur
  superieure a 100% signifie que plusieurs coeurs/processus sont utilises.
- `cpu_machine_percent`: CPU normalise sur l'ensemble de la machine, donc
  interpretable entre 0 et 100%.
- `memory_mb`: memoire residente du processus ou groupe de processus agent.

## Critere D'Acceptation

Pour une preuve minimale:

- au moins 5 cycles `ok`;
- presence d'au moins un agent API/orchestrateur;
- latence moyenne et maximale renseignees;
- CPU/RAM moyens et maximaux par agent.

Pour une preuve article:

- 30 cycles ou plus;
- meme source de logs ou meme limite `max_mb`;
- mention de la machine utilisee;
- moyenne, maximum et ecart-type si necessaire;
- discussion des pics de latence.

## Limite

Cette campagne mesure le prototype local. Elle ne prouve pas a elle seule la
scalabilite multi-machine; elle sert a quantifier la charge du workflow local et
du dashboard/API.
