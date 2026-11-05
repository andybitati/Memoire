# Agent 4 — Révision BGL et CSE-CIC-IDS2018 : notes de correctifs

## En-tête : effort d'intégration et blocages

**Effort estimé** : 3 à 4 heures. Le travail comprend 19 blocs de remplacement, deux nouvelles sous-sections avec tableau au chapitre 5, l'ajout de lignes au tableau d'index des preuves en annexe et une recompilation. Aucune figure nouvelle n'est requise. Les figures existantes `fig_bgl_*` et `fig_csecic_*` restent exactes pour les runs qu'elles citent.

**Blocages** :
1. **Résumé en lingala** (`main.tex`, l. 559-575) : il doit recevoir les mêmes corrections que les résumés français et anglais (patchs P-M1 à P-M4). L'agent ne peut pas produire une traduction lingala fiable ; l'auteur doit s'en charger.
2. **Journées CSE-CIC-IDS2018 absentes** : seules les journées du 15 et du 16 février 2018 sont présentes localement (`data/raw/external/CSE-CIC-IDS2018/`, 2 fichiers). Aucune autre journée ne figure sous `data/`. L'évaluation inter-journées élargie n'est donc pas réalisable ici ; le protocole à exécuter figure à la section C.
3. **Choix post hoc des protocoles BGL G et F** : le protocole G suit une règle positionnelle qui n'utilise pas les labels. Il a cependant été conçu après l'échec du protocole E et après la cartographie des familles d'anomalies. Le protocole F a été choisi au vu des labels. Le texte proposé le signale ; le jury doit pouvoir le lire.
4. **Reproduction du Random Forest publié** : la régression logistique publiée est reproduite à l'identique sur 5 graines sur 5. Le Random Forest est reproduit à 0,0011 près au plus par graine (moyenne 0,400882 contre 0,401375 publiée). Cause probable : l'aller-retour CSV des pools figés. Aucune conclusion n'en dépend.

## Artefacts produits (tous sous `revision_reports/agent_4/`)

| run_id | Script | Résultat principal |
| --- | --- | --- |
| `agent4_bgl_second_protocol_20261104T142629Z` | `scripts/bgl_second_protocol.py` | `artifacts/bgl/agent4_bgl_second_protocol_20261104T142629Z__result.json`, `…__group_metrics.csv` (protocoles R0, B5, B10, B20, C, D, E) |
| `agent4_bgl_contiguous_horizon_20261104T145740Z` | `scripts/bgl_known_template_diagnostic.py G` | `artifacts/bgl/agent4_bgl_contiguous_horizon_20261104T145740Z__result.json`, `…__group_metrics.csv` (protocole G) |
| `agent4_bgl_known_template_diag_20261104T143926Z` | `scripts/bgl_known_template_diagnostic.py` (F) | `artifacts/bgl/agent4_bgl_known_template_diag_20261104T143926Z__result.json`, `…__group_metrics.csv` (protocole F, diagnostic) |
| `agent4_bgl_anomaly_family_map_20261104T144946Z` | `scripts/bgl_anomaly_family_map.py` | `artifacts/bgl/agent4_bgl_anomaly_family_map_20261104T144946Z__result.json` |
| `agent4_bgl_drain_match_check_20261104T145500Z` | commande en ligne (sortie conservée) | `artifacts/bgl/agent4_bgl_drain_match_check_20261104T145500Z__stdout.txt` |
| `agent4_csecic_shortcut_20261104T144738Z` | `scripts/csecic_shortcut_audit.py` | `artifacts/csecic/agent4_csecic_shortcut_20261104T144738Z__result.json` + 5 CSV + `…__printed_summary.txt` |

SHA-256 des entrées : `BGL.log` = `666130b15ef44eb32fd02bd053e6c6e007c37696b5e7e8b9d8e45b729876a5d2`, identique à `bgl_preparation.json`. Les SHA-256 des deux CSV CSE-CIC-IDS2018 et des pools publiés sont consignés dans `inputs` du JSON CSE-CIC.

Environnement : `.venv-hdfs-bgl\Scripts\python.exe`, commit `35da3a9…`. Le script BGL réutilise sans les modifier `parse_bgl`, `drain_config`, `assign_templates`, `histogram_scores`, `select_threshold` et `prediction_metrics` de `scripts/run_strict_sequence_experiments.py`. Le protocole R0 reproduit exactement le run publié : seuil 10,81975828421028, TP 2 885, FP 545, TN 16 478, FN 0, F1 0,913698.

---

## A. BGL — constats

### A1. Unité d'analyse : événement brut, pas fenêtre (incohérence texte/code)

- `docs/memoire/final_experiments_2026/configs/strict_sequence_protocol.json` : `"BGL": {"observation_unit": "raw log event", "group_key": null}`.
- `scripts/run_strict_sequence_experiments.py::histogram_scores` calcule un score par ligne : moyenne de `-log(max(count,1)/N_normal_train)` sur trois histogrammes (template Drain3, source, sévérité). Aucune agrégation n'a lieu.
- Des variables causales sur fenêtre glissante de 30 minutes existent (`causal_features`, `prior_*_window_*`). Elles alimentent IsolationForest, ZScore, IQR et AutoencoderMLP, mais **pas Histogram**.
- Le mémoire écrit « BGL suit un protocole différent, fondé sur des fenêtres » (ch. 4) et « fenêtre/template » (tableau 5.1). **Les deux formulations sont inexactes** (patchs P-4.1 et P-5.1).

### A2. Le F1 publié de 0,913698 équivaut exactement à une règle de nouveauté de sévérité

Source : `agent4_bgl_second_protocol_20261104T142629Z__result.json`, `results[R0_reproduction].histogram_decision_decomposition`.
- Le train compte 49 999 événements, 0 positif, et une seule sévérité normale : `["INFO"]`. Drain3 n'y forme que 7 clusters.
- Le score maximal possible vaut ln(49 999) = 10,81975828421028. Le seuil choisi sur validation lui est égal (`threshold_equals_max_possible_score: true`). Est donc prédit anomal tout événement dont le template, la source et la sévérité sont tous absents du train normal (`hist_pred_equals_sev_and_src_and_tpl_absent: true`).
- Sur ce test, la décision est **identique** à la règle « sévérité absente du train normal » (`hist_pred_equals_severity_novelty: true`). Le modèle `SeverityNoveltyBaseline` obtient F1 0,913698 et la même matrice de confusion (2 885 / 545 / 16 478 / 0).
- Composition du test par sévérité et label : FATAL\|1 = 2 884, FATAL\|0 = 544, FAILURE\|1 = 1, ERROR\|0 = 1, INFO\|0 = 16 478.
- **Contradiction** : « Histogram dépasse donc nettement une règle de nouveauté brute » (ch. 5) n'est vrai que pour la nouveauté de *template*. Une autre règle de nouveauté, celle de sévérité, l'égale exactement.

