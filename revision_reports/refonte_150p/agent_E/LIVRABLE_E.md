# LIVRABLE E — Forme, redondance, lisibilité et volume

Agent E, chantier « Refonte 150 pages », 2026-11-05. Aucun `.tex` modifié.

Mesures faites sur `main.pdf` (180 pages), texte extrait par `pdftotext -enc UTF-8 -layout`, sur `main.toc`, `main.lot`, `main.lof` et `references.bib`. Correspondance des pages : page arabe *p* = page physique *p* + 23. Il y a donc 23 pages liminaires (titre et pages i–xxii) et 157 pages arabes (1–157).

---

## 1. Classement des reproches du périmètre

| # | Reproche | Classement | Preuve |
|---|---|---|---|
| E1 | Redondance massive : « 0,1577 » ×9, « 0,8724 » ×14, « 20/20 » ×14, « 7 001 » ×10 (L2 §2.5) | **Fondé** ; un compte est sous-estimé | Recompté dans le PDF : 0,1577 → **9** ; 0,8724 → **14** ; 20/20 → **14** ; 7 001 → **14** (et non 10). Voir le détail par partie ci-dessous |
| E2 | « Le chapitre 7 et l'annexe A.3 redoublent les chapitres 4 et 5 » (L2 §2.5) | **Partiellement fondé** | La matrice A.3 (tableau A.2, p. 143–147) est le seul endroit légitime des identifiants de campagne : elle doit rester, mais sans recopier les commentaires des résultats. Le ch. 7 (p. 131–134) recoupe le ch. 3.13, l'annexe (A.4–A.6) et le ch. 5.8. L'annexe A.9, « Notes détaillées des figures » (p. 149–152, environ 3,5 p.), redouble les légendes et les paragraphes du ch. 4 : c'est le doublon le plus net, que le lecteur ne cite pas |
| E3 | Résumé illisible, liste de chiffres (L2 §2.5) | **Fondé** | Résumé : 446 mots et 15 valeurs numériques (`main.tex`, l. 278–288). Abstract : 407 mots |
| E4 | Bokuse plus long et différent du résumé, avec des intervalles absents (L2 §2.5) | **Fondé** | Bokuse : 988 mots (deux fois le résumé), p. x–xii. Divergences listées au §3.3 |
| E5 | Jargon des identifiants internes dans les légendes et le corps (L2 §2.5) | **Fondé** | 29 run_id dans `chapitre5_resultats.tex` (pages 88–115 du PDF). Les codes de protocole (E-H3, E-CNP-LEAST-LOADED…) apparaissent dans l'introduction (6), le ch. 7 (15), la déclaration IA (6), le ch. 4 (8), la discussion (2) et la conclusion (1). Inventaire au §4 |
| E6 | Précision numérique incohérente, « [0,8568 ; 0,879493] » (L2 §2.5) | **Fondé, mais limité** | Dans le corps (p. 1–141), seules 7 valeurs ont plus de quatre décimales : p. 89, 90, 91, 94, 123 et le bokuse. L'annexe en compte 72 (six décimales). Liste au §5 |
| E7 | Bibliographie : pages web consultées le jour de la compilation, aucun DOI, Sharafaldin pour deux jeux (L2 §2.5) | **Partiellement fondé** | (a) 10 entrées `@misc` web, « consultées le 5 novembre 2026 » (`references.bib`, l. 468–540), plus une au 4 novembre (l. 344). Le lecteur en compte 9. Elles font 10 entrées sur 57 : « dominée » est **inexact**. (b) « Aucun DOI » est **fondé dans le PDF, mais pour une cause technique** : 34 entrées sur 57 ont un champ `doi`, et le style `plain-fr` ne l'imprime pas (0 occurrence de « doi » dans les pages 153–157). (c) Sharafaldin : **inexact en tant que défaut**. Une seule entrée, `sharafaldin2018cicids`, sert aux deux jeux, parce que le CIC demande de citer l'article ICISSP 2018 pour CSE-CIC-IDS2018 aussi (note de `cic2018csecicids`, l. 344). Il faut le dire dans le texte |
| E8 | Tableaux 1.4, 1.5 et 7.1 surchargés au point d'être illisibles (L2 §2.5) | **Fondé** | 1.4 : 9 lignes × 4 colonnes en `\scriptsize` (p. 40). 1.5 : 10 lignes × 5 colonnes en `\scriptsize` (p. 41). 7.1 : 5 lignes, avec des cellules de 80 à 150 mots en `\scriptsize` (p. 138) |
| E9 | Fragmentation : 26 sections au ch. 1, 26 au ch. 2 (L1 §F) | **Fondé** | `main.toc` : ch. 1 = 26 sections sur 30 pages (1,15 p. par section) ; ch. 2 = 26 sections sur 28 pages (1,08 p. par section) |
| E10 | Distinction implémenté / testé / supérieur dispersée entre les ch. 4 à 7 (L1 §F) | **Fondé** (fond, signalé) | Elle apparaît en 4.16, 5.7, 6.2–6.7, dans le tableau 7.1 et dans « Apports » de la conclusion. Arbitrage : agent d'intégration (section unique de synthèse) |
| E11 | Ch. 2 rédigé au conditionnel (L2 §2.4, pour mémoire) | **Fondé** (signalé à A et D) | 57 occurrences de « peut », « peuvent » ou « pourrait » dans `chapitre3_modele_propose.tex` |

