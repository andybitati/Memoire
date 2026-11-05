# LIVRABLE 2 — Statut des hypothèses et critères de décision

Agent 2, chantier de révision du 2026-11-05. Document autoportant : un repreneur n'a besoin que de ce fichier, du dossier `sections/` voisin et des fichiers du dépôt cités.

Statut : **terminé**. Aucune expérience exécutée. Aucun fichier `.tex` du mémoire modifié (décision C1). Les sections livrées ont été appliquées à une **copie** du manuscrit (scratchpad, hors dépôt) et compilées : 0 erreur, 0 référence indéfinie, 0 débordement (§12).

---

## 1. Périmètre traité

| Élément (numérotation du PDF) | Fichier source | Repère textuel |
|---|---|---|
| Question centrale, QR1–QR6 (p. 5) | `chapters/chapitre1_introduction.tex` | `\section*{Question centrale et questions de recherche}` |
| H1–H5 et critères (p. 6–7) | idem | `\section*{Hypothèses de recherche}` |
| Phrase « préenregistrement » (p. 7) | idem | « Les seuils numériques et les budgets sont fixés dans le protocole avant l'exécution » |
| Phrase du titre (p. 4, lot A1-a) | idem | « la question centrale y ajoute les qualificatifs » |
| Objectif général (p. 7) | idem | « destiné à la détection et à la priorisation » |
| §1.23–1.24, tableau 1.3 (p. 38–40) | `chapters/chapitre2_etat_art.tex` | `tab:positionnement-logminer` |
| §3.5.1 fonction d'utilité (p. 72–74), pour H5 seulement | `chapters/spec_utilite.tex` | `sec:spec-utilite` |
| Conclusion : bilan, réponses aux QR, statut, tableau 7.1 (p. 125–127) | `chapters/chapitre6_conclusion.tex` | `\section*{Réponse aux questions de recherche}`, `tab:statut-hypotheses` |
| Paragraphe « hypothèses » des trois résumés | `main.tex` (via `agent_1/sections/main.tex__*.tex`) | « Aucune hypothèse n'est validée » |
| Points C5 affectés à l'Agent 2 | — | question fourre-tout ; priorisation, périodique, micro-lots ; QR descriptives, QR6 « la mieux couverte » ; exigences / hypothèses / propriétés (L1 C.2) ; « partiellement soutenue » conjonctif (L1 C.3) ; H4 face aux baselines triviales (L2 §2.4) ; scénario hétérogène conjoint (L3) ; tableau de bord sans étude d'utilisabilité (L1 D.2) |

Remarque : les lecteurs appellent « §1.23 » la section « Lacunes identifiées » (p. 38) ; le tableau de positionnement est au §1.24 (p. 40). Le « chapitre 7 » du PDF (`chapitre7_reproductibilite_deploiement.tex`) ne contient aucun statut d'hypothèse ; les réponses aux QR et le tableau 7.1 sont dans la conclusion (`chapitre6_conclusion.tex`, sections non numérotées que la table des figures rattache au chapitre 7).

## 2. Méthode

1. Lecture intégrale de `MISSION.md`, `RETOURS_LECTEURS.md` (trois lecteurs), `ETAT_CHANTIER.md`, `LIVRABLE_1_integrite.md` et des sections de l'Agent 1 désignées par C9, `HANDOFF.md` §1, `PATCH_NOTES.md` (correspondance).
2. Lecture intégrale de l'introduction, de la conclusion, du chapitre 4 (`chapitre5_resultats.tex`), du chapitre 6 (`chapitre6_discussion.tex`), de `spec_utilite.tex`, de `limites_consolidees.tex`, des §1.23–1.24 et des passages du chapitre 2 sur le noyau commun (§2.8.1–2.8.3).
3. Pour chaque hypothèse : citation exacte de l'énoncé et du critère ; décomposition en composantes ; rattachement de chaque composante à une section du corps et à un artefact ; relecture de chaque chiffre dans l'artefact (§3) ; application des règles R1–R6 ci-dessous.
4. Recherche des grandeurs que les énoncés supposent fixées à l'avance : `grep` de « budget », « prioris », « incompatib », « périodique », « micro-lot » dans `chapters/*.tex`.
5. Rédaction des sections (`sections/`) et test de compilation sur une copie (§12).

### Règles de décision appliquées (identiques pour les cinq hypothèses)

- **R1.** Si le comparateur exigé par l'énoncé n'a pas été exécuté, la composante est **non tranchée**. C'est la règle écrite p. 7 : « Une hypothèse reste non tranchée lorsque le comparateur requis n'a pas été exécuté. »
- **R2.** Si le comparateur a été exécuté et que l'observation prévue par le critère de réfutation se produit, la composante est **réfutée**.
- **R3.** Hypothèse conjonctive : **réfutée** dès qu'une composante l'est ; **validée** si toutes sont établies ; **partiellement soutenue** si au moins une est établie, aucune réfutée, les autres non tranchées ; **non tranchée** sinon.
- **R4.** Hypothèse existentielle (« au moins un candidat ») : réfutée seulement si chaque instance évaluable est infirmée et qu'aucune ne reste non tranchée ; sinon non tranchée (ou mieux, selon R3).
- **R5.** Un seuil, un budget ou une métrique « fixé à l'avance » qui ne l'a pas été ne peut pas l'être après coup (garde-fou anti-HARKing, décision C4 c) : la composante concernée ne peut plus être établie par ce travail.
- **R6.** La « baseline déclarée » d'un test est la meilleure règle que le mémoire évalue sur ce test. Retenir la seule baseline battue serait un choix fait après lecture des résultats (c'est le reproche de L2 §2.4).

Ces règles sont des règles de logique appliquées au texte existant ; elles sont énoncées dans la conclusion (section livrée), non présentées dans l'introduction comme fixées avant l'expérience. Seule R1 figure déjà dans l'introduction.

## 3. Abréviations des chemins (relatifs à `E:\Cours\TFE\`)

[R] `experiments/phase_revision_20261104/` ; [D] `experiments/phase_dataset_strengthening/` ; [M] `experiments/phase_multi_agent/` ; [E] `experiments/phase_cnp_endurance/` ; [P] `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/` ; [X] `data/processed/final_experiments_2026/`.

## 4. Fiches par hypothèse

### H1 — Normalisation

**Énoncé (intro, p. 6, `chapitre1_introduction.tex`, item `\item[\textbf{H1.}]`)** : « Pour chaque unité des formats retenus, la normalisation produit un événement conforme au noyau commun et conserve une référence vérifiable vers la donnée source. »
**Critère** : « L'hypothèse est réfutée si une unité présente ne peut être lue, normalisée ou retracée. »

