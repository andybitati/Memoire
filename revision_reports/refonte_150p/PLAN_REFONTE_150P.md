# Plan de refonte du mémoire Ariel Logminer : de 180 à environ 150 pages

Agent d'intégration, chantier « Refonte 150 pages », 2026-11-05. Il fusionne les livrables A à F (`agent_A/` à `agent_F/LIVRABLE_*.md`) et les réponses de l'auteur consignées dans `ETAT.md`. Aucun `.tex`, script, donnée ni artefact n'a été modifié, et aucune expérience n'a été lancée. Les pages sont celles du PDF de 180 pages (`main.toc`) : 23 pages liminaires et 157 pages numérotées en chiffres arabes.

Abréviations : L1 et L2 désignent le lecteur 1 et le lecteur 2, suivis de la section de leur rapport (`RETOURS_LECTEURS.md`). « Ch. 4 » renvoie au chapitre 4 du PDF (`chapitre5_resultats.tex`). La correspondance complète entre fichiers et chapitres est dans `CONSIGNES.md`.

---

## 0. Synthèse

**Verdict.** On peut défendre le mémoire à condition qu'il cesse de se présenter comme une architecture et devienne ce que ses résultats soutiennent : une étude expérimentale critique qui attribue chaque propriété observée du prototype à son mécanisme effectif (L1 §5, 1re objection). Il est possible d'arriver à environ 150 pages sans retirer un seul résultat valide. Le gain vient surtout de la redondance (chiffres répétés, limites et statuts dispersés, annexe A.9), de l'état de l'art et du modèle proposé.

**Contre-vérification préalable (étape 0) : le défaut CICIDS2017 est confirmé.**
- Code relu : `collect_network_sample` (`scripts/evaluate_supervised_strict_splits.py`, l. 229–277), appelée par `run_final_experiments.py::load_holdout` (l. 304) et par `evaluate_cicids_model_candidates.py` (l. 191).
  - La fonction parcourt les fichiers dans l'ordre alphabétique (`cicids_files` : `sorted(glob)`), prend les premières lignes de chaque classe et s'arrête dès que les deux plafonds de 8 000 lignes sont atteints.
- Contrôle direct sur les données (`data/raw/Datasets/MachineLearningCSV/MachineLearningCVE/`) :
  - les 100 000 premières lignes de `Friday-…-DDos` contiennent 38 806 BENIGN et 61 194 DDoS ;
  - celles de `Friday-…-PortScan` contiennent 87 512 BENIGN et 12 488 PortScan.
  - Les deux plafonds sont donc atteints dans le premier bloc du premier fichier lu. L'entraînement ne porte que sur un seul scénario : PortScan quand DDoS est tenu à l'écart, DDoS sinon.
- Résultats touchés :
  - le tableau des cinq candidats (`tab:cicids-candidats`) ;
  - le F1 de 0,1577 du Random Forest en holdout par scénario (`experiments/phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv`, ligne « Holdout scénario ») ;
  - la ligne « CICIDS2017, holdout par scénario » du tableau des règles simples (0,4733 contre 0,2337) ;
  - la figure `fig_cicids_protocol_comparison` ;
  - toutes leurs reprises : résumés, QR6, conclusion, discussion, annexe ;
  - les recalculs de pondération de l'Agent B (§3 de son livrable), qui portent sur ce même holdout.
- Restent sains (Agent C, §2.1) : la séparation temporelle, l'Isolation Forest temporel, et la séparation aléatoire, qui prend les premières lignes de **chaque** fichier.
- Le constat qualitatif « le score dépend du protocole » reste établi sans le holdout. Le même Random Forest passe de 0,9951 en séparation aléatoire à 0,4374 en séparation temporelle (même CSV, lignes « Random stratifié » et « Holdout temporel »).

**H4, réfutée selon la décision de l'auteur : la réfutation tient sans le holdout défectueux, mais sur un périmètre plus étroit.**
- Protocoles valides et résultats (`tab:baselines-par-jeu`) :
  - CICIDS2017 temporel : tout positif 0,6667 ; régression logistique 0,5566, Random Forest 0,4374 ;
  - HDFS, niveau bloc : règle 0,8724 ; Histogram 0,8684 ;
  - BGL, niveau événement : règle 0,9137 ; Histogram 0,9137, puisque Histogram *est* la règle sur ce protocole ;
  - CSE-CIC-IDS2018 : règle 0,9997 ; régression logistique 0,9992, à condition que l'intégrité des fichiers soit vérifiée (décision 2).
- Formulation exacte à retenir :
  > H4 est réfutée dans le périmètre testé : sous les protocoles stricts retenus (CICIDS2017 en séparation temporelle, HDFS au niveau bloc, BGL au niveau événement et CSE-CIC-IDS2018 entre deux journées), aucun des modèles évalués ne dépasse la meilleure règle simple appliquée au même test. Le holdout par scénario de CICIDS2017, dont l'échantillonnage d'origine ne couvrait qu'un scénario d'entraînement, a été réexécuté après correction ; [RÉSULTAT D'E-CICIDS-HOLDOUT-FIX À INSÉRER, qu'il confirme ou non le constat]. Le budget local de temps et de mémoire n'a jamais été fixé ; il ne l'est pas après coup.
- Si CSE-CIC est retiré, écrire « trois protocoles » et supprimer CSE-CIC-IDS2018 de la liste.
- Réserve à écrire une fois : sur HDFS et BGL, le « modèle » est un score de rareté (HBOS) et la règle qui le bat en est une version réduite. La réfutation porte sur les candidats évalués, non sur l'apprentissage automatique en général (L1 §B.1).