### A3. Second protocole et variantes : résultats

Seuil choisi sur validation dans tous les cas. Drain3 est ajusté sans label sur le train puis gelé ; les histogrammes portent sur les événements normaux du train ; l'unité est l'événement.

| Protocole | Entraînement | Test (N / positifs) | Positifs à template connu | F1 Histogram | Matrice (TP/FP/TN/FN) | F1 baseline « template inconnu » | run_id |
| --- | --- | --- | ---: | ---: | --- | ---: | --- |
| R0 (publié) | lignes 1 399 389-1 449 388 | 19 908 / 2 885 | 0 | 0,913698 | 2885/545/16478/0 | 0,277885 | second_protocol |
| B5 | 5 blocs × 10 000 lignes avant validation | idem R0 | 4 | 0,923791 | 2885/476/16547/0 | 0,280130 | second_protocol |
| B10 | 10 blocs | idem R0 | 5 | 0,891293 | 2677/445/16578/208 | 0,280333 | second_protocol |
| B20 | 20 blocs | idem R0 | 6 | 0,730935 | 2885/2124/14899/0 | 0,292433 | second_protocol |
| C | R0 ; Drain3 adapté sans label sur train + validation | idem R0 | 4 | 0,913698 | 2885/545/16478/0 | 0,279627 | second_protocol |
| D | chronologique 60/20/20, 20/10/10 blocs | 97 107 / 2 439 | 7 | 0,598528 | 2439/3272/91396/0 | 0,057592 | second_protocol |
| E | 20 blocs entre 3 800 001 et la validation | idem R0 | 6 | 0,940466 | 2883/363/16660/2 | 0,915567 | second_protocol |
| **G** | **80 000 lignes contiguës 4 163 167-4 243 166 ; validation 4 243 167-4 263 166** | **idem R0** | **2 880** | **0,941927** | **2879/349/16674/6** | **0,003257** | contiguous_horizon |
| F (diagnostic, choisi au vu des labels) | lignes 1-200 000 ; val. 700 001-800 000 | 149 375 / 3 400 | 3 000 | 0,885166 | 3276/726/145249/124 | 0,163767 | known_template_diag |

Protocole G (`agent4_bgl_contiguous_horizon_20261104T145740Z__result.json`) :
- Train de 74 162 événements analysés, dont 10 327 positifs ; 299 clusters. Seuil 6,977042351996222 (F1 de validation 0,999493).
- Groupe KNOWN_TEMPLATE : 19 723 événements, 2 880 positifs ; TP 2 875, FP 201, TN 16 642, FN 5 ; précision 0,934655, rappel 0,998264, F1 0,965413.
- Groupe UNKNOWN_TEMPLATE : 185 événements, 5 positifs ; F1 0,050955.
- Couverture du parseur : 0,9293 % d'événements de test sur un template inconnu (0,1733 % des positifs, 1,0574 % des négatifs). Dans R0 : 89,8081 % (100 % des positifs, 88,0808 % des négatifs).
- Mécanisme : Drain3 reconnaît le template, mais les histogrammes ne comptent que les événements normaux. Un template rencontré à l'entraînement uniquement sur des anomalies reçoit donc la probabilité plancher. Histogram exploite ainsi, au train, la séparation normal/anomal par les labels, ce qui est conforme à la conception de R0 (`template_statistics_partition: "normal-labelled train only"`) et doit être dit.

### A4. Couverture du parseur : diagnostic

- `agent4_bgl_anomaly_family_map_20261104T144946Z__result.json` : 2 874 des 2 885 positifs du test R0 appartiennent à une seule famille, « ciod: Error reading message prefix on [CioStream socket …] ». Elle apparaît pour la première fois ligne 4 215 995 et compte 5 468 occurrences avant le début du test.
- `agent4_bgl_drain_match_check_20261104T145500Z__stdout.txt` : aucune de ces 5 468 occurrences ne tombe dans les blocs d'entraînement de E. Un Drain3 ajusté sur ces seules occurrences reconnaît les 2 874 messages du test, soit 2 874 sur 2 874.
- Conclusion : l'absence de positifs à template connu dans R0 ne tient pas à une limite de Drain3. Elle tient à l'**échantillonnage temporel du train** et au caractère **en rafales** des familles d'anomalies BGL. Les taux d'inconnus parmi les *négatifs* (88,08 % dans R0, 0,9293 % des événements dans G) montrent que la couverture dépend d'abord de la proximité temporelle entre train et test.
- Selon le protocole, le F1 Histogram va de 0,598528 (D) à 0,941927 (G) et n'est pas monotone avec la taille du train (B5 > B10 > B20). Le baseline de nouveauté est inopérant dans G (0,003257) mais presque aussi bon qu'Histogram dans E (0,915567 contre 0,940466).

---

## B. CSE-CIC-IDS2018 — constats

Source unique : `artifacts/csecic/agent4_csecic_shortcut_20261104T144738Z__result.json`. Les tableaux lisibles sont dans `…__printed_summary.txt` ; le détail par graine figure dans les CSV `…__part1_published_setting_rows.csv` et `…__part2_observed_prevalence_rows.csv`.

### B1. Inventaire local
- Présents : `Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv` (375 945 899 octets) et `Friday-16-02-2018_TrafficForML_CICFlowMeter.csv` (333 723 605 octets). Aucun autre fichier CSE-CIC-IDS2018 sous `data/`.
- Lignes de données balayées (`part2_audit`) : 1 048 575 pour le 15 février ; 1 048 574 pour le 16 février, plus 1 en-tête répété. Les deux fichiers totalisent donc 1 048 575 lignes sous l'en-tête, soit exactement 2^20 − 1. Ce total est compatible avec une troncature à la limite de lignes d'un tableur ; **à vérifier** auprès de la source, sans conclusion à ce stade.
- Prévalence des attaques sur le fichier complet : 15 février 0,050066 ; 16 février 0,573924.

