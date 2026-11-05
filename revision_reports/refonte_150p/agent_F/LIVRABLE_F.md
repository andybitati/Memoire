# LIVRABLE F — Autonomie, paternité et reproductibilité

Agent F, chantier « Refonte 150 pages », 2026-11-05. Aucun `.tex` modifié.

Périmètre : L1 §E.2, §E.3, §F (intégrité) ; L2 §2.7, §3 points 3 et 10, §4 points 1 et 2.

**Garde-fou appliqué partout.** « Doser » la déclaration signifie ici la rendre *précise*, pas plus discrète. Chaque phrase proposée au §3 est vérifiable contre les traces citées au §2. Ce que les traces ne prouvent pas sur la part de l'étudiant figure entre crochets `[À CONFIRMER PAR L'AUTEUR : …]`, et seul l'auteur peut le lever. La décision C4(b) de l'auteur (`chantier_20261105/ETAT_CHANTIER.md`) demande que la déclaration ne soit « ni retirée ni atténuée » : la proposition la respecte, puisqu'elle ne retire aucun usage déclaré et ajoute ce que l'auteur a décidé.

---

## 1. Reproches du périmètre : classement et preuves

| Reproche | Classement | Preuve |
|---|---|---|
| L2 §2.7 — déclaration « honnête, mais accablante » | **Fondé quant à l'effet produit** ; la déclaration est exacte | `frontmatter/declaration_ia.tex` énumère les usages des outils dans un tableau, puis ne décrit le rôle de l'auteur qu'en une phrase générique (« L'auteur a arrêté les choix retenus… »). Ce que l'auteur a décidé n'est pas visible, d'où la lecture « délégation intégrale ». La cause est un manque de précision, pas une erreur. |
| L2 §2.7 — « le calendrier confirme cette délégation » ; campagnes préenregistrées dans les 48 heures avant la compilation | **Fondé pour les six protocoles préenregistrés** ; **partiellement fondé** pour l'ensemble | Les commits des protocoles datent du 2026-11-05 entre 12:49 et 16:39 (+0100) (`git log 22be416^..8876861`), et les artefacts de `experiments/phase_revision_20261105/` du même jour. Mais une large part des preuves citées est antérieure : référentiel A–D et multi-VM (`ma_20260909…`, commits `c86aa90`, `1b641b5` du 2026-09-09), endurance (`cnp_endurance_multivm_20260918T130822Z`), renforcement des jeux (2026-09-10), consolidation (2026-09-11). Les run_id datés relevés dans `chapters/*.tex`, `main.tex` et `frontmatter/` : 15 de septembre, 29 du 4 novembre. Les conclusions sur la négociation et la mémoire (E-CNP, E-CNP-LL, E-H5) datent bien du 5 novembre. |
| L2 §2.7 — part intellectuelle de l'étudiant non démontrable à partir du document | **Fondé** | Le PDF ne contient aucun élément qui la montre. Les traces locales (§2) en montrent une partie, mais elles ne sont pas accessibles au jury, et une partie reste inconnue. |
| L2 §2.7, §4.1 — aucun dépôt fourni (« doit contenir », sans URL, archive ni DOI) | **Fondé** | `chapitre7_reproductibilite_deploiement.tex`, section « Disponibilité des éléments… » : « Le dépôt remis avec le mémoire doit contenir… ». Un dépôt GitHub existe (`origin = https://github.com/andybitati/Memoire`), mais il n'est cité nulle part. Sa visibilité publique n'est pas vérifiée. Il s'arrête à `35da3a9` (2026-11-04) : les 13 commits du 5 novembre, dont les protocoles, ne sont pas poussés. Il contient en outre des fichiers internes (`PUBLIC_RELEASE_PLAN.md` §2). |
| L2 §3.3 — paternité des expériences clés incertaine : conçues et exécutées par des agents d'IA, au dernier moment | **Fondé pour les campagnes complémentaires** ; **à nuancer** pour l'architecture | Les protocoles E-H4, E-H3b, E-H5, E-CNP, E-CNP-LL et E-H3B-STRICT ont été rédigés par des agents (`chantier_20261105/agent_4/protocoles/`, `agent_5/protocoles/`), qui ont aussi écrit les runners et exécuté les campagnes. `agent_6/PREPARATION_SOUTENANCE.md` attribue ces tâches à Copilot SDK et à Claude Code. Leur *lancement* et leur *périmètre* sont des décisions de l'auteur, consignées : C13 (« Exécuter les expériences rapides et décisives […] Pas d'E-HET ») ; C17 à C20 (« Je dis oui pour tout », réponse à quatre propositions de Claude Code). Le prototype et les campagnes principales sont antérieurs, de mai à septembre (§2). |
| L2 §3.10, §2.2 — préenregistrement auto-certifié | **Fondé** | Le registre est local (`chantier_20261105/PROTOCOLES_PREENREGISTRES.md`). Les commits n'ont été poussés vers aucun tiers : `origin/main` = `35da3a9`. Un historique git local peut être réécrit ; rien d'extérieur n'horodate les protocoles avant leur exécution. |
| L1 §E.2 — les commits des protocoles précèdent-ils les exécutions ? | **Vérifié localement, non certifiable** | Antériorité, commit → début d'exécution, en UTC : E-H4 `5dc8cbc` 12:30:54 → 12:33 (tentative arrêtée), puis 13:06:17 (exécution retenue) ; E-H3b `3c86587` 12:31:52 → artefacts à 12:41 ; E-H5 `658e639` 14:40:46 → 14:42:28 ; E-CNP `472d5e7` 14:40:52 → 14:50:21 ; E-CNP-LL `6db45dd` 15:39:26 → 15:40:00 ; E-H3B-STRICT `8876861` 15:39:43 → 15:48:14 (heures d'exécution tirées du registre, §« Écarts »). |
| L1 §E.2 — le runner a-t-il été modifié après lecture des résultats ? | **Partiellement** | Le runner d'E-H4 a été corrigé deux fois. La seconde tentative « a consommé le test » avant de lever `KeyError`, sans émettre de score : c'est documenté au registre, mais seule la parole du registre en atteste. `scripts/run_family_routing_ablation.py` a été corrigé *après* E-H3b et E-H3B-STRICT ; les manifestes gardent l'empreinte d'origine, restituable par `git show 27deb22:…`. Aucun critère n'a été modifié. |
| L1 §E.3 — l'intégrité des artefacts ne garantit pas la reproductibilité | **Déjà traité dans le texte, fondé sur le fond** | Le ch. 7 (§ « Portée de la reproductibilité ») distingue traçabilité, répétabilité et reproductibilité indépendante, et ne revendique pas la troisième. Sans dépôt accessible, le jury ne peut atteindre ni la deuxième ni la troisième. |
| L1 §F — contrôle de provenance des scripts nécessaire ; aucune preuve de fraude | **Fondé** (recommandation) | Le §2 fournit la chronologie. Le §5 propose les questions qui permettent ce contrôle en soutenance. |

---

## 2. Chronologie et répartition des rôles

### 2.1 Chronologie (git, sessions d'assistants, artefacts)

Sources : `git log` (165 commits, tous signés `andybitati` ; 10 portent `Co-Authored-By: Claude Opus 5.5`) ; dossier `C:\Users\aoliv\.codex\sessions\2026\` (sessions OpenAI Codex, répertoire `…\Cours\TFE`) ; run_id des artefacts.

| Période | Ce qui est produit | Traces |
|---|---|---|
| Avant le 14 mai 2026 | Code de prétraitement compilé (`.pyc`) | `62b5897` (2026-05-14) ne contient que des `.pyc`. Les sources sont « récupérées » le 15 mai (`623fd56`, outil `tools/pylingual`), dans la première session Codex du projet : « Pourquoi je n'ai plus accès à mes codes .py ? ». Ce code est donc antérieur à tout usage de Codex sur le projet, mais **son auteur n'est pas attesté** par les traces. |
| 14 mai – 5 juin | Normalisation (Windows EVTX, Linux), premiers modèles (UNSW et réseau, entraînés sur Kaggle et Colab), agents collecteurs, bus Redis, API FastAPI, interface, premiers articles | Commits quotidiens ; une session Codex sur le projet presque chaque jour de commit. Demandes de l'auteur relevées, par exemple : « Je veux que mes modèles couvrent le maximum des journaux possibles », « Lis le travail et regarde les datasets Linux ajoutés », « Donne-moi les codes pour faire tourner [l'entraînement sur Kaggle] ». L'auteur exécute lui-même l'entraînement en nuage avec le code fourni. |
| 17 juillet – 3 août | Runtime « intelligent » (`intelligent_runtime`, 2026-07-17), campagne Redis sur VM, protocole HDFS/BGL, mémoire et apprentissage des agents, réentraînement, rédaction sur Overleaf | Sessions Codex. Demandes de l'auteur : « Les VM sont lancées », « Qu'en est-il de Drain et du split qui aurait dû être fait ? », « Peut-on doter nos agents de la capacité d'apprendre afin de s'améliorer ? », « Peut-on programmer un réentraînement mensuel des modèles […] ? » |
| 7 – 23 septembre | Gel de l'environnement ; campagnes principales (CICIDS, HDFS/BGL strict, multiformat, routeur, corrélation, statistiques, du 7 au 11) ; **cœur Contract Net, idempotence et utilité** (`3f2005b`, 2026-09-09) ; multi-VM (`1b641b5`) ; renforcement des jeux ; endurance (18 septembre) ; rédaction remise aux co-directeurs (15–23 septembre) | Messages de commit en anglais, typiques des sessions Codex (« experiment: freeze… / complete… »). Sessions des 7, 14, 18 et 21 septembre. Questions de l'auteur : « Concrètement, quel est l'apport de ce travail, puisque Wazuh existe déjà ? », « Quel est l'apport exact de MQTT ici ? J'ai l'impression que Redis Streams fait tout et lui de la figuration », « Sur quoi se base l'ordre de priorité ici ? » |
| 4 novembre | Révision à sept agents Codex, sur le cahier de l'auteur et 20 remarques du jury : campagnes `agent2_…` à `agent6_…` (HDFS complet, BGL second protocole, audit CSE-CIC, routeur étendu, corrélation, multiformat, Isolation Forest, saturation, panne appariée, HDFS sur deux VM) | Session orchestrateur `11/04/rollout-2026-11-04T11-10-43-*.jsonl` ; `revision_reports/agent_1…7/`. Question de l'auteur à l'ouverture : « Peut-on rendre ces agents plus autonomes que ce qu'ils sont ? » ; puis : « U = 0.30C + … : cette formule est-elle toujours d'actualité malgré les changements opérés ? » |
| 5 novembre | Chantier à huit agents (Codex, Copilot SDK, Claude Code) : six protocoles versionnés puis exécutés ; intégration ; relecture | `chantier_20261105/` ; décisions C1 à C20 ; commits de 12:49 à 18:22. |

### 2.2 Répartition par catégorie

| Catégorie | Ce que les traces attestent | Ce que seul l'auteur peut déclarer | Inconnu |
|---|---|---|---|
| **Problématique, objectifs, choix des sources et de l'environnement** | Les demandes adressées aux assistants fixent les orientations : couverture maximale des journaux, ajout des jeux Linux, agents capables d'apprendre, réentraînement, place de MQTT, positionnement face à Wazuh et au marché. L'auteur exécute l'entraînement sur Kaggle et Colab, et démarre les VM. Il pose la question du découpage HDFS/BGL (21 juillet). | Origine du sujet ; choix initial des jeux de données ; installation et configuration des VM. `[À CONFIRMER PAR L'AUTEUR]` | Part des suggestions des assistants dans ces choix. |
| **Conception du prototype et de l'architecture** | Les briques ont été écrites dans des sessions d'assistant, sur demande de l'auteur. Contract Net, l'idempotence et l'utilité arrivent le 9 septembre dans un commit au style Codex (`3f2005b`). | Qui a conçu l'architecture d'ensemble (agents spécialisés, bus, rôle du coordinateur) et la forme de l'utilité. `[À CONFIRMER PAR L'AUTEUR]` | Auteur du code de prétraitement d'avant mai. Lignes écrites à la main. |
| **Conception des protocoles complémentaires** (4–5 novembre) | Rédigés par des agents d'IA : `agent_4/protocoles/`, `agent_5/protocoles/`, `revision_reports/agent_<N>/`. **Décidés par l'auteur** : C13 (exécuter des expériences « rapides et décisives » versionnées avant exécution, sans scénario conjoint E-HET) ; C18 (comparer au moindre chargé) ; C20 (refaire E-H3b sous partition stricte) ; C17 (statut de H5). C18 et C20 répondent à des propositions de Claude Code. | Contribution de l'auteur à la *conception* de ces protocoles, au-delà de leur approbation. Les traces n'en montrent pas. | — |
| **Écriture des scripts** | Majoritairement produite dans des sessions d'assistant (messages de commit, `Co-Authored-By`, scripts sous `revision_reports/agent_*/scripts/`). Tous les commits sont signés par l'auteur, ce qui ne dit pas qui a écrit le code. | Scripts ou parties de scripts écrits ou modifiés par l'auteur. `[À CONFIRMER PAR L'AUTEUR]` | Proportion exacte. |
| **Exécution** | Campagnes de septembre et de novembre lancées par les assistants dans l'environnement de l'auteur, sur sa machine et ses VM. Entraînements de mai sur Kaggle et Colab lancés par l'auteur. | — | — |
| **Interprétation et décisions** | Pour les protocoles versionnés, les conséquences sur les hypothèses sont écrites dans les protocoles avant exécution, par les agents. L'auteur a validé les statuts (C17), retiré les résultats issus du script fautif (« Retire tout ce qui conduit à une erreur »), décidé de présenter un seul travail (C4) et refusé E-HET (C13). | Interprétation personnelle des résultats, à démontrer en soutenance (§5). | — |
| **Rédaction** | Rédaction et restructuration assistées (ChatGPT et Codex, puis Codex, Copilot et Claude Code en novembre). Rédaction sur Overleaf en juillet. Modifications manuelles ponctuelles signalées par l'auteur (« j'ai fait une petite modification à l'introduction », 16 septembre). | Passages rédigés par l'auteur lui-même. `[À CONFIRMER PAR L'AUTEUR]` | Proportion. |

**Constat sans détour.** Les traces montrent un auteur qui *pilote* : il fixe les objectifs, pose les questions critiques, décide et arbitre. Elles montrent aussi que l'écriture du code, la conception détaillée des protocoles complémentaires, leur exécution et une grande part de la rédaction ont été assistées ou effectuées par des outils, et ce **depuis mai 2026**, pas seulement en novembre. Une déclaration qui ferait de l'étudiant le concepteur des protocoles E-H5, E-CNP ou E-CNP-LL serait fausse.

---

## 3. Déclaration IA proposée (remplace `frontmatter/declaration_ia.tex`)

### 3.1 Principes du dosage

1. Remplacer le tableau « outil → usages », qui se lit comme une liste d'aveux, par un tableau « activité → rôle de l'auteur / rôle des outils ». Il ne retire aucun usage et rend visibles les décisions de l'auteur.
2. Énoncer une seule fois ce que les outils ont fait. La version actuelle mentionne l'exécution des campagnes trois fois.
3. Donner une phrase de calendrier, sans chercher à le cacher. Les dates restent lisibles dans les artefacts et le dépôt, et les taire après le remplacement des run_id par des étiquettes (Agent E) passerait pour une dissimulation. Cette phrase nuance C4(a) (« sans dates d'exécution ») : **décision de l'auteur requise**.
4. Ne rien affirmer sur la part de l'étudiant que les traces ne prouvent pas : tout cela reste entre crochets jusqu'à ce que l'auteur l'atteste.
5. Supprimer la mention des « préfixes `agent2` à `agent6` » : ces préfixes disparaissent du corps (Agent E). La remplacer par « les campagnes de contrôle complémentaires ».

### 3.2 Texte proposé

```latex
\chapter*{Déclaration relative à l'utilisation d'outils d'intelligence artificielle}
\addcontentsline{toc}{chapter}{Déclaration relative à l'utilisation d'outils d'intelligence artificielle}

Des outils d'intelligence artificielle générative ont été utilisés tout au long du travail,
de mai à novembre 2026 : ChatGPT et OpenAI Codex (modèle GPT-5, OpenAI), Copilot SDK dans
Visual Studio Code, et Claude Code (modèle Claude Opus, Anthropic). Ils ne sont la source
d'aucune affirmation scientifique du mémoire ; les références renvoient aux publications,
normes, documentations et jeux de données consultés.

\section*{Répartition des rôles}

\begin{table}[H]
\centering
\small
\begin{tabularx}{\textwidth}{p{0.22\textwidth}XX}
\toprule
\textbf{Activité} & \textbf{Auteur} & \textbf{Outils} \\
\midrule
Problématique et objectifs &
Choix du sujet, des objectifs et des familles de journaux ; questions de positionnement
(apport face aux plateformes existantes, rôle de chaque composant). &
Analyse documentaire et reformulation sur demande. \\
Environnement &
Mise en place et exploitation des machines virtuelles, de Redis et des entraînements
en nuage. [À CONFIRMER PAR L'AUTEUR : installation et configuration des VM] &
Scripts de déploiement et de lancement. \\
Prototype &
Spécification des capacités attendues et validation du fonctionnement.
[À CONFIRMER PAR L'AUTEUR : conception de l'architecture d'ensemble ; parties du code
écrites par l'auteur] &
Écriture et adaptation d'une large part du code et des tests. \\
Campagnes principales &
Décision des expériences à mener et des jeux à employer. &
Écriture des scripts ; exécution dans l'environnement de l'auteur ; agrégation. \\
Campagnes complémentaires &
Décision de les mener, choix des comparateurs retenus (répartiteur au moindre chargé,
partition stricte) et exclusion du scénario conjoint ; validation des conclusions. &
Proposition et rédaction des protocoles, des critères et des scripts ; exécution ;
analyse selon les règles fixées avant exécution. \\
Rédaction &
Plan, arbitrages et contenu final. [À CONFIRMER PAR L'AUTEUR : passages rédigés
directement] &
Structuration, reformulation, contrôles de cohérence, figures et tableaux tirés des
artefacts. \\
\bottomrule
\end{tabularx}
\end{table}

Le prototype et les campagnes principales ont été réalisés de mai à septembre 2026. Les
campagnes complémentaires, qui contrôlent les conclusions par des comparateurs plus
simples, ont été conçues et exécutées en novembre 2026, après une première lecture du
manuscrit ; elles sont postérieures aux résultats qu'elles éprouvent. Six d'entre elles
(E-H3b, E-H3b stricte, E-H4, E-H5, E-CNP et E-CNP au moindre chargé) ont fait l'objet d'un
protocole versionné dans le dépôt avant leur exécution ; cette antériorité est attestée
par l'historique du dépôt et non par un registre externe. Les autres campagnes de contrôle
ne sont pas présentées comme préenregistrées.

\section*{Vérification et responsabilité}

Chaque valeur numérique retenue provient d'un fichier CSV ou JSON identifié dans la matrice
résultats--preuves, et non d'une réponse textuelle d'un outil. Les descriptions du
comportement ont été confrontées au code et aux journaux d'exécution ; les résultats
défavorables ont été conservés, et ceux qu'un défaut de script invalidait ont été retirés.
Les empreintes SHA-256 attestent l'intégrité des artefacts, non l'exactitude des calculs ;
aucune reproduction indépendante par un tiers n'a été réalisée.

L'auteur a arrêté les choix présentés, en assume les résultats et l'interprétation, et
s'engage à justifier en soutenance chaque protocole, chaque script cité et chaque valeur
retenue.
```

### 3.3 Points à faire confirmer par l'auteur avant intégration

1. Les quatre crochets ci-dessus : chacun reste en crochets, ou est retiré avec sa ligne, tant que l'auteur ne l'a pas attesté. Toute affirmation ajoutée doit pouvoir être soutenue devant le jury.
2. La phrase de calendrier, qui nuance C4(a) : recommandée, car le calendrier est déjà connu du lecteur 2 et visible dans les artefacts.
3. La dernière phrase (« s'engage à justifier ») n'a de valeur que si l'auteur prépare le §5.

---

## 4. Dépôt

### 4.1 Contenu minimal

Code (`src/logminer/`, `tests/`) ; scripts ayant produit les artefacts cités (`scripts/` et `revision_reports/agent_*/scripts/`, `chantier_20261105/agent_4|5/scripts/` et les runners) ; configurations (`experiments/*/configs/`, `agent_policy.json`) ; protocoles et registre (`agent_4/protocoles/`, `agent_5/protocoles/`, `PROTOCOLES_PREENREGISTRES.md`) ; artefacts et manifestes (`experiments/phase_*`, avec `MANIFEST_SHA256.csv` et `manifests/*.json`) ; graines (inscrites dans les protocoles et les `summary.json`) ; partitions (listes d'identifiants de blocs ou de lignes, ou script déterministe qui les régénère) ; environnement (`requirements*.txt`, Dockerfile, `docker-compose.redis.yml`, versions de Python 3.11 hôte, Debian 3.13, Ubuntu 3.8) ; matrice résultats–preuves ; instructions de téléchargement et de vérification des données.

### 4.2 Existant

- Plan de publication détaillé : `revision_reports/agent_7/public_release/PUBLIC_RELEASE_PLAN.md`, avec structure, exclusions, données sensibles et procédure Zenodo. On y trouve aussi `README_public.md`, `LICENSE` (MIT), `DATA_LICENSES.md`, `CITATION.cff` et `.zenodo.json`.
- Artefacts suivis par git : `experiments/` (544 fichiers ; manifestes SHA-256 de `phase_revision_20261104`, 54 entrées vérifiées, et des six campagnes de `phase_revision_20261105`).
- Aucun secret dans l'historique (`git log --all -- .secrets` est vide).

### 4.3 Manquant

- Les 13 commits du 5 novembre ne sont pas poussés (`origin/main` = `35da3a9`).
- Copie publique sélective non construite. Le dépôt de travail contient des notes internes, les rapports de révision et `docs/` ; le plan prévoit de les exclure.
- Artefacts cités hors de `experiments/`, absents ou ignorés par git : par exemple `correlation_synthetic_summary.json` (`PUBLIC_RELEASE_PLAN.md` §4).
- Licences CIC et UNSW non vérifiées (`[À VÉRIFIER PAR L'AUTEUR]` dans `DATA_LICENSES.md`).
- Décision sur les journaux Windows de la machine personnelle (nom d'utilisateur, nom d'hôte) : le plan recommande de les exclure.
- Le générateur de figures lit d'anciens chemins (trois lignes à modifier, `PUBLIC_RELEASE_PLAN.md` §4).

### 4.4 Données non redistribuables ou à ne pas redistribuer

Bruts CICIDS2017, CSE-CIC-IDS2018 et UNSW-NB15 : conditions des éditeurs, à vérifier. Le dépôt donne la source, la version et la procédure de vérification. Les bruts HDFS et BGL (Loghub, CC BY 4.0, DOI 10.5281/zenodo.8196385) sont redistribuables, mais trop volumineux (`data/raw/` ≈ 23,4 Go) ; on publie un lien et des empreintes. Les journaux personnels sont à exclure.

### 4.5 Options (décision A6-Q1 de l'auteur) et texte du ch. 7 pour chacune

Le texte remplace le premier paragraphe de la section « Disponibilité des éléments et vérification externe ». Le second paragraphe, sur l'absence de reproduction par un tiers, est conservé.

**Option 1 — Archive Zenodo avec DOI (recommandée).** C'est la seule option qui fixe un horodatage tiers et un contenu immuable.
> Le code du prototype, les scripts, les configurations, les protocoles versionnés, les artefacts et leurs manifestes SHA-256 sont archivés sous le DOI [DOI]. Les jeux de données publics n'y sont pas redistribués ; l'archive donne pour chacun la source, la version attendue, l'empreinte des fichiers utilisés et la procédure de préparation. La matrice résultats--preuves (annexe~A) renvoie à des chemins relatifs à la racine de cette archive.

**Option 2 — Dépôt GitHub public, sans DOI.**
> Le code, les scripts, les configurations, les protocoles versionnés et les artefacts, avec leurs manifestes SHA-256, sont publiés à l'adresse [URL], dans l'état correspondant à l'étiquette [vX.Y] (commit [hash]). […mêmes deux dernières phrases…]

**Option 3 — Archive privée remise au jury.**
> Une archive contenant le code, les scripts, les configurations, les protocoles versionnés, les artefacts et leurs manifestes SHA-256 est remise au jury avec le mémoire (empreinte SHA-256 de l'archive : [empreinte]). […mêmes deux dernières phrases…]

Pour les trois options, il faut ajouter dans le ch. 5 (« Validité scientifique »), à l'endroit qui traite du préenregistrement, une phrase qui reste vraie quoi qu'il arrive : « L'antériorité des protocoles est attestée par l'historique du dépôt ; elle n'a pas été déposée auprès d'un registre externe avant exécution. » Pousser ou archiver aujourd'hui horodate l'état actuel, mais ne prouve pas rétroactivement l'antériorité : il ne faut pas laisser entendre le contraire.

### 4.6 Invérifiable sans dépôt

Toutes les valeurs du mémoire, faute de pouvoir les recalculer depuis les CSV et JSON ; l'antériorité des protocoles ; l'identité entre le code décrit (utilité, Contract Net, idempotence) et le code exécuté ; les partitions et les graines effectives ; l'absence de fuite d'étiquette dans les campagnes non auditées.

Même avec le dépôt, une partie reste invérifiable : l'antériorité des protocoles vis-à-vis d'un tiers ; le déroulé exact des tentatives techniques non conservées (la seconde tentative d'E-H4) ; la part personnelle de l'étudiant.

---

## 5. Annexe de défense (document de préparation, **hors manuscrit**)

**Pourquoi hors manuscrit.** C4(d) l'a déjà décidé. Une annexe « réponses aux questions du jury » dans le mémoire ajouterait des pages, alors que l'objectif est −30, et ne prouverait rien : la maîtrise se démontre oralement. L'insérer lui donnerait l'apparence d'un texte préparé, ce qui aggraverait le reproche L2 §4.2. À compléter dans `agent_6/PREPARATION_SOUTENANCE.md`, nouvelle section « Justifications personnelles », que l'auteur rédige **de sa main**.

| Objet | Questions probables du jury | Ce que l'étudiant doit justifier seul | Fichiers à relire |
|---|---|---|---|
| **E-H5** (mémoire) | Pourquoi une confiance déclarée volontairement fausse ? Pourquoi p = 0,3 ; 0,6 ; 0,9 ? Le gain à 0,9 a-t-il un sens opérationnel ? Pourquoi un critère conjoint, échec et débit ≥ 0,95 ? Pourquoi l'indice de Jain se dégrade-t-il ? Pourquoi trente graines, et que représente une graine ? | La mémoire n'a d'effet que si la confiance déclarée est fausse ; c'est le scénario qu'elle doit corriger, donc un test de sa *raison d'être*, pas une configuration complaisante. Ce que veut dire « gain conditionnel ». Pourquoi H5 reste NON TRANCHÉE (la priorisation n'est pas mesurée). Le lissage de Laplace et la mise à jour en mode actif seulement. | `agent_5/protocoles/E-H5-MEMORY-RELIABILITY.md` ; `agent_5/scripts/run_e_h5_e_cnp.py` ; `src/logminer/agents/intelligent_runtime.py` ; `experiments/phase_revision_20261105/E-H5-MEMORY-RELIABILITY/summary.json` |
| **E-CNP** (contre table statique) | Pourquoi le contraste C − static n'isole-t-il pas la négociation ? Que mesure s0 ? | La table ignore la charge et C n'a pas de mémoire ; le gain accompagne l'étalement dû au terme de charge. C'est l'écart d'interprétation consigné au registre, et c'est lui qui a motivé E-CNP-LL. | `agent_5/protocoles/E-CNP-STATIC-ASSIGNMENT.md` ; `PROTOCOLES_PREENREGISTRES.md` (§ « Écarts ») ; `E-CNP-STATIC-ASSIGNMENT/summary.json` |
| **E-CNP-LL** (contre moindre chargé) | Pourquoi Contract Net est-il plus lent dans les quatre scénarios ? Le répartiteur est-il avantagé ? Pourquoi de nouvelles graines ? Contract Net est-il donc inutile ? Que dit la littérature (power of two choices, JSQ) ? | Le répartiteur lit l'état directement, dans un seul processus, sans coût de message ni information périmée : c'est un avantage de construction. Le résultat vaut dans ce cadre et ne s'étend pas à un système distribué. Ce qu'il faudrait pour trancher ailleurs. Les pertes finales de tâches sous Contract Net (agents occupés exclus du repli, L1 §C.3). | `agent_5/protocoles/E-CNP-LEAST-LOADED.md` ; `agent_5/scripts/run_e_cnp_least_loaded.py` ; `src/logminer/agents/contract_net.py` ; `E-CNP-LEAST-LOADED/summary.json` |
| **Fonction d'utilité** | D'où viennent les poids ? Pourquoi M = 1 et A = L ? Pourquoi le seuil de refus est-il inactif ? En quoi est-ce « intelligent » ? | L'origine des poids : choix, ou proposition acceptée, `[À CONFIRMER PAR L'AUTEUR]`. L'utilité est un *classement* à poids fixes, non appris, et elle se réduit en pratique dans les campagnes Redis. Pourquoi le mot « intelligent » n'est pas défendu. La question que l'auteur a lui-même posée le 4 novembre (« cette formule est-elle toujours d'actualité ? ») est un bon point d'appui. | `chapters/spec_utilite.tex` ; `src/logminer/agents/contract_net.py` ; `experiments/phase_multi_agent/configs/agent_policy.json` ; `scripts/logminer_redis_cnp_agent.py` (profils de confiance) |
| **Découpage HDFS/BGL** | Pourquoi un ordre chronologique par première apparition des blocs ? Pourquoi un parseur ajusté sur 6 000 blocs ? Pourquoi la prévalence diffère-t-elle entre validation et test ? Pourquoi cinq graines donnent-elles la même matrice ? Pourquoi BGL est-il dégénéré (entraînement entièrement INFO) ? Pourquoi le protocole G a-t-il été conçu après coup ? | La question du découpage, que l'auteur a posée le 21 juillet (« Qu'en est-il de Drain et du split ? »). La raison du 60/20/20 chronologique. Pourquoi des graines identiques ne sont pas des réplications. Pourquoi le résultat BGL se réduit à la règle de sévérité. | `chapters/chapitre5_resultats.tex` (sections HDFS et BGL) ; `agent_4/protocoles/E-H4-HDFS-BLOCK-BASELINES.md` ; `experiments/phase_revision_20261104/agent_2_hdfs/`, `agent_4_bgl/` |

Exercice à faire avant la soutenance, déjà prévu par `PREPARATION_SOUTENANCE.md` §3 : relancer seul une campagne par groupe (§6) et recalculer à la main une métrique depuis le CSV.

---

## 6. Reproductibilité

### 6.1 Formulation à retenir, à placer une seule fois au ch. 7

> Les empreintes SHA-256 établissent que les artefacts n'ont pas changé depuis leur production ; elles n'établissent pas que les calculs sont exacts. Les campagnes ont été réexécutées par l'auteur dans son environnement ; aucune n'a été reproduite par un tiers.

Point à vérifier par l'auteur avant de garder « réexécutées » : les rejeux connus (E-H3b, E-H4, identiques à l'octet) ont été faits par Claude Code dans son environnement (`ETAT_CHANTIER.md`, « Audit de la reprise »). Sauf rejeu personnel de l'auteur, il faut écrire : « Certaines campagnes ont été rejouées dans l'environnement de l'auteur, à l'identique ».

### 6.2 Reproduction ciblée proposée au jury

Courte, sans VM, sur un poste Windows ou Linux disposant de Python, à partir de l'archive :
1. Vérifier les manifestes : recalculer le SHA-256 de chaque fichier de `experiments/phase_revision_20261105/*/MANIFEST_SHA256.csv`.
2. Recalculer une valeur sans rien exécuter : le F1 « tout positif » du holdout par scénario CICIDS2017, 0,473265 = moyenne de 2p/(1+p) sur `test_positive_rate` (méthode consignée dans `ETAT_CHANTIER.md`, « Contrôle »).
3. Relancer E-CNP-LEAST-LOADED, environ 8 minutes (15:40:00 → 15:47:39 UTC) : `python revision_reports/chantier_20261105/agent_5/scripts/run_e_cnp_least_loaded.py`, puis comparer `summary.json` à l'archive.
4. Relancer E-H5, environ 8 minutes : `run_e_h5_e_cnp.py E-H5`.
5. Avec les données HDFS téléchargées depuis Loghub : relancer E-H4, environ 11 minutes ; `run_e_h4_hdfs_baselines.py`.
6. Pour E-H3B-STRICT : partir du commit `27deb22`, qui contient le chargeur d'origine (registre, dernière ligne des écarts).

Avant de proposer cette procédure, l'auteur doit l'avoir exécutée lui-même sur une copie propre de l'archive, et la documenter dans le README public.

---

## 7. Effet sur le volume

| Élément | Effet |
|---|---|
| Déclaration IA (§3) : tableau à trois colonnes à la place de deux, paragraphes fusionnés | Environ +0,25 page (1,5 → 1,75) |
| Ch. 7, disponibilité (§4.5) : texte de même longueur | 0 |
| Ch. 7, formulation unique de la reproductibilité (§6.1), qui remplace les mentions dispersées | Environ −0,25 page, à confirmer avec l'Agent E |
| Phrase sur l'antériorité au ch. 5 | +2 lignes |
| Annexe de défense | 0 (hors manuscrit) |
| **Net** | **≈ 0 page** |

---

=== PASSATION ===
Agent : F — Autonomie, paternité et reproductibilité
Statut : terminé
Livrable : `revision_reports/refonte_150p/agent_F/LIVRABLE_F.md`
Décisions requises de l'auteur :
(1) attester ou retirer chaque `[À CONFIRMER PAR L'AUTEUR]` de la déclaration ;
(2) accepter la phrase de calendrier, qui nuance C4(a) ;
(3) choisir le mode de dépôt (A6-Q1 ; Zenodo recommandé), pousser les 13 commits non poussés, construire la copie publique selon `PUBLIC_RELEASE_PLAN.md` ;
(4) rédiger de sa main les justifications du §5 dans `PREPARATION_SOUTENANCE.md` ;
(5) avant d'écrire « réexécutées par l'auteur », vérifier qu'il a lui-même rejoué au moins une campagne.
Pour l'intégrateur :
- la déclaration et le ch. 7 sont neutres en volume ;
- « préfixes agent2–agent6 » disparaît de la déclaration en même temps que les identifiants (Agent E) ;
- la phrase « antériorité attestée par l'historique du dépôt, non par un registre externe » doit figurer une seule fois (ch. 5), en cohérence avec l'Agent C.
Points de vigilance :
- ne jamais attribuer à l'étudiant la conception des protocoles complémentaires : les traces montrent qu'ils ont été rédigés par des agents et décidés par l'auteur ;
- les citations de sessions du §2 viennent de `C:\Users\aoliv\.codex\sessions\` : elles sont réservées à l'auteur et ne doivent pas être publiées ;
- hors périmètre, signalé par l'Agent A : E-H3B-STRICT utilise le chargeur d'origine (empreinte `8de67257…`), à traiter par l'Agent C.
=== FIN PASSATION ===