### Répétitions par partie (nombre d'occurrences dans le PDF)

| Valeur | Liminaires | Ch. 3 | Ch. 4 | Ch. 5 | Ch. 6 | Concl. | Annexe |
|---|---|---|---|---|---|---|---|
| 0,9951 | 2 | – | 2 | 2 | – | 2 | 2 |
| 0,1577 | 2 | – | 2 | 1 | – | 2 | 2 |
| 0,8684 | 2 | – | 5 | 1 | 1 | 3 | – |
| 0,868373 (même valeur, 6 déc.) | – | – | – | – | – | – | 10 |
| 0,8724 | 1 | – | 2 | 1 | 1 | 3 | 6 |
| 0,9137 | 2 | – | 6 | – | – | 2 | – |
| 0,9997 | 2 | – | 5 | 2 | – | 2 | 2 |
| 20/20 | 3 | – | 4 | 3 | – | 2 | 2 |
| 3/46 | 3 | – | 1 | 4 | – | 2 | 2 |
| 7 001 | 3 | 1 | 1 | – | – | 4 | 5 |
| 1,23 | 2 | – | 1 | – | – | 1 | – |

Les résultats sont répétés surtout dans les **résumés**, le **ch. 5** (validité), la **conclusion** et l'**annexe**. L'introduction et le ch. 1 ne contiennent aucune de ces valeurs. Les anticipations du ch. 1 signalées par L2 §2.4 sont qualitatives : elles relèvent de l'Agent D.

**Règle proposée.** Chaque valeur est donnée en détail, avec son intervalle, une seule fois, à sa section du ch. 4. Le résumé donne au plus trois chiffres. La conclusion et le ch. 5 renvoient au ch. 4 et à la section unique de synthèse, et ne citent un chiffre que lorsque l'argument en dépend, au plus une fois par chapitre. L'annexe A.2 garde les valeurs à six décimales, puisqu'elle sert de référence de traçabilité, mais sans phrases de commentaire.

---

## 2. Cartographie des pages et cible de 150 pages

### 2.1 Pages actuelles (`main.toc`)

| Partie | Pages | Nb | Sections |
|---|---|---|---|
| Titre et liminaires (épigraphe, dédicace, remerciements i–iii ; déclaration IA iv–v ; résumé vi–vii ; abstract viii–ix ; bokuse x–xii ; table des matières xiii–xvii ; figures xviii ; tableaux xix–xx ; sigles xxi–xxii) | — | 23 | — |
| Introduction générale | 1–15 | 15 | 10 |
| Ch. 1 État de l'art | 16–45 | 30 | 26 |
| Ch. 2 Modèle proposé | 46–73 | 28 | 26 |
| Ch. 3 Implémentation | 74–83 | 10 | 13 |
| Ch. 4 Résultats | 84–117 | 34 | 16 (18 figures, 15 tableaux) |
| Ch. 5 Validité | 118–124 | 7 | 8 |
| Ch. 6 Discussion | 125–130 | 6 | 8 |
| Ch. 7 Reproductibilité | 131–134 | 4 | 7 |
| Conclusion | 135–141 | 7 | 7 |
| Annexe A | 142–152 | 11 | 9 |
| Bibliographie | 153–157 | 5 | 57 entrées |
| **Total** | | **180** | |

Détail des sections longues du ch. 4 : 4.2 CICIDS2017, 3 p. (85–87) ; 4.3 HDFS, 3 p. ; 4.4 BGL, 3 p. ; 4.6 CSE-CIC-IDS2018, **6 p.** (95–100, 5 figures : 4.7–4.11) ; 4.10 benchmark A–D, **6 p.** (104–109) ; 4.12 multi-VM, 4 p. (111–114). Annexe : A.3 matrice, 4 p. (143–146) ; A.9 notes des figures, 3,5 p. (149–152).

### 2.2 Doublons de fond signalés (non arbitrés ici)

