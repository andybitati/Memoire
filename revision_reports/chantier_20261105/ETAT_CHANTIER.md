# ETAT_CHANTIER — révision académique du mémoire Ariel Logminer

Dernière mise à jour : 2026-11-05, reprise Claude Code. Statut global : **AGENTS CLOS, verdict provisoire ; reste aux mains de l'auteur (voir « Questions à l'auteur »)**. Consignes communes à tous les agents : `CONSIGNES_COMMUNES.md`.

Retours des trois lecteurs, texte intégral : `revision_reports/chantier_20261105/RETOURS_LECTEURS.md`. Chaque agent lit **les trois retours en entier**, pas seulement les points listés pour son périmètre.

## Repères pour tout repreneur

- Mission complète (texte de l'auteur, périmètres, protocole de passation) : `revision_reports/chantier_20261105/MISSION.md`. La lire en entier avant toute action.
- Manuscrit : `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex` + `chapters/*.tex` + `frontmatter/*.tex` ; PDF `ARIEL_LOGMINER_MEMOIRE_FINAL/main.pdf` (181 pages, compilé le 2026-11-05). Compilation : `pdflatex main` → `bibtex main` → `pdflatex main` ×2, dans `ARIEL_LOGMINER_MEMOIRE_FINAL/`.
- Correspondance fichiers / numérotation du PDF : voir `revision_reports/agent_7/PATCH_NOTES.md`, section « Correspondance fichiers / numérotation du PDF ». Les numéros de page et de section cités dans MISSION.md se réfèrent au PDF.
- Révision précédente (4 novembre, agents 1–7 de l'ancienne numérotation) : `revision_reports/HANDOFF.md`. **Attention : les dossiers `revision_reports/agent_<N>/` appartiennent à cette révision antérieure.** Les livrables du présent chantier vont dans `revision_reports/chantier_20261105/`.
- Artefacts expérimentaux publics : `experiments/phase_revision_20261104/` (manifeste SHA-256).
- Environnement (Python, Redis, VM) : `revision_reports/HANDOFF.md` §6.

## Décisions du coordinateur

| # | Décision | Justification |
|---|---|---|
| C1 | Les agents **n'éditent pas les `.tex`**. Chaque agent dépose ses sections corrigées dans `revision_reports/chantier_20261105/agent_<N>/sections/` (un fichier par section, nommé d'après le fichier source et la section), plus son `LIVRABLE_<N>_*.md`. L'Agent 0 intègre lot par lot, arbitre et compile. | Choix de l'auteur (2026-11-05) : les périmètres se recouvrent (résumés : 1 et 5 ; tableau 7.1 : 1 et 2 ; ch. 4–5 : 4 et 5 ; agent 7 partout). |
| C2 | Les retours des trois lecteurs seront enregistrés tels quels dans `revision_reports/chantier_20261105/RETOURS_LECTEURS.md` avant toute activation. | Les agents 1, 2, 4 et 5 s'y réfèrent par page et par extrait. |
| C3 | Règles héritées de la révision du 4 novembre, toujours applicables : aucun chiffre sans artefact (run_id + chemin) ; si une expérience contredit le texte, corriger le texte, jamais le résultat ; français soutenu et sobre. | `revision_reports/HANDOFF.md` §1. |
| C4 | **Tranché par l'auteur (2026-11-05)** : « Le travail à présenter au lecteur est unique, peu importe les tentatives faites en coulisse. C'est le résultat final de tous les travaux qui est à présenter. » Application : (a) le manuscrit présente un seul travail et ses résultats finaux, sans historique des tentatives, versions, campagnes abandonnées ni dates d'exécution ; (b) la déclaration IA (`frontmatter/declaration_ia.tex`) reste **factuelle** sur le rôle des outils d'IA (rédaction, code, exécution de campagnes) : elle n'est ni retirée ni atténuée, mais elle ne raconte pas l'historique ; (c) le manuscrit ne revendique rien qu'il ne peut prouver, en particulier aucun préenregistrement des seuils ou budgets ; (d) l'inventaire campagne par campagne demandé à l'Agent 6 (part de l'auteur, part automatisée, points à vérifier en soutenance) est un **document de préparation de la soutenance, hors manuscrit** : `agent_6/PREPARATION_SOUTENANCE.md`. | Respecte le choix de l'auteur tout en répondant aux lecteurs : présenter un résultat final est la norme, mais une déclaration IA inexacte ou une revendication de préenregistrement serait une faute académique (lecteur 2, points de non-recevabilité B et D). |

## Remarques des lecteurs hors MISSION.md, affectées par le coordinateur (C5)

Ces points figurent dans `RETOURS_LECTEURS.md` mais pas dans la liste de tâches de `MISSION.md`. Ils s'ajoutent au périmètre de l'agent indiqué.

