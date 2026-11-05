# LIVRABLE B — Rigueur expérimentale et comparateurs manquants

Agent B, chantier « Refonte 150 pages », 2026-11-05. Aucune expérience lancée, aucun `.tex`, code ni artefact modifié. Trois recalculs en lecture seule sur des artefacts existants ont été faits ; leurs scripts et sorties sont dans ce dossier :

- `sensibilite_bonferroni.py` → `sensibilite_bonferroni_sortie.txt` (décisions E-H5, E-CNP, E-CNP-LL sous correction de Bonferroni) ;
- `recalcul_cicids_ponderation.py` → `recalcul_cicids_ponderation_sortie.txt` (F1 micro, F1 sans Infiltration, prévalences de test) ;
- `pertes_par_bras.py` → `pertes_par_bras_sortie.txt` (échecs finaux par bras et par nombre de coordinateurs).

Abréviations : « ch. 4 » = `chapitre5_resultats.tex` ; « intro » = `chapitre1_introduction.tex` ; « concl. » = `chapitre6_conclusion.tex`. Les passages sont repérés par leur texte.

---

## 1. Classement des reproches du périmètre

| # | Reproche | Classement | Preuve et commentaire |
|---|---|---|---|
| B1 | Modèles battus par des règles simples (L1 §B.1 ; L2 §2.2) | **Fondé, déjà rapporté** | Tableau `tab:baselines-par-jeu` (ch. 4, « Comparaison aux règles simples ») : aucune ligne où le modèle dépasse la règle. Le texte le dit (« aucun résultat principal ne dépasse sa règle simple »). Reste à corriger le statut de H4 (§4 ci-dessous). |
| B2 | Spécialisation non généralisable, condition oracle (L1 §B.2) | **Fondé, déjà rapporté** | ch. 4, `sec:e-h3b` : « Le modèle spécialisé reçoit la famille correcte ; cette condition oracle ne teste donc pas le classifieur de routage » ; « Spécialiser le modèle ne corrige donc pas la fragilité ». Aucune action, hormis la phrase sur les « données corrigées » (B6). |
| B3 | Benchmark A–D sur microtâches (L2 §2.2) | **Fondé** | Tableau `tab:benchmark-debit` : 72 657 à 84 728 tâches/s pour A. Le texte reconnaît que « le coût d'orchestration domine entièrement le travail utile » mais renvoie à `sec:e-cnp`, qui utilise encore des tâches synthétiques de 2 ms (`SERVICE_SEC = 0.002`, `run_e_h5_e_cnp.py`). Aucune tâche d'inférence réelle n'est comparée entre architectures. Protocole P3 (§2). |
| B4 | Comparateur H2 « agents sans idempotence » non exécuté (L2 §2.2, §3) | **Fondé** | Concl., tableau `tab:statut-hypotheses`, ligne H2 : « la même exécution à agents n'a pas été réalisée ». Dans `revision_reports/agent_3/run_paired_failure_abcd.py`, `run_cnp` affecte toujours le magasin (`agent.idempotency_store = store`). Protocole P2. |
| B5 | Comparateur H3 « chaîne sans routage » non exécuté ; « Loghub fournit plus de 16 sources » (L2 §2.2) | **Fondé pour l'absence ; partiellement fondé pour l'argument Loghub** | L'absence est déclarée (ligne H3 du même tableau). Le motif invoqué (« 90 sources ») appartient en réalité à E-H3, qui compare le routeur à une table statique (`agent_4/LIVRABLE_4_methodologie.md`, l. 7 et 42). Le comparateur de H3, une chaîne sans routage, n'exige pas 90 sources : on peut le mener sur le corpus open-set existant. Inventaire local (`data/raw/Datasets/`) : seuls HDFS (`HDFS_1`), BGL et `Linux_2k.log` relèvent de Loghub ; les autres jeux Loghub ne sont pas présents et devraient être téléchargés. Protocole P1. |
| B6 | « mêmes données corrigées » incohérent avec l'usage des CSV non corrigés (L2 §2.2) | **Fondé (formulation)** | ch. 4, `sec:e-h3b` : « sur les mêmes données corrigées ». Le contexte vise le chargement sans fuite (E-H3B-STRICT), non les corrections d'Engelen et al. ; la section CICIDS dit l'inverse (« sans les corrections proposées par Engelen et al. »). Remplacer par : « sur les mêmes données, chargées sans la fuite d'étiquette ». |
| B7 | Seuils par défaut, échantillons plafonnés, pondération d'Infiltration (L2 §2.2) | **Fondé pour le seuil et le plafonnement ; inexact quant à l'effet d'Infiltration** | Seuil et plafonds : divulgués (ch. 4, « Comparaison de cinq candidats »). Mais le recalcul (`recalcul_cicids_ponderation_sortie.txt`) montre que **les plafonds fixent la prévalence de test** (0,5 pour DDoS et PortScan ; 0,3295 Bot ; 0,0079 Infiltration ; 0,3528 WebAttacks), donc le F1 de la prédiction tout positif (2p/(1+p)) : 0,4733 en est une conséquence arithmétique. L'égal poids d'Infiltration **favorise les modèles** et non la règle : sans Infiltration, tout positif 0,5876 contre LR 0,1989 ; en F1 micro, tout positif 0,5491 contre au mieux 0,3488 (RF). La conclusion « aucun candidat ne dépasse tout positif » est donc robuste à la pondération. §3. |
| B8 | Contract Net sans avantage face au moindre chargé (L1 §C.1) | **Fondé, déjà rapporté** | ch. 4, `sec:e-cnp-moindre` : « l'avantage propre de la négociation n'est pas établi ». Le biais du comparateur est déjà écrit (« Cette comparaison avantage le répartiteur par construction… ») ; paragraphe consolidé proposé au §5. |
| B9 | Pertes de tâches sous Contract Net, analyse causale exigée (L1 §C.3) | **Fondé ; cause établie à partir du code et des artefacts, confirmation instrumentée à faire** | §5. |
| B10 | Mémoire bénéfique seulement à p = 0,9, confiance volontairement erronée (L1 §C.2 ; L2 §2.4) | **Fondé, déjà rapporté** ; formulation à resserrer | ch. 4, `sec:e-h5` : « La mémoire n'apporte donc un bénéfice net que lorsque la déclaration de confiance est très éloignée de la fiabilité réelle ». Manque une justification du choix des niveaux 0,3, 0,6 et 0,9 (§6). |
| B11 | Distribution non démontrée (L1 §C.4 ; L2 §2.2 : 1,23 %, 100 % sur debian-alpha, trace tronquée, 0,5 tâche/s) | **Fondé, déjà rapporté** | ch. 4, `sec:cnp-multivm` : « La seconde machine n'augmente donc pas la capacité observée » ; « pas un partage effectif de la charge » ; trace « exclus[e] des conclusions » ; endurance « très éloignée » de la capacité. La dispersion sur quatre paragraphes est à réduire (§6). |
| B12 | Aucune correction pour comparaisons multiples (L2 §2.2) | **Fondé (aucune correction), sans effet sur les décisions** | Les runners utilisent un IC de Student à 95 % non ajusté (`T_CRITICAL_95`, `run_e_h5_e_cnp.py`). Le recalcul sous Bonferroni (k = 3 pour E-H5, 8 pour E-CNP, 4 et 12 pour E-CNP-LL) reproduit d'abord exactement les décisions publiées à α = 0,05, puis montre qu'**aucune décision ne change** (`sensibilite_bonferroni_sortie.txt`). |
| B13 | Mesures corrélées traitées comme indépendantes dans E-H3B-STRICT (L1 §E.1) | **Déjà traité en grande partie** | `agent_4/run_e_h3b_strict.py`, fonction de synthèse : l'IC est calculé sur les moyennes par graine et par famille (`per_seed = pivot.groupby(["seed", "family"])…mean()`), soit n = 5 et non 18 × 5. Il faut l'écrire dans le texte (une phrase) et préciser que les cinq graines partagent les mêmes fichiers sources. |
| B14 | Graines ≠ environnements indépendants (L1 §E.1) | **Fondé** | À déclarer dans la section unique des limites : les 30 graines font varier la charge générée et les tirages d'échec, pas la machine, le réseau ni le système. |