### B2. Évaluation à la prévalence observée (direction 15 → 16)
Protocole : échantillon de Bernoulli uniforme, indépendant du label, au taux de 0,15 par journée (157 319 et 157 366 lignes). Train de 50 000 lignes à prévalence naturelle ; test sur l'échantillon complet du 16 février (prévalence 0,5714) ; seuil 0,5 ; graines 42-46 ; hyperparamètres identiques au protocole publié.

| Modèle | Variables | F1 moyen [min ; max] | Précision | Rappel | FPR |
| --- | --- | --- | ---: | ---: | ---: |
| LR | 78 | 0,994345 [0,981583 ; 0,999672] | 0,9888 | 1,0000 | 0,0153 |
| RF | 78 | 0,095915 [0,037969 ; 0,234837] | 0,9996 | 0,0521 | 0,0000 |
| LR | sans Dst Port (77) | 0,728397 [0,728395 ; 0,728401] | 0,5728 | 1,0000 | 0,9940 |
| RF | sans Dst Port (77) | 0,071316 | 0,0846 | 0,0619 | 0,8167 |
| LR | Dst Port seul | 0,999728 | 0,9995 | 1,0000 | 0,0007 |
| RF | Dst Port seul | 0,869156 | 1,0000 | 0,7686 | 0,0000 |
| Règle fixe `Dst Port < 1024` (sans apprentissage) | 1 | 0,999728 | 0,9995 | 1,0000 | 0,0007 |

### B3. Raccourci par Dst Port : tests de l'hypothèse
- Distribution des ports (`part2_dst_port_by_family_sample`). Le 16 février, 0,0726 % des flux bénins ont un Dst Port < 1024. Hulk est entièrement sur le port 80, SlowHTTPTest entièrement sur le port 21. Le 15 février, 76,01 % des flux bénins ont un Dst Port < 1024 (53, 80, 443, 3389, 445 en tête) ; GoldenEye et Slowloris sont sur le port 80.
- La règle fixe `Dst Port < 1024`, sans apprentissage, reproduit exactement le F1 de la LR mono-variable : 0,999720 sur test équilibré (réglage publié) et 0,999728 à prévalence observée. Le score publié de Dst Port seul est donc entièrement expliqué par un seuil de port.
- Inter-journées. Dans le sens 16 → 15 (test à prévalence 0,0499), le F1 tombe à 0,234195 pour la LR (78 variables), 0,109142 pour la LR sur Dst Port seul et 0,121517 pour la règle `< 1024`. En intra-journée sur le 15 février, la LR sur Dst Port seul atteint 0,161611. **Dst Port ne sépare les classes que le 16 février** : la propriété tient à cette journée, pas aux attaques DoS.
- Ablation. Sans Dst Port, la LR 15 → 16 déclare presque tout flux comme attaque (FPR 0,9940 ; F1 0,661077 sur test équilibré dans le réglage publié, 0,728397 à prévalence observée).
- Importance par permutation (réglage publié, graine 42, 4 000 flux de test équilibrés) : pour la LR, Dst Port arrive en tête avec une perte de F1 de 0,5004, suivi de Fwd Seg Size Min (0,1391).
- Qualification : il ne s'agit pas d'une fuite de label au sens strict, puisqu'aucune variable ne code le label. Il s'agit d'un **raccourci propre à la journée de test**. La LR, linéaire et monotone en Dst Port, extrapole « port bas ⇒ attaque » ; cette règle coïncide avec la composition du 16 février et échoue sur le 15.

### B4. Pourquoi le Random Forest échoue (0,40) alors que la LR réussit (0,999)
- Le RF n'est pas faible en soi : en intra-journée, il atteint un F1 de 0,998598 le 15 février et de 0,999958 le 16.
- SlowHTTPTest (port 21) n'est jamais détecté par le RF en 15 → 16 : taux de prédiction « attaque » égal à 0,0 pour toutes les graines et tous les jeux de variables, dans le réglage publié comme à prévalence observée. Les attaques d'entraînement sont toutes sur le port 80. Un arbre découpe Dst Port en intervalles autour de 80 au lieu d'une pente monotone, si bien que le port 21 tombe hors de la région « attaque ». Le RF mono-variable Dst Port obtient 0,872314 dans le réglage publié, soit exactement la règle « port ∈ ports d'attaque du train » ({80}).
- Avec 78 variables, le RF fonde sa décision sur des variables de dynamique de flux : l'importance par impureté place en tête Fwd Seg Size Min (0,2195), puis Flow IAT Mean (0,0638) et Flow Pkts/s (0,0597). Or ces distributions diffèrent entre GoldenEye/Slowloris et Hulk/SlowHTTPTest. Dans le réglage publié, le taux de détection de Hulk varie de 0,0895 à 0,9952 selon la graine et le FPR de 0,0001 à 0,8752. Cette dispersion explique la moyenne de 0,40 et les extrêmes 0,129605-0,622379.
- À prévalence observée, le RF tombe à 0,095915, avec un rappel de 0,0521.
- Synthèse : l'écart LR/RF ne mesure pas une meilleure généralisation de la LR. Il mesure la rencontre entre l'extrapolation monotone de la LR sur Dst Port et une particularité du fichier du 16 février.

---

## C. Expérience non réalisable ici : autres journées CSE-CIC-IDS2018

**Statut** : NON RÉALISÉE, faute de données locales. Seuls le 15 et le 16 février sont présents.

**Protocole à exécuter** :
1. Télécharger les autres fichiers `Processed Traffic Data for ML Algorithms/*_TrafficForML_CICFlowMeter.csv` du bucket officiel `s3://cse-cic-ids2018/` (la liste exacte des journées est à relever sur le bucket), consigner taille, ETag et SHA-256 comme dans `external_csecicids2018_protocol.json`, et vérifier le nombre de lignes (B1).
2. Premier contrôle, sans apprentissage : pour chaque journée, part des flux bénins de Dst Port < 1024 et F1 de la règle fixe `Dst Port < 1024`. Si la part est élevée, comme le 15 février (0,7601), le raccourci ne tient pas sur cette journée.
3. Évaluation leave-one-day-out et par paires (train jour i, test jour j), à prévalence observée, avec LR et RF sous les mêmes hyperparamètres, pour trois jeux de variables : ALL, NO_DST_PORT, et Dst Port remplacé par une catégorie de service (bien connu / enregistré / éphémère). Seuil 0,5 ou seuil choisi sur une journée de validation distincte, graines 42-46.
4. Rapporter, par famille d'attaque, F1, précision, rappel, FPR, matrice de confusion et taux de détection, en distinguant les familles vues et non vues à l'entraînement.
5. Le script `scripts/csecic_shortcut_audit.py` s'adapte en étendant le dictionnaire `DAYS` et les `directions`. Budget estimé : environ 13 minutes de calcul pour deux journées sur cette machine (`elapsed_sec` du JSON), échelle à peu près linéaire en nombre de paires.