**Ce qui change sur le fond par rapport au manuscrit actuel :**
1. **CICIDS2017 holdout par scénario** : défaut d'échantillonnage du même type que celui d'E-H3b, non déclaré aujourd'hui. **L'auteur a choisi de réexécuter** : le protocole préenregistré E-CICIDS-HOLDOUT-FIX est préparé et exécuté par le coordinateur (expérience en cours, P0). Les anciens chiffres seront **remplacés par ceux de la réexécution, quels qu'ils soient** : tableau des cinq candidats, 0,1577, ligne holdout du tableau 4.15, QR6, résumés. Le défaut d'échantillonnage reste déclaré en §4.2 et au ch. 5.
2. **H4** passe de « non tranchée » à « réfutée dans le périmètre testé », avec le périmètre restreint ci-dessus.
3. **Linux/auth est un corpus synthétique public.** Les quatre fichiers `linux_auth_logs_*.csv` forment exactement le jeu Kaggle « linux_auth_log-anomalies » (LİN ÇORBACI, `kaggle.com/datasets/lnorbaci/linux-auth-log-anomalies`, licence MIT, v1 du 2025-10-27) : la somme de leurs tailles (204 854 155 octets) est égale à la taille déclarée par Kaggle (`ETAT.md`). Sa description le dit **entièrement généré avec Faker**, ce qui explique les dates postérieures relevées par l'Agent D. La « partie générée » évoquée par l'auteur correspond vraisemblablement aux fichiers `Dataset_csv/*_logs.csv` de 50 lignes, qui ne servent à aucune campagne citée. Conséquence : le citer comme jeu Kaggle synthétique (auteur, version, date d'accès). Aucun résultat sur Linux/auth, dont l'écart de spécialisation de +0,1669, ne vaut pour des journaux réels.
4. **Histogram est une instance de HBOS** (Goldstein et Dengel, 2012) sur trois attributs catégoriels. Il reçoit ainsi une filiation, et la baseline HDFS en est la restriction au seul template (Agent D §4).
5. **E-H3B-STRICT n'est pas touchée** par le chargeur fautif d'E-H3b (Agent C §2.2) ; ses résultats restent utilisables.
6. **Déclaration IA** : sa structure est revue, sans qu'aucun usage n'en soit retiré. Les protocoles complémentaires y sont attribués à des agents d'IA sur décision de l'auteur (Agent F).
7. **Pertes de tâches sous Contract Net** : la cause est trouvée. La liste de repli est figée au moment de l'appel d'offres, et aucune tâche n'est perdue sans coordinateurs concurrents (Agent B §5).

**Décisions attendues de l'auteur :**
1. ~~**Holdout CICIDS2017**~~ : **tranché par l'auteur**, réexécution sous E-CICIDS-HOLDOUT-FIX (en cours, coordinateur). Reste à vérifier : le protocole est commité **et poussé** avant l'exécution (§3).
2. **CSE-CIC-IDS2018** : comparer la taille des fichiers locaux à celle de la distribution officielle (`aws s3 ls --no-sign-request`, environ 5 minutes ; Agent C §3). Si elles concordent, garder §4.6 réduit à 2 pages ; sinon, ou si la vérification n'est pas faite, retirer §4.6.
3. **Titre** (Agent A Q1) : proposition recommandée, « Ariel Logminer : conception et évaluation critique, en laboratoire, d'une architecture multi-agents légère pour l'analyse de journaux système et réseau ». Elle revient sur la décision D1 ; à soumettre aux co-directeurs.
4. **Hypothèses** (Agent A Q2 à Q4) :
   - reclasser H1 et H2 en exigences de réalisation R1 et R2 ;
   - scinder H5 en H5a (mémoire d'attribution), H5b (priorisation) et R3 (gouvernance) ;
   - ajouter H-CNP comme hypothèse de campagne ;
   - supprimer QR4 ;
   - accepter la phrase qui dit que l'opposition E1/E2 a été posée après une partie des résultats.
5. ~~**Linux/auth**~~ : **identifié** (jeu Kaggle synthétique, voir le point 3 ci-dessus). Reste à confirmer par l'auteur : la date de téléchargement, pour la date d'accès, et le fait que les fichiers `Dataset_csv/*_logs.csv` sont bien la « partie générée ».
6. **Déclaration IA** : attester ou retirer chacun des quatre passages `[À CONFIRMER PAR L'AUTEUR]` ; accepter la phrase de calendrier, qui nuance la décision C4(a).
7. **Dépôt** (A6-Q1) : choisir entre Zenodo (recommandé), GitHub public ou archive remise au jury. **Pousser dès maintenant** les commits non poussés.
8. **Expériences** à exécuter avant la soutenance : P1, P2, P3, P0 (§3).
9. **Rejeu personnel** d'au moins une campagne, avant d'écrire « réexécutées par l'auteur » (Agent F §6.1).
10. **Bokuse** : relecture par une personne qui parle le lingala (décision C19, déjà prise).

---

## 1. Tableau de bord

Statuts : **R** = corrigeable par réécriture ; **X** = exige une expérience ; **A** = exige une action de l'auteur ; **L** = limite résiduelle acceptée et déclarée une seule fois.

### 1.1 Les huit faiblesses les plus graves (L1 §4)

| Rang | Faiblesse | Agent | Correctif | Statut |
|---|---|---|---|---|
| 1 | Aucune hypothèse intégralement validée (tableau 7.1) | A | H1 et H2 reclassées en exigences R1 et R2 (satisfaites) ; tableau unique QR ↔ hypothèse ↔ mesure ↔ statut ; thèse E1/E2 qui donne aux résultats négatifs le rôle de réponse ; phrase de tête conservée : « aucune hypothèse comparative n'est validée » | R + L |
| 2 | Aucune supériorité prédictive face aux règles simples (tableau 4.15) | B, C | H4 réfutée dans le périmètre testé (§0) ; ligne CICIDS holdout retirée ou réexécutée ; réserve HBOS | R (+ X si P0) |
| 3 | Pas d'avantage propre de Contract Net face au moindre chargé | B, D | Biais du comparateur écrit une seule fois (Agent B §5.2) ; rattachement à JSQ et power of two choices (Agent D §3) ; H-CNP réfutée dans un seul processus | R + L |
| 4 | Pas d'analyse conjointe système/réseau | A, D | Titre et conclusion recadrés ; « sait normaliser » corrigé ; limite écrite une seule fois. Aucune expérience proposée : E-HET a été exclue par l'auteur (C13) | R + L |
| 5 | H3 non tranchée, comparateur sans routage absent | B | P1, faisable sur le corpus open-set existant ; sinon, formulation « non exécuté, faute de temps » (Agent B §2) | X ou L |
| 6 | Mémoire bénéfique seulement sous défaillance extrême | B | Justification des niveaux 0,3, 0,6 et 0,9 ; phrase de synthèse unique ; H5a non établie en général | R + L |
| 7 | Distribution insuffisante pour démontrer la scalabilité | B | Paragraphe unique sur la distribution (Agent B §6.2) : exécution répartie démontrée, montée en capacité non démontrée | R + L |
| 8 | Originalité trop proche de critiques publiées | D | Contribution recadrée (Agent D §5) ; ch. 1 nettoyé de ses résultats ; littérature d'équilibrage de charge citée comme ayant prédit les résultats | R + L |

### 1.2 Points de non-recevabilité (L2 §4)

| # | Point | Agent | Correctif | Statut |
|---|---|---|---|---|
| 1 | Aucun dépôt accessible | F | Choisir un mode de dépôt (Zenodo recommandé) ; pousser les commits ; construire la copie publique selon `agent_7/public_release/PUBLIC_RELEASE_PLAN.md` ; texte du ch. 7 pour chaque option (Agent F §4.5) | **A (bloquant)** |
| 2 | Attestation de l'apport personnel | F | Déclaration IA restructurée ; justifications à rédiger de la main de l'auteur dans `PREPARATION_SOUTENANCE.md` (Agent F §5) ; rejeu personnel d'une campagne | **A** |
| 3 | Intégrité de CSE-CIC-IDS2018 | C | Vérifier les tailles sur S3 ; garder §4.6 réduit, ou le retirer et passer H4 à trois protocoles | **A** puis R |
| 4 | Titre et conclusion à mettre en cohérence (« hétérogènes », « intelligents », « sait normaliser ») | A, D | Titre proposé ; définition plus modeste de l'agent ; « intelligent » retiré des mots-clés ; conclusion corrigée (Agent A §5.2) | R + A (titre) |
| 5 | Jeux UNSW, Linux/auth, Solaris BSM et DARPA 1998 non cités | D | Moustafa et Slay 2015 et 2016 ; Lippmann 2000 et McHugh 2000. Solaris BSM et DARPA 1998 sont un seul jeu. Linux/auth : jeu Kaggle synthétique identifié, entrée `@misc` (§4) | R |

---

## 2. Plan de 150 pages

### 2.1 Règles transversales (à appliquer partout)

1. **Un chiffre détaillé n'apparaît qu'une fois**, avec son intervalle, dans sa section du ch. 4. Le résumé en donne trois au plus. La conclusion et la validité renvoient au ch. 4 et ne citent un chiffre qu'au plus une fois par chapitre. L'annexe A.2 garde les valeurs brutes, sans commentaire (Agent E §1).
2. **Une seule section de limites** : §5.8 actuel (`limites_consolidees.tex`). Les autres endroits la citent : délimitations de l'introduction, 2.25 et tableau 2.4, 7.6–7.7, « Limites » de la conclusion.
3. **Une seule section de synthèse** « implémenté / testé / effectivement supérieur » (nouvelle, ch. 6, §2.3 ci-dessous). Elle remplace 4.16, 5.7, les redites de 6.2–6.7, le tableau 1.6 et le détail du tableau 7.1.
4. **Un seul tableau QR ↔ hypothèse ↔ mesure ↔ statut** (Agent A §4). Il remplace `tab:nature-qr`, le tableau 2.3 (2.24) et le tableau 7.1. L'introduction en donne les colonnes de cadrage, la conclusion les colonnes de statut.
5. **Aucun identifiant interne hors de l'annexe A.2** : run_id, préfixes `agent2_` à `agent6_`, noms de dossiers. Le corps emploie les étiquettes lisibles proposées par l'Agent E (§4). Contrôle final : `grep -c "2026[0-9]\{4\}T"` doit valoir 0 hors de `annexes.tex`.
6. **Précision des nombres** : quatre décimales pour les métriques, deux pour les pourcentages, convention `\,\%` (Agent E §5, huit écarts listés).
7. **Aucun gain obtenu par la mise en page** : police, marges et interligne restent inchangés (Agent E §2.3).

### 2.2 Section par section

Colonnes : Action (C = conserver, R = réviser, F = fusionner, S = supprimer, A = ajouter) ; Justification ; pages actuelles → cibles ; Risque (ce qui affaiblirait l'idée principale si l'action est mal exécutée).

**Pages liminaires (23 → 20)**

| Élément | Action | Justification | p. | Risque |
|---|---|---|---|---|
| Titre | R | L2 §2.1, §4.4 ; décision 3 | — | Titre trop modeste, qui masque l'objet multi-agents : garder « architecture multi-agents légère » |
| Déclaration IA (iv–v) | R | L2 §2.7 ; texte de l'Agent F §3.2 (voir §5) | 2 → 2,25 | Minimiser : aucun usage déclaré ne doit être retiré |
| Résumé, abstract (vi–ix) | R | L2 §2.5 ; résumé de l'Agent E §3.1 avec les **trois corrections** ci-dessous | 4 → 2 | Retirer un résultat négatif majeur pour faire court |
| Bokuse (x–xii) | R | L2 §2.5 ; règle d'alignement de l'Agent E §3.3 ; relecture C19 | 3 → 1,5 | Traduction non relue |
| Tables, listes, sigles | R (mécanique) | Effet des fusions de sections | 9 → 8 | — |

Corrections au résumé proposé par l'Agent E (et à l'abstract) :
- (i) remplacer « passe de 0,9951 à 0,1577 lorsqu'un scénario d'attaque est tenu hors de l'entraînement » par « passe de 0,9951 en séparation aléatoire à 0,4374 lorsque les derniers jours de capture sont tenus à l'écart » (`cicids_protocol_comparison.csv`) ;
- (ii) remplacer « Aucune des cinq hypothèses n'est validée » par le décompte de l'Agent A §3.1, avec H4 « réfutée dans le périmètre testé » ;
- (iii) « sur quatre jeux » devient « sous les protocoles stricts retenus », ou « trois protocoles » si CSE-CIC est retiré.

**Introduction générale (15 → 12)**

| Section (p.) | Action | Justification | p. | Risque |
|---|---|---|---|---|
| Contexte, problématique (1–4) | R | L1 §A.1 : resserrer autour de la thèse E1/E2 | 4 → 3,5 | — |
| Définitions opérationnelles (4–5) | R | L2 §2.3 : définition plus modeste de l'agent, retrait d'« intelligent » (Agent D §7) | 1 → 0,75 | Vider le mot « agent » de son sens : garder la mention de la règle de décision locale |
| Question centrale et QR (5–7) | R | L2 §2.1 : question remplacée par la thèse E1/E2 (Agent A §2.2), avec la phrase d'honnêteté (§2.4) ; cinq QR, QR4 supprimée ; tableau unique | 2 → 1,75 | Thèse lue comme réécrite après coup : la phrase d'honnêteté est obligatoire |
| Hypothèses et critères (7–9) | R | L2 §2.1, L1 §A.3 : R1, R2 et R3 ; H3, H4, H5a, H5b, H-CNP ; grandeurs fixées pour l'avenir seulement, sans application rétroactive (Agent A §3.2) | 2 → 1,75 | Reclassement lu comme un habillage : rappeler les énoncés initiaux et dire que les statuts ne changent pas |
| Objectifs (9–10) | F | Agent A : de dix à cinq objectifs, alignés sur les QR | 1 → 0,5 | — |
| Démarche méthodologique (10–12) | R | Préenregistrement limité aux campagnes concernées (Agent C §7) | 2 → 1,5 | — |
| Contributions, délimitations, organisation (12–15) | F | Contribution recadrée (Agent D §5) ; délimitations renvoyées à la section des limites | 3 → 2,25 | — |

**Ch. 1, état de l'art (30 → 22)** — plan détaillé de l'Agent D §2, avec 11 sections cibles. Conflit avec l'Agent E, qui en proposait 8 : **l'intégration retient les 11 sections de l'Agent D**, plus fines sur les sections que L1 §D crédite.

| Section actuelle (p.) | Action | Justification | p. actuel → cible |
|---|---|---|---|
| 1.1–1.4 Introduction, journaux, détection, règles (16–21) | F | L1 §F, fragmentation | 5 → 3,25 |
| 1.5 Supervisé (21–22) | R | L2 §2.3 : ET et HGB reliés à la comparaison CICIDS ; SGD introduit. *Adapter ce passage aux candidats effectivement évalués par E-CICIDS-HOLDOUT-FIX* | 1,5 → 0,75 |
| 1.6 Non supervisé (22–24) | S (LOF, One-Class SVM) + A (HBOS) | L2 §2.3 | 2 → 1,25 |
| 1.7–1.8 Déséquilibre, jeux de données (24–26) | F + A | L2 §2.3, §4.5 : UNSW, DARPA 1998/BSM, Linux/auth (synthétique public, Kaggle) ; demi-phrase sur Sharafaldin ; phrases de résultats F-1 et F-2 retirées | 2,5 → 2,5 |
| 1.9–1.10 Parsing, normalisation (26–29) | F | Phrase de résultat F-3 retirée | 3 → 2,5 |
| 1.11–1.12 Séquentiel, sémantique (29–31) | F | 1.11.5 conservé intégralement (cadre de la QR sur le protocole) | 2 → 1,5 |
| 1.13 Cadres intégrés (31–32) | C | Crédité par L1 §D | 1 → 1 |
| 1.14–1.15 Agents, files, livraison (32–34) | R + A | L2 §2.3 : paragraphe sur l'allocation de tâches (Agent D §3) | 2 → 2,5 |
| 1.16–1.20 Routage, corrélation, mémoire, gouvernance, tableau de bord (34–38) | F | Phrases F-4 et F-5 déplacées au ch. 2 ou 4 | 4 → 2,5 |
| 1.21 Reproductibilité (38–39) | S → renvoi au ch. 7 | Agent E | 1 → 0,25 |
| 1.22 Tableau 1.4 (39–40) | S | L2 §2.5 (Agent D, plus radical que la refonte de l'Agent E : retenu) | 1 → 0 |
| 1.23 Tableau 1.5 (40–42) | R : 7 à 8 lignes, 3 colonnes | L2 §2.5 | 2 → 0,75 |
| 1.24–1.26 Tensions, positionnement, synthèse (42–45) | F ; tableau 1.6 → synthèse unique du ch. 6 ; F-6 et F-7 retirés | L2 §2.4 ; L1 §F | 3,5 → 1,25 |

*Risques* : effacer en condensant ce que L1 §D crédite (1.13 à 1.15, marqués « conserver ») ; déplacer le tableau 1.6 sans créer la synthèse du ch. 6, alors que les deux opérations vont ensemble.

**Ch. 2, modèle proposé (28 → 23)** — fusion de 26 sections en 9 (Agent E §2.4).

| Section | Action | Justification | p. |
|---|---|---|---|
| 2.1–2.3 | F « Exigences et principes » | L1 §F | 3 → 2,5 |
| 2.4–2.7 | F | — | 7 → 6 |
| 2.8–2.11 | F ; description du corrélateur (venue du ch. 1, F-4) | L2 §2.4 | 3 → 3 |
| 2.12–2.13, 2.17 | F | — | 3 → 2,5 |
| 2.14–2.16 + `spec_utilite.tex` | C, avec une phrase qui dit que l'utilité est un classement à poids fixes (Agent D §7) | L2 §2.3 | 4 → 4 |
| 2.18–2.23 | F, sécurité et scénarios réduits | — | 5 → 3,5 |
| 2.24 et tableau 2.3 | S → tableau unique (Agent A) | L2 §2.1 | 1 → 0 |
| 2.25 et tableau 2.4 | S → section des limites | Règle 2 | 1 → 0 |
| 2.26 | C | — | 1 → 0,5 |
| **Passe sur le conditionnel** | R | L2 §2.4 : 57 occurrences de « peut », « peuvent » ou « pourrait » (Agent E §1, E11). Écrire à l'indicatif ce qui est implémenté, et marquer explicitement « non implémenté » ce qui ne l'est pas | 0 |

*Risque* : en passant à l'indicatif, présenter comme implémenté ce qui ne l'est pas. Vérifier chaque phrase contre le code.

**Ch. 3, implémentation (10 → 9)**

| Section | Action | Justification | p. |
|---|---|---|---|
| 3.4 Routeur | R : une phrase sur la circularité partielle (colonnes `dataset` et `subtype`), avec renvoi aux limites | L2 §2.2 ; Agent C §8 | = |
| 3.8.1 Histogram | A : « suit le principe de HBOS » | L2 §2.3 | +0,1 |
| 3.5 Agents | R : `MultiTaskIntelligentAgent` présenté comme un nom hérité du code | L2 §2.3 | = |
| 3.13 Lien code–preuves | S → renvoi à A.2 | Agent E | 1 → 0 |

**Ch. 4, résultats (34 → 28 sans nouvelle expérience)**

| Section (p.) | Action | Justification | p. actuel → cible | Risque |
|---|---|---|---|---|
| 4.1 Cadre de lecture (84) | R + A : une note annonce que chaque étiquette renvoie à A.2 | L2 §2.5, jargon | 1 → 1 | — |
| 4.2 CICIDS2017 (85–87) | **R (expérience en cours, P0)** : défaut d'échantillonnage de la campagne d'origine déclaré ; protocole corrigé décrit ; tableau des cinq candidats et 0,1577 **remplacés par les résultats d'E-CICIDS-HOLDOUT-FIX, quels qu'ils soient** (aucun chiffre avant exécution) ; anciens chiffres gardés seulement dans A.2, marqués « défaut d'échantillonnage, non retenu » ; phrase « CSV non corrigés » justifiée (Agent C §4) ; contrôle Isolation Forest (Agent 6 de la révision précédente) conservé | Défaut confirmé (§0) ; L2 §2.2 | 3 → 2 | Effacer le constat sur le protocole : il reste établi par le passage de l'aléatoire au temporel |
| 4.3 HDFS (88–90) | R : « identique pour les cinq graines » ; IC à quatre décimales ; raison des 6 000 blocs ou sensibilité non évaluée ; phrase sur la prévalence ; HBOS et baseline univariée (Agent D §4) | L2 §2.2 ; Agent C §6 | 3 → 2,75 | — |
| 4.4 BGL (91–94) | R : protocole principal présenté comme « Histogram = règle de sévérité » ; tableau 4.5 et protocole G **en annexe**, avec leur titre « variantes exploratoires conçues après lecture du test » ; légende « test et seuil indépendants » corrigée (Agent C §5) | L2 §2.2, chemins multiples | 3 → 2 | Présenter G comme un résultat |
| 4.5 Comparaison à la littérature (94) | F avec 4.3–4.4 | Agent E | 1 → 0,5 | — |
| 4.6 CSE-CIC-IDS2018 (95–100) | **R → 2 p. ou S (décision 2)** ; figures 4.8 à 4.11 en un tableau ; coefficients et permutation en annexe | L2 §2.2, §4.3 | 6 → 2 (ou 0) | Retirer sans mettre à jour H4 et les résumés |
| 4.7 Routeur open-set (101–102) | R : circularité ; IC de calibration ; une seule mention de 20/20 et 3/46 | L2 §2.2 | 1,5 → 1,25 | — |
| 4.8 Spécialisation (102–103) | R : « mêmes données corrigées » → « chargées sans la fuite » ; unité de l'IC = moyennes par graine, n = 5 (Agent B, B13) ; Linux/auth présenté comme corpus synthétique public (Kaggle, Faker), avec le mandataire possible `status`/`service` (Agent C §2.2) | L1 §B.2, §E.1 ; L2 §2.2 | 1,5 → 1,5 | — |
| 4.9 Multi-format (103–104) | R : « 7 001 dont une fixture Apache d'une ligne » ; aucun jeu Apache réel | L2 §2.4 ; L1 §B.4 | 1 → 1 | — |
| 4.10 Benchmark A–D, panne, E-CNP, E-H5, E-CNP-LL (104–109) | R : tableaux E-CNP et E-CNP-LL fusionnés ; paragraphe causal sur les pertes (Agent B §5.1) ; biais du comparateur, en un seul endroit (§5.2) ; niveaux d'E-H5 justifiés (§6.1) ; deux charges sur quatre dans `tab:benchmark-debit` ; phrase « Ces débits portent sur des microtâches » (P3 non fait) | L1 §C.1–C.3 ; L2 §2.2 | 6 → 5 | Retirer la fusion de l'intervalle de confiance |
| 4.11 Bout en bout (110) | C | — | 1 → 1 | — |
| 4.12 Multi-VM (111–114) | R : paragraphe unique sur la distribution (Agent B §6.2) | L1 §C.4 ; L2 §2.2 | 4 → 3,25 | — |
| 4.13 Corrélation (115) | R : demi-phrase « circuit fermé » avec renvoi aux limites | L2 §2.2 | 1 → 0,75 | — |
| 4.14–4.15 Mise à jour, règles simples (116) | R : ligne CICIDS holdout retirée (ou remplacée par P0) ; ligne CSE-CIC selon la décision 2 ; réserve HBOS | §0 | 1 → 1 | — |
| 4.16 Synthèse (117) | S → synthèse unique du ch. 6 | L1 §F | 1 → 0 | — |

**Ch. 5, validité scientifique (7 → 5,5)**

| Section | Action | Justification | p. |
|---|---|---|---|
| 5.1–5.6 | R, condensés. **Ajouts** : (i) l'audit des chargeurs et le défaut CICIDS, avec la phrase de l'Agent C §2.3 selon que les tests anti-fuite sont faits ou non ; (ii) le préenregistrement, avec la formulation de l'Agent C §7, une seule fois ; (iii) les comparaisons multiples : Bonferroni ne change aucune décision d'E-H5, E-CNP ni E-CNP-LL (Agent B, `sensibilite_bonferroni_sortie.txt`) ; (iv) les graines ne sont pas des environnements indépendants (L1 §E.1) | L1 §E.1–E.2 ; L2 §2.2 | 4 → 3,5 |
| 5.7 Conclusions soutenues | S → synthèse unique du ch. 6 | L1 §F | 1 → 0 |
| 5.8 Limites | **C, comme section unique des limites**, mise à jour : CICIDS, Linux/auth, CSE-CIC, routeur, corrélation, distribution, absence d'analyse conjointe | Règle 2 | 2 → 2 |

**Ch. 6, discussion (6 → 7,5)**

| Section | Action | Justification | p. |
|---|---|---|---|
| **A 6.1 Ce qui est implémenté, testé et effectivement supérieur** (nouvelle) | A | L1 §F | +2,5 |
| 6.1 actuel, score et validité du protocole | R, sans 0,1577 | §0 | 1 → 0,75 |
| 6.2–6.6 | F en deux sections : « Agents ou mécanismes simples » (thèse E1/E2 : idempotence, moindre chargé, mémoire) et « Hétérogénéité, normalisation, corrélation » ; chiffres renvoyés au ch. 4 | L2 §2.5 | 4 → 3 |
| 6.7 Contribution | R : paragraphe de l'Agent D §5 | L1 §D ; L2 §2.6 | 0,5 → 0,75 |
| 6.8 Prolongements | C, réduit | — | 0,5 → 0,5 |

Contenu de la nouvelle section 6.1. C'est un tableau d'une ligne par mécanisme, suivi d'un court paragraphe par mécanisme. Aucun chiffre nouveau : renvoyer au ch. 4.

| Mécanisme | Implémenté | Testé (comparateur, section) | Effectivement supérieur à l'alternative simple ? | Origine du contenu actuel |
|---|---|---|---|---|
| Lecture et normalisation | Adaptateurs, schéma commun | Lecture et émission ; remplissage par source (4.9) | Sans objet (exigence R1) ; remplissage nul pour les flux tabulaires | tableau 1.6 ; 4.16 ; QR1 de la conclusion |
| Routage | Routeur open-set | Rejet des inconnus, faux rejets (4.7) ; chaîne sans routage **non exécutée** (sauf P1) | Non établi | tableau 7.1, H3 ; 5.7 |
| Spécialisation | Modèles par famille | Non-infériorité contre un modèle commun (4.8) | Non établi (CICIDS) | tableau 7.1 ; 6.2 |
| Détection | HBOS (Histogram), LR, RF, IF | Règles simples sur le même test (4.15) | Non : H4 réfutée dans le périmètre testé | 4.15 ; 5.7 ; 6.1 |
| Négociation Contract Net | Appel d'offres, utilité | Table statique, moindre chargé (4.10) | Non : aucun avantage face au moindre chargé, dans un seul processus | 6.3 ; tableau 1.6 |
| Reprise sans doublon | Magasin d'idempotence | Panne appariée A–D ± idempotence (4.10) | L'effet vient du magasin, pas des agents | 6.4 ; tableau 7.1, H2 |
| Mémoire | Compteur de Laplace | Mémoire activée ou non sous fiabilité hétérogène (4.10) | Seulement à p = 0,9, avec une moindre équité | 6.6 ; tableau 7.1, H5 |
| Distribution | Deux VM, Redis | Endurance, saturation, HDFS réparti (4.12) | Exécution répartie démontrée ; capacité non accrue | 4.12 ; 7.5 |
| Corrélation | Corrélateur hôte + fenêtre | Baselines, corpus synthétique (4.13) | En circuit fermé seulement | 6.5 ; tableau 1.6 |
| Gouvernance, interface | Promotion, tableau de bord | Essai à blanc ; aucune mesure auprès d'analystes | Non vérifié (R3) | 6.6 ; 4.14 |

**Ch. 7, reproductibilité (4 → 2,5)**

| Section | Action | Justification | p. |
|---|---|---|---|
| 7.1–7.4 | F : formulation unique de l'Agent F §6.1 ; paramètres renvoyés à A.4–A.6 | L1 §E.3 ; L2 §2.5 | 2,5 → 1,25 |
| 7.5 Environnement multi-agent | F avec A.5 | — | 0,5 → 0,25 |
| 7.6 Disponibilité | R : texte de l'option choisie (Agent F §4.5) ; phrase sur l'antériorité, ici ou au ch. 5, une seule fois | L2 §4.1 | 0,5 → 0,75 |
| 7.7 Frontière d'exploitation | S → section des limites | Règle 2 | 0,5 → 0,25 |

**Conclusion (7 → 5)** : bilan resserré ; réponses aux QR en un paragraphe chacune, avec renvoi au tableau unique ; corrections de l'Agent A §5.2 (« sait normaliser », « multi-source », « aucune des cinq hypothèses ») ; H4 réfutée dans le périmètre testé ; « Limites » remplacé par un renvoi.

**Annexe A (11 → 9)**

| Section | Action | p. |
|---|---|---|
| A.1–A.2 Messages | C | 1,5 |
| A.3 Matrice résultats–preuves (tableau A.2) | R : seul endroit des run_id ; colonne d'étiquette lisible ; lignes CICIDS holdout marquées « défaut d'échantillonnage, non retenu » ; ligne Linux/auth avec sa provenance | 4 → 4 |
| A.4–A.8 | F (A.8 fondue dans le ch. 5) | 2,5 → 1,5 |
| A.9 Notes des figures | **S** : doublon des légendes (Agent E) | 3,5 → 0 |
| A (nouvelles) : variantes BGL ; détail CSE-CIC (si conservé) ; description des tests anti-fuite (si faits) | A | +2 |

**Bibliographie (5 → 6)** : environ 11 entrées ajoutées, 2 retirées (LOF, OCSVM), DOI imprimés (§4).

### 2.3 Bilan des pages

| Partie | Actuel | Cible | Écart |
|---|---|---|---|
| Liminaires | 23 | 20 | −3 |
| Introduction | 15 | 12 | −3 |
| Ch. 1 | 30 | 22 | −8 |
| Ch. 2 | 28 | 23 | −5 |
| Ch. 3 | 10 | 9 | −1 |
| Ch. 4 | 34 | 28 (26 si §4.6 est retiré) | −6 |
| Ch. 5 | 7 | 5,5 | −1,5 |
| Ch. 6 | 6 | 7,5 | +1,5 |
| Ch. 7 | 4 | 2,5 | −1,5 |
| Conclusion | 7 | 5 | −2 |
| Annexe | 11 | 9 | −2 |
| Bibliographie | 5 | 6 | +1 |
| **Total** | **180** | **≈ 149,5** | **≈ −30,5** |

Réconciliation des estimations des agents :
- Le gain du ch. 1 est compté une seule fois. L'Agent D annonçait −9 net et l'Agent E −8, pour la même opération ; la part du tableau 1.6 qui réapparaît est comptée au ch. 6.
- Le gain de l'Agent A (−3,6) est inclus dans l'introduction et la conclusion.
- Celui de l'Agent C (−4 avec CSE-CIC réduit) est inclus au ch. 4.
- Celui de l'Agent B (−1,2) est inclus aux ch. 4 et 6.
- L'Agent F est neutre.
- Le bilan de l'Agent E (« ≈ 151 ») contenait une erreur d'addition : ses lignes donnaient −33, et non −29. Le tableau ci-dessus le remplace.

Les estimations sont à ±3 pages ; seule une compilation dira le total réel. Si P1, P2 et P3 sont exécutés (environ +2,5 p.), compenser en passant en annexe la figure du bootstrap HDFS et la figure de couverture du routeur, ou en retirant §4.6 si la vérification CSE-CIC n'est pas faite.

---

## 3. Expériences à exécuter avant la soutenance

**Préalable, valable pour toutes.** Un protocole commité dans un dépôt local ne prouve son antériorité que localement : l'historique peut être réécrit, et rien d'extérieur ne l'horodate (Agent C §7 ; aujourd'hui, `origin/main` = `35da3a9`). Pour chaque protocole : (1) le commiter avec l'empreinte de son runner ; (2) **le pousser vers le dépôt distant, ou l'archiver sur Zenodo, avant l'exécution** ; (3) exécuter. Pousser aujourd'hui les commits du 5 novembre fige l'état actuel, sans rien prouver de façon rétroactive.

| # | Expérience | Critère de succès fixé a priori | Durée estimée (non mesurée) | Formulation si elle n'est pas faite |
|---|---|---|---|---|
| P0 | **Holdout CICIDS2017 corrigé, E-CICIDS-HOLDOUT-FIX : EN COURS** (décision de l'auteur ; protocole préparé et exécuté par le coordinateur, qui fait foi sur les critères ; les éléments ci-contre sont ceux que l'intégration recommandait). Même partition par scénario ; entraînement tiré au hasard **dans chacun** des fichiers d'entraînement, avec une graine qui change la sélection ; test sans plafond, à sa prévalence naturelle ; seuil calibré sur une validation interne à l'entraînement (Agent B §3.1, appliqué au chargeur corrigé) ; tests `test_sampling_coverage` et `test_seed_changes_selection` (Agent C §2.3) au vert avant exécution | Un modèle « dépasse tout positif » si la borne inférieure de l'IC de la différence par scénario (n = 5) est > 0, avec α = 0,01 (Bonferroni, cinq modèles). Sinon, la ligne est réintégrée à la réfutation de H4 | ½ à 1 jour | Phrase « si non faits » de l'Agent C §2.3, et protocole corrigé décrit en 4.2 |
| P1 | **H3, chaîne sans routage** : 66 fichiers open-set, bras R contre N (Agent B §2, P1) | H3 soutenue si la borne supérieure de l'IC à 97,5 % du Δ du taux d'incompatibilité est < 0 **et** si la borne inférieure de l'IC du ΔF1 est ≥ −0,01 ; réfutée si la borne inférieure du Δ du taux est ≥ 0 ou si la borne supérieure du ΔF1 est < −0,01 ; non tranchée sinon. Bootstrap par grappe ; connus et inconnus présentés séparément | 1 à 2 jours | « La chaîne sans routage n'a pas été exécutée […] faute de temps, non par impossibilité ; H3 reste non tranchée » (Agent B) ; retirer l'argument des « 90 sources », qui relève d'E-H3 |
| P2 | **H2, agents sans idempotence** : C, D, C−I, D−I ; 40 tâches ; 10 répétitions | Soutenue si C et D ont 0 doublon sur 10 exécutions sur 10, et C−I et D−I au moins un doublon sur 10 exécutions sur 10 ; réfutée sinon (détail à l'Agent B) | < 2 h | « L'exécution à agents sans magasin n'a pas été réalisée ; le doublon attendu découle du code » |
| P3 | **Benchmark A–D sur une inférence HDFS réelle** : bras A, B, C et moindre chargé ; 1, 10 et 100 blocs par tâche ; 30 graines | Coût négligeable si la borne inférieure de l'IC du rapport C/B est ≥ 0,90, substantiel si la borne supérieure est < 0,90, indéterminé sinon. Bonferroni sur 6 comparaisons. Aucune conclusion de supériorité de C n'est prévue | 1 à 2 jours, plus 1 à 3 h d'exécution | « Ces débits portent sur des microtâches […] ce rapport n'a pas été mesuré » (Agent B) |
| V1 | **Tailles CSE-CIC sur S3** (vérification, pas une expérience) | Tailles égales à 375 945 899 et 333 723 605 octets → fichiers identiques à la distribution officielle | 5 min | Retrait de §4.6 (Agent C §3) |
| V2 | **Pertes de Contract Net, diagnostic** (optionnel) : rejouer s2 et s3 en journalisant `refusals` et `ranked` | Mécanisme confirmé si ≥ 95 % des tâches perdues ont au moins un agent non défaillant refusé pour `agent_overloaded` | ½ jour | Paragraphe causal de l'Agent B §5.1, l'explication des 50 pertes de D restant une hypothèse |
| T | **Tests anti-fuite** (Agent C §2.3), à lancer avant toute nouvelle exécution | Les six tests passent ; `test_sampling_coverage` doit échouer sur le chargeur actuel, ce qui sert de contrôle | ½ jour | Phrase « si non faits » de l'Agent C |

Ordre recommandé : V1, puis pousser les commits, puis T, puis P0 (en cours) et P2, puis P1, puis P3. Si une seule autre expérience est possible : P1, la plus informative pour la thèse (Agent B).

**Ne pas utiliser** les recalculs CICIDS de l'Agent B (§3.3 : 0,5876, 0,5491, etc.). Ils portent sur le holdout défectueux.

---

## 4. Corrections formelles et bibliographiques

1. **DOI non imprimés** : 34 des 57 entrées ont un champ `doi`, mais `plain-fr.bst` ne l'affiche pas. Copier ce style en `plain-fr-doi.bst` et y ajouter `format.doi` (Agent E §7.1). C'est la solution la moins risquée.
2. **Références à ajouter** (Agent D §3, vérifiées en ligne) :
   - Mitzenmacher 2001 et 2000, Azar et al. 1999, Jiang 2016, Dias et al. 2006 ;
   - Moustafa et Slay 2015 et 2016, Lippmann et al. 2000, McHugh 2000 ;
   - Goldstein et Dengel 2012 (HBOS, sans DOI) ;
   - Winston 1977 ;
   - à citer : `hmimou2025multiagent` et `song2024auditllm`, déjà présentes dans le `.bib` mais jamais citées.
3. **À vérifier avant d'entrer dans le `.bib`** :
   - le DOI de Winston 1977 sur cambridge.org ;
   - la liste des auteurs de Lippmann 2000 sur IEEE Xplore ;
   - le DOI de Moustafa et Slay 2016 sur Taylor & Francis ;
   - le contenu de Hmimou 2025 et de Song 2024, pour la phrase sur l'allocation ;
   - les DOI marqués « à vérifier » de l'Agent E §7.2 (RFC 5424, arXiv, Information Fusion, LNCS).

   Aucun de ces DOI n'entre dans le `.bib` sans contrôle.
4. **Linux/auth** : ajouter une entrée `@misc` pour le jeu Kaggle « linux_auth_log-anomalies » (LİN ÇORBACI, Kaggle, 2025, licence MIT, `https://www.kaggle.com/datasets/lnorbaci/linux-auth-log-anomalies`, version utilisée et date d'accès à confirmer par l'auteur). La note précise « jeu synthétique, généré avec la bibliothèque Faker ». Le présenter en 1.8 comme corpus synthétique public.
5. **Références retirées** : LOF (`breunig2000lof`) et One-Class SVM (`scholkopf2001estimating`).
6. **Documentation web** (11 entrées) : à regrouper sous « Documentation technique et jeux de données ». Une seule graphie, « consulté le ». Dates de consultation réelles, sans antidater : si l'auteur reconsulte les pages, mettre la nouvelle date.
7. **Sharafaldin** : une demi-phrase en 1.8. Le CIC demande cette citation pour les deux jeux ; ne pas dupliquer l'entrée.
8. **Identifiants** : liste de l'Agent E §4 (18 run_id et 7 codes de protocole), avec une étiquette lisible pour chacun.
9. **Précision** : huit écarts listés par l'Agent E §5. « 89,8081 % » devient 89,81 %.
10. **Tableaux** : 1.4 supprimé, 1.5 réduit, 7.1 remplacé par le tableau unique ; statuts écrits partout dans la même casse.
11. **Conditionnel du ch. 2** : passe complète (57 occurrences).
12. **« Hétérogène »** (environ 35 occurrences) et **« intelligent »** : qualifier ou retirer (Agent A §5.2 ; Agent D §7).
13. **Contrôle final** : `grep` des valeurs répétées (au plus une occurrence détaillée hors du ch. 4) ; `grep` des run_id ; compilation complète `pdflatex` → `bibtex` → `pdflatex` ×2 ; aucune référence indéfinie, aucun débordement.

---

## 5. Note de dosage de la déclaration IA

**Formulation proposée** : celle de l'Agent F §3.2, reprise sans changement sur le fond. Les quatre passages `[À CONFIRMER PAR L'AUTEUR : …]` sont conservés et doivent être attestés ou supprimés par l'auteur avant intégration.

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

Deux ajustements de cohérence, à faire au moment de l'intégration, qui ne changent pas le fond :
- Le holdout CICIDS étant réexécuté, la phrase « ceux qu'un défaut de script invalidait ont été retirés » devient « … ont été retirés ou réexécutés après correction ». Ajouter E-CICIDS-HOLDOUT-FIX à la liste des protocoles versionnés avant exécution, à condition que ce soit vrai au moment de l'intégration.
- Si E-H3b reste nommée, préciser « E-H3b, écartée pour un défaut de chargement ».

**Pourquoi cette version est moins accablante sans être moins vraie.**
- La version actuelle énumère, outil par outil, ce que les outils ont fait, puis réduit le rôle de l'auteur à une phrase générique. Le lecteur 2 y a donc lu une délégation intégrale.
- La version proposée garde chaque usage déclaré : écriture du code, rédaction et exécution des protocoles, reformulation. Elle le place en regard des décisions que les traces attribuent à l'auteur : les objectifs, les questions de positionnement, le lancement des campagnes complémentaires, le choix du moindre chargé et de la partition stricte, l'exclusion du scénario conjoint, la validation des statuts (C13, C17 à C20).
- Elle dit aussi le calendrier sans le cacher. Les dates restent visibles dans les artefacts et le dépôt ; les taire passerait pour une dissimulation.
- Ce qu'elle ne fait pas : attribuer à l'étudiant la conception des protocoles E-H5, E-CNP ou E-CNP-LL. Les traces montrent qu'ils ont été rédigés par des agents d'IA (Agent F §2.2). L'écrire serait faux et se verrait en soutenance.
- La part personnelle se démontre oralement, avec les justifications rédigées de la main de l'auteur (Agent F §5).

---

## 6. Checklist de conformité

Statuts : R, X, A, L (voir §1). « Fondé », « partiellement fondé », « déjà traité » et « inexact » reprennent le classement des agents. La dernière colonne renvoie à la section du présent plan.

### Lecteur 1

| Reproche | Classement | Statut | Plan |
|---|---|---|---|
| §1 Pas de supériorité propre de l'architecture | Fondé | R + L : thèse E1/E2, synthèse unique | §2.2 intro, ch. 6 |
| §A.1 Problématique dispersée | Fondé | R | intro |
| §A.1 Exigences fonctionnelles présentées comme hypothèses | Fondé | R : R1, R2, R3 | intro ; décision 4 |
| §A.2 Aucune hypothèse validée ; sur quoi repose la contribution ? | Fondé | R + L : tableau unique, contribution recadrée | §1.1 n° 1 ; ch. 6.7 |
| §A.3 Préenregistrement partiel ; grandeurs non fixées | Fondé, déjà déclaré | R : grandeurs pour l'avenir seulement, aucune application rétroactive | intro |
| §A.3 Confirmatoire de campagne ≠ de programme | Fondé | R : phrase d'honnêteté E1/E2 ; formulation de l'Agent C §7 | intro ; ch. 5 |
| §B.1 Modèles ne dépassant pas les règles simples | Fondé | R : H4 réfutée dans le périmètre testé (périmètre restreint, §0) | §0 ; ch. 4.15 |
| §B.2 Spécialisation : gains faibles, condition oracle | Fondé, déjà rapporté | L (+ X : P1 pour le routage effectif) | ch. 4.8 ; §3 |
| §B.3 Contamination E-H3b ; audit et tests anti-fuite | Fondé ; audit fait par l'Agent C, défaut CICIDS trouvé | R + X (T, P0) | §0 ; ch. 5 ; §3 |
| §B.4 Multi-format superficiel ; Apache sur une ligne ; 0 champ ; pas d'analyse conjointe | Fondé | R + L | ch. 4.9 ; conclusion |
| §C.1 Contract Net sans avantage ; comparateur avantagé | Fondé, déjà rapporté | R : biais en un seul endroit ; littérature d'équilibrage de charge | ch. 4.10 ; ch. 1.9 |
| §C.2 Mémoire seulement à p = 0,9 ; indice de Jain | Fondé | R : niveaux justifiés, phrase unique | ch. 4.10 |
| §C.3 Pertes de tâches, analyse causale | Fondé ; cause trouvée | R (+ V2) | ch. 4.10 ; §3 |
| §C.4 Distribution ≠ scalabilité | Fondé, déjà rapporté | R + L : paragraphe unique | ch. 4.12 |
| §D Originalité limitée ; intégration de mécanismes connus | Fondé | R + L : contribution étroite, assumée | ch. 6.7 |
| §D Titre acceptable, pas de revendication de supériorité | — | R : titre proposé (décision 3) | liminaires |
| §E.1 Graines ≠ environnements indépendants | Fondé | L : phrase en ch. 5 | ch. 5 |
| §E.1 Mesures corrélées dans E-H3B-STRICT | Déjà traité dans le code (n = 5) | R : une phrase | ch. 4.8 |
| §E.2 Commits antérieurs aux exécutions ; runner modifié | Vérifié localement (Agent C §7) ; runner d'E-H4 corrigé, documenté | R + A (pousser) | ch. 5 ; §3 |
| §E.3 Empreinte ≠ reproductibilité ; dépôt non disponible | Fondé | R + A : formulation unique, dépôt | ch. 7 ; décision 7 |
| §F Fragmentation en 26 + 26 sections | Fondé | R : 11 et 9 sections | ch. 1, ch. 2 |
| §F Distinction implémenté / testé / supérieur dispersée | Fondé | R : synthèse unique | ch. 6.1 nouveau |
| §F Contrôle de provenance des scripts | Fondé | A : chronologie de l'Agent F, dépôt, soutenance | §5 ; décision 6 |
| §F Plagiat : contrôle textuel externe nécessaire | Hors de portée du chantier | L (contrôle institutionnel) | — |
| §5 Objections 1 à 4 | — | Voir §1.1 et décisions 3, 4, 7, 8 | §1 |

### Lecteur 2

| Reproche | Classement | Statut | Plan |
|---|---|---|---|
| §1/§3.1 Aucune contribution positive ; QR6 réplique la littérature | Partiellement fondé : les comparaisons architecturales sont propres au travail (Agent A §2.3) | R + L | ch. 6.7 |
| §2.1 Question descriptive | Fondé | R : thèse E1/E2 | intro |
| §2.1 H1 et H2 tautologiques | H2 fondé ; H1 inexact, c'est une exigence et non une tautologie | R : R1, R2 (+ X : P2) | intro ; §3 |
| §2.1 H3 à H5 non opérationnalisées ; « non tranché » garanti d'avance | Partiellement fondé : la supériorité de H4 et H5a étaient tranchables et ont été tranchées | R + L | intro |
| §2.1 Six QR pour cinq hypothèses ; QR4 sans mesure | Fondé | R : QR4 supprimée | intro ; décision 4 |
| §2.1/§4.4 Titre « hétérogènes » | Partiellement fondé | R + A | décision 3 |
| §2.2 Benchmark A–D sur microtâches | Fondé | X (P3) ou L | §3 ; ch. 4.10 |
| §2.2 Cinq modèles au seuil par défaut | Fondé ; traité par la réexécution (seuil calibré si le protocole du coordinateur le prévoit) | X (P0, en cours) | §0 ; ch. 4.2 |
| §2.2 Plafonds 8 000/4 000 | Fondé ; aggravé par la sélection des premières lignes | R + X (P0) | ch. 4.2 |
| §2.2 Poids d'Infiltration | Inexact quant à l'effet (Agent B), recalcul sur le holdout défectueux, donc à ne pas citer | X (P0, en cours) : pondération à rapporter sur les nouveaux résultats | §3 |
| §2.2 « Tout positif » bat les candidats : protocole mal conçu | **Fondé**, et la cause est plus grave que le seuil : un seul scénario d'entraînement | R + X | §0 |
| §2.2 CSV CICIDS2017 non corrigés ; « mêmes données corrigées » | Fondé (choix à justifier ; formulation) | R | ch. 4.2, 4.8 |
| §2.2 CSE-CIC-IDS2018 possiblement tronqué | Fondé (2²⁰ lignes physiques) | A (V1) puis R | décision 2 |
| §2.2 BGL dégénéré | Fondé, déjà décrit | R : présenté comme la règle de sévérité | ch. 4.4 |
| §2.2 BGL : chemins multiples, protocole G, tableau 4.5 | Fondé | R : annexe, légende corrigée | ch. 4.4 ; annexe |
| §2.2 Graines HDFS : une seule observation | Déjà traité pour l'essentiel | R : « identique pour les cinq graines » | ch. 4.3 |
| §2.2 6 000 blocs sans justification | Partiellement traité | R : raison donnée, ou sensibilité déclarée non évaluée | ch. 4.3 |
| §2.2 Prévalence test ≠ validation | Déjà traité | R : effet sur le F1 | ch. 4.3 |
| §2.2 Préenregistrement auto-certifié | Fondé (aucune ancre externe) | R + A (pousser, archiver) | ch. 5 ; §3 |
| §2.2 E-CNP-LL décidé après lecture | Fondé, déjà déclaré | L | ch. 4.10 |
| §2.2 Artefacts datés du jour de la compilation | Fondé | R : phrase de calendrier dans la déclaration IA | §5 |
| §2.2 Comparateur H2 non exécuté | Fondé | X (P2) ou L | §3 |
| §2.2 Comparateur H3 non exécuté ; argument Loghub | Fondé ; l'argument des « 90 sources » relève d'E-H3 | X (P1) ou L | §3 |
| §2.2 Routeur partiellement circulaire ; calibration sur 3 inconnus | Déjà déclaré ; conséquence non tirée | R | ch. 3.4, 4.7 |
| §2.2 Corrélation en circuit fermé ; 16 anomalies | Déjà déclaré | L | ch. 4.13 ; limites |
| §2.2 Distribution : 0,5 tâche/s ; 1,23 % ; 100 % sur debian-alpha ; trace tronquée | Fondé, déjà rapporté | R : paragraphe unique | ch. 4.12 |
| §2.2/§3.7 Fuite trouvée par hasard ; autres campagnes non auditées | Fondé ; audit fait, défaut CICIDS trouvé | R + X (T) | §0 ; ch. 5 |
| §2.2 Aucune correction pour comparaisons multiples | Fondé ; sans effet sur les décisions (Bonferroni) | R | ch. 5 |
| §2.2 (barème) Un seul processus | Fondé | L : biais du comparateur | ch. 4.10 |
| §2.3 Catalogue ; LOF et One-Class SVM inutilisés | Fondé | R : supprimés | ch. 1 |
| §2.3 Extra Trees et gradient boosting sans lien | Partiellement fondé : ils sont utilisés | R : lien écrit | ch. 1 |
| §2.3 Littérature d'allocation absente | Fondé | R : paragraphe et références | ch. 1.9 ; §4 |
| §2.3 Aucun travail MAS récent pour SOC/IDS | Fondé dans le PDF | R : citer Hmimou 2025, Song 2024 | §4 |
| §2.3 Histogram sans filiation | Fondé | R : HBOS | ch. 1, ch. 3 |
| §2.3 Agent vidé de sens ; utilité à termes constants ; « intelligent » | Fondé | R : définition plus modeste, mot retiré | intro ; §4 n° 12 |
| §2.3/§4.5 Jeux non cités | Fondé | R (Linux/auth identifié : Kaggle, synthétique) | §4 |
| §2.4 « Sait normaliser » ; 7 001 gonflé par Apache | Fondé | R | conclusion ; ch. 4.9 |
| §2.4 Résultats dans le ch. 1 | Fondé (10 passages) | R | ch. 1 |
| §2.4 E-H5 crée les conditions de son seul gain | Fondé, déjà rapporté | R : niveaux justifiés, gain limité | ch. 4.10 |
| §2.4 Ch. 2 au conditionnel | Fondé (57 occurrences) | R | ch. 2 |
| §2.5 Chiffres répétés | Fondé (7 001 : 14 occurrences) | R : règle 1 | §2.1 |
| §2.5 Ch. 7 et A.3 redoublent les ch. 4 et 5 | Partiellement fondé : A.3 est légitime ; A.9 est le vrai doublon | R | ch. 7 ; annexe |
| §2.5 Résumé en liste de chiffres | Fondé | R | liminaires |
| §2.5 Bokuse divergent | Fondé (9 divergences) | R + A (C19) | liminaires |
| §2.5 Identifiants internes | Fondé | R | §2.1 règle 5 |
| §2.5 Précision incohérente | Fondé, limité (8 écarts) | R | §4 n° 9 |
| §2.5 Bibliographie web ; dates ; aucun DOI | Partiellement fondé : 11 entrées web sur 57 ; DOI présents mais non imprimés | R | §4 |
| §2.5 Sharafaldin pour deux jeux | Inexact en tant que défaut | R : demi-phrase | §4 n° 7 |
| §2.5 Tableaux 1.4, 1.5 et 7.1 illisibles | Fondé | R | §4 n° 10 |
| §2.6 Quatre résultats négatifs ; banc d'essai sans contribution | Partiellement fondé | R + L : contribution étroite, assumée | ch. 6.7 |
| §2.7 Déclaration IA accablante | Fondé quant à l'effet produit | R + A | §5 ; décision 6 |
| §2.7 Calendrier ; campagnes des 48 dernières heures | Fondé pour les six protocoles ; partiellement pour l'ensemble (15 campagnes de septembre) | R | §5 |
| §2.7 Part intellectuelle non démontrable | Fondé | A (soutenance, `PREPARATION_SOUTENANCE.md`) | décision 6 |
| §2.7/§4.1 Aucun dépôt | Fondé | **A (bloquant)** | décision 7 |
| §4.2 Attestation de l'apport personnel | Fondé | A | décisions 6 et 9 |
| §4.3 Intégrité de CSE-CIC | Fondé | A puis R | décision 2 |
| §4.4 Titre et conclusion | Fondé | R + A | décision 3 |
| §4.5 Références des jeux | Fondé | R | §4 |

**Limites résiduelles acceptées**, déclarées une seule fois dans la section des limites :
- pas d'analyse conjointe système/réseau ;
- pas de comparaison distribuée de Contract Net ;
- corrélation en circuit fermé ;
- pas de mesure auprès d'analystes ;
- validité externe des graines ;
- corpus Linux/auth synthétique (aucune validité pour des journaux réels) ;
- pas de reproduction par un tiers ;
- contrôle de plagiat institutionnel.

---

## 7. Corrections aux livrables des agents, à appliquer à l'intégration

- **Agent E §3.1 (résumé) et Agent D §5 (contribution)** : remplacer 0,9951 → 0,1577 par 0,9951 → 0,4374 (temporel) ; « sur les quatre jeux publics » devient « sous les protocoles stricts retenus ».
- **Agent A §4 (ligne QR5) et §3.2 (H4)** : « supériorité infirmée sur les quatre jeux » devient « réfutée dans le périmètre testé (§0) ».
- **Agent B §3** : recalculs de pondération à ne pas intégrer (holdout défectueux) ; la calibration se fait dans P0, sur un échantillonnage corrigé.
- **Agent F §6.2, étape 2** : le recalcul proposé (0,473265, holdout CICIDS) porte sur le résultat défectueux. Le remplacer par le recalcul du F1 HDFS à partir de la matrice de confusion : TP 1 679, FP 509, FN 0, donc F1 = 2 × 1 679 / (2 × 1 679 + 509) = 0,868373 (`agent2_hdfs_full_20261104T131314Z`).
- **Agent E §2.3** : bilan « ≈ 151 » remplacé par le §2.3 du présent plan.

=== PASSATION ===
Agent : intégration — Plan de refonte 150 pages
Statut : terminé ; plan seulement, aucun `.tex` modifié
Livrable : `revision_reports/refonte_150p/PLAN_REFONTE_150P.md`
Étape 0 : défaut CICIDS2017 confirmé, par le code et par le comptage des 100 000 premières lignes de DDoS et PortScan. H4 reste réfutée sur les protocoles valides (CICIDS temporel, HDFS, BGL, et CSE-CIC sous réserve de V1), mais pas sur le holdout.
Prochaine étape : décisions 1 à 10 de l'auteur (§0), puis application lot par lot dans cet ordre : ch. 4 et 5, puis introduction, ch. 1, ch. 2, ch. 3, ch. 6, ch. 7, conclusion, liminaires, annexe et bibliographie. Compiler après chaque lot.
Vigilance : insérer les résultats d'E-CICIDS-HOLDOUT-FIX, quels qu'ils soient, à la place des anciens chiffres ; aucun chiffre avant leur publication par le coordinateur ; ne pas attribuer à l'étudiant la conception des protocoles complémentaires ; ne faire entrer dans le `.bib` aucun DOI marqué « à vérifier ».
=== FIN PASSATION ===