| Thème | Lieux | Agent compétent |
|---|---|---|
| Limites | Intro « Délimitations » (p. 13) ; 2.25 Frontières, tableau 2.4 (p. 71) ; 5.8 Limites et `limites_consolidees.tex` (p. 123) ; 7.6–7.7 (p. 133–134) ; conclusion « Limites » (p. 139) | intégration (règle : une seule section) |
| Contributions et positionnement | Intro « Contributions » (p. 12) ; 1.24–1.25 et tableau 1.6 (p. 42–45) ; 6.7 (p. 129) ; conclusion « Apports » (p. 139) | D |
| Réponses aux QR et statut des hypothèses | Tableau 2 de l'intro (p. 7) ; 2.24, tableau 2.3 (p. 70) ; 5.7 Conclusions soutenues (p. 122) ; conclusion « Réponse aux QR » et tableau 7.1 (p. 136–138) | A (tableau unique) |
| Implémenté / testé / supérieur | 4.16 ; 5.7 ; 6.2–6.7 ; tableau 7.1 ; « Apports » | intégration (section unique de synthèse) |
| Reproductibilité | 1.21 (p. 38) ; 3.13 (p. 83) ; ch. 7 entier ; A.3–A.6 | F |
| Reprise et idempotence | 1.15 ; 2.19–2.20 ; 3.6 ; 6.4 | B, intégration |

### 2.3 Cible chiffrée : 180 → 150 pages

« Forme » : gain obtenu par ce livrable seul (réécriture, fusion, renvois). « Fond » : gain qui dépend d'une décision d'un autre agent ; c'est une estimation.

| Partie | Actuel | Cible | Gain | Dont forme | Dont fond (agent) | Moyens |
|---|---|---|---|---|---|---|
| Liminaires | 23 | 19 | −4 | −4 | — | Résumé et abstract d'une page chacun (−2) ; bokuse aligné, environ 1,5 p. (−1,5) ; table des matières raccourcie par les fusions de sections (−1). La déclaration IA reste à 2 p. (F) |
| Introduction | 15 | 11 | −4 | −2 | −2 (A) | « Contributions », « Délimitations » et « Organisation » ramenées à des paragraphes ; tableau QR unique (A) ; définitions opérationnelles non répétées en 1.25 |
| Ch. 1 | 30 | 22 | −8 | −5 | −3 (D) | 26 sections fusionnées en 8 (voir plus bas) ; tableaux 1.4 et 1.5 condensés (−1) ; 1.21 reproductibilité fondue dans le ch. 7 ou l'annexe (−1) ; LOF, One-Class SVM et Extra Trees retirés, 1.24–1.26 sans anticipation de résultats (D) |
| Ch. 2 | 28 | 22 | −6 | −4 | −2 (A, D) | 26 sections fusionnées en 9 ; 2.24 et tableau 2.3 supprimés au profit du tableau QR unique (A) ; 2.25 et tableau 2.4 fondus dans la section unique des limites ; 2.22–2.23 (sécurité, scénarios) réduits à une demi-page |
| Ch. 3 | 10 | 9 | −1 | −1 | — | 3.13 « Lien entre code et preuves » remplacé par un renvoi à A.2 |
| Ch. 4 | 34 | 29 | −5 | −3 | −2 (C) | Identifiants retirés des légendes ; 4.16 remplacé par la section unique de synthèse ; CSE-CIC 4.6 : les figures 4.8–4.11 deviennent un seul tableau (−2), ou la section disparaît selon C (−6) ; 4.5 réduit à un paragraphe ; tableau 4.5 BGL en annexe si C le décide |
| Ch. 5 + 6 + 7 | 17 | 12 | −5 | −4 | −1 (F) | Ch. 7 réduit à une section de 1,5 p. (« Disponibilité et reproduction »), ou intégré à l'annexe (−2,5) ; 5.7 et 5.8 fusionnés avec la section unique de synthèse et des limites (−1,5) ; chiffres remplacés par des renvois (−1) |
| Conclusion | 7 | 5 | −2 | −2 | — | Tableau 7.1 refondu (voir §6) ; « Réponse aux QR » sans chiffres détaillés |
| Annexe A | 11 | 8 | −3 | −3 | — | A.9 supprimée : son contenu utile passe dans les légendes (−3) ; A.8 fondue dans le ch. 5 ; A.2 conservée, colonnes resserrées |
| Bibliographie | 5 | 6 | +1 | +0,5 | +0,5 (D) | DOI imprimés ; références ajoutées par D (allocation de charge, jeux de données) |
| Ajouts des autres agents | — | — | +4 | — | +4 | Section unique de synthèse (environ +2), filiation d'Histogram, littérature d'allocation, annexe de défense hors manuscrit (F) |
| **Total** | **180** | **≈ 151** | **≈ −29** | **≈ −22,5** | **≈ −6,5** | |