---

## D. Modifications de texte proposées

Conventions : « Actuel » reproduit le texte exact du .tex ; « Proposé » donne le remplacement. La formulation complète des limites figure au chapitre 5 (P-5.4 et P-5.8) ; ailleurs, renvois.

### P-4.1 — `chapters/chapitre4_implementation.tex`, section « Parsing HDFS et BGL » (l. 78)
**Actuel** :
> BGL suit un protocole différent, fondé sur des fenêtres.

**Proposé** :
> BGL suit un protocole différent : chaque ligne du journal constitue une unité d'évaluation, et le score Histogram est calculé événement par événement, sans agrégation par fenêtre. Les variables causales sur fenêtre de 30 minutes ne servent qu'aux autres détecteurs.

**Preuve** : `strict_sequence_protocol.json` (`observation_unit: "raw log event"`) ; `scripts/run_strict_sequence_experiments.py::histogram_scores` ; `agent4_bgl_second_protocol_20261104T142629Z__result.json` (`observation_unit`).

### P-5.1 — `chapters/chapitre5_resultats.tex`, tableau « Synthèse des protocoles expérimentaux » (l. 35)
**Actuel** :
> BGL & fenêtre/template & Apport d’Histogram au-delà d’un baseline de nouveauté. \\

**Proposé** :
> BGL & événement/template & Apport d’Histogram au-delà de baselines de nouveauté ; couverture du parseur. \\

**Preuve** : comme P-4.1.

### P-5.2 — `chapitre5_resultats.tex`, section « BGL : templates connus et inconnus » (l. 165-167)
**Actuel** :
> \section{BGL : templates connus et inconnus}
>
> Le détecteur Histogram est évalué sur $19\,908$ unités, dont $2\,885$ positives.

**Proposé** :
> \section{BGL : templates connus et inconnus}
> \label{sec:bgl-resultats}
>
> Le détecteur Histogram est évalué sur $19\,908$ événements, dont $2\,885$ positifs.

**Preuve** : `ds_bgl_known_unknown_20260910T082706Z__bgl_known_unknown_result.json` (`test_rows`) ; unité : P-4.1.

### P-5.3 — `chapitre5_resultats.tex`, même section (l. 181)
**Actuel** :
> Le baseline \texttt{UnknownTemplateBaseline} prédit une anomalie pour tout template inconnu. Il atteint seulement un F1 de $0{,}277885$, avec $14\,994$ faux positifs. Histogram dépasse donc nettement une règle de nouveauté brute, mais la composition du test demeure déterminante.

**Proposé** :
> Le baseline \texttt{UnknownTemplateBaseline} prédit une anomalie pour tout template inconnu. Il atteint seulement un F1 de $0{,}277885$, avec $14\,994$ faux positifs. Histogram dépasse donc la nouveauté de template, mais pas toute règle de nouveauté. Son score moyenne $-\log p$ sur trois histogrammes appris sur les événements normaux du train : template, source et sévérité. Or les $49\,999$ événements d’entraînement sont tous de sévérité \texttt{INFO} et Drain3 n’y forme que 7 clusters. Le seuil choisi sur validation est égal à $\ln 49\,999$, soit le score maximal possible : un événement n’est déclaré anomal que si son template, sa source et sa sévérité sont tous absents du train. Sur ce test, cette décision coïncide exactement avec la règle « sévérité absente du train normal », qui produit la même matrice de confusion et le même F1. Le résultat de ce protocole mesure donc une nouveauté de sévérité, non une modélisation de la dynamique des journaux.

**Preuve** : `revision_reports/agent_4/artifacts/bgl/agent4_bgl_second_protocol_20261104T142629Z__result.json` → `results[0]` (R0_reproduction) : `histogram_decision_decomposition` (`train_normal_severities: ["INFO"]`, `threshold_equals_max_possible_score: true`, `hist_pred_equals_severity_novelty: true`), `coverage.drain3_clusters: 7` ; `…__group_metrics.csv`, lignes `SeverityNoveltyBaseline`/`ALL`.

### P-5.4 — `chapitre5_resultats.tex`, **nouvelle sous-section** insérée après la figure `fig:bgl-baseline` (après l. 193, avant `\section{CSE-CIC-IDS2018 …}`)
**Actuel** : (aucun texte)

