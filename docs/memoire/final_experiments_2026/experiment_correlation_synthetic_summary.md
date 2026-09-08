# Corrélation d'incidents — validation synthétique contrôlée

## Objectif

Évaluer l'implémentation réelle `correlate_anomalies` sur une vérité terrain synthétique figée avant exécution, sans revendiquer une validation SOC réelle.

## Protocole

- Fenêtre fixe: 15 minutes, arrondie par plancher temporel.
- Clés: `host`, `user`, `source`, `category`, `subcategory`, `proto`, `dst_port`.
- Vérité terrain séparée de l'entrée du corrélateur.
- 19 événements: 16 anomalies dans 6 incidents vrais et 3 bruits non anomaux.
- Cas contrôlés: deux incidents stables, un incident traversant une frontière de fenêtre, deux incidents distincts aux clés identiques dans la même fenêtre, un incident stable supplémentaire et trois bruits.
- Mesure pairwise sur les 120 paires d'événements anomaux.

## Résultats

- Incidents produits: 6 pour 6 incidents vrais.
- Précision pairwise: `0.764706`.
- Rappel pairwise: `0.866667`.
- F1 pairwise: `0.812500`.
- Comptages pairwise: TP=13, FP=4, FN=2, TN=101.
- Incidents vrais fragmentés: 1.
- Incidents prédits fusionnant plusieurs incidents vrais: 1.
- Bruits exclus: 3/3.

## Interprétation

Le corrélateur fonctionne conformément à ses règles explicites sur les cas stables et filtre le bruit marqué non anomal. La fenêtre fixe peut fragmenter un incident traversant sa frontière. Des incidents indépendants indiscernables par les clés disponibles sont fusionnés. Cette expérience teste la logique déterministe sur scénarios construits; elle ne mesure ni une généralisation à des incidents réels ni une performance SOC.

## Artefacts

- `configs/correlation_synthetic_protocol.json`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_input.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_truth.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_incidents.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_pairs.csv`.
- `data/processed/final_experiments_2026/correlation_synthetic_summary.json`.
- `tables/correlation_synthetic_metrics.md`.
- `figures/correlation_synthetic_metrics.png`.
