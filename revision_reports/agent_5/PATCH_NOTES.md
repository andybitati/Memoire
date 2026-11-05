# Agent 5 — Routeur open-set, corrélation, multi-format : notes de patch

## En-tête : effort d'intégration et blocages

**Effort estimé.** Environ 3 h 30 : 24 remplacements de texte (≈ 1 h 30), ajout d'un `\label` et d'une ligne de tableau (10 min), régénération de la figure open-set sans la courbe de couverture (30 min, script hors de ce dossier), copie facultative des scripts et artefacts dans `scripts/` et `experiments/` (30 min), recompilation et relecture (45 min).

**Blocages.**
1. **Aucun corpus Apache réel disponible localement.** Recherches menées : `data/` (glob), dépôt complet (`git ls-files`), `E:\Mémoire`, `C:\Users\aoliv\Downloads`. La recherche récursive sur `E:\` a été arrêtée par la limite de temps (expérience HDFS concurrente) : son résultat n'est pas conclusif. La fixture d'une ligne ne peut donc pas être remplacée sans téléchargement (protocole en C.3). Point important : le jeu Loghub *Apache* est un journal d'**erreurs**, que le parseur du projet (journaux d'accès, `src/logminer/parsers/apache.py`) ne reconnaît pas. Il ne convient pas comme remplaçant.
2. **Figure `fig_router_open_set_tradeoff.png`.** Elle trace la « coverage » (`scripts/run_router_open_set_consolidation.py`, l. 245). La retirer suppose de modifier ce script, hors de mon périmètre d'écriture.
3. **Résumé en lingala (`main.tex`, l. 577-604).** Je propose seulement des suppressions sûres. La mise à jour des chiffres doit être traduite par l'auteur.
4. **Le corpus de corrélation reste synthétique et construit par l'auteur**, même agrandi. Il ne remplace pas une vérité terrain d'incidents réels, qui n'existe pas localement.
5. **Inventaire de provenance borné.** Le SHA-256 n'est calculé que pour les fichiers de moins de 64 Mio : 28 gros fichiers ne sont pas hachés et aucune lecture complète n'a été lancée pendant la campagne HDFS.
6. **Un run écarté.** `agent5_router_open_set_20261104T145047Z` a été supprimé avant toute exploitation. Il relisait les artefacts neutres avec `dtype=str`, ce qui ne reproduisait pas les scores du run de référence (159 contre 167 pour `win_system_live`). Le run retenu reproduit la référence sans aucun écart sur les 31 sources.

---

## Artefacts produits (tous sous `revision_reports/agent_5/`)

| Objet | run_id | Résultat | Script |
|---|---|---|---|
| Routeur open-set étendu | `agent5_router_open_set_20261104T145601Z` | `router_open_set/agent5_router_open_set_20261104T145601Z/result.json`, `routes.csv`, `sources_config.json` | `scripts/agent5_router_open_set_extended.py` |
| Corrélation, corpus agrandi | `agent5_correlation_20261104T141916Z` | `correlation/agent5_correlation_20261104T141916Z/result.json`, `per_seed_metrics.csv`, `protocol.json`, exemples graine 0 | `scripts/agent5_correlation_extended.py` |
| Corrélation, sensibilité (secondaire) | `agent5_correlation_gapsens_20261104T143159Z` | `correlation/agent5_correlation_gapsens_20261104T143159Z/result.json` | `scripts/agent5_correlation_gap_sensitivity.py` |
| Multi-format (relecture) | `agent5_multiformat_20261104T150111Z` | `multiformat/agent5_multiformat_20261104T150111Z/result.json` | `scripts/agent5_multiformat_reframe.py` |
| Inventaire de provenance | `agent5_provenance_20261104T145837Z` | `provenance/agent5_provenance_20261104T145837Z/inventory.csv`, `result.json` | `scripts/agent5_data_provenance_inventory.py` |

Commande : `.venv\Scripts\python.exe revision_reports\agent_5\scripts\<script>.py`. Aucun fichier hors de `revision_reports/agent_5/` n'a été modifié.

---

## A. Routeur open-set

### A.1 Protocole

- Politique **gelée**, relue depuis `experiments/phase_final_scientific_consolidation/configs/router_open_set_selected_policy.json` : `min_top_score = 100`, `min_decision_margin = 0`, `min_compatible_rules = 0`. Une route `fallback` est toujours rejetée. **Aucune recalibration.**
- Les 31 sources d'origine sont rejouées depuis les artefacts neutres de `router_independent_20260910T094257Z`, avec **0 écart** sur la famille et le `top_score` par rapport à `final_router_open_set_20260911T000746Z`.
- 37 fichiers nouveaux, tous locaux, avec étiquettes figées dans `sources_config.json` avant routage :
  - **U, 17 inconnus** : 14 tables CSV de `Dataset_csv/` et 3 fichiers DARPA 1998 (audit Solaris BSM `praudit`, `bsm.list`, `tcpdump.list`) ;
  - **K, 18 connus de sources nouvelles** : CSE-CIC-IDS2018 (2 fichiers), archive de type CIC-DDoS2019 (1), UNSW-NB15 Parquet (2), `linux_auth_logs_labeled.csv`, `Linux_2k.log_structured.csv`, `data/samples/Application.evtx` et 10 exports Wazuh de décembre et janvier ;
  - **A, 2 ambigus**, exclus des taux : CSV de paquets produits par le parseur pcap du projet.
- Chaque fichier inconnu reçoit un **groupe de schéma**. Les fichiers qui partagent un schéma ne sont pas indépendants : par exemple `cloud_service`, `virtualization`, `router_log` et `switch_log` ont les mêmes colonnes.
- **Deux modes d'entrée.**
  - **P** : trame telle que produite par les adaptateurs du projet.
  - **N** : même trame sans les colonnes `dataset`, `subtype` et `filepath`. Ces colonnes sont écrites par l'adaptateur que choisit l'expérimentateur ; elles ne sont pas lues dans la source.
- Intervalles de Clopper-Pearson exacts à 95 % (`scipy.stats.beta`).

### A.2 Résultats chiffrés

Source : `router_open_set/agent5_router_open_set_20261104T145601Z/result.json`.

| Mode | Sous-ensemble | Inconnus rejetés | IC 95 % | Schémas inconnus entièrement rejetés | Connus rejetés à tort | IC 95 % | Connus acceptés bien orientés |
|---|---|---|---|---|---|---|---|
| P | 31 d'origine | 3/3 | [0,292 ; 1] | 2/2 | 0/28 | [0 ; 0,123] | 28/28 |
| P | nouveaux | 17/17 | [0,805 ; 1] | 15/15 | 3/18 | [0,036 ; 0,414] | 15/15 |
| P | **ensemble** | **20/20** | **[0,832 ; 1]** | **16/16** ([0,794 ; 1]) | **3/46** | **[0,014 ; 0,179]** | 43/43 |
| N | 31 d'origine | 3/3 | [0,292 ; 1] | 2/2 | 2/28 | [0,009 ; 0,235] | 26/26 |
| N | ensemble | 20/20 | [0,832 ; 1] | 16/16 | 5/46 | [0,036 ; 0,236] | 41/41 |

Observations, d'après `routes.csv` :

1. **Faux rejets en mode P.**
   - `k_cicids2018_thu` et `k_cicids2018_fri` : route `network`, `top_score` 44. Les noms de colonnes CICFlowMeter de 2018 diffèrent de ceux de CICIDS2017.
   - `k_linux_2k_structured` : `top_score` 43.
   - Les trois correspondent à des familles connues présentées sous un schéma absent de la calibration.
2. **Dépendance aux étiquettes écrites par l'adaptateur (mode N).**
   - Sans `dataset` ni `subtype`, `bgl_loghub` passe de 103 à 70 et sa meilleure famille devient `windows`.
   - `linux_2k` passe de 233 à 63.
   - Les deux sont rejetés. Pour les familles texte, la reconnaissance reprend donc en partie la décision du parseur de format (`detect_kind`).
3. **Rejet des formats texte inconnus en mode P.** Les trois fichiers DARPA sont rejetés par la règle `fallback_route` : le pipeline leur attribue `dataset = subtype = unknown`, ce qui donne au fallback un score de 141. Le seuil n'intervient pas. En mode N, ils sont rejetés par le seuil (`top_score` 40).
4. **Doublons d'entrée.** `source_001` (`win_app_live`) et `source_004` (`win_app_20260518`) ont le même SHA-256 d'artefact neutre ; c'est aussi le cas de `source_002` et `source_005` (manifeste `final_router_open_set_20260911T000746Z_manifest.json`). Le routeur reçoit donc **26 entrées connues distinctes** sur 28.
5. **La « couverture » 0,903 = 28/31 n'est pas une métrique.** Elle vaut (acceptés)/(total) et découle mécaniquement de la composition 28 connus / 3 inconnus lorsque le rejet est parfait. Elle est retirée et remplacée par les deux taux et leurs IC.

### A.3 Ce qui contredit le mémoire

- « 31 fichiers indépendants » : 2 paires d'entrées sont identiques, ce qui laisse 26 entrées connues distinctes.
- Le seuil gelé « rejette les inconnus sans faux rejet » ne tient que sur les 28 connus de calibration. Sur des sources connues nouvelles, le faux rejet vaut 3/18.
- « Le routeur examine la structure » : pour HDFS, BGL et Linux, la reconnaissance s'appuie aussi sur des colonnes de famille écrites par l'adaptateur. Sans elles, BGL et Linux_2k sont rejetés.

---

## B. Corrélation

### B.1 Protocole

- Le code réutilisé est `src/logminer/agents/correlator.py::correlate_anomalies`, sans modification : regroupement par égalité stricte de `floor(t, 15 min)` et de 7 clés (`host`, `user`, `source`, `category`, `subcategory`, `proto`, `dst_port`).
- Les baselines utilisent le **même code** sur une copie de l'entrée dont certaines clés sont vidées :
  - `B_time` : fenêtre temporelle seule ;
  - `B_host_time` : fenêtre et hôte.
- Générateur à graine (`numpy.default_rng`) : 20 graines (0 à 19). Chaque corpus compte 80 incidents de 1 + Poisson(3) événements (plafond 10), avec des écarts exponentiels de moyenne 3 min sur 12 h, plus 20 anomalies isolées et 40 événements non anomaux. Cela donne 315 à 365 anomalies par corpus et environ 1,15 million de paires par scénario.
- Deux scénarios :
  - S1, clés stables ;
  - S2, 30 % d'incidents multi-étapes (`LOGIN_FAILURE` → `LOGIN_SUCCESS` → `SPAWN`, même hôte et même utilisateur), soit 469 incidents sur 1 600.
- Les paramètres sont écrits dans `protocol.json` avant l'évaluation et n'ont pas été réglés a posteriori.
- **IC.** Bootstrap percentile sur les graines (B = 5 000), unité indépendante. Les IC de Clopper-Pearson sur paires agrégées ne figurent qu'à titre indicatif dans le JSON, car les paires ne sont pas indépendantes.
- **Observation sur le code.** `_incident_row` tronque la colonne `events` à 20 identifiants. 18 groupes de `B_time` dépassaient ce seuil. Leur appartenance a été reconstruite à partir de la clé de groupe publiée par le corrélateur. `M_keys` n'est pas concerné. Cette troncature mérite une mention au chapitre 3, car elle limite l'auditabilité des grands incidents.

### B.2 Résultats chiffrés

Corpus de référence (19 événements, 120 paires), run `agent5_correlation_20261104T141916Z`, clé `original_corpus` :

| Méthode | TP | FP | FN | TN | Précision | Rappel | F1 |
|---|---|---|---|---|---|---|---|
| M_keys (mémoire) | 13 | 4 | 2 | 101 | 0,764706 | 0,866667 | 0,812500 |
| B_host_time | 13 | 4 | 2 | 101 | 0,764706 | 0,866667 | 0,812500 |
| B_time | 13 | 31 | 2 | 74 | 0,295455 | 0,866667 | 0,440678 |

Sur ce petit corpus, les clés autres que l'hôte n'apportent rien. IC de Clopper-Pearson indicatifs, à ne pas imprimer : précision [0,501 ; 0,932], rappel [0,595 ; 0,983].

Corpus agrandi, comptes agrégés sur 20 graines et IC bootstrap sur graines :

| Scénario | Méthode | TP | FP | FN | Précision [IC] | Rappel [IC] | F1 [IC] | Incidents vrais fragmentés (moy./100) |
|---|---|---|---|---|---|---|---|---|
| S1 | M_keys | 7 076 | 83 | 4 770 | 0,9884 [0,9808 ; 0,9951] | 0,5973 [0,5837 ; 0,6106] | 0,7446 [0,7336 ; 0,7556] | 41,05 |
| S1 | B_host_time | 7 076 | 993 | 4 770 | 0,8769 [0,8575 ; 0,8976] | 0,5973 | 0,7106 [0,6993 ; 0,7218] | 41,05 |
| S1 | B_time | 7 076 | 23 664 | 4 770 | 0,2302 [0,2213 ; 0,2391] | 0,5973 | 0,3323 [0,3224 ; 0,3427] | 41,05 |
| S2 | M_keys | 5 817 | 61 | 6 215 | 0,9896 [0,9819 ; 0,9959] | 0,4835 [0,4670 ; 0,4988] | 0,6496 [0,6340 ; 0,6638] | 53,55 |
| S2 | B_host_time | 7 263 | 691 | 4 769 | 0,9131 [0,8919 ; 0,9323] | 0,6036 [0,5882 ; 0,6185] | 0,7268 [0,7123 ; 0,7404] | 42,85 |
| S2 | B_time | 7 263 | 23 303 | 4 769 | 0,2376 [0,2310 ; 0,2442] | 0,6036 | 0,3410 [0,3327 ; 0,3490] | 42,85 |

Différences appariées de F1 par graine (IC de Student à 95 %) :

| Scénario | Comparaison | Écart moyen [IC] | M_keys meilleur sur |
|---|---|---|---|
| S1 | M_keys − B_time | +0,4111 [0,4002 ; 0,4220] | 20/20 graines |
| S1 | M_keys − B_host_time | +0,0340 [0,0266 ; 0,0414] | 20/20 graines |
| S2 | M_keys − B_host_time | −0,0782 [−0,0916 ; −0,0647] | 0/20 (baseline meilleure sur 20/20) |

Sensibilité secondaire, descriptive et non utilisée pour régler un paramètre (`agent5_correlation_gapsens_20261104T143159Z`, S1, M_keys), selon l'écart moyen entre événements :

| Écart moyen | Rappel | IC bootstrap | Précision | F1 |
|---|---|---|---|---|
| 1 min | 0,856 | [0,838 ; 0,873] | 0,992 | 0,919 |
| 3 min | 0,597 | — | 0,988 | 0,745 |
| 6 min | 0,392 | [0,377 ; 0,407] | 0,986 | 0,561 |

Le rappel est gouverné par le rapport entre la durée des incidents et la fenêtre fixe.

### B.3 Ce qui contredit le mémoire

- La phrase « les règles temporelles et contextuelles rapprochent la majorité des événements » n'est pas robuste. Le rappel tombe à 0,4835 lorsque des incidents enchaînent plusieurs catégories.
- Dans ce scénario, la règle complète est **moins bonne** que la variante hôte + fenêtre sur 20 graines sur 20.
- Les clés apportent surtout de la **précision** face à la fenêtre seule. Les omissions viennent de la fenêtre fixe et de l'égalité stricte de la catégorie.

---

## C. Multi-format

### C.1 Relecture du run de référence

Source : `multiformat/agent5_multiformat_20261104T150111Z/result.json`, dérivé de `multiformat_balanced_summary.csv` et de `multiformat_mandatory_field_completeness.csv` (run `multiformat_balanced_20260910T094422Z`).

- 7 001 = 7 000 unités de 7 sources réelles + 1 unité de fixture Apache. La fixture est routée vers `fallback`.
- Dans `scripts/run_multiformat_validation.py::analyse_item`, `n_normalise = n_parse = nombre de lignes émises`. « Normalisé » ne peut donc échouer que si l'adaptateur plante : c'est un **test d'intégration**.
- Champs standard renseignés (sur 7) :

| Source | Champs complets |
|---|---|
| syslog | 7/7 |
| BGL | 7/7 |
| Apache | 6/7 |
| HDFS | 6/7 |
| Windows | 5/7 |
| Linux/auth | 4/7 |
| Wazuh | 4/7 (aucun horodatage normalisé : 0/1 000) |
| flux réseau tabulaires | **0/7** |

**Contradiction.** Le chapitre 4 affirme que « les adaptateurs testés parviennent à alimenter le schéma commun ». C'est faux pour les flux tabulaires et partiel pour Wazuh.

### C.2 Inventaire des copies de données

Run `agent5_provenance_20261104T145837Z`, fichier `inventory.csv` : 116 fichiers ; 110 n'apparaissent pas nominativement dans `final_data_source_traceability.csv`, certains étant couverts par une ligne agrégée, comme CICIDS2017.

| Copie | Constat (preuve) | Proposition |
|---|---|---|
| `Dataset_csv/*.csv`, 24 fichiers, dont les 3 inconnus d'origine et 14 inconnus de l'extension | Absents de la matrice. Contenus génériques (« Sample log description », « Log message 0 », « Details for event 0 », `example12.com`) et adresses du bloc de documentation RFC 5737 `203.0.113.0/24` : indices forts de génération synthétique. | **Assumer** : « tables CSV locales d'origine non établie, vraisemblablement synthétiques ». Lever seulement si l'URL d'origine est retrouvée. |
| `Dataset_csv/bgl.csv`, `hdfs.csv`, `outside_tcp_dump*.csv`, `sample_data01.csv` | En-tête `dataset;filepath;…` : dérivés produits par l'extracteur du projet (`Datasets/Extra.py`). | **Lever** : documenter « dérivé de X par Extra.py », ou supprimer. |
| Exports Wazuh, 17 CSV (7 d'octobre dans le routeur, 10 de décembre et janvier) | Seul `06-20-October.csv` est documenté (`docs/datasets/WAZUH.md`, matrice). | **Lever** : une ligne par export (instance, période, requête), ou **assumer** « exports d'une même instance locale ». |
| `linux_auth_logs_*.csv`, 4 fichiers | Matrice : « ORIGINE INDÉTERMINÉE » ; configuration du routeur : groupe `linux_auth_generated_corpus`. Les deux qualifications sont incohérentes. | **Assumer** : « corpus généré, générateur non identifié ». |
| `UNSWNB15.zip` et dossier `UNSWNB15/` | Même liste d'entrées (nom et taille) que `archive.zip` : fichiers `DrDoS_*`, `UDPLag`, `syn`, de type CIC-DDoS2019. Ce n'est pas UNSW-NB15 (déjà signalé par la matrice). | **Lever** : renommer ou supprimer ; ne jamais citer ces fichiers sous le nom UNSW-NB15. |
| Windows EVTX, 7 fichiers | Seul `windows_events/Application.evtx` est documenté. Deux instantanés donnent des échantillons de 200 enregistrements identiques aux fichiers « live ». | **Lever** : dater les instantanés et signaler les doublons (A.2, point 4). |
| `Datasets/bgl.log`, `hdfs.log` | 63 et 66 octets : en-têtes CSV seuls. | **Supprimer** ou ignorer explicitement. |
| `DARPA_eval_b/`, `outside.tcpdump` | Échantillon public MIT Lincoln Laboratory 1998 (README local). `outside.tcpdump` est horodaté 1999-03-01. Aucun des deux n'est dans la matrice. | **Lever** : ajouter deux lignes à la matrice (référence DARPA 1998 ; semaine et jour DARPA 1999 à identifier). |
| Fixture Apache | 2 copies identiques (`robustness_scalability_inputs/`, `parallel_robustness_inputs/`) et 2 échantillons identiques. | **Assumer** : fixture documentée (`SYNTHETIC_DOCUMENTED`). |

### C.3 Protocole pour remplacer la fixture Apache (non exécuté : corpus absent)

1. Télécharger un journal d'**accès** public au format Common Log Format, par exemple les traces NASA-HTTP de juillet 1995 de l'Internet Traffic Archive. Consigner l'URL, la date, le SHA-256 de l'archive et du fichier extrait.
2. Ne pas utiliser Loghub *Apache_2k* : c'est un journal d'erreurs, hors du périmètre du parseur `apache.py`.
3. Dans une copie de `multiformat_balanced_protocol.json`, remplacer l'entrée `apache` : `source`, `source_sha256`, `source_status = "public_corpus_hash_recorded"`, `limit = 1000`. La règle « premiers enregistrements, sans duplication » reste inchangée.
4. Relancer `scripts/run_multiformat_balanced_strengthening.py`. Rapporter lus, parsés, émis, champs complets et lignes rejetées par l'expression régulière, sans les masquer.
5. La route attendue reste `fallback` (`model_router.py`, l. 312) : aucun modèle Apache n'existe.
6. Mettre à jour `final_data_source_traceability.csv`.

---

## D. Modifications de texte proposées

Convention : *Actuel* est copié exactement du `.tex` ; *Proposé* est le texte de remplacement. Les limites sont formulées en entier au chapitre 5 (« Validité scientifique », `chapitre6_approfondissements_scientifiques.tex`) ; ailleurs, on y renvoie.

### D.0 `chapters/chapitre6_approfondissements_scientifiques.tex` — label du chapitre

**Actuel :**
```
\chapter{Validité scientifique}
```
**Proposé :**
```
\chapter{Validité scientifique}
\label{chap:validite}
```
**Preuve :** prérequis des renvois ci-dessous.

### D.1 `chapitre6_approfondissements_scientifiques.tex`, § Validité interne (l. 20) — formulation complète des limites du routeur

**Actuel :**
```
Pour le routeur open-set, le seuil 100 est calibré uniquement à partir des sources connues. Les trois fichiers inconnus ne participent pas au choix de ce seuil. L’évaluation immédiate reste donc séparée de la calibration. La faiblesse vient plutôt de la taille du jeu inconnu : trois exemples ne permettent pas de représenter l’ensemble des formes de nouveauté possibles.
```
**Proposé :**
```
Pour le routeur open-set, le seuil 100 est calibré uniquement à partir des sources connues, puis gelé ; ni les trois fichiers inconnus du protocole initial ni les fichiers ajoutés ensuite ne participent à son choix. Trois limites demeurent. D’abord, les 28 fichiers connus ne fournissent que 26 entrées distinctes, deux paires d’instantanés Windows produisant des échantillons identiques. Ensuite, pour les journaux texte, une partie de la reconnaissance repose sur les colonnes \texttt{dataset} et \texttt{subtype} écrites par le parseur de format : lorsqu’elles sont retirées, BGL et Linux\_2k sont rejetés (faux rejet $2/28$). Le routeur confirme donc, pour ces familles, une décision déjà prise par la détection de format. Enfin, le seuil est sensible aux variantes de schéma : sur 18 fichiers connus issus de sources nouvelles, trois sont rejetés à tort (les deux journées CSE-CIC-IDS2018, dont les noms de colonnes diffèrent de CICIDS2017, et la forme structurée de Linux\_2k). Les inconnus ajoutés proviennent de quelques schémas tabulaires génériques d’origine non établie et d’un échantillon DARPA 1998 ; ils élargissent le test sans représenter l’ensemble des formes de nouveauté possibles.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z` (`result.json` → `summary.N.original_31`, `summary.P.agent5_new` ; `routes.csv`) ; doublons : `experiments/phase_final_scientific_consolidation/manifests/final_router_open_set_20260911T000746Z_manifest.json` (SHA-256 de `source_001` = `source_004`, `source_002` = `source_005`).

### D.2 `chapitre6_approfondissements_scientifiques.tex`, § Validité de construit (l. 44) — retrait de la couverture

**Actuel :**
```
Le même principe vaut pour le routeur. La \texttt{decision\_margin} mesure un écart entre scores heuristiques ; elle ne représente pas une probabilité calibrée de bonne classification.
```
**Proposé :**
```
Le même principe vaut pour le routeur. La \texttt{decision\_margin} mesure un écart entre scores heuristiques ; elle ne représente pas une probabilité calibrée de bonne classification. La « couverture » (part des fichiers acceptés) n’est pas retenue comme métrique : elle découle mécaniquement de la proportion de fichiers inconnus dans le jeu de test. Seuls le taux de rejet des inconnus et le taux de faux rejet des connus sont rapportés.
```
**Preuve :** `router_open_set_summary.json` (`coverage` 0,9032 = 28/31 avec rejet parfait) ; `agent5_router_open_set_20261104T145601Z/result.json` (`protocol.coverage_metric`).

### D.3 `chapitre6_approfondissements_scientifiques.tex`, § Validité de construit (l. 46) — multi-format comme test d'intégration

**Actuel :**
```
La couverture multi-format possède elle aussi une définition précise. Elle vérifie la lecture, le parsing et la normalisation des unités effectivement présentes dans la campagne. Elle ne mesure ni la conservation bit à bit du journal original, ni la complétude de tous les champs, ni la compatibilité avec toutes les implémentations possibles d’un format. La présence d’une seule fixture Apache doit donc rester visible dans l’interprétation.
```
**Proposé :**
```
La campagne multi-format est un test d’intégration et non une validation. Une unité y est comptée comme normalisée dès que l’adaptateur émet une ligne, ce qui rend ce compte égal par construction au nombre d’unités parsées. Le décompte $7\,001/7\,001$ ne renseigne donc ni sur la conservation du journal original ni sur le remplissage du schéma commun, qui varie fortement : les sept champs standard sont complets pour syslog et BGL, quatre pour Wazuh, dont l’horodatage normalisé est absent, et aucun pour les flux réseau tabulaires. La voie Apache n’est exercée que sur une fixture d’une ligne ; aucun corpus Apache réel n’était disponible localement, et le jeu Loghub Apache, qui est un journal d’erreurs, ne relève pas du parseur d’accès du prototype.
```
**Preuve :** `agent5_multiformat_20261104T150111Z/result.json` ; `experiments/phase_dataset_strengthening/aggregated/multiformat_mandatory_field_completeness.csv` ; `scripts/run_multiformat_validation.py` (`analyse_item`, `n_normalise = n_parsed`).

### D.4 `chapitre6_approfondissements_scientifiques.tex`, § Validité externe — ajout après le paragraphe multi-VM (après l. 33)

**Actuel :** (insertion après le paragraphe se terminant par)
```
Une heure améliore la preuve d’endurance du protocole, mais ne renseigne pas sur les partitions réseau, le multi-site, un vieillissement sur plusieurs jours ou la haute disponibilité du broker.
```
**Proposé (nouveaux paragraphes) :**
```
La corrélation n’est évaluée que sur des corpus synthétiques construits par l’auteur. Le générateur à graine ajouté pour cette révision élargit le corpus initial de 16 anomalies à 20 corpus de 315 à 365 anomalies, mais il ne remplace pas une vérité terrain d’incidents observés. Ses résultats dépendent de paramètres choisis : avec des clés stables, le rappel par paires passe de 0,856 à 0,392 lorsque l’écart moyen entre événements d’un même incident passe de 1 à 6 minutes, la fenêtre fixe de 15 minutes fragmentant les incidents plus longs. Ces chiffres décrivent le comportement des règles, non une performance opérationnelle.

Plusieurs copies locales de données n’ont pas de provenance établie. Les tables de \texttt{Dataset\_csv}, utilisées comme sources inconnues du routeur, présentent des contenus génériques et des adresses du bloc de documentation RFC~5737 ; elles sont traitées comme des données vraisemblablement synthétiques d’origine non établie. Seul l’un des exports Wazuh est documenté ; le corpus Linux/auth est généré par un outil non identifié ; l’archive nommée \texttt{UNSWNB15.zip} contient en réalité des fichiers de type CIC-DDoS2019. Aucun résultat n’est attribué à une source publique dont la correspondance n’a pas été vérifiée.
```
**Preuve :** `agent5_correlation_gapsens_20261104T143159Z/result.json` (rappels 0,856 et 0,392) ; `agent5_correlation_20261104T141916Z/per_seed_metrics.csv` (315 à 365 anomalies) ; `agent5_provenance_20261104T145837Z/inventory.csv` et `result.json` (`duplicate_groups_zip_entries`).

### D.5 `chapitre6_approfondissements_scientifiques.tex`, § Validité statistique — ajout en fin de section (après l. 65)

**Actuel :** (insertion après)
```
Les résultats disponibles soutiennent seulement l’absence de gain systématique des architectures C et D dans le protocole effectivement exécuté.
```
**Proposé (nouveau paragraphe) :**
```
Les taux du routeur portent sur peu de fichiers et sont accompagnés d’intervalles exacts de Clopper-Pearson à 95~\%. Au protocole initial, le rejet de $3/3$ inconnus laisse un intervalle $[0{,}292\,;\,1]$ et l’absence de faux rejet sur 28 connus un intervalle $[0\,;\,0{,}123]$. Après extension, le rejet de $20/20$ inconnus donne $[0{,}832\,;\,1]$ et le faux rejet de $3/46$ connus $[0{,}014\,;\,0{,}179]$. Les fichiers d’un même schéma ne sont pas indépendants ; à l’échelle des schémas, les 16 schémas inconnus sont entièrement rejetés ($[0{,}794\,;\,1]$). Pour la corrélation, les paires d’événements d’un même corpus ne sont pas indépendantes ; aucun intervalle n’est donc calculé sur le corpus initial de 120 paires. Sur le corpus agrandi, l’incertitude est estimée par bootstrap sur 20 graines, chaque graine constituant un corpus indépendant.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z/result.json` (`*_cp95`) ; `agent5_correlation_20261104T141916Z/result.json` (`seed_bootstrap95`).

### D.6 `chapitre6_approfondissements_scientifiques.tex`, tableau `tab:risques-validite` (l. 98)

**Actuel :**
```
Surajustement du rejet & Calibration sur connus seulement & Trois inconnus seulement. \\
```
**Proposé :**
```
Surajustement du rejet & Calibration sur connus seulement ; extension à 20 inconnus sans recalibration & Faux rejets sur variantes de schéma connues ($3/46$) ; reconnaissance texte appuyée sur le parseur. \\

Corrélation synthétique & 20 graines, baselines fenêtre seule et hôte + fenêtre & Générateur construit par l’auteur ; rappel limité par la fenêtre fixe. \\
```
**Preuve :** `agent5_router_open_set_20261104T145601Z`, `agent5_correlation_20261104T141916Z`.

### D.7 `chapitre6_approfondissements_scientifiques.tex`, § Conclusions soutenues (l. 115)

**Actuel :**
```
Le prototype parvient à lire, parser et normaliser les unités prévues dans la campagne multi-format. Sur le jeu indépendant du routeur, les 28 fichiers connus sont correctement orientés et les trois fichiers inconnus sont rejetés lorsque le seuil gelé est appliqué.
```
**Proposé :**
```
Les adaptateurs du prototype traitent sans erreur d’exécution les unités prévues dans le test d’intégration multi-format. Avec le seuil gelé, le routeur rejette les 20 fichiers inconnus évalués et oriente correctement tous les fichiers connus qu’il accepte ; il rejette en revanche 3 des 46 fichiers connus, dont le schéma s’écarte de celui de la calibration.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z/result.json` (`summary.P.combined`) ; `agent5_multiformat_20261104T150111Z/result.json`.

### D.8 `chapters/chapitre5_resultats.tex`, tableau `tab:protocoles-experimentaux` (l. 39)

**Actuel :**
```
Routeur & fichier & Reconnaissance des sources connues et rejet de trois inconnues. \\
```
**Proposé :**
```
Routeur & fichier & Reconnaissance des sources connues et rejet d’inconnues (3 au protocole initial, 20 après extension). \\
```
**Preuve :** `agent5_router_open_set_20261104T145601Z`.

### D.9 `chapitre5_resultats.tex`, § Routeur open-set (l. 275)

**Actuel :**
```
Le jeu indépendant contient 31 fichiers répartis en neuf groupes : 28 connus et 3 inconnus. Sans seuil, le routeur classe correctement tous les connus mais ne rejette aucun inconnu. Le seuil de score principal est calibré sur les seules sources connues, puis gelé. À 100, les trois inconnus sont rejetés et aucun des 28 connus ne l’est.
```
**Proposé :**
```
Le jeu de référence contient 31 fichiers distincts répartis en neuf groupes : 28 connus et 3 inconnus. Sans seuil, le routeur classe correctement tous les connus mais ne rejette aucun inconnu. Le seuil de score principal est calibré sur les seules sources connues, puis gelé. À 100, les trois inconnus sont rejetés (intervalle exact à 95~\% : $[0{,}292\,;\,1]$) et aucun des 28 connus ne l’est ($[0\,;\,0{,}123]$).

Le même seuil, sans recalibration, a ensuite été appliqué à 37 fichiers locaux supplémentaires dont l’étiquette a été fixée avant le routage : 17 inconnus relevant de 15 schémas (tables CSV génériques, audit Solaris BSM et listes de sessions DARPA 1998) et 18 connus issus de sources nouvelles. Sur l’ensemble, $20/20$ inconnus sont rejetés ($[0{,}832\,;\,1]$) et $3/46$ connus le sont à tort ($[0{,}014\,;\,0{,}179]$) : les deux journées CSE-CIC-IDS2018 et la forme structurée de Linux\_2k. Les 43 fichiers connus acceptés sont tous correctement orientés.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z/result.json` (`summary.P.original_31`, `summary.P.combined`) et `routes.csv` (`k_cicids2018_thu`, `k_cicids2018_fri`, `k_linux_2k_structured`).

### D.10 `chapitre5_resultats.tex`, § Routeur open-set (l. 289)

**Actuel :**
```
Le rejet open-set fonctionne donc sur les trois fichiers inconnus inclus dans ce jeu indépendant, sans faux rejet parmi les 28 connus. Ce résultat concerne la décision de routage.
```
**Proposé :**
```
Le rejet open-set fonctionne donc sur tous les inconnus évalués, mais le seuil gelé écarte aussi des sources connues dont le schéma n’a pas été vu à la calibration ; les limites de ce résultat sont détaillées au chapitre~\ref{chap:validite}. Ce résultat concerne la décision de routage.
```
**Preuve :** idem D.9.

### D.11 `chapitre5_resultats.tex`, § Couverture multi-format (l. 293)

**Actuel :**
```
La campagne \texttt{multiformat\_balanced\_20260910T094422Z} vise $1\,000$ unités par source. Sept sources réelles atteignent ce volume ; Apache utilise une fixture synthétique d’une ligne. Au total, $7\,001$ unités sont lues, parsées et normalisées sans perte enregistrée.
```
**Proposé :**
```
La campagne \texttt{multiformat\_balanced\_20260910T094422Z} est un test d’intégration des adaptateurs. Elle vise $1\,000$ unités par source. Sept sources réelles fournissent $7\,000$ unités ; Apache n’est représenté que par une fixture synthétique d’une ligne. Au total, $7\,001$ unités sont lues et émises dans le schéma commun sans erreur d’exécution ni perte enregistrée.
```
**Preuve :** `agent5_multiformat_20261104T150111Z/result.json` (`real_sources_units` = 7 000, `apache_fixture_units` = 1).

### D.12 `chapitre5_resultats.tex`, § Couverture multi-format (l. 307)

**Actuel :**
```
La campagne établit donc une propriété fonctionnelle : les adaptateurs testés parviennent à alimenter le schéma commun pour les unités présentes dans le protocole. Elle ne mesure ni la complétude universelle des champs ni la compatibilité avec tout format possible. Les preuves de provenance indiquent en outre que certaines copies locales ne disposent pas d’une correspondance officielle démontrée ; aucun score n’est donc attribué à une source officielle qui n’a pas été vérifiée.
```
**Proposé :**
```
La campagne établit donc une propriété d’intégration : chaque unité présente dans le protocole produit une ligne, sans erreur d’exécution. Le remplissage du schéma commun varie selon la source, de sept champs standard sur sept pour syslog et BGL à aucun pour les flux réseau tabulaires. La portée de ce test et la provenance des sources sont discutées au chapitre~\ref{chap:validite}.
```
**Preuve :** `multiformat_mandatory_field_completeness.csv` ; `agent5_multiformat_20261104T150111Z/result.json` (`per_source`).

### D.13 `chapitre5_resultats.tex`, § Corrélation d’incidents (l. 406)

**Actuel :**
```
La campagne synthétique de corrélation atteint une précision de 0,764706, un rappel de 0,866667 et un F1 de 0,812500. Elle vérifie que les règles temporelles et contextuelles rapprochent la majorité des événements appartenant aux incidents construits, tout en produisant encore des associations incorrectes et des omissions.
```
**Proposé :**
```
Sur le corpus synthétique de référence (16 anomalies réparties en 6 incidents, soit 120 paires), le corrélateur réunit correctement 13 paires (TP), en réunit 4 à tort (FP) et en sépare 2 à tort (FN) : précision $13/17 = 0{,}764706$, rappel $13/15 = 0{,}866667$, F1 $0{,}812500$. Une baseline fondée sur la seule fenêtre temporelle obtient le même rappel avec 31 FP (précision $13/44 = 0{,}295455$).

Ce corpus a été complété par un générateur à graine (20 graines, 80 incidents, 20 anomalies isolées et 40 événements non anomaux par corpus). Avec des clés stables, le corrélateur atteint, en comptes agrégés, 7\,076 TP, 83 FP et 4\,770 FN : précision $0{,}9884$ (intervalle bootstrap sur graines $[0{,}9808\,;\,0{,}9951]$) et rappel $0{,}5973$ ($[0{,}5837\,;\,0{,}6106]$). La fenêtre seule conserve le même rappel mais ne dépasse pas une précision de $0{,}2302$. Les omissions viennent de la fenêtre fixe, qui fragmente en moyenne 41 des 100 incidents vrais d’une graine. Lorsque 30~\% des incidents enchaînent plusieurs catégories d’événements, le rappel tombe à $0{,}4835$ et la variante réduite à l’hôte et à la fenêtre obtient un meilleur F1 sur chacune des 20 graines ($0{,}7268$ contre $0{,}6496$). Les clés contextuelles apportent donc surtout de la précision ; elles fragmentent les incidents multi-étapes.
```
**Preuve :** `agent5_correlation_20261104T141916Z/result.json` (`original_corpus`, `extended_corpus.S1_cles_stables`, `extended_corpus.S2_multi_etapes`, `paired_f1_diff_M_keys_minus_B_host_time`) ; référence : `data/processed/final_experiments_2026/correlation_synthetic_summary.json` (run `e8_correlation_synthetic_controlled`).

### D.14 `chapters/chapitre4_implementation.tex`, § Corrélation (l. 83)

**Actuel :**
```
La couche de corrélation reçoit les alertes déjà normalisées et applique des contraintes temporelles et contextuelles pour déterminer lesquelles peuvent appartenir au même ensemble.
```
**Proposé :**
```
La couche de corrélation reçoit les alertes déjà normalisées et regroupe celles qui tombent dans la même fenêtre temporelle fixe (plancher à 15 minutes par défaut) et partagent exactement sept clés : hôte, utilisateur, source, catégorie, sous-catégorie, protocole et port de destination. La liste d’événements publiée pour chaque incident est limitée à vingt identifiants ; le nombre total d’événements reste conservé dans \texttt{event\_count}.
```
**Preuve :** `src/logminer/agents/correlator.py` (`GROUP_COLUMNS`, `_incident_row` : `event_ids[:20]`) ; 18 groupes tronqués observés dans `agent5_correlation_20261104T141916Z/result.json` (`observation_code`).

### D.15 `chapitre4_implementation.tex`, § Routeur (l. 34)

**Actuel :**
```
Dans le protocole open-set, un seuil de score principal est fixé avant l'évaluation afin de permettre le rejet des entrées insuffisamment compatibles avec les familles connues.
```
**Proposé :**
```
Dans le protocole open-set, un seuil de score principal est fixé avant l'évaluation afin de permettre le rejet des entrées insuffisamment compatibles avec les familles connues ; une entrée dont la meilleure famille est le fallback est également rejetée. Pour les journaux texte, les scores intègrent les colonnes \texttt{dataset} et \texttt{subtype} renseignées par le parseur de format, si bien que le routage reprend en partie la détection de format.
```
**Preuve :** `src/logminer/agents/model_router.py` (`apply_open_set_rejection`, règle `fallback_route` ; `_score_dataframe`, marqueurs `dataset_values`/`subtype_values`) ; `agent5_router_open_set_20261104T145601Z/routes.csv` (mode N : `bgl_loghub` 103 → 70, `linux_2k` 233 → 63).

### D.16 `chapitre4_implementation.tex`, § Adaptateurs (l. 27)

**Actuel :**
```
Cette présence vérifie donc le fonctionnement de la voie Apache, mais elle n'est pas comparable à l'utilisation d'un corpus réel comportant plusieurs milliers d'événements.
```
**Proposé :**
```
Cette présence vérifie seulement que la voie Apache s'exécute de bout en bout ; elle ne valide pas le parseur, qui reste à éprouver sur un journal d'accès réel.
```
**Preuve :** `agent5_multiformat_20261104T150111Z/result.json` (`real_apache_corpus_found_locally: false`).

### D.17 `chapters/chapitre6_discussion.tex` (l. 14)

**Actuel :**
```
Dans le protocole open-set, il peut également refuser une source lorsque les indices disponibles ne permettent pas de l’associer convenablement aux familles connues ; c’est ce qui est observé pour les trois fichiers inconnus évalués.
```
**Proposé :**
```
Dans le protocole open-set, il peut également refuser une source lorsque les indices disponibles ne permettent pas de l’associer convenablement aux familles connues ; c’est ce qui est observé pour les 20 fichiers inconnus évalués, au prix de faux rejets lorsque le schéma d’une source connue s’écarte de celui vu à la calibration (chapitre~\ref{chap:validite}).
```
**Preuve :** `agent5_router_open_set_20261104T145601Z`.

### D.18 `chapitre6_discussion.tex` (l. 74)

**Actuel :**
```
Les tests open-set devraient inclure davantage de familles inconnues et les validations temporelles couvrir plusieurs périodes. Pour Apache, l’utilisation d’un corpus réel remplacerait avantageusement la fixture employée.
```
**Proposé :**
```
Les tests open-set devraient porter sur des familles inconnues de provenance documentée et sur des variantes de schéma des familles connues, et les validations temporelles couvrir plusieurs périodes. Pour Apache, un journal d’accès public remplacerait la fixture employée.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z` (faux rejets sur variantes de schéma) ; protocole C.3.

### D.19 `chapters/chapitre6_conclusion.tex` (l. 13)

**Actuel :**
```
Au seuil gelé, le routeur rejette les trois fichiers inconnus testés sans rejeter les 28 fichiers connus. La chaîne multiformat lit, parse et normalise $7\,001$ unités.
```
**Proposé :**
```
Au seuil gelé, le routeur rejette les 20 fichiers inconnus évalués ; il rejette aussi 3 des 46 fichiers connus, dont le schéma n'avait pas été vu à la calibration. Le test d'intégration multiformat traite $7\,001$ unités, dont une seule pour Apache.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z` ; `agent5_multiformat_20261104T150111Z`.

### D.20 `chapitre6_conclusion.tex` (l. 27)

**Actuel :**
```
Sur le jeu indépendant retenu, le routeur oriente correctement les 28 fichiers connus et rejette les trois inconnus après application du seuil gelé.
```
**Proposé :**
```
Avec le seuil gelé, le routeur rejette les 20 fichiers inconnus évalués et oriente correctement les fichiers connus qu'il accepte, mais rejette à tort 3 des 46 fichiers connus.
```
**Preuve :** idem.

### D.21 `chapitre6_conclusion.tex`, tableau des hypothèses (H1, l. 63 ; H3, l. 71)

**Actuel (H1) :**
```
$7\,001/7\,001$ unités présentes traitées ; couverture universelle non testée. \\
```
**Proposé (H1) :**
```
Test d'intégration : $7\,001/7\,001$ unités émises, dont une fixture Apache ; remplissage des champs variable selon la source. \\
```
**Actuel (H3) :**
```
Routage compatible, rejet 3/3 et faux rejet 0/28 dans un jeu indépendant limité ; sur le plan prédictif, le gain apporté par le routage n'est pas systématique (cf.\ QR3). \\
```
**Proposé (H3) :**
```
Routage compatible ; rejet 20/20 et faux rejet 3/46 après extension, sans recalibration ; sur le plan prédictif, le gain apporté par le routage n'est pas systématique (cf.\ QR3). \\
```
**Preuve :** `agent5_router_open_set_20261104T145601Z` ; `agent5_multiformat_20261104T150111Z`.

### D.22 `chapitre6_conclusion.tex` (l. 101) — remplacer la répétition de limite par un renvoi

**Actuel :**
```
L'évaluation open-set du routeur repose pour sa part sur seulement trois fichiers inconnus.
```
**Proposé :**
```
Les limites de l'évaluation open-set du routeur sont détaillées au chapitre~\ref{chap:validite}.
```
**Preuve :** règle de non-répétition ; formulation complète en D.1.

### D.23 `chapters/chapitre7_reproductibilite_deploiement.tex` (l. 54)

**Actuel :**
```
Le routeur open-set utilise enfin 31 fichiers indépendants : 28 connus et 3 inconnus. Le seuil 100 est déterminé uniquement à partir des sources connues. Le modifier après observation des trois fichiers inconnus reviendrait à exécuter une expérience différente.
```
**Proposé :**
```
Le routeur open-set utilise enfin 31 fichiers distincts : 28 connus et 3 inconnus. Le seuil 100 est déterminé uniquement à partir des sources connues. Le modifier après observation des fichiers inconnus reviendrait à exécuter une expérience différente. L'extension à 37 fichiers supplémentaires applique ce seuil sans le modifier ; elle est reproductible par \texttt{agent5\_router\_open\_set\_extended.py}, dont les étiquettes sont figées dans \texttt{sources\_config.json}.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z/sources_config.json`. *Intégration :* copier le script dans `scripts/` ou citer son chemin `revision_reports/agent_5/scripts/`.

### D.24 `chapters/annexes.tex`, tableau des chiffres-clés (l. 67, 68, 72)

**Actuel :**
```
Routeur open-set & rejet 3/3 ; faux rejet 0/28 & \texttt{router\_open\_set\_final\_tradeoff\_diagnostic.csv} \\
Multiformat & $7\,001/7\,001$ & \texttt{multiformat\_balanced\_summary.csv} \\
```
**Proposé :**
```
Routeur open-set & rejet 3/3 ; faux rejet 0/28 & \texttt{router\_open\_set\_final\_tradeoff\_diagnostic.csv} \\
Routeur open-set étendu & rejet 20/20 ; faux rejet 3/46 & \texttt{agent5\_router\_open\_set\_20261104T145601Z/result.json} \\
Multiformat (intégration) & $7\,001/7\,001$, dont 1 fixture Apache & \texttt{multiformat\_balanced\_summary.csv} \\
```
**Actuel :**
```
Corrélation & F1 0,812500 & \texttt{data/processed/final\_experiments\_2026/correlation\_synthetic\_summary.json} \\
```
**Proposé :**
```
Corrélation & TP 13, FP 4, FN 2 ; F1 0,812500 & \texttt{data/processed/final\_experiments\_2026/correlation\_synthetic\_summary.json} \\
Corrélation, 20 graines & S1 : P 0,9884, R 0,5973 ; S2 : P 0,9896, R 0,4835 & \texttt{agent5\_correlation\_20261104T141916Z/result.json} \\
```
**Preuve :** les artefacts cités dans chaque ligne.

### D.25 `annexes.tex`, § Conditions d'interprétation (l. 156)

**Actuel :**
```
Le routage open-set porte sur trois inconnus.
```
**Proposé :**
```
Les limites du routage open-set sont détaillées au chapitre~\ref{chap:validite}.
```
**Preuve :** renvoi (D.1).

### D.26 `annexes.tex`, notes de figures (l. 210 et 213)

**Actuel :**
```
Au seuil 100, le rejet des inconnus vaut 3/3, le faux rejet des connus 0/28, la couverture 0,903226 et l’exactitude sélective 1,0. La \texttt{decision\_margin} reste un score heuristique et non une probabilité.
```
**Proposé :**
```
Au seuil 100, le rejet des inconnus vaut 3/3 et le faux rejet des connus 0/28 ; l’exactitude sélective vaut 1,0. La couverture n’est pas interprétée, car elle dépend de la proportion d’inconnus dans le jeu. La \texttt{decision\_margin} reste un score heuristique et non une probabilité.
```
*Intégration :* régénérer la figure sans la courbe « Coverage » (`scripts/run_router_open_set_consolidation.py`, l. 245), ou conserver cette phrase si la figure reste inchangée.

**Actuel :**
```
Les $7\,001$ unités présentes sont lues, parsées et normalisées. HDFS et BGL contribuent chacun $1\,000$ unités, tandis qu’Apache repose sur une seule fixture. Cette couverture ne mesure ni la complétude de tous les champs ni une compatibilité universelle.
```
**Proposé :**
```
Les $7\,001$ unités présentes sont lues et émises sans erreur ; il s’agit d’un test d’intégration. Chaque source réelle contribue $1\,000$ unités, tandis qu’Apache repose sur une seule fixture.
```
**Preuve :** `router_open_set_summary.json` ; `agent5_multiformat_20261104T150111Z/result.json`.

### D.27 `main.tex`, résumé français (l. 338-344 et 360-362)

**Actuel :**
```
La validation multiformat lit, parse et normalise $7\,001/7\,001$ unités.
Ce résultat mesure la couverture fonctionnelle des formats testés ; il
n'établit ni la complétude de tous les champs ni la conservation universelle
du contenu brut. Une politique
open-set calibrée uniquement sur les sources connues rejette $3/3$ fichiers
inconnus sans faux rejet parmi $28$ fichiers connus ; la couverture est
$0{,}903226$ et la marge de décision n'est pas une probabilité calibrée.
```
**Proposé :**
```
Un test d'intégration multiformat lit et émet $7\,001/7\,001$ unités, dont
une seule unité Apache issue d'une fixture ; le remplissage des champs varie
selon la source. Une politique open-set calibrée uniquement sur les sources
connues, puis gelée, rejette $20/20$ fichiers inconnus (intervalle exact à
95~\% : $[0{,}83\,;\,1]$) et $3/46$ fichiers connus ($[0{,}01\,;\,0{,}18]$) ;
la marge de décision n'est pas une probabilité calibrée.
```
**Actuel :**
```
Le corrélateur, évalué sur un corpus synthétique contrôlé, obtient une
précision de $0{,}764706$, un rappel de $0{,}866667$ et un F1 pairwise de
$0{,}812500$.
```
**Proposé :**
```
Le corrélateur, évalué sur des corpus synthétiques construits par l'auteur,
réunit 13 des 15 paires attendues pour 4 paires erronées sur le corpus de
référence ; sur 20 corpus générés, sa précision dépasse $0{,}98$ mais son
rappel reste de $0{,}60$ avec des clés stables et de $0{,}48$ avec des
incidents multi-étapes, la fenêtre fixe fragmentant les incidents longs.
```
**Preuve :** `agent5_router_open_set_20261104T145601Z` ; `agent5_correlation_20261104T141916Z` (S1 : P 0,9884, R 0,5973 ; S2 : P 0,9896, R 0,4835) ; `agent5_multiformat_20261104T150111Z`.

### D.28 `main.tex`, résumé anglais (l. 457-463 et 477-479)

**Actuel :**
```
The multi-format validation reads, parses, and normalizes $7,001/7,001$
units. This result measures functional coverage of the tested formats; it
does not establish field completeness or universal preservation of raw data.
An open-set policy calibrated only on known sources
rejects $3/3$ unknown files without falsely rejecting any of the 28 known
files; coverage is $0.903226$, and the decision margin is not a calibrated
probability.
```
**Proposé :**
```
A multi-format integration test reads and emits $7,001/7,001$ units,
including a single Apache unit taken from a fixture; field completeness
varies across sources. An open-set policy calibrated only on known sources
and then frozen rejects $20/20$ unknown files (exact 95\% interval
$[0.83, 1]$) and $3/46$ known files ($[0.01, 0.18]$); the decision margin
is not a calibrated probability.
```
**Actuel :**
```
The correlation mechanism,
evaluated on a controlled synthetic corpus, obtains a precision of
$0.764706$, a recall of $0.866667$, and a pairwise F1-score of $0.812500$.
```
**Proposé :**
```
The correlation mechanism,
evaluated on author-built synthetic corpora, joins 13 of the 15 expected
pairs with 4 erroneous pairs on the reference corpus; on 20 generated
corpora its precision exceeds $0.98$, but its recall is $0.60$ with stable
keys and $0.48$ with multi-stage incidents, because the fixed window
fragments long incidents.
```
**Preuve :** idem D.27.

### D.29 `main.tex`, résumé en lingala (l. 583-584) — suppression seulement

**Actuel :**
```
faux rejet kati na $28$ fichiers connus ; couverture ezali
$0{,}903226$, mpe marge ya décision ezali te probabilité calibrée.
```
**Proposé :**
```
faux rejet kati na $28$ fichiers connus ; marge ya décision ezali te
probabilité calibrée.
```
*Blocage :* la mise à jour des chiffres (20/20, 3/46, corrélation), dans ce passage et aux l. 602-604, doit être traduite par l'auteur.
**Preuve :** `router_open_set_summary.json`.