**Proposé** :
> \subsection{Second protocole : anomalies à template connu}
> \label{sec:bgl-second-protocole}
>
> Le protocole principal ne contient aucun positif sur un template connu. Plusieurs variantes ont été évaluées sur la même plage de test, avec un seuil choisi sur validation, un Drain3 ajusté sans label sur le seul train puis gelé, et des histogrammes calculés sur les événements normaux du train. Les variantes à entraînement élargi ou adapté laissent au plus 7 positifs sur un template connu. En effet, 2\,874 des 2\,885 positifs du test appartiennent à une seule famille de messages (\texttt{ciod: Error reading message prefix on CioStream socket}), apparue peu avant le test. Un entraînement contigu de $80\,000$ lignes placé juste avant la validation (protocole G) couvre cette famille : 2\,880 positifs du test portent alors un template connu.
>
> \begin{table}[H]
> \centering
> \caption{BGL : protocoles complémentaires, test et seuil indépendants.}
> \label{tab:bgl-protocoles}
> \small
> \begin{tabular}{lrrrr}
> \toprule
> \textbf{Protocole} & \textbf{N test / positifs} & \textbf{Positifs connus} & \textbf{F1 Histogram} & \textbf{F1 template inconnu} \\
> \midrule
> Principal (49\,999 lignes) & 19\,908 / 2\,885 & 0 & 0,913698 & 0,277885 \\
> 5 blocs de 10\,000 lignes & 19\,908 / 2\,885 & 4 & 0,923791 & 0,280130 \\
> 10 blocs & 19\,908 / 2\,885 & 5 & 0,891293 & 0,280333 \\
> 20 blocs & 19\,908 / 2\,885 & 6 & 0,730935 & 0,292433 \\
> Drain3 adapté sur validation & 19\,908 / 2\,885 & 4 & 0,913698 & 0,279627 \\
> Chronologique 60/20/20 & 97\,107 / 2\,439 & 7 & 0,598528 & 0,057592 \\
> 20 blocs avant le test & 19\,908 / 2\,885 & 6 & 0,940466 & 0,915567 \\
> G : 80\,000 lignes contiguës & 19\,908 / 2\,885 & 2\,880 & 0,941927 & 0,003257 \\
> \bottomrule
> \end{tabular}
> \end{table}
>
> Dans le protocole G, le seuil vaut $6{,}977042$ et la matrice de confusion globale compte 2\,879 vrais positifs, 349 faux positifs, 16\,674 vrais négatifs et 6 faux négatifs. Sur les 19\,723 événements à template connu, dont 2\,880 positifs, Histogram atteint une précision de $0{,}934655$, un rappel de $0{,}998264$ et un F1 de $0{,}965413$. La part d’événements de test à template inconnu tombe à $0{,}9293\,\%$, contre $89{,}8081\,\%$ dans le protocole principal ; elle vaut $0{,}1733\,\%$ parmi les positifs et $1{,}0574\,\%$ parmi les négatifs. Une sévérité inconnue n’explique plus la décision : la règle correspondante n’obtient qu’un F1 de $0{,}000693$. Histogram tire alors parti de templates rencontrés à l’entraînement uniquement sur des événements étiquetés anormaux, puisque ses histogrammes ne comptent que les événements normaux.
>
> Trois limites encadrent cette lecture. Premièrement, la couverture du parseur dépend surtout de la proximité temporelle entre entraînement et test, car les familles d’anomalies de BGL surviennent en rafales. Parmi les négatifs, la part de templates inconnus passe de $88{,}0808\,\%$ à $1{,}0574\,\%$, et les échecs de couverture des variantes tiennent à l’échantillonnage du train, non à Drain3, qui reconnaît la totalité des messages de la famille dominante dès qu’il l’a rencontrée. Deuxièmement, le F1 varie de $0{,}598528$ à $0{,}941927$ selon le protocole et n’évolue pas de façon monotone avec la taille du train ; aucune valeur unique ne résume donc la performance sur BGL. Troisièmement, le protocole G suit une règle positionnelle sans label, mais il a été conçu après examen de la position des familles d’anomalies : il démontre un mécanisme et ne constitue pas une estimation indépendante. Un diagnostic complémentaire, sur un segment initial choisi au vu des labels (3\,000 positifs connus sur 3\,400), donne un F1 de $0{,}956522$ sur le groupe connu.

**Preuves** :
- Lignes 1-4 et 6-7 du tableau, et les deux premières valeurs du paragraphe de limites (88,0808 % ; 0,598528) : `agent4_bgl_second_protocol_20261104T142629Z__result.json` (`results[*].coverage`, `test_metrics_histogram`) et `…__group_metrics.csv` (`UnknownTemplateBaseline`/`ALL`).
- Ligne G et paragraphe G : `agent4_bgl_contiguous_horizon_20261104T145740Z__result.json` (`threshold` 6,977042351996222 ; `group_rows` ; `coverage`) et `…__group_metrics.csv`.
- Famille dominante (2 874) : `agent4_bgl_anomaly_family_map_20261104T144946Z__result.json` (`test_R0_positive_families`).
- Reconnaissance de 2 874/2 874 messages : `agent4_bgl_drain_match_check_20261104T145500Z__stdout.txt`.
- Diagnostic complémentaire : `agent4_bgl_known_template_diag_20261104T143926Z__result.json`.

### P-5.5 — `chapitre5_resultats.tex`, section CSE-CIC-IDS2018 (l. 195-199)
**Actuel** :
> \section{CSE-CIC-IDS2018 : transfert et dépendance aux variables}
>
> \subsection{Protocole principal}
>
> L’entraînement utilise le 15 février 2018 et le test le 16 février 2018. Pour chacune des graines 42 à 46, $20\,000$ lignes d’entraînement et $20\,000$ de test sont équilibrées, avec 78 caractéristiques. La régression logistique atteint un F1 moyen de $0{,}999212$, contre $0{,}401375$ pour le Random Forest.

**Proposé** :
> \section{CSE-CIC-IDS2018 : transfert et dépendance aux variables}
> \label{sec:csecic-resultats}
>
> \subsection{Protocole principal}
>
> L’entraînement utilise le 15 février 2018 et le test le 16 février 2018 ; ce sont les deux seules journées disponibles localement. Pour chacune des graines 42 à 46, $20\,000$ lignes d’entraînement et $20\,000$ de test sont équilibrées, avec 78 caractéristiques. La régression logistique atteint un F1 moyen de $0{,}999212$, contre $0{,}401375$ pour le Random Forest. À la prévalence observée du 16 février ($0{,}5714$ dans l’échantillon de test), avec un entraînement à la prévalence naturelle du 15 février, la régression logistique obtient $0{,}994345$ (min. $0{,}981583$, max. $0{,}999672$) et le Random Forest $0{,}095915$.

**Preuve** : `agent4_csecic_shortcut_20261104T144738Z__result.json` → `part2_summary` (direction `15_to_16`, `feature_set` `ALL`) et `part2_audit` ; `…__part2_observed_prevalence_rows.csv`.

### P-5.6 — `chapitre5_resultats.tex`, sous-section « Coefficients et scores mono-feature » (l. 229)
**Actuel** :
> L’expérience mono-feature apporte un diagnostic particulièrement important : \texttt{Dst Port}, utilisé seul, atteint déjà un F1 moyen de 0,999720. Plusieurs autres variables sont beaucoup moins informatives et certaines conduisent à des comportements proches du hasard. Le score principal dépend donc fortement de la structure du scénario observé ; il serait excessif de l’interpréter comme une robustesse démontrée face à un changement d’environnement.

**Proposé** :
> L’expérience mono-feature apporte un diagnostic particulièrement important : \texttt{Dst Port}, utilisé seul, atteint déjà un F1 moyen de 0,999720. Une règle fixe, sans apprentissage, qui déclare attaque tout flux de port de destination inférieur à 1024 obtient exactement le même score. Le 16 février, seuls $0{,}0726\,\%$ des flux bénins vérifient cette condition, alors que toutes les attaques visent les ports 80 (Hulk) et 21 (SlowHTTPTest). Le score principal repose donc sur un raccourci propre à la journée de test, analysé en section~\ref{sec:csecic-raccourci}.

