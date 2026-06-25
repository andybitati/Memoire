# Pack Redaction Memoire

Date: 2026-06-05

Objectif: rassembler les elements directement reutilisables pour rediger le
memoire selon le plan detaille, hors redaction integrale des chapitres.

Sujet:

> Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et
> Reseaux a l'aide d'Agents Intelligents Multi-Taches

Position scientifique recommandee:

> Logminer est un prototype multi-agents local, modulaire et extensible, qui
> valide la faisabilite d'une detection d'anomalies sur journaux heterogenes
> par normalisation commune, routage multi-modeles, correlation et dashboard
> analyste. La distribution multi-machine et l'auto-apprentissage continu sont
> des perspectives, pas des resultats a sur-vendre.

## Contributions A Annoncer

1. Pipeline de collecte, parsing et normalisation multi-format.
2. Architecture multi-agents composee d'agents collecteur, parseur, routeur,
   detecteur, correlateur, audit et dashboard.
3. Routage multi-modeles par famille de journaux: Windows, Wazuh, Linux/auth,
   reseau, HDFS, BGL et fallback.
4. Evaluation multi-datasets combinant logs locaux, exports Wazuh, datasets
   publics et scenarios robustesse.
5. Dashboard interactif avec alertes, incidents, decisions analyste, audit,
   timeline, heatmap et graphiques CPU/RAM.
6. Campagne experimentale mesurant latence et ressources sur 30 cycles.

## Chapitre 1 - Introduction Generale

Objectifs:

- introduire la masse et l'heterogeneite des journaux systemes/reseaux;
- expliquer les limites de l'analyse manuelle et des regles seules;
- formuler la problematique et les objectifs;
- annoncer la contribution Logminer.

Problematique proposee:

> Comment concevoir un systeme autonome, modulaire et exploitable par un
> analyste, capable de collecter des journaux heterogenes, de les normaliser,
> de router chaque famille vers un modele adapte et de transformer les
> anomalies detectees en incidents interpretable?

Hypothese principale:

> Une architecture multi-agents avec schema commun et modeles specialises par
> famille de journaux permet d'obtenir une detection plus exploitable qu'un
> modele global unique applique indistinctement a toutes les sources.

Elements a inserer:

- contexte: journaux Windows, Linux, Wazuh, HDFS, BGL, CICIDS, UNSW;
- limites: volume, heterogeneite, faux positifs, manque de labels;
- objectifs officiels 1 a 7;
- annonce des chapitres.

Preuves locales:

- `docs/memoire/plan.md`;
- `docs/memoire/etat_lieu_exigences_techniques.md`;
- `docs/memoire/comparaison_avancement_document_directeur.md`.

## Chapitre 2 - Etat De L'Art

Sections conseillees:

1. Journalisation systeme et reseau.
2. Normalisation et taxonomie des logs.
3. Detection d'intrusion et detection d'anomalies.
4. Methodes statistiques et rule-based.
5. Machine learning classique: Isolation Forest, RandomForest, LOF, SVM,
   k-Means.
6. Deep learning pour logs: autoencodeurs, LSTM, DeepLog, LogAnomaly,
   LogBERT.
7. Architectures multi-agents et SIEM.
8. Limites recurrentes: faux positifs, derive de donnees, generalisation,
   manque de labels.

References a mobiliser:

- `docs/memoire/exploitation_references.md`;
- `docs/references/nistspecialpublication800-92.pdf`;
- `docs/references/rfc5424.txt.pdf`;
- `docs/references/Deep Learning for Anomaly Detection in Log Data.pdf`;
- `docs/references/deep_learning_log_survey_comparison.md`;
- `docs/references/axelsson00intrusion.pdf`;
- `docs/references/wenke-ieee99.pdf`.

Formulation defensive:

> Les methodes profondes sont importantes dans la litterature, mais le
> prototype privilegie des modeles legers et deployables localement. Le deep
> learning est donc discute comme comparaison et perspective, tandis que
> l'evaluation centrale repose sur des modeles classiques interpretable et
> rapides.

## Chapitre 3 - Methodologie Et Architecture Proposee

Sections conseillees:

1. Vue generale Logminer.
2. Sources de logs et detection de format.
3. Schema commun de normalisation.
4. Agents et responsabilites.
5. Contrat de messages.
6. Routage multi-modeles.
7. Correlation des anomalies en incidents.
8. V1 CLI, V2 FastAPI et Redis Streams optionnel comme trajectoire
   concrete d'orchestration evenementielle; MQTT reste une perspective.

Figures a inserer:

- `docs/memoire/figures/fig_architecture_logminer.svg`;
- diagrammes Mermaid dans `docs/architecture/diagrammes_memoire.md`.

Tableaux a inserer:

