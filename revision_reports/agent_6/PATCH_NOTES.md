# PATCH_NOTES — Agent 6 : état de l'art, bibliographie, baselines publiées, détection non supervisée

## En-tête : effort d'intégration et blocages

**Effort estimé d'intégration : 3 à 4 heures** (copie de 11 entrées BibTeX : 10 min ; 17 modifications de texte dont 3 nouvelles sous-sections et 3 nouveaux tableaux : 2 h 30 ; recompilation `pdflatex → bibtex → pdflatex ×2` et contrôle des débordements de tableaux : 45 min). Aucune dépendance logicielle nouvelle : `url`, `hyperref`, `booktabs` et `tabularx` sont déjà chargés dans `main.tex`.

**Blocages et réserves (aucun bloquant) :**
1. `fipa.org` refuse les requêtes automatiques (HTTP 403). La spécification SC00029H a été vérifiée sur un miroir universitaire (compilation officielle FIPA, PDF lu p. 28–30). SC00061G et SC00037J sont vérifiées par titre, numéro, statut et date uniquement.
2. Crossref a renvoyé HTTP 429 pour Landauer et al. (2023) et Yu et al. (2024) ; ces références sont confirmées par d'autres sources (DOI résolu, ACM DL, arXiv). La pagination de Yu et al. (« art. 35 ») est à recontrôler.
3. **CSE-CIC-IDS2018 n'a pas d'article propre** : la page officielle de l'UNB demande de citer Sharafaldin et al. (ICISSP 2018), c'est-à-dire l'article déjà cité pour CICIDS2017. La consigne « vérifie la référence correcte pour IDS2018 » se résout donc ainsi : citer `sharafaldin2018cicids` **et** la page de distribution `cic2018csecicids`.
4. Prénom de Smith (1980) : « Reid G. » d'après IEEE Xplore ; Crossref n'a pas été lisible sur ce point.
5. Deux expériences contredisent ou nuancent le texte actuel (règle 2) : (a) l'unité d'analyse BGL est l'**événement**, non la fenêtre (patchs P14 et P15) ; (b) sur BGL, le F1 de validation de Histogram (0,733460) est très inférieur au F1 de test (0,913698), et le FPR passe de 0,612783 à 0,032016 (patch P13).
6. L'expérience HDFS lourde en cours n'a pas été touchée. Mes calculs : Isolation Forest sur ≈ 120 000 lignes, `n_jobs=2`, environ 1 min ; une agrégation en lecture seule de fichiers JSON existants.

**Fichiers produits (tous dans `revision_reports/agent_6/`) :**
- `references_proposees.bib` — 11 entrées vérifiées, à ajouter à `ARIEL_LOGMINER_MEMOIRE_FINAL/references.bib` (aucune collision de clé).
- `verification_references.md` — tableau de vérification, avec la source de chaque référence.
- `scripts/run_cicids_isolation_forest_temporal.py` → run `agent6_cicids_iforest_20261104T141904Z` (`artifacts/…_metrics.csv`, `…_summary.csv`, `…_per_source.csv`, `…_manifest.json`, `iforest_run_stdout.txt`, `iforest_results_dump.txt`).
- `scripts/aggregate_strict_e3_unsupervised.py` → run `agent6_strict_e3_aggregate_20261104T143019Z` (`artifacts/…_per_run.csv`, `…_summary.csv`), qui agrège en lecture seule les runs `e3_strict_*` existants.
- `artifacts/published_baselines_hdfs_bgl.csv` — chiffres publiés, avec leur protocole et leur provenance exacte.

---

## Résultats établis (preuves)

### R1 — Isolation Forest non supervisé sur CICIDS2017, protocole temporel (tâche C)

Run `agent6_cicids_iforest_20261104T141904Z`, fichier `revision_reports/agent_6/artifacts/agent6_cicids_iforest_20261104T141904Z_summary.csv`.
- Données : pools figés du run existant `cicids_temporal_20260910T083015Z` (`experiments/phase_dataset_strengthening/processed/…_train_pool.csv.gz`, SHA-256 `d4c9a135…`, et `…_test_pool.csv.gz`, SHA-256 `fbc94c1b…`), 78 caractéristiques.
- Ajustement : 10 000 flux BENIGN de lundi à jeudi, sans aucun label d'attaque. Validation sur lundi–jeudi, disjointe de l'ajustement : 5 000 BENIGN et 5 000 attaques. Test : vendredi, tiré par la même fonction `seed_sample` et les mêmes graines que la campagne LR/RF. Les tests sont donc identiques par construction (même pool, même fonction, même `random_state`).
- Modèle : `IsolationForest(n_estimators=200, max_samples=256)`, graines 42 à 46.
- Deux règles de seuil, toutes deux fixées sur validation :
  - `benign_q99` : quantile 99 % des scores BENIGN de validation. Cette règle n'utilise que des données normales.
  - `val_maxf1` : seuil maximisant le F1 de validation. Cette calibration est semi-supervisée, car elle utilise les attaques de lundi à jeudi.

| Modèle (même test vendredi, 10 000 + 10 000) | Seuil | F1 moyen (σ) | Rappel | FPR | MCC | PR-AUC | ROC-AUC |
|---|---|---|---|---|---|---|---|
| Isolation Forest (non supervisé) | `benign_q99` | 0,115719 (0,011881) | 0,063500 | 0,033440 | 0,069723 | 0,571803 | 0,639037 |
| Isolation Forest (non supervisé) | `val_maxf1` | 0,521436 (0,170794) | 0,519480 | 0,312340 | 0,257523 | 0,571803 | 0,639037 |
| Régression logistique (supervisée), run `cicids_temporal_20260910T083015Z` | défaut | 0,556615 (0,017124) | 0,400960 | 0,039360 | 0,436298 | 0,871448 | — |
| Random Forest (supervisé), même run | défaut | 0,437429 (0,004046) | 0,280620 | 0,002400 | 0,399112 | 0,830759 | — |
| Référence triviale « tout attaque » (prévalence 0,5) | — | 0,666667 | 1 | 1 | 0 | 0,5 | 0,5 |