| Point (lecteur, section) | Agent |
|---|---|
| p. 4 : « Le titre du mémoire emploie les termes autonome, distribuée et agents intelligents multitâches », absents du titre actuel (L2 §2.1) | 1 |
| §5.2 « ne mettent pas en évidence de fuite triviale » contre §4.6.4 raccourci Dst Port (L2 §2.4) — déjà dans MISSION (§5.2 vs §4.6.4) ; rappel | 1 |
| §5.7 « proposent ou refusent des tâches » contre tableau A.4 « non conclusifs » (L2 §2.4) — déjà dans MISSION ; rappel | 1 |
| Question centrale fourre-tout ; priorisation, traitements périodiques et micro-lots annoncés mais jamais mesurés ; QR1–QR6 descriptives, QR6 « la mieux couverte » (L1 C.1–C.2, L2 §2.1, L3 §1) ; distinguer exigences logicielles / hypothèses scientifiques / propriétés opérationnelles (L1 C.2) | 2 |
| « Partiellement soutenue » contre validation d'une proposition conjonctive (L1 C.3) ; H4 réfutée par les baselines triviales sur chaque jeu (L2 §2.4) | 2 |
| Absence de scénario hétérogène conjoint (journal système + flux réseau sur un même incident) : point de non-recevabilité du lecteur 3 | 2 (statut des revendications), 4 (faisabilité d'une campagne), 8 (verdict) |
| Absence de stratégie démontrée pour corriger la fragilité de généralisation ; « piège du résultat négatif » (L1 A.3, A.5 ; L3 faiblesse 5) | 4 (pistes), 8 |
| HistGradientBoosting : F1 0,0036 et PR-AUC 0,569, classement des cinq modèles dû au seuil (L2 §2.3) | 4 |
| BGL tableau 4.4 : huit protocoles explorés sans plan préalable (L2 §2.3) | 4 |
| Ablation du routage invoquée p. 97 et p. 115 sans tableau, chiffre ni artefact (L2 §2.4) | 4 |
| CSE-CIC-IDS2018 : section 4.6 « scientifiquement invalide » selon L3 ; décider si elle reste une évaluation ou devient un audit de jeu de données | 4 |
| Benchmark A–D : aucun chiffre de débit, barre d'erreur ni test statistique malgré dix répétitions (L2 §2.4) | 5 |
| Endurance « preuve directe » p. 103 à 0,5 tâche/s, soit 16 à 32 fois sous la saturation (L2 §2.4) | 5 |
| Pourquoi ces poids d'utilité ; politique comparée à un ordonnanceur déterministe (L1 B.2) ; « file d'attente avec routeur à règles » (L3 §2, faiblesse 3) | 5 |
| Distribution de la décision seulement, scores précalculés hors VM (L1 A.6) | 5 |
| Gouvernance et MLOps absents de l'état de l'art ; bibliographie mince, 39 références (L2 §2.2) ; chapitre 1 « manuel » sans débat contradictoire (L2 §2.2, L3 §2) ; redite empirique de Sommer et Paxson, Arp et al., Le et Zhang, Engelen et al. (L2 §2.6, L3 §6) | 3 |
| Tableau de bord : aucune étude d'utilisabilité (L1 D.2) | 2 (revendications), 8 |
| Reproductibilité indépendante non vérifiable sans dépôt (L1 E.2) ; plagiat non établissable sur PDF seul (L1 E.3) | 6 |
| Style marqué par la rédaction assistée (L3 §5) | 7 |

## Interventions hors agents (Agent 0)

- 2026-11-05 : la suppression du §7.7 (compilation pdfLaTeX) est **transférée de l'Agent 7 à l'Agent 6**, pour qu'un seul agent touche le chapitre 7. **Agent 7 : ce point de la liste est retiré.**
- 2026-11-05 : coquille « imparti, Il remporte » (`chapters/chapitre5_resultats.tex`, sous-section Saturation) corrigée en « imparti. Il remporte ». Elle avait été introduite par la mise à jour des figures du même jour. **Agent 7 : ce point de la liste est clos.**

## Périmètres

| Agent | Périmètre | Statut | Livrables |
|---|---|---|---|
| 1 Intégrité factuelle | voir MISSION.md + C5 | **COMPLET** le 2026-11-05 (3 questions au coordinateur : Q1-Q3 ci-dessous) | `agent_1/LIVRABLE_1_integrite.md` ; `agent_1/sections/` (15 fichiers, dont 1 option B conditionnelle) |
| 2 Hypothèses | voir MISSION.md + C5 + C9 | **COMPLET** le 2026-11-05 (5 questions au coordinateur : Q1-Q5 de l'Agent 2 ci-dessous) | `agent_2/LIVRABLE_2_hypotheses.md` ; `agent_2/sections/` (12 fichiers, dont les 3 résumés qui remplacent ceux de l'Agent 1) ; test de compilation sur copie : 0 erreur, 0 débordement, 0 référence indéfinie |
| 3 État de l'art | voir MISSION.md + C5 + C12 | **COMPLET** le 2026-11-05 (3 dépendances d'intégration A3-Q1 à A3-Q3 ci-dessous) | `agent_3/LIVRABLE_3_etat_art.md` ; `agent_3/references_proposees.bib` (18 entrées) ; `agent_3/sections/` (8 fichiers) ; validation isolée : 0 erreur, 0 citation/référence indéfinie, 0 débordement horizontal |
| 4 Méthodologie | voir MISSION.md + C5 + C13 | **COMPLET** le 2026-11-05 après compléments de la reprise (intégré directement ; voir la fin du livrable) — E-H3b : non-infériorité non établie sur `linux_auth` ; E-H4 : meilleure baseline simple légèrement supérieure à Histogram ; E-H3 : non faisable localement, constat documenté | `agent_4/LIVRABLE_4_methodologie.md` ; protocoles et runners ; résultats et manifestes E-H3b/E-H4 |
| 5 Architecture | voir MISSION.md + C13 | **COMPLET** le 2026-11-05 — E-H5 : gain conditionnel (p = 0,9) ; E-CNP : avantage conditionnel sur la table ; E-CNP-LEAST-LOADED : aucun avantage de la négociation | `agent_5/LIVRABLE_5_architecture.md` ; protocoles, runner, artefacts ; `agent_5/sections/` (6 fichiers) |
| 6 Reproductibilité / IA | voir MISSION.md + C4 (d) + C5 ; suppression transférée du §7.7 | **COMPLET** le 2026-11-05 (3 points d'intégration A6-Q1 à A6-Q3 ci-dessous) | `agent_6/LIVRABLE_6_reproductibilite.md` ; `agent_6/PREPARATION_SOUTENANCE.md` ; `agent_6/sections/` (4 fichiers : déclaration IA, chapitre 7 complet, introduction de la matrice A.2, ligne BGL G) |
| 7 Forme | voir MISSION.md | **PARTIEL** le 2026-11-05 : forme mécanique faite ; style réservé à l'auteur | `agent_7/LIVRABLE_7_forme.md` |
| 8 Verdict | synthèse | **PROVISOIRE** le 2026-11-05 : validation conditionnelle, 12/20 selon une grille proposée, évaluateur non indépendant | `agent_8/LIVRABLE_8_verdict.md` |

## Décisions de l'Agent 1 (2026-11-05)

| # | Décision | Justification |
|---|---|---|
| A1-1 | Campagne `multivm_cnp_20260909T202632Z_37592` retirée des trois résumés (option A), remplacée par la campagne d'endurance du corps ; option B (l'introduire au §4.11) préparée mais non appliquée. | L'artefact existe et confirme 60/60, 30/30, 15 refus, mais aucun `chapters/*.tex` ne la présente ; le choix d'ajouter une campagne au corps revient au coordinateur. |
| A1-2 | Paragraphe « hypothèses » des résumés aligné sur le tableau 7.1 **actuel** (3 partiellement soutenues, 2 non tranchées), marqué provisoire. | L'Agent 1 ne statue pas sur les hypothèses (Agent 2). |
| A1-3 | Chiffres des résumés absents du corps (± 0,001013, IC [0,993884 ; 0,996400], DDoS 0,778774) retirés, bien que sourcés. | Un résumé ne doit rien affirmer que le corps ne présente pas ; réintroduction possible si l'Agent 4 les ajoute au §4.2. |
| A1-4 | F1 0,157744 et 0,157827 conservés tous deux, distingués dans le texte (25 évaluations contre 5, un scénario par graine). | Deux plans d'expérience distincts, vérifiés dans les artefacts ; aucune des deux valeurs n'est fausse. |
| A1-5 | Statuts et critères du tableau 7.1 non modifiés ; seuls la phrase d'introduction et les « éléments observés » de H1 et H4 sont complétés par des faits du corps. | Le statut des hypothèses relève de l'Agent 2. |
| A1-6 | Résumés : ajout des faits défavorables établis dans le corps (règle de sévérité BGL, raccourci Dst Port, 0/7 champs, idempotence transposable, corrélation battue par la variante hôte + fenêtre). | Le résumé ne doit pas être plus favorable que le corps ; corrections factuelles minimales, reformulation de fond laissée à l'Agent 5. |

