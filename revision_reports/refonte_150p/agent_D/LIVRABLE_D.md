# LIVRABLE D — Cadre théorique, originalité et positionnement

Agent D, chantier « Refonte 150 pages », 2026-11-05. Aucun `.tex` ni `references.bib` modifié.
Fichiers lus : `chapters/chapitre2_etat_art.tex` (ch. 1 du PDF, p. 16–45), `chapters/chapitre4_implementation.tex` (§3.8.1 Histogram), `chapters/spec_utilite.tex`, `chapters/chapitre1_introduction.tex` (définitions), `main.tex` (résumés), `chapitre6_conclusion.tex`, `chapitre6_discussion.tex`, `references.bib`, `main.toc`, `main.bbl`, `docs/datasets/LINUX_AUTH.md`, `docs/memoire/final_experiments_2026/final_data_source_traceability.csv`, `data/raw/Datasets/DARPA_eval_b/DARPA_eval_b/README*`.

---

## 1. Reproches du périmètre : classement et preuves

| # | Reproche | Classement | Preuve |
|---|---|---|---|
| D-1 | Ch. 1 = catalogue ; LOF et One-Class SVM présentés puis jamais utilisés (L2 §2.3) | **Fondé** | §1.6.3 et §1.6.4 (`chapitre2_etat_art.tex`, « \subsection{Local Outlier Factor} », « \subsection{One-Class SVM} ») ; aucune occurrence de LOF/OCSVM ailleurs dans `chapters/*.tex`. Les clés `breunig2000lof` et `scholkopf2001estimating` ne sont citées que là. |
| D-2 | Extra Trees et gradient boosting « introduits sans lien avec une question » (L2 §2.3) | **Partiellement fondé** | Ils *sont* utilisés : comparaison des cinq modèles CICIDS2017, `chapitre5_resultats.tex` (« Une expérience distincte compare LogisticRegression, RandomForest, SGDLogistic, ExtraTrees et HistGradientBoosting »), tableau des candidats. Mais §1.5.4 ne dit pas quelle question ils servent, et SGDLogistic n'est pas présenté du tout. Le lien est à écrire, pas la section à supprimer. |
| D-3 | Littérature allocation / équilibrage de charge absente (power of two choices, JSQ) (L2 §2.3) | **Fondé** | Aucune entrée Mitzenmacher, Azar, Winston, Jiang dans `references.bib` (57 entrées). §1.14 compare Contract Net à Celery, Kafka, Redis Streams, Temporal (outils), jamais à la théorie de l'allocation. |
| D-4 | MAS : seulement Smith, FIPA, Wooldridge, AAFID ; rien de récent sur les agents pour SOC/IDS (L2 §2.3) | **Fondé** (pour le PDF) | `hmimou2025multiagent` et `song2024auditllm` existent dans `references.bib` mais ne sont cités nulle part : `main.bbl` ne les contient pas (0 occurrence), ils n'apparaissent donc pas dans la bibliographie imprimée. |
| D-5 | Histogram sans filiation (§3.8.1) (L2 §2.3) | **Fondé** | `chapitre4_implementation.tex`, « \subsection{Détecteur Histogram} » : définition formelle, aucune `\cite`. La seule mention voisine est §1.6.5 (« un histogramme appris sur une période considérée comme normale »), sans référence. |
| D-6 | Jeux UNSW, Linux/auth, Solaris BSM, DARPA 1998 utilisés sans présentation ni référence (L2 §2.3, §4 point 5) | **Fondé**, avec une nuance de fond pour Linux/auth | UNSW et Linux/auth : tableau E-H3B-STRICT (`chapitre5_resultats.tex`, « Linux/auth & 0,0528 & 0,2197 »), Solaris BSM et DARPA 1998 : routeur open-set (« audit Solaris BSM et listes de sessions DARPA 1998 »). Aucune entrée bib. **Linux/auth n'a pas de source publique** : `docs/datasets/LINUX_AUTH.md` le déclare « corpus local étiqueté ; provenance publique : NON APPLICABLE ; Références : INFORMATION À VÉRIFIER », et la traçabilité le classe « E ORIGINE INDÉTERMINÉE ». Le fichier contient au moins une ligne horodatée du 13 novembre 2026 (`linux_auth_logs_labeled.csv`, ligne 4), postérieure à la date de compilation : indice fort d'un corpus généré. Solaris BSM et DARPA 1998 sont **un seul et même jeu** : l'échantillon de l'évaluation DARPA 1998 du MIT Lincoln Laboratory (`DARPA_eval_b/README` : « sample data for the 1998 DARPA Intrusion Detection Evaluation » ; BSM = audit Solaris du serveur attaqué). |
| D-7 | Originalité limitée ; constats répliqués (L1 §D, §4 rang 8 ; L2 §2.6) | **Fondé, déjà reconnu** dans le texte | `chapitre2_etat_art.tex` §1.24 (« elles ne constituent pas une découverte conceptuelle ») et §1.25 (« Il n'introduit ni algorithme de détection, ni schéma de normalisation, ni protocole d'allocation nouveau ») ; `chapitre6_discussion.tex` §6.x « Nature et limites de la contribution » (« Ils répliquent plusieurs critiques publiées »). Ce qui manque : énoncer positivement *quelle connaissance* est obtenue (voir §5). |
| D-8 | Résultats injectés dans l'état de l'art (L2 §2.4) | **Fondé** | Six passages, listés au §6 ci-dessous (renvoi à `sec:cicids-resultats`, résultat multiformat, corrélateur, §1.24 avec renvoi à `sec:e-cnp-moindre`, tableau 1.6 avec « probabilité d'échec de 0,9 »). |
| D-9 | Définition « opérationnelle » de l'agent vide le concept ; utilité à termes constants ; « intelligents » non tenu (L2 §2.3) | **Fondé** pour les campagnes Redis, **partiellement** pour le Contract Net local | `spec_utilite.tex` : « Comme M=1 et A=L, toute offre émise vérifie […] U=0,20+0,30C+0,20H+0,25(1−ρ_a)+0,05T » ; « Dans les campagnes Redis, P_a=1 […] U=0,65+0,30C+0,20H+0,05T » ; « le refus pour faible utilité y reste donc inactif ». Dans le Contract Net local, ρ_a varie (charge), donc A et L ne sont pas constants ; H et T évoluent par `learn` si la mémoire est active. L'intelligence se réduit bien à un score pondéré à poids fixes, dont trois composantes sur six (M, A, L) sont constantes dans les campagnes Redis. |
| D-10 | Sharafaldin cité pour deux jeux distincts (L2 §2.5) | **Inexact sur le fond** (périmètre E) | `cic2018csecicids` note : « Publication de référence demandée par les auteurs : Sharafaldin, Habibi Lashkari et Ghorbani, ICISSP 2018 ». Le CIC demande cette citation pour les deux jeux. À expliciter en une phrase, pas à corriger. |

---

## 2. Plan section par section du chapitre 1 (p. 16–45, 30 pages, 26 sections)

Cible : ~19–20 pages, 11 sections numérotées. Les pages viennent de `main.toc`.

| Section actuelle (p.) | Action | Détail | Gain (p.) |
|---|---|---|---|
| 1.1 Introduction (16) | Condenser | Garder le 3ᵉ paragraphe (fil du chapitre) ; supprimer « ne cherche donc pas à dresser un catalogue » (le chapitre doit le démontrer, pas l'affirmer). | 0,5 |
| 1.2 Journaux système et réseau (17–18), 3 sous-sections | Fusionner en une section sans sous-sections | Garder NIST SP 800-92, RFC 5424, typologie en un paragraphe. | 0,5 |
| 1.3 Détection d'intrusion et d'anomalies (18–20) + 1.4 Règles et signatures (20–21) | Fusionner : « Détection : règles, anomalies, décision » | Denning, Axelsson, Chandola ; règles en un paragraphe (avantages, limites, complémentarité) ; garder « signal → alerte → incident ». | 1,25 |
| 1.5 Apprentissage supervisé (21–22), 4 sous-sections | Condenser en « Modèles évalués » | Un paragraphe par famille **utilisée** : RF, régression logistique (+ SGD, à introduire), Extra Trees, HistGradientBoosting, chacun relié à la comparaison CICIDS2017 du ch. 4 par la question qu'il sert (contrôle de complexité ; sensibilité au choix d'ensemble d'arbres). | 0,75 |
| 1.6 Non supervisé (22–24) | **Supprimer 1.6.3 LOF et 1.6.4 One-Class SVM** ; garder Isolation Forest (utilisé, contrôle CICIDS) ; **réécrire 1.6.5** en « Scores de rareté fréquentielle » avec la filiation d'Histogram (§4) | Les clés `breunig2000lof`, `scholkopf2001estimating` disparaissent alors de la bibliographie (plus citées). | 0,75 |
| 1.7 Déséquilibre des classes (24) | Fusionner dans 1.8 (un paragraphe « métriques ») | | 0,25 |
| 1.8 Datasets (24–26) | Conserver, **ajouter** UNSW-NB15, DARPA 1998 (dont audit Solaris BSM), Linux/auth (corpus local d'origine indéterminée) ; retirer les anticipations de résultats (§6) | Ajout de ~0,5 p. | −0,5 |
| 1.9 Parsing (26–27) | Conserver, alléger l'exemple | | 0,25 |
| 1.10 Normalisation (27–29) | Conserver tableau 1.1 ; retirer la phrase de résultat multiformat (§6) | | 0,25 |
| 1.11 Analyse séquentielle (29–30) + 1.12 Représentation sémantique (30–31) | Fusionner | DeepLog, LogAnomaly, LogBERT, LLM en un paragraphe ; **garder intégralement** 1.11.5 (sensibilité au protocole : c'est le cadre de QR6). | 1,5 |
| 1.13 Cadres intégrés (31–32) | Conserver | L1 §D le crédite explicitement. Tableau 1.2 conservé. | 0 |
| 1.14 Agents, files, workflows (32–33) | Conserver et **enrichir** : « Allocation de tâches : négociation et équilibrage de charge » | Ajouter Jiang 2016, Azar et al. 1999, Mitzenmacher 2001 et 2000 (information périmée), Winston 1977 (JSQ), Dias et al. 2006 (allocation par marché), Hmimou et al. 2025, Song et al. 2024. Paragraphe proposé au §3. | −0,75 |
| 1.15 Livraison, reprise, idempotence (33–34) | Conserver | Cadre direct de H2. | 0 |
| 1.16 Routage et spécialisation (34–35) | Condenser | Supprimer la liste à puces d'indices ; garder la distinction orientation / gain prédictif. | 0,25 |
| 1.17 Corrélation (35–36) | Condenser ; déplacer le dernier paragraphe (corrélateur d'Ariel, circuit fermé) au ch. 2 ou 4 | | 0,3 |
| 1.18 Mémoire et feedback (36) + 1.19 Gouvernance MLOps (36–37) | Fusionner ; déplacer le paragraphe final sur Ariel au ch. 2 | | 0,7 |
| 1.20 Tableaux de bord (37–38) | Réduire à un paragraphe dans 1.18/1.19 fusionnés (sort de QR4 à arbitrer par l'Agent A) | | 0,5 |
| 1.21 Reproductibilité (38–39) | Réduire à un paragraphe (la chaîne résultat → artefact) ; le détail relève du ch. 7 | | 0,6 |
| 1.22 Tableau 1.4, familles d'approches (39–40) | **Supprimer** | Redit les sections 1.3–1.18 ; jugé illisible par L2 §2.5. | 1,25 |
| 1.23 Tableau 1.5, travaux représentatifs (40–42) | Réduire à 7–8 lignes en lien direct avec les questions : Contract Net/FIPA, AAFID, Hmimou et al. 2025, He et al. 2016, Le et Zhang 2022, Engelen/Liu (validité des corpus), LogAI. Supprimer Denning, Isolation Forest, DeepLog, LogAnomaly, LogBERT, Loghub, CICIDS2017 (déjà présentés dans le texte). | | 1 |
| 1.24 Tensions + 1.25 Positionnement (42–45) | Fusionner en « Positionnement » (~1 p.) ; **sortir le tableau 1.6** vers la section unique de synthèse « implémenté / testé / effectivement supérieur » demandée par L1 §F (ch. 6) | Ch. 1 ne garde que ce que le travail *examine* et ce qu'il *ne revendique pas*, sans résultat. | 2 (dont ~1 p. réapparaît au ch. 6) |
| 1.26 Synthèse (45) | Condenser à une demi-page | | 0,5 |

**Bilan ch. 1** : ~11,7 p. retirées, ~1,25 p. ajoutées, ~1 p. transférée au ch. 6 → **gain net sur le document ≈ 9,5 p.** ; 26 → 11 sections.

Structure cible du ch. 1 : 1.1 Introduction · 1.2 Journaux système et réseau · 1.3 Détection : règles, anomalies, décision · 1.4 Modèles évalués et scores de rareté · 1.5 Jeux de données et validité des évaluations · 1.6 Parsing et normalisation · 1.7 Analyse séquentielle et sensibilité au protocole · 1.8 Cadres intégrés · 1.9 Allocation de tâches, agents et orchestration (dont livraison et idempotence) · 1.10 Routage, corrélation, mémoire et gouvernance · 1.11 Positionnement et synthèse.

---

## 3. Références à ajouter

Toutes vérifiées par recherche web le 2026-11-05 (métadonnées et DOI croisés sur au moins deux notices), sauf mention « à vérifier ».

```bibtex
@article{mitzenmacher2001power,
  author  = {Mitzenmacher, Michael},
  title   = {The Power of Two Choices in Randomized Load Balancing},
  journal = {IEEE Transactions on Parallel and Distributed Systems},
  volume  = {12},
  number  = {10},
  pages   = {1094--1104},
  year    = {2001},
  doi     = {10.1109/71.963420}
}

@article{mitzenmacher2000old,
  author  = {Mitzenmacher, Michael},
  title   = {How Useful Is Old Information?},
  journal = {IEEE Transactions on Parallel and Distributed Systems},
  volume  = {11},
  number  = {1},
  pages   = {6--20},
  year    = {2000},
  doi     = {10.1109/71.824633}
}

@article{azar1999balanced,
  author  = {Azar, Yossi and Broder, Andrei Z. and Karlin, Anna R. and Upfal, Eli},
  title   = {Balanced Allocations},
  journal = {SIAM Journal on Computing},
  volume  = {29},
  number  = {1},
  pages   = {180--200},
  year    = {1999},
  doi     = {10.1137/S0097539795288490}
}

@article{winston1977shortest,
  author  = {Winston, Wayne},
  title   = {Optimality of the Shortest Line Discipline},
  journal = {Journal of Applied Probability},
  volume  = {14},
  number  = {1},
  pages   = {181--189},
  year    = {1977},
  doi     = {10.1017/S0021900200104772}
}

@article{jiang2016survey,
  author  = {Jiang, Yichuan},
  title   = {A Survey of Task Allocation and Load Balancing in Distributed Systems},
  journal = {IEEE Transactions on Parallel and Distributed Systems},
  volume  = {27},
  number  = {2},
  pages   = {585--599},
  year    = {2016},
  doi     = {10.1109/TPDS.2015.2407900}
}

@article{dias2006market,
  author  = {Dias, M. Bernardine and Zlot, Robert and Kalra, Nidhi and Stentz, Anthony},
  title   = {Market-Based Multirobot Coordination: A Survey and Analysis},
  journal = {Proceedings of the IEEE},
  volume  = {94},
  number  = {7},
  pages   = {1257--1270},
  year    = {2006},
  doi     = {10.1109/JPROC.2006.876939}
}

@inproceedings{moustafa2015unsw,
  author    = {Moustafa, Nour and Slay, Jill},
  title     = {{UNSW-NB15}: A Comprehensive Data Set for Network Intrusion Detection Systems ({UNSW-NB15} Network Data Set)},
  booktitle = {Military Communications and Information Systems Conference (MilCIS)},
  pages     = {1--6},
  year      = {2015},
  publisher = {IEEE},
  doi       = {10.1109/MilCIS.2015.7348942}
}

@article{moustafa2016evaluation,
  author  = {Moustafa, Nour and Slay, Jill},
  title   = {The Evaluation of Network Anomaly Detection Systems: Statistical Analysis of the {UNSW-NB15} Data Set and the Comparison with the {KDD99} Data Set},
  journal = {Information Security Journal: A Global Perspective},
  volume  = {25},
  number  = {1--3},
  pages   = {18--31},
  year    = {2016},
  doi     = {10.1080/19393555.2015.1125974}
}

@inproceedings{lippmann2000darpa,
  author    = {Lippmann, Richard P. and Fried, David J. and Graf, Isaac and Haines, Joshua W. and Kendall, Kristopher R. and McClung, David and Weber, Dan and Webster, Seth E. and Wyschogrod, Dan and Cunningham, Robert K. and Zissman, Marc A.},
  title     = {Evaluating Intrusion Detection Systems: The 1998 {DARPA} Off-Line Intrusion Detection Evaluation},
  booktitle = {Proceedings of the DARPA Information Survivability Conference and Exposition (DISCEX'00)},
  volume    = {2},
  pages     = {12--26},
  year      = {2000},
  publisher = {IEEE},
  doi       = {10.1109/DISCEX.2000.821506}
}

@article{mchugh2000testing,
  author  = {McHugh, John},
  title   = {Testing Intrusion Detection Systems: A Critique of the 1998 and 1999 {DARPA} Intrusion Detection System Evaluations as Performed by {Lincoln Laboratory}},
  journal = {ACM Transactions on Information and System Security},
  volume  = {3},
  number  = {4},
  pages   = {262--294},
  year    = {2000},
  doi     = {10.1145/382912.382923}
}

@inproceedings{goldstein2012hbos,
  author    = {Goldstein, Markus and Dengel, Andreas},
  title     = {Histogram-Based Outlier Score ({HBOS}): A Fast Unsupervised Anomaly Detection Algorithm},
  booktitle = {KI-2012: Poster and Demo Track, 35th German Conference on Artificial Intelligence},
  editor    = {W{\"o}lfl, Stefan},
  pages     = {59--63},
  year      = {2012},
  address   = {Saarbr{\"u}cken}
}
```

Remarques de vérification :
- **Winston 1977** : DOI Cambridge `10.1017/S0021900200104772`, relevé sur Scilit ; résolution sur cambridge.org **à vérifier** avant intégration.
- **Lippmann 2000** : la liste de onze auteurs est celle de la notice IEEE ; le Lincoln Laboratory demande la forme « Lippmann et al. » (archive.ll.mit.edu/ideval/results.html). Liste complète **à vérifier** sur IEEE Xplore avant intégration.
- **HBOS** : actes en ligne sans DOI (DFKI, publication 6431). Pas de DOI à ajouter.
- **Moustafa & Slay 2016** : DOI tiré d'une notice researchr ; **à vérifier** sur le site de l'éditeur (Taylor & Francis). C'est l'article qui décrit les partitions `training-set` / `testing-set` utilisées localement (`UNSW_NB15_training-set.parquet`, `…testing-set.parquet`).
- **McHugh 2000** : à citer avec Lippmann, car c'est la critique classique de DARPA 1998 ; elle prolonge exactement le thème de QR6 (validité des corpus construits).

**Déjà présentes dans `references.bib`, à citer** (aucun ajout BibTeX) : `hmimou2025multiagent` (IEEE Access, DOI `10.1109/ACCESS.2025.3602681`, vérifié) et `song2024auditllm` (arXiv 2408.08902, vérifié). Ce sont les travaux récents « agents pour SOC/IDS » demandés par L2.

**Linux/auth — pas de référence à ajouter.** Aucune source publique n'est établie (`docs/datasets/LINUX_AUTH.md`). Fabriquer une référence serait une faute. Action : présenter le jeu en une phrase au §1.5 cible comme « corpus local étiqueté de tentatives d'authentification, d'origine non documentée et vraisemblablement généré (au moins un horodatage postérieur à la rédaction) ; il sert au routage et aux comparaisons de familles, sans valeur de représentativité ». Conséquence pour les Agents B et C : les résultats E-H3B-STRICT sur Linux/auth (+0,1669) portent sur un corpus de provenance inconnue ; la limite doit figurer une fois dans la section des limites. À signaler à l'auteur : s'il connaît l'origine (Kaggle ou autre), la donner, sinon la déclarer inconnue.

**Solaris BSM / DARPA 1998** : une seule référence, `lippmann2000darpa` (+ `mchugh2000testing`). Ajouter au §1.5 cible : « l'échantillon public de l'évaluation DARPA 1998 du MIT Lincoln Laboratory, qui comprend l'audit BSM d'un serveur Solaris et des listes de sessions, sert uniquement de source *inconnue* pour le test open-set du routeur ».

**Paragraphe proposé pour le §1.9 cible (allocation de tâches)** :

> Le choix d'un exécutant pour une tâche est un problème classique d'équilibrage de charge, bien antérieur aux systèmes multi-agents \cite{jiang2016survey}. Pour des serveurs identiques, affecter chaque arrivée à la file la plus courte est optimal sous des hypothèses markoviennes \cite{winston1977shortest} ; consulter seulement deux exécutants tirés au hasard et retenir le moins chargé suffit déjà à réduire exponentiellement la charge maximale \cite{azar1999balanced,mitzenmacher2001power}. Ces résultats supposent toutefois une information de charge fraîche : lorsque l'état observé est périmé, les politiques gloutonnes peuvent provoquer des effets de troupeau et se dégrader \cite{mitzenmacher2000old}. La négociation à la Contract Net \cite{smith1980contract} et les mécanismes d'allocation par marché \cite{dias2006market} répondent au cas où l'état des exécutants n'est connu que d'eux-mêmes : l'appel d'offres leur fait révéler une évaluation locale au prix d'un aller-retour de messages. Dans les architectures récentes d'agents pour la détection et la corrélation de menaces, l'allocation reste le plus souvent déterminée par la spécialisation des agents plutôt que négociée \cite{hmimou2025multiagent,song2024auditllm}. La littérature prédit ainsi qu'avec un état de charge directement accessible et sans coût de communication, une affectation au moindre chargé constitue un comparateur difficile à battre pour une négociation ; c'est le comparateur retenu au chapitre~4.

*Note pour l'Agent C/E* : la phrase sur Hmimou et Song (« le plus souvent déterminée par la spécialisation ») doit être vérifiée sur les deux articles avant intégration ; à défaut, la réduire à « proposent des architectures d'agents spécialisés pour la détection et la corrélation de menaces ». La dernière phrase répond aussi à L1 §C.1 (biais du comparateur) : elle doit rester cohérente avec la formulation de l'Agent B.

---

## 4. Filiation d'Histogram

Constat technique (d'après `chapitre4_implementation.tex` §3.8.1) : r(e) = −(1/3) Σ_{a∈{τ,s,v}} log p̃_a(a(e)), avec des histogrammes appris sur les seuls événements normaux et un plancher de compte à 1. C'est **exactement le score HBOS** (Goldstein & Dengel 2012 : somme, sur les attributs, du logarithme de l'inverse de la hauteur de l'histogramme), appliqué à trois attributs catégoriels dont chaque modalité forme une classe, au facteur 1/3 près, qui ne change pas l'ordre des scores. C'est aussi l'information propre (surprise) moyenne d'un événement sous un modèle d'indépendance des attributs. La baseline HDFS `template_only_mean_surprisal` est la restriction de ce même score au seul template : la comparaison E-H4 oppose donc Histogram à sa propre version univariée, ce qui mérite d'être dit (à transmettre à l'Agent B).

**Paragraphe proposé** (à placer au §1.4 cible « Modèles évalués et scores de rareté », et à rappeler en une phrase au début de §3.8.1) :

> Les scores de rareté fréquentielle constituent la famille la plus simple de détecteurs non supervisés. HBOS estime, pour chaque attribut, un histogramme sur des données de référence et attribue à une observation la somme des logarithmes de l'inverse des fréquences de ses valeurs ; l'indépendance supposée entre attributs le rend rapide, au prix d'une cécité aux anomalies qui ne se manifestent que par des combinaisons de valeurs \cite{goldstein2012hbos}. Appliqué à des attributs catégoriels, ce score est l'information propre moyenne d'une observation sous un modèle d'indépendance : un événement est d'autant plus suspect que ses modalités étaient rares dans la période de référence. Le détecteur Histogram utilisé dans ce travail (section~\ref{subsec:histogram}) est une instance de HBOS sur trois attributs catégoriels des journaux (template, source, sévérité), appris sur les seuls événements normaux de l'entraînement. Il n'introduit aucune idée nouvelle ; il sert de détecteur léger de référence, et sa faiblesse attendue, la confusion entre rareté et nouveauté, est précisément ce que les protocoles du chapitre~4 mettent à l'épreuve.

Dans §3.8.1, ajouter en tête : « Le détecteur suit le principe de HBOS \cite{goldstein2012hbos}, restreint à des attributs catégoriels. »

---

## 5. Contribution recadrée

**Paragraphe proposé** (remplace la fin de §1.25 et sert de modèle à la discussion, à la conclusion et aux résumés) :

> Ce travail ne propose ni algorithme de détection, ni schéma de normalisation, ni protocole d'allocation nouveau. Il s'agit d'une étude expérimentale critique de l'intégration et de l'orchestration, menée sur un prototype construit à cette fin et sous contraintes de laboratoire. Son apport tient à la connaissance obtenue en soumettant une même chaîne à des comparateurs contrôlés : à protocole strict, aucun des détecteurs principaux ne dépasse une règle simple sur les quatre jeux publics ; l'effet attribué aux agents lors de la reprise relève du magasin d'idempotence ; face à un répartiteur au moindre chargé, la négociation n'apporte aucun gain de débit ; et le gain de la mémoire n'apparaît que sous une défaillance extrême. Les deux premiers constats répliquent, dans une chaîne intégrée, des avertissements déjà publiés sur la validité des évaluations ; les deux derniers ont été prédits par la littérature de l'équilibrage de charge, mais rarement mesurés sur une architecture d'agents. La contribution est donc étroite : un banc instrumenté, des ablations qui attribuent chaque propriété observée à son mécanisme effectif, et des résultats négatifs documentés. Ce travail ne démontre ni la supériorité d'une architecture multi-agents, ni sa capacité à analyser conjointement des journaux système et réseau.

Points de contrôle :
- Chaque constat cité doit correspondre à un résultat déjà dans le manuscrit (tableau 4.15 ; tableau 4.10 ; §4.10.4 ; tableau 4.11). Aucun chiffre n'est ajouté ici volontairement : les chiffres restent au ch. 4.
- « rarement mesurés sur une architecture d'agents » est une appréciation de la littérature ; si l'Agent E ou l'auteur ne peut pas l'étayer, la retirer et garder « prédits par la littérature de l'équilibrage de charge ».
- Le résumé (`main.tex`), la conclusion (`chapitre6_conclusion.tex`, 1ᵉʳ paragraphe : « dans l'organisation d'une chaîne traçable qui associe […] ») et la discussion (« Nature et limites de la contribution ») doivent reprendre la même formulation. La conclusion actuelle met encore en avant l'*organisation* de la chaîne plutôt que la connaissance obtenue : à aligner.

---

## 6. Frontière cadre / constats : passages du ch. 1 à traiter

| # | Passage (repérer par le texte, `chapitre2_etat_art.tex`) | Page PDF | Action |
|---|---|---|---|
| F-1 | §1.8.2 : « La chute du F1 observée ici entre séparation aléatoire et séparation par scénario (section~\ref{sec:cicids-resultats}) est donc cohérente avec ces constats indépendants » | 25 | **Supprimer** la phrase. La rapprocher, au ch. 4 (§4.2), des critiques d'Engelen et Lanvin. |
| F-2 | §1.8.3, dernier paragraphe : « Dans ce mémoire, CSE-CIC-IDS2018 est donc traité comme un objet d'audit […] comparaison avec des règles mono-variable » | 25 | **Réécrire** au futur méthodologique, sans résultat : « La littérature impose donc de contrôler l'intégrité des fichiers et l'absence de variable de substitution avant d'interpréter un score. » Le protocole va au ch. 4. |
| F-3 | §1.10.2 : « Dans le protocole multiformat de ce mémoire, les flux tabulaires ne renseignent aucun des sept champs standard retenus. Le résultat démontre la lecture […] » | 28 | **Supprimer** ces deux phrases ; garder la phrase de principe (« La conformité doit donc être évaluée champ par champ »). Le 0/7 reste au ch. 4. |
| F-4 | §1.17.2, dernier paragraphe : « Le corrélateur d'Ariel Logminer appartient à la famille […] Son corpus synthétique reprend les clés […] fragmentation des incidents multi-étapes » | 35–36 | **Déplacer** la description au ch. 2 (modèle) et le constat (circuit fermé, fragmentation) au ch. 4 ; ne garder au ch. 1 que l'exigence d'évaluation (incidents de référence, baselines « hôte + fenêtre », « fenêtre seule »). |
| F-5 | §1.19.2, dernier paragraphe : « Dans Ariel Logminer, la mémoire persistante […] support de gouvernance expérimental » ; §1.20.2 dernière phrase : « le tableau de bord fait l'objet d'une validation fonctionnelle » | 37–38 | **Déplacer** au ch. 2 ou à la section de synthèse ; le ch. 1 ne qualifie pas le prototype. |
| F-6 | §1.24, dernier paragraphe : « Ariel Logminer satisfait partiellement cette ambition […] aucun bénéfice propre de la négociation n'est établi face à une répartition au moindre chargé (section~\ref{sec:e-cnp-moindre}) […] elles ne constituent pas une découverte conceptuelle » | 42 | **Supprimer** du ch. 1 ; le contenu va dans la section unique de synthèse (ch. 6). Garder les quatre exigences de comparaison (liste à puces), qui sont un cadre. |
| F-7 | §1.25, 2ᵉ paragraphe : « Les expériences du mémoire établissent pour leur part plusieurs limites : forte dépendance aux jeux […] corrélation validée seulement en circuit fermé » | 42–43 | **Supprimer** du ch. 1. |
| F-8 | Tableau 1.6 (`tab:positionnement-logminer`), colonne « Ce que le prototype établit », et ligne Mémoire : « établi seulement pour une probabilité d'échec de 0,9 » | 44 | **Déplacer** le tableau au ch. 6, transformé en tableau « implémenté / testé / effectivement supérieur » (L1 §F). Au ch. 1, au plus une phrase : ce que le travail examine et ce qu'il ne revendique pas. |
| F-9 | §1.11.5 : « Ces constats justifient de privilégier ici des partitions chronologiques ou par scénario et de ne pas écarter a priori les modèles légers (H4). » | 30 | **Conserver** : c'est une justification de conception, pas un résultat. |
| F-10 | §1.6.2 et §1.5.2 : « Cette limite justifie la présence de plusieurs protocoles d'évaluation dans le travail expérimental de ce mémoire. » | 21 | **Conserver** (choix de protocole), ou fusionner avec F-9. |

Après ces actions, le ch. 1 ne contient plus de `\ref` vers le ch. 4 ni de chiffre issu des expériences ; les seuls nombres restants sont des résultats publiés par d'autres (Le et Zhang : 0,927 → 0,426 ; synthèse LLM : 183 travaux).

---

## 7. Définition de l'agent et qualificatif « intelligent »

Diagnostic : la définition de l'introduction (`chapitre1_introduction.tex`, « Le qualificatif \textbf{intelligent} renvoie, dans ce contexte, à une adaptation opérationnelle ») promet une adaptation fondée sur l'état, l'historique, la charge et la latence. `spec_utilite.tex` montre que, dans les campagnes Redis, la décision se réduit à U = 0,65 + 0,30C + 0,20H + 0,05T, avec un seuil de refus inactif ; l'adaptation n'existe que par H et T, et seulement si la mémoire est activée. Le mot « intelligent » n'est pas tenu ; L2 a raison.

**Actions proposées** :
1. Supprimer le paragraphe « Le qualificatif intelligent » de l'introduction et le mot « intelligents » des mots-clés (`main.tex`, mots-clés FR « agents intelligents » ; EN « intelligent agents » ; bokuse). Remplacer par « agents logiciels à décision locale paramétrée ».
2. Conserver le nom de classe `MultiTaskIntelligentAgent`, mais le présenter comme un identifiant de code, à la première occurrence : « la classe `MultiTaskIntelligentAgent` (le nom est hérité du code et ne qualifie pas le comportement) ».
3. **Formulation proposée** pour l'introduction (remplace la définition de l'agent et celle d'« intelligent ») :

> Un agent désigne ici une entité logicielle qui dispose de capacités déclarées, d'un état propre et d'une règle locale de décision : face à une tâche, elle calcule un score d'utilité, propose ou refuse son exécution, exécute un traitement compatible et peut produire des sous-tâches. Cette définition est volontairement faible. Elle correspond aux propriétés de réactivité et de capacité sociale de Wooldridge \cite{wooldridge2009introduction}, mais pas à la proactivité ni à l'autonomie cognitive : la règle de décision est une somme pondérée à poids fixés avant les expériences, dont plusieurs composantes sont constantes dans les campagnes distribuées (section~\ref{sec:spec-utilite}), et sa seule adaptation tient à la mise à jour de deux taux empiriques lorsque la mémoire est activée. Le mot « agent » désigne donc une organisation du logiciel, non une capacité de raisonnement ; savoir si cette organisation apporte un bénéfice mesurable par rapport à une affectation plus simple est précisément l'une des questions examinées.

4. Dans le tableau de synthèse unique (ch. 6), ligne « Agents » : implémenté = échanges de type Contract Net, état persistant, score d'utilité ; testé = débit, reprise, mémoire ; effectivement supérieur = aucun constat.

Cette requalification rejoint celle du titre (Agent A) : si « intelligents » n'apparaît pas dans le titre actuel, il est présent dans les mots-clés et l'introduction.

---

## 8. Effet sur le volume

| Poste | Pages |
|---|---|
| Ch. 1 : suppressions et condensations (§2) | −11,7 |
| Ch. 1 : ajouts (jeux, allocation, HBOS) | +1,25 |
| Tableau 1.6 transféré vers le ch. 6 (part qui réapparaît) | +1 (au ch. 6) |
| Introduction : définition « intelligent » remplacée (plus courte) | −0,25 |
| Bibliographie : +11 entrées imprimées (9 nouvelles + 2 déjà présentes mais non citées), −2 (LOF, OCSVM) | +0,75 |
| **Net document** | **≈ −9 pages** |

Risque principal : en condensant §1.13–1.15 et §1.24, effacer les éléments que L1 §D crédite (comparaison aux cadres intégrés, files de tâches, politiques d'orchestration). Ces sections sont marquées « conserver ». Second risque : déplacer le tableau 1.6 sans créer la section de synthèse au ch. 6 ; les deux opérations doivent être faites ensemble.

---

## Points hors périmètre signalés

- Ch. 2 rédigé au conditionnel (L2 §2.4) : à confier à l'Agent E ou à l'intégration.
- E-H4 : Histogram est comparé à sa propre restriction univariée (§4) ; Linux/auth de provenance inconnue (§3) : à transmettre aux Agents B et C.
- Sharafaldin pour deux jeux : citation demandée par le CIC (D-10) ; à l'Agent E.

=== PASSATION ===
Agent : D — Cadre théorique, originalité et positionnement
Statut : terminé
Livrable : `revision_reports/refonte_150p/agent_D/LIVRABLE_D.md`
Résultats clés : ch. 1 ramené de 26 à 11 sections, gain net ≈ 9 p. ; LOF et One-Class SVM supprimés, Extra Trees et HGB conservés mais reliés à la comparaison CICIDS ; 11 références vérifiées (dont 2 déjà présentes mais non citées) ; Histogram = HBOS catégoriel ; dix passages de résultats dans le ch. 1 à retirer ou déplacer ; tableau 1.6 à transférer vers la synthèse unique du ch. 6 ; « intelligent » retiré.
Points à vérifier avant intégration : résolution du DOI de Winston 1977 ; liste d'auteurs de Lippmann 2000 ; DOI de Moustafa & Slay 2016 ; contenu exact de Hmimou 2025 et Song 2024 pour la phrase sur l'allocation.
Question à l'auteur : origine du corpus Linux/auth (aucune source publique documentée ; horodatages postérieurs à la rédaction).
Dépendances : Agent A (sort de QR4 et du titre) ; Agent B (formulation du biais du moindre chargé) ; intégration (section unique de synthèse au ch. 6).
=== FIN PASSATION ===
