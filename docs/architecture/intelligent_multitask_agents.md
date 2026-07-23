# Architecture Agents Intelligents Multi-Taches

Date: 2026-07-17

Cette branche vise a rapprocher Logminer du titre initial du memoire:

> Detection d'anomalies distribuee avec agents intelligents multi-taches.

L'objectif technique est de rendre cette phrase defendable par des preuves
executables, et non seulement par une formulation redactionnelle.

## Criteres De Reussite

| Critere | Definition verifiable | Etat branche |
| --- | --- | --- |
| Agent logiciel | Entite avec identifiant, capacites, memoire, decisions et traces | En place via `MultiTaskIntelligentAgent` |
| Multi-taches | Un meme agent execute plusieurs types de taches | En place: discovery, parsing, routage, detection, correlation |
| Intelligence operationnelle | Selection de taches selon priorite, confiance, cout et historique | En place: `score_task`, memoire succes/erreurs |
| Autonomie faible | Cycle heartbeat -> perception des taches -> choix -> action -> memoire | En place localement |
| Memoire adaptative | Capitalisation des executions, erreurs, decisions et retours analyste | En place comme base auditable; reentrainement controle en perspective |
| Distribution | Plusieurs processus agents consomment un bus partage | Valide localement via Redis Streams, voir `intelligent_agents_redis_proof.md` |
| Tolerance aux pannes | Jobs non acquittes recuperables, erreurs tracees | En place: reprise via `XAUTOCLAIM` et panne simulee avant `ack` |
| Preuve experimentale | Scripts reproductibles et sorties auditables | En place: demos locales, Redis distribue, campagne longue 150 taches panne/reprise |

## Nouveaux Composants

- `src/logminer/agents/intelligent_runtime.py`
  - `AgentCapability`: competence annoncee par un agent;
  - `AgentTask`: tache transportable;
  - `MultiTaskIntelligentAgent`: agent capable de choisir et executer plusieurs taches;
  - `InMemoryTaskSource`: source locale pour demonstrations;
  - `RedisTaskSource`: source distribuee via Redis Streams.

- `scripts/run_intelligent_agents_demo.py`
  - demonstration locale sans Redis;
  - execute en parallele `discover.logs`, `parse.logs` et `route.model`;
  - produit une memoire et un bus JSONL.

- `scripts/logminer_intelligent_agent_worker.py`
  - worker Redis Streams;
  - permet plusieurs agents/processus consommateurs;
  - publie heartbeat, decisions et resultats dans `logminer:events`.

- `src/logminer/agents/supervisor_agent.py` et `src/logminer/agents/audit.py`
  - conservent une memoire persistante du superviseur;
  - tracent les decisions analyste issues du dashboard;
  - relisent les rejets/reclassements audites pour ajuster la selection;
  - fournissent la base d'une reduction future plus mesuree des faux positifs par feedback.

- `scripts/run_intelligent_redis_campaign.py`
  - enfile une campagne de taches multi-types;
  - lance plusieurs workers Redis;
  - simule une panne avant acquittement;
  - mesure repartition, pending, pertes estimees et latences p95/p99.

## Commandes De Validation

Demo locale:

```powershell
python scripts\run_intelligent_agents_demo.py --json
```

Verification syntaxique:

```powershell
python -m py_compile src\logminer\agents\intelligent_runtime.py scripts\run_intelligent_agents_demo.py scripts\logminer_intelligent_agent_worker.py
```

Worker Redis, apres lancement de Redis:

```powershell
python scripts\logminer_intelligent_agent_worker.py --enqueue-demo --cycles 1
python scripts\logminer_intelligent_agent_worker.py --consumer worker-2 --cycles 1 --claim-idle-ms 30000
```

Campagne Redis panne/reprise:

```powershell
python scripts\run_intelligent_redis_campaign.py --workers 3 --repetitions 4
```

## Ce Qui Reste Pour Atteindre 95%

1. Ajouter une ablation:
   - pipeline centralise;
   - agent unique multi-taches;
   - plusieurs agents Redis;
   - panne/reprise.
2. Integrer ces preuves dans le chapitre resultats du memoire.
3. Tester deux machines physiques ou deux VM pour remplacer la distribution locale multi-processus.

## Preuve Longue Redis Du 17/07/2026

Le run `redis-campaign-20260717161257` a execute 150 taches Redis avec trois
workers principaux, une panne volontaire avant acquittement et un worker de
reprise. Resultat: 150 taches uniques terminees, 0 echec, 0 pending final,
debit observe 1.4646 taches/s et latence p95/p99 de 5.3567 s / 8.2873 s.

Cette preuve suffit pour le memoire sur le point "distribution locale
multi-processus + reprise". Elle ne remplace pas un deploiement multi-machine,
qui reste une perspective separee.

## Position Scientifique

Avec cette branche, le terme agent devient plus solide: chaque agent possede
des capacites, choisit ses taches, execute plusieurs competences et conserve
une memoire. Cette memoire doit etre lue comme une adaptation comportementale:
elle aide a prioriser, eviter des repetitions et documenter les choix; elle ne
constitue pas un apprentissage par renforcement ni un reentrainement automatique
des modeles. Le systeme devient distribue lorsque plusieurs workers Redis sont
lances dans des processus ou machines differentes.

La revendication forte reste a valider experimentalement: reduction mesuree
des faux positifs, boucle d'apprentissage actif, surveillance du concept drift
et deploiement multi-machine.
