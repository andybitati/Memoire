# EXPERIMENT MODEL UPDATE END-TO-END — SUMMARY

Objectif: Vérifier fonctionnellement la boucle complète d'entraînement d'un candidat, d'évaluation courant/candidat, de décision selon un seuil minimal, de sauvegarde, de promotion ou de rejet, et d'audit.

Protocole: Trois cas ont été figés avant exécution dans `configs/model_update_e2e_plan.json`. Ils utilisent des copies isolées de modèles sous `data/processed/final_experiments_2026/phase_4`, le même holdout DDoS local CICIDS2017 seed 42 et la même métrique F1. Le seuil de promotion est `delta >= 0,02`. L'option `--promote` est activée. Aucun chemin de modèle de production n'appartient au plan.

Nombre de runs prévus: 3 comparaisons fonctionnelles.

Nombre terminé: 3/3.

Nombre échoué: 0.

## Données et modèles

- Bundle d'entraînement: 16 000 lignes, 78 caractéristiques, 50 % de positifs, SHA-256 `28c8e20632d29cf2009e4e01d5b199bc73c28cf773e0e61af7f8e8eee50da0de`.
- Évaluation gelée: 8 000 lignes, 78 caractéristiques, 50 % de positifs, SHA-256 `23019860997b8071e0922c52c1710e10b017adcc20f53121872e3875dc5a3126`.
- Cas promotion: ExtraTrees courant contre RandomForest candidat.
- Cas rejet: RandomForest courant contre SGDLogistic candidat.
- Cas gain insuffisant: ExtraTrees courant contre LogisticRegression candidat.
- La seed 42 et les relations attendues provenaient de résultats déjà observés en phase 2. Ces cas testent donc les branches logicielles ; ils ne constituent pas une nouvelle validation prédictive indépendante.

## Résultats

| Cas | F1 courant | F1 candidat | Delta | Seuil | Décision |
| --- | ---: | ---: | ---: | ---: | --- |
| Promotion | 0,711340 | 0,779185 | +0,067845 | 0,020000 | candidat promu |
| Candidat inférieur | 0,779185 | 0,716022 | -0,063163 | 0,020000 | courant conservé |
| Gain positif insuffisant | 0,711340 | 0,720357 | +0,009016 | 0,020000 | courant conservé |

## Intégrité

- Promotion: hash courant avant `13f009d7337fb5a1d59ea27979c516dcaeb23dda91169ccba713028146313beb` ; hash backup identique ; hash candidat et courant après `4eea1f245e8810915eccfca8d568daefa49ba36ca254dd1a129c8d0357bff106`.
- Rejet inférieur: hash courant avant et après `bc2ce2ed6a0343d383f643eaea982406ef840c3fb8eaedf8b7f3e8ce45051880` ; candidat `a2963b84cefccac58ccc881357562dcb55d2a552780d08c9d822caca4637325f`.
- Gain insuffisant: hash courant avant et après `8f333fadf6f57482e45e33dd9b57f188511edde9837c05d488b0f2fc5c1fb7cb` ; candidat `aeb4902254490eeb2ba6a8b3b57a4995589d8475c2ef49d6d9e2c04de8c42840`.
- Une seule sauvegarde existe, uniquement pour le cas promu.
- Trois candidats réels ont été entraînés.
- L'audit explicite contient le résultat global de l'exécution et se trouve dans l'espace expérimental isolé.
- `model_update_integrity_report.json` indique `all_integrity_checks_passed=true` et `production_models_touched=false`.

## Statut exact

| Dimension | Statut | Preuve ou limite |
| --- | --- | --- |
| Code présent | IMPLÉMENTÉ | entraînement, évaluation, seuil, backup, copie et audit dans `monthly_model_retraining.py` |
| Dry-run | TESTÉ | vérifié avant l'exécution réelle |
| Comparaison courant/candidat | TESTÉ | trois évaluations réelles sur le même CSV gelé |
| Promotion | TESTÉ | une copie candidat→courant observée et vérifiée par hash |
| Rejet | TESTÉ | deux courants inchangés vérifiés par hash |
| Performance prédictive indépendante | NON ÉVALUÉ | scénarios choisis à partir de résultats phase 2 déjà connus |
| Fonctionnement périodique en production | NON ÉVALUÉ | aucun ordonnanceur ni cycle prolongé testé ici |
| Apprentissage continu autonome | PERSPECTIVE | aucune preuve correspondante |

Résultat négatif éventuel: Le candidat SGDLogistic est inférieur au courant (`delta=-0,063163`) et LogisticRegression s'améliore sans atteindre le seuil (`delta=+0,009016`). Ces deux non-promotions sont des résultats fonctionnels attendus et conservés.

Limites:

- Une seule seed, un seul scénario DDoS et une seule partition gelée sont utilisés.
- La sélection des trois paires exploite des résultats antérieurs ; aucune conclusion prédictive nouvelle n'est permise.
- Les modèles sont des copies expérimentales et non des artefacts en service.
- Aucun test de concurrence, d'ordonnancement mensuel réel, de dérive, de panne pendant la copie ou de rollback opérationnel n'est réalisé.
- La provenance officielle des copies locales CICIDS2017 reste non démontrée ; seuls leurs hashes locaux sont traçables.

Conclusion scientifique: La procédure contrôlée de mise à jour est testée fonctionnellement de bout en bout sur trois branches isolées : promotion avec sauvegarde, rejet d'un candidat inférieur et rejet d'un gain inférieur au seuil. Elle n'est pas une preuve d'apprentissage continu autonome, de sûreté de production ou de gain prédictif généralisable.

Artefacts:

- `configs/model_update_e2e_plan.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_preparation.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_end_to_end_report.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_{promotion,rejection,min_delta}_case.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_integrity_report.json`.
- `data/processed/final_experiments_2026/phase_4/model_update_audit.jsonl`.
- `data/processed/final_experiments_2026/phase_4/model_update_decisions.csv`.
- `tables/model_update_end_to_end.md`.
- `figures/model_update_promotion_rejet.png`.