Lecture :
- Le classement d'Isolation Forest reste faible : ROC-AUC 0,639 et PR-AUC 0,572, pour une référence de 0,5.
- Avec un seuil appris sur le normal seul, le FPR visé de 1 % devient 3,3 % le vendredi, et 6,4 % seulement des attaques sont détectées. Les rappels par fichier valent 0,000255 pour PortScan, 0,1437 pour DDoS et 0,0086 pour Bot (`…_per_source.csv`).
- La règle `val_maxf1` est instable : le FPR de validation varie de 0,0698 à 0,7026 selon la graine (`…_metrics.csv`). Les F1 obtenus restent sous la référence triviale « tout attaque », qui vaut 0,667 sur un test équilibré.
- **Conclusion :** sur CICIDS2017, le détecteur non supervisé ne remplace pas la classification supervisée. L'évaluation réseau du mémoire relève donc bien, pour l'essentiel, de la classification supervisée.

### R2 — Détecteurs non supervisés stricts déjà présents dans le dépôt, mais non rapportés

Run `agent6_strict_e3_aggregate_20261104T143019Z`, agrégation en lecture seule de `data/processed/final_experiments_2026/phase_3/e3_strict_*.json`, fichier `revision_reports/agent_6/artifacts/agent6_strict_e3_aggregate_20261104T143019Z_summary.csv`.
- HDFS, niveau événement (prévalence de test 0,0059) : Isolation Forest F1 moyen 0,204530 (σ 0,004496, 5 graines) ; Histogram 0,269307 (graine 42, valeur « historique » déjà mentionnée) ; AutoencoderMLP 0,214286.
- BGL, niveau événement (prévalence de test 0,144917) : Isolation Forest F1 moyen 0,253473, FPR 0,998285, soit le niveau de la référence « tout positif » (0,253148) ; Histogram 0,913698.
- La sélection d'Histogram n'est pas pilotée par le test : c'est aussi le meilleur F1 de validation (0,733460 contre 0,627781 à 0,701985 pour les autres méthodes).

### R3 — Nature de l'apprentissage par campagne (preuve des artefacts)

| Campagne | Score | Labels utilisés | Qualification exacte |
|---|---|---|---|
| CICIDS2017 (aléatoire, holdout scénario, temporel), CSE-CIC-IDS2018 | LR, RF, ET, HGB, SGD | train étiqueté | **classification supervisée binaire** |
| HDFS bloc (`ds_hdfs_block_20260910T081756Z`) | rareté Histogram appris sur l'entraînement (194 blocs positifs sur 6 000 présents mais non utilisés comme labels pour le score) | agrégateur et seuil choisis sur la validation étiquetée | **score non supervisé, calibration semi-supervisée** |
| BGL (`ds_bgl_known_unknown_20260910T082706Z` ; `bgl_preparation.json`) | Histogram appris sur 49 999 événements d'entraînement **sans aucun positif** | seuil choisi sur la validation étiquetée | **détection de nouveauté (normal seul), calibration semi-supervisée** |
| CICIDS2017 Isolation Forest (R1) | IF appris sur le BENIGN seul | aucun (`benign_q99`) ou validation (`val_maxf1`) | **non supervisé / semi-supervisé** |

### R4 — Baselines publiées sur HDFS et BGL (tâche B)

Chiffres relevés directement dans les PDF (voir `artifacts/published_baselines_hdfs_bgl.csv`) :

| Source | Jeu | Méthode | Cadre | Unité | Partition | F1 publié |
|---|---|---|---|---|---|---|
| Du et al. 2017 (texte §5.1.3, tab. 3–4) | HDFS | DeepLog | semi-supervisé (normal seul) | session `block_id` | 4 855 sessions normales issues des 100 000 premières lignes ; test 553 366 normales / 15 200 anormales | 0,96 |
| Guo et al. 2021 (tab. 2) | HDFS | LogBERT / DeepLog / iForest | auto-supervisé / semi-supervisé / non supervisé | session `block_id` | ≈ 5 000 séquences normales en entraînement ; test 553 366 / 10 647 | 0,8232 / 0,7734 / 0,6049 |
| Guo et al. 2021 (tab. 2) | BGL | LogBERT / DeepLog / iForest | idem | fenêtre glissante de 5 min | test 10 045 / 2 630 | 0,9083 / 0,8612 / 0,3065 |
| Le & Zhang 2022 (tab. 4) | HDFS | DeepLog / PLELog / LogRobust / CNN | semi-sup. / semi-sup. / sup. / sup. | session `block_id` | aléatoire 80:20 (460 048 / 115 013) | 0,908 / 0,934 / 0,980 / 0,982 |
| Le & Zhang 2022 (tab. 2) | BGL | DeepLog | semi-supervisé | fenêtre fixe de 1 h | aléatoire → chronologique | 0,927 → 0,426 |
| Le & Zhang 2022 (tab. 2) | BGL | LogRobust | supervisé | fenêtre fixe de 1 h | aléatoire → chronologique | 0,981 → 0,967 |
| **Mémoire** `ds_hdfs_block_20260910T081756Z` | HDFS | Histogram + moyenne par bloc | score non supervisé, seuil sur validation | bloc | chronologique 60/20/20, échantillon 6 000/2 000/2 000, 29 positifs en test | **0,892308** |
| **Mémoire** même run | HDFS | Histogram | idem | événement | idem | 0,213115 |
| **Mémoire** `ds_bgl_known_unknown_20260910T082706Z` | BGL | Histogram | nouveauté (normal seul), seuil sur validation | événement | trois blocs chronologiques (juillet / septembre / novembre 2005) | **0,913698** |

