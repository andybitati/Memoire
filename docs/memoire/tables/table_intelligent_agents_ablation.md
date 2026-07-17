# Ablation Agents Intelligents

| Scenario | Preuve | Taches | Echecs | Duree | Debit | Panne/reprise | Conclusion |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| Pipeline centralise | Parsing + routage dans un seul processus | 2 | 0 | n/a | n/a | Non | Reference non distribuee |
| Agent unique multi-taches | `run_intelligent_agents_demo.py` | 3 | 0 | n/a | n/a | Non | Un agent execute discovery, parsing et routage |
| Agents locaux multiples | `intelligent_agents_campaign_summary.json` | 9 | 0 | 6.0688 s | 1.483 taches/s | Non | Plusieurs agents partagent une file locale |
| Agents Redis panne/reprise | `redis-campaign-20260717161257` | 150 | 0 | 102.4202 s | 1.4646 taches/s | Oui, 1 tache reprise | Distribution locale multi-processus validee |

Note: l'ablation compare la progression architecturale plutot qu'un meme calcul numerique strictement identique. Le pipeline centralise sert de reference; l'agent unique ajoute la decision multi-taches; les agents locaux ajoutent la repartition; Redis ajoute la distribution multi-processus et la reprise d'une tache non acquittee.