**Preuve** : `agent4_csecic_shortcut_20261104T144738Z__result.json` → `part1_summary` (`rule_dst_port_lt_1024` et `LogisticRegression`/`DST_PORT_ONLY` : 0,999720) ; `part2_dst_port_by_family_sample` (`2018-02-16|Benign.share_dst_port_lt_1024` = 0,0007264).

### P-5.7 — `chapitre5_resultats.tex`, sous-section « Ablation et permutation » (l. 259)
**Actuel** :
> Après permutation des labels d’entraînement, les F1 deviennent très instables selon les graines : environ 0,350, 0,575, 0,001, 0,400 et 0,374. On ne retrouve donc plus le comportement stable du protocole principal. Les contrôles effectués ne mettent pas en évidence de fuite triviale parmi les mécanismes testés, sans pour autant exclure toute fuite possible ni un biais structurel entre les deux journées.

**Proposé** :
> Après permutation des labels d’entraînement, les F1 deviennent très instables selon les graines : environ 0,350, 0,575, 0,001, 0,400 et 0,374. On ne retrouve donc plus le comportement stable du protocole principal. Aucune variable ne code directement le label, mais un biais structurel entre les deux journées est désormais établi (section~\ref{sec:csecic-raccourci}).

**Preuve** : comme P-5.8.

### P-5.8 — `chapitre5_resultats.tex`, **nouvelle sous-section** insérée après la figure `fig:csecic-permutation` (après l. 271, avant `\section{Routeur open-set}`)
**Actuel** : (aucun texte)

**Proposé** :
> \subsection{Raccourci par le port de destination et échec du Random Forest}
> \label{sec:csecic-raccourci}
>
> Une évaluation complémentaire conserve les hyperparamètres du protocole principal mais tire un échantillon uniforme, indépendant du label, de chaque journée. L’entraînement compte $50\,000$ lignes à prévalence naturelle ; le test est évalué à sa prévalence observée. Elle croise quatre directions et trois jeux de variables.
>
> \begin{table}[H]
> \centering
> \caption{CSE-CIC-IDS2018 à prévalence observée, F1 moyen sur cinq graines.}
> \label{tab:csecic-prevalence}
> \small
> \begin{tabular}{llrr}
> \toprule
> \textbf{Direction} & \textbf{Variables} & \textbf{LR} & \textbf{RF} \\
> \midrule
> 15 $\rightarrow$ 16 & 78 & 0,994345 & 0,095915 \\
> 15 $\rightarrow$ 16 & sans \texttt{Dst Port} & 0,728397 & 0,071316 \\
> 15 $\rightarrow$ 16 & \texttt{Dst Port} seul & 0,999728 & 0,869156 \\
> 16 $\rightarrow$ 15 & 78 & 0,234195 & 0,144013 \\
> intra 15 & 78 & 0,989686 & 0,998598 \\
> intra 16 & 78 & 0,999942 & 0,999958 \\
> \bottomrule
> \end{tabular}
> \end{table}
>
> Trois constats en découlent. D’abord, la séparation quasi parfaite tient à la journée du 16 février et non aux attaques DoS. Une règle fixe sur le port de destination (inférieur à 1024) atteint $0{,}999728$ sur le 16 février, mais $0{,}121517$ sur le 15, où $76{,}01\,\%$ des flux bénins visent des ports inférieurs à 1024. Le transfert inverse, du 16 vers le 15, ne dépasse pas $0{,}234195$. Ensuite, la régression logistique perd toute capacité de décision sans \texttt{Dst Port} : elle déclare presque tout flux comme attaque, avec un taux de faux positifs de $0{,}9940$. L’importance par permutation confirme ce rôle, \texttt{Dst Port} causant la plus forte perte de F1 ($0{,}5004$). Enfin, le Random Forest n’est pas faible en soi : il atteint $0{,}998598$ et $0{,}999958$ en intra-journée. Il échoue au transfert parce que ses arbres isolent le port 80, seul port d’attaque du 15 février, au lieu d’en extrapoler une pente. SlowHTTPTest, sur le port 21, n’est ainsi jamais détecté. Avec toutes les variables, ses décisions reposent sur des grandeurs de dynamique des flux qui diffèrent d’une famille DoS à l’autre : le taux de détection de Hulk varie de $0{,}0895$ à $0{,}9952$ selon la graine dans le protocole principal.
>
> L’écart entre les deux modèles ne traduit donc pas une meilleure généralisation de la régression logistique. Il résulte de la rencontre entre son extrapolation monotone sur le port et une particularité du fichier du 16 février. Les deux fichiers disponibles comptent par ailleurs exactement $1\,048\,575$ lignes de données, ce qui appelle une vérification de leur complétude. Seules deux journées sont disponibles localement : la transférabilité à d’autres journées reste non évaluée.

**Preuves** : `agent4_csecic_shortcut_20261104T144738Z__result.json` → `part2_summary` (toutes les cellules du tableau ; `rule_dst_port_lt_1024` 0,999728 et 0,121517 ; FPR 0,9940) ; `part2_dst_port_by_family_sample` (76,01 %) ; `part1_top_importances` (`LogisticRegression|permutation_f1_test_balanced_4000`, Dst Port 0,5004) ; `part1_family_predicted_attack_rate` (`RandomForest`/`ALL`/`Hulk_port80` min 0,0895 max 0,9952 ; `SlowHTTPTest_port21` 0,0) ; `part2_audit.rows_scanned` (1 048 575 ; 1 048 574 + 1 en-tête répété).

### P-5.9 — `chapitre5_resultats.tex`, « Synthèse des résultats » (l. 418)
**Actuel** :
> HDFS rappelle de son côté que l’unité d’analyse doit correspondre à l’unité des labels, tandis que BGL montre pourquoi la proportion de templates inconnus doit accompagner le score global.

**Proposé** :
> HDFS rappelle de son côté que l’unité d’analyse doit correspondre à l’unité des labels. BGL montre que la proportion de templates inconnus doit accompagner le score global et que ce score varie fortement avec la proximité temporelle entre entraînement et test. CSE-CIC-IDS2018 montre qu’un score quasi parfait peut reposer sur une seule variable propre à la journée de test.

