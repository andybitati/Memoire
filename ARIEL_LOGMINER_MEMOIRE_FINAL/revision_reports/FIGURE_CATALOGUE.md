# Catalogue des figures scientifiques finales

Toutes les figures sont produites par `revision_reports/generate_final_scientific_figures.py`, à 360 dpi, avec une taille de police minimale de 12 pt pour rester lisibles après réduction A4.

## `fig_architecture_multi_agent_global.png`
- Source : `code/classes + chapitre 3`
- Caption proposée : Le schéma relie les sources, la normalisation, le routage, le Contract Net et les artefacts de preuve ; il décrit le prototype évalué, sans extrapoler une architecture industrielle.

## `fig_contract_net_sequence.png`
- Source : `implémentation ContractNetCoordinator/RedisContractNetTransport`
- Caption proposée : La séquence explicite les messages métier observés lors d'une attribution, d'un refus, d'une reprise et d'un échec contrôlé.

## `fig_cicids_protocol_comparison.png`
- Source : `experiments/phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv`
- Caption proposée : Les mêmes familles de trafic produisent des performances très différentes selon la séparation ; la figure documente la validité externe limitée du protocole aléatoire.

## `fig_cicids_model_comparison.png`
- Source : `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/cicids_model_candidates_summary.csv`
- Caption proposée : La régression logistique est le meilleur candidat selon le F1 macro moyen de ce protocole, sans supprimer la fragilité du holdout.

## `fig_hdfs_event_vs_block.png`
- Source : `experiments\phase_dataset_strengthening\raw\ds_hdfs_block_20260910T081756Z__hdfs_block_result.json`
- Caption proposée : Le niveau bloc est l'unité alignée sur les labels finaux ; la valeur événementielle est conservée comme référence historique non équivalente.

## `fig_hdfs_bootstrap_distribution.png`
- Source : `E:\Cours\TFE\experiments\phase_final_scientific_consolidation\raw\hdfs_block_robustness_20260911T002351Z_bootstrap_replicates.csv`
- Caption proposée : La dispersion bootstrap quantifie l'incertitude liée aux blocs testés ; elle complète le F1 ponctuel par une distribution et un intervalle empirique.

## `fig_bgl_known_unknown.png`
- Source : `E:\Cours\TFE\experiments\phase_dataset_strengthening\raw\ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv`
- Caption proposée : Le F1 élevé est porté par les templates inconnus ; le groupe connu ne contient aucune anomalie dans ce test et ne permet pas d'estimer un rappel d'anomalies connu.

## `fig_bgl_histogram_vs_unknown_baseline.png`
- Source : `E:\Cours\TFE\experiments\phase_dataset_strengthening\raw\ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv`
- Caption proposée : La comparaison montre que le score d'Histogram dépasse le baseline fondé uniquement sur l'inconnu, tout en restant dépendant de la composition du test.

## `fig_csecic_lr_vs_rf.png`
- Source : `experiments/phase_dataset_strengthening/raw/external_csecicids2018_20260910T230136Z_metrics.csv`
- Caption proposée : Sur le split train 2018-02-15 / test 2018-02-16, la régression logistique domine la forêt aléatoire selon le F1 moyen ; cette observation ne prouve pas l'absence de fuite.

## `fig_csecic_lr_coefficients.png`
- Source : `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_lr_coefficients.csv`
- Caption proposée : Les coefficients décrivent les associations apprises par LR ; ils ne constituent pas à eux seuls une preuve causale.

## `fig_csecic_lr_single_feature.png`
- Source : `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_single_feature_scores.csv`
- Caption proposée : La performance mono-feature signale une dépendance forte à certaines variables et motive les contrôles de robustesse.

## `fig_csecic_lr_ablation.png`
- Source : `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_feature_ablation.csv`
- Caption proposée : Le retrait de variables dégrade le F1 dans les configurations testées ; l'ablation mesure une sensibilité, non une garantie de généralisation.

## `fig_csecic_lr_label_permutation.png`
- Source : `experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_label_permutation.csv`
- Caption proposée : La permutation détruit la stabilité attendue du F1 selon les seeds ; ce contrôle documente un signal de fragilité, sans identifier à lui seul la cause.

## `fig_router_open_set_tradeoff.png`
- Source : `experiments/phase_final_scientific_consolidation/aggregated/router_open_set_final_tradeoff_diagnostic.csv`
- Caption proposée : Le seuil 100 rejette les trois fichiers inconnus tout en conservant les 28 fichiers connus ; la courbe expose le compromis plutôt qu'une probabilité calibrée.

## `fig_multiformat_coverage_by_source.png`
- Source : `experiments/phase_dataset_strengthening/aggregated/multiformat_balanced_summary.csv`
- Caption proposée : La lecture, le parsing et la normalisation sont complets pour les unités effectivement présentes ; Apache reste une fixture d'une seule ligne répétée par le protocole.

## `fig_multi_agent_task_distribution.png`
- Source : `experiments\phase_multi_agent\raw\multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.json`
- Caption proposée : Les deux VM traitent chacune 30 des 60 tâches ; la figure documente la distribution observée, sans prétendre démontrer une haute disponibilité.

## `fig_multi_agent_throughput_latency.png`
- Source : `experiments/phase_multi_agent/aggregated/ma_20260909T160812Z_34016__statistics.csv`
- Caption proposée : Les courbes comparent quatre architectures, quatre charges et dix répétitions ; elles montrent l'absence d'accélération systématique des agents dans le protocole contrôlé.

## `fig_e2e_real_model_coverage.png`
- Source : `experiments/phase_final_scientific_consolidation/aggregated/multisource_cnp_model_inference_by_source.csv`
- Caption proposée : La condition M exécute les modèles réels pour 1400 unités sur 1401 ; une seule unité Apache utilise le fallback.

## `fig_e2e_real_model_latency.png`
- Source : `experiments/phase_final_scientific_consolidation/aggregated/multisource_cnp_model_inference_by_source.csv`
- Caption proposée : La comparaison H/M met en regard la voie heuristique et la voie modèles ; les valeurs sont des latences observées, pas des garanties de production.
