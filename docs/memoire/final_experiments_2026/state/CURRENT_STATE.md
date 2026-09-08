# CURRENT STATE

Last update: 2026-09-08
Git commit: 6e07c3e (checkpoint final PHASE 2; baseline expérimental 37bccf083f3c8e92a11377cf758cf1e9e183dee9)
Active phase: PHASE 3
Active experiment: Préparation BGL stricte et état Drain3 train-only
Status: HDFS 18/18 COMPLETED — BGL READY

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
- PHASE 2 RandomForest × DDoS : 5/5 résultats réutilisés, aucun refit.
- PHASE 2 ExtraTrees × DDoS : 5/5 nouveaux runs terminés.
- HistGradientBoosting × DDoS : cinq tentatives FAILED dans le bac à sable, traces conservées.
- HistGradientBoosting × DDoS : reprise hors bac à sable réussie, 5/5 runs COMPLETED.
- LogisticRegression × DDoS : 5/5 runs COMPLETED.
- SGDLogistic × DDoS : 5/5 runs COMPLETED.
- Scénario DDoS PHASE 2 : 25/25 résultats disponibles, 20 nouveaux fits et 5 réutilisés.
- RandomForest × PortScan : 5/5 résultats réutilisés.
- ExtraTrees × PortScan : 5/5 nouveaux runs terminés.
- HistGradientBoosting × PortScan : 5/5 runs terminés hors bac à sable.
- LogisticRegression × PortScan : 5/5 runs terminés.
- SGDLogistic × PortScan : 5/5 runs terminés.
- Scénario PortScan PHASE 2 : 25/25 résultats disponibles.
- RandomForest × Bot : 5/5 résultats réutilisés.
- ExtraTrees × Bot : 5/5 nouveaux runs terminés.
- HistGradientBoosting × Bot : 5/5 runs terminés hors bac à sable.
- LogisticRegression × Bot : 5/5 runs terminés.
- SGDLogistic × Bot : 5/5 runs terminés.
- Scénario Bot PHASE 2 : 25/25 résultats disponibles.
- RandomForest × Infiltration : 5/5 résultats réutilisés.
- ExtraTrees × Infiltration : 5/5 nouveaux runs terminés, F1 nul.
- HistGradientBoosting × Infiltration : 5/5 runs terminés hors bac à sable, F1 nul.
- LogisticRegression × Infiltration : 5/5 runs terminés, F1 0,372881.
- SGDLogistic × Infiltration : 5/5 runs terminés, F1 moyen 0,111097 et forte dispersion.
- Scénario Infiltration PHASE 2 : 25/25 résultats disponibles ; phase 2 à 100/125.
- RandomForest × WebAttacks : 5/5 résultats réutilisés.
- ExtraTrees × WebAttacks : 5/5 nouveaux runs terminés, F1 nul.
- HistGradientBoosting × WebAttacks : 5/5 runs terminés hors bac à sable, F1 nul.
- LogisticRegression × WebAttacks : 5/5 runs terminés, F1 0,074614.
- SGDLogistic × WebAttacks : 5/5 runs terminés, F1 nul.
- PHASE 2 terminée : 125/125 artefacts valides, 100 nouveaux fits, 25 réutilisations, aucun échec final.
- Quatre figures et un tableau multi-métrique PHASE 2 générés et inspectés.
- Audit de l'ancien pipeline HDFS/BGL terminé : espace Drain3 séparé, fréquences par partition, rangs test et quota test identifiés.
- Protocole strict HDFS/BGL figé avant inspection des labels des nouvelles fenêtres.
- Venv dédié `.venv-final-experiments` opérationnel avec Drain3 0.9.11 ; environnement global restauré et valide.
- Runner spécialisé phase 3 créé ; dry-run 36/36 plans et test synthétique du seuil réussis.
- HDFS préparé : 50 000 train, 20 000 validation, 20 000 test, zéro bloc partagé.
- État Drain3 HDFS train-only sauvegardé/rechargé : 13 clusters, hash vérifié, aucune mise à jour validation/test.
- HDFS strict : 18/18 résultats terminés, aucun échec.
- Résumé HDFS régénéré sans durées par méthode non comparables.

## In progress

- Aucun run en cours.

## Pending