**Preuve** : P-5.4, P-5.8.

### P-6A.1 — `chapters/chapitre6_approfondissements_scientifiques.tex` (l. 18)
**Actuel** :
> Le cas de CSE-CIC-IDS2018 demande encore une autre lecture. La séparation par journée limite le mélange direct entre lignes d’entraînement et de test, mais le score obtenu avec \texttt{Dst Port} seul, ainsi que la chute observée après ablation, révèlent une dépendance importante à certaines caractéristiques. L’étude des coefficients, la permutation des labels et les retraits successifs ne mettent pas en évidence de fuite triviale parmi les mécanismes testés. Cela n’exclut toutefois pas l’existence d’un artefact lié aux journées sélectionnées ou au processus de génération du dataset.

**Proposé** :
> Le cas de CSE-CIC-IDS2018 demande encore une autre lecture. La séparation par journée limite le mélange direct entre lignes d’entraînement et de test, mais le score repose sur un raccourci propre au 16 février : une règle fixe sur le port de destination atteint le même F1 que la régression logistique et échoue sur le 15 février (section~\ref{sec:csecic-raccourci}).

**Preuve** : P-5.8.

### P-6A.2 — `chapitre6_approfondissements_scientifiques.tex` (l. 31)
**Actuel** :
> BGL présente une autre particularité : $89{,}8081\,\%$ des unités de test utilisent un template absent de l’entraînement. Une modification de ce taux de nouveauté pourrait donc changer sensiblement les performances observées.

**Proposé** :
> BGL présente une autre particularité : $89{,}8081\,\%$ des événements de test utilisent un template absent de l’entraînement. Les protocoles complémentaires confirment que ce taux, et avec lui le F1, dépendent de la proximité temporelle entre entraînement et test (section~\ref{sec:bgl-second-protocole}).

**Preuve** : P-5.4.

### P-6A.3 — `chapitre6_approfondissements_scientifiques.tex` (l. 63)
**Actuel** :
> BGL présente une difficulté différente : aucun positif n’est présent dans le groupe des templates connus. Il est donc impossible d’y calculer un rappel d’anomalies connues.

**Proposé** :
> BGL présente une difficulté différente : le protocole principal ne contient aucun positif sur un template connu. Le protocole G en contient 2\,880, avec un rappel de $0{,}998264$, sous les réserves exposées en section~\ref{sec:bgl-second-protocole}.

**Preuve** : `agent4_bgl_contiguous_horizon_20261104T145740Z__group_metrics.csv` (`Histogram`/`KNOWN_TEMPLATE`).

### P-6A.4 — `chapitre6_approfondissements_scientifiques.tex`, tableau (l. 94)
**Actuel** :
> Nouveauté lexicale BGL & Groupes connu/inconnu et baseline & Aucun positif dans le groupe connu. \\

**Proposé** :
> Nouveauté BGL & Groupes connu/inconnu, baselines template et sévérité, protocole G & Protocole G conçu après inspection ; F1 dépendant du découpage. \\

**Preuve** : P-5.3, P-5.4.

### P-6D.1 — `chapters/chapitre6_discussion.tex` (l. 67)
**Actuel** :
> L’absence de positifs parmi les templates BGL connus interdit certaines conclusions sur le rappel.

**Proposé** :
> Sur BGL, le F1 du protocole principal se réduit à une règle de nouveauté de sévérité, et la mesure du rappel sur templates connus exige un autre découpage temporel.

**Preuve** : P-5.3, P-5.4.

### P-6C.1 — `chapters/chapitre6_conclusion.tex` (l. 11)
**Actuel** :
> Sur BGL, le F1 de $0{,}913698$ doit être interprété avec le taux élevé de templates inconnus, soit $89{,}8081\,\%$, et avec le baseline de nouveauté qui obtient $0{,}277885$.

**Proposé** :
> Sur BGL, le F1 de $0{,}913698$ doit être interprété avec le taux élevé d’événements à template inconnu, soit $89{,}8081\,\%$ : la décision y coïncide avec une règle de nouveauté de sévérité. Un entraînement contigu au test porte ce taux à $0{,}9293\,\%$ et donne un F1 de $0{,}941927$, dont $0{,}965413$ sur les templates connus.

**Preuve** : P-5.3 ; `agent4_bgl_contiguous_horizon_20261104T145740Z__result.json`.

### P-6C.2 — `chapitre6_conclusion.tex` (l. 101)
**Actuel** :
> Pour BGL, aucun exemple positif n'est présent parmi les templates connus, ce qui empêche d'y mesurer le rappel.

**Proposé** :
> Pour BGL, la mesure sur templates connus repose sur un protocole conçu après inspection du journal (section~\ref{sec:bgl-second-protocole}).

**Preuve** : P-5.4.

### P-6C.3 — `chapitre6_conclusion.tex` (l. 112)
**Actuel** :
> Pour BGL, un protocole contenant des anomalies parmi les templates déjà connus serait nécessaire pour mesurer ce cas aujourd'hui absent du test.

**Proposé** :
> Pour BGL, il conviendrait de répéter le protocole G sur plusieurs plages de test fixées à l'avance, afin d'obtenir une estimation indépendante du rappel sur templates connus.

**Preuve** : P-5.4.

### P-6C.4 — `chapitre6_conclusion.tex` (l. 99)
**Actuel** :
> Sur CSE-CIC-IDS2018, quelques caractéristiques jouent un rôle particulièrement important dans la séparation observée.

**Proposé** :
> Sur CSE-CIC-IDS2018, la séparation observée repose sur un raccourci par le port de destination propre à la journée de test (section~\ref{sec:csecic-raccourci}).

**Preuve** : P-5.8.

### P-6C.5 — `chapitre6_conclusion.tex` (l. 114)
**Actuel** :
> CSE-CIC-IDS2018 mérite également une validation sur d'autres journées. Les expériences actuelles montrent qu'une petite partie des caractéristiques porte une fraction importante de la séparation. Tester d'autres périodes et réduire la dépendance aux variables fortement liées au scénario permettrait de mieux apprécier la transférabilité du modèle.

**Proposé** :
> CSE-CIC-IDS2018 mérite également une validation sur d'autres journées, qui n'étaient pas disponibles localement. Le premier contrôle consisterait à mesurer, pour chaque journée, la part des flux bénins dirigés vers des ports inférieurs à 1024, puis à évaluer des modèles privés de \texttt{Dst Port} ou utilisant une catégorie de service plutôt que le numéro de port.

