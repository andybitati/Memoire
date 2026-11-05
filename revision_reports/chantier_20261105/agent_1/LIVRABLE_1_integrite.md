# LIVRABLE 1 — Intégrité factuelle et cohérence documentaire

Agent 1, chantier de révision du 2026-11-05. Document autoportant : un repreneur n'a besoin que de ce fichier, du dossier `sections/` voisin et des fichiers du dépôt cités.

Statut : **terminé** (toutes les tâches du périmètre sont traitées ; deux décisions sont renvoyées au coordinateur, §8).

---

## 1. Périmètre traité

Périmètre fixé par `MISSION.md` (section « Agent 1 ») et par le tableau C5 de `ETAT_CHANTIER.md` :

| Élément (numérotation du PDF) | Fichier source | Lignes | Page PDF |
|---|---|---|---|
| Résumé | `main.tex` | 275-390 | vi-viii |
| Abstract | `main.tex` | 396-507 | ix-xi |
| Bokuse (lingala) | `main.tex` | 513-636 | xii-xiv |
| Introduction, « Positionnement… » (titre) | `chapters/chapitre1_introduction.tex` | 58 | 4 |
| Introduction, « Hypothèses de recherche » (préenregistrement) | `chapters/chapitre1_introduction.tex` | 147 | 7 |
| §1.8.2 CICIDS2017 (renvoi) | `chapters/chapitre2_etat_art.tex` | 336 | 22 |
| Tableau 4.2 (candidats CICIDS2017) | `chapters/chapitre5_resultats.tex` | 73-123 | 83 |
| §5.2 contre §4.6.4 | `chapters/chapitre6_approfondissements_scientifiques.tex` l. 19 ; `chapitre5_resultats.tex` l. 394-420 | | 108 ; 95 |
| §5.7 contre tableau A.4 | `chapitre6_approfondissements_scientifiques.tex` l. 118 ; `annexes.tex` l. 116-139 | | 112 ; 134 |
| Conclusion : QR3, QR6, tableau 7.1 | `chapters/chapitre6_conclusion.tex` | 28-38, 46-89 | 125-127 |
| Tableau A.2 (matrice résultats-preuves) | `chapters/annexes.tex` | 45-87 | 131-132 |
| Tableau A.3 (paramètres HDFS) | `chapters/annexes.tex` | 89-112 | 133 |
| Tableau A.4 (multi-VM) | `chapters/annexes.tex` | 114-139 | 134 (vérifié, exact, non modifié) |
| Annexe A.8 | `chapters/annexes.tex` | 167-169 | 135 |

Correspondance PDF / fichiers : `revision_reports/agent_7/PATCH_NOTES.md` ; pages établies par `main.toc` et `main.lot` (le PDF de 166 pages compilé le 2026-11-05 ; aucune bibliothèque d'extraction PDF n'est installée dans `.venv`).

## 2. Méthode

1. Lecture intégrale de `MISSION.md`, `RETOURS_LECTEURS.md` (trois lecteurs), `ETAT_CHANTIER.md`, `HANDOFF.md` §1 et §6.
2. Lecture intégrale des trois résumés, de l'introduction, des chapitres 4 (`chapitre5_resultats.tex`), 5, 6, 7, de la conclusion, des annexes et de `limites_consolidees.tex`.
3. Recherche systématique, dans `chapters/*.tex`, de chaque nombre des résumés (normalisation `{,}`, `\,`, `~` ; script `scratchpad/chk2.py`, non livré) pour distinguer les chiffres présents dans le corps de ceux qui ne figurent que dans les résumés.
4. Pour chaque chiffre : ouverture de l'artefact (CSV/JSON) et relecture de la valeur. Aucun chiffre n'a été recalculé autrement que par lecture ou par moyenne des lignes brutes d'un artefact.
5. Recherche active d'autres contradictions par motifs : `trois inconnus`, `28 connus`, `préenregistr`, `fixés avant`, `fuite triviale`, `non conclusif`, `refus`, `cinq hypothèses`, `réponse forte`, `0,892308`, `section~[0-9]`.
6. Rédaction des sections corrigées (`sections/`), sans modifier aucun `.tex` du mémoire (décision C1).

