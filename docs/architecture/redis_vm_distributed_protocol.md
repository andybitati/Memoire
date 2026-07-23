# Protocole De Validation Redis Multi-VM

Objectif: transformer la preuve actuelle `local multi-processus` en preuve
`multi-machine locale` avec un bus Redis unique et des workers executes depuis
les VM Debian et Ubuntu.

## Principe

La machine Windows heberge Redis et le depot principal. Les VM Debian et Ubuntu
executent chacune un ou plusieurs workers Logminer qui se connectent au Redis
Windows par l'adresse IP de l'hote. Les taches sont enfilees une seule fois,
puis consommees par des workers situes sur des machines differentes.

La preuve attendue n'est pas une scalabilite SOC industrielle. Elle doit montrer:

- au moins deux machines consommatrices distinctes;
- des taches terminees par chaque VM;
- aucune tache finale en attente;
- reprise de taches non acquittees si un worker est interrompu;
- export JSON/Markdown conservant la repartition par agent et par type.

## Preparation Reseau

1. Avec VirtualBox en NAT, conserver la configuration existante et utiliser
   l'adresse speciale de l'hote depuis l'invite:

```text
redis://10.0.2.2:6379/0
```

2. Si les VM sont placees en `Bridge Adapter`, relever l'adresse IP Windows
   accessible depuis les VM:

```powershell
ipconfig
```

3. Tester depuis chaque VM, en remplacant l'adresse selon le mode reseau:

```bash
ping 10.0.2.2
nc -vz 10.0.2.2 6379
```

4. Lancer Redis sur Windows:

```powershell
docker compose -f docker-compose.redis.yml up -d
docker exec logminer-redis redis-cli ping
```

5. Si le pare-feu Windows bloque le port 6379, autoriser ce port uniquement sur
le reseau prive de laboratoire.

## Preparation Des VM

Sur chaque VM:

```bash
git clone <URL_DU_DEPOT> Logminer
cd Logminer
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-container.txt
```

Si le depot est deja copie dans les VM, verifier seulement:

```bash
python scripts/logminer_intelligent_agent_worker.py --help
```

## Campagne Courte De Validation

Depuis Windows, le script d'orchestration prepare l'environnement, verifie
`VBoxManage`, confirme Redis, controle l'etat des VM et affiche les commandes
invites:

```powershell
.\scripts\run_vbox_redis_validation.ps1 -EnqueueDemo
```

Pour un stream de validation isole:

```powershell
.\scripts\run_vbox_redis_validation.ps1 `
  -EnqueueDemo `
  -TaskStream logminer:agent_tasks:vbox_smoke `
  -RunId redis-vbox-smoke
```

Si les additions invitees VirtualBox permettent `guestcontrol`, les workers
peuvent etre lances depuis Windows en passant les identifiants au script:

```powershell
.\scripts\run_vbox_redis_validation.ps1 `
  -EnqueueDemo `
  -RunGuestWorkers `
  -DebianUser <UTILISATEUR_DEBIAN> `
  -DebianPassword <MOT_DE_PASSE_DEBIAN> `
  -UbuntuUser <UTILISATEUR_UBUNTU> `
  -UbuntuPassword <MOT_DE_PASSE_UBUNTU>
```

Ne pas conserver les mots de passe dans le depot. Les transmettre uniquement
au lancement du script.

Si `guestcontrol` n'est pas disponible, activer les redirections SSH NAT:

```powershell
.\scripts\run_vbox_redis_validation.ps1 -EnsureSshForwarding
```

Puis se connecter aux VM sur `localhost:2222` pour Debian et `localhost:2223`
pour Ubuntu, a condition qu'un serveur SSH soit installe et actif dans les
invites.

Sur Windows, enfile les taches:

```powershell
python scripts/logminer_intelligent_agent_worker.py `
  --redis-url redis://localhost:6379/0 `
  --enqueue-demo `
  --enqueue-only `
  --consumer windows-seeder `
  --cycles 1
```

Sur Debian:

```bash
python scripts/logminer_intelligent_agent_worker.py \
  --redis-url redis://10.0.2.2:6379/0 \
  --consumer debian-worker-1 \
  --cycles 20 \
  --claim-idle-ms 30000 \
  --memory data/processed/debian-worker-1-memory.json
```