Pour descendre de 151 à 150 : passer en annexe le tableau 4.5 (BGL, variantes exploratoires) et la figure 4.4 (bootstrap HDFS), si C et B l'acceptent. Il ne faut pas réduire la mise en page (police, marges, interligne) : ce serait un gain artificiel que le jury verrait.

### 2.4 Fusion des sections des ch. 1 et 2

**Ch. 1, de 26 à 8 sections :**
1. Journaux, détection d'intrusion et règles (1.1–1.4).
2. Apprentissage pour la détection et déséquilibre (1.5–1.7, sans LOF ni One-Class SVM : D).
3. Jeux de données et validité des évaluations (1.8, présentation de tous les jeux utilisés : D).
4. Parsing, normalisation et représentations (1.9–1.12).
5. Orchestration : cadres intégrés, agents, files, livraison et idempotence, routage (1.13–1.16, tableaux 1.2–1.3).
6. Corrélation, mémoire, gouvernance et analyste (1.17–1.20).
7. Comparaison et positionnement (1.22–1.25, tableaux 1.4–1.6 fondus en deux).
8. Synthèse (1.26, une demi-page).

1.21 (reproductibilité) passe au ch. 7 ou à l'annexe.

**Ch. 2, de 26 à 9 sections :**
1. Exigences et principes (2.1–2.3).
2. Architecture générale et plans (2.4–2.5).
3. Agents et cycle de vie d'une donnée (2.6–2.7).
4. Normalisation, routage, portefeuille, corrélation (2.8–2.11).
5. Mémoire, audit, gouvernance (2.12–2.13, 2.17).
6. Messages, bus, tâches et utilité (2.14–2.16, `spec_utilite.tex`).
7. Erreurs, reprise, topologies (2.19–2.21).
8. Interface et sécurité (2.18, 2.22–2.23, condensés).
9. Synthèse (2.26 ; 2.24–2.25 retirées, voir §2.2).

---

## 3. Résumé, abstract, bokuse

Ces propositions dépendent du titre et de la thèse retenus par l'Agent A ; il faudra les ajuster après son arbitrage. Chaque affirmation reprend une valeur déjà présente dans le manuscrit. Il n'y a aucun chiffre nouveau.

### 3.1 Résumé proposé (≈ 300 mots, 3 chiffres)

> Ce mémoire conçoit et évalue en laboratoire Ariel Logminer, une architecture multi-agents légère pour l'analyse de journaux système et réseau de formats différents. Les agents y sont des composants logiciels qui déclarent leurs capacités, conservent un état et se répartissent les tâches par le protocole Contract Net. Le travail ne propose aucun nouvel algorithme : il mesure ce que cette organisation apporte et ce qu'elle coûte, en confrontant chaque mécanisme à une solution plus simple, sur un ou deux hôtes.
>
> Sur quatre jeux de données publics, les scores dépendent d'abord du protocole d'évaluation. Sur CICIDS2017, le F1 d'un Random Forest passe de 0,9951 à 0,1577 lorsqu'un scénario d'attaque est tenu hors de l'entraînement. Sous les protocoles stricts, aucun modèle retenu ne dépasse la meilleure règle simple évaluée sur le même test, ce qui réplique des critiques déjà publiées.
>
> Les adaptateurs lisent tous les formats testés, mais le schéma commun reste vide pour les flux réseau tabulaires. Chaque source est analysée séparément : aucun incident n'est reconstitué à partir de journaux système et de flux réseau. Le routeur écarte les fichiers inconnus testés, au prix de quelques rejets à tort.
>
> Sur des microtâches, l'organisation en agents est nettement plus lente qu'un monolithe. L'absence de doublon après une panne tient au magasin d'idempotence, et non aux agents. Contract Net réduit les échecs par rapport à une table statique, mais un répartiteur au moindre chargé, sans négociation, obtient les mêmes taux d'échec avec un meilleur débit. La mémoire n'apporte de gain établi que pour une probabilité d'échec de 0,9, et une seconde machine virtuelle n'ajoute pas de capacité.
>
> Aucune des cinq hypothèses n'est validée. La contribution est méthodologique : une chaîne traçable et des comparaisons qui isolent l'effet de chaque mécanisme et montrent que, dans les conditions testées, une solution plus simple suffit souvent.

### 3.2 Abstract aligné

