# SESSION HANDOFF

## Mission

Consolider expérimentalement le mémoire Ariel Logminer sans réécrire le mémoire.

## Current phase

PHASE 2 — comparaison multi-modèles CICIDS2017.

## Current experiment

RandomForest × Infiltration, réutilisation des cinq seeds.

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
- Checkpoint PHASE 1 : `265cdfb`.
- Plan PHASE 2 : 125 résultats, dont 25 réutilisés et 100 nouveaux fits.
- RandomForest × DDoS : 5/5 réutilisés, artefacts validés.
- ExtraTrees × DDoS : 5/5 nouveaux runs terminés ; F1 moyen 0,707001, PR-AUC 0,954894.
- HistGradientBoosting × DDoS : cinq FAILED conservés ; `PermissionError [WinError 5]` lors de la création du pool interne joblib.
- HistGradientBoosting × DDoS : reprise hors bac à sable réussie, F1 moyen 0,016809, rappel 0,008500.
- LogisticRegression × DDoS : 5/5 terminés, F1 0,720357 sur chaque seed, PR-AUC 0,811788.
- SGDLogistic × DDoS : 5/5 terminés, F1 moyen 0,715936, PR-AUC 0,861798.
- DDoS phase 2 complet : RandomForest meilleur F1, ExtraTrees meilleure PR-AUC ; aucun gagnant toutes métriques.
- RandomForest × PortScan : 5/5 résultats réutilisés.
- ExtraTrees × PortScan : F1 moyen 0,008955, rappel 0,004500, PR-AUC 0,855074.
- HistGradientBoosting × PortScan : F1=0, rappel=0, PR-AUC 0,804916.
- LogisticRegression × PortScan : F1 0,000497, rappel 0,000250, PR-AUC 0,527866.
- SGDLogistic × PortScan : F1=0, rappel=0, PR-AUC 0,800987.
- PortScan complet : aucun modèle ne dépasse F1 moyen 0,009947.
- RandomForest × Bot : 5/5 résultats réutilisés, F1 nul.
- ExtraTrees × Bot : 5/5 terminés, F1 nul, PR-AUC 0,440980.
- HistGradientBoosting × Bot : 5/5 terminés, F1 nul, PR-AUC 0,475149.
- LogisticRegression × Bot : 5/5 terminés, F1 nul, PR-AUC 0,313997, 77 FP moyens.
- SGDLogistic × Bot : 5/5 terminés, F1 nul, PR-AUC 0,485505.
- Bot complet : aucun vrai positif pour aucun des cinq modèles.

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
- HistGradientBoosting doit être exécuté hors bac à sable sur cette machine.
- Premier manifeste interrompu par le nom physique ` Label`; correction appliquée, aucune sortie de manifeste partielle conservée.

## Exact next action

Exécuter `rtk python scripts/run_final_experiments.py --resume --phase 2 --scenario Infiltration --model RandomForest`.

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

`python scripts/run_final_experiments.py --resume --phase 2 --scenario Infiltration --model RandomForest`