| Composante | Résultat rattaché | Source |
|---|---|---|
| (i) Lecture de chaque unité | 7 001/7 001 unités lues et émises ; 7 sources réelles × 1 000 + 1 fixture Apache d'une ligne | §4.8 ; [R] `agent_5_multiformat/result.json` (total_read 7001, apache « existing_synthetic_fixture_one_line ») ; [D] `aggregated/multiformat_balanced_summary.csv` |
| (ii) Événement « conforme au noyau commun » | Le noyau n'impose aucun champ : les champs absents prennent une valeur nulle (§2.8.3) ; les flux réseau tabulaires sont « normalisés » avec 0/7 champs standard ; remplissage 7/7 (syslog, BGL), 6/7 (HDFS, Apache), 5/7 (Windows), 4/7 (Linux/auth, Wazuh), 0/7 (flux) | §4.8 (7/7 à 0/7) ; §2.8.3 ; [R] `agent_5_multiformat/result.json` (per_source.standard_fields_complete_7 ; definition_note : « normalisé compte les lignes émises par l'adaptateur ; il est égal à parsé par construction ») |
| (iii) Référence vérifiable vers la source, par unité | Non présentée dans le corps ; §5.8 : la couverture « mesure la lecture, le parsing et la normalisation des unités présentes, non la complétude des champs ni la conservation intégrale du contenu brut » | `limites_consolidees.tex` |

**Application du critère.** Aucune unité n'échoue à la lecture ni à l'émission : le critère n'est pas déclenché pour (i). Pour (ii), il ne peut pas l'être : « normalisé » vaut « émis » par construction (artefact), et le noyau ne rend aucun champ obligatoire ; la conformité est nominale. Pour (iii), aucune mesure dans le corps : non tranchée (R1).

**Statut : PARTIELLEMENT SOUTENUE** (R3 : (i) établie, (ii) établie au sens formel seulement, (iii) non tranchée ; aucune réfutée).

**Points des lecteurs.**
- *H1 quasi infalsifiable (L2 §2.1)* : **fondé en partie.** Deux des trois verbes du critère (« lue », « normalisée ») ne peuvent échouer qu'en cas de plantage de l'adaptateur ; la conformité n'a pas de contenu testable ; le corpus (formats, 1 000 unités, une ligne Apache) est choisi par l'auteur. Seule la composante (iii) aurait pu discriminer, et elle n'est pas mesurée dans le corps.
- *Fixture Apache d'une ligne (L2, L3)* : la voie Apache n'est testée que sur une ligne synthétique ; aucune revendication de prise en charge d'Apache n'est soutenue. L'artefact consigne qu'aucun corpus Apache réel n'a été trouvé localement (`real_apache_corpus_found_locally: false`).
- *0/7 champs pour les flux réseau* : confirme que « conforme au noyau commun » ne garantit pas que l'événement porte l'information partagée ; le tableau 7.1 livré le dit explicitement.

**Requalification (réduction des revendications, forme a).** Ce que H1 établit est une **exigence de réalisation** : chaque unité des sources retenues est lue et émise dans le schéma commun. Ce n'est pas une connaissance sur la normalisation de journaux hétérogènes.

**Élément d'artefact non présenté dans le corps (pour l'Agent 4).** [D] `raw/multiformat_balanced_20260910T094422Z_units.csv` contient, par unité, `event_index`, `source_path`, `raw_sha256` (de quoi documenter la composante iii) et un test `original_message_test` : TRUE pour 2 001 unités (Linux/auth, Wazuh, Apache), FALSE pour 4 000 (BGL, HDFS, syslog, Windows : 1 000 chacune), NOT_APPLICABLE pour les 1 000 flux. Le FALSE vient probablement du retrait de l'en-tête (le message normalisé n'est pas la ligne brute), mais ce n'est pas vérifié. Ne pas citer sans interprétation. Si l'Agent 4 documente (iii) dans le corps, H1 reste « partiellement soutenue » (la composante ii demeure non discriminante).

### H2 — Idempotence

**Énoncé (p. 6)** : « Dans l'architecture à agents, lors d'un arrêt contrôlé après persistance et avant émission du résultat, l'activation de l'idempotence permet de terminer la tâche sans perte ni effet dupliqué, contrairement à la même exécution sans idempotence. »
**Critère** : « L'hypothèse est réfutée si cette différence n'est pas observée. »

| Composante | Résultat rattaché | Source |
|---|---|---|
| (i) Agents **avec** idempotence : ni perte ni doublon | C et D : 0 perte, 0 doublon, 10/10 rejeux idempotents ; reprise médiane 5,819 et 5,864 ms. Multi-VM : 1 effet persistant, 0 doublon après réattribution | §4.9.1, tableau 4.7 ; [R] `agent_3_distribution/agent3_paired_failure_abcd_20261104T141803Z__summary.json` ; §4.11, tableau 4.8 ; [E] `aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json` |
| (ii) La **même exécution à agents sans** idempotence produit perte ou doublon | **Non exécutée.** Les six bras sont A, B (sans magasin), C, D, A+I, B+I (avec) : aucun bras « agents sans magasin ». Le script `revision_reports/agent_3/run_paired_failure_abcd.py` code `uses_store = architecture in {"C", "D", "A+I", "B+I"}` et `run_cnp` exige un magasin | même artefact (summary : six clés) ; script cité |
| Contraste disponible | A et B : 10 doublons sur 10 ; A+I et B+I : 0. Le magasin supprime les doublons dans toutes les architectures | tableau 4.7 ; §4.9.1 : « L'avantage observé provient donc du mécanisme d'idempotence [...] et non de la négociation Contract Net » |

**Application du critère.** (i) établie. (ii) : le comparateur exigé par l'énoncé (« la même exécution » à agents, sans idempotence) n'a pas été exécuté ; les contrastes disponibles changent l'architecture en même temps que le magasin (A/B contre C/D) ou portent sur d'autres architectures (A contre A+I, B contre B+I). R1 : non tranchée.

**Statut : PARTIELLEMENT SOUTENUE** (R3 : (i) établie, (ii) non tranchée). Le libellé ne change pas, mais sa justification oui.

**Point des lecteurs.**
- *H2 tautologique (L2 §2.1, L3 §1)* : **fondé.** Sans magasin, le rejeu d'une tâche dont l'effet est persistant répète cet effet par construction (A et B le montrent) ; l'issue du bras manquant est donc connue d'avance. Le bras « avec » est un test de correction de l'implémentation (il pourrait échouer en cas de défaut), pas une proposition explicative.