Les protocoles diffèrent par l'unité, le fenêtrage, la taille et la prévalence du test, ainsi que par le caractère aléatoire ou chronologique de la partition. Ils ne permettent **aucun classement direct**. Le constat le plus robuste est celui de Le & Zhang : la partition chronologique fait chuter le F1 de DeepLog sur BGL de 0,927 à 0,426. Ce constat va dans le même sens que celui du mémoire sur CICIDS2017.

---

## Modifications de texte proposées

Convention : le « texte actuel » est cité **exactement**, retours à la ligne compris lorsque le source est coupé en dur.

### P1 — `chapters/chapitre1_introduction.tex`, section « Positionnement et définition opérationnelle des termes » (l. 80)

**Texte actuel :**
```
Un agent est dit \textbf{multitâche} lorsqu'il peut traiter plusieurs catégories de tâches à travers différents handlers compatibles. La négociation s'appuie sur un protocole Contract Net qui rend explicites les principales étapes de décision : CFP, PROPOSE ou REFUSE, AWARD ou REJECT, ACCEPT, RESULT ou FAIL, puis FEEDBACK.
```
**Texte proposé :**
```
Un agent est dit \textbf{multitâche} lorsqu'il peut traiter plusieurs catégories de tâches à travers différents handlers compatibles. La négociation s'appuie sur le protocole Contract Net \cite{smith1980contract}, dans une variante inspirée de la spécification FIPA \cite{fipa2002contractnet}, qui rend explicites les principales étapes de décision : CFP, PROPOSE ou REFUSE, AWARD ou REJECT, ACCEPT, RESULT ou FAIL, puis FEEDBACK.
```
**Preuve :** Smith 1980 et SC00029H (voir `verification_references.md`). Aucune citation ne couvre aujourd'hui « Contract Net » dans le mémoire (recherche `\cite` dans `chapters/*.tex` : aucune occurrence).

### P2 — `chapitre1_introduction.tex`, « Démarche méthodologique » (l. 205)

**Texte actuel :**
```
Les données proviennent de plusieurs catégories qu'il est nécessaire de distinguer. Parmi les \textbf{jeux de données publics}, CICIDS2017 fournit des flux réseau comportant du trafic bénin et différents scénarios d'attaque dans un environnement contrôlé \cite{sharafaldin2018cicids}. HDFS est largement utilisé pour l'étude des anomalies dans les journaux de systèmes distribués \cite{xu2009hdfs}, tandis que BGL provient des journaux du supercalculateur Blue Gene/L \cite{oliner2007bgl}. Leur diffusion et leur emploi pour l'analyse automatisée de journaux sont également documentés dans Loghub \cite{zhu2023loghub}.
```
**Texte proposé :**
```
Les données proviennent de plusieurs catégories qu'il est nécessaire de distinguer. Parmi les \textbf{jeux de données publics}, CICIDS2017 fournit des flux réseau comportant du trafic bénin et différents scénarios d'attaque dans un environnement contrôlé \cite{sharafaldin2018cicids}. CSE-CIC-IDS2018, produit par la même équipe selon une méthodologie comparable, sert de jeu externe \cite{sharafaldin2018cicids,cic2018csecicids}. HDFS est largement utilisé pour l'étude des anomalies dans les journaux de systèmes distribués \cite{xu2009hdfs}, tandis que BGL provient des journaux du supercalculateur Blue Gene/L \cite{oliner2007bgl}. Leur diffusion et leur emploi pour l'analyse automatisée de journaux sont également documentés dans Loghub \cite{zhu2023loghub}.
```
**Preuve :** CSE-CIC-IDS2018 est utilisé au chapitre 5 (run `external_csecicids2018_20260910T230136Z`), mais n'est ni présenté ni cité au chapitre 1. La page UNB IDS2018 demande de citer Sharafaldin et al. 2018.

### P3 — `chapitre1_introduction.tex`, « Démarche méthodologique » (l. 209) — tâche C

**Texte actuel :**
```
Les expériences de détection suivent plusieurs protocoles. Pour CICIDS2017, l'étude compare notamment une séparation aléatoire stratifiée à des holdouts par scénario, sur plusieurs graines.
```
**Texte proposé :**
```
Les expériences de détection suivent plusieurs protocoles et ne relèvent pas toutes du même cadre d'apprentissage. Sur les flux réseau (CICIDS2017 et CSE-CIC-IDS2018), l'évaluation porte principalement sur une \textbf{classification supervisée binaire}, entraînée sur des exemples étiquetés des deux classes ; un détecteur non supervisé, appris sur le seul trafic bénin, est évalué à titre de contrôle. Pour CICIDS2017, l'étude compare notamment une séparation aléatoire stratifiée à des holdouts par scénario, sur plusieurs graines.
```
**Preuve :** R3 ; scripts `scripts/run_cicids_temporal_strengthening.py` (`RandomForestClassifier`, `LogisticRegression` entraînés sur `target`) ; R1.

### P4 — `chapitre1_introduction.tex`, « Démarche méthodologique » (l. 211) — tâche C

**Texte actuel :**
```
HDFS et BGL sont traités différemment. Entraînement, validation et test sont séparés explicitement.
```
**Texte proposé :**
```
HDFS et BGL sont traités différemment, dans un cadre de détection d'anomalies : le score de rareté est appris sans utiliser les labels (pour BGL, l'entraînement ne contient d'ailleurs aucun événement anormal), tandis que le seuil est fixé sur une validation étiquetée. Il s'agit donc d'une détection non supervisée à calibration semi-supervisée. Entraînement, validation et test sont séparés explicitement.
```
**Preuve :** `data/processed/final_experiments_2026/phase_3/prepared/bgl_preparation.json` (`splits.train.positives = 0`) ; `ds_bgl_known_unknown_20260910T082706Z__bgl_known_unknown_result.json` (`threshold_selected_on: validation_only`) ; `ds_hdfs_block_20260910T081756Z__hdfs_block_result.json` (`event_score: histogram_template_source_severity_rarity`, `selection_partition: validation_only`).

