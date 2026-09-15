# EXPERIMENT ROUTER REAL — SUMMARY

Objectif: Mesurer la capacité de l'implémentation réellement appelée, `agents.model_router.route_model`, à attribuer la famille de modèle attendue à des fichiers dont la source est connue.

Protocole: Neuf sources identifiées par SHA-256 sont découpées en fichiers CSV séquentiels de 100 lignes, au maximum dix chunks par source. Les noms `chunk_000.csv`, etc., sont neutres. La vraie famille est fixée depuis la source avant routage. Le routeur inspecte jusqu'à 100 lignes et retourne famille, modèle, scores, marge, raisons et fallback. Apache ne fournit qu'un fichier d'une ligne.

Nombre de runs prévus: 81 décisions de routage.

Nombre terminé: 81/81.

Nombre échoué: 0.

## Résultats globaux

- 80/81 fichiers correctement routés.
- Exactitude: `0,987654`.
- Précision macro sur l'union vraies+prédites: `0,888889`.
- Rappel macro sur l'union vraies+prédites: `0,878788`.
- F1 macro sur l'union vraies+prédites: `0,883598`.
- F1 macro limité aux huit familles réellement présentes en vérité terrain: `0,994048`.
- Fallback: 1/81, soit `0,012346`.
- Unknown: 0/81.
- Erreur d'exécution: 0/81.
- Tous les chemins de modèles sélectionnés existent.
- Reprise idempotente: `SKIPPED_ALREADY_COMPLETED`.

La métrique macro principale inclut `fallback`, classe prédite une fois mais absente de la vérité terrain. Sa précision, son rappel et son F1 sont donc nuls. Ce choix pénalise explicitement la fausse route Apache au lieu de la masquer.

## Résultats par famille

| Famille vraie | Support | Précision | Rappel | F1 | Résultat |
| --- | ---: | ---: | ---: | ---: | --- |
| bgl | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| hdfs | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| linux | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| linux_auth | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| network | 11 | 1,000000 | 0,909091 | 0,952381 | 10/10 UNSW corrects, Apache incorrect |
| network_cicids | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| wazuh | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| windows | 10 | 1,000000 | 1,000000 | 1,000000 | 10/10 corrects |
| fallback, prédite seulement | 0 | 0,000000 | 0,000000 | 0,000000 | 1 faux positif |

## Erreur observée

- Source: fixture Apache normalisé, une seule ligne.
- Famille fixée: `network`, cohérente avec la taxonomie de modèles et `KIND_FAMILY["apache"]` sur entrée brute.
- Famille prédite sur la représentation CSV normalisée: `fallback`.
- Marge: `21` points.
- Raison dominante explicite: `format web/SIEM/cloud sans modele specialise`, ajoutant 140 points au fallback.
- Cette erreur révèle une dépendance à la représentation : le même type Apache est associé à `network` à l'état brut, mais son `subtype=apache` normalisé favorise explicitement le fallback.

## Marges de routage

- Minimum: 21, pour l'erreur Apache.
- Chunks corrects: BGL 43 ; HDFS 83 ; Linux/auth 83 ; Windows 133 à 183 ; Linux 167 ; Wazuh 180 ; CICIDS 148 ; UNSW 191.
- Ces valeurs sont des écarts entiers entre scores heuristiques et ne sont pas des probabilités calibrées.

Résultat négatif éventuel: Le routeur choisit le fallback pour Apache normalisé alors que la famille de modèle attendue est network. Aucune conclusion de robustesse Apache n'est permise avec N=1.

Limites:

- L'unité est le fichier dérivé, pas l'événement individuel.
- Les dix chunks d'une source partagent schéma, provenance et préfixe ; ils ne sont pas dix réplications indépendantes.
- Les valeurs `dataset`, `subtype` et `filepath` restent présentes dans les contenus normalisés lorsqu'elles existent ; le routeur est conçu pour les exploiter.
- Une seule source par sous-type, sauf la famille network qui combine UNSW et Apache.
- Le corpus couvre les premiers 1 000 événements seulement.
- La vraie famille Apache repose sur la taxonomie interne de familles de modèles ; elle n'est pas une ontologie externe indépendante.
- Cette expérience mesure le routeur réel ; elle ne remplace pas l'ablation global/spécialisé D005 et ne démontre aucun gain prédictif du routage.
- La provenance officielle des copies locales reste `INFORMATION À VÉRIFIER.`.

Conclusion scientifique: Le routeur réel fonctionne correctement sur 80/81 fichiers dérivés à noms neutres dans ce corpus local. La preuve est forte pour le fonctionnement sur ces représentations, mais limitée pour la généralisation à de nouvelles sources. Une incohérence Apache brut/normalisé est observée. Aucun gain prédictif systématique n'est démontré.

Artefacts:

- `configs/router_evaluation_protocol.json`.
- `data/processed/final_experiments_2026/router_evaluation_raw.csv`.
- `data/processed/final_experiments_2026/router_metrics_by_family.csv`.
- `data/processed/final_experiments_2026/router_confusion_matrix.csv`.
- `data/processed/final_experiments_2026/router_evaluation_summary.json`.
- `tables/router_metrics_by_family.md`.
- `figures/router_confusion_matrix.png`.

