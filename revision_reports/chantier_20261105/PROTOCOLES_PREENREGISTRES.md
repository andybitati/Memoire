# Registre des protocoles préenregistrés (chantier 2026-11-05)

Procédure : décision C13-proc de `ETAT_CHANTIER.md`. Une ligne par protocole, ajoutée **avant** l'exécution et commitée avec le fichier du protocole. Ne jamais modifier une ligne existante : un écart s'ajoute en section « Écarts ».

| ID | Agent | Fichier du protocole | SHA-256 | Horodatage UTC | Commit |
|---|---|---|---|---|---|
| E-H4-HDFS-BLOCK-BASELINES | 4 | `revision_reports/chantier_20261105/agent_4/protocoles/E-H4-HDFS-BLOCK-BASELINES.md` | `9bdd07555b59bea54ea625c1ecf6491381aa0bdca6f83b1481f5f21e87e820cc` | `2026-11-05T12:29:53.6488951Z` | ce commit (`Protocole E-H4-HDFS-BLOCK-BASELINES préenregistré`) |
| E-H3B-FAMILY-MODELS | 4 | `revision_reports/chantier_20261105/agent_4/protocoles/E-H3B-FAMILY-MODELS.md` | `a0aa90c857e01b6ae428871270f9addfe6f098ab4503fec6c5db77337c8b276d` | `2026-11-05T12:29:53.6488951Z` | ce commit (`Protocole E-H3B-FAMILY-MODELS préenregistré`) |
| E-H5-MEMORY-RELIABILITY | 5 | `revision_reports/chantier_20261105/agent_5/protocoles/E-H5-MEMORY-RELIABILITY.md` | `b5f782c7d72ba57ef4f9fa35e7b9a474b9953bcaeafab5779f345e75206db48e` | `2026-11-05T14:40:44Z` | ce commit (`Protocole E-H5-MEMORY-RELIABILITY préenregistré`) |
| E-CNP-STATIC-ASSIGNMENT | 5 | `revision_reports/chantier_20261105/agent_5/protocoles/E-CNP-STATIC-ASSIGNMENT.md` | `d2f699b5c30e0611a62f9138583e44c11dca8a31568be4001eeb768f895855bb` | `2026-11-05T14:40:48Z` | ce commit (`Protocole E-CNP-STATIC-ASSIGNMENT préenregistré`) |

## Écarts au protocole

| ID | Écart | Raison | Effet sur la conclusion |
|---|---|---|---|
| E-H4-HDFS-BLOCK-BASELINES | Première tentative arrêtée avant calcul : remplacement dans le programme de la clé JSON `full_partition_counts` par la clé existante `partition_counts` ; nouveau SHA-256 du programme `7f1529da4af9e1931fac1f4f928e8e6334de013aa96989013c1c7d22541d0fb1` (`2026-11-05T12:33:36.4334570Z`). | Erreur de nom de champ dans le contrôle préalable des dimensions de la partition source. | Aucun : données, comparateurs, graines, seuils, métriques et critère numérique inchangés ; l'arrêt précède toute lecture des résultats de test. |
| E-H4-HDFS-BLOCK-BASELINES | Nouvelle tentative terminée après le calcul du test mais avant l'écriture des artefacts ; le runner attendait `results`, alors que le JSON source expose `per_seed`. Runner corrigé, SHA-256 `83ce9265918c10bd15a82760c09dea0dc365f7454011d6a83bfd8160d8fb759d` (`2026-11-05T13:05:24.3929051Z`). | Mauvais nom de clé dans l'adaptation des résultats de référence. Aucun score n'a été émis par la tentative échouée ; le script a terminé les comparaisons avant de lever `KeyError`. | La tentative a consommé le test sans produire de résultat consultable ; seuils, comparateurs, métriques et critère restent inchangés. Cette exécution technique est documentée et le résultat final doit être rattaché à la tentative corrigée. |
| E-H4-HDFS-BLOCK-BASELINES | Exécution corrigée du `2026-11-05T13:06:17Z` au `2026-11-05T13:17:00Z` ; manifeste complet vérifié (8 empreintes sur 8). Histogram : F1 moyen 0,868373 ; meilleure baseline, surprise moyenne du template : 0,872434 ; delta Histogram − baseline : −0,004061. | Relance avec le runner corrigé ; mêmes données, comparateurs, graines et critère préenregistrés. | Le critère d'avantage d'au moins 0,01 échoue ; la baseline simple dépasse Histogram. Conclusion préenregistrée : résultat dominé par une règle simple. Artefacts : `experiments/phase_revision_20261105/E-H4-HDFS-BLOCK-BASELINES/`. |
