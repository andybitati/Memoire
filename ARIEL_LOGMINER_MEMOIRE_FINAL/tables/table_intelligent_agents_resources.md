# Ressources Et Debits Des Agents Intelligents

| Scenario | Source mesure | CPU/RAM | Debit observe | Commentaire |
| --- | --- | --- | ---: | --- |
| Campagne CPU/RAM FastAPI | `table_resource_campaign_multicycle.md` | API: 7.45% CPU machine moy., 187.82 MB RAM moy.; processus Logminer: 0.41% CPU machine moy., 495.41 MB RAM moy. | n/a | Mesure ressources principale sur 30 cycles |
| Campagne parallele locale | `table_parallel_resource_campaign.md` | CPU machine max moyen 17.1725%; RAM maximale moyenne 176.89 MB | n/a | Mesure locale multi-worker hors Redis |
| Agents locaux multiples | `intelligent_agents_campaign_summary.json` | Non echantillonne dans cette campagne courte | 1.483 taches/s | Repartition locale de 9 taches |
| Agents Redis prevalidation | `intelligent_redis_long_campaign_summary.json` | Ressources non echantillonnees pendant le run court | 1.4646 taches/s | 150 taches, 0 echec, 0 pending final |
| Agents Redis endurance 6h | `intelligent_redis_6h_campaign_summary.json` | Ressources non echantillonnees pendant le run endurance | 0.3936 taches/s | 8508 taches, 0 echec, 0 pending final, 709 reprises |

Interpretation: la consommation CPU/RAM consolidable reste celle des campagnes ressources dediees. La campagne Redis de six heures complete ces mesures par une preuve d'endurance, de repartition locale multi-processus et de tolerance repetee a une panne avant acquittement.
