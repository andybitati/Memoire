# Comparaison Avancement / Document Directeur

Date de controle: 2026-06-03

Mise a jour d'execution: 2026-06-03

Document directeur:

- `docs/memoire/Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et Reseaux a l'aide d'Agents Intelligents Multi-Taches.pdf`

Documents et preuves compares:

- `docs/roadmap/README.md`
- `docs/memoire/plan.md`
- `docs/anomaly_detection/README.md`
- `docs/architecture/README.md`
- `docs/architecture/message_contract.md`
- `docs/model_training/model_registry.md`
- `data/processed/validation_summary.csv`
- `data/processed/validation_selection_summary.csv`
- `data/processed/random_forest_linux_auth_metrics.csv`
- `data/processed/random_forest_network_cicids_metrics.csv`
- `data/random_forest_unsw_80_20_metrics.csv`
- `data/processed/robustness_scalability_report.csv`
- `data/processed/realtime_workflow_benchmark.csv`
- `docs/memoire/figures/`
- `docs/memoire/tables/`
- `models/`

## Synthese

Le projet est globalement tres avance par rapport au document directeur. Les
sept objectifs officiels ont tous une correspondance technique dans le depot.
Les parties les plus solides sont le pipeline multi-format, le routage
multi-modeles, les artefacts `.joblib`, les validations quantitatives et le
dashboard. Les principaux risques ne sont plus l'implementation de base, mais
la consolidation redactionnelle: diagrammes finaux, tableaux propres,
separation supervise/non supervise, comparaison avec outils standards et
mesures de latence/CPU/RAM.

Statut global recommande:

| Objectif | Statut controle | Niveau de conformite |
| --- | --- | --- |
| 1. Logs, parsing, normalisation | Tres avance | Conforme, avec annexes a completer |
| 2. Comparaison des techniques | Tres avance | Conforme, grille finale a consolider |
| 3. Architecture multi-agents | Avance | Conforme prototype, distribution multi-machine a cadrer |
| 4. IA legere quasi temps reel | Avance | Conforme prototype, benchmark final manquant |
| 5. Dashboard interactif | Avance | Conforme prototype, captures de base disponibles |
| 6. Tests sur donnees variees | Tres avance | Conforme, comparaison outils standards a completer |
| 7. Evaluation globale | Partiellement consolide | Metriques fortes, latence/CPU/RAM a finaliser |

Apres mise a jour du 2026-06-03:

- le benchmark quasi temps reel a ete produit dans
  `data/processed/realtime_workflow_benchmark.csv`;
- les figures SVG pour memoire/articles ont ete generees dans
  `docs/memoire/figures/`;
- les tableaux Markdown exploitables ont ete generees dans
  `docs/memoire/tables/`;
- la comparaison qualitative avec fail2ban/OSSEC/Wazuh est formalisee dans
  `docs/memoire/tables/table_comparaison_outils_standards.md`;
- les diagrammes Mermaid sont disponibles dans
  `docs/architecture/diagrammes_memoire.md`.

## Objectif 1 - Identifier, categoriser et structurer les logs

Attendu directeur:

- taxonomie des logs;
- parsing multi-format;
- normalisation commune.

Avancement constate:

- parseurs disponibles pour Windows Event, syslog/Linux, Apache, HDFS, BGL,
  CEF/LEEF, CloudTrail, JSONL, tcpdump texte, pcap et autres formats;
- detection de format dans `src/logminer/detectors/file_detector.py`;
- pipeline commun dans `src/logminer/pipeline.py`;
- schema commun dans `src/logminer/schema/columns.py`;
- taxonomie dans `docs/memoire/taxonomie_journaux.md`;
- collecte Windows documentee par `data/processed/windows_collection_summary.txt`
  avec 17 725 evenements exportes recemment et 61 356 evenements parses dans le
  pipeline.

Conclusion:

- objectif techniquement conforme;
- ajouter au memoire des exemples bruts vers normalises et les limites des logs
  incomplets/corrompus.

## Objectif 2 - Comparer les techniques de detection d'anomalies

Attendu directeur:

- comparaison methodes classiques, statistiques, heuristiques et IA;
- justification du choix de modeles legers;
- precision, rappel, F1, temps et memoire.

Avancement constate:

- comparateur implemente dans `src/logminer/agents/model_compare.py`;
- documentation dans `docs/anomaly_detection/README.md`;
- resultats dans `data/processed/validation_summary.csv` et
  `data/processed/validation_selection_summary.csv`;
- methodes presentes: seuils/regles, z-score, IQR, histogramme, entropie,
  Isolation Forest, k-Means, One-Class SVM, LOF, Autoencoder MLP, LSTM
  experimental;
- metriques deja disponibles: precision, recall, F1, accuracy, specificity,
  duree, pic memoire, TP/FP/FN/TN.

Points importants:

- BGL est tres bon sur validation: F1 autour de 0.994333 pour plusieurs
  methodes;
- HDFS est plus difficile: meilleurs ensembles autour de F1 0.599 a 0.600;
- Windows simule atteint F1 1.0 sur certaines methodes, ce qui doit etre
  presente comme validation controlee et non comme preuve generale.

Conclusion:

- objectif conforme;
- transformer les CSV en tableau final clair et distinguer explicitement:
  supervise, non supervise, deep learning experimental et baseline explicable.

## Objectif 3 - Architecture multi-agents distribuee

Attendu directeur:

- agents specialises;
- flux de communication;
- prototype modulaire;
- REST, pub/sub, sockets ou bus equivalent.

Avancement constate:

- agents disponibles: collecteur, parseur, detecteur, correlateur,
  orchestrateur, routeur, runtime, privilege, dashboard;
- bus local JSONL dans `src/logminer/agents/bus.py`;
- contrat de message dans `docs/architecture/message_contract.md`;
- API FastAPI dans `src/logminer/api.py`;
- Redis Streams optionnel via `docker-compose.redis.yml`, `RedisMessageBus`,
  `/redis/health`, `/events` et `use_redis=true`;
- documentation d'architecture dans `docs/architecture/README.md` et
  `docs/architecture/v1_cli_v2_services.md`.

Conclusion:

- conforme pour un prototype local modulaire;
- il faut cadrer la formulation "distribuee": aujourd'hui la distribution est
  surtout logique et locale. Redis Streams est cependant integre comme bus
  evenementiel optionnel pour traces inter-agents; la distribution
  multi-machine avec back-pressure et workers paralleles reste a valider.

## Objectif 4 - IA legere adaptative et quasi temps reel

Attendu directeur:

- integration de modeles IA legers;
- fonctionnement quasi temps reel;
- benchmark en conditions simulees;
- adaptation ou auto-ajustement.

Avancement constate:

- modeles sauvegardes dans `models/`;
- routeur multi-modeles dans `src/logminer/agents/model_router.py`;
- Isolation Forest pour Windows, Wazuh, HDFS, BGL, Linux/syslog et fallback;
- RandomForest supervise pour Linux/auth, CICIDS et UNSW/CIC-DDoS;
- registre dans `docs/model_training/model_registry.md`;
- dashboard avec rafraichissement automatique mentionne dans la roadmap.

Preuves quantitatives:

- Linux/auth RandomForest: F1 0.916602;
- CICIDS RandomForest: F1 0.997163;
- UNSW/CIC-DDoS RandomForest: F1 0.999965;
- Wazuh Isolation Forest: 122 563 evenements, 3 676 anomalies candidates.

Ecart restant:

- l'adaptation automatique doit etre formulee prudemment: le systeme route et
  applique des modeles specialises, mais l'auto-apprentissage continu n'est pas
  encore une preuve forte.

Conclusion:

- objectif conforme prototype;
- benchmark quasi temps reel produit: 10 cycles OK, 8 537 lignes par cycle,
  latence workflow moyenne 8.2012 s, min 3.1672 s, max 15.3289 s.

## Objectif 5 - Dashboard visuel interactif

Attendu directeur:

- dashboard Streamlit/Flask/web;
- timelines, heatmaps, filtrage;
- validation/rejet d'alertes.

Avancement constate:

- dashboard Streamlit dans `src/logminer/agents/dashboard.py`;
- dashboard web dans `web/dashboard`;
- vues metier et techniques;
- filtres, tableaux, timeline/heatmap, details incidents;
- decisions analyste, audit trail et exports CSV mentionnes dans la roadmap.

Conclusion:

- objectif conforme prototype;
- produire les captures desktop/mobile et un scenario de demonstration.

## Objectif 6 - Tests sur logs simules, reels et datasets publics

Attendu directeur:

- logs simules;
- journaux reels;
- attaques connues;
- comparaison fail2ban, OSSEC ou Wazuh.

Avancement constate:

- datasets publics: HDFS, BGL, DARPA, CICIDS2017, UNSW/CIC-DDoS;
- journaux reels locaux: Windows Event/Security, Wazuh, Linux/auth;
- scripts de preparation dans `scripts/`;
- injection/simulation via `scripts/inject_simulated_anomalies.py`;
- controle robustesse/scalabilite sur Apache, CEF/LEEF, CloudTrail, Linux auth
  et log corrompu/incomplet;
- rapport `data/processed/robustness_scalability_report.csv`: 5 fichiers,
  6 lignes normalisees, statut `ok` ou `kept_unknown`, duree pipeline 0.1242 s.

Ecart:

- les scenarios doivent etre separes en reels, simules, injectes et datasets
  publics.

Conclusion:

- objectif tres avance;
- comparaison qualitative avec les outils standards formalisee dans
  `docs/memoire/tables/table_comparaison_outils_standards.md`;
- reste surtout a rediger le protocole experimental final dans le chapitre 5.

## Objectif 7 - Evaluation globale

Attendu directeur:

- precision, rappel, F1;
- latence;
- CPU/RAM par agent;
- scalabilite;
- resilience aux pannes et logs corrompus.

Avancement constate:

- metriques supervisees fortes pour Linux/auth, CICIDS et UNSW/CIC-DDoS;
- metriques non supervisees/controlees pour BGL, HDFS et Windows simule;
- duree et memoire dans les validations de detection;
- robustesse sur logs corrompus/incomplets;
- monitoring agent/API mentionne dans la roadmap et le dashboard.

Ecarts:

- les faux positifs par periode ne sont pas encore generalises;
- la resilience a l'arret d'un agent doit etre presentee comme limite ou test a
  executer si aucune preuve finale n'est disponible.

Conclusion:

- objectif plus consolide: metriques, latence workflow et robustesse existent;
- tableaux principaux, benchmark et instantane CPU/RAM sont produits;
- restent prioritaires pour enrichissement les captures dashboard ciblees, les faux positifs par periode et
  une campagne CPU/RAM plus longue si le chapitre d'evaluation exige moyenne,
  maximum et ecart-type par agent.

## Ecarts Critiques A Corriger Avant Depot

1. Ajouter eventuellement captures dashboard ciblees desktop/mobile et scenario de demonstration.
2. Ajouter ou extraire les faux positifs par periode quand timestamps/labels le
   permettent.
3. Consolider les mesures CPU/RAM par agent sur plusieurs cycles si le chapitre
   d'evaluation les detaille statistiquement.
4. Formuler prudemment les limites: distribution locale, auto-apprentissage
   continu non complet, anomalies candidates pour les modeles non supervises.

## Priorite De Redaction Recommandee

1. Chapitre 3: architecture agents, flux, bus, API, routeur.
2. Chapitre 4: implementation prototype, pipeline, modeles, dashboard.
3. Chapitre 5: datasets, resultats, tableaux, evaluation.
4. Chapitre 6: limites et discussion critique.
5. Chapitre 2: etat de l'art finalise autour des choix vraiment utilises.
6. Chapitre 1 et conclusion: synthese propre des sept objectifs.

## Verdict

Le prototype peut deja soutenir le coeur du memoire. La soutenance ne devrait
pas presenter le travail comme un systeme industriel totalement distribue et
auto-apprenant, mais comme un prototype multi-agents modulaire, localement
fonctionnel, extensible vers FastAPI/Redis, et valide sur plusieurs familles de
logs avec des modeles adaptes.
