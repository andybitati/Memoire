# Statut final des hypothèses

Source des formulations: `memoire_logminer_latex_overleaf/chapters/chapitre1_introduction.tex`, lignes 53–63.

| Hypothèse | Expérience | Résultat | Statut | Preuve | Limite |
| --- | --- | --- | --- | --- | --- |
| H1 — Des journaux hétérogènes peuvent être rapprochés par un noyau commun sans supprimer les informations originales utiles à l'audit. | Phase 5 | 5 001/7 001 unités normalisées; HDFS/BGL 0/1 000; conservation exacte Windows XML et syslog complet 0/1 000 | PARTIELLEMENT SOUTENUE | `multiformat_validation_summary.csv`; `multiformat_field_completeness.csv` | Plusieurs voies fonctionnent, mais la normalisation et la conservation du brut ne sont ni complètes ni universelles. |
| H2 — Des agents spécialisés peuvent améliorer modularité, traçabilité et robustesse par rapport à une chaîne monolithique. | Benchmark D008; multi-VM; phase 7 | Architecture et audit implémentés; une reprise avant ACK observée; débit agents inférieur au monolithe à 60 tâches | PARTIELLEMENT SOUTENUE | `controlled_monolith_vs_agents.csv`; `vbox_redis_recovery_campaign.json`; code des agents | Modularité/traçabilité surtout soutenues par la conception; robustesse testée sur N=1 panne; aucun gain de débit. |
| H3 — Le routage par famille peut limiter les incompatibilités entre données, features et modèles. | Ablation D005; phase 6 | Routeur réel 80/81 sur corpus dérivé; gain prédictif spécialisé non systématique | PARTIELLEMENT SOUTENUE | `router_evaluation_summary.json`; table d'ablation | Intérêt architectural soutenu; bénéfice prédictif et généralisation externe non démontrés. |
| H4 — Des modèles légers conservent un intérêt dans une chaîne locale reproductible avec métriques, corrélation et validation humaine. | Phases 1–3, 8 | Certains résultats utiles (DDoS, BGL Histogram), mais échecs sévères Bot/PortScan/WebAttacks; corrélation synthétique F1 pairwise 0,812500 | PARTIELLEMENT SOUTENUE | Résumés CICIDS; HDFS/BGL; `correlation_synthetic_summary.json` | « Intérêt » n'est pas une métrique unique; validation humaine et utilité opérationnelle non évaluées expérimentalement. |
| H5 — Une mémoire persistante peut soutenir l'adaptation progressive, la priorisation et la mise à jour contrôlée. | Phase 4; implémentation mémoire/audit | Trois branches de mise à jour exécutées avec hashes; mémoire et feedback présents dans le code | PARTIELLEMENT SOUTENUE | `model_update_end_to_end_report.json`; `src/logminer/agents/supervisor_agent.py`; audit phase 4 | Le bénéfice de la mémoire sur la priorisation n'est pas isolé; aucun apprentissage continu autonome ou service production. |

Règle de lecture: aucune hypothèse n'est déclarée « validée ». Les statuts portent uniquement sur le prototype, les données locales et les protocoles documentés.

