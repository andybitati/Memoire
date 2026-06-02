# Guide D'Utilisation D'Ariel Logminer

Ce guide explique comment lancer et utiliser le prototype Ariel Logminer V2. Le
systeme sert a decouvrir des journaux locaux, choisir le modele adapte, detecter
des anomalies candidates, correler les resultats et afficher une synthese dans
le dashboard web.

## 1. Prerequis

- Python avec l'environnement `.venv` du projet.
- Node.js pour le dashboard web.
- Docker Desktop uniquement si l'on veut utiliser Redis via Docker.
- PowerShell administrateur uniquement pour exporter certains journaux Windows
  sensibles, par exemple `Security.evtx`.

Installation Python:

```powershell
cd F:\Cours\TFE
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 2. Lancer Le Systeme

Depuis la racine du projet:

```powershell
cd F:\Cours\TFE
.\.venv\Scripts\python.exe -m uvicorn src.logminer.api:app --host 127.0.0.1 --port 8000
```

Dans un autre terminal:

```powershell
cd F:\Cours\TFE\web\dashboard
node server.mjs
```

Adresses utiles:

```text
Dashboard: http://127.0.0.1:5173
API:       http://127.0.0.1:8000
Docs API:  http://127.0.0.1:8000/docs
```

## 3. Comprendre Le Dashboard

Le dashboard est organise en trois vues.

| Vue | Role |
| --- | --- |
| Vue d'ensemble | Piloter le systeme sans detail technique |
| Resultats | Lire les incidents, anomalies et evenements |
| Technique | Voir Redis, les agents, l'audit et les validations |

La vue d'ensemble affiche un parcours en quatre etapes:

1. Infrastructure: verifie API, Redis et Docker.
2. Acces sensible: demande une autorisation admin si necessaire.
3. Journaux: montre la source choisie par le collecteur.
4. Analyse: indique si le workflow a ete lance.

Le dashboard se rafraichit automatiquement toutes les 5 secondes et relance le
workflow d'analyse autonome lorsque aucune analyse n'est deja en cours. Cette
cadence donne au prototype un comportement temps reel ou quasi temps reel:
collecte/discovery, routage modele, detection, correlation puis affichage.

## 4. Parcours Normal

1. Cliquer sur `Actualiser`.
2. Cliquer sur `Trouver les journaux` si aucune source n'est encore visible.
3. Laisser l'analyse automatique tourner ou cliquer sur `Lancer l'analyse` pour
   forcer un cycle immediat.
4. Ouvrir `Resultats` pour lire les anomalies et evenements.
5. Cliquer sur `Expliquer les resultats` pour obtenir une synthese humaine.

Le rafraichissement automatique et le bouton `Lancer l'analyse` appellent le
workflow autonome:

```text
collecteur -> routeur modele -> detecteur -> correlateur -> dashboard
```

Les sorties sont ecrites dans `data/processed` avec des noms du type:

```text
api_<run_id>_anomalies.csv
api_<run_id>_incidents.csv
api_<run_id>_parsed.csv
```

## 5. Journaux Sensibles Windows

Certains journaux Windows demandent une autorisation administrateur. Le bouton
`Autoriser journaux sensibles` lance une demande via le mecanisme natif Windows.

Ariel Logminer ne lit pas et ne stocke jamais le mot de passe administrateur. Si
Windows affiche une fenetre UAC, l'administrateur valide dans cette fenetre.

Selon la maniere dont le serveur FastAPI a ete lance, Windows peut refuser
d'afficher l'invite UAC depuis le processus en arriere-plan. Dans ce cas,
Ariel Logminer prepare aussi un lanceur interactif:

```text
scripts/generated/run_windows_sensitive_collection_admin.cmd
```

L'administrateur doit alors ouvrir ce fichier avec `Executer en tant
qu'administrateur`. La demande de mot de passe ou de validation apparaitra dans
la fenetre Windows officielle.

Les journaux exportes sont places dans:

```text
data/raw/windows_events_admin
```

Ensuite, relancer:

1. `Trouver les journaux`
2. `Lancer l'analyse`

## 6. Docker Et Redis

Redis sert de bus evenementiel entre agents. Le bouton `Preparer runtime` tente
de verifier Docker et de lancer les services declares dans:

```text
docker-compose.redis.yml
```

Si Docker Desktop affiche:

```text
Virtual Machine Platform not enabled
```

ouvrir PowerShell en administrateur et executer:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName VirtualMachinePlatform
```

Puis redemarrer Windows.

## 7. Journal D'Audit

Ariel Logminer enregistre les actions importantes dans:

```text
data/processed/logminer_audit.jsonl
```

Ce journal contient notamment:

- preparation du runtime Docker;
- demande d'autorisation privilegiee;
- decouverte des journaux;
- execution d'un workflow autonome.

Il est aussi visible dans la vue `Technique` du dashboard.

## 8. Lire Les Resultats

Dans la vue `Resultats`:

- `Incidents correles`: groupes d'evenements lies.
- `Detail incident`: fenetre temporelle, contexte, justification et anomalies
  sources probables de l'incident selectionne.
- `Anomalies candidates`: evenements scores par le modele.
- `Evenements normalises`: lignes sources nettoyees et uniformisees.
- `decision`: boutons de validation, rejet ou reclassement d'une alerte.
- `Exporter`: export CSV des anomalies, evenements ou du detail incident.

Une anomalie candidate n'est pas automatiquement une attaque. Elle doit etre
interpretee avec:

- la severite;
- le message;
- la repetition temporelle;
- la source;
- le contexte utilisateur ou reseau.

Chaque decision analyste est ajoutee au journal d'audit avec l'action
`alert.accept`, `alert.reject` ou `alert.reclassify`. Cela permet de conserver
une trace exploitable pour l'evaluation qualitative et les retours utilisateur.

## 9. Depannage Rapide

| Probleme | Cause probable | Action |
| --- | --- | --- |
| Docker rouge | Moteur Docker indisponible | Activer Virtual Machine Platform puis redemarrer |
| Redis rouge | Conteneur Redis non lance | Cliquer `Preparer runtime` ou lancer Docker Compose |
| Aucun journal trouve | Dossiers `data/raw` vides | Ajouter des logs ou exporter les journaux Windows |
| Security.evtx inaccessible | Droits insuffisants | Cliquer `Autoriser journaux sensibles` |
| Dashboard trop ancien | Node pas relance | Redemarrer `node server.mjs` |
| API indisponible | Uvicorn non lance | Relancer FastAPI sur le port 8000 |

## 10. Commandes De Verification

Verifier l'API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Verifier Redis:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/redis/health
```

Voir l'audit:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/audit
```

Lancer une analyse autonome par API:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/run/discovered `
  -ContentType "application/json" `
  -Body '{"use_redis":true,"max_mb":5}'
```

Mesurer le comportement quasi temps reel:

```powershell
python scripts\benchmark_realtime_workflow.py --cycles 5 --interval-sec 5
```

Verifier la robustesse multi-source et les logs corrompus/incomplets:

```powershell
python scripts\run_robustness_scalability_checks.py
```

## 11. Limites Actuelles

- L'autonomie concerne les journaux accessibles localement.
- Les droits administrateur restent sous controle du systeme d'exploitation.
- Docker ne peut pas etre repare automatiquement si Windows exige une option
  systeme ou un redemarrage.
- Les resultats non supervises sont des signaux candidats, pas des preuves
  definitives d'attaque.
