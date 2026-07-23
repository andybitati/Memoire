# Ablation Memoire Feedback

| Scenario | Decisions feedback | Lignes | Anomalies candidates | Lignes abaissees | Priorite >= 70 | Priorite >= 50 | Lecture |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| audit_reel | 0 | 122563 | 3676 | 0 | 2613 | 6150 | effet mesure a partir des decisions analyste auditees |
| controle_top_5_motifs_rejetes | 15 | 122563 | 3676 | 1343 | 2613 | 6150 | test de sensibilite: motifs repetitifs abaisses par feedback simule |

Note: cette ablation mesure l'effet de la memoire sur la priorisation des alertes. Elle ne prouve pas a elle seule une amelioration de la generalisation du modele.
