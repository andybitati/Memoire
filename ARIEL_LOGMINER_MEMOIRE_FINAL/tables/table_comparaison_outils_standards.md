# Comparaison Qualitative Avec Outils Standards

| Critere | Logminer | fail2ban | OSSEC/Wazuh |
| --- | --- | --- | --- |
| Detection | Anomalies statistiques/IA et correlation contextuelle | Regles sur echecs d'authentification et bannissement IP | Regles, decodage, alertes SIEM/HIDS |
| Sources | Windows, Linux, Wazuh, HDFS, BGL, reseau, cloud | Principalement services exposes et logs auth | Tres large via agents et decoders |
| Adaptation | Routage multi-modeles; apprentissage par famille | Seuils et filtres configures manuellement | Regles, listes, enrichissements et configuration SOC |
| Explicabilite | Scores, incidents, justification locale/dashboard | Tres explicable par regle | Alertes riches mais dependantes des regles |
| Positionnement | Complement analytique leger pour anomalies candidates | Protection operationnelle immediate | Socle SIEM/HIDS mature a completer par IA |