- Préparer BGL : fenêtres chronologiques, état Drain3 train-only et bundle causal.
- Exécuter les 18 résultats BGL.
- Phases 3 à 12.

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
- Phase 2 planifiée : 125 résultats, dont 25 réutilisations RandomForest et 100 nouveaux ajustements.
- DDoS ExtraTrees : F1 moyen 0,707001 ± 0,003380 ; PR-AUC 0,954894 ; N=5.
- DDoS HistGradientBoosting : F1 moyen 0,016809 ± 0,010885 ; rappel 0,008500 ; PR-AUC 0,853632 ; N=5.
- DDoS LogisticRegression : F1 0,720357 sur chaque seed ; PR-AUC 0,811788 ; entraînement moyen 0,274312 s ; N=5.
- DDoS SGDLogistic : F1 0,715936 ± 0,000813 ; PR-AUC 0,861798 ; entraînement moyen 0,213420 s ; N=5.
- DDoS : RandomForest domine le F1 ; ExtraTrees domine la PR-AUC ; aucune domination multi-métriques.
- PortScan ExtraTrees : F1 0,008955 ± 0,002246 ; rappel 0,004500 ; PR-AUC 0,855074 ; N=5.
- PortScan HistGradientBoosting : F1 et rappel nuls ; PR-AUC 0,804916 ; N=5.
- PortScan LogisticRegression : F1 0,000497 ; rappel 0,000250 ; PR-AUC 0,527866 ; N=5.
- PortScan : aucun modèle ne dépasse F1 moyen 0,009947 ; SGDLogistic et HistGradientBoosting ont F1 nul.
- Bot ExtraTrees : F1 et rappel nuls ; PR-AUC 0,440980 ; N=5.
- Bot HistGradientBoosting : F1 et rappel nuls ; PR-AUC 0,475149 ; N=5.
- Bot LogisticRegression : F1 et rappel nuls ; PR-AUC 0,313997 ; 77 FP moyens ; N=5.
- Bot : les cinq modèles ont F1 et rappel nuls ; meilleure PR-AUC 0,485505 (SGDLogistic), sans vrai positif.
- Infiltration LogisticRegression : F1 0,372881, rappel 0,343750, PR-AUC 0,356763 et MCC 0,369642 ; N=5 mais seulement 32 positifs par test.
- Infiltration SGDLogistic : F1 moyen 0,111097 ± 0,181391 ; résultat instable.
- Infiltration : ExtraTrees, HistGradientBoosting et RandomForest ont F1 et rappel nuls.
- Phase 2 : 125 JSON présents et lisibles, 125 run_id uniques, cinq résultats pour chaque couple modèle/scénario.
- LogisticRegression est premier uniquement par F1 macro (0,233670) et MCC macro (0,186858) parmi les cinq candidats testés.
- HistGradientBoosting a la meilleure PR-AUC macro (0,567697) mais un F1 macro de 0,003362.
- WebAttacks : LogisticRegression F1 0,074614 et rappel 0,039908 ; les quatre autres modèles ont F1 nul.
- L'ancien HDFS/BGL n'a pas de validation séparée et utilise des informations de distribution du test ; il reste exploratoire.
- Le nouveau protocole prévoit 18 résultats par dataset : 15 stochastiques sur cinq seeds et trois déterministes sans pseudo-réplication.
- Prévalence HDFS observée après gel : train 3,716 %, validation 2,995 %, test 0,590 % ; aucune adaptation du protocole.
- HDFS : 13 clusters Drain3 train-only ; templates inconnus test 1,880 %.
- HDFS strict : meilleur F1 Histogram 0,269307 ; IQR 0,268775 ; ensemble 0,242946 ± 0,010487.
- Sur 118 anomalies HDFS test, Histogram détecte 68 vrais positifs avec 319 faux positifs.

## Open issues

- La provenance officielle des copies locales reste `INFORMATION À VÉRIFIER.`.
- Le venv Drain3 repose sur `--system-site-packages`; il n'est pas destiné à exécuter Streamlit à cause des contraintes cachetools incompatibles.
- La mise à jour Graphify est bloquée par un accès refusé Windows.
- HistGradientBoosting nécessite l'exécution hors bac à sable sur cette machine ; reprise réussie.

## Important artifact paths

- `docs/memoire/final_experiments_2026/state/`
- `data/processed/final_experiments_2026/`
- `docs/memoire/final_experiments_2026/environment_final_experiments.json`
- `docs/memoire/final_experiments_2026/dataset_manifest_final.csv`
- `docs/memoire/final_experiments_2026/PHASE_0_COMPLETED.md`
