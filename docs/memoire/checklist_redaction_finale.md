# Checklist Redaction Finale

Date: 2026-06-03

Cette checklist recense les elements necessaires pour rediger le memoire et
preparer des articles a partir du prototype Logminer.

## Elements De Fond

| Element | Etat | Fichier |
| --- | --- | --- |
| Plan detaille du memoire | pret | `docs/memoire/plan.md` |
| Pack redaction memoire | pret | `docs/memoire/pack_redaction_memoire.md` |
| Pack articles scientifiques | pret | Aligne sur Article 1 IEEE conference et Article 2 IEEE Access |
| Frontiere Article 1/2 scalabilite | pret | `docs/memoire/frontiere_article1_article2_scalabilite.md` |
| Etat des exigences techniques | pret | `docs/memoire/etat_lieu_exigences_techniques.md` |
| Comparaison au document directeur | pret | `docs/memoire/comparaison_avancement_document_directeur.md` |
| Synthese resultats | pret | `docs/memoire/synthese_resultats_pour_memoire_articles.md` |
| Fiche reproductibilite | pret | `docs/memoire/fiche_reproductibilite_experimentale.md` |
| References exploitees | pret | `docs/memoire/exploitation_references.md` |
| Taxonomie des journaux | pret | `docs/memoire/taxonomie_journaux.md` |
| Protocole CPU/RAM multi-cycles | pret | `docs/memoire/protocole_campagne_cpu_ram_multicycles.md` |
| Comparaison outils standards | pret | `docs/memoire/comparaison_scientifique_outils_standards.md` |

## Figures Pretes

| Figure | Etat | Usage principal |
| --- | --- | --- |
| `fig_architecture_logminer.svg` | pret | Architecture |
| `fig_model_portfolio_scale.svg` | pret | Methodologie multi-modeles |
| `fig_validation_selection_f1.svg` | pret | Evaluation globale |
| `fig_supervised_models_f1.svg` | pret | Resultats supervises |
| `fig_false_positive_rates.svg` | pret | Faux positifs |
| `fig_realtime_workflow_latency.svg` | pret | Latence |
| `fig_resource_campaign_multicycle.svg` | pret | CPU/RAM 30 cycles |
| `fig_robustness_multiformat.svg` | pret | Robustesse |
| `fig_wazuh_logminer_overlap.svg` | pret | Comparaison Wazuh |

## Tableaux Prets

| Tableau | Etat | Usage principal |
| --- | --- | --- |
| `table_resultats_principaux.md` | pret | Chapitre 5, synthese |
| `table_datasets_scenarios.md` | pret | Protocole experimental |
| `table_realtime_benchmark.md` | pret | Latence |
| `table_realtime_benchmark_detailed.md` | pret | Annexe resultats |
| `table_resource_campaign_multicycle.md` | pret | CPU/RAM 30 cycles |
| `table_false_positives.md` | pret | Discussion faux positifs |
| `table_resource_snapshot.md` | pret | Monitoring API |
| `table_resource_campaign.md` | pret | Historique ressources |
| `table_resilience_agent.md` | pret | Robustesse/resilience |
| `table_redis_streams_integration.md` | pret | Bus evenementiel optionnel |
| `table_mqtt_integration.md` | pret | Pub/sub MQTT optionnel |
| `table_scalability_redis_smoke.md` | pret | Memoire / Article 2, pas resultat central Article 1 |
| `table_comparaison_outils_standards.md` | pret | Outils standards |
| `table_operational_tool_comparison.md` | pret | Positionnement SOC |
| `table_fail2ban_like_baseline.md` | pret | Baseline rule-based |
| `table_wazuh_logminer_summary.md` | pret | Wazuh |
| `table_wazuh_logminer_overlap.md` | pret | Recouvrement Wazuh |

## Donnees Et Resultats Experimentaux

| Element | Etat | Remarque |
| --- | --- | --- |
| Resultats supervises Linux/auth | pret | F1 = 0.916602 |
| Resultats supervises CICIDS | pret | F1 = 0.997163 |
| Resultats supervises UNSW/CIC-DDoS | pret | F1 = 0.999965 |
| Resultats Wazuh | pret | 122 563 evenements, 3 676 anomalies |
| Benchmark temps reel | pret | 5 cycles, moyenne 10.6473 s |
| Campagne CPU/RAM | pret | 30 cycles, moyenne 9.3300 s |
| Robustesse multi-format | pret | logs incomplets conserves |
| Comparaison fail2ban-like | pret | baseline rule-based, pas fail2ban officiel |

## Captures A Produire

| Capture | Etat | Usage |
| --- | --- | --- |
| Vue d'ensemble dashboard | pret | `docs/memoire/captures/dashboard_vue_ensemble.png` |
| Vue longue dashboard | pret | `docs/memoire/captures/dashboard_longue_vue.png` |
| Timeline et heatmap remplies | partiel | incluse si visible dans la vue longue |
| Resultats avec filtres | a produire | Chapitre 4 |
| Detail incident | a produire | Chapitre 4/6 |
| Decisions analyste et audit | a produire | Chapitre 4 |
| Ressources CPU/RAM agents | a produire | Chapitre 5 |
| Dashboard mobile ou fenetre reduite | optionnel | Annexe/demo |

## Informations De Reproductibilite A Ajouter Dans La Redaction

- machine utilisee pour la campagne CPU/RAM;
- nombre de coeurs logiques;
- RAM totale;
- OS;
- version Python;
- versions de `pandas`, `numpy`, `scikit-learn`, `psutil`;
- commande exacte de benchmark;
- valeur `max_mb=5`;
- nombre de cycles: 30;
- statut de l'API FastAPI pendant les mesures.

## Points De Prudence Scientifique

- distinguer les resultats supervises des anomalies candidates non supervisees;
- ne pas presenter la baseline fail2ban-like comme fail2ban officiel;
- presenter OSSEC comme reference fonctionnelle si aucune execution directe
  n'est ajoutee;
- presenter Wazuh via les exports disponibles;
- cadrer la distribution comme logique et locale;
- presenter l'auto-apprentissage continu comme perspective;
- discuter les faux positifs et le desequilibre des datasets.

## Ordre De Redaction Conseille

1. Chapitre 3 - Methodologie et architecture.
2. Chapitre 4 - Implementation.
3. Chapitre 5 - Experimentations et resultats.
4. Chapitre 6 - Discussion.
5. Chapitre 2 - Etat de l'art.
6. Chapitre 1 - Introduction.
7. Chapitre 7 - Conclusion.
8. Annexes.

## Verdict

Les elements techniques, experimentaux, figures, tableaux, exports PNG/PDF et
captures dashboard de base sont prets pour une redaction solide. Il reste
seulement des captures plus ciblees si l'article exige une vue precise du
detail incident, de l'audit ou de la heatmap.
