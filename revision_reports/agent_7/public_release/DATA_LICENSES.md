# Licences des données et des modèles

Le code est publié sous licence MIT. Cette licence ne s'applique **pas** aux
données ni aux modèles entraînés sur ces données.

| Élément du dépôt | Origine | Licence / conditions | Statut de vérification |
|---|---|---|---|
| Extraits et dérivés HDFS, BGL (`experiments/phase_dataset_strengthening/...`, `data/verification/public_sources/HDFS_v1/preprocessed/anomaly_label.csv`) | Loghub, Zenodo DOI 10.5281/zenodo.8196385 | CC BY 4.0 | Vérifié dans `data/verification/public_sources/zenodo_8196385_metadata.json` (champ `metadata.license.id = cc-by-4.0`) |
| Dérivés CICIDS2017 (résultats agrégés, modèle `models/random_forest_network_cicids.joblib`) | Canadian Institute for Cybersecurity (UNB) | Conditions publiées par l'éditeur ; citation de Sharafaldin et al. (2018) demandée | [À VÉRIFIER PAR L'AUTEUR sur la page officielle du jeu] |
| Dérivés CSE-CIC-IDS2018 | CIC et Communications Security Establishment ; registre AWS Open Data | Conditions publiées par l'éditeur | [À VÉRIFIER PAR L'AUTEUR] |
| Modèle `models/random_forest_network_unsw_80_20_sampled.joblib` | UNSW-NB15 | Conditions publiées par l'éditeur | [À VÉRIFIER PAR L'AUTEUR] |
| Corpus synthétiques (corrélation, micro-tâches CNP) | Générés par les scripts du dépôt | Même licence que le texte du mémoire [À COMPLÉTER] | — |
| Journaux Windows, Wazuh, syslog de la machine de laboratoire (`experiments/phase_dataset_strengthening/processed/...`) | Machine de l'auteur | Publication soumise à la décision de l'auteur (données personnelles et de sécurité) | [DÉCISION DE L'AUTEUR REQUISE, voir PUBLIC_RELEASE_PLAN.md §3] |

Avant tout dépôt, vérifier que les conditions des jeux CIC et UNSW autorisent
la redistribution d'extraits ou de modèles dérivés. À défaut, retirer ces
éléments de l'archive et documenter la procédure pour les régénérer.