Abréviations de chemins utilisées ci-dessous (toutes relatives à `E:\Cours\TFE\`) :
[R] `experiments/phase_revision_20261104/` ; [D] `experiments/phase_dataset_strengthening/` ; [F] `experiments/phase_final_scientific_consolidation/` ; [M] `experiments/phase_multi_agent/` ; [E] `experiments/phase_cnp_endurance/` ; [P] `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/` ; [X] `data/processed/final_experiments_2026/`.

## 3. Tableau de correction ligne par ligne

Colonnes : n° ; localisation (page PDF, section, fichier:ligne) ; texte actuel (extrait exact) ; texte corrigé (ou renvoi au fichier de `sections/`) ; justification et source.

### 3.1 Résumés (`main.tex`) — fichiers `sections/main.tex__resume_fr.tex`, `__abstract_en.tex`, `__bokuse_ln.tex`

| n° | Localisation | Texte actuel | Texte corrigé | Justification / source |
|---|---|---|---|---|
| K01 | p. vii, Résumé, `main.tex:354-359` | « La campagne multi-VM (\texttt{multivm\_cnp\_20260909T202632Z\_37592}) exécute 60/60 tâches sur Debian et Ubuntu, réparties 30/30 […] Elle comprend 15 refus, un échec contrôlé, une réattribution réussie et un replay idempotent sans effet dupliqué. » | « Une campagne d'endurance d'une heure, sur deux machines virtuelles Debian et Ubuntu reliées à un Redis centralisé sur l'hôte du laboratoire, mène à terme 1 800 tâches sur 1 800, réparties 451 et 1 349 selon les profils de capacité configurés ; un arrêt contrôlé après persistance conduit à une réattribution et à un rejeu sans effet dupliqué. En saturation, la capacité de cette topologie se situe entre 8 et 16 tâches/s, et la seconde machine ne traite que 1,23 % des tâches réussies : elle n'augmente pas la capacité observée. » | La campagne 37592 n'apparaît dans aucun fichier `chapters/*.tex` (ni dans le commit `HEAD`) ; le corps (§4.11, tableau 4.8, tableau A.4, §7.6) présente `cnp_endurance_multivm_20260918T130822Z`. L'artefact 37592 **existe** et confirme 60/60, 30/30, 15 REFUSE, 1 FAIL, 1 réattribution, 0 effet dupliqué ([M] `raw/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.json`) : le résumé n'invente pas, il décrit une campagne que le corps ne présente pas. Chiffres de remplacement : [E] `aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json` (1 800/1 800 ; 451/1 349 ; reassignments 1 ; duplicate_effects 0) ; saturation [R] `agent_3_distribution/agent3_saturation_multivm_20261104T142325Z__saturation_tasks.csv` (11 430 tâches, 11 427 ok, Ubuntu 140 ok → 140/11 427 = 1,23 %) et corps §4.11.3. Option B (introduire 37592 dans le corps) : §8, Q1. |
| K02 | p. x, Abstract, `main.tex:473-478` | « The multi-VM campaign (\texttt{multivm\_cnp\_…37592}) executes 60/60 tasks […] 15 refusals […] » | Paragraphe « A one-hour endurance campaign… » de `main.tex__abstract_en.tex` | Idem K01. |
| K03 | p. xiii, Bokuse, `main.tex:594-600` | « Campagne multi-VM (\texttt{multivm\_cnp\_…37592}) esali 60/60 tâches […] Ezali na 15 refus […] » | Paragraphe « Campagne d'endurance ya ngonga moko… » de `main.tex__bokuse_ln.tex` | Idem K01. |
| K04 | p. viii, Résumé, `main.tex:376-377` | « Les cinq hypothèses de recherche sont partiellement soutenues. » | « Aucune hypothèse n'est validée : trois (H1, H2 et H4) sont partiellement soutenues et deux (H3 et H5) restent non tranchées, faute de comparateur sans routage pour la première et de gain quantitatif démontré de la mémoire pour la seconde. » | Tableau 7.1 actuel (`chapitre6_conclusion.tex:65-83`) : H3 et H5 « NON TRANCHÉE ». Formulation **provisoire** qui reprend fidèlement le tableau 7.1 actuel ; l'Agent 2 la modifiera s'il change les statuts. |
| K05 | p. xi, Abstract, `main.tex:493` | « All five research hypotheses are partially supported. » | « No hypothesis is validated: three (H1, H2, and H4) are partially supported and two (H3 and H5) remain undecided, […] » | Idem K04. |
| K06 | p. xiv, Bokuse, `main.tex:619` | « Ba hypothèses mitano ya recherche esimbami kaka na ndambo. » | « Hypothèse moko te endimisami mobimba : misato (H1, H2 mpe H4) esimbami kaka na ndambo, mpe mibale (H3 mpe H5) etikali NON TRANCHÉE […] » | Idem K04. Lingala non vérifié par un locuteur natif. |
| K07 | p. viii, Résumé, `main.tex:377-379` (+ EN 494-496, LN 619-622) | « Les trois premières questions reçoivent des réponses partielles renforcées, les quatrième et cinquième des réponses partielles, et la sixième une réponse forte dans le périmètre du laboratoire. » | « Les réponses aux questions de recherche restent partielles ; la question méthodologique (QR6) est la mieux couverte dans le périmètre du laboratoire. » | La conclusion (`chapitre6_conclusion.tex:22-38`) ne qualifie aucune réponse de « renforcée » ni de « forte » ; QR6 y est « la mieux couverte ». Le bien-fondé de ce jugement relève de l'Agent 2 (critique du lecteur 2, §2.1). |
| K08 | p. vi, Résumé, `main.tex:293-306` (+ EN 413-426, LN 530-544) | « obtient un F1 moyen de 0,995142 ± 0,001013, avec un intervalle de confiance à 95 % de [0,993884 ; 0,996400], pour cinq graines. » | « obtient un F1 moyen de 0,995142 sur cinq graines. » | ± et IC absents du corps (aucune occurrence dans `chapters/*.tex`). Valeurs **sourcées** : [X] `cicids_random_vs_holdout_summary.csv`, ligne random_stratified (f1_std 0,0010134 ; f1_ci95_half_width 0,0012583 → 0,995142 ± 0,001258 = [0,993884 ; 0,996400]). Retirées pour aligner le résumé sur le corps et alléger (Agent 7) ; l'Agent 4 peut les introduire au §4.2, auquel cas elles peuvent revenir. |
| K09 | p. vi, Résumé, `main.tex:313-315` (+ EN 433-435, LN 551-553) | « Le scénario DDoS conserve un F1 de 0,778774, tandis que PortScan, Bot, Infiltration et WebAttacks révèlent des performances très faibles ou nulles au seuil retenu. » | Phrase retirée. | Absent du corps. Valeur sourcée : [X] `cicids_holdout_multiseed_summary.csv` (DDoS f1_mean 0,7787739 ; PortScan 0,009947 ; Bot, Infiltration, WebAttacks 0,0). Même traitement que K08 (réintroduction possible si l'Agent 4 l'ajoute au §4.2). |
| K10 | p. vi, Résumé, `main.tex:306-311` (+ EN, LN) | « Lorsque cinq scénarios sont successivement tenus hors entraînement, le F1 macro tombe à 0,157744. » | « Lorsque chacun des cinq scénarios d'attaque est tenu hors entraînement, le F1 moyen tombe à 0,157744. » | 0,157744 est **exact** pour son plan : moyenne de 25 évaluations (5 scénarios × 5 graines), [D] `aggregated/cicids_protocol_comparison.csv` (n = 25, f1 0,1577441) et [X] `cicids_holdout_multiseed_raw.csv` (25 lignes). La contradiction avec le tableau 4.2 (0,157827) vient de deux plans distincts, non d'une erreur : voir K19. « macro » remplacé par « moyen » (terme du tableau 4.2 et du corps). |
| K11 | p. vi, Résumé, `main.tex:315-317` (+ EN, LN) | « Logistic Regression obtient le meilleur F1 macro, soit 0,233670 » | « la régression logistique obtient le meilleur F1 moyen, 0,233670, tandis que HistGradientBoosting obtient une PR-AUC macro de 0,569002 pour un F1 presque nul au seuil retenu » | Tableau 4.2 : « F1 moyen » ; [P] `cicids_model_candidates_summary.csv` (LR 0,2336698 ; HGB pr_auc_mean 0,5690020, f1_mean 0,003568). |
| K12 | p. vii, Résumé, `main.tex:326-328` (+ EN 447-449, LN 565-567) | « mais 89,8081 % des templates de test sont inconnus du train » | « mais 89,8081 % des événements de test portent un template inconnu de l'entraînement » | Unité erronée : il s'agit d'événements (17 879 sur 19 908), non de templates. Corps §4.4 (`chapitre5_resultats.tex:210`) et §5.3 (« des unités de test ») ; [D] `raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv` (UNKNOWN_TEMPLATE n = 17 879 ; ALL n = 19 908) et `…__bgl_known_unknown_result.json` (unknown_template_rate 0,898081). |
| K13 | p. vii, Résumé, BGL (après `main.tex:328`) (+ EN, LN) | (omission) | « et la décision d'Histogram coïncide exactement avec la règle « sévérité absente de l'entraînement normal ». Ce score mesure donc une nouveauté de sévérité plutôt qu'une modélisation de la dynamique des journaux » | Constat central du corps (§4.4, `chapitre5_resultats.tex:224` ; tableau A.9, `annexes.tex:205`) omis du résumé, qui présente 0,913698 comme résultat. Source : [R] `agent_4_bgl/agent4_bgl_second_protocol_20261104T142629Z__result.json` (hist_pred_equals_severity_novelty = true). |
| K14 | p. vii, Résumé, `main.tex:334-335` (+ EN 454-456, LN 574-575) | « Le score principal est donc présenté comme fortement dépendant des variables et du scénario. » | « […] score qu'une règle fixe sur le port de destination (inférieur à 1024) obtient également, et […] le transfert inverse, du 16 vers le 15 février, ne dépasse pas 0,234195. Le score principal repose donc sur un raccourci propre à la journée de test. » | Le corps conclut plus fermement (`chapitre5_resultats.tex:350` : « repose donc sur un raccourci propre à la journée de test » ; l. 418). Source : [R] `agent_4_csecic/agent4_csecic_shortcut_20261104T144738Z__printed_summary.txt` (règle port < 1024, test équilibré : 0,999720 ; LR 16→15 : 0,234195). |
| K15 | p. vii, Résumé, `main.tex:337-340` (+ EN, LN) | « La validation multiformat lit, parse et normalise 7 001/7 001 unités. […] il n'établit ni la complétude de tous les champs […] » | ajout : « dont une seule fixture Apache » ; « le remplissage du schéma commun varie de sept champs standard sur sept (syslog, BGL) à aucun (flux réseau tabulaires) » | Corps §4.8 (`chapitre5_resultats.tex:444, 458`) ; [R] `agent_5_multiformat/result.json` (per_source.standard_fields_complete_7 ; apache « existing_synthetic_fixture_one_line »). Omission dénoncée par les lecteurs 2 et 3. |
| K16 | p. vii, Résumé, `main.tex:345` (+ EN 464, LN 585) | « Le gain prédictif du routage spécialisé n'est pas systématique. » | « Aucune comparaison avec une chaîne sans routage n'a été exécutée : le bénéfice prédictif du routage spécialisé n'est pas établi. » | Tableau 7.1, H3 : « le comparateur sans routage manque ». La formulation actuelle suppose une comparaison dont l'artefact n'est pas cité (point Agent 4, §6). |
| K17 | p. vii, Résumé, `main.tex:349-352` (+ EN 468-471, LN 589-592) | « Les architectures à agents ne sont toutefois pas plus rapides sur les microtâches du protocole. Leur intérêt est architectural : autonomie locale, négociation, séparation des responsabilités, réattribution, idempotence et auditabilité. » | « Sur les microtâches du protocole, le monolithe domine et les architectures à agents ajoutent un coût d'orchestration. Lors d'une panne appariée survenant après persistance, les architectures à agents ne dupliquent aucun effet, contrairement au monolithe et aux workers centralisés ; doter ces derniers du même magasin d'idempotence supprime également les doublons. » | Contradiction avec le corps : §4.9.1 (`chapitre5_resultats.tex:506`) établit que l'absence de doublon provient du magasin d'idempotence, transposable à A et B, « et non de la négociation Contract Net » ; l'auditabilité n'est mesurée nulle part. « Le monolithe domine » : `annexes.tex:229`. Source panne : [R] `agent_3_distribution/agent3_paired_failure_abcd_20261104T141803Z__summary.json`. **Correction factuelle minimale ; l'Agent 5 reformule au fond** (périmètre « résumé p. vii »). |
| K18 | p. vii, Résumé, `main.tex:360-362` (+ EN 478-480, LN 602-604) | « Le corrélateur […] obtient une précision de 0,764706, un rappel de 0,866667 et un F1 pairwise de 0,812500. » | ajout : « Sur des corpus générés plus grands, son rappel tombe à 0,5973 ; lorsque 30 % des incidents enchaînent plusieurs catégories d'événements, une variante réduite à l'hôte et à la fenêtre temporelle obtient un meilleur F1 (0,7268 contre 0,6496). » | Le résumé ne rapporte que le petit corpus favorable ; le corps (§4.12, `chapitre5_resultats.tex:627`) rapporte la défaite face à la variante simple. Source : [R] `agent_5_correlation/result.json` (extended S1 M_keys recall 0,59733 ; S2 M_keys f1 0,64958 ; B_host_time f1 0,72681). |
| K18b | p. viii, Résumé, `main.tex:381` (+ EN 497-498, LN 624-625) | « d'une chaîne locale, modulaire, auditable et expérimentalement traçable » | « d'une chaîne locale, modulaire et expérimentalement traçable » | L'auditabilité n'est pas mesurée (lecteur 2, §2.4) ; proposition à confirmer par l'Agent 5. |

### 3.2 Introduction, §1.8.2, chapitre 4, chapitre 5

| n° | Localisation | Texte actuel | Texte corrigé | Justification / source |
|---|---|---|---|---|
| K19 | p. 83, §4.2.2, tableau 4.2, `chapitre5_resultats.tex:75` et `:81` | « La partition est un holdout fichier ou scénario, les graines sont 42 à 46 […] » ; légende « Candidats CICIDS2017 sur holdout fichier/scénario, cinq graines. » | `sections/chapitre5_resultats.tex__tableau_4.2.tex` : chaque graine tient hors entraînement un scénario différent (cinq évaluations par modèle) ; phrase qui distingue ce plan des 25 évaluations de la comparaison des protocoles (0,157744 contre 0,157827) ; légende « […] une évaluation par graine. » | F1 0,157744 (résumés, conclusion l. 10, `limites_consolidees.tex`, A.2) et 0,157827 (tableau 4.2) sont deux grandeurs **différentes**, toutes deux exactes : [P] `cicids_model_candidates_metrics.csv` (seed 42 DDoS, 43 PortScan, 44 Bot, 45 Infiltration, 46 WebAttacks ; f1_mean RF 0,1578266) contre [D] `cicids_protocol_comparison.csv` (n = 25 ; 0,1577441). Mêmes 78 variables, 16 000 lignes d'entraînement. Le texte les présentait comme la même grandeur. |
| K20 | p. 4, Introduction, « Positionnement… », `chapitre1_introduction.tex:58` | « Le titre du mémoire emploie les termes \textit{autonome}, \textit{distribuée} et \textit{agents intelligents multitâches}. » | « Le titre du mémoire qualifie l'architecture de \textit{multi-agents} et de \textit{légère} ; la question centrale y ajoute les qualificatifs \textit{autonome}, \textit{distribué} et \textit{multitâche}, et l'implémentation désigne ses agents comme \textit{intelligents}. » | Titre réel (`main.tex:77, 201`) : « Architecture multi-agents légère pour l'analyse de journaux système et réseau hétérogènes — Conception et évaluation en laboratoire d'Ariel Logminer » ; question centrale `chapitre1_introduction.tex:95` ; classe `MultiTaskIntelligentAgent` (`chapitre4_implementation.tex:43`). |
| K21 | p. 7, Introduction, « Hypothèses de recherche », `chapitre1_introduction.tex:147` | « Les seuils numériques et les budgets sont fixés dans le protocole avant l'exécution, et non choisis après lecture des résultats. » | `sections/chapitre1_introduction.tex__hypotheses_preenregistrement.tex` : seuils choisis sur validation, seuil du routeur gelé ; aucun préenregistrement ; budget H4 non fixé ; protocole G conçu après lecture de résultats antérieurs. | Contradiction directe avec le tableau 7.1 (`chapitre6_conclusion.tex:79` : « le budget local n'est pas un critère de décision préenregistré ») et avec §4.4 (`chapitre5_resultats.tex:268` : protocole G « tient compte de la position des familles d'anomalies »). Point de non-recevabilité B du lecteur 2. |
| K22 | p. 22, §1.8.2, `chapitre2_etat_art.tex:336` | « (section~6.2) » | « (section~\ref{sec:cicids-resultats}) », avec ajout de `\label{sec:cicids-resultats}` après `chapitre5_resultats.tex:53` | Section 6.2 du PDF = « Valeur de la spécialisation » (`main.toc`) ; le résultat est en section 4.2 « CICIDS2017 : influence du protocole ». |
| K23 | p. 108, §5.2, `chapitre6_approfondissements_scientifiques.tex:19` | « L'étude des coefficients, la permutation des labels et les retraits successifs ne mettent pas en évidence de fuite triviale parmi les mécanismes testés. Cela n'exclut toutefois pas l'existence d'un artefact lié aux journées sélectionnées […] » | `sections/chapitre6_approfondissements_scientifiques.tex__s5.2_csecic.tex` | Le §4.6.4 établit un raccourci propre à la journée de test et « un biais structurel entre les deux journées » (`chapitre5_resultats.tex:350, 380, 418`). Chiffres : [R] `agent_4_csecic/…__printed_summary.txt` (0,999720 ; 0,121517 ; 0,234195). Le terme « fuite » est évité pour rester cohérent avec la note A.9 (`annexes.tex:214`). |
| K24 | p. 112, §5.7, `chapitre6_approfondissements_scientifiques.tex:118` | « Dans la campagne multi-VM, ils proposent ou refusent des tâches, les exécutent, produisent des résultats et participent à une réattribution après l'échec contrôlé. » | `sections/chapitre6_approfondissements_scientifiques.tex__s5.7_conclusions.tex`, variante A (refus non dénombrés) ou B (si option B retenue) | Tableau A.4 (`annexes.tex:136`) : « compteurs non conclusifs » ; [E] `…130822Z__summary.json` : la fenêtre conservée ne contient **aucun** message REFUSE (message_counts sans clé REFUSE), et `message_counts_scope` = « retained tail only ». Aucun refus n'est établi pour la campagne du corps. |

### 3.3 Conclusion (tableau 7.1, QR3, QR6)

| n° | Localisation | Texte actuel | Texte corrigé | Justification / source |
|---|---|---|---|---|
| K25 | p. 125-126, QR3, `chapitre6_conclusion.tex:29` | « Sur le jeu indépendant retenu, le routeur oriente correctement les 28 fichiers connus et rejette les trois inconnus après application du seuil gelé. […] ce qui n'est pas observé dans toutes les familles et toutes les graines. » | `sections/chapitre6_conclusion.tex__QR3_QR6.tex` (a) : 20/20 inconnus rejetés, 3/46 connus écartés à tort, 43 acceptés correctement orientés ; aucune comparaison sans routage. | 28/3 = calibration (31 fichiers), qui n'est pas un « jeu indépendant ». Test étendu : `chapitre5_resultats.tex:426` ; [R] `agent_5_router_open_set/result.json`, summary.P.combined (unknown 20/20 ; known_falsely_rejected 3/46 ; known_accepted_correct 43/43). |
| K26 | p. 126, QR6, `chapitre6_conclusion.tex:38` | « La campagne multi-VM ajoute des preuves portant sur la répartition des tâches, les refus, la reprise et l'idempotence. » | « […] sur la répartition des tâches, la reprise et l'idempotence ; ses compteurs de messages n'étant pas conclusifs, elle n'établit pas de décompte des refus. » | Idem K24. |
| K27 | p. 126, « Statut des hypothèses », `chapitre6_conclusion.tex:46` | « Aucune n'est considérée comme totalement validée : les expériences apportent des éléments favorables, mais conservent pour chacune une limite […] » | « Aucune n'est validée : trois sont partiellement soutenues, avec pour chacune une limite qui empêche une généralisation complète, et deux restent non tranchées faute de comparateur ou de campagne décisive. » | Incohérent avec le tableau qui suit (H3, H5 non tranchées : pas d'« éléments favorables » au sens du critère). Statuts non modifiés. |
| K28 | p. 127, tableau 7.1, H1, `chapitre6_conclusion.tex:67` | « 7 001/7 001 unités présentes sont lues et normalisées ; la conservation champ par champ et la couverture universelle ne sont pas établies. » | ajout : « dont une fixture Apache d'une ligne ; le remplissage du schéma commun va de sept champs standard sur sept (syslog, BGL) à aucun (flux réseau tabulaires) » | Le critère de H1 porte sur la conformité au noyau commun ; le corps (§4.8) montre 0/7 champs pour les flux tabulaires. Source : [R] `agent_5_multiformat/result.json`. Statut inchangé (Agent 2). |
| K29 | p. 127, tableau 7.1, H4, `chapitre6_conclusion.tex:79` | « Des modèles légers et des baselines sont évalués ; les gains dépendent du jeu, du split et du seuil, et le budget local n'est pas un critère de décision préenregistré. » | ajout des faits établis dans le corps : CICIDS2017 temporel LR 0,556615 et RF 0,437429 sous « tout positif » 0,666667 ; BGL = règle de sévérité ; CSE-CIC règle port < 1024 0,999720 > LR 0,999212 ; HDFS : seuls comparateurs au niveau bloc = autres agrégations d'Histogram. | Sources : tableau 4.3 et `chapitre5_resultats.tex:162` ; [D] `cicids_protocol_comparison.csv` ; [R] `agent4_bgl_second_protocol_…__result.json` ; [R] `agent4_csecic_shortcut_…__printed_summary.txt` ; `annexes.tex:196` et `chapitre5_resultats.tex:310-312`. Statut inchangé ; ces faits sont fournis à l'Agent 2. Le point HDFS est à confirmer par l'Agent 4 (absence de baseline forte au niveau bloc). |

Fichier : `sections/chapitre6_conclusion.tex__tableau_7.1.tex` (K27-K29).

### 3.4 Annexes

| n° | Localisation | Texte actuel | Texte corrigé | Justification / source |
|---|---|---|---|---|
| K30 | p. 133, A.4, tableau A.3, `annexes.tex:93-109` | « \caption{Configuration HDFS vérifiée.} » ; « Échantillons & 6 000 / 2 000 / 2 000 blocs » ; « Événements & 126 368 / 37 153 / 30 948 » ; « Blocs positifs & 194 / 70 / 29 » ; « Seuil gelé & 1,2729429339548877 » ; « Test & TP 29, FP 7, TN 1 964, FN 0 » | `sections/annexes.tex__tableau_A3.tex` : protocole principal (345 036 / 115 012 / 115 013 blocs ; 11 158 / 4 001 / 1 679 positifs ; échantillon 6 000 blocs / 194 positifs par graine ; 2 122 752 et 1 766 455 événements ; 24 à 36 clusters ; seuils 1,272927-1,274817 ; TP 1 679, FP 509, TN 112 825, FN 0 ; F1 0,868373) + ligne séparée pour l'échantillon de 2 000 blocs de l'exécution distribuée. | Le tableau actuel reproduit `ds_hdfs_block_20260910T081756Z` ([D] `raw/…__hdfs_block_result.json`), échantillon distinct du résultat principal (§4.3). Sources : [R] `agent_2_hdfs/agent2_hdfs_full_20261104T131314Z__partition_prevalence.csv`, `__result.json`, `__seed_metrics.csv`. Point E de non-recevabilité du lecteur 2. |
| K31 | p. 135, A.8, `annexes.tex:169` | « Le routage open-set porte sur trois inconnus. Le F1 BGL ne fournit aucun rappel pour les anomalies à template connu. Le score CSE-CIC-IDS2018 dépend fortement de certaines caractéristiques. » | `sections/annexes.tex__A8.tex` : 20 inconnus et 46 connus, 3 faux rejets ; BGL « dans le protocole principal » + règle de sévérité ; CSE-CIC « raccourci par le port de destination propre à la journée de test ». | Routeur : `chapitre5_resultats.tex:426` ; [R] `agent_5_router_open_set/result.json`. BGL : le protocole G contient 2 880 positifs à template connu (`chapitre5_resultats.tex:241`), d'où la restriction. CSE-CIC : §4.6.4. |
| K32 | p. 131, A.3, tableau A.2, `annexes.tex:47-49` et colonnes « Artefact » | « Pour les campagnes ajoutées lors de la consolidation finale, les chemins de la troisième colonne sont relatifs à \texttt{experiments/phase\_revision\_20261104/}. » ; autres lignes en nom de fichier nu | `sections/annexes.tex__tableau_A2.tex` : sept préfixes de racine explicites [R] [D] [F] [M] [E] [P] [X], chaque fichier localisé sur disque. | Douze lignes renvoyaient à des fichiers hors de `phase_revision_20261104/` sans le dire (vérification par `find` le 2026-11-05). |
| K33 | p. 131, tableau A.2, `annexes.tex:62` | « CICIDS scénario RF & F1 macro 0,157744 & Même synthèse, protocole holdout scénario. » | « F1 moyen 0,157744 ; 25 évaluations (5 scénarios × 5 graines) » | Voir K19. |
| K34 | p. 131, tableau A.2, `annexes.tex:64` | « Sélection CICIDS & LR 0,233670 » | « LR 0,233670 ; RF 0,157827 (5 évaluations, un scénario par graine) ; PR-AUC HGB 0,569002 » | Valeurs citées au tableau 4.2 et dans les résumés sans entrée dans la matrice. [P] `cicids_model_candidates_summary.csv`. |
| K35 | tableau A.2 (lignes ajoutées) | (absentes) | BGL règle de sévérité ; CSE-CIC prévalence observée (0,994345 ; 0,234195) ; multiformat remplissage ; E2E latences et F1 Linux/auth ; endurance 451/1 349 ; saturation Ubuntu 140 ; corrélation multi-étapes 0,6496 / 0,7268 | Résultats cités dans le corps ou les résumés sans artefact dans la matrice. Valeurs relues dans les artefacts indiqués dans le fichier de section. |

## 4. Inventaire des chiffres des trois résumés et de leurs sources

Les chiffres sont identiques dans les trois résumés (vérifié ligne à ligne ; seules la typographie et la langue changent). « Corps » indique la section du PDF où le chiffre figure ; « absent » signifie qu'il n'apparaît dans aucun `chapters/*.tex`.

### 4.1 Chiffres du texte actuel

| Chiffre (résumé actuel) | Artefact (run_id / chemin) | Corps | Décision |
|---|---|---|---|
| CICIDS2017 RF aléatoire 0,995142 ; 5 graines | [D] `aggregated/cicids_protocol_comparison.csv` (0,99514232) ; [X] `cicids_random_vs_holdout_summary.csv` | §4.2 (fig.), §5.2, conclusion | conservé |
| ± 0,001013 | [X] `cicids_random_vs_holdout_summary.csv`, f1_std 0,00101338 | **absent** | retiré (K08) |
| IC [0,993884 ; 0,996400] | même fichier, f1_ci95_half_width 0,00125828 (méthode de l'IC non documentée dans le fichier) | **absent** | retiré (K08) |
| cinq scénarios ; RF holdout 0,157744 | [D] `cicids_protocol_comparison.csv` (n = 25) ; [X] `cicids_holdout_multiseed_raw.csv` | §4.2 (fig.), §4.14, conclusion | conservé, « F1 moyen » (K10) |
| DDoS 0,778774 ; PortScan, Bot, Infiltration, WebAttacks « très faibles ou nulles » | [X] `cicids_holdout_multiseed_summary.csv` (0,77877393 ; 0,009947 ; 0 ; 0 ; 0) | **absent** | retiré (K09) |
| cinq modèles ; LR 0,233670 | [P] `cicids_model_candidates_summary.csv` | tableau 4.2 | conservé (K11) |
| HGB PR-AUC 0,569002 | même fichier, pr_auc_mean 0,56900204 | §4.2.2 l. 123 | conservé |
| HDFS F1 0,868373 ; IC [0,856771 ; 0,879493] ; 115 013 blocs ; 1 679 positifs ; rappel 1 ; précision 0,767367 ; cinq graines identiques | [R] `agent_2_hdfs/agent2_hdfs_full_20261104T131314Z__seed_metrics.csv` et `__test_block_ci.json` | §4.3 | conservé |
| BGL 0,913698 | [D] `raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv` ; [R] `agent4_bgl_second_protocol_20261104T142629Z__result.json` | §4.4 | conservé |
| 89,8081 % (« des templates ») | [D] `…__bgl_known_unknown_result.json` (unknown_template_rate 0,898081, sur les événements) | §4.4 (« événements ») | conservé, unité corrigée (K12) |
| baseline template inconnu 0,277885 | [D] `…__bgl_group_metrics.csv` | §4.4 | conservé |
| CSE-CIC 15/16 février ; LR 0,999212 ; RF 0,401375 | [D] `raw/external_csecicids2018_20260910T230136Z_metrics.csv` (moyennes 5 graines relues) | §4.6.1 | conservé |
| Dst Port seul 0,999720 | [R] `agent_4_csecic/agent4_csecic_shortcut_20261104T144738Z__printed_summary.txt` (part1) ; [F] `aggregated/external_csecicids2018_single_feature_scores.csv` | §4.6.2 | conservé |
| dix premières retirées 0,657859 | [F] `aggregated/external_csecicids2018_feature_ablation.csv` | §4.6.3 | conservé |
| multiformat 7 001/7 001 | [D] `aggregated/multiformat_balanced_summary.csv` ; [R] `agent_5_multiformat/result.json` | §4.8 | conservé |
| routeur 20/20 ; 3/46 ; 43 | [R] `agent_5_router_open_set/result.json` (summary.P.combined) | §4.7 | conservé |
| 4 architectures, 4 charges, 10 répétitions, 160 runs, 264 000 traitements, sans échec | [M] `aggregated/ma_20260909T160812Z_34016__statistics.csv` (16 configurations × n = 10) | §4.9 | conservé |
| multi-VM `…37592` : 60/60 ; 30/30 ; 15 refus ; un échec ; une réattribution ; replay sans doublon | [M] `raw/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.json` et `…_tasks.csv` ; ledger [M] `manifests/EXPERIMENT_LEDGER.csv` l. 10 | **absent** | retiré ; remplacé par l'endurance (K01-K03) ; option B §8 |
| corrélation 0,764706 ; 0,866667 ; 0,812500 | [X] `correlation_synthetic_summary.json` (TP 13, FP 4, FN 2) | §4.12 | conservé |
| E2E 1400/1401 ; un fallback Apache ; aucune erreur | [F] `aggregated/multisource_cnp_model_inference_by_source.csv` | §4.10 | conservé |
| latences 0,105420 s / 0,031027 s | [F] `aggregated/multisource_cnp_model_inference_summary.json` (latency_mean 0,10542010 / 0,03102693) | §4.10 | conservé |
| F1 Linux/auth 0,390244 | même fichier | §4.10 | conservé |
| « cinq hypothèses partiellement soutenues » | tableau 7.1 | **contredit** | corrigé (K04-K06) |
| « réponses partielles renforcées […] réponse forte » | — | **absent** (conclusion) | corrigé (K07) |

### 4.2 Chiffres introduits par les résumés corrigés

| Chiffre | Artefact | Corps |
|---|---|---|
| règle port < 1024 = même score que Dst Port seul ; 16→15 : 0,234195 | [R] `agent4_csecic_shortcut_20261104T144738Z__printed_summary.txt` | §4.6.2 l. 350, §4.6.4 tableau 4.6 |
| remplissage 7/7 (syslog, BGL) à 0 (flux tabulaires) ; une fixture Apache | [R] `agent_5_multiformat/result.json` | §4.8 |
| endurance 1 800/1 800 ; 451 / 1 349 ; une heure | [E] `aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json` | §4.11.2, tableau 4.8, A.4 |
| saturation 8-16 tâches/s ; 1,23 % (140 / 11 427) | [R] `agent_3_distribution/agent3_saturation_multivm_20261104T142325Z__saturation_tasks.csv` et `__saturation_summary.json` | §4.11.3 |
| corrélation étendue rappel 0,5973 ; 30 % ; 0,7268 contre 0,6496 | [R] `agent_5_correlation/result.json` | §4.12 |

Aucun chiffre des résumés corrigés n'est dépourvu à la fois d'artefact et de section du corps.

## 5. Contradictions relevées : synthèse par gravité

1. **Campagne décrite dans les trois résumés mais absente du corps** (K01-K03). La campagne existe (artefact complet, ledger, manifeste), mais le corps ne la mentionne pas ; il décrit une autre campagne, dont les refus ne sont pas comptés.
2. **Statut des hypothèses** (K04-K07) : « cinq partiellement soutenues » contre deux NON TRANCHÉE au tableau 7.1 ; gradation des réponses aux QR absente de la conclusion.
3. **Préenregistrement** (K21) : p. 7 contre tableau 7.1 et protocole G.
4. **Tableau A.3** (K30) : configuration d'un échantillon de 2 000 blocs présentée comme « configuration vérifiée » du résultat principal.
5. **Résumé sélectif sur les points défavorables du corps** (K13, K14, K15, K17, K18) : règle de sévérité BGL, raccourci Dst Port, 0/7 champs, idempotence transposable, corrélation battue par la variante simple.
6. **QR3** (K25) et **A.8** (K31) restés sur la calibration (28/3, trois inconnus).
7. **§5.2 contre §4.6.4** (K23) et **§5.7 contre A.4** (K24, K26).
8. **F1 0,157744 contre 0,157827** (K10, K19, K33-K34) : deux plans distincts, présentés comme la même grandeur.
9. Renvoi « section 6.2 » (K22), titre p. 4 (K20), unité de 89,8081 % (K12).

## 6. Points relevant d'autres agents

| Point | Localisation | Agent |
|---|---|---|
| Statuts H1-H5 ; formulation finale du paragraphe « hypothèses » des trois résumés (provisoire ici) ; bien-fondé de « QR6 la mieux couverte » (conclusion l. 38 et résumés) ; « gain prédictif n'est pas systématique » de H3 (tableau 7.1 l. 75), qui repose sur une ablation sans artefact cité | conclusion, tableau 7.1, résumés | 2 |
| Faits ajoutés aux lignes H1 et H4 du tableau 7.1 (K28, K29) : à intégrer au raisonnement sur les statuts | `chapitre6_conclusion.tex:67, 79` | 2 |
| Ablation du routage invoquée sans artefact (§4.7 `chapitre5_resultats.tex:440` ; §6.2 `chapitre6_discussion.tex:16`) ; **artefact candidat repéré** : [P] `family_routing_ablation.csv` (variantes global_common_model / family_aware_models ; non relu en détail) | ch. 4, ch. 6 | 4 |
| `chapitre5_resultats.tex:420` : « Les deux fichiers disponibles comptent par ailleurs exactement 1 048 575 lignes de données ». L'audit [R] `agent4_csecic_shortcut_…__printed_summary.txt` (part2 audit) donne, pour le 16 février, `rows_scanned` = 1 048 574 et `repeated_header_rows` = 1 (le 15 février : 1 048 575 et 0) : le fichier du 16 février contient un en-tête répété au milieu des données, et son nombre de lignes de données diffère de celui du 15 ; la phrase « exactement 1 048 575 lignes de données » pour les deux fichiers est à vérifier et à corriger | §4.6.4 | 4 |
| `limites_consolidees.tex:13-14` (« un artefact lié aux journées retenues […] ne peut être exclu ») : même retrait que le §5.2 sur le raccourci établi | §5.8 | 4 |
| Option : ajouter au §4.2 l'écart-type, l'IC et le détail par scénario (DDoS 0,778774) si le résumé doit les citer | §4.2 | 4 |
| Confirmer qu'aucune baseline forte n'est évaluée au niveau bloc sur HDFS (fait ajouté à H4, K29) | §4.3, §4.5 | 4 |
| Reformulation de fond des paragraphes « architecture » des résumés (K17, K18b) et de §5.7 (« au-delà d'une simple description architecturale ») | résumés p. vii, §5.7 | 5 |
| `chapitre5_resultats.tex:621` : le paragraphe « La trace de messages ne conserve que la fenêtre terminale de 10 001 événements […] » se trouve dans la sous-section « Détection HDFS en mode distribué » (§4.11.4) mais décrit la campagne d'endurance ([E] summary : message_events_retained 10 001) ; il doit être déplacé en §4.11.2 | §4.11 | 5 |
| « refus » présentés comme observés sans campagne citée : `chapitre5_resultats.tex:641` (§4.14), `chapitre6_discussion.tex:23, 65` (§6.3, §6.7) ; avec l'option B, la campagne de 60 tâches peut les sourcer | ch. 4, ch. 6 | 5 |
| Opportunité d'introduire la campagne de 60 tâches (option B) ; son inscription au manifeste public (elle n'est pas dans `phase_revision_20261104/`) | §4.11, A.2, manifeste | 5 (fond), 6 (preuves) |
| `chapitre1_introduction.tex:280` annonce que le chapitre 6 met les résultats « en relation avec […] la littérature » ; le chapitre 6 ne contient aucune citation | introduction, ch. 6 | 3 |
| `revision_reports/HANDOFF.md` §3 (saturation « 3 échecs / 10 080 ») est périmé : l'artefact et le corps donnent 3 sur 11 430 | document de passation | 0 (information) |
| Précision excessive : seuil HDFS à 16 chiffres (A.3, corrigé à six décimales), run_id dans les résumés (retirés des passages corrigés) | A.3, résumés | 7 |

## 7. Points laissés en suspens

- **Lingala** : les phrases nouvelles du Bokuse (marquées `[N]` en commentaire dans `sections/main.tex__bokuse_ln.tex`) suivent le registre existant mais n'ont pas été relues par un locuteur natif ; les paragraphes inchangés sont repris à l'identique.
- **Méthode de l'IC [0,993884 ; 0,996400]** : la demi-largeur 0,00125828 figure dans l'artefact, sans indication de la méthode (vraisemblablement t de Student à 4 ddl, non vérifié). Sans objet si le chiffre reste retiré du résumé.
- **Page exacte des passages des résumés** : estimée par `main.toc` (Résumé vi-viii, Abstract ix-xi, Bokuse xii-xiv) et par les pages citées par les lecteurs ; pas d'extraction PDF possible (aucune bibliothèque PDF dans `.venv`).
- **Tableau A.4** : vérifié contre [E] summary, exact ; non modifié.
- **Paragraphes des résumés sur l'architecture** : corrigés sur l'exactitude seulement ; l'Agent 5 peut les réécrire. Le coordinateur devra intégrer la version la plus récente (Agent 5 > Agent 1 sur ces paragraphes, Agent 2 > Agent 1 sur le paragraphe « hypothèses »).

## 8. Questions au coordinateur

- **Q1 (campagne `multivm_cnp_20260909T202632Z_37592`)**. Option A (recommandée et appliquée par défaut dans les sections livrées) : la retirer des trois résumés, qui décrivent alors la campagne d'endurance du corps. Option B : l'introduire dans le corps (§4.11, paragraphe prêt dans `sections/chapitre5_resultats.tex__s4.11_OPTION_B_campagne_60.tex`, ligne A.2 commentée, variante B du §5.7). L'option B est la seule qui permette de sourcer l'affirmation « les agents refusent des tâches » (15 refus, tous de Debian sur les tâches de corrélation, motif `capability_missing`). Avis de l'Agent 5 souhaitable.
- **Q2 (ordre d'intégration des résumés)**. Les paragraphes « hypothèses » (Agent 2) et « architecture » (Agent 5) seront réécrits après l'Agent 1. Proposition : n'intégrer `main.tex__resume_fr.tex`, `__abstract_en.tex` et `__bokuse_ln.tex` qu'après les livrables 2 et 5, en partant des fichiers de l'Agent 1 comme base factuelle.
- **Q3 (retraits K08-K09)**. Confirmer que le résumé ne doit contenir aucun chiffre absent du corps (règle appliquée ici). Sinon, demander à l'Agent 4 d'ajouter ces chiffres au §4.2.

## 9. Fichiers livrés

Tous dans `revision_reports/chantier_20261105/agent_1/` :

| Fichier | Cible | Corrections |
|---|---|---|
| `LIVRABLE_1_integrite.md` | — | ce document |
| `sections/main.tex__resume_fr.tex` | `main.tex` l. 278-382 | K01, K04, K07-K18b |
| `sections/main.tex__abstract_en.tex` | `main.tex` l. 399-499 | K02, K05, K07-K18b |
| `sections/main.tex__bokuse_ln.tex` | `main.tex` l. 517-626 | K03, K06, K07-K18b |
| `sections/chapitre1_introduction.tex__positionnement_titre.tex` | l. 58 | K20 |
| `sections/chapitre1_introduction.tex__hypotheses_preenregistrement.tex` | l. 147 | K21 |
| `sections/chapitre2_etat_art.tex__ss1.8.2_renvoi.tex` | `chapitre2_etat_art.tex` l. 336 + label après `chapitre5_resultats.tex` l. 53 | K22 |
| `sections/chapitre5_resultats.tex__tableau_4.2.tex` | l. 75 et 81 | K19 |
| `sections/chapitre5_resultats.tex__s4.11_OPTION_B_campagne_60.tex` | après l. 594 (option B seulement) | Q1 |
| `sections/chapitre6_approfondissements_scientifiques.tex__s5.2_csecic.tex` | l. 19 | K23 |
| `sections/chapitre6_approfondissements_scientifiques.tex__s5.7_conclusions.tex` | l. 118 | K24 |
| `sections/chapitre6_conclusion.tex__QR3_QR6.tex` | l. 28-29 et 37-38 | K25, K26 |
| `sections/chapitre6_conclusion.tex__tableau_7.1.tex` | l. 46-89 | K27-K29 |
| `sections/annexes.tex__tableau_A2.tex` | l. 47-87 | K32-K35 |
| `sections/annexes.tex__tableau_A3.tex` | l. 91-112 | K30 |
| `sections/annexes.tex__A8.tex` | l. 169 | K31 |

Labels utilisés, tous existants sauf `sec:cicids-resultats` (à créer, K22) : `tab:statut-hypotheses`, `sec:bgl-second-protocole`, `sec:csecic-raccourci`, `tab:csecic-prevalence`, `tab:multivm-parametres-annexe`, `sec:hdfs-distribue`, `sec:cnp-multivm`, `fig:cicids-protocoles`. Aucune compilation n'a été lancée (décision C1 : l'Agent 0 intègre et compile).