**Requalification (forme a).** H2 établit une **exigence de réalisation** : « sous une panne survenant après persistance et avant émission du résultat, le magasin d'idempotence empêche tout effet dupliqué, dans les quatre architectures qui en sont dotées ». La lecture « propriété des agents » est retirée : la propriété tient au magasin (§4.9.1, `limites_consolidees.tex`).

### H3 — Routage

**Énoncé (p. 6)** : « Sur un corpus comprenant des familles connues et inconnues, le routage par famille réduit le taux d'exécutions incompatibles par rapport à la même chaîne sans routage, sans accroître le taux d'erreur prédictive fixé par le protocole. »
**Critère** : « L'hypothèse est réfutée en l'absence de réduction mesurée. »

| Composante | Résultat rattaché | Source |
|---|---|---|
| (i) Réduction des exécutions incompatibles face à la chaîne sans routage | Chaîne sans routage **non exécutée** ; « taux d'exécutions incompatibles » **jamais défini** dans le corps | tableau 7.1 actuel ; recherche « incompatib » dans `chapters/*.tex` : seulement l'énoncé de H3 et le tableau 7.1 |
| (ii) Taux d'erreur prédictive non accru | « Taux d'erreur fixé par le protocole » **jamais fixé** ; l'« ablation du routage » invoquée au §4.7 et au §6.2 n'a ni tableau ni artefact dans le corps | §4.7 dernier paragraphe ; §6.2 ; L2 §2.4 |
| Ce qui est mesuré : le routeur seul | Au seuil gelé (100), sans recalibration : 20/20 inconnus rejetés (IC [0,832 ; 1]), 3/46 connus écartés à tort (IC [0,014 ; 0,179]), 43/43 connus acceptés correctement orientés | §4.7 ; [R] `agent_5_router_open_set/result.json` (summary.P.combined ; recalibrated false ; policy.min_top_score 100) |

**Application du critère.** R1 pour (i) et (ii). R5 : le taux d'erreur de référence ne peut plus être fixé.

**Statut : NON TRANCHÉE** (inchangé).