- `docs/memoire/tables/table_datasets_scenarios.md`;
- `docs/memoire/taxonomie_journaux.md`.
- `docs/memoire/tables/table_redis_streams_integration.md`.

Preuves code:

- `src/logminer/pipeline.py`;
- `src/logminer/detectors/file_detector.py`;
- `src/logminer/schema/columns.py`;
- `src/logminer/agents/bus.py`;
- `src/logminer/agents/orchestrator.py`;
- `src/logminer/agents/model_router.py`;
- `src/logminer/api.py`;
- `docs/architecture/message_contract.md`.

Phrase de transition:

> La separation en agents permet d'isoler les responsabilites: collecte,
> parsing, detection, correlation et visualisation peuvent evoluer separement,
> tout en partageant un schema commun et un contrat de messages.

Paragraphe Redis Streams a integrer:

> Le prototype conserve un bus JSONL local comme socle reproductible, mais il
> integre aussi Redis Streams comme bus evenementiel optionnel dans la V2
> FastAPI. Le meme contrat `AgentMessage` est publie en JSONL ou dans le Stream
> `logminer:events`, ce qui permet de tracer les etapes du workflow sans
> modifier la logique metier. Une file `logminer:jobs` et un worker Redis
> permettent aussi de decoupler l'API de l'inference: plusieurs workers peuvent
> consommer les jobs via consumer group et acquitter les traitements termines.
> Cette integration prepare la scalabilite operationnelle du prototype, mais
> elle ne doit pas etre interpretee comme une validation de debit SOC industriel.
> Les mesures queuees et multi-workers sont reservees a l'article 2, avec les
> retries avances, la dead-letter queue, le back-pressure applicatif, la
> securisation et les tests de charge prolonges.

Paragraphe MQTT a integrer:

> MQTT est ajoute comme bus pub/sub optionnel et complementaire a Redis Streams.
> Il reutilise le contrat `AgentMessage` et publie les evenements sur des topics
> de type `logminer/events/<target>/<message_type>`. Son role est de soutenir
> des collecteurs legers, des notifications temps reel et des scenarios IoT ou
> reseau local. Contrairement a Redis Streams, MQTT n'est pas utilise ici comme
> file de jobs persistante pour workers; les mesures de debit MQTT et la
> comparaison Redis/MQTT sont reservees a l'article 2.

Attention article 1 / article 2:

> Dans l'article 1, Redis Streams doit rester un detail d'implementation et un
> chemin d'evolution non bloquant. Les mesures queuees, workers, reprise pending,
> resilience et stress appartiennent a l'article 2. Voir
> `docs/memoire/frontiere_article1_article2_scalabilite.md`.

## Chapitre 4 - Implementation Du Prototype

Sections conseillees:

1. Organisation du depot.
2. Collecte et preparation des journaux.
3. Parsing multi-format et conservation des lignes inconnues.
4. Features et normalisation.
5. Entrainement et chargement des modeles.
6. Routeur multi-modeles.
7. Correlation et priorisation.
8. API FastAPI et dashboard web.
9. Audit, decisions analyste et export.
10. Commandes de reproduction.

Elements a citer:

- registre des modeles: `docs/model_training/model_registry.md`;
- guide: `docs/guide_utilisation_logminer.md`;
- architecture V2: `docs/architecture/v2_fastapi.md`;
- comparaison V1/V2: `docs/architecture/v1_cli_v2_services.md`.