### P5 — `chapitre1_introduction.tex`, « Délimitations et portée du mémoire » (l. 257)

**Texte actuel :**
```
Le choix de modèles relativement légers répond enfin au périmètre local de l'étude. Les architectures profondes spécialisées dans l'analyse séquentielle des journaux sont prises en compte dans l'état de l'art, mais leur comparaison exhaustive avec toutes les méthodes intégrées au prototype n'est pas l'objet principal du mémoire.
```
**Texte proposé :**
```
Le choix de modèles relativement légers répond enfin au périmètre local de l'étude. Les architectures profondes spécialisées dans l'analyse séquentielle des journaux sont prises en compte dans l'état de l'art, mais leur comparaison exhaustive avec toutes les méthodes intégrées au prototype n'est pas l'objet principal du mémoire ; les scores publiés sont rappelés au chapitre des résultats avec leur protocole, sans être réputés directement comparables. De même, la détection d'intrusion réseau est évaluée pour l'essentiel comme une classification supervisée : la capacité à détecter des attaques sans exemple étiqueté n'est mesurée que par un contrôle limité, dont le résultat est défavorable.
```
**Preuve :** R1, R4.

### P6 — `chapters/chapitre2_etat_art.tex`, section « Systèmes multi-agents », « Concept général » (l. 532–534)

**Texte actuel :**
```
Un système multi-agent décompose un problème entre plusieurs entités capables d'exécuter
des tâches et de communiquer. Dans sa forme la plus générale, un agent peut posséder un
état, des objectifs, des capacités et un mécanisme de décision.
```
**Texte proposé :**
```
Un système multi-agent décompose un problème entre plusieurs entités capables d'exécuter
des tâches et de communiquer. Dans sa forme la plus générale, un agent peut posséder un
état, des objectifs, des capacités et un mécanisme de décision. Wooldridge caractérise
l'agent par son autonomie, sa réactivité, sa proactivité et sa capacité sociale, et
distingue ces propriétés de la simple distribution d'un calcul \cite{wooldridge2009introduction}.
La définition opérationnelle retenue dans ce mémoire n'en reprend qu'une partie, bornée et
vérifiable dans le code.
```
**Preuve :** Wooldridge 2009 (2ᵉ éd.), ISBN vérifié. *Remarque à l'auteur :* les quatre propriétés (autonomie, réactivité, proactivité, capacité sociale) constituent la caractérisation classique de Wooldridge et Jennings, reprise dans l'ouvrage. Contrôler le numéro de chapitre dans l'exemplaire consulté avant d'ajouter une page précise.

### P7 — `chapitre2_etat_art.tex`, nouvelle sous-section à insérer **avant** `\subsection{Intérêt architectural}` (l. 550)

