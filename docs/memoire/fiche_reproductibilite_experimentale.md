# Fiche Reproductibilite Experimentale

Date de mesure: 2026-06-03

Cette fiche rassemble les informations minimales a rapporter dans le memoire ou
dans un article pour permettre l'interpretation des benchmarks Logminer.

## Environnement Local

| Element | Valeur |
| --- | --- |
| Type de machine | Laptop |
| Systeme | Windows 11 / Microsoft Windows NT 10.0.26200.0 |
| Plateforme Python | Windows-11-10.0.26200-SP0 |
| Processeur | Intel64 Family 6 Model 142 Stepping 10, GenuineIntel |
| Processeurs logiques detectes | 8 |
| RAM totale detectee | 7.85 GB |
| PowerShell | 7.5.5 |
| Python | 3.12.3 |
| Chemin environnement | `.venv` |
| API benchmarkee | FastAPI Logminer, `http://127.0.0.1:8000` |
| Dashboard | `http://127.0.0.1:5173` |

Note: les informations WMI detaillees ont retourne `Acces refuse` dans
l'environnement courant. Les valeurs ci-dessus proviennent de Python, `platform`
et `psutil`. Pour une soumission article finale, le nom commercial exact du
processeur peut etre complete manuellement si necessaire.

## Versions Principales

| Bibliotheque | Version |
| --- | --- |
| pandas | 3.0.3 |
| numpy | 2.4.5 |
| scikit-learn | 1.8.0 |
| psutil | 7.2.2 |
| FastAPI | 0.136.3 |
| uvicorn | 0.47.0 |
| Streamlit | 1.57.0 |
| Redis client | 8.0.0 |
| pyarrow | 24.0.0 |
| joblib | 1.5.3 |
| cairosvg | 2.9.0 |
| svglib | 1.6.0 |
| reportlab | 4.5.1 |

## Commande Campagne CPU/RAM

```powershell
.\.venv\Scripts\python.exe scripts\run_resource_campaign.py --cycles 30 --interval-sec 2 --max-mb 5
```

Sorties:

- `data/processed/resource_campaign.csv`;
- `docs/memoire/tables/table_resource_campaign_multicycle.md`;
- `docs/memoire/figures/fig_resource_campaign_multicycle.svg`.

## Resultats Campagne CPU/RAM

| Agent | Cycles | Workflow moy. s | Workflow max s | CPU equiv. moy. | CPU machine moy. | RAM moy. MB |
| --- | --- | --- | --- | --- | --- | --- |
| API / Orchestrateur | 30 | 9.3300 | 21.6007 | 59.61 | 7.45 | 187.82 |
| Processus Logminer | 30 | 9.3300 | 21.6007 | 3.26 | 0.41 | 495.41 |

Interpretation:

- `CPU equiv.` represente le CPU cumule en equivalent coeur; il peut depasser
  100% sur une machine multi-coeurs.
- `CPU machine` represente le CPU normalise par rapport aux 8 processeurs
  logiques detectes.
- Les mesures representent une execution locale du prototype; elles ne prouvent
  pas une scalabilite multi-machine.

## Commande Benchmark Temps Reel

Le benchmark temps reel deja consolide dans les tableaux du memoire repose sur
10 cycles de `/run/discovered`, avec 8 537 lignes par cycle.

Resultats:

- latence moyenne workflow: 8.2012 s;
- latence minimale workflow: 3.1672 s;
- latence maximale workflow: 15.3289 s.

## Commande Campagne Redis Agents Intelligents

```powershell
python scripts\run_intelligent_redis_campaign.py --workers 3 --repetitions 50 --cycles 60 --max-parallel-tasks 2
```

Run retenu: `redis-campaign-20260717161257`.

Resultats:

- 150 taches enfilees;
- 150 taches uniques terminees;
- 0 echec;
- 0 pending final;
- 0 perte estimee;
- 1 panne simulee avant acquittement et reprise par `redis-recovery-agent`;
- duree observee depuis Redis: 102.4202 s;
- debit observe: 1.4646 taches/s;
- latence p95/p99: 5.3567 s / 8.2873 s.

Sorties:

- `data/processed/intelligent_redis_long_campaign_summary.json`;
- `docs/memoire/tables/table_intelligent_redis_long_campaign.md`;
- `docs/architecture/intelligent_agents_redis_campaign_summary.md`.

## Informations A Completer Avant Soumission Externe

- nom commercial exact du CPU, si exige;
- stockage utilise si pertinent;
- charge systeme concurrente pendant les mesures;
- commit Git ou archive du code;
- taille exacte des fichiers sources utilises;
- hash ou version des datasets si la conference l'exige.
