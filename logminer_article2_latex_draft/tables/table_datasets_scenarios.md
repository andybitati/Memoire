# Datasets Et Scenarios Experimentaux

| Categorie | Source | Nature | Objectif de test | Preuve locale |
| --- | --- | --- | --- | --- |
| Reel local | Windows Event/Application/System/Security | Journaux systeme Windows | Collecte, parsing EVTX/XML, detection locale | windows_collection_summary.txt; windows_*_pipeline.csv |
| Reel/SIEM | Wazuh exports | Alertes et evenements SIEM/HIDS | Detection non supervisee sur signaux securite | wazuh_months_logminer.csv; wazuh_months_anomalies.csv |
| Reel/tabulaire | Linux/auth | Authentification Linux labelisee | Evaluation supervisee et faux positifs | random_forest_linux_auth_metrics.csv |
| Public systeme | HDFS | Logs distribues avec labels | Validation detecteurs sur logs sequentiels | validation_hdfs_metrics.csv |
| Public systeme | BGL | Logs BlueGene/L avec labels | Validation detecteurs sur logs HPC | validation_bgl_metrics.csv |
| Public reseau | CICIDS2017/MachineLearningCVE | Flux reseau labelises | Detection supervisee attaques connues | random_forest_network_cicids_metrics.csv |
| Public reseau | UNSW/CIC-DDoS | Flux reseau/DDoS | Evaluation 80/20 par chunks | random_forest_unsw_80_20_metrics.csv |
| Controle simule | Windows simule | Evenements avec anomalies injectees | Comparer baseline, statistiques et IA | validation_simulated_windows_metrics.csv |
| Robustesse | Apache, CEF/LEEF, CloudTrail, Linux auth, log incomplet | Multi-format et entree corrompue | Tolerance parser et conservation unknown | robustness_scalability_report.csv |
