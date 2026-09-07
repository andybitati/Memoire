# CURRENT STATE

Last update: 2026-09-07
Git commit: 4db70f0 (checkpoint PHASE 0; baseline expérimental 37bccf083f3c8e92a11377cf758cf1e9e183dee9)
Active phase: PHASE 2
Active experiment: Comparaison des modèles CICIDS — préparation du premier batch
Status: READY

## Completed

- Détection du mode NEW.
- État Git et commit initial enregistrés.
- Arborescence isolée `final_experiments_2026` créée.
- Décisions scientifiques D001 à D008 figées.
- Runner central créé et validé en dry-run pour la phase 0 et le batch DDoS de la phase 1.
- Protocole CICIDS final figé dans un fichier de configuration distinct.
- Environnement et manifeste de 11 fichiers avec SHA-256 validés.
- PHASE 0 terminée.
- Batch DDoS : 5/5 runs terminés, aucun échec.
- Batch PortScan : 5/5 runs terminés, aucun échec.
- Batch Bot : 5/5 runs terminés, aucun échec.
- Batch Infiltration : 5/5 runs terminés, aucun échec.
- Batch WebAttacks : 5/5 runs terminés, aucun échec.
- Holdout : 25/25 runs terminés.
- Contrôle random stratifié : 5/5 runs terminés.
- PHASE 1 terminée : 30/30 runs, aucun échec, tableaux et figures produits.

## In progress

- Aucun run en cours.

## Pending

- Préparer la réutilisation traçable des 25 résultats RandomForest de phase 1.
- Lancer les batches modèle × scénario des quatre autres candidats.
- Phases 2 à 12.

## Verified facts

- Aucun ancien artefact de preuve n'a été modifié.
- Le score F1 0,999965 est exclu des nouvelles expériences.
- Le dépôt avait six fichiers non suivis préexistants au démarrage de la mission.
- Le manifeste contient 8 fichiers CICIDS2017, 2 HDFS et 1 BGL, tous hashés.
- Le plan de phase 1 contient 30 runs : 25 holdout et 5 random stratifié.
- DDoS holdout : F1 moyen 0,778774 ± 0,001342 ; rappel 0,637700 ; FP moyen 0 ; N=5.
- PortScan holdout : F1 moyen 0,009947 ± 0,000001 ; rappel 0,005000 ; PR-AUC 0,881982 ; N=5.
- Bot holdout : F1 et rappel nuls ; PR-AUC 0,322471 ; 0 vrai positif sur 1 966 attaques par run ; N=5.
- Infiltration holdout : F1 et rappel nuls sur seulement 32 attaques par run ; résultat négatif mais échantillon positif limité ; N=5.
- WebAttacks holdout : F1 et rappel nuls ; PR-AUC 0,654341 ; 0 vrai positif sur 2 180 attaques par run ; N=5.
- Random stratifié : F1 moyen 0,995142 ± 0,001013 ; N=5.
- Holdout macro : F1 moyen 0,157744 ; dispersion inter-scénarios 0,347193 contre dispersion intra-scénario combinée 0,000600.

## Open issues

- La provenance officielle des copies locales reste `INFORMATION À VÉRIFIER.`.
- Drain3 n'est pas installé dans l'interpréteur actuel.
- La mise à jour Graphify est bloquée par un accès refusé Windows.

## Important artifact paths

- `docs/memoire/final_experiments_2026/state/`
- `data/processed/final_experiments_2026/`
- `docs/memoire/final_experiments_2026/environment_final_experiments.json`
- `docs/memoire/final_experiments_2026/dataset_manifest_final.csv`
- `docs/memoire/final_experiments_2026/PHASE_0_COMPLETED.md`