> This thesis designs and evaluates in a laboratory Ariel Logminer, a lightweight multi-agent architecture for analyzing system and network logs of different formats. Its agents are software components that declare capabilities, keep a state and allocate tasks through the Contract Net protocol. The work proposes no new algorithm: it measures what this organization brings and what it costs, by confronting each mechanism with a simpler solution, on one or two hosts.
>
> On four public datasets, scores depend first on the evaluation protocol. On CICIDS2017, the F1 of a Random Forest falls from 0.9951 to 0.1577 when an attack scenario is held out from training. Under strict protocols, no retained model exceeds the best simple rule evaluated on the same test set, which replicates published criticisms.
>
> The adapters read every tested format, but the common schema remains empty for tabular network flows. Each source is analyzed separately: no incident is reconstructed from both system logs and network flows. The router rejects the tested unknown files, at the cost of a few wrongful rejections.
>
> On microtasks, the agent organization is markedly slower than a monolith. The absence of duplicates after a failure comes from the idempotency store, not from the agents. Contract Net reduces failures compared with a static table, but a least-loaded dispatcher, without negotiation, reaches the same failure rates with higher throughput. Memory yields an established gain only at a failure probability of 0.9, and a second virtual machine adds no capacity.
>
> None of the five hypotheses is validated. The contribution is methodological: a traceable pipeline and comparisons that isolate the effect of each mechanism and show that, under the tested conditions, a simpler solution is often sufficient.

### 3.3 Bokuse : règle d'alignement et divergences actuelles

**Règle.** Le bokuse traduit le résumé paragraphe par paragraphe. Il garde le même nombre de paragraphes, les mêmes chiffres et rien de plus : pas d'intervalle, pas d'effectif, pas de résultat absent du résumé. La traduction et la relecture reviennent à un locuteur du lingala (décision C19) ; cet agent ne rédige pas en lingala.

**Divergences actuelles** (`main.tex`, l. 329–420, comparées au résumé, l. 278–288) :
1. Longueur : 988 mots contre 446.
2. Intervalle HDFS « IC 95 % : [0,8568 ; 0,879493] », absent du résumé, et avec une précision mixte (l. 359).
3. Effectifs absents du résumé : 115 013 blocs, 1 679 positifs (HDFS) ; 89,8081 % de templates inconnus, 0,2779 pour la règle « template inconnu » (BGL) ; 43 fichiers connus bien orientés.
4. Comparaison des cinq modèles CICIDS2017 (LR 0,2337, PR-AUC HistGradientBoosting 0,5690) : absente du résumé.
5. CSE-CIC-IDS2018 : 0,9992 (LR), 0,4014 (RF), transfert 0,2342 : absents (le résumé ne donne que 0,9997).
6. Benchmark : « 160 exécutions, 264 000 traitements » ; endurance « 1 800/1 800, Debian 451, Ubuntu 1 349 » ; saturation « 8–16 tâches/s » : absents.
7. Statuts d'hypothèses : le bokuse détaille H3–H5 (« NON TRANCHÉE » en capitales françaises) ; le résumé les résume en une phrase.
8. Contribution : « intégration architecturale mpe méthodologique » ; le résumé dit « méthodologique et d'ingénierie ». Ce n'est pas la même formulation.
9. La phrase « Ces constats répliquent des critiques déjà publiées » et la mention « aucun nouvel algorithme » manquent.

---

## 4. Identifiants internes : inventaire et étiquettes lisibles

Règle : les run_id et les noms de dossiers ne figurent que dans la matrice de traçabilité (annexe A.2), dans une colonne « Identifiant de campagne ». Le corps et les légendes utilisent l'étiquette lisible. Une note de lecture au début du ch. 4 annonce que chaque étiquette renvoie à une ligne de A.2. Les codes de protocole préenregistrés (E-…) restent dans A.2 et dans le registre des protocoles ; dans le corps, on emploie l'étiquette lisible, avec le code entre parenthèses à la première mention seulement si l'Agent C le juge nécessaire pour l'audit du préenregistrement.