Commandes types:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.logminer.api:app --host 127.0.0.1 --port 8000
```

```powershell
.\.venv\Scripts\python.exe scripts\run_resource_campaign.py --cycles 30 --interval-sec 2 --max-mb 5
```

Limite a expliciter:

> Le dashboard et l'API valident l'exploitation locale interactive; la
> distribution multi-machine complete reste une extension technique.

## Chapitre 5 - Experimentations Et Resultats

Organisation recommandee:

1. Protocole experimental.
2. Datasets utilises.
3. Evaluation supervisee.
4. Evaluation non supervisee.
5. Robustesse multi-format.
6. Benchmark quasi temps reel.
7. Campagne CPU/RAM multi-cycles.
8. Comparaison prudente avec outils standards.
9. Synthese des resultats.

Tableaux a inserer:

- `docs/memoire/tables/table_resultats_principaux.md`;
- `docs/memoire/tables/table_datasets_scenarios.md`;
- `docs/memoire/tables/table_realtime_benchmark.md`;
- `docs/memoire/tables/table_realtime_benchmark_detailed.md`;
- `docs/memoire/tables/table_false_positives.md`;
- `docs/memoire/tables/table_resource_campaign_multicycle.md`;
- `docs/memoire/tables/table_resilience_agent.md`;
- `docs/memoire/tables/table_comparaison_outils_standards.md`;
- `docs/memoire/tables/table_fail2ban_like_baseline.md`;
- `docs/memoire/tables/table_wazuh_logminer_summary.md`;
- `docs/memoire/tables/table_wazuh_logminer_overlap.md`.

Figures a inserer:

- `fig_validation_selection_f1.svg`;
- `fig_supervised_models_f1.svg`;
- `fig_false_positive_rates.svg`;
- `fig_realtime_workflow_latency.svg`;
- `fig_resource_campaign_multicycle.svg`;
- `fig_robustness_multiformat.svg`;
- `fig_wazuh_logminer_overlap.svg`.

Resultats cles:

| Famille | Resultat exploitable |
| --- | --- |
| Linux/auth | RandomForest, F1 = 0.916602 |
| CICIDS2017 | RandomForest, F1 = 0.997163 |
| UNSW/CIC-DDoS | RandomForest, F1 = 0.999965 |
| Wazuh | 122 563 evenements, 3 676 anomalies candidates |
| BGL | meilleure selection autour de F1 = 0.994333 |
| HDFS | meilleure selection autour de F1 = 0.599333 a 0.600333 |
| Robustesse | 6 lignes normalisees en 0.1242 s, log incomplet conserve |
| Temps reel | 10 cycles, latence moyenne 8.2012 s |
| CPU/RAM | 30 cycles, workflow moyen 9.3300 s |

Formulation pour resultats non supervises:

> Les resultats non supervises sont rapportes comme anomalies candidates. Ils
> mesurent la capacite du modele a signaler des comportements rares ou atypiques
> et necessitent une interpretation par correlation ou validation analyste.

Formulation pour les scores tres eleves:

> Les scores eleves sur certains datasets reseau valident la pertinence du
> modele specialise dans le cadre experimental considere, mais ils doivent etre
> interpretes avec prudence en raison du desequilibre possible des classes et de
> la specificite des distributions.

## Chapitre 6 - Discussion

Axes a traiter:

- interet d'un portefeuille de modeles plutot qu'un modele global;
- complementarite avec Wazuh, OSSEC et fail2ban;
- charge analyste liee aux faux positifs;
- difference entre anomalie candidate et intrusion confirmee;
- limites de generalisation entre datasets;
- latence acceptable en local mais perfectible;
- distribution logique validee, distribution multi-machine en perspective;
- auto-apprentissage continu partiel.

Phrase de discussion centrale:

> La contribution la plus robuste n'est pas la promesse d'un detecteur universel,
> mais l'integration d'une chaine complete et reproductible reliant collecte,
> normalisation, routage, detection, correlation et visualisation.

Limites a declarer:

- pas de preuve multi-machine stricte;
- pas d'execution officielle complete OSSEC/fail2ban/Wazuh sur une meme
  infrastructure;
- modeles non supervises non assimilables a des labels d'attaque;
- captures dashboard de base et captures ciblees disponibles pour resultats,
  detail incident, ressources agents et audit;
- auto-apprentissage continu a presenter comme perspective.

## Chapitre 7 - Conclusion Et Perspectives

Bilan par objectif:

| Objectif | Statut redactionnel |
| --- | --- |
| 1. Collecte/parsing/normalisation | Conforme, preuves et taxonomie disponibles |
| 2. Detection et comparaison | Conforme, resultats et figures disponibles |
| 3. Architecture multi-agents | Conforme prototype, distribution stricte a cadrer |
| 4. IA legere quasi temps reel | Conforme prototype, benchmark disponible |
| 5. Dashboard interactif | Conforme prototype, captures de base disponibles |
| 6. Tests varies | Tres avance, datasets et robustesse disponibles |
| 7. Evaluation globale | Avance, metriques, latence et CPU/RAM disponibles |

Perspectives:

- extension multi-machine a partir de Redis Streams, files de jobs et workers;
  MQTT reste une piste complementaire pour collecteurs temps reel;
- integration SOC/SIEM plus stricte;
- templates de logs type Drain;
- reduction des faux positifs par apprentissage actif;
- apprentissage federe ou incremental;
- cartographie MITRE ATT&CK;
- tests de resilience par arret volontaire d'agents.

## Annexes Recommandees

1. Taxonomie des journaux.
2. Contrat de messages agents.
3. Registre des modeles.
4. Commandes de reproduction.
5. Tableaux complets.
6. Figures SVG.
7. Protocole CPU/RAM multi-cycles.
8. Comparaison outils standards.
9. Captures dashboard.

## Captures Dashboard Disponibles

Captures disponibles:

- `docs/memoire/captures/dashboard_vue_ensemble.png`;
- `docs/memoire/captures/dashboard_longue_vue.png`;
- `docs/memoire/captures/dashboard_resultats_detail_incident.png`;
- `docs/memoire/captures/dashboard_ressources_audit.png`.

Capture mobile optionnelle:

- `docs/memoire/captures/dashboard_mobile.png`.