---

## 2. Protocoles à exécuter avant la soutenance

Chaque protocole est rédigé pour être commité **avant** exécution dans `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md`, selon la procédure déjà suivie (empreinte SHA-256 du protocole, du runner et des sources importées ; refus du runner hors mode `--smoke` si le protocole n'est pas inscrit). Les durées sont des estimations de l'Agent B, non des mesures.

### P1 — E-H3-NOROUTE : chaîne avec routage contre chaîne sans routage (H3)

**Question.** À corpus identique, le routage par famille réduit-il les exécutions incompatibles sans accroître l'erreur prédictive, par rapport à la même chaîne sans routage ?

**Bras.**
- R : routeur open-set gelé (seuil inchangé, `run_router_open_set_consolidation.py`), puis modèle de la famille attribuée ; un fichier rejeté n'est pas exécuté.
- N : aucun routage ; chaque fichier est envoyé au **modèle commun** d'E-H3B-STRICT (17 variables, mêmes hyperparamètres ; `agent_4/run_e_h3b_strict.py`, état du commit à figer).

**Données.** Les 66 fichiers du corpus open-set (46 connus, 20 inconnus ; l'artefact `agent5_router_open_set_20261104T145601Z` en compte 68 avec 2 ambigus, exclus a priori). Option d'extension : jeux Loghub absents localement (à télécharger ; chaque jeu = une source). L'unité statistique est le **fichier** ; les fichiers dérivés d'un même jeu forment une grappe (CICIDS2017, UNSW, Linux/auth, HDFS, BGL, etc.).

**Définition fixée a priori.** Une exécution est *incompatible* si moins de 9 des 17 variables d'entrée du modèle qui la reçoit sont renseignées sans imputation, ou si la famille réelle du fichier n'appartient pas aux familles d'entraînement de ce modèle. Taux d'erreur de référence : F1 du bras N sur les fichiers connus étiquetés.

**Métrique primaire.** Différence appariée par fichier du taux d'exécutions incompatibles (R − N), IC à 95 % par bootstrap **par grappe** (10 000 réplications, graine fixée).

**Métrique secondaire.** F1 sur les fichiers connus étiquetés, R − N, marge de non-infériorité −0,01 (même marge qu'E-H3B-STRICT).

**Règle de décision.** H3 soutenue si la borne supérieure de l'IC du taux d'incompatibilité est < 0 **et** la borne inférieure de l'IC du ΔF1 est ≥ −0,01. Réfutée si la borne inférieure de l'IC du taux d'incompatibilité est ≥ 0, ou si la borne supérieure de l'IC du ΔF1 est < −0,01. Non tranchée sinon. Deux tests : seuil corrigé de Bonferroni α = 0,025 pour chacun, soit des IC à 97,5 %.

**Avertissement à écrire dans le protocole.** Pour les fichiers inconnus, la réduction des incompatibilités est en grande partie acquise par construction : le routeur rejette 20/20 inconnus (artefact open-set), et R n'exécute donc rien sur eux. La part informative est la composante prédictive sur les fichiers connus, ainsi que le coût des 3/46 faux rejets. Le rapport doit présenter séparément les connus et les inconnus.

**Durée estimée.** 1 à 2 jours de développement (adaptateur fichier → 17 variables, réutilisation du modèle commun), calcul inférieur à une heure. Ajouter Loghub : +1 jour (téléchargement, adaptateurs, étiquettes).

**Fichiers à écrire.** `revision_reports/chantier_20261105/protocoles/E-H3-NOROUTE.md`, runner `…/scripts/run_e_h3_noroute.py`, artefacts `experiments/phase_revision_20261106/E-H3-NOROUTE/` (`runs.csv`, `summary.json`, `MANIFEST_SHA256.csv`).

**Formulation si non exécuté** (ligne H3 du tableau des statuts et §5 de validité) :
> La chaîne sans routage n'a pas été exécutée. Ce comparateur ne demandait pas de corpus supplémentaire : il pouvait être mené sur les fichiers de l'évaluation open-set. Son absence tient au temps disponible, non à une impossibilité. H3 reste non tranchée, et aucun résultat de ce mémoire ne mesure l'effet du routage sur les exécutions incompatibles.

Remplacer en conséquence l'argument « l'inventaire local ne fournit pas les 90 sources » (concl., ligne H3), qui relève d'E-H3 et non de H3.

### P2 — E-H2-AGENTS-NO-IDEMPOTENCE : agents sans magasin d'idempotence (H2)

**Question.** Dans l'architecture à agents, l'arrêt après persistance et avant `RESULT` produit-il un effet dupliqué sans magasin d'idempotence, et aucun avec ?

**Bras.** C, D (magasin SQLite, comme dans `agent3_paired_failure_abcd_20261104T141803Z`) ; C−I, D−I (même code, `agent.idempotency_store = None`). Le runtime accepte `None` (`intelligent_runtime.py`, gardes `if self.idempotency_store is not None`).

**Données et plan.** Celui de `run_paired_failure_abcd.py` : 40 tâches, arrêt à l'indice 9, mêmes graines que la campagne A–D appariée (10 répétitions).

**Métrique primaire.** Nombre d'effets dupliqués par exécution (`duplicate_effects`). Secondaires : tâches perdues, latence de reprise.

**Règle de décision.** H2 soutenue si C et D ont 0 doublon dans 10/10 exécutions et que C−I et D−I ont au moins un doublon dans 10/10 exécutions ; réfutée si C−I ou D−I a 0 doublon dans au moins une exécution, ou si C ou D en a au moins un ; non tranchée en cas de perte de tâche qui empêche la mesure. Aucune inférence statistique : le mécanisme est déterministe, donc pas de correction multiple.

**Avertissement à écrire.** Le résultat est prévisible par construction (L2 §2.1). L'exécution ferme le comparateur manquant ; elle n'apporte pas de connaissance au-delà de la vérification du code. Elle ne change pas la requalification de H2 en exigence de réalisation (Agent A).

**Durée estimée.** Moins de deux heures, exécution en quelques secondes.

**Fichiers à écrire.** `protocoles/E-H2-AGENTS-NO-IDEMPOTENCE.md` ; runner dérivé de `revision_reports/agent_3/run_paired_failure_abcd.py`, avec deux architectures ajoutées et le fichier d'origine inchangé ; artefacts sous `experiments/phase_revision_20261106/E-H2-AGENTS-NO-IDEMPOTENCE/`.

**Formulation si non exécuté :**
> L'exécution à agents sans magasin d'idempotence n'a pas été réalisée. Le doublon attendu dans ce cas découle du code. H2 n'est donc soutenue que pour sa première composante, et ce qu'elle établit relève d'une exigence de réalisation.

### P3 — E-ABCD-INFERENCE : architectures A, B, C et moindre chargé sur des tâches d'inférence réelles

**Question.** Quelle part du débit l'orchestration par agents consomme-t-elle lorsque chaque tâche porte une inférence réelle, et non une microtâche ?

**Tâche.** Décision HDFS au niveau bloc, telle qu'en `sec:hdfs-distribue` : séquence d'événements d'un bloc → parsing avec l'état Drain3 gelé (`revision_reports/agent_2/hdfs_seed42_drain3_state.bin`) → score Histogram → seuil figé 1,2729. Trois tailles fixées a priori : 1, 10 et 100 blocs par tâche, ce qui fait varier le temps de service sans le choisir après coup.

**Bras.** A (monolithe), B (workers centralisés), C (Contract Net sans mémoire), LL (répartiteur au moindre chargé de `run_e_cnp_least_loaded.py`). D est exclu : sans échec, la mémoire n'a pas d'information à exploiter (`sec:e-h5`). Les workers sont des **processus** et non des threads, ou à défaut le rapport le déclare : sous verrou global de l'interpréteur, des threads ne parallélisent pas une inférence CPU.

**Plan.** 1 000 tâches par exécution, trois coordinateurs, 30 graines appariées (tirage des blocs dans le test HDFS complet), soit 3 tailles × 4 bras × 30 = 360 exécutions.

**Métrique primaire.** Rapport de débit apparié C/A et C/B par taille. Secondaires : C/LL, latence p95, CPU, RSS.

**Règle de décision.** Coût d'orchestration négligeable à une taille donnée si la borne inférieure de l'IC du rapport C/B est ≥ 0,90 ; coût substantiel si la borne supérieure est < 0,90 ; indéterminé sinon. Six comparaisons primaires (2 rapports × 3 tailles) : IC de Student à 1 − 0,05/6 ≈ 99,17 % (Bonferroni). Aucune conclusion de supériorité de C n'est prévue ni ne peut être tirée : la question porte sur le coût.

**Attente déclarée.** Les données existantes montrent déjà que le rapport dépend de la durée de service : C/table vaut 0,211 sans service et 0,867 avec 2 ms (`tab:e-cnp`). P3 mesure ce rapport sur une tâche réelle, sans l'extrapoler.

**Durée estimée.** 1 à 2 jours de développement, 1 à 3 heures d'exécution (estimation non mesurée).

**Fichiers à écrire.** `protocoles/E-ABCD-INFERENCE.md`, `scripts/run_e_abcd_inference.py`, `experiments/phase_revision_20261106/E-ABCD-INFERENCE/`.

**Formulation si non exécuté** (fin de `Benchmark des architectures A--D`) :
> Ces débits portent sur des microtâches : ils mesurent le coût fixe de l'orchestration, non le rapport entre architectures lorsque la tâche contient une inférence. Ce rapport n'a pas été mesuré. Les comparaisons E-CNP indiquent seulement qu'il se resserre lorsque la durée de service augmente (0,211 sans service, 0,867 pour 2 ms).

Supprimer en conséquence la phrase « Il ne préjuge pas du rapport observé lorsque la tâche dure plus longtemps, qu'examine la section~\ref{sec:e-cnp} » : E-CNP n'examine pas de tâche réelle.

### Ordre recommandé

P2 (deux heures, ferme un comparateur), puis P1 (le plus informatif pour la problématique), puis P3. Si une seule expérience est possible : P1.

---

## 3. CICIDS2017 : seuil, plafonnement, pondération

Ces trois points sont des **analyses nouvelles**. Seul le recalcul de la pondération, fait sur les matrices de confusion existantes, peut entrer tel quel ; la calibration et le retrait des plafonds sont à exécuter ou à déclarer non faits.

### 3.1 Calibration des seuils (E-CICIDS-THRESHOLD, à préenregistrer)

- Pour chaque graine 42–46 : partition inchangée du scénario tenu à l'écart. On réserve 20 % de l'entraînement comme validation, stratifiée par scénario d'entraînement ; le scénario de test en est donc absent.
- Seuil de chaque modèle : celui qui maximise le F1 sur la validation, sur une grille des quantiles 0,01 à 0,99 des scores de validation. Il est gelé, puis appliqué au test.
- Métrique primaire : F1 moyen au seuil calibré. Secondaires : PR-AUC (déjà disponible), et F1 de la prédiction tout positif sur le même test.
- Décision : un modèle « dépasse tout positif » si la borne inférieure de l'IC de la différence par graine (n = 5) est > 0. Cinq modèles, Bonferroni α = 0,01.
- Avertissement : la validation ne contient pas l'attaque de test. Le seuil calibré reflète donc les attaques connues, ce qui est le cas d'usage visé. Avec n = 5 scénarios, une conclusion favorable est peu probable. Les PR-AUC de LR par scénario (0,8118 ; 0,5279 ; 0,3140 ; 0,3568 ; 0,2837) sont inférieures à la prévalence pour Bot (0,3295) et WebAttacks (0,3528), et aucun seuil ne corrige un ordonnancement inférieur au hasard.
- Durée : une demi-journée, à partir de `scripts/evaluate_cicids_model_candidates.py`, qui n'a pas de validation (vérifié : aucune option de validation ni de seuil).
- **Si non exécuté :** « Le F1 est calculé au seuil par défaut ; aucun seuil n'a été calibré sur une validation. Le classement des cinq candidats n'est donc pas une comparaison de modèles, et le tableau n'est retenu que comme illustration de la sensibilité au seuil. »

### 3.2 Plafonnement 8 000/4 000 — décision : le justifier pour l'entraînement, le supprimer pour le test

Le plafond de test fixe la prévalence (§1, B7), donc le score de référence tout positif. Il produit ainsi le constat qu'il prétend mesurer. Proposition :
- **Test** : supprimer le plafond. Évaluer sur toutes les lignes du fichier tenu à l'écart, à sa prévalence naturelle, en rapportant cette prévalence et la PR-AUC, dont le niveau de hasard égale la prévalence.
- **Entraînement** : conserver le plafond comme contrainte de calcul déclarée, avec une sensibilité à 32 000 lignes par classe pour une graine.
- **Si non exécuté**, phrase à ajouter après la description des plafonds : « Ces plafonds fixent la prévalence du test : 0,5 pour DDoS et PortScan, 0,0079 pour Infiltration. Le F1 de la prédiction tout positif (0,4733 en moyenne) en est une conséquence arithmétique et ne décrit pas la prévalence d'un trafic réel. »

### 3.3 Pondération d'Infiltration — recalcul disponible, à ajouter en une phrase

Source : `recalcul_cicids_ponderation_sortie.txt`, calculé à partir de `data/processed/cicids_model_candidates_metrics.csv`.

| Agrégat | LR | RF | Tout positif |
|---|---|---|---|
| Macro, 5 scénarios (publié) | 0,2337 | 0,1578 | 0,4733 |
| Macro, sans Infiltration | 0,1989 | 0,1973 | 0,5876 |
| Micro (TP, FP et FN cumulés) | 0,3205 | 0,3488 | 0,5491 |

Phrase proposée : « Le poids égal d'Infiltration, qui ne compte que 32 attaques, ne favorise pas la règle : sans ce scénario, l'écart entre la prédiction tout positif et le meilleur candidat s'accroît (0,5876 contre 0,1989), et il persiste en F1 micro (0,5491 contre 0,3488). » Il s'agit d'un recalcul sur des matrices de confusion existantes, non d'une expérience nouvelle ; ajouter le script à l'annexe de traçabilité.

---

## 4. H4 : statut et formulation

**Constat d'incohérence interne (à trancher par l'intégration et l'auteur).** La conclusion fixe la règle suivante : « Une composante est réfutée lorsque son comparateur a été exécuté et que l'observation prévue par le critère se produit […]. Une hypothèse conjonctive est réfutée dès qu'une composante l'est ». Le critère de H4 dit : « L'hypothèse est réfutée si aucun candidat ne satisfait conjointement ces critères ». Sur les quatre jeux, le comparateur de supériorité a été exécuté et aucun candidat ne dépasse sa baseline. Par la règle du mémoire lui-même, H4 est donc **réfutée dans le périmètre testé**, que le budget ait été fixé ou non : aucun budget ne peut rendre supérieur un modèle qui ne dépasse pas la règle. Le statut actuel « NON TRANCHÉE ; supériorité infirmée » contredit cette règle.

**Recommandation.** Statut : **RÉFUTÉE dans le périmètre testé** (composante de supériorité infirmée sur quatre jeux ; composante de budget jamais définie). Si l'auteur préfère « NON VALIDÉE », il faut récrire la règle de la conclusion, et ce changement serait fait après lecture des résultats. L'Agent B le déconseille. La mission demande « non validée, composante de supériorité infirmée » : cette formulation est compatible avec la recommandation si « non validée » qualifie la conclusion générale et « réfutée » le statut du tableau.

**Formulation exacte proposée.**
- Concl., paragraphe « Aucune hypothèse n'est validée » : remplacer « H4 ne l'est pas davantage dans son ensemble, et sa condition de supériorité est infirmée sur les quatre jeux publics ; aucun budget n'ayant été fixé avant l'exécution, elle ne peut plus être validée par ce travail » par :
  > H4 est réfutée dans le périmètre testé : sous chacun des quatre protocoles stricts, aucun modèle ne dépasse la meilleure règle simple évaluée sur le même test. Le budget local de temps et de mémoire n'a jamais été fixé ; il ne l'est pas après coup, et sa fixation ne pourrait de toute façon pas rendre supérieur un modèle qui ne dépasse pas la règle.
- Tableau `tab:statut-hypotheses`, ligne H4 : statut « RÉFUTÉE (périmètre testé) » ; cellule *Budget* : « jamais fixé ; non fixé rétroactivement ». Le reste est inchangé.
- `main.tex` : le résumé français (« H3, H4 et H5 ne sont pas tranchées, et la supériorité visée par H4 est infirmée sur les quatre jeux publics »), l'abstract (« H3, H4 and H5 remain undecided, and the superiority targeted by H4 is refuted… ») et le Bokuse (« H4 etikali NON TRANCHÉE … mpe budget ya ressources etyamaki te ») sont à aligner, la traduction lingala restant à faire relire (C19).
- `chapitre7_reproductibilite_deploiement.tex` : « ne fixe pas rétroactivement le budget de H4 dans son ensemble » peut rester ; supprimer « dans son ensemble ».
- Intro, paragraphe « Aucun des critères de H1 à H5 n'a en revanche fait l'objet d'un préenregistrement… » : inchangé, il annonce déjà qu'une grandeur non fixée ne l'est pas après coup.

À répercuter partout où « H3, H4 et H5 ne sont pas tranchées » apparaît (Agent E : repérage par grep).

---

## 5. Contract Net : pertes de tâches et biais du comparateur

### 5.1 Analyse causale des pertes (L1 §C.3)

**Faits** (`pertes_par_bras_sortie.txt`, lecture des `runs.csv` d'`experiments/phase_revision_20261105/`) :
- Table statique et moindre chargé : 0 échec final dans tous les scénarios (E-CNP, E-CNP-LL ; 30 × 1 000 tâches par cellule).
- Contract Net avec 3 coordinateurs : 4 (C) et 8 (D) pertes sous fiabilité hétérogène, 0 (C) et 50 (D) sous panne silencieuse (E-CNP) ; 5 (C) sous fiabilité hétérogène (E-CNP-LL). E-H5 à 3 coordinateurs : C 3 / 19 / 44, D 6 / 4 / 3 pour p = 0,3 / 0,6 / 0,9.
- **Contract Net avec un seul coordinateur** (sensibilité d'E-H5, 10 graines par cellule, 60 exécutions, 60 000 tâches) : **0 perte**, y compris à p = 0,9, où C en perd 44 avec trois coordinateurs.

**Mécanisme, lu dans le code.**
1. `ContractNetCoordinator.negotiate` (`src/logminer/agents/contract_net.py`) envoie l'appel d'offres, puis ne retient dans `ranked` que les agents qui proposent.
2. `MultiTaskIntelligentAgent.evaluate` (`intelligent_runtime.py`) refuse avec `agent_overloaded` si `active_tasks >= max_parallel_tasks` (2 dans le benchmark).
3. En cas d'échec, le repli ne parcourt que `ranked`, fixée au moment de l'appel d'offres : un agent occupé à cet instant n'y figure pas, et aucun nouvel appel d'offres n'est émis. Un agent de `ranked` devenu occupé entre-temps refuse à l'`AWARD` (`accept`) et il est sauté.
4. Le seul échec injecté porte sur l'agent de plus forte confiance pour le type (`instrument` dans `run_e_h5_e_cnp.py`) ou sur `agent-gamma` en panne silencieuse ; les autres agents réussissent toujours. Une tâche n'est donc perdue que si tous les agents encore candidats sont soit l'agent défaillant, soit occupés.
5. Le comparateur statique et le moindre chargé parcourent **tous** les agents au moment de chaque tentative (`run_static` ; `run_least_loaded`, qui recalcule `perceive().load_ratio` à chaque essai) : un agent momentanément occupé n'est pas écarté définitivement.

**Conclusion causale.** Les pertes exigent la concurrence (aucune sans elle) et proviennent de la liste de repli figée à l'appel d'offres, qui écarte les agents occupés à cet instant, sans nouvel appel d'offres. La plus forte perte de D sous panne silencieuse (50 contre 0 pour C) est **compatible** avec une concentration des attributions par la mémoire sur `agent-alpha` et `agent-beta` : ceux-ci seraient plus souvent occupés, laissant `agent-gamma`, défaillant, seul candidat. Cette explication reste une **hypothèse non vérifiée** : les motifs de refus de `NegotiationResult.refusals` ne sont pas conservés par le runner.

**Confirmation à mener** (diagnostic, non confirmatoire) : rejouer E-CNP s2 et s3 (C, D, 30 graines) en journalisant, pour chaque tâche perdue, `refusals` et `ranked`. Critère fixé a priori : le mécanisme est confirmé si au moins 95 % des tâches perdues ont au moins un agent non défaillant refusé pour `agent_overloaded` à l'appel d'offres. Ablation corrective : variante qui relance un appel d'offres après échec, avec un critère de 0 perte sur 30 000 tâches. Durée : une demi-journée. Les ordres d'exécution des threads n'étant pas déterministes, le rejeu ne reproduit pas les pertes à l'identique ; il en reproduit la fréquence.

**Paragraphe proposé** (remplace, dans `sec:e-cnp`, « D'après le code, un agent occupé lors de l'appel d'offres ne propose pas et n'entre pas dans la liste de repli de ce contrat. Ces échecs restent rares […] ») :
> Ces pertes n'apparaissent qu'avec plusieurs coordinateurs concurrents : en exécution séquentielle, aucune des 60 000 tâches de l'analyse de sensibilité d'E-H5 n'est perdue, même lorsque l'agent préféré échoue neuf fois sur dix. Leur cause est dans la liste de repli. Elle est fixée au moment de l'appel d'offres et ne contient que les agents qui ont proposé ; or un agent occupé à cet instant refuse de proposer, et aucun nouvel appel d'offres n'est émis après un échec. La table statique et le répartiteur au moindre chargé, qui examinent tous les agents à chaque tentative, ne perdent aucune tâche. Il s'agit d'un défaut de l'implémentation, non d'une propriété du protocole : une relance de l'appel d'offres après échec le corrigerait, mais elle n'a pas été testée.

### 5.2 Biais du comparateur au moindre chargé — paragraphe consolidé

Remplace le paragraphe existant « Cette comparaison avantage le répartiteur par construction… » (`sec:e-cnp-moindre`), et ne doit figurer qu'à cet endroit :
> Cette comparaison avantage le répartiteur par construction. Il lit directement l'état de chaque agent dans la mémoire du processus, sans message, sans délai de transport et sans risque d'information périmée ; Contract Net, lui, fait transiter la même information par environ dix messages par tâche. Dans un système réparti, connaître la charge d'un agent distant a un coût et un retard, et l'écart mesuré ici pourrait se réduire ou s'inverser ; cette configuration n'a pas été testée. Les mêmes gains face à la table statique sont obtenus par le répartiteur seul : la prise en compte de la charge suffit à les expliquer. Dans le périmètre évalué, aucun résultat ne justifie le coût de la négociation, et rien n'établit qu'elle soit inutile hors de ce périmètre.

---

## 6. Formulations honnêtes : E-H5 et distribution

### 6.1 E-H5

Le texte est déjà juste. Deux ajouts sont à faire, et la répétition dans la discussion et la conclusion est à couper (Agent E).
- **Justification des niveaux**, à ajouter au premier paragraphe de `sec:e-h5` (sans source, le protocole ne motive pas ces valeurs) :
  > Les niveaux 0,3, 0,6 et 0,9 ont été fixés dans le protocole pour couvrir un écart modéré, fort et extrême entre la confiance déclarée et la fiabilité réelle. Ils ne sont tirés d'aucune mesure opérationnelle, et le niveau auquel le gain apparaît, p = 0,9, est le plus éloigné d'une configuration réaliste.
- **Phrase de synthèse unique** (conclusion et section de synthèse ; à ne pas répéter ailleurs) :
  > La mémoire n'apporte un gain établi que dans une simulation où l'agent préféré, déclaré le plus fiable, échoue neuf fois sur dix ; ce gain s'accompagne d'une moindre équité de répartition. Il n'établit pas une capacité d'apprentissage utile en conditions ordinaires.
- Ajouter dans `sec:e-h5` une phrase signalant que les pertes finales de C à trois coordinateurs (3, 19 et 44) relèvent du mécanisme décrit au §5.1.

### 6.2 Distribution

Fusionner les constats dispersés de `sec:cnp-multivm` en un paragraphe final unique, puis supprimer les redites dans la discussion et la conclusion :
> La topologie à deux machines virtuelles démontre l'exécution répartie du protocole et la reprise idempotente entre hôtes, non un partage de charge ni une montée en capacité. En endurance, la charge offerte (0,4993 tâche/s) est très inférieure à la capacité ; la répartition 451/1 349 découle des profils de confiance. En saturation, la seconde machine ne reçoit des tâches qu'une fois la première hors délai et assure 1,23 % des tâches réussies ; le plafond (8,4 à 15,0 tâches/s) est atteint sans gain de capacité. En détection HDFS, les deux agents ayant le même profil, toutes les tâches vont à `debian-alpha` par départage alphabétique. La trace des messages d'endurance, tronquée aux 10 001 derniers événements, n'est pas exploitée. Aucune de ces campagnes ne mesure la scalabilité.

Sources : `tab:cnp-endurance`, paragraphe `Saturation`, `sec:hdfs-distribue`, tous dans `chapitre5_resultats.tex`.

---

## 7. Effet sur le volume

| Action | Effet estimé (pages) |
|---|---|
| Fusion de `tab:e-cnp` et `tab:e-cnp-moindre` en un seul tableau (scénario × table, moindre chargé, C), avec un paragraphe d'interprétation au lieu de quatre | −0,8 |
| Paragraphe unique sur la distribution (§6.2), redites retirées de la discussion et de la conclusion | −0,7 |
| `tab:benchmark-debit` : IC conservés, deux charges au lieu de quatre (les quatre en annexe ou dans la matrice A.2) | −0,3 |
| Paragraphe sur les pertes (§5.1) à la place de la phrase actuelle | +0,2 |
| Phrases CICIDS (§3.2, §3.3) et justification des niveaux d'E-H5 | +0,3 |
| Note de sensibilité de Bonferroni (une phrase dans la section de validité) | +0,1 |
| Si P1, P2 et P3 sont exécutés : une sous-section chacun, avec un tableau | +2,0 à +2,5 |
| **Net sans nouvelles expériences** | **≈ −1,2** |
| **Net avec les trois expériences** | **≈ +1** |

Le gain de volume de cet axe est faible. La réduction à 150 pages doit venir de la redondance (Agent E), et non de la suppression de résultats.

---

=== PASSATION ===
Agent : B — Rigueur expérimentale et comparateurs manquants
Statut : terminé
Livrable : `revision_reports/refonte_150p/agent_B/LIVRABLE_B.md` ; recalculs en lecture seule : `sensibilite_bonferroni.py`, `recalcul_cicids_ponderation.py`, `pertes_par_bras.py` et leurs `*_sortie.txt`
Résultats nouveaux, issus d'artefacts existants :
- Bonferroni ne change aucune décision d'E-H5, d'E-CNP ni d'E-CNP-LL ; le recalcul reproduit d'abord les décisions publiées.
- Le F1 tout positif CICIDS (0,4733) est fixé par les plafonds de test (prévalence 0,5 sur deux scénarios). Le poids d'Infiltration favorise les modèles, non la règle ; en micro-F1, tout positif 0,5491 contre au mieux 0,3488.
- Pertes Contract Net : aucune sans concurrence (60 000 tâches) ; cause = liste de repli figée à l'appel d'offres. L'explication des 50 pertes de D reste à confirmer.
Points pour l'intégration :
1. H4 est réfutée selon la propre règle de la conclusion : le statut « NON TRANCHÉE » est incohérent. Décision à soumettre à l'auteur (§4).
2. L'argument des « 90 sources » invoqué pour H3 appartient à E-H3 ; P1 est faisable sur le corpus open-set existant.
3. P2 est trivial et prévisible par construction ; P1 est le plus informatif ; P3 mesure un coût, pas une supériorité.
Prochain agent : intégration.
=== FIN PASSATION ===