| Identifiant (pages PDF du corps) | Étiquette proposée |
|---|---|
| `agent2_hdfs_full_20261104T131314Z` (88–90) | campagne HDFS, test complet |
| `hdfs_block_robustness_20260911T002351Z` (90) | campagne HDFS, échantillon de 2 000 blocs |
| `agent6_cicids_iforest_20261104T141904Z_summary` (88) | contrôle Isolation Forest, CICIDS2017 |
| `cicids_temporal_20260910T083015Z` (88) | campagne CICIDS2017, séparation temporelle |
| `agent4_bgl_second_protocol_20261104T142629Z` (92–93) | campagne BGL, second protocole |
| `agent4_bgl_contiguous_horizon_20261104T145740Z` (94) | campagne BGL, protocole contigu (G) |
| `agent6_strict_e3_aggregate_20261104T143019Z` (95) | contrôle Isolation Forest strict, HDFS et BGL |
| `agent4_csecic_shortcut_20261104T144738Z` (96, 100) | audit CSE-CIC-IDS2018 |
| `final_csecic_lr_forensic_20260911T000140Z` (100) | analyse des coefficients et permutation, CSE-CIC-IDS2018 |
| `agent5_router_open_set_20261104T145601Z` (101–102) | évaluation open-set du routeur |
| `multiformat_balanced_20260910T094422Z`, `agent5_multiformat_20261104T150111Z` (103–104) | campagne de couverture multi-format |
| `ma_20260909T160812Z` (105) | benchmark A–D |
| `agent3_paired_failure_abcd_20261104T141803Z` (106–107) | panne appariée A–D |
| `cnp_endurance_multivm_20260918T130822Z` (annexe) | endurance sur deux VM |
| `agent3_saturation_multivm_20261104T142325Z` (112–114) | saturation sur deux VM |
| `hdfs_multivm_cnp_20261104T135345Z` (114) | détection HDFS répartie sur deux VM |
| `agent5_correlation_…` (115) | évaluation de la corrélation |
| `phase_revision_20261104`, `phase_revision_20261105` (131) | paquet de preuves (nom de dossier dans A.2 seulement) |
| E-H3B-STRICT-HOLDOUT (102 et ailleurs) | comparaison modèle spécialisé / modèle commun |
| E-H3B-FAMILY-MODELS (non retenue) | ne citer qu'en limite de validité, avec son défaut |
| E-H4-HDFS-BLOCK-BASELINES | baselines HDFS au niveau bloc |
| E-H5-MEMORY-RELIABILITY | comparaison mémoire et fiabilité |
| E-CNP-STATIC-ASSIGNMENT | Contract Net contre table statique |
| E-CNP-LEAST-LOADED | Contract Net contre répartiteur au moindre chargé |
| E-H3 (non faisable localement) | comparaison du routeur à une chaîne sans routage (non exécutée) |

Fichiers à reprendre : `chapitre5_resultats.tex` (29 run_id, environ 20 mentions « Source(s) : »), `chapitre7_reproductibilite_deploiement.tex` (15 codes), `chapitre1_introduction.tex` (6), `frontmatter/declaration_ia.tex` (6, à coordonner avec F), `chapitre6_discussion.tex` (2), `chapitre6_conclusion.tex` (1). Les mentions « agent2 » à « agent6 » disparaissent avec les run_id : elles ne doivent plus apparaître hors de A.2. Pour A.2 elle-même, F décide si la colonne garde les noms bruts ou un renvoi au registre.

---

## 5. Précision numérique

**Règle proposée.** Corps, résumés et légendes : quatre décimales pour les métriques (F1, précision, rappel, PR-AUC), bornes d'intervalle comprises. Pourcentages : au plus deux décimales (89,81 %, et non 89,8081 %). Débits : entiers, ou deux chiffres significatifs pour les rapports. L'annexe A.2 garde six décimales, ce qui est annoncé une fois en tête de l'annexe (« valeurs brutes des artefacts »). Une valeur arrondie et sa valeur brute ne doivent jamais apparaître côte à côte.

**Écarts à corriger** (texte du PDF, pages arabes) :