**Texte actuel (ancre) :**
```
\subsection{Intérêt architectural}
```
**Texte proposé (insertion avant l'ancre, ancre conservée) :**
```
\subsection{Protocole Contract Net et standards FIPA}

Le protocole Contract Net, proposé par Smith, organise l'allocation de tâches dans un
système distribué sous la forme d'une négociation : un gestionnaire annonce une tâche,
des contractants potentiels soumettent des offres, puis le gestionnaire attribue la tâche
à l'offre jugée la meilleure \cite{smith1980contract}. L'intérêt du mécanisme tient à ce que
la décision d'allocation s'appuie sur une information détenue localement par les agents,
sans exiger une connaissance centrale de leur état.

La FIPA a normalisé une version de ce protocole \cite{fipa2002contractnet}. L'initiateur
émet un \texttt{cfp} ; chaque participant répond par \texttt{propose} ou \texttt{refuse}
avant une date limite portée par le paramètre \texttt{reply-by} ; l'initiateur envoie
ensuite \texttt{accept-proposal} ou \texttt{reject-proposal}, et le participant retenu
conclut par \texttt{inform-done}, \texttt{inform-result} ou \texttt{failure}. Chaque échange
porte un identifiant de conversation unique. Ces actes et la structure des messages sont
définis par les spécifications FIPA ACL \cite{fipa2002aclmessage,fipa2002cal}.

Le protocole d'Ariel Logminer reprend cette structure sous une nomenclature propre :
\texttt{CFP} correspond à \texttt{cfp}, \texttt{PROPOSE}/\texttt{REFUSE} à
\texttt{propose}/\texttt{refuse}, \texttt{AWARD}/\texttt{REJECT} à
\texttt{accept-proposal}/\texttt{reject-proposal}, et \texttt{RESULT}/\texttt{FAIL} à
\texttt{inform-result}/\texttt{failure}. Les messages \texttt{ACCEPT} (confirmation de
l'attribution par l'agent) et \texttt{FEEDBACK} (retour utilisé par la mémoire) n'existent
pas dans la spécification FIPA : ce sont des extensions. Le prototype ne revendique donc
pas la conformité FIPA, mais une parenté de protocole explicitement documentée.

```
**Preuve :** SC00029H, figure 1 et §1.1 (PDF lu) ; nomenclature du prototype en `chapitre3_modele_propose.tex` l. 437–439 et `chapitre6_discussion.tex` l. 23. *À vérifier par l'auteur dans le code :* que `ACCEPT` est bien une confirmation émise par l'agent et `FEEDBACK` un retour vers la mémoire. Corriger les deux parenthèses si la sémantique diffère.

### P8 — `chapters/chapitre3_modele_propose.tex`, « Architecture multi-agents » (l. 433–440)

**Texte actuel :**
```
Le cycle de négociation est :

\begin{center}

\textit{CFP} $\rightarrow$ \textit{PROPOSE/REFUSE}
$\rightarrow$ \textit{AWARD/REJECT} $\rightarrow$ \textit{ACCEPT}
$\rightarrow$ \textit{RESULT/FAIL} $\rightarrow$ \textit{FEEDBACK}.
\end{center}
```
**Texte proposé :**
```
Le cycle de négociation, dérivé du Contract Net \cite{smith1980contract} et de sa
spécification FIPA \cite{fipa2002contractnet} (correspondance détaillée au
chapitre~\ref{chap:etat-art}), est :

\begin{center}

\textit{CFP} $\rightarrow$ \textit{PROPOSE/REFUSE}
$\rightarrow$ \textit{AWARD/REJECT} $\rightarrow$ \textit{ACCEPT}
$\rightarrow$ \textit{RESULT/FAIL} $\rightarrow$ \textit{FEEDBACK}.
\end{center}
```
**Preuve :** idem P7 ; le label `chap:etat-art` existe (`chapitre2_etat_art.tex` l. 3).

### P9 — `chapitre2_etat_art.tex`, « Rôle des datasets publics » (l. 309–312)

**Texte actuel :**
```
Sommer et Paxson mettent en garde contre l'application naïve de méthodes de machine
learning issues d'un environnement expérimental à des réseaux réels
\cite{sommer2010outside}. Cette remarque reste centrale : la qualité d'un modèle dépend
autant du protocole d'évaluation que de l'algorithme.
```
**Texte proposé :**
```
Sommer et Paxson mettent en garde contre l'application naïve de méthodes de machine
learning issues d'un environnement expérimental à des réseaux réels
\cite{sommer2010outside}. Arp et al. ont depuis recensé dix écueils récurrents dans
les travaux d'apprentissage automatique appliqué à la sécurité, parmi lesquels le biais
d'échantillonnage, la fuite d'information entre entraînement et test et le choix de
métriques inadaptées \cite{arp2022dos}. Ces remarques restent centrales : la qualité d'un
modèle dépend autant du protocole d'évaluation que de l'algorithme.
```
**Preuve :** Arp et al., USENIX Security 2022 (dix écueils, d'après le résumé vérifié). *À contrôler par l'auteur :* l'appellation exacte des trois écueils cités dans le texte de l'article (« sampling bias », « data snooping », « inappropriate performance measures »).

### P10 — `chapitre2_etat_art.tex`, nouvelle sous-section après la sous-section CICIDS2017, **avant** `\subsection{HDFS}` (l. 335)

**Texte actuel (fin de la sous-section CICIDS2017, l. 333, puis ancre) :**
```
mesurées~\cite{engelen2021troubleshooting,lanvin2023errors}. La chute du F1 observée ici entre séparation aléatoire et séparation par scénario (section~6.2) est donc cohérente avec ces constats indépendants portant sur le même corpus.

\subsection{HDFS}
```
**Texte proposé :**
```
mesurées~\cite{engelen2021troubleshooting,lanvin2023errors}. La chute du F1 observée ici entre séparation aléatoire et séparation par scénario (section~6.2) est donc cohérente avec ces constats indépendants portant sur le même corpus.

\subsection{CSE-CIC-IDS2018}

CSE-CIC-IDS2018 est un jeu de flux réseau produit par le Canadian Institute for
Cybersecurity et le Communications Security Establishment, diffusé sur une infrastructure
infonuagique publique. Ses auteurs demandent de le citer par la même publication
méthodologique que CICIDS2017 \cite{sharafaldin2018cicids,cic2018csecicids}. Il partage
donc l'outil d'extraction des caractéristiques et une partie des choix de construction de
CICIDS2017, ce qui limite sa valeur de jeu véritablement indépendant : il permet surtout
d'éprouver le transfert entre journées de capture, et non entre environnements de
production.

\subsection{HDFS}
```
**Preuve :** page UNB IDS2018 (lue). La caractéristique « même outil d'extraction » découle de la référence commune exigée et des 78 caractéristiques communes aux deux protocoles (`configs/dataset_strengthening_protocol.json` : 78 pour CICIDS ; `chapitre7…` l. 52 : 78 pour CSE-CIC). *Attention :* vérifier, avant intégration, que la section citée « section~6.2 » existe toujours sous ce numéro (référence en dur dans le texte actuel ; mieux vaut un `\ref`).

### P11 — `chapitre2_etat_art.tex`, sous-section « Loghub » (l. 362–364)

**Texte actuel :**
```
Loghub rassemble plusieurs datasets de journaux largement utilisés dans la recherche
\cite{zhu2023loghub}. Cette collection facilite la comparaison d'approches de parsing et
de détection sur des sources hétérogènes.
```
**Texte proposé :**
```
Loghub rassemble plusieurs datasets de journaux largement utilisés dans la recherche
\cite{zhu2023loghub}. Cette collection facilite la comparaison d'approches de parsing et
de détection sur des sources hétérogènes. Elle a servi de base à plusieurs évaluations
comparatives : He et al. comparent des détecteurs supervisés et non supervisés sur HDFS et
BGL \cite{he2016experience}, Le et Zhang réévaluent des modèles profonds en faisant varier
la sélection des données d'entraînement, le regroupement des événements et le déséquilibre
des classes \cite{le2022logbased}, et Landauer et al. proposent une synthèse des méthodes
d'apprentissage profond pour la détection d'anomalies dans les journaux \cite{landauer2023deep}.
```
**Preuve :** références vérifiées. Le contenu attribué à Le & Zhang reprend leurs RQ1 à RQ3 (PDF lu, p. 5).

### P12 — `chapitre2_etat_art.tex`, nouvelle sous-section après « LogBERT », **avant** `\section{Représentation sémantique et évolution récente de l'analyse de logs}` (l. 503)

**Texte actuel (fin de la sous-section LogBERT, l. 498–501, puis ancre) :**
```
Dans le contexte de \logminer{}, ces approches servent surtout à situer le prototype par
rapport aux méthodes spécialisées de l'état de l'art. Le travail privilégie des mécanismes
plus légers et s'intéresse davantage à l'intégration de plusieurs étapes qu'à la recherche
du meilleur modèle profond sur un benchmark unique.

\section{Représentation sémantique et évolution récente de l'analyse de logs}
```
**Texte proposé :**
```
Dans le contexte de \logminer{}, ces approches servent surtout à situer le prototype par
rapport aux méthodes spécialisées de l'état de l'art. Le travail privilégie des mécanismes
plus légers et s'intéresse davantage à l'intégration de plusieurs étapes qu'à la recherche
du meilleur modèle profond sur un benchmark unique.

\subsection{Sensibilité des benchmarks au protocole}

Les scores publiés sur HDFS et BGL dépendent fortement du protocole. Le et Zhang montrent
que, sur BGL regroupé en fenêtres d'une heure, le F1 de DeepLog passe de $0{,}927$ avec
une sélection aléatoire des séquences d'entraînement à $0{,}426$ avec une sélection
chronologique ; ils attribuent l'écart à une fuite d'information temporelle et recommandent
la partition chronologique \cite{le2022logbased}. Les mêmes auteurs observent que les
modèles supervisés surpassent nettement les modèles semi-supervisés lorsque des anomalies
étiquetées sont disponibles à l'entraînement. Yu et al. rapportent par ailleurs que des
méthodes d'apprentissage classiques peuvent égaler ou dépasser les modèles profonds, en
précision comme en temps de calcul, sur plusieurs jeux publics \cite{yu2024deep}. Ces
constats justifient de privilégier ici des partitions chronologiques ou par scénario et de
ne pas écarter a priori les modèles légers (H4).
```
**Preuve :** Le & Zhang 2022, tableau 2 et §4.1 (PDF lu) ; Yu et al. 2024 (résumé vérifié). *Réserve :* la formulation sur Yu et al. reprend le résumé (« simple classical methods can outperform deep learning methods in both accuracy and time efficiency ») ; ne pas ajouter de chiffre sans lecture de l'article.

### P13 — `chapters/chapitre5_resultats.tex`, section « BGL : templates connus et inconnus » (l. 167) — correction (règle 2)

**Texte actuel :**
```
Le détecteur Histogram est évalué sur $19\,908$ unités, dont $2\,885$ positives. Son seuil vaut $10{,}81975828421028$. Il produit $2\,885$ vrais positifs, 545 faux positifs, $16\,478$ vrais négatifs et aucun faux négatif, soit un F1 de $0{,}913698$. Toutefois, $17\,879$ unités, soit $89{,}8081\,\%$, portent un template inconnu.
```
**Texte proposé :**
```
Le détecteur Histogram est appris sur $49\,999$ événements d'entraînement ne contenant aucune anomalie étiquetée, puis évalué sur $19\,908$ événements de test, dont $2\,885$ positifs. Son seuil, choisi sur la validation, vaut $10{,}81975828421028$. Il produit $2\,885$ vrais positifs, 545 faux positifs, $16\,478$ vrais négatifs et aucun faux négatif, soit un F1 de $0{,}913698$. Ce score dépasse nettement celui de la validation ($0{,}733460$, avec un taux de faux positifs de $0{,}612783$ contre $0{,}032016$ en test) : les trois périodes, de juillet, septembre et novembre 2005, n'ont pas la même composition (prévalence de $0{,}457442$ en validation et de $0{,}144917$ en test). Toutefois, $17\,879$ événements, soit $89{,}8081\,\%$, portent un template inconnu.
```
**Preuve :** `experiments/phase_dataset_strengthening/raw/ds_bgl_known_unknown_20260910T082706Z__bgl_known_unknown_result.json` (`validation_metrics.f1 = 0.733459698528748`, `validation_metrics.fpr = 0.6127827350072629`, `prevalence` validation et test) ; `data/processed/final_experiments_2026/phase_3/prepared/bgl_preparation.json` (train de 49 999 lignes, 0 positif ; périodes et plages de lignes).

### P14 — `chapitre5_resultats.tex`, tableau `tab:protocoles-experimentaux` (l. 35) — correction (règle 2)

**Texte actuel :**
```
BGL & fenêtre/template & Apport d’Histogram au-delà d’un baseline de nouveauté. \\
```
**Texte proposé :**
```
BGL & événement/template & Apport d’Histogram au-delà d’un baseline de nouveauté. \\
```
**Preuve :** `bgl_known_unknown_result.json` (`test_rows: 19908`) ; `reports/BGL_KNOWN_UNKNOWN_ANALYSIS.md` (« Test : 19908 événements ») ; `bgl_preparation.json` (lignes source contiguës ; les variables `prior_*_window_*` sont des caractéristiques de contexte passé, non l'unité évaluée).

### P15 — `chapters/chapitre4_implementation.tex` (l. 78) — correction (règle 2)

**Texte actuel :**
```
BGL suit un protocole différent, fondé sur des fenêtres.
```
**Texte proposé :**
```
BGL suit un protocole différent : l'unité évaluée est l'événement, décrit par des caractéristiques de template et par des statistiques de contexte calculées sur une fenêtre passée.
```
**Preuve :** idem P14 (`bgl_preparation.json`, `features.window_direction: past_only`).

### P16 — `chapitre5_resultats.tex`, nouvelle sous-section après la fin de la section CICIDS2017 (après l. 123, avant `\section{HDFS : décision au niveau bloc}`) — tâche C

**Texte actuel (ancre, l. 123) :**
```
Dans ce protocole précis, la régression logistique arrive en tête selon le F1 moyen. Le niveau reste cependant faible et la dispersion élevée, signe que les scénarios n’ont pas tous la même difficulté. HistGradientBoosting présente un comportement différent : sa PR-AUC macro atteint 0,567697 dans l’artefact complémentaire, mais cette capacité de classement ne se traduit pas par un bon F1 au seuil retenu.
```
**Texte proposé (ancre conservée, puis insertion) :**
```
\subsection{Contrôle non supervisé : Isolation Forest sous protocole temporel}

Les campagnes précédentes relèvent de la classification supervisée. Pour mesurer ce que
devient la détection lorsque aucune attaque n’est vue à l’apprentissage, un Isolation
Forest \cite{liu2008isolation} est ajusté sur $10\,000$ flux bénins de lundi à jeudi, puis
évalué sur les mêmes tests du vendredi que la régression logistique et le Random Forest du
protocole temporel (graines 42 à 46). Deux seuils sont fixés sur une validation de lundi à
jeudi, disjointe de l’ajustement : le quantile 99\,\% des scores bénins, qui n’utilise que
des données normales, et le seuil maximisant le F1 de validation, qui utilise les attaques
de lundi à jeudi.

\begin{table}[H]
\centering
\caption[Isolation Forest et modèles supervisés, protocole temporel CICIDS2017.]{Isolation Forest et modèles supervisés sur le même test du vendredi, cinq graines. Sources : \texttt{agent6\_cicids\_iforest\_20261104T141904Z\_summary.csv} ; \texttt{cicids\_temporal\_20260910T083015Z\_metrics.csv}.}
\label{tab:cicids-iforest}
\small
\begin{tabular}{llrrrr}
\toprule
\textbf{Modèle} & \textbf{Seuil} & \textbf{F1 moyen} & \textbf{Rappel} & \textbf{FPR} & \textbf{PR-AUC} \\
\midrule
Isolation Forest & quantile bénin 99\,\% & 0,115719 & 0,063500 & 0,033440 & 0,571803 \\
Isolation Forest & max.\ F1 validation & 0,521436 & 0,519480 & 0,312340 & 0,571803 \\
LogisticRegression & supervisé & 0,556615 & 0,400960 & 0,039360 & 0,871448 \\
RandomForest & supervisé & 0,437429 & 0,280620 & 0,002400 & 0,830759 \\
\bottomrule
\end{tabular}
\end{table}

Le classement produit par Isolation Forest reste peu discriminant (ROC-AUC moyenne de
$0{,}639037$). Avec le seuil appris sur le seul trafic bénin, le taux de faux positifs
visé de 1\,\% atteint $3{,}3$\,\% le vendredi, et seulement $6{,}35$\,\% des attaques sont
détectées ; PortScan est presque entièrement manqué (rappel de $0{,}000255$). Le seuil
optimisé sur la validation relève le rappel, mais au prix d’un taux de faux positifs moyen
de $0{,}312340$ et d’une forte instabilité entre graines (écart-type du F1 : $0{,}170794$).
Sur ce test équilibré, un détecteur signalant tout flux comme attaque obtiendrait un F1 de
$0{,}667$ : le F1 seul ne suffit donc pas à juger ces résultats, et la PR-AUC comme le MCC
($0{,}069723$ et $0{,}257523$ pour Isolation Forest, contre $0{,}436298$ pour la régression
logistique) confirment l’écart. Sur ces flux, la détection sans exemple d’attaque n’atteint
pas le niveau des modèles supervisés, eux-mêmes limités hors des scénarios d’entraînement.
Les résultats réseau du mémoire doivent donc être lus comme ceux d’une classification
supervisée.
```
**Preuve :** R1 (run `agent6_cicids_iforest_20261104T141904Z`, fichiers `_summary.csv`, `_metrics.csv`, `_per_source.csv`). *Note d'intégration :* le chemin des artefacts se trouve dans `revision_reports/agent_6/artifacts/`. Le copier sous `experiments/phase_dataset_strengthening/` si la convention du chapitre 7 l'exige. Le script en fixe la provenance (`_manifest.json`).

### P17 — `chapitre5_resultats.tex`, nouvelle section après la section BGL (après la figure `fig:bgl-baseline`, l. 193, avant `\section{CSE-CIC-IDS2018 : transfert et dépendance aux variables}`) — tâche B

**Texte actuel (ancre, l. 191–195) :**
```
  \label{fig:bgl-baseline}

\end{figure}

\section{CSE-CIC-IDS2018 : transfert et dépendance aux variables}
```
**Texte proposé (insertion entre `\end{figure}` et `\section{CSE-CIC-IDS2018…}`) :**
```
\section{Mise en perspective avec des résultats publiés sur HDFS et BGL}

Le tableau~\ref{tab:baselines-publiees} rappelle quelques scores publiés sur HDFS et BGL,
accompagnés de leur protocole. Ces valeurs ne sont pas directement comparables à celles
du mémoire : l’unité évaluée (session, fenêtre ou événement), le fenêtrage, la taille et la
prévalence du test, le caractère aléatoire ou chronologique de la partition et l’usage des
labels diffèrent d’une étude à l’autre. Les tests du mémoire sont en outre beaucoup plus
petits ($2\,000$ blocs HDFS, dont 29 positifs ; $19\,908$ événements BGL).

\begin{table}[H]
\centering
\caption[Scores publiés sur HDFS et BGL et protocoles associés.]{Scores F1 publiés sur HDFS et BGL et protocoles associés. Sources : articles cités ; pour le mémoire, \texttt{ds\_hdfs\_block\_20260910T081756Z} et \texttt{ds\_bgl\_known\_unknown\_20260910T082706Z}.}
\label{tab:baselines-publiees}
\scriptsize
\begin{tabularx}{\textwidth}{p{2.3cm}p{0.9cm}p{2.2cm}p{2.0cm}Xr}
\toprule
\textbf{Source} & \textbf{Jeu} & \textbf{Méthode} & \textbf{Cadre} & \textbf{Unité et partition} & \textbf{F1} \\
\midrule
DeepLog \cite{du2017deeplog} & HDFS & DeepLog & semi-supervisé & session ; 4\,855 sessions normales en entraînement & 0,96 \\
LogBERT \cite{guo2021logbert} & HDFS & LogBERT & auto-supervisé & session ; $\approx$5\,000 séquences normales & 0,8232 \\
LogBERT \cite{guo2021logbert} & HDFS & Isolation Forest & non supervisé & session ; idem & 0,6049 \\
LogBERT \cite{guo2021logbert} & BGL & LogBERT & auto-supervisé & fenêtre de 5 min & 0,9083 \\
LogBERT \cite{guo2021logbert} & BGL & Isolation Forest & non supervisé & fenêtre de 5 min & 0,3065 \\
Le et Zhang \cite{le2022logbased} & HDFS & DeepLog & semi-supervisé & session ; aléatoire 80:20 & 0,908 \\
Le et Zhang \cite{le2022logbased} & HDFS & LogRobust & supervisé & session ; aléatoire 80:20 & 0,980 \\
Le et Zhang \cite{le2022logbased} & BGL & DeepLog & semi-supervisé & fenêtre d’1 h ; aléatoire / chronologique & 0,927 / 0,426 \\
Le et Zhang \cite{le2022logbased} & BGL & LogRobust & supervisé & fenêtre d’1 h ; aléatoire / chronologique & 0,981 / 0,967 \\
\midrule
Ce mémoire & HDFS & Histogram, moyenne par bloc & score non supervisé, seuil sur validation & bloc ; chronologique 60/20/20, 2\,000 blocs testés & 0,892308 \\
Ce mémoire & HDFS & Histogram & idem & événement ; même partition & 0,213115 \\
Ce mémoire & BGL & Histogram & nouveauté, seuil sur validation & événement ; trois périodes chronologiques & 0,913698 \\
\bottomrule
\end{tabularx}
\end{table}

Deux enseignements peuvent néanmoins être tirés. D’abord, le F1 au niveau bloc obtenu sur
HDFS se situe dans l’ordre de grandeur des méthodes séquentielles publiées, alors que le
même détecteur évalué au niveau événement chute à $0{,}213115$ : l’unité d’évaluation pèse
davantage que le choix d’architecture. Ensuite, la sensibilité au protocole observée sur
CICIDS2017 se retrouve dans la littérature sur les journaux, où le F1 de DeepLog sur BGL
passe de $0{,}927$ à $0{,}426$ avec une partition chronologique \cite{le2022logbased}. Les
Isolation Forest stricts du dépôt confirment la faiblesse de ce détecteur générique sur ces
corpus, comme dans les résultats de LogBERT : F1 moyen de $0{,}204530$ au niveau événement
sur HDFS et de $0{,}253473$ sur BGL, valeur égale à celle d’une prédiction systématiquement
positive ($0{,}253148$) (\texttt{agent6\_strict\_e3\_aggregate\_20261104T143019Z\_summary.csv}).
```
**Preuve :** R2, R4 ; `artifacts/published_baselines_hdfs_bgl.csv`. Le F1 de LogAnomaly sur HDFS de Le & Zhang (tableau 4) est volontairement omis en raison de son incohérence interne (voir `verification_references.md`).

### P18 — `chapitre5_resultats.tex`, « CSE-CIC-IDS2018 », « Protocole principal » (l. 199)

**Texte actuel :**
```
L’entraînement utilise le 15 février 2018 et le test le 16 février 2018.
```
**Texte proposé :**
```
Le jeu CSE-CIC-IDS2018 \cite{sharafaldin2018cicids,cic2018csecicids} est utilisé avec un entraînement sur le 15 février 2018 et un test sur le 16 février 2018.
```
**Preuve :** page UNB IDS2018 ; la section ne contient aujourd'hui aucune citation.

### P19 — `chapitre2_etat_art.tex`, tableau `tab:travaux-representatifs` (après la ligne Loghub, l. 920–924)

**Texte actuel :**
```
Loghub \cite{zhu2023loghub} &
2023 &
Collection de datasets &
Mise à disposition de plusieurs corpus de logs utilisés par la recherche. &
Fournit les données et benchmarks, sans architecture intégrée d'analyse. \\
```
**Texte proposé (lignes ajoutées après, dans l'ordre chronologique : à replacer selon la convention du tableau) :**
```
Loghub \cite{zhu2023loghub} &
2023 &
Collection de datasets &
Mise à disposition de plusieurs corpus de logs utilisés par la recherche. &
Fournit les données et benchmarks, sans architecture intégrée d'analyse. \\
Contract Net \cite{smith1980contract,fipa2002contractnet} &
1980 / 2002 &
Allocation négociée de tâches &
Appel à propositions, offres, attribution ; normalisation FIPA des actes. &
Protocole repris avec une nomenclature propre et deux extensions (ACCEPT, FEEDBACK) ; pas de revendication de conformité FIPA. \\
He et al. \cite{he2016experience} &
2016 &
Benchmark de détection sur logs &
Comparaison de détecteurs supervisés et non supervisés sur HDFS et BGL. &
Évaluation d'algorithmes isolés ; pas de chaîne multi-source. \\
Le et Zhang \cite{le2022logbased} &
2022 &
Réévaluation de modèles profonds &
Effet de la partition, du regroupement et du déséquilibre sur le F1. &
Motive les partitions chronologiques retenues ici ; protocoles non identiques. \\
```
**Preuve :** références vérifiées. *Remarque :* le tableau est trié par année. Placer la ligne Contract Net en tête (1980) et la ligne He et al. entre DeepLog (2017) et CICIDS2017 (2018), ou plutôt avant DeepLog, l'année 2016 précédant 2017.

---

## Récapitulatif des citations ajoutées

| Clé | Patchs où elle est citée |
|---|---|
| `smith1980contract` | P1, P7, P8, P19 |
| `fipa2002contractnet` | P1, P7, P8, P19 |
| `fipa2002aclmessage`, `fipa2002cal` | P7 |
| `wooldridge2009introduction` | P6 |
| `cic2018csecicids` | P2, P10, P18 |
| `he2016experience` | P11, P19 |
| `le2022logbased` | P11, P12, P17, P19 |
| `landauer2023deep` | P11 |
| `yu2024deep` | P12 |
| `arp2022dos` | P9 |

Toutes les nouvelles clés sont citées au moins une fois ; avec le style `plain`, une entrée non citée n'apparaîtrait pas. La bibliographie passerait de 28 à 39 références.
