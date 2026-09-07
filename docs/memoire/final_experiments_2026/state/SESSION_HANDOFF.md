# SESSION HANDOFF

## Mission

Consolider expérimentalement le mémoire Ariel Logminer sans réécrire le mémoire.

## Current phase

PHASE 2 — comparaison multi-modèles CICIDS2017.

## Current experiment

Préparation de la réutilisation traçable RandomForest, puis batches modèle × scénario.

## Completed since previous checkpoint

- Mode NEW détecté.
- Commit initial et état Git relevés.
- Arborescence expérimentale isolée créée.
- Décisions D001 à D008 enregistrées.
- Runner central créé et validé en dry-run.
- Configuration CICIDS multi-seeds figée.
- Environnement et manifeste hashé terminés.
- PHASE 0 clôturée avec son rapport.
- Batch DDoS terminé : 5/5 runs COMPLETED, aucun échec.
- Batch PortScan terminé : 5/5 runs COMPLETED, aucun échec.
- Batch Bot terminé : 5/5 runs COMPLETED, aucun échec.
- Batch Infiltration terminé : 5/5 runs COMPLETED, aucun échec.
- Batch WebAttacks terminé : 5/5 runs COMPLETED, aucun échec.
- Holdout complet : 25/25 runs.
- Contrôle random complet : 5/5 runs.
- PHASE 1 terminée, résumés, tableau et cinq figures produits.

## Key results

- Commit initial : `37bccf083f3c8e92a11377cf758cf1e9e183dee9`.
- Checkpoint PHASE 0 : `4db70f0` (`experiment: freeze final environment`).
- Aucun ancien artefact modifié.
- Onze fichiers prioritaires identifiés par SHA-256.
- Les 30 runs de phase 1 sont détectés comme manquants par le dry-run.
- DDoS : F1 moyen 0,778774, écart-type 0,001342, rappel moyen 0,637700, aucun faux positif sur les cinq tests.
- PortScan : F1 moyen 0,009947, rappel moyen 0,005000, PR-AUC moyenne 0,881982 ; quasi-défaillance au seuil fixe malgré un classement encore informatif.
- Bot : F1=0 sur cinq seeds, aucun vrai positif, PR-AUC 0,322471 pour une prévalence 0,329534.
- Infiltration : F1=0 sur cinq seeds, mais seulement 32 attaques par test ; ne pas extrapoler au scénario complet.
- WebAttacks : F1=0 sur cinq seeds et 2 180 attaques par test ; PR-AUC 0,654341, donc information de classement sans décision positive utile au seuil fixe.
- Random : F1 moyen 0,995142 ± 0,001013.
- Holdout macro : F1 0,157744 ; la dispersion inter-scénarios domine très largement la dispersion entre seeds.

## Files created or modified

- `docs/memoire/final_experiments_2026/state/*`
- Répertoires `data/processed/final_experiments_2026` et `docs/memoire/final_experiments_2026/{tables,figures,logs,configs}`.

## Current blockers

- `drain3` absent de l'interpréteur courant ; requis seulement en phase 3.
- `graphify update .` échoue avec `[WinError 5] Accès refusé`.
- Premier manifeste interrompu par le nom physique ` Label`; correction appliquée, aucune sortie de manifeste partielle conservée.

## Exact next action

Implémenter la réutilisation des résultats RandomForest de phase 1, puis exécuter le dry-run complet de phase 2.

## Read only these files first

- `state/CURRENT_STATE.md`
- `state/NEXT_ACTION.md`
- `state/DECISIONS.md`
- `state/EXPERIMENT_LEDGER.csv`
- `configs/cicids_final_protocol.json`
- `scripts/run_final_experiments.py`
- `dataset_manifest_final.csv`
- `PHASE_0_COMPLETED.md`

## Do not reread

- Le mémoire complet.
- Les anciens rapports multi-VM et éditoriaux.

## Resume command

`python scripts/run_final_experiments.py --resume --phase 2 --dry-run`
