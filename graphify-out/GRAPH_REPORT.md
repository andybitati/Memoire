# Graph Report - .  (2026-08-03)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 1855 nodes · 4059 edges · 92 communities (90 shown, 2 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 270 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5ed3e4d4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Community 0
- Community 1
- Community 2
- Community 3
- Community 4
- Community 5
- Community 6
- Community 7
- Community 8
- Community 9
- Community 10
- Community 11
- Community 12
- Community 13
- Community 14
- Community 15
- Community 16
- Community 17
- Community 18
- Community 19
- Community 20
- Community 21
- Community 22
- Community 23
- Community 24
- Community 25
- Community 26
- Community 27
- Community 28
- Community 29
- Community 30
- Community 31
- Community 32
- Community 33
- Community 34
- Community 35
- Community 36
- Community 37
- Community 38
- Community 39
- Community 40
- Community 41
- Community 42
- Community 43
- Community 44
- Community 45
- Community 46
- Community 47
- Community 48
- Community 49
- Community 50
- Community 51
- Community 52
- Community 53
- Community 54
- Community 55
- Community 56
- Community 57
- Community 58
- Community 59
- Community 60
- Community 61
- Community 62
- Community 63
- Community 64
- Community 65
- Community 66
- Community 67
- Community 68
- Community 69
- Community 70
- Community 71
- Community 72
- Community 73
- Community 75
- Community 76
- Community 77
- Community 80

## God Nodes (most connected - your core abstractions)
1. `RedisMessageBus` - 44 edges
2. `render()` - 40 edges
3. `render()` - 39 edges
4. `MqttMessageBus` - 38 edges
5. `AgentTask` - 28 edges
6. `compare_models()` - 26 edges
7. `escapeHtml()` - 25 edges
8. `compare_models()` - 24 edges
9. `escapeHtml()` - 22 edges
10. `MessageBus` - 20 edges

## Surprising Connections (you probably didn't know these)
- `get_runtime_status()` --calls--> `runtime_status()`  [INFERRED]
  docs/memoire/pack_redaction_final/09_code_et_scripts_preuves/api.py → src/logminer/agents/runtime_agent.py
- `prepare_runtime()` --calls--> `ensure_runtime()`  [INFERRED]
  docs/memoire/pack_redaction_final/09_code_et_scripts_preuves/api.py → src/logminer/agents/runtime_agent.py
- `collect_discover()` --calls--> `discover_logs()`  [INFERRED]
  docs/memoire/pack_redaction_final/09_code_et_scripts_preuves/api.py → src/logminer/agents/collector_agent.py
- `collect_windows_privileged()` --calls--> `request_windows_sensitive_collection()`  [INFERRED]
  docs/memoire/pack_redaction_final/09_code_et_scripts_preuves/api.py → src/logminer/agents/privilege_agent.py
- `run_discovered()` --calls--> `discover_logs()`  [INFERRED]
  docs/memoire/pack_redaction_final/09_code_et_scripts_preuves/api.py → src/logminer/agents/collector_agent.py

## Import Cycles
- None detected.

## Communities (92 total, 2 thin omitted)