**Preuve** : section C de ces notes ; P-5.8.

### P-AN.1 — `chapters/annexes.tex`, tableau d'index (après l. 66) : lignes à ajouter
**Actuel** :
> Ablation CSE-CIC & top 10 retirées : 0,657859 & \texttt{external\_csecicids2018\_feature\_ablation.csv} \\

**Proposé** (conserver la ligne et ajouter à sa suite) :
> Ablation CSE-CIC & top 10 retirées : 0,657859 & \texttt{external\_csecicids2018\_feature\_ablation.csv} \\
> BGL baseline sévérité & F1 0,913698 & \texttt{agent4\_bgl\_second\_protocol\_20261104T142629Z\_\_group\_metrics.csv} \\
> BGL protocole G & F1 0,941927 ; connus 0,965413 & \texttt{agent4\_bgl\_contiguous\_horizon\_20261104T145740Z\_\_result.json} \\
> CSE-CIC prévalence observée & LR 0,994345 ; RF 0,095915 & \texttt{agent4\_csecic\_shortcut\_20261104T144738Z\_\_result.json} \\
> CSE-CIC règle port $<1024$ & F1 0,999720 & Même artefact, \texttt{part1\_summary}. \\

**Preuve** : artefacts cités.

### P-AN.2 — `annexes.tex` (l. 156)
**Actuel** :
> Le F1 BGL ne fournit aucun rappel pour les anomalies à template connu. Le score CSE-CIC-IDS2018 dépend fortement de certaines caractéristiques.

**Proposé** :
> Les limites BGL et CSE-CIC-IDS2018 sont exposées aux sections~\ref{sec:bgl-second-protocole} et~\ref{sec:csecic-raccourci}.

**Preuve** : P-5.4, P-5.8.

### P-AN.3 — `annexes.tex` (l. 189 et 192)
**Actuel (l. 189)** :
> Le groupe \texttt{KNOWN\_TEMPLATE} contient $2\,029$ unités et aucune anomalie ; aucun rappel d’anomalies connues ne peut donc y être estimé. Le F1 global est porté par le groupe des templates inconnus, ce qui limite son interprétation comme apprentissage de comportement.

**Proposé** :
> Le groupe \texttt{KNOWN\_TEMPLATE} contient $2\,029$ événements et aucune anomalie dans ce protocole. Le F1 global est porté par le groupe des templates inconnus. Le rappel sur templates connus est mesuré par le protocole G (section~\ref{sec:bgl-second-protocole}).

**Actuel (l. 192)** :
> Le gain de F1, de 0,277885 à 0,913698, indique que le seuil Histogram filtre une grande partie des nouveautés normales. La comparaison ne résout pas l’absence de positifs parmi les templates connus et ne permet donc pas d’estimer ce rappel.

**Proposé** :
> Le gain de F1, de 0,277885 à 0,913698, vient du seuil, égal au score maximal : seuls les événements dont le template, la source et la sévérité sont tous absents du train sont retenus. Le résultat coïncide avec une règle de nouveauté de sévérité.

**Preuve** : P-5.3.

### P-AN.4 — `annexes.tex` (l. 201)
**Actuel** :
> Le F1 de 0,999720 obtenu avec \texttt{Dst Port} révèle qu’une seule variable porte presque toute la séparation dans ce split. Le graphique sert de diagnostic de dépendance et non de preuve de fuite.

**Proposé** :
> Le F1 de 0,999720 obtenu avec \texttt{Dst Port} est égal à celui d’une règle fixe « port inférieur à 1024 ». Il traduit un raccourci propre au 16 février, non une fuite de label (section~\ref{sec:csecic-raccourci}).

**Preuve** : P-5.6.

### P-M1 à P-M4 — `main.tex`, résumés français et anglais
**P-M1, actuel (l. 327-329)** :
> Sur BGL, le F1 vaut $0{,}913698$,
> mais 89,8081\,% des templates de test sont inconnus du train et la
> baseline « template inconnu » n'atteint que $0{,}277885$.

**Proposé** :
> Sur BGL, le F1 vaut $0{,}913698$,
> mais 89,8081\,\% des événements de test portent un template inconnu du train et la
> décision coïncide avec une règle de nouveauté de sévérité ; un entraînement
> contigu au test donne $0{,}941927$, dont $0{,}965413$ sur les templates connus.

Note : l'original écrit `89,8081\,%` sans échappement ; en LaTeX, ce `%` ouvre un commentaire et supprime la fin de la ligne. **À corriger** dans tous les cas : `\%`.

**P-M2, actuel (l. 333-336)** :
> L’audit montre cependant que
> \texttt{Dst Port} seul atteint $0{,}999720$ et que le retrait des dix
> premières caractéristiques ramène le F1 à $0{,}657859$. Le score principal
> est donc présenté comme fortement dépendant des variables et du scénario.

**Proposé** :
> L’audit montre cependant que
> \texttt{Dst Port} seul atteint $0{,}999720$, comme une règle fixe « port
> inférieur à 1024 » : ce raccourci, propre au 16 février, échoue sur le
> 15 février, et le Random Forest, qui ne l’extrapole pas, chute à $0{,}095915$
> à la prévalence observée.

**P-M3, actuel (l. 446-448)** :
> On BGL, F1 is $0.913698$, but 89.8081\%
> of test templates are unknown to training and the ``unknown template''
> baseline reaches only $0.277885$.

**Proposé** :
> On BGL, F1 is $0.913698$, but 89.8081\%
> of test events carry a template unknown to training and the decision
> coincides with a severity-novelty rule; a training window contiguous to the
> test yields $0.941927$, and $0.965413$ on known templates.

**P-M4, actuel (l. 452-455)** :
> However, \texttt{Dst Port} alone reaches $0.999720$, while
> removing the ten leading features reduces F1 to $0.657859$. The primary
> score is therefore reported as strongly dependent on the features and
> scenario.

**Proposé** :
> However, \texttt{Dst Port} alone reaches $0.999720$, as does a fixed
> ``port below 1024'' rule: this shortcut is specific to February 16 and fails
> on February 15, and Random Forest, which does not extrapolate it, drops to
> $0.095915$ at the observed prevalence.

**Résumé lingala (l. 559-575)** : mêmes corrections à apporter par l'auteur (voir blocages).

**Preuves** : P-5.3, P-5.4, P-5.8.