**Point des lecteurs.**
- *H3 sans comparateur « sans routage » (L1 A.1, L2 §2.1)* : **fondé.** De plus, si « la même chaîne sans routage » signifie un pipeline unique pour toutes les sources, l'issue est connue d'avance (toute source d'une autre famille y est incompatible par construction) : comme H2, la comparaison serait tautologique. Le comparateur informatif est une **table de routage statique** (extension, en-tête, nom de fichier), c'est-à-dire le « routeur à règles » que L3 oppose au prototype (voir §8, E-H3).
- La mention « le gain prédictif n'est pas systématique » (tableau 7.1 actuel) est retirée des sections livrées : elle repose sur une ablation absente du corps. **Artefact candidat** (non présenté dans le corps) : [P] `family_routing_ablation.csv`, une seule exécution sans graine documentée, 3 000 lignes de test par famille : F1 global/spécialisé = 0,999667/0,999667 (cicids), 0,824368/0,816399 (linux_auth), 0,995662/0,994660 (unsw). Il compare un modèle commun à des modèles par famille (composante ii), pas des exécutions incompatibles (composante i). S'il entre dans le corps (Agent 4), il pèse **contre** la composante (ii) sur deux familles sur trois, mais sans protocole ni incertitude suffisants pour la réfuter.

### H4 — Modèles légers

**Énoncé (p. 6)** : « Sous une séparation stricte fixée avant l'expérience, au moins un modèle léger surpasse la baseline déclarée en F1 sur le test tenu à l'écart et reproduit ce résultat dans le budget local de temps et de mémoire fixé par le protocole. »
**Critère** : « L'hypothèse est réfutée si aucun candidat ne satisfait conjointement ces critères. »

Composantes : (a) séparation stricte fixée avant l'expérience ; (b) F1 supérieur à la baseline déclarée sur le test ; (c) budget local de temps et de mémoire fixé par le protocole.

| Instance (jeu, protocole principal) | (b) supériorité, selon R6 | Source |
|---|---|---|
| CICIDS2017, séparation temporelle (lundi–jeudi → vendredi, test équilibré, prévalence 0,5) | **Infirmée** : LR 0,556615 et RF 0,437429 < prédiction systématiquement positive 0,666667 (= 2×0,5/1,5) | tableau 4.3, §4.2.3 ; [R] `agent_6_iforest_baselines/agent6_cicids_iforest_20261104T141904Z_summary.csv` (test_f1_mean LR 0,5566145, RF 0,4374292) et `_metrics.csv` (test_prevalence 0,5) ; [D] `aggregated/cicids_protocol_comparison.csv` |
| CICIDS2017, holdout par scénario | **Non présentée dans le corps.** Calcul de l'Agent 2 sur l'artefact : la prédiction tout positif obtient en moyenne 0,473265 (moyenne de 2p/(1+p) sur les 25 évaluations, p = `test_positive_rate`), au-dessus des cinq candidats (meilleur : LR 0,233670) ; par scénario : DDoS 0,666667 (RF 0,778774), PortScan 0,666667 (RF 0,009947), WebAttacks 0,521531 (0), Bot 0,495714 (0), Infiltration 0,015748 (0) | [X] `cicids_holdout_multiseed_raw.csv` ; [P] `cicids_model_candidates_metrics.csv` (même moyenne 0,473265). **À introduire dans le corps par l'Agent 4 avant toute citation** (C8) |
| CSE-CIC-IDS2018, 15 → 16 février, test équilibré | **Infirmée** : règle « port < 1024 » 0,999720 > LR 0,999212 (RF 0,401375) | §4.6.1–4.6.2 ; [R] `agent_4_csecic/agent4_csecic_shortcut_20261104T144738Z__printed_summary.txt` (part1 : rule_dst_port_lt_1024 0,999720 ; LR ALL 0,999212) |
| CSE-CIC-IDS2018, prévalence observée | **Infirmée** : règle sur le port 0,999728 (§4.6.4) > LR 0,994345 | tableau 4.6 ; même artefact (part2) |
| BGL, protocole principal | **Infirmée** : Histogram 0,913698 = règle « sévérité absente de l'entraînement » (même matrice) ; il ne dépasse que la règle « template inconnu » (0,277885) | §4.4 ; [R] `agent_4_bgl/agent4_bgl_second_protocol_20261104T142629Z__result.json` (R0 : hist_pred_equals_severity_novelty true) et `__group_metrics.csv` |
| BGL, sept protocoles complémentaires | Histogram dépasse la règle « template inconnu » dans les sept (tableau 4.4) ; la règle de sévérité n'est rapportée que pour G (0,000693 contre 0,941927). **Mais (a) n'est pas satisfaite** : protocoles explorés après le principal, sans plan (L2 §2.3) ; G « tient compte de la position des familles d'anomalies » (§4.4.1) | tableau 4.4 ; §4.4.1 |
| HDFS, niveau bloc, test complet | **Non évaluable** : aucune baseline au niveau bloc ; seules d'autres agrégations d'Histogram (figure 4.3) ; les Isolation Forest de contrôle sont au niveau événement (0,204530) | §4.3, §4.5 ; [R] `agent_2_hdfs/agent2_hdfs_full_20261104T131314Z__result.json` (aucune clé baseline ; agrégateurs maximum, mean, abnormal_ratio) |

Composante (c) : **aucun budget n'a été fixé** (tableau 7.1 actuel : « le budget local n'est pas un critère de décision préenregistré » ; aucune occurrence d'un budget de temps ou de mémoire dans le corps). R5 : aucun candidat ne pourra la satisfaire dans ce travail. Composante (a) : aucune séparation n'est prouvablement fixée avant l'expérience (C4 c) ; elle est infirmée pour G.

**Application du critère.** Sur trois jeux, la composante (b) est infirmée dans le protocole principal ; sur HDFS, elle n'est pas évaluable (R1) ; les instances BGL complémentaires n'ont pas de valeur confirmatoire. R4 : une instance (HDFS) reste non tranchée, donc l'hypothèse existentielle n'est pas réfutée au sens strict. R5 : la composante (c) ne peut plus être établie, donc H4 ne peut plus être validée par ce travail, ni même « partiellement soutenue » au sens du critère conjoint, puisque la seule instance où (b) pourrait tenir (HDFS) n'a pas de baseline.

**Statut : NON TRANCHÉE ; supériorité infirmée sur trois des quatre jeux publics** (avant : PARTIELLEMENT SOUTENUE).

Pourquoi pas « réfutée » ? Parce que l'énoncé est existentiel et qu'HDFS reste ouvert (R4). Pourquoi pas « partiellement soutenue » ? Parce qu'aucune composante n'est établie pour aucun candidat (L1 C.3 : une composante favorable ne valide pas une proposition conjonctive ; ici, aucune ne l'est). Le coordinateur peut préférer « réfutée » en lisant le critère au pied de la lettre (« aucun candidat ne satisfait conjointement » est vrai et le restera, faute de budget) ; voir Q1 (§11).

**Points des lecteurs.**
- *Budget non préenregistré (L1 A.2, L2 point B)* : **fondé** ; corrigé dans l'introduction (section livrée).
- *H4 sous les baselines triviales (L2 §2.4)* : **fondé** pour CICIDS2017 temporel, CSE-CIC-IDS2018 et BGL ; **renforcé** par le calcul sur le holdout par scénario (tout positif 0,473265 > cinq candidats), à faire entrer dans le corps ; HDFS : absence de baseline au niveau bloc **confirmée**.

**Requalification (forme a).** Ce que le travail établit sur la détection est un **constat de dépendance au protocole** (QR6 reformulée), pas une supériorité de modèles légers. Le seul résultat prédictif sans règle triviale équivalente connue est HDFS au niveau bloc (F1 0,868373), dont la portée reste à établir face à une baseline de même niveau.

### H5 — Mémoire et mise à jour

**Énoncé (p. 6)** : « À protocole et tâches identiques, l'activation de la mémoire persistante améliore au moins une métrique de priorisation fixée à l'avance sans dégrader les autres métriques principales, et la procédure de mise à jour ne remplace le modèle actif que lorsqu'un candidat satisfait la règle de promotion. »
**Critère** : « L'hypothèse est réfutée si aucun gain n'est observé ou si une promotion contraire à la règle se produit. »

| Composante | Résultat rattaché | Source |
|---|---|---|
| (i) Mémoire : gain sur une métrique de priorisation, sans dégradation | Comparateur **exécuté** : D (mémoire activée) contre C (désactivée), mêmes charges (100, 500, 1 000, 5 000), dix répétitions appariées. Corps : « la campagne ne montre pas d'amélioration systématique du débit, de la latence ou de l'équité ». **Aucune métrique de priorisation définie ni mesurée** | §4.9 ; figure 4.14 ; annexe A.9 (« Les courbes C et D ne montrent pas de gain systématique ») ; recherche « prioris » dans `chapters/*.tex` |
| Détail apparié D − C (artefact, non présenté dans le corps) | Débit : −59,8 ; −62,4 ; −112,7 ; −22,6 tâches/s (toujours défavorable). Latence p95 : −0,51 ; −1,75 ; −0,39 ; −0,09 ms (favorable, intervalles à 95 % de l'artefact contenant tous 0). Équité de Jain : à 500 tâches, −0,0403, IC [−0,0638 ; −0,0167] (dégradation). RSS : à 100 tâches, +0,34 Mo, IC [0,12 ; 0,55] (dégradation). Test : `none_descriptive` | [M] `aggregated/ma_20260909T160812Z_34016__paired_memory_effects.csv` |
| (ii) Promotion conforme à la règle | Aucune promotion contraire observée ; mais aucun cycle de promotion et de rejet exécuté (« Promotion/rejet observé : NON ÉVALUÉ ») | §4.13 ; tableau A.5 (`tab:statut-model-update`) |

**Application du critère.** (i) : le comparateur prévu (« à protocole et tâches identiques ») a été exécuté, et l'observation qui réfute (« aucun gain n'est observé ») se produit sur toutes les métriques mesurées. Même en retenant la seule tendance favorable (latence p95, dans le bruit), la condition « sans dégrader les autres métriques principales » échoue (débit plus faible aux quatre charges ; équité dégradée à 500 tâches). R2 : réfutée. (ii) : R1, non tranchée. R3 : une composante réfutée suffit.

**Statut : RÉFUTÉE** (avant : NON TRANCHÉE).

**Point des lecteurs.**
- *H5 réfutée selon son propre critère mais classée « non tranchée » (L2 §2.1, point C)* : **fondé.** La règle « non tranchée faute de comparateur » ne s'applique pas : le comparateur mémoire activée/désactivée a été exécuté.
- *Priorisation jamais mesurée (L2 §2.1)* : **fondé.** La réfutation porte donc sur les métriques effectivement mesurées ; la revendication de priorisation n'est pas seulement réfutée, elle est **retirée** (§7).

**Lien avec §3.5.1 (spécification de l'utilité).** La mémoire n'agit que par H (poids 0,20) et T (0,05) ; M = 1 et A = L. Elle ne peut donc améliorer une attribution que si les agents diffèrent en fiabilité ou en latence pour un même type de tâche. Dans le benchmark, aucune tâche n'échoue (§4.9 : « Aucun échec n'est enregistré ») ; l'artefact [M] `raw/ma_20260909T160812Z_34016__adaptation.csv` montre l'utilité de l'agent qui a déjà réussi passer de 0,845 à 0,93 pendant que les autres restent à 0,845, ce qui concentre les tâches sur lui. Interprétation à vérifier par l'Agent 5 : la mémoire actuelle favorise l'agent déjà servi, ce qui est cohérent avec la baisse d'équité, et le benchmark ne contient pas la situation où elle pourrait aider. Ce constat motive l'expérience E-H5 (§8) ; il ne change pas le statut.

## 5. Tableau récapitulatif des statuts

| Hyp. | Avant (tableau 7.1 actuel) | Après | Justification en une ligne |
|---|---|---|---|
| H1 | PARTIELLEMENT SOUTENUE | **PARTIELLEMENT SOUTENUE**, requalifiée en exigence de réalisation | Lecture 7 001/7 001 établie ; conformité non discriminante (0/7 champs pour les flux) ; référence vers la source non mesurée. |
| H2 | PARTIELLEMENT SOUTENUE | **PARTIELLEMENT SOUTENUE**, requalifiée en exigence de réalisation | Agents avec idempotence : 0 perte, 0 doublon ; bras « agents sans idempotence » non exécuté ; effet dû au magasin, transposable à A et B. |
| H3 | NON TRANCHÉE | **NON TRANCHÉE** | Chaîne sans routage non exécutée ; taux d'exécutions incompatibles et taux d'erreur de référence jamais définis. |
| H4 | PARTIELLEMENT SOUTENUE | **NON TRANCHÉE ; supériorité infirmée sur trois jeux** | Sous la règle triviale sur CICIDS2017 temporel, CSE-CIC-IDS2018, BGL ; HDFS sans baseline au niveau bloc ; aucun budget fixé, donc plus validable. |
| H5 | NON TRANCHÉE | **RÉFUTÉE** | Comparateur mémoire activée/désactivée exécuté, aucun gain établi ; priorisation jamais mesurée ; promotion non tranchée. |

Bilan : 0 validée ; 2 partiellement soutenues (toutes deux des exigences de réalisation) ; 2 non tranchées ; 1 réfutée. Aucune des hypothèses comparatives (H3, H4, H5) n'est soutenue.

## 6. Question centrale et questions de recherche

### 6.1 Diagnostic

- La question actuelle (« Comment concevoir un prototype autonome, distribué au sens logiciel, modulaire et exploitable par un analyste, capable de détecter et de prioriser des anomalies candidates [...] par traitements périodiques, par micro-lots et par agents multitâches ? ») est un cahier des charges (L3 §1) ; elle compte plus de dix attributs (L2 §2.1) et n'a pas de variable principale (L1 C.1).
- Jamais mesurés : **priorisation** (aucune métrique) ; **traitements périodiques** et **micro-lots** (décrits au §2.23.2 seulement) ; **exploitabilité par l'analyste** (aucune étude, §5.8 et QR4) ; **auditabilité** (aucune mesure ; voir Agent 5).
- QR1–QR5 commencent par « Comment… » et appellent une description ; QR6 est une question de méthode sur le mémoire lui-même ; la déclarer « la mieux couverte » est circulaire (L2 §2.1).

### 6.2 Proposition (section livrée `chapitre1_introduction.tex__question_centrale_QR.tex`)

Question centrale resserrée : « Dans quelle mesure une chaîne d'analyse multi-agents légère, exécutée en laboratoire sur un ou deux hôtes, peut-elle lire des journaux système et réseau de formats hétérogènes, les orienter vers un traitement compatible et y détecter des anomalies sous des protocoles d'évaluation stricts, et que coûte cette organisation par rapport à une exécution monolithique ou à des workers centralisés ? »

Variable principale (partie prédictive) : F1 sur un test tenu à l'écart, au niveau de l'unité annotée, rapporté à la meilleure règle triviale évaluée sur le même test. Partie architecturale : débit, latence, effets dupliqués après panne, répartition entre machines. L'hétérogénéité visée est celle des **formats** ; l'analyse conjointe d'un même incident est explicitement hors question.

Pourquoi ce n'est pas du HARKing : la question et les QR sont un cadrage, non des prédictions ; la reformulation **retire** des attributs non mesurés (réduction, forme a) et ne change aucune hypothèse. La dépendance au protocole (nouvelle QR6) figure déjà dans la démarche initiale (introduction, « Démarche méthodologique » : « L'objectif est d'observer dans quelle mesure la constitution des ensembles d'entraînement et de test modifie les performances » ; « Contributions » : « L'apport méthodologique tient surtout au protocole d'évaluation »).

### 6.3 Classification en trois catégories

| QR (reformulée) | Catégorie | Ce que le mémoire mesure réellement | Hyp. | Réponse |
|---|---|---|---|---|
| QR1 sources lues et remplissage du schéma | Exigence de réalisation + propriété opérationnelle | Lecture/émission 7 001 unités ; remplissage par source (7/7 à 0/7) | H1 | Exigence satisfaite ; pas de preuve de rapprochement sans perte |
| QR2 organisation des agents et son coût | Exigence + propriété opérationnelle | Tests du noyau ; débit A–D ; panne appariée ; multi-VM (1,23 % ; HDFS distribué sur un seul agent) | H2 | Exigence satisfaite ; coût mesuré, défavorable ; aucun avantage propre aux agents |
| QR3 routeur | Exigence + hypothèse comparative | Décisions du routeur (20/20, 3/46, 43/43) ; comparaison sans routage **non exécutée** | H3 | Exigence satisfaite ; hypothèse non tranchée |
| QR4 tableau de bord | Exigence de réalisation | Captures des fonctions ; **aucune** mesure d'utilité | — | Exigence satisfaite ; utilité pour l'analyste non établie |
| QR5 mémoire et mise à jour | Hypothèse comparative + exigence | C contre D ; procédure de promotion testée sur des branches | H5 | Hypothèse réfutée ; exigence (procédure) partiellement vérifiée |
| QR6 dépendance des scores au protocole | Hypothèse comparative (H4) + propriété mesurée | Aléatoire / scénario / temporel ; événement / bloc ; connu / inconnu ; règles triviales | H4 | Réponse la plus nette : sur 3 jeux sur 4, le score principal n'excède pas une règle triviale |

Les exigences des QR1–QR5 recoupent le tableau 2.1 (`tab:exigences-fonctionnelles`) ; le coordinateur peut y renvoyer.

## 7. Revendications retirées ou réduites

| Revendication | Localisation (repère textuel) | Traitement | Fichier livré / agent |
|---|---|---|---|
| Préenregistrement : « Les seuils numériques et les budgets sont fixés dans le protocole avant l'exécution » | intro, p. 7 | **Retirée** ; remplacée par ce qui est vérifiable (seuils sur validation, seuil du routeur gelé) et par la liste des grandeurs jamais fixées | `__hypotheses_criteres.tex` |
| Priorisation des anomalies | question centrale ; QR5 ; objectif général (« détection et priorisation ») ; H5 (énoncé conservé tel quel) ; état de l'art « Le prototype détecte, priorise et rapproche » ; chapitre 2 « automatiser la préparation et la priorisation des signaux » | **Retirée** de la question, des QR et de l'objectif ; déclarée « prévue par la conception, non évaluée » | `__question_centrale_QR.tex`, `__objectif_general.tex`, tableau 1.3, limites ; état de l'art et ch. 2 : Agent 3 / Agent 0 |
| Traitements périodiques, micro-lots | question centrale ; §2.23.2 | **Retirés** de la question ; déclarés non évalués (limites) | idem ; §2.23.2 : mention « non évalué » à ajouter (Agent 0) |
| « Exploitable par un analyste » ; utilité du tableau de bord | question centrale ; QR4 | **Réduite** à l'exigence fonctionnelle ; « il n'est pas établi que cette interface améliore le travail d'un analyste » | `__question_centrale_QR.tex`, `__reponses_QR.tex`, tableau 1.3 |
| QR6 « la mieux couverte » | conclusion ; trois résumés | **Retirée** | `__reponses_QR.tex`, résumés |
| H1 : normalisation « conforme » et conservation de l'information | tableau 7.1 ; QR1 conclusion (« leur provenance reste identifiable ») | **Réduite** à une exigence de réalisation ; « provenance identifiable » retirée (non mesurée dans le corps) | tableau 7.1, QR1 |
| H2 : bénéfice des agents par l'idempotence | tableau 7.1 ; résumés (Agent 1, K17) | **Réduite** : propriété du magasin, transposable | tableau 7.1, QR2 ; résumé : Agent 5 |
| H3 : « le gain prédictif n'est pas systématique » | tableau 7.1 ; §4.7 ; §6.2 ; QR3 | **Retirée** de la conclusion (ablation absente du corps) | tableau 7.1, QR3 ; §4.7 et §6.2 : Agent 4 |
| H4 « partiellement soutenue » | tableau 7.1 ; résumés | **Retirée** ; non tranchée, supériorité infirmée sur trois jeux | tableau 7.1, résumés |
| BGL lu avec la seule baseline battue (template inconnu) | conclusion, « Bilan » | **Corrigée** : la règle de sévérité égale Histogram | `chapitre6_conclusion.tex__bilan_BGL.tex` |
| Hétérogénéité comme bénéfice (analyse conjointe) | titre ; question centrale ; QR1 | **Réduite** à l'hétérogénéité des formats ; absence d'analyse conjointe déclarée (conclusion, résumés, limites, tableau 1.3) | plusieurs fichiers livrés |
| Distribution : « autonome, distribué, multitâche » dans la question | p. 4 (lot A1-a) | Phrase p. 4 réécrite pour ne plus renvoyer à la question | `__positionnement_l58.tex` |

## 8. Expériences qui trancheraient les points ouverts (non exécutées)

Règle commune, si l'auteur décide d'en exécuter une : écrire le protocole (comparateur, métrique, critère numérique, taille, graines) dans un fichier, le **versionner avant l'exécution** (commit horodaté, empreinte SHA-256 dans le manifeste), puis exécuter. C'est la seule forme de critère « fixé à l'avance » que le mémoire pourra revendiquer, et seulement pour ces nouvelles expériences. Les hypothèses H1–H5 restent jugées sur leur énoncé.

| Id | Point | Comparateur | Métrique et critère (à fixer avant) | Taille | Faisabilité (code et données du dépôt) |
|---|---|---|---|---|---|
| E-H3 | H3, composante (i) | (1) Table de routage statique (extension, en-tête de colonnes, nom de fichier) ; (2) pipeline unique par défaut, à titre de borne | Taux d'exécutions incompatibles = part des fichiers acheminés vers un traitement dont la famille diffère de l'étiquette fixée avant routage, ou acceptés alors qu'inconnus ; test de McNemar exact apparié sur les mêmes fichiers ; critère : réduction ≥ 10 points, p < 0,05 | Les 66 fichiers de §4.7 sont déjà connus : un **nouveau** jeu indépendant est nécessaire ; au moins 30 inconnus et 60 connus pour un IC de largeur ≈ 0,1 | **Élevée** pour le code : [R] `agent_5_router_open_set/routes.csv` et `sources_config.json`, `scripts/run_router_open_set_consolidation.py` ; table statique : quelques dizaines de lignes ; ½ à 1 jour. **Limite** : peu de fichiers locaux nouveaux (aucun corpus Apache réel trouvé localement). |
| E-H3b | H3, composante (ii) | Modèle commun contre modèles par famille, mêmes variables et partitions | F1 et FPR par famille, 5 graines ou plus, partition par scénario ou temporelle ; critère : différence de F1 ≥ −0,01 (non-infériorité) avec IC apparié | 3 familles × 5 graines | **Élevée** : `scripts/run_family_routing_ablation.py`, [P] `family_routing_ablation.csv` (une exécution) ; ½ jour. |
| E-H5 | H5, composante (i) | C contre D, **avec des agents de fiabilité ou de latence hétérogènes** (ex. : un agent échoue avec probabilité 0,3 sur un type de tâche), même flux de tâches et mêmes graines d'échec | Métrique fixée d'avance : taux d'échec à la première attribution (ou nombre de réattributions par tâche) ; critère : réduction avec IC apparié excluant 0, débit non dégradé de plus de 5 % | 30 graines × 1 à 2 charges | **Élevée à moyenne** : `scripts/run_true_multi_agent_experiments.py` (benchmark, `build_agents`) ; injection d'échecs à ajouter (enveloppe de handler à graine, ~50 lignes) ; minutes d'exécution. Seule l'attribution est « priorisée » par la mémoire actuelle (§3.5.1). |
| E-H5b | H5, priorisation des anomalies (si l'auteur tient au terme) | Classement des anomalies avec et sans mémoire de retours d'analyste | Précision@k des anomalies confirmées ; nécessite des décisions d'analyste étiquetées | ≥ 200 décisions étiquetées | **Faible** : `src/logminer/agents/feedback_memory.py` et `scripts/run_memory_feedback_ablation.py` existent, mais l'audit réel ne contient **aucune** décision d'analyste (`docs/memoire/tables/table_memory_feedback_ablation.md` : 0 décision ; scénario simulé seulement). |
| E-H5c | H5, composante (ii) | Candidats volontairement meilleurs et moins bons | Proportion de décisions conformes à la règle (attendu 100 %) ; variation du F1 sur test indépendant après décision | ≥ 10 candidats | **Moyenne** : `scripts/monthly_model_retraining.py`, `scripts/prepare_model_update_e2e.py`, mode dry-run ; 1 à 2 jours. Déjà décrite en perspective (conclusion, §6.8). |
| E-H4 | H4 sur HDFS | Baselines au niveau bloc : tout positif ; « bloc contenant un template inconnu de l'entraînement » ; comptage d'événements rares ; éventuellement PCA/Isolation Forest sur vecteurs de comptage (type Loglizer) | F1 au niveau bloc sur les 115 013 blocs du test, même parseur gelé, même seuil sur validation | Partition existante | **Moyenne** : [R] `agent_2_hdfs/*`, `scripts/run_hdfs_block_strengthening.py` ; le tout-positif se déduit de la prévalence (1 679/115 013) ; les autres demandent de recalculer les templates par bloc (heures). **La composante budget (c) reste impossible à fixer rétroactivement** : H4 ne deviendra pas « validée » ; au mieux, la supériorité sur HDFS sera établie ou infirmée. |
| E-H2 | H2, composante (ii) | Architecture C sans magasin d'idempotence | Effets dupliqués sur 10 répétitions | 10 | **Très élevée** (rendre `store` optionnel dans `revision_reports/agent_3/run_paired_failure_abcd.py::run_cnp`) ; minutes. **Non recommandée** : issue connue par construction (A et B) ; la requalification suffit. |
| E-HET | Scénario hétérogène conjoint (L3) | Détection d'incident par une source seule contre la combinaison journal système + flux réseau du même incident | Rappel par incident, faux incidents par heure, délai de détection | Échantillon DARPA 1998 : 13 sessions d'attaque dans `bsm.list`, 39 dans `tcpdump.list` (30 port-scan, 4 guess, 2 rsh, 1 rcp, 1 rlogin, 1 phf), une journée | **Faible à moyenne** : `data/raw/Datasets/DARPA_eval_b/DARPA_eval_b/` contient l'audit BSM et le tcpdump d'une même journée avec vérité terrain par session ; jeu ancien et critiqué, effectifs très petits (démonstration, pas estimation). Alternative : scénario d'attaque contrôlé dans les deux VM (auth.log + capture réseau), 1 à 2 semaines. Faisabilité détaillée : Agent 4. |

## 9. Implications pour les autres agents

**Agent 4 (méthodologie)**
- Ajouter au corps la prédiction tout positif pour **chaque** test comparatif (mission déjà prévue) ; en particulier le holdout par scénario CICIDS2017 (0,473265 en moyenne, au-dessus des cinq candidats ; calcul §4, H4) et le niveau bloc HDFS. Sans cela, la nouvelle QR6 et le tableau 7.1 ne peuvent citer ces chiffres (C8).
- §4.7 dernier paragraphe et §6.2 : « l'ablation montre que l'acheminement fonctionne, mais aucun gain de F1 n'apparaît de manière constante dans toutes les familles et graines » n'a ni tableau ni artefact ; l'artefact candidat ([P] `family_routing_ablation.csv`) est une exécution unique sans graines : retirer ou présenter avec ses limites.
- Composante (iii) de H1 : documenter, si l'auteur le souhaite, la référence par unité ([D] `raw/multiformat_balanced_20260910T094422Z_units.csv` : index, chemin, SHA-256) et interpréter `original_message_test` (4 000 FALSE) avant toute citation.
- Les protocoles BGL complémentaires (tableau 4.4) doivent être présentés comme exploratoires ; aucun ne compte pour H4.
- E-H4 et E-HET : avis de faisabilité.

**Agent 5 (architecture)**
- §4.9 : ajouter les différences appariées D − C (débit, latence p95, équité, RSS) de [M] `aggregated/ma_20260909T160812Z_34016__paired_memory_effects.csv` ; elles sourcent la réfutation de H5 (actuellement fondée sur la seule phrase « pas d'amélioration systématique »).
- Ajouter au corps la phrase « aucune expérience ne compare l'attribution par Contract Net à une affectation statique » (QR2 la cite).
- Vérifier l'interprétation « la mémoire favorise l'agent déjà servi » (§4, H5) avant de l'utiliser.
- Paragraphes « architecture » des résumés : partir de **`agent_2/sections/main.tex__*.tex`** (qui intègrent déjà le paragraphe « hypothèses » final).
- Conclusion générale (« l'architecture est fonctionnelle, modulaire et auditable ») et §6.7 (« attribution explicite, refus, reprise ») : auditabilité et refus non mesurés.

**Agent 3 (état de l'art)**
- Tableau 1.3 : quatre lignes livrées (`chapitre2_etat_art.tex__tableau_1.3_positionnement.tex`) ; à reprendre s'il refond le tableau.
- §1.23.2 et l'état de l'art (« Le prototype détecte, priorise et rapproche ») : retirer « priorise ».
- La nouvelle QR6 est une réplication de critiques publiées (Sommer et Paxson ; Arp et al. ; Engelen et al. ; Le et Zhang) : la réponse livrée le dit en une phrase et cite `sommer2010outside`, `arp2022dos`, `engelen2021troubleshooting` (clés existantes) ; à positionner au chapitre 6.

**Agent 8 (verdict)**
- Aucune hypothèse comparative n'est soutenue ; H1 et H2 sont des exigences de réalisation ; H5 réfutée ; H4 infirmée sur trois jeux et plus validable (budget). Le travail établit des exigences, des coûts et un constat de dépendance au protocole déjà connu de la littérature.
- Absence de scénario hétérogène conjoint : revendication réduite dans le texte, mais le point de non-recevabilité de L3 n'est levé que par une expérience (E-HET).

**Agent 0 (intégration)**
- Le lot A1-a a intégré une phrase p. 4 qui renvoie aux qualificatifs de la question centrale : à remplacer si la question reformulée est retenue (`__positionnement_l58.tex`).
- Tableau 2.3 (`tab:architecture-qr`, `chapitre3_modele_propose.tex`) : la ligne QR6 (« Évaluer le prototype avec des preuves quantitatives et fonctionnelles reproductibles ») doit devenir « Mesurer la dépendance des scores au protocole, à l'unité d'analyse et aux règles triviales » si la QR6 reformulée est retenue ; la ligne QR5 devrait dire « effet de la mémoire » au lieu de « persistance des décisions ».
- §2.23.2 (micro-lots) et chapitre 2 (« automatiser la préparation et la priorisation des signaux ») : ajouter « non évalué ».
- Les fichiers de l'Agent 1 `chapitre1_introduction.tex__hypotheses_preenregistrement.tex`, `chapitre6_conclusion.tex__tableau_7.1.tex`, `chapitre6_conclusion.tex__QR3_QR6.tex` et `main.tex__*.tex` sont **remplacés** par ceux de l'Agent 2 (C7, C9).

## 10. Points laissés en suspens

- **Lingala** : le paragraphe réécrit du Bokuse n'est pas relu par un locuteur natif (termes signalés en tête de fichier).
- **H4, libellé** : « non tranchée » (R4) ou « réfutée » (lecture littérale) : Q1.
- **H1, composante (iii)** : dépend de ce que l'Agent 4 ajoute au corps ; le statut ne change pas.
- **Réfutation de H5 dans le corps** : solide sur le fond (artefact), mais le corps ne contient qu'une phrase ; dépend de l'Agent 5 (§9).
- **Holdout par scénario CICIDS2017** : le chiffre 0,473265 est un calcul de l'Agent 2 sur l'artefact (formule 2p/(1+p), vérifiée par ailleurs sur le test temporel : p = 0,5 donne 0,666667) ; il n'est utilisé dans aucune section livrée tant que l'Agent 4 ne l'a pas introduit.
- **Sections non réécrites** mais touchées par les statuts : §5.7 (« Conclusions soutenues »), §6.7, conclusion « Apports » et « Conclusion générale » (Agents 1, 5, 7).

## 11. Questions au coordinateur

- **Q1 (H4).** Retenir « NON TRANCHÉE ; supériorité infirmée sur trois jeux » (recommandé : règle R4, l'énoncé est existentiel et HDFS reste ouvert) ou « RÉFUTÉE » (lecture littérale du critère : aucun candidat ne satisfait conjointement, et aucun ne le pourra faute de budget) ? Les deux excluent « partiellement soutenue ». Les sections livrées appliquent la première.
- **Q2 (règles R1–R6).** Valider leur énoncé dans la conclusion (section livrée). Elles sont présentées comme règles d'application, non comme critères préexistants.
- **Q3 (question centrale et QR).** Retenir la reformulation (en particulier QR6 transformée en question sur la dépendance au protocole) ? Sinon, conserver les anciennes QR et utiliser la variante QR6 fournie en fin de `__reponses_QR.tex` ; dans ce cas, ne pas intégrer `__positionnement_l58.tex`.
- **Q4 (périmètres partagés).** Les fichiers `limites_consolidees.tex__grandeurs_non_mesurees.tex` et `chapitre2_etat_art.tex__tableau_1.3_positionnement.tex` touchent les limites et l'état de l'art ; arbitrer l'intégration (proposition : intégrer maintenant, l'Agent 3 reprendra le tableau 1.3 s'il le refond).
- **Q5 (expériences).** Décision de l'auteur : exécuter ou non E-H3, E-H5, E-H4, E-HET (§8). Sans elles, les sections livrées sont définitives ; avec elles, seul le tableau 7.1 et la QR concernée changent, et le protocole doit être versionné avant exécution.

## 12. Fichiers livrés et contrôle

Tous dans `revision_reports/chantier_20261105/agent_2/` :

| Fichier | Cible (repère textuel) | Remplace |
|---|---|---|
| `LIVRABLE_2_hypotheses.md` | — | — |
| `sections/chapitre1_introduction.tex__question_centrale_QR.tex` | section « Question centrale et questions de recherche » entière | — |
| `sections/chapitre1_introduction.tex__hypotheses_criteres.tex` | section « Hypothèses de recherche » entière (H1–H5 mot pour mot) | `agent_1/.../__hypotheses_preenregistrement.tex` |
| `sections/chapitre1_introduction.tex__positionnement_l58.tex` | 1re phrase de « Positionnement… » (lot A1-a) | — |
| `sections/chapitre1_introduction.tex__objectif_general.tex` | 1re phrase de l'objectif général | — |
| `sections/chapitre6_conclusion.tex__reponses_QR.tex` | `\begin{description}` … `\end{description}` des QR | `agent_1/.../__QR3_QR6.tex` |
| `sections/chapitre6_conclusion.tex__statut_hypotheses_tableau_7.1.tex` | paragraphe « Le statut des hypothèses… » + tableau 7.1 | `agent_1/.../__tableau_7.1.tex` |
| `sections/chapitre6_conclusion.tex__bilan_BGL.tex` | phrase BGL du « Bilan » | — |
| `sections/chapitre2_etat_art.tex__tableau_1.3_positionnement.tex` | lignes Hétérogénéité, Mémoire, (+ Priorisation), Dashboard | — |
| `sections/limites_consolidees.tex__grandeurs_non_mesurees.tex` | ajout en fin de « Grandeurs non mesurées » | — |
| `sections/main.tex__resume_fr.tex` | `main.tex` l. 278–382 (plage de l'Agent 1, vérifiée) | `agent_1/.../main.tex__resume_fr.tex` |
| `sections/main.tex__abstract_en.tex` | `main.tex` l. 399–499 | `agent_1/.../main.tex__abstract_en.tex` |
| `sections/main.tex__bokuse_ln.tex` | `main.tex` l. 517–626 | `agent_1/.../main.tex__bokuse_ln.tex` |

Contrôle de compilation : toutes les sections ci-dessus appliquées à une copie du manuscrit dans le répertoire temporaire de session (script `apply_agent2.py`, non livré : remplacements par repère textuel et, pour `main.tex`, par les plages de l'Agent 1), puis `pdflatex` → `bibtex` → `pdflatex` ×2 : **0 erreur, 0 débordement, 0 référence ni citation indéfinie, 171 pages**. Labels nouveaux : `tab:nature-qr` seulement (défini dans la section livrée) ; tous les autres labels cités existent.