Sur Ubuntu:

```bash
python scripts/logminer_intelligent_agent_worker.py \
  --redis-url redis://10.0.2.2:6379/0 \
  --consumer ubuntu-worker-1 \
  --cycles 20 \
  --claim-idle-ms 30000 \
  --memory data/processed/ubuntu-worker-1-memory.json
```

## Campagne Panne/Reprise

1. Lancer les deux workers VM.
2. Interrompre volontairement un worker avant la fin.
3. Laisser l'autre worker continuer avec `--claim-idle-ms 30000`.
4. Verifier les pending Redis:

```powershell
docker exec logminer-redis redis-cli XPENDING logminer:agent_tasks logminer-intelligent-agents
```

5. Exporter les evenements:

```powershell
docker exec logminer-redis redis-cli XRANGE logminer:events - + COUNT 2000
```

## Campagnes Executees Le 2026-07-22

Deux validations multi-VM ont ete executees avec Redis sur Windows, Debian et
Ubuntu en NAT VirtualBox.

### Campagne equilibree

Script:

```powershell
.\scripts\run_vbox_redis_balanced_campaign.ps1
```

Resultat retenu:

| Indicateur | Valeur |
| --- | ---: |
| Taches enfilees | 12 |
| Taches terminees | 12 |
| Taches uniques terminees | 12 |
| Taches echouees | 0 |
| Pending final Redis | 0 |
| Taches Debian | 8 |
| Taches Ubuntu | 4 |

### Campagne panne/reprise

Script:

```powershell
.\scripts\run_vbox_redis_recovery_campaign.ps1
```

Resultat retenu:

| Indicateur | Valeur |
| --- | ---: |
| Taches enfilees | 3 |
| Taches terminees | 3 |
| Taches uniques terminees | 3 |
| Taches echouees | 0 |
| Pannes simulees avant ack | 1 |
| Taches prises avant panne | 1 |
| Taches de panne reprises | 1 |
| Pending final Redis | 0 |
| Taches Ubuntu recovery | 3 |

Lecture: Debian a volontairement pris une tache sans l'acquitter, puis Ubuntu a
reclame cette tache pending et l'a terminee. Le patch runtime conserve
`XAUTOCLAIM` quand il est disponible et utilise `XPENDING` + `XCLAIM` comme
fallback pour les clients Redis plus anciens.

### Campagne endurance supervisee 1 h

Scripts:

```powershell
.\scripts\run_vbox_redis_1h_campaign.ps1
python scripts\summarize_vbox_redis_1h_campaign.py `
  --run-id redis-vbox-1h-20260722153650 `
  --task-stream logminer:agent_tasks:vbox_1h:20260722153650 `
  --enqueue-iterations 175
```

Resultat retenu:

| Indicateur | Valeur |
| --- | ---: |
| Duree cible | 3600 s |
| Iterations d'enfilement | 175 |
| Taches enfilees | 525 |
| Entrees lues par le groupe Redis | 525 |
| Taches acquittees par le groupe | 525 |
| Lag final Redis | 0 |
| Pending final Redis | 0 |
| Echecs observes dans la fenetre evenements | 0 |

Lecture: la campagne d'une heure est exploitable comme preuve d'endurance
multi-VM supervisee. Les workers Debian et Ubuntu ont consomme le meme stream
Redis. Des relances supervisees ont ete necessaires parce que les sessions
VirtualBox `guestcontrol` peuvent s'interrompre, mais Redis ne conserve aucune
tache pending et le groupe termine avec un lag nul.

## Criteres De Validation Pour Le Memoire

La validation multi-VM est acceptable si le tableau final indique:

- `debian-worker-*` a termine au moins une tache;
- `ubuntu-worker-*` a termine au moins une tache;
- le total des taches uniques terminees est egal au nombre de taches enfilees;
- le pending final est nul ou explique;
- au moins une reprise est observee si la panne/reprise est testee.

## Formulation Scientifique

Formulation a utiliser:

> La campagne Redis multi-VM montre que les agents peuvent consommer une file
> commune depuis plusieurs machines virtuelles connectees au meme bus. Elle
> etend la preuve locale multi-processus vers une distribution reseau de
> laboratoire, sans constituer encore une validation SOC industrielle.
