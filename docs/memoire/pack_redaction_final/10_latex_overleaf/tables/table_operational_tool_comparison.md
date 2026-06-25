# Comparaison Operationnelle Outils Standards

| Point | Logminer | fail2ban | OSSEC/Wazuh | Conclusion |
| --- | --- | --- | --- | --- |
| Reaction automatique | Decision analyste/audit, pas de bannissement systeme | Bannissement IP operationnel | Alertes/regles HIDS/SIEM | Logminer complete plus qu'il ne remplace |
| Detection inconnue | IA legere et rarete statistique | Limitee aux filtres | Depend des regles/decoders | Avantage Logminer sur signaux atypiques |
| Maturite SOC | Prototype recherche | Outil operationnel cible | Plateforme mature | Wazuh/OSSEC restent references production |
| Interpretabilite | Scores, incidents, dashboard | Regles simples | Regles et contexte SIEM | Complementarite forte |
| Donnees heterogenes | Routeur multi-modeles | Principalement logs auth/service | Tres large via agents | Logminer interessant comme couche analytique |