| Page | Passage | Correction |
|---|---|---|
| 89 | précision 0,7674, « intervalle exact [0,7491 ; 0,784932] » | [0,7491 ; 0,7849] |
| 89 | F1 HDFS, « [0,8568 ; 0,879493] » | [0,8568 ; 0,8795] |
| 90 | échantillon de 2 000 blocs, « [0,8000 ; 0,961039] » | [0,8000 ; 0,9610] |
| 91 | tableau 4.4, valeur 0,000011 | « < 0,0001 » |
| 94 | protocole G, seuil « 6,977042 » ; F1 « 0,000693 » | 6,9770 ; 0,0007 (ou « < 0,001 ») |
| 123 | `limites_consolidees.tex` l. 19, « [0,8568 ; 0,879493] » | [0,8568 ; 0,8795] |
| xi | bokuse, « [0,8568 ; 0,879493] » | supprimé (règle §3.3) |
| vi, x et corps | « 89,8081 % » (l'échappement `\,\%` est correct) | 89,81 % |

Sources dans les `.tex` : `chapitre5_resultats.tex` l. 188, 192 et 291 (et le paragraphe HDFS) ; `limites_consolidees.tex` l. 19 ; `main.tex` l. 359.

Ailleurs, la cohérence typographique est à vérifier : `$13~\%$` et `11 à 14~\%` (espace insécable ordinaire) contre `$1{,}23\,\%$` (espace fine) dans le résumé, l. 284. Il faut une seule convention, `\,\%`.

---

## 6. Refonte des tableaux 1.4, 1.5 et 7.1

**Tableau 1.4 « Comparaison des principales familles d'approches »** (`chapitre2_etat_art.tex`, l. 979–1018 ; 9 lignes × 4 colonnes en `\scriptsize`).
- Garder trois colonnes : *Approche* | *Limite principale* | *Rôle dans ce mémoire*. La colonne « Atouts » disparaît : elle répète le texte des sections 1.4–1.17.
- Au plus 12 mots par cellule, en `\footnotesize`.
- Fusionner « Méthodes statistiques » et « Règles et signatures » ; fusionner « Corrélation » et « Mémoire et feedback ».
- Résultat : 7 lignes, environ un tiers de page. Le paragraphe qui suit le tableau est ramené à deux phrases.

**Tableau 1.5 « Travaux représentatifs »** (l. 1043–1110 ; 10 lignes × 5 colonnes).
- Supprimer la colonne « Année », qui figure déjà dans la citation, et la colonne « Apport », dont le contenu revient au texte.
- Garder *Travail* | *Objet* | *Différence avec ce mémoire*, sur une ligne ou deux par entrée.
- Retirer les lignes déjà couvertes par 1.3 (Contract Net/FIPA) et par 1.4 (Isolation Forest).
- Résultat : environ 7 lignes, une demi-page. Les lignes de positionnement qui annoncent des résultats relèvent de l'Agent D.

**Tableau 7.1 « Statut des hypothèses »** (`chapitre6_conclusion.tex`, l. 50–95 ; cellules de 80 à 150 mots).
- Le découper en un tableau compact d'une ligne par hypothèse : *Hyp.* | *Nature* (exigence de réalisation / comparative) | *Comparateur exécuté ?* (oui / non / partiel) | *Statut* | *Section de preuve*.
- Il tient en un quart de page, en `\small`, sans `\scriptsize`.
- Le détail par composante va dans la section unique de synthèse (implémenté / testé / supérieur, voir l'intégration), sous forme d'un paragraphe court par hypothèse, sans répéter les chiffres du ch. 4.
- Ce tableau doit être **le même** que le tableau unique QR ↔ hypothèse ↔ mesure ↔ statut de l'Agent A, ou en dériver directement. Il ne faut pas laisser coexister deux tableaux.
- Les statuts en capitales (« NON TRANCHÉE », « PARTIELLEMENT SOUTENUE ») passent en petites capitales ou en casse normale, de façon uniforme dans le texte, les résumés et le bokuse.

---

## 7. Bibliographie (`references.bib`, 57 entrées)

**7.1 DOI non imprimés (priorité 1).** 34 entrées ont un champ `doi`, mais `plain-fr.bst` l'ignore. Deux solutions :
- (a) copier `plain-fr.bst` dans le dossier sous le nom `plain-fr-doi.bst` et ajouter l'affichage du champ `doi` (fonction `format.doi`, appel dans chaque type d'entrée) ;
- (b) passer à `biblatex` avec `style=numeric`, ce qui touche le préambule et la compilation (`biber`).

La solution (a) est la moins risquée. À vérifier après compilation : affichage « doi:10.… » sur les 34 entrées.

**7.2 Entrées sans DOI (23).**

| Entrée | Action |
|---|---|
| `rfc5424` | DOI RFC : 10.17487/RFC5424 (schéma RFC Editor ; à vérifier) |
| `song2024auditllm` | arXiv 2408.08902 → DOI 10.48550/arXiv.2408.08902 (schéma arXiv ; à vérifier) |
| `zhang2025aiops` | Annoncé dans ACM Computing Surveys avec la note arXiv 2507.12472 : DOI ACM **à vérifier** ; à défaut, 10.48550/arXiv.2507.12472 et type `@misc` (prépublication) |
| `kheddar2025transformers` | Information Fusion 2025 : DOI **à vérifier** (Elsevier) |
| `lanvin2023errors` | LNCS, CRiSIS 2022 : DOI Springer **à vérifier** |
| `arp2022dos`, `sculley2015debt` | Pas de DOI (USENIX, NeurIPS) : ajouter l'URL officielle de l'article |
| `axelsson2000intrusion` | Rapport technique Chalmers, sans DOI : URL si disponible, sinon laisser |
| `wooldridge2009introduction` | Livre : ajouter l'ISBN (à vérifier sur l'exemplaire) |
| `fipa2002contractnet`, `fipa2002aclmessage`, `fipa2002cal` | Spécifications FIPA, sans DOI : URL fipa.org (à vérifier) |
| `cic2018csecicids` | Page du jeu de données : garder l'URL |
| 10 `@misc` de documentation (Kafka, Redis, Celery, Temporal, Wazuh, Elastic ×2, OpenSearch, OCSF, Loglizer) | Pas de DOI : voir §7.3 |

Aucun DOI marqué « à vérifier » ne doit entrer dans le `.bib` avant d'avoir été contrôlé sur le site de l'éditeur ou sur doi.org.