### Community 0 - "Community 0"
Cohesion: 0.05
Nodes (87): AgentMessage, filter_messages(), MqttMessageBus, Any, Bus de communication entre agents Logminer. La V1 conserve un bus JSONL local,…, Bus Redis Streams pour les runs FastAPI/agents distribues., Retourne un etat leger du Stream Redis., Cree un consumer group Redis Streams si necessaire. (+79 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (84): alert_decision(), AlertDecisionRequest, _audit(), collect_discover(), collect_windows_privileged(), correlate(), CorrelateRequest, _count_rows() (+76 more)

### Community 2 - "Community 2"
Cohesion: 0.05
Nodes (78): LocalMessageBus, MessageBus, Path, Protocol, Contrat minimal partage par les bus JSONL et Redis., Bus append-only stocke dans un fichier JSONL., _family(), main() (+70 more)

### Community 3 - "Community 3"
Cohesion: 0.05
Nodes (77): align_features(), detect_anomalies(), load_model_artifact(), main(), DataFrame, IsolationForest, LocalMessageBus, Path (+69 more)

### Community 4 - "Community 4"
Cohesion: 0.07
Nodes (75): AGENT_LABELS, agentFlowPanel(), agentName(), alertKey(), analystConsole(), analystDecisionPanel(), analystQueuePanel(), auditDecisions() (+67 more)

### Community 5 - "Community 5"
Cohesion: 0.07
Nodes (71): AGENT_LABELS, agentFlowPanel(), agentName(), alertKey(), auditDecisions(), auditPanel(), captureFocusSelector(), createRealtimeSample() (+63 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (73): DetectorTask, detect_baseline(), main(), DataFrame, Path, _rarity_score(), Detecteur baseline explicable pour l'objectif 2. Ce module sert de point de…, Produit un CSV d'anomalies candidates avec la baseline explicable. (+65 more)

### Community 7 - "Community 7"
Cohesion: 0.08
Nodes (57): _candidate_models(), CandidateResult, evaluate(), main(), _metrics(), DataFrame, ndarray, Path (+49 more)

### Community 8 - "Community 8"
Cohesion: 0.10
Nodes (56): _add_selection_scores(), _anomaly_strength(), _clip_contamination(), compare_models(), _detect_label_column(), _event_sequence_signal(), _labels_from_column(), main() (+48 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (47): correlate_anomalies(), _first_non_empty(), main(), _priority_details(), _priority_label(), DataFrame, LocalMessageBus, Path (+39 more)

### Community 10 - "Community 10"
Cohesion: 0.07
Nodes (20): AgentMessage, filter_messages(), LocalMessageBus, MqttMessageBus, Any, Path, Bus Redis Streams pour les runs FastAPI/agents distribues., Retourne un etat leger du Stream Redis. (+12 more)

### Community 11 - "Community 11"
Cohesion: 0.08
Nodes (38): detect_file(), detect_kind(), iter_files(), _joined(), looks_like_apache(), looks_like_bgl(), looks_like_cef_leef(), looks_like_cloudtrail() (+30 more)

### Community 12 - "Community 12"
Cohesion: 0.12
Nodes (38): _active_column(), _default_output(), _detect_linux_auth_model(), _detect_supervised_model(), _first_alias(), _has_column(), _infer_sep(), _linux_auth_features() (+30 more)

### Community 13 - "Community 13"
Cohesion: 0.12
Nodes (36): _active_column(), _default_output(), _detect_linux_auth_model(), _detect_supervised_model(), _first_alias(), _has_column(), _infer_sep(), _linux_auth_features() (+28 more)

### Community 14 - "Community 14"
Cohesion: 0.09
Nodes (34): enrich_sequence_windows(), main(), Path, Agent de fenetrage glissant pour HDFS/BGL. Il enrichit un CSV Logminer avec des…, Lit un CSV normalise, ajoute les features sequentielles et l'ecrit., build_templates(), _Cluster, drain3_templates() (+26 more)

### Community 15 - "Community 15"
Cohesion: 0.09
Nodes (32): count_rows(), main(), Path, Controle robustesse et scalabilite Logminer. Ce script couvre les objectifs 6…, rows_by_filepath(), run_checks(), write_samples(), main() (+24 more)

### Community 16 - "Community 16"
Cohesion: 0.12
Nodes (32): callOpenAiExplanation(), dataFiles, dynamicDataPatterns, extractOpenAiText(), fetchJson(), formatMetric(), handleAgentsStatus(), handleAlertDecision() (+24 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (32): callOpenAiExplanation(), dataFiles, dynamicDataPatterns, extractOpenAiText(), fetchJson(), formatMetric(), handleAgentsStatus(), handleAlertDecision() (+24 more)

### Community 18 - "Community 18"
Cohesion: 0.14
Nodes (31): _balanced(), load_cicids(), load_linux_auth(), load_unsw(), main(), make_model(), _metric_row(), _numeric_summary() (+23 more)

### Community 19 - "Community 19"
Cohesion: 0.13
Nodes (22): BaseNormalizer, Any, Classes de base pour la normalisation semantique des evenements., Interface minimale commune a tous les normaliseurs., categorize(), CategorizerNormalizer, Any, Categorisation explicable des evenements de securite. (+14 more)

### Community 20 - "Community 20"
Cohesion: 0.12
Nodes (12): AgentCapability, AgentMemory, MultiTaskIntelligentAgent, Any, MessageBus, Path, Memoire locale simple pour apprendre des executions precedentes., Agent logiciel multi-taches avec politique de decision explicite. (+4 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (25): Element, _children(), _event_data_to_message(), _first_child(), _iso(), _iter_evtx_events(), _iter_xml_events(), _level_to_severity() (+17 more)

### Community 22 - "Community 22"
Cohesion: 0.16
Nodes (22): _count_priority(), main(), DataFrame, Path, Ablation de la memoire de feedback analyste sur les anomalies Logminer. Le…, run_ablation(), _simulated_profile(), apply_feedback_memory() (+14 more)

### Community 23 - "Community 23"
Cohesion: 0.23
Nodes (22): _balanced(), _display_family(), load_cicids(), load_linux_auth(), load_unsw(), main(), make_model(), _metric_row() (+14 more)

### Community 24 - "Community 24"
Cohesion: 0.17
Nodes (20): append_file(), build_dataset(), collect_columns(), _data_files(), _deduplicate_files(), _file_key(), _infer_csv_sep(), main() (+12 more)

### Community 25 - "Community 25"
Cohesion: 0.26
Nodes (19): build_redis_agent(), main(), Path, RedisMessageBus, Worker d'agents intelligents multi-taches sur Redis Streams. Ce script permet…, build_agent(), correlate_handler(), default_tasks() (+11 more)

### Community 26 - "Community 26"
Cohesion: 0.13
Nodes (6): Parser, Parser, Parser, Parser, Parser, Compatibilite avec l'ancien module `writer`. Les parseurs recuperes depuis les…

### Community 27 - "Community 27"
Cohesion: 0.25
Nodes (17): CompletedProcess, docker_cli_available(), docker_compose_available(), docker_engine_available(), ensure_runtime(), install_preflight(), InstallPreflightStatus, main() (+9 more)

### Community 28 - "Community 28"
Cohesion: 0.26
Nodes (16): env(), extract_json(), main(), normalize_metrics(), process_tree(), Any, Namespace, Path (+8 more)

### Community 29 - "Community 29"
Cohesion: 0.35
Nodes (15): as_float(), Bar, bar_chart(), generate(), latest_existing(), line_chart(), main(), matrix_diagram() (+7 more)

### Community 30 - "Community 30"
Cohesion: 0.35
Nodes (15): as_float(), Bar, bar_chart(), generate(), latest_existing(), line_chart(), main(), matrix_diagram() (+7 more)

### Community 31 - "Community 31"
Cohesion: 0.23
Nodes (15): _bgl_label_to_binary(), _bgl_timestamp_to_iso(), _can_add(), _label_to_binary(), main(), prepare_bgl(), prepare_hdfs(), Path (+7 more)

### Community 32 - "Community 32"
Cohesion: 0.15
Nodes (9): Synthese d'une campagne Redis multi-VM d'endurance., MessageBus, Protocol, Bus de communication entre agents Logminer. La V1 conserve un bus JSONL local,…, Contrat minimal partage par les bus JSONL et Redis., Protocol, Noyau d'agents intelligents multi-taches pour Logminer. Ce module ajoute une…, Source abstraite de taches pour agents. (+1 more)

### Community 33 - "Community 33"
Cohesion: 0.17
Nodes (12): clean(), make_pbar(), norm_sev(), parse_epoch(), Compacte les espaces et supprime CR/LF., Epoch secondes + sous-secondes (ns/us)., Crée une barre tqdm optionnelle. total=None -> total=0 pour éviter bool(None)…, to_iso() (+4 more)

### Community 34 - "Community 34"
Cohesion: 0.31
Nodes (13): as_int(), fail2ban_like(), is_positive_label(), main(), metrics(), Path, Comparaison mesuree avec outils standards de supervision securite. Ce script ne…, read_csv_limited() (+5 more)

### Community 35 - "Community 35"
Cohesion: 0.25
Nodes (13): campaign_tasks(), compact_process_output(), main(), percentile(), Namespace, Path, Popen, RedisMessageBus (+5 more)

### Community 36 - "Community 36"
Cohesion: 0.20
Nodes (8): App(), Incidents(), DataTable(), filterRows(), severityClass(), Sidebar(), uniqueValues(), useDashboardData()

### Community 37 - "Community 37"
Cohesion: 0.20
Nodes (8): App(), Incidents(), DataTable(), filterRows(), severityClass(), Sidebar(), uniqueValues(), useDashboardData()

### Community 38 - "Community 38"
Cohesion: 0.36
Nodes (12): get_json(), main(), num(), post_json(), Any, Path, Campagne CPU/RAM multi-cycles pour Logminer. Le script mesure plusieurs cycles…, run_campaign() (+4 more)

### Community 39 - "Community 39"
Cohesion: 0.36
Nodes (12): Event, build_synthetic_dataset(), main(), _monitor(), num(), Any, Path, Campagne ressources pour execution parallele Logminer. Cette campagne mesure un… (+4 more)

### Community 40 - "Community 40"
Cohesion: 0.22
Nodes (12): browser, captureOne(), captures, connect(), delay(), docsDir, latexDir, newPage() (+4 more)

### Community 41 - "Community 41"
Cohesion: 0.29
Nodes (12): anomaly_row(), balanced_sample(), build_incidents(), build_messages(), event_name(), main(), normalize_row(), Path (+4 more)

### Community 42 - "Community 42"
Cohesion: 0.27
Nodes (10): build_tasks(), main(), _project_path(), Path, Campagne locale multi-agents pour mesurer la repartition des taches. Cette…, run_agent(), summarize(), write_markdown() (+2 more)

### Community 43 - "Community 43"
Cohesion: 0.36
Nodes (12): get_json(), main(), num(), post_json(), Any, Path, Campagne CPU/RAM multi-cycles pour Logminer. Le script mesure plusieurs cycles…, run_campaign() (+4 more)

### Community 44 - "Community 44"
Cohesion: 0.23
Nodes (9): DictWriter, emit(), normalize_event(), open_writer(), Any, Ecriture CSV normalisee pour Logminer. Ce module est volontairement simple:…, Fallback minimal quand les normalizers ne sont pas disponibles., Ouvre un fichier CSV et ecrit l'en-tete normalise. Args: base_out: Chemin du… (+1 more)

### Community 45 - "Community 45"
Cohesion: 0.38
Nodes (11): asset_report(), benchmark_rows(), false_positive_rows(), main(), number(), Path, Produit les preuves manquantes rapides pour le suivi technique du TFE. Sorties:…, read_csv() (+3 more)

### Community 46 - "Community 46"
Cohesion: 0.29
Nodes (5): enqueue_demo_tasks(), AgentTask, Source de taches basee sur Redis Streams. Les taches sont stockees dans un…, Tache transportable entre agents ou workers., RedisTaskSource

### Community 47 - "Community 47"
Cohesion: 0.35
Nodes (11): _category(), _default_month_files(), main(), _normalise_chunk(), normalise_files(), _pick(), DataFrame, Path (+3 more)

### Community 48 - "Community 48"
Cohesion: 0.41
Nodes (11): _label_counts(), main(), DataFrame, Path, Split experimental propre pour datasets labellises Logminer. Le but est…, split_chronological(), split_dataset(), split_group_chronological() (+3 more)

### Community 49 - "Community 49"
Cohesion: 0.21
Nodes (5): detect_file(), looks_like_bgl(), Retourne (kind, path) pour le premier fichier plausible. kind ∈…, sample_lines(), sniff_pcap()

### Community 50 - "Community 50"
Cohesion: 0.36
Nodes (10): _cpu_seconds(), _env(), main(), _process_tree(), Any, Path, Controlled comparison between monolithic execution and Logminer agents., _run_mode() (+2 more)

### Community 51 - "Community 51"
Cohesion: 0.38
Nodes (10): filter_frame(), load_csv(), main(), metric_row(), DataFrame, Path, Dashboard Streamlit pour les agents Logminer., show_bus() (+2 more)

### Community 52 - "Community 52"
Cohesion: 0.27
Nodes (10): create_windows_admin_launcher(), main(), PrivilegedRequest, Path, _quote_cmd(), _quote_ps(), Agent d'autorisation privilegiee. Cet agent demande a l'administrateur…, Cree un lanceur interactif a executer en administrateur. (+2 more)

### Community 53 - "Community 53"
Cohesion: 0.36
Nodes (9): main(), _normalise_chunk(), normalise_file(), _pick(), DataFrame, Path, Series, Normalise les datasets Linux/auth vers le schema Logminer. Les fichiers… (+1 more)

### Community 54 - "Community 54"
Cohesion: 0.29
Nodes (9): configure_imports(), main(), Path, Traite les journaux Windows recents depuis C:\\Windows\\System32\\winevt\\Logs.…, Rend les modules Logminer importables depuis ce script., Retourne les fichiers EVTX modifies dans les `days` derniers jours., Ecrit la liste des fichiers utilises pour la verification., recent_evtx_files() (+1 more)

### Community 55 - "Community 55"
Cohesion: 0.40
Nodes (7): _clean(), _open_text(), Parser, Any, Parseur AWS CloudTrail JSON ou JSONL., _records_from_json(), _user()

### Community 56 - "Community 56"
Cohesion: 0.39
Nodes (6): _clean(), Parser, Any, Parseur Apache/Nginx access log., _severity(), _timestamp()

### Community 57 - "Community 57"
Cohesion: 0.36
Nodes (7): _clean(), _parse_ext(), Parser, _pick_timestamp(), Any, Parseur CEF et LEEF tolerant., _severity()

### Community 58 - "Community 58"
Cohesion: 0.22
Nodes (8): dependencies, devDependencies, name, private, scripts, dev, type, version

### Community 59 - "Community 59"
Cohesion: 0.22
Nodes (8): dependencies, devDependencies, name, private, scripts, dev, type, version

### Community 60 - "Community 60"
Cohesion: 0.36
Nodes (7): extract_text(), find_default_pdf(), main(), Path, Extrait le texte d'un PDF. Usage: python scripts/extract_pdf.py…, Retourne le premier PDF disponible dans docs/memoire., Lit toutes les pages d'un PDF avec PyPDF2.

### Community 61 - "Community 61"
Cohesion: 0.39
Nodes (7): build_summary(), main(), merge_counts(), percentile(), Path, Campagne Redis longue par iterations bornees dans le temps. Ce pilote relance…, write_table()

### Community 62 - "Community 62"
Cohesion: 0.36
Nodes (6): _clean(), Parser, Any, Parseur syslog RFC3164/RFC5424 heuristique., _severity(), _timestamp_3164()

### Community 63 - "Community 63"
Cohesion: 0.43
Nodes (6): main(), post_json(), Any, Path, Benchmark quasi temps reel du workflow Logminer. Le script appelle l'API…, run_benchmark()

### Community 64 - "Community 64"
Cohesion: 0.57
Nodes (6): AgentResource, _classify_process(), Any, Mesure de consommation des ressources Logminer., _safe_cmdline(), snapshot()

### Community 65 - "Community 65"
Cohesion: 0.43
Nodes (6): main(), post_json(), Any, Path, Benchmark quasi temps reel du workflow Logminer. Le script appelle l'API…, run_benchmark()

### Community 66 - "Community 66"
Cohesion: 0.52
Nodes (6): capture(), find_browser(), main(), mirror_capture(), Path, Capture Ariel Logminer dashboard views for the memoire. Run the dashboard…

### Community 67 - "Community 67"
Cohesion: 0.52
Nodes (6): _add_proof_columns(), main(), DataFrame, Build final supervised proof CSVs and thesis tables., _write_proof(), _write_strict_table()

### Community 68 - "Community 68"
Cohesion: 0.48
Nodes (6): main(), DataFrame, Path, Resume les fichiers de validation produits par model_compare.py. Le script aide…, summarize(), summarize_file()

### Community 69 - "Community 69"
Cohesion: 0.48
Nodes (5): _clean(), Parser, _pick(), Any, Parseur JSON Lines generique.

### Community 70 - "Community 70"
Cohesion: 0.73
Nodes (5): export_pdf(), export_png(), find_edge(), main(), Path

### Community 71 - "Community 71"
Cohesion: 0.53
Nodes (5): _attack_labels(), _heldout_file(), _labels(), main(), Explain CICIDS2017 holdout instability by held-out scenario.

### Community 72 - "Community 72"
Cohesion: 0.73
Nodes (5): export_pdf(), export_png(), find_edge(), main(), Path

### Community 75 - "Community 75"
Cohesion: 0.33
Nodes (4): parse_line(), Parser, clean(), Nettoie un message sans dependre de `common.py`. Le fichier `common.py`…

### Community 76 - "Community 76"
Cohesion: 0.50
Nodes (4): inject_anomalies(), main(), Path, Cree un dataset de logs simules avec anomalies injectees. Le script part d'un…

### Community 77 - "Community 77"
Cohesion: 0.50
Nodes (4): main(), Any, Worker Redis Streams pour executer les workflows Logminer en file. Le worker…, _run_job()

## Knowledge Gaps
- **48 isolated node(s):** `name`, `version`, `private`, `type`, `dev` (+43 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `run_pipeline()` connect `Community 1` to `Community 44`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `run_pipeline()` connect `Community 15` to `Community 0`, `Community 9`, `Community 2`, `Community 44`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `open_writer()` connect `Community 44` to `Community 1`, `Community 54`, `Community 15`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `RedisMessageBus` (e.g. with `AlertDecisionRequest` and `CorrelateRequest`) actually correct?**
  _`RedisMessageBus` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `render()` (e.g. with `discoverLogs()` and `enableBrowserNotifications()`) actually correct?**
  _`render()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `render()` (e.g. with `discoverLogs()` and `enableBrowserNotifications()`) actually correct?**
  _`render()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `MqttMessageBus` (e.g. with `AlertDecisionRequest` and `CorrelateRequest`) actually correct?**
  _`MqttMessageBus` has 31 INFERRED edges - model-reasoned connections that need verification._