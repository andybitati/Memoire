# Convention canonique des artefacts experimentaux

Cette convention s'applique aux nouvelles campagnes. Les artefacts historiques
restent immuables afin de preserver leurs hashes et les references du memoire.

## Identifiant de run

Format : `<experiment>_<topology>_YYYYMMDDTHHMMSSZ`.

Exemple : `cnp_endurance_multivm_20260918T143000Z`.

Contraintes : minuscules ASCII, chiffres et underscores uniquement. Le timestamp
est toujours UTC. Un run ne reutilise jamais l'identifiant d'un run precedent.

## Noms de fichiers

Tous les fichiers produits par un run commencent par son `run_id` et utilisent
exactement un separateur double underscore avant leur role :

- `<run_id>__summary.json` : resultat consolide faisant autorite ;
- `<run_id>__task_metrics.csv` : une ligne par tache ;
- `<run_id>__messages.jsonl` : trace des messages du protocole ;
- `<run_id>__<agent_id>.log` : sortie d'un agent distant identifie ;
- `<run_id>__checkpoint.json` : progression atomique du run actif ;
- `<run_id>__runner.log` : sortie standard et erreurs du processus ;
- `<run_id>__error.log` : erreur terminale eventuelle ;
- `<run_id>__report.md` : rapport lisible ;
- `<run_id>__manifest.json` : chemins, tailles et SHA-256.

Les noms `final`, `latest`, `new`, `old`, `copy` et `result2` sont interdits pour
les nouveaux artefacts, car ils ne decrivent ni le protocole ni le statut.

## Statuts

Le ledger est append-only. Les statuts autorises sont `RUNNING`, `COMPLETED`,
`FAILED`, `INTERRUPTED`, `SUPERSEDED` et `LEGACY`. Un resultat `LEGACY` reste
valide dans son ancien protocole mais ne porte pas les conclusions de
l'architecture courante.

## Hierarchie

Chaque phase suit la meme structure : `configs/`, `raw/`, `processed/`,
`aggregated/`, `figures/`, `logs/`, `reports/` et `manifests/`. Le ledger de
phase se nomme toujours `LEDGER.csv`; le registre transversal reste
`state/EXPERIMENT_LEDGER.csv`.