**7.3 Documentation web et dates de consultation.**
- Fait : 10 entrées portent « Consultée le 5 novembre 2026 » et une porte « consulté le 4 novembre 2026 » (`cic2018csecicids`).
- Honnêteté : la date doit rester celle d'une consultation réelle ; il ne faut pas antidater. Si l'auteur reconsulte les pages pour la version finale, toutes les dates prennent la date de cette nouvelle consultation.
- Harmoniser la graphie : une seule forme, « consulté le … », au masculin, puisque le sujet sous-entendu est le document ; ou bien au féminin pour « page ». Aujourd'hui, « Consulté » et « Consultée » coexistent (l. 508 contre les autres).
- Présentation : regrouper ces 11 entrées dans une sous-partie « Documentation technique et jeux de données » (par exemple avec `\nocite` et une bibliographie à deux blocs, ou `biblatex` et `keyword`). Ce sont des sources primaires de spécification, citées pour leurs garanties (sémantique de livraison, schémas), et non une littérature scientifique. Le reproche de L2 tombe alors : la bibliographie scientifique compte 46 entrées, dont 34 avec DOI.
- Ajouter, si l'Agent D les retient, les entrées académiques correspondantes : publication de référence de Loglizer (He et al., ISSRE 2016, déjà présente sous `he2016experience`, qu'il suffit de citer conjointement), et OCSF/ECS s'il existe une publication.

**7.4 Sharafaldin.**
- Une seule entrée (`sharafaldin2018cicids`, l. 122) sert à CICIDS2017 et à CSE-CIC-IDS2018 (`chapitre2_etat_art.tex`, l. 321, 343, 1088). C'est conforme à la demande du CIC.
- Correction : ajouter une demi-phrase en 1.8, par exemple « les deux jeux sont décrits par la même publication de référence, que le CIC demande de citer pour chacun ; leurs pages de distribution sont citées séparément ».
- Ne pas dupliquer l'entrée.

**7.5 Jeux de données non cités** (L2 §2.3, §4 : UNSW-NB15, Linux/auth, Solaris BSM, DARPA 1998). Ils relèvent de l'Agent D. Côté forme, chaque jeu reçoit une ligne dans un tableau de présentation des jeux en 1.8 (nom, référence, type de journal, usage dans le mémoire).

---

## 8. Récapitulatif des corrections formelles (liste pour l'intégration)

1. Résumé et abstract remplacés (§3.1–3.2) ; bokuse retraduit selon la règle §3.3 (C19).
2. Run_id et codes E-… retirés du corps et des légendes ; étiquettes du §4 ; identifiants uniquement en A.2.
3. Précision : règle du §5 et 8 corrections ; convention `\,\%`.
4. Tableaux 1.4, 1.5, 7.1 refondus (§6) ; statuts en casse uniforme.
5. Chiffres : une occurrence détaillée par valeur, au ch. 4 ; renvois ailleurs (§1).
6. Ch. 1 : 8 sections ; ch. 2 : 9 sections (§2.4).
7. Annexe A.9 supprimée et légendes enrichies ; A.8 fondue dans le ch. 5 ; ch. 7 réduit à 1,5 p.
8. Bibliographie : DOI imprimés (§7.1), DOI manquants vérifiés (§7.2), bloc « Documentation technique » et dates honnêtes (§7.3), demi-phrase Sharafaldin (§7.4).
9. Contrôle final : `grep` des valeurs du §1 (au plus une occurrence détaillée hors ch. 4), `grep -c "2026[0-9]\{4\}T"` égal à 0 hors `annexes.tex`, compilation complète, sans débordement.

=== PASSATION ===
Agent : E — Forme, redondance et lisibilité
Statut : terminé
Livrable : `revision_reports/refonte_150p/agent_E/LIVRABLE_E.md`
Prochain agent : intégration (après A, B, C, D, F)
Points clés pour l'intégrateur :
- La cible de 150 pages tient avec environ −22,5 p. de forme et −6,5 p. de fond, en comptant environ +4 p. d'ajouts. Les principaux gisements sont le ch. 1 (−8), le ch. 2 (−6), le ch. 4 (−5), les ch. 5–7 (−5) et les liminaires (−4).
- L'annexe A.9 (3,5 p.) est un doublon pur que les lecteurs n'ont pas cité.
- « Aucun DOI » vient du style `plain-fr`, qui n'imprime pas les 34 DOI présents : c'est une correction technique simple.
- Sharafaldin pour deux jeux est conforme à la demande du CIC : expliquer, ne pas dupliquer.
- Le résumé et l'abstract proposés dépendent du titre et de la thèse de l'Agent A ; le tableau 7.1 doit être le tableau unique de l'Agent A.
Vigilance : aucun DOI « à vérifier » ne doit entrer dans le `.bib` sans contrôle ; aucune date de consultation antidatée ; aucun gain obtenu par la mise en page.
=== FIN PASSATION ===