## Arbitrages du coordinateur sur le livrable 1 (2026-11-05)

| # | Décision | Justification |
|---|---|---|
| C6 | Q1 (campagne de 60 tâches) : **option A provisoire** (retrait des résumés) ; décision définitive après avis de l'Agent 5, qui dira si un comportement de refus doit être établi dans le corps (option B) ou si la revendication de refus est retirée. | Conforme à C4 (un seul travail, résultats finaux) ; l'option B n'a de sens que si l'Agent 5 conserve une revendication qui en dépend. |
| C7 | Q2 : les trois résumés (`agent_1/sections/main.tex__*.tex`) seront intégrés **après** les livrables 2 et 5 ; les agents 2 et 5 partent de ces fichiers et les amendent dans leur propre dossier `sections/`. | Les paragraphes hypothèses et architecture des résumés sont provisoires. |
| C8 | Q3 : **règle confirmée** pour tous les agents : aucun chiffre ni résultat dans un résumé ou la conclusion qui ne soit présenté dans le corps. | Point de non-recevabilité A du lecteur 2. |
| C9 | Le tableau 7.1 et les réponses QR3/QR6 de l'Agent 1 (`chapitre6_conclusion.tex__tableau_7.1.tex`, `__QR3_QR6.tex`) ne sont **pas** intégrés : ils passent à l'Agent 2 comme point de départ. Les sections `§5.7`, `tableau A.2` et l'option B attendent C6 et l'Agent 5. | Périmètres de l'Agent 2 (tableau 7.1, conclusion) et de l'Agent 5 (§5.7). |

## Décisions de l'Agent 2 (2026-11-05)

Détail et sources : `agent_2/LIVRABLE_2_hypotheses.md` (§4 fiches, §5 tableau, §7 revendications, §8 expériences).

| # | Décision | Justification |
|---|---|---|
| A2-1 | Énoncés et critères de H1–H5 repris **mot pour mot** dans l'introduction et jugés tels quels ; aucune hypothèse reformulée. | Garde-fou anti-HARKing (L1 A.2, L2 points B-C) ; seules les formes « réduction des revendications » et « perspective » sont admises. |
| A2-2 | Règles de décision R1–R6 (comparateur absent → non tranchée ; comparateur exécuté et observation réfutante → réfutée ; conjonctive réfutée dès qu'une composante l'est ; existentielle ; grandeur non fixée à l'avance non fixable après coup ; baseline = meilleure règle évaluée sur le même test), énoncées dans la conclusion. | Rendre le statut reproductible et identique pour les cinq hypothèses ; R1 est déjà écrite p. 7. |
| A2-3 | H1 : PARTIELLEMENT SOUTENUE (inchangé), requalifiée en exigence de réalisation. | Lecture 7 001/7 001 établie ; conformité non discriminante (0/7 champs pour les flux ; « normalisé » = « émis » par construction) ; référence vers la source non mesurée. |
| A2-4 | H2 : PARTIELLEMENT SOUTENUE (inchangé), requalifiée en exigence de réalisation. | Bras « agents sans idempotence » non exécuté (artefact `agent3_paired_failure_abcd…` : six bras A, B, C, D, A+I, B+I) ; effet dû au magasin, transposable ; tautologique pour le bras manquant. |
| A2-5 | H3 : NON TRANCHÉE (inchangé) ; « gain prédictif non systématique » retiré. | Comparateur non exécuté ; taux d'exécutions incompatibles jamais défini ; ablation absente du corps. |
| A2-6 | H4 : PARTIELLEMENT SOUTENUE → **NON TRANCHÉE, supériorité infirmée sur trois jeux** ; plus validable. | Sous la règle triviale sur CICIDS2017 temporel, CSE-CIC-IDS2018, BGL ; HDFS sans baseline au niveau bloc ; aucun budget fixé (R5). « Réfutée » possible en lecture littérale : Q1. |
| A2-7 | H5 : NON TRANCHÉE → **RÉFUTÉE**. | Comparateur mémoire activée/désactivée exécuté (C/D), aucun gain établi, débit et équité dégradés dans l'artefact apparié ; priorisation jamais mesurée. |
| A2-8 | Phrase de préenregistrement (p. 7) remplacée par ce qui est vérifiable, avec la liste des grandeurs jamais fixées (taux d'incompatibilité et d'erreur de H3, budget de H4, métrique de priorisation de H5). | C4 (c) ; point de non-recevabilité B (L2). |
| A2-9 | Question centrale resserrée (formats hétérogènes, routage, détection sous protocole strict, coût) avec variable principale ; priorisation, périodique, micro-lots, aide à l'analyste retirés ; QR reformulées et classées en exigences / propriétés / hypothèses (tableau `tab:nature-qr`) ; QR6 devient la question sur la dépendance au protocole ; « QR6 la mieux couverte » retiré. | L1 C.1-C.2, L2 §2.1, L3 §1 ; cadrage seulement, aucune hypothèse modifiée. |
| A2-10 | Absence de scénario hétérogène conjoint déclarée dans la question, QR1, les résumés, les limites et le tableau 1.3 ; revendication réduite à l'hétérogénéité des formats. | Point de non-recevabilité L3 ; seule une expérience (E-HET) le lèverait. |
| A2-11 | Résumés : seul le paragraphe « hypothèses » change ; les versions `agent_2/sections/main.tex__*.tex` remplacent celles de l'Agent 1 et servent de base à l'Agent 5. | C7 ; C8 (aucun chiffre nouveau). |

## Arbitrages du coordinateur sur le livrable 2 (2026-11-05)

| # | Décision | Justification |
|---|---|---|
| C10 | H4 : **« NON TRANCHÉE ; supériorité sur la baseline infirmée sur trois jeux »** (choix de l'Agent 2 retenu, pas « RÉFUTÉE »). | Le budget « fixé par le protocole » n'a jamais été fixé : la composante budgétaire est intestable (règle R1, comparateur absent), et la conclure réfutée confondrait absence de protocole et échec. Les trois infirmations sont énoncées sans atténuation ; « partiellement soutenue » est exclu. |
| C11 | Règles de décision R1–R6 : **à énoncer dans la conclusion** avant le tableau 7.1. | Elles rendent le jugement vérifiable par le jury. Elles sont présentées comme règles d'application des critères écrits, non comme critères nouveaux. |
| C12 | `chapitre2_etat_art.tex__tableau_1.3_positionnement.tex` → **entrée de l'Agent 3**, qui l'intègre à son positionnement. `limites_consolidees.tex__grandeurs_non_mesurees.tex` → retenu ; intégré par le coordinateur avec les apports des agents 4 et 5 à la section unique des limites. | Tableau 1.3 dans le périmètre de l'Agent 3 ; section des limites partagée par 2, 4 et 5. |
| Contrôle | Chiffre 0,473265 (« tout positif », holdout par scénario CICIDS2017) **recalculé par le coordinateur** : moyenne sur les 25 évaluations de 2p/(1+p), p = `test_positive_rate` de `data/processed/final_experiments_2026/cicids_holdout_multiseed_raw.csv` (Bot 0,495714 ; DDoS 0,666667 ; Infiltration 0,015748 ; PortScan 0,666667 ; WebAttacks 0,521531). | Confirmé. Utilisable dès que l'Agent 4 l'introduit dans le corps (C8). |

## Décisions de l'auteur sur le livrable 2 (2026-11-05)

| # | Décision | Application |
|---|---|---|
| C13 | **Exécuter les expériences rapides et décisives**, protocole écrit et versionné avant l'exécution. Pas d'E-HET (scénario hétérogène conjoint). | **Agent 4** : E-H4 (baselines HDFS au niveau bloc), E-H3b (modèle commun contre modèles par famille), E-H3 (routeur contre table de routage statique, si un jeu de fichiers indépendant suffisant existe ; sinon, constat de non-faisabilité argumenté). **Agent 5** : E-H5 (mémoire C contre D avec agents de fiabilité hétérogène) **et** E-CNP (Contract Net contre affectation statique, même flux de tâches), ajoutée par le coordinateur : l'auteur l'a choisie sur la foi d'une description du coordinateur qui la confondait avec E-H3 ; elle répond au lecteur 2 (§2.4). Protocoles décrits dans `agent_2/LIVRABLE_2_hypotheses.md` §8. |
| C13-proc | **Procédure obligatoire de préenregistrement** pour chaque expérience de C13 : (1) écrire `agent_<N>/protocoles/<ID>.md` (question, comparateurs, métrique, critère numérique de décision, taille, graines, artefacts attendus, analyse prévue) ; (2) l'enregistrer dans `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md` (ID, chemin, SHA-256, horodatage UTC) ; (3) `git add` de ces deux fichiers **seulement** puis `git commit -m "Protocole <ID> préenregistré"` sur la branche `revision-chantier-20261105` ; (4) exécuter seulement ensuite, sans modifier le protocole. Tout écart ultérieur est consigné comme écart, jamais en réécrivant le protocole. Artefacts dans `experiments/phase_revision_20261105/<ID>/`. | Seule forme de critère « fixé à l'avance » que le mémoire pourra revendiquer, et seulement pour ces expériences. H1–H5 restent jugées sur leur énoncé (C10, garde-fou de l'Agent 2). |
| C14 | **Question centrale et QR reformulées adoptées** (`agent_2/sections/chapitre1_introduction.tex__question_centrale_QR.tex`), ainsi que `__positionnement_l58.tex`. | Réduction de revendications : la priorisation, les traitements périodiques, les micro-lots et l'aide à l'analyste sortent de la question. |
| C15 | **E-H3 non exécutée : non-faisabilité locale retenue.** L'ensemble open-set déjà évalué comprend 68 chemins distincts (46 connus, 20 inconnus, 2 ambigus ; `revision_reports/agent_5/router_open_set/agent5_router_open_set_20261104T145601Z/sources_config.json`). L'inventaire laisse au plus 44 fichiers non utilisés sous `data/raw/` et un échantillon dans `data/samples/`, soit 45 candidats au maximum pour les 90 sources indépendantes requises ; plusieurs sont des archives, fichiers de configuration ou doublons. | Aucun corpus indépendant local ne permet la comparaison planifiée avec une table statique sans pseudo-réplication. L'ablation existante compare des classifieurs, non des politiques de routage. |
| C16 | **E-H3b et E-H4 terminés selon leurs critères préenregistrés.** E-H3b échoue à établir la non-infériorité sur `linux_auth` (borne inférieure −0,012326, marge −0,01) ; E-H4 est dominé par la baseline `template_only_mean_surprisal` (F1 0,872434 contre 0,868373, delta −0,004061). | E-H3b porte sur la spécialisation sous affectation parfaite ; il ne valide pas le routeur. E-H4 ne fixe pas le budget global de H4 : le statut de H4 reste non tranché, avec supériorité infirmée sur quatre jeux. |
| Git | Branche de travail `revision-chantier-20261105` créée le 2026-11-05 à partir de `main` (modifications non commitées conservées). Aucun autre commit que ceux des protocoles sans accord de l'auteur. | Les commits de protocoles sont autorisés par C13 ; `main` reste intact. |

## Décisions de l'Agent 3 (2026-11-05)

Détail, sources et ordre d'intégration : `agent_3/LIVRABLE_3_etat_art.md`. Bibliographie : `agent_3/references_proposees.bib`.

| # | Décision | Justification |
|---|---|---|
| A3-1 | Abandonner la lacune « aucune plateforme intégrée » ; positionner Ariel Logminer comme prototype d'intégration instrumenté. | Wazuh, Elastic Security et OpenSearch Security Analytics couvrent déjà une grande partie de la chaîne ; aucune comparaison expérimentale ne montre une supériorité du prototype. |
| A3-2 | Qualifier le contrat commun de projection locale partielle, sans conformité ECS/OCSF. | Les flux tabulaires renseignent 0/7 champs mesurés ; une enveloppe émise ne prouve ni couverture ni équivalence sémantique. |
| A3-3 | Traiter table statique, files spécialisées, groupes de consommateurs et moteur de workflow comme concurrents directs de Contract Net. | Ils fournissent affectation, acquittement ou reprise sans négociation multi-agent ; la négociation doit être évaluée par ablation. |
| A3-4 | Attribuer l'idempotence au magasin/opération et la réattribution au transport/orchestrateur. | L'ablation appariée montre que le même magasin supprime les doublons dans A et B ; la propriété n'est pas spécifique aux agents. |
| A3-5 | Classer le corrélateur comme temporel et contextuel, non causal. | Il regroupe par fenêtre et égalité de clés, sans préconditions ni modèle de scénario ; la baseline « hôte + fenêtre » le dépasse sur les incidents multi-étapes. |
| A3-6 | Qualifier registre, `dry-run` et promotion de support expérimental de gouvernance, non de MLOps validé. | Aucun cycle répété candidat → décision → déploiement → surveillance → retour arrière n'est démontré. |
| A3-7 | Absorber le tableau C12 de l'Agent 2 dans le tableau 1.3 étendu de l'Agent 3. | Les quatre restrictions C12 sont conservées et enrichies ; appliquer les deux fichiers créerait un conflit sur le même passage. |

## Décisions de l'Agent 6 (2026-11-05)

Détail et sources : `agent_6/LIVRABLE_6_reproductibilite.md` ; inventaire de soutenance : `agent_6/PREPARATION_SOUTENANCE.md`.

| # | Décision | Justification |
|---|---|---|
| A6-1 | Distinguer explicitement traçabilité, répétabilité et reproductibilité indépendante ; ne revendiquer aucune reproduction indépendante complète. | Le paquet de 54 artefacts et son manifeste établissent l'intégrité et la traçabilité, mais aucun rapport d'exécution par un tiers n'est disponible (L1 E.2, C5). |
| A6-2 | Déclaration IA : mentionner la proposition/mise en œuvre de protocoles complémentaires, l'écriture ou l'adaptation de scripts, l'exécution et l'agrégation ; conserver la responsabilité finale de l'auteur. | La déclaration actuelle minimise la contribution aux protocoles ; le remplacement reste factuel, sans chronologie narrative, conformément à C4(b). |
| A6-3 | Ne qualifier de préenregistré qu'un protocole documenté, horodaté et versionné avant l'exécution ; les campagnes `agent2` à `agent6` ne le sont pas. | Aucun document indépendant antérieur à ces exécutions n'a été retrouvé ; C4(c) interdit une revendication non prouvée. |
| A6-4 | Remplacer intégralement le chapitre 7, ce qui supprime le §7.7 pdfLaTeX et les contrôles purement éditoriaux, tout en conservant les paramètres déterminants et la frontière d'exploitation. | Le §7.7 n'a pas de valeur scientifique (L2 §2.5) et sa suppression a été transférée à l'Agent 6. |
| A6-5 | Corriger la ligne BGL G de la matrice : l'artefact exact est `agent4_bgl_contiguous_horizon_20261104T145740Z__result.json`, non le JSON `second_protocol`. | Le JSON `second_protocol` contient R0 et B--E ; G est dans l'artefact `contiguous_horizon` (`revision_reports/agent_4/PATCH_NOTES.md` §A3). |
| A6-6 | Maintenir l'inventaire campagne par campagne hors manuscrit dans `PREPARATION_SOUTENANCE.md`. | Application directe de C4(d) : transparence pour la soutenance sans raconter l'historique du chantier dans le mémoire. |

## Lots intégrés dans le manuscrit

| Lot | Contenu | Fichiers touchés | Compilation |
|---|---|---|---|
| A1-a (2026-11-05) | Agent 1 : renvoi §1.8.2 + label `sec:cicids-resultats` ; phrase du titre (p. 4) ; paragraphe et légende du tableau 4.2 (0,157744 contre 0,157827 distingués) ; §5.2 CSE-CIC ; tableau A.3 (protocole principal HDFS) ; annexe A.8 | `chapitre1_introduction.tex` l. 58 ; `chapitre2_etat_art.tex` l. 336 ; `chapitre5_resultats.tex` l. 53, 75, 81 ; `chapitre6_approfondissements_scientifiques.tex` l. 19 ; `annexes.tex` l. 91–112 et 169 | OK : 167 pages, 0 erreur, 0 référence indéfinie, 0 débordement |
| A2-a (2026-11-05) | Agent 2 : question centrale et QR resserrées ; nature des preuves ; hypothèses et règles de décision ; objectif général ; réponses QR ; bilan BGL ; statuts H1–H5 ; alignement du tableau 2.3, des micro-lots et de la priorisation | `chapitre1_introduction.tex` ; `chapitre3_modele_propose.tex` ; `chapitre6_conclusion.tex` | OK : 170 pages, 0 erreur, 0 référence/citation indéfinie, 0 débordement horizontal ; cycle complet `pdflatex` → `bibtex` → `pdflatex` ×2 |
| A5-a (2026-11-05) | Agent 5 : débit A--D avec IC, E-H5, E-CNP, résumés FR/EN/lingala, §5.7, endurance, H5 NON TRANCHÉE. Agent 3 : discussion complète. Reprise : version CICIDS2017, 0,473265, tableau des baselines par jeu, 1 048 575 lignes, H4 « quatre jeux », déclaration IA, A.2, chapitre 7 | `main.tex` ; `chapitre1_introduction.tex` ; `chapitre5_resultats.tex` ; `chapitre6_approfondissements_scientifiques.tex` ; `chapitre6_discussion.tex` ; `chapitre6_conclusion.tex` ; `chapitre7_reproductibilite_deploiement.tex` ; `limites_consolidees.tex` ; `annexes.tex` ; `declaration_ia.tex` | OK : 181 pages, cycle complet, 0 référence/citation indéfinie, 0 débordement horizontal |
| A5-b (2026-11-05) | E-CNP-LEAST-LOADED et E-H3B-STRICT-HOLDOUT : §4.5 et §4.10, discussion, limites, QR2, QR3, résumés, A.2, chapitre 7, déclaration IA | mêmes fichiers que A5-a, sauf `chapitre6_approfondissements_scientifiques.tex` | OK : 181 pages, cycle complet, 0 référence/citation indéfinie, 0 débordement horizontal |
| A4-b, A7-a (2026-11-05) | Restes de l'Agent 4 (échantillonnage, seuil, HDFS, BGL, audit CSE-CIC, circuit fermé, pistes) ; forme (bibliographie `plain-fr`, quatre décimales, anglicismes, résumés raccourcis) | `main.tex` ; chapitres 1, 3, 4, 5, 6 ; `limites_consolidees.tex` ; `annexes.tex` | OK : 181 pages, cycle complet, 0 référence/citation indéfinie, 0 débordement horizontal |
| A3-a (2026-11-05) | Agent 3 : cadres intégrés, ECS/OCSF, concurrents Contract Net, livraison/idempotence, corrélation, gouvernance, critiques CSE-CIC et tableau 1.3 ; fusion des 18 références proposées. La discussion du chapitre 6 attend les résultats C13 et E-CNP. | `chapitre2_etat_art.tex` ; `references.bib` | OK : cycle complet `pdflatex` → `bibtex` → `pdflatex` ×2 ; 0 référence/citation indéfinie, 0 débordement horizontal |

**Attention pour les agents suivants : les numéros de ligne cités dans `LIVRABLE_1_integrite.md` pour ces fichiers sont décalés après le lot A1-a.** Repérer les passages par leur texte.

## Questions ouvertes

1. ~~Retours des lecteurs~~ : fournis le 2026-11-05.
2. ~~Décision C4~~ : tranchée par l'auteur le 2026-11-05, voir C4. L'Agent 6 n'est plus bloqué.
3. ~~Q1~~ : voir C6 — **Agent 5** doit rendre un avis option A / option B.
4. ~~Q2~~ : voir C7.
5. ~~Q3~~ : voir C8.
6. **Agent 4** : `chapitre5_resultats.tex:420` (« exactement 1 048 575 lignes de données » pour les deux fichiers CSE-CIC) est contredit par l'audit `agent4_csecic_shortcut_20261104T144738Z` (16 février : 1 048 574 lignes lues, dont un en-tête répété). Artefact candidat pour l'ablation du routage : `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/family_routing_ablation.csv`. Détail : LIVRABLE_1 §6.
7. **Agent 5** : paragraphe mal placé `chapitre5_resultats.tex:621` (trace de messages de l'endurance placée dans §4.11.4) ; « refus » présentés comme observés en §4.14 et §6.3/§6.7. Détail : LIVRABLE_1 §6.

8. ~~Agent 2, Q1~~ : voir C10.
9. ~~Agent 2, Q2~~ : voir C11.
10. ~~Agent 2, Q3~~ : tranché par l'auteur, voir C14.
11. ~~Agent 2, Q4~~ : voir C12.
12. ~~Agent 2, Q5~~ : tranché par l'auteur, voir C13.
13. **Agent 4** : introduire au corps la prédiction tout positif sur chaque test (holdout par scénario CICIDS2017 : 0,473265 en moyenne, au-dessus des cinq candidats ; HDFS au niveau bloc) ; retirer ou sourcer l'« ablation du routage » (§4.7, §6.2) ; présenter E-H3 comme non faisable localement selon C15 ; avis sur E-H4 et E-HET. Détail : LIVRABLE_2 §9.
14. **Agent 5** : ajouter à §4.9 les différences appariées D − C (`experiments/phase_multi_agent/aggregated/ma_20260909T160812Z_34016__paired_memory_effects.csv`), qui sourcent la réfutation de H5 ; ajouter au corps « aucune expérience ne compare Contract Net à une affectation statique » (cité par QR2) ; partir de `agent_2/sections/main.tex__*.tex` pour les résumés. Détail : LIVRABLE_2 §9.
15. **A6-Q1 — Auteur / coordinateur** : choisir le mode de remise du dépôt (URL publique, archive privée au jury ou DOI stable). Aucun URL/DOI non confirmé ne doit être inséré dans le manuscrit.
16. **A6-Q2 — Coordinateur** : ajouter au paquet stable les scripts des campagnes complémentaires et l'artefact BGL G, puis régénérer le manifeste couvrant exactement les éléments livrés ; à défaut, conserver dans A.2 le chemin complet vers `revision_reports`.
17. **A6-Q3 — Auteur** : valider `agent_6/PREPARATION_SOUTENANCE.md` et recalculer au moins une métrique par groupe de campagne avant la soutenance ; ce document reste hors manuscrit (C4(d)).
18. ~~**A3-Q1 — Agent 4 / coordinateur**~~ : les phrases de discussion sur HDFS ont été mises à jour dans la proposition de l'Agent 3 et dans le chapitre intégré ; E-H3b et E-H3 sont également explicités dans la discussion et la conclusion.
19. **A3-Q2 — Agent 5 / coordinateur** : après E-CNP, remplacer le constat « avantage de Contract Net non établi » par le résultat préenregistré, qu'il soit favorable ou défavorable.
20. ~~**A3-Q3 — Coordinateur**~~ : tableau 1.3 de l'Agent 3 intégré à la place du fichier C12 ; 18 références fusionnées et compilées dans le lot A3-a.
21. **Reprise du 2026-11-05** : E-H3b est terminé ; la borne inférieure de l'IC apparié du delta F1 spécialisé − commun vaut −0,012326 pour `linux_auth`, sous la marge −0,01, et le critère global de non-infériorité échoue. E-H4 est terminé : F1 moyen 0,868373 pour Histogram contre 0,872434 pour la meilleure baseline simple ; le critère de marge +0,01 échoue et le résultat est dominé par la baseline. Les 17 entrées du manifeste E-H3b et les 8 entrées E-H4 ont été vérifiées. E-H3 est non faisable localement (C15). Résultats, limites et intégration au manuscrit : `agent_4/LIVRABLE_4_methodologie.md`.

## Audit de la reprise (2026-11-05, Claude Code)

| Point contrôlé | Constat |
|---|---|
| E-H3b, E-H4 : manifestes, hachages, antériorité du commit, décisions | Conformes ; rejeux identiques à l'octet (CSV de métriques). **Un rejeu reproduit aussi les bugs : voir la ligne suivante** |
| E-H3b : données | **Défauts graves, découverts ensuite** dans `scripts/run_family_routing_ablation.py` : `load_unsw` inclut `target` dans le résumé numérique (F1 spécialisé 0,9926 avec la fuite, 0,9000 sans, trois graines) ; `load_cicids` et `load_linux_auth` prennent les premières lignes (CICIDS = DDoS d'un seul fichier). **Résultat UNSW d'E-H3b invalide.** Script non modifié, car son empreinte figure au manifeste. Écart consigné au registre ; E-H3B-STRICT-HOLDOUT corrige |
| E-H3, non-faisabilité (C15) | Dénombrement confirmé : 68 chemins utilisés, 44 fichiers restants sous `data/raw/`, 1 échantillon |
| Agent 4, statut COMPLET | **Surévalué.** Comblés par la reprise : tableau des baselines par jeu (`tab:baselines-par-jeu`), version CICIDS2017, 0,473265. Le reste est traité : voir la fin de `agent_4/LIVRABLE_4_methodologie.md` |
| Conclusion, H4 | Incohérence « trois » / « quatre jeux » : **corrigée** (quatre jeux, HDFS compris depuis E-H4) |
| `chapitre5_resultats.tex`, 1 048 575 lignes | Inexact pour le 16 février : **corrigé** selon `agent4_csecic_shortcut_20261104T144738Z` (question ouverte 6) |
| C13-proc | Respectée ; C15 et C16 figurent à tort sous « Décisions de l'auteur » alors que ce sont des constats de la reprise |
| E-H3b | Le plan de l'Agent 2 prévoyait une partition par scénario ou temporelle ; le protocole utilise un split aléatoire. Divulgué dans le protocole et le chapitre 6, mais c'est une version affaiblie de la comparaison prévue |

## Décisions de l'Agent 5 (2026-11-05)

Détail : `agent_5/LIVRABLE_5_architecture.md` §5. C6 est clos : option A définitive. Protocoles commités : `658e639` (E-H5), `472d5e7` (E-CNP). Runner : `agent_5/scripts/run_e_h5_e_cnp.py`, SHA-256 `0975d87982dad3c6588be0dd7ae11d9cec5b9a8af18d032c0939989aa6313aba`.

## Prochain agent à activer

Tous les lots sont intégrés. **Plus d'agent à activer : le mémoire attend l'auteur** (conditions de `agent_8/LIVRABLE_8_verdict.md` §5). Ensuite seulement : les articles (priorité décidée par l'auteur), dont le score `0,999965`. Le mémoire ne doit plus citer E-H3b comme résultat.

## Décisions de l'auteur sur la reprise (2026-11-05)

Réponse de l'auteur aux quatre questions : « Je dis oui pour tout ».

| # | Décision | Application |
|---|---|---|
| C17 | H5 NON TRANCHÉE validée. | Déjà intégré (lot A5-a). |
| C18 | Comparer Contract Net à un répartiteur au moindre chargé. | Protocole E-CNP-LEAST-LOADED, commit `6db45dd`. |
| C19 | Bokuse à faire relire par un locuteur du lingala. | Action de l'auteur ; Claude ne peut pas la remplir. |
| C20 | Refaire E-H3b sous partition stricte. | Protocole E-H3B-STRICT-HOLDOUT, commit `8876861`. |

Résultats intégrés (lot A5-b). E-CNP-LEAST-LOADED : aucun avantage de la négociation. E-H3B-STRICT-HOLDOUT : non-infériorité non établie (CICIDS) ; E-H3b n'est plus retenue.

## Questions à l'auteur (reprise du 2026-11-05)

1. ~~Commit du manuscrit, des runners et des artefacts~~ : fait par l'auteur, commit `27deb22`, contrôlé (aucune suppression, aucun fichier sensible, manifestes valides).
2. Relecture du Bokuse par un locuteur du lingala (C19).
3. Questions déjà ouvertes : A6-Q1 (mode de remise du dépôt), A6-Q3 (validation de `agent_6/PREPARATION_SOUTENANCE.md`).
4. ~~Correction de `scripts/run_family_routing_ablation.py`~~ : faite à la demande de l'auteur ; rupture des manifestes documentée au registre.
5. ~~Documents citant `family_routing_ablation.csv`~~ : demande de l'auteur, « Retire tout ce qui conduit à une erreur ». Figures, tables, CSV et copie du script retirés ; articles 1 et 2 et documents récrits (H1 et H2 de l'article 1 remplacées par un constat de non-établissement). Conservés volontairement : registre, protocoles et artefacts d'E-H3b, qui documentent le défaut, et citations textuelles des lecteurs.
6. **Score `0,999965` (UNSW/CIC-DDoS), à décider par l'auteur :** `FINAL_EXPERIMENTAL_REPORT_FOR_LUNA.md` l'exclut pour provenance non démontrée, mais il figure encore dans les articles 1 et 2 (dont le résumé de l'article 2), la figure `fig_supervised_models_f1`, les anciennes copies LaTeX et plusieurs documents de `docs/memoire/`. Le manuscrit ne l'affiche pas. Retrait non fait : une cinquantaine de fichiers, et les articles perdraient une de leurs familles de résultats.
