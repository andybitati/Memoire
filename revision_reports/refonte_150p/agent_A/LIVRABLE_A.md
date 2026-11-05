# LIVRABLE A — Resserrement de l'objet scientifique

Agent A, chantier « Refonte 150 pages », 2026-11-05. Aucun `.tex`, code ou artefact modifié.

Sources lues : `chapitre1_introduction.tex` (problématique, définitions, question centrale, QR, tableau `tab:nature-qr`, hypothèses, objectifs, contributions) ; `chapitre6_conclusion.tex` (bilan, réponses aux QR, tableau `tab:statut-hypotheses` = tableau 7.1 du PDF, conclusion générale) ; `main.tex` (titre, l. 77 et 199–209 ; résumé l. 278) ; `spec_utilite.tex` ; `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md` et protocoles E-H5 et E-CNP-LEAST-LOADED.

Les passages sont repérés par leur texte ; les numéros de ligne indiqués sont ceux du 2026-11-05 et bougeront.

---

## 1. Vérification des reproches du périmètre

| # | Reproche | Verdict | Preuve dans le manuscrit actuel |
|---|---|---|---|
| A-1 | Question centrale descriptive, sans explications concurrentes (L2 §2.1) | **Fondé** | `chapitre1_introduction.tex` l. 95 : « Dans quelle mesure une chaîne […] peut-elle lire […], les orienter […] et y détecter […], et que coûte cette organisation […] ? ». Elle appelle un inventaire, avec une seule comparaison implicite : le coût face au monolithe. |
| A-2 | Problématique dispersée (L1 §A.1) | **Fondé** | Six QR couvrant formats, organisation, routage, tableau de bord, mémoire et protocole (l. 103–117) ; dix objectifs spécifiques (l. 191–213), dont l'interface, la corrélation et la gouvernance. |
| A-3 | H1 et H2 tautologiques (L2 §2.1 ; L1 §A.1) | **Partiellement fondé** | H2 l'est, de l'aveu même du texte (l. 170 : sans magasin d'idempotence, le rejeu « répète cet effet par construction »). H1 n'est pas une tautologie : elle aurait pu échouer sur une unité illisible. C'est une **exigence de réalisation**, que le texte qualifie déjà ainsi (l. 170 ; tableau 7.1, H1 : « relève d'une exigence de réalisation »). Le défaut tient à leur statut d'« hypothèses », que le manuscrit leur conserve et compte dans « aucune des cinq hypothèses n'est validée » (conclusion l. 126). |
| A-4 | H3–H5 non opérationnalisées ; statut « non tranché » garanti d'avance (L2 §2.1 ; L1 §A.3) | **Partiellement fondé** | Fondé pour H3 (taux d'exécutions incompatibles et taux d'erreur de référence non définis, l. 168), pour le budget de H4 et pour la métrique de priorisation des anomalies de H5 (l. 168). **Inexact pour une partie** : la composante « supériorité » de H4 était tranchable et a été infirmée sur les quatre jeux (tableau 7.1, H4) ; la composante mémoire de H5 a été tranchée par un critère fixé avant son exécution (E-H5, registre l. 9 et l. 21 : `gain_conditionnel`). Le statut « non tranchée » de H4 et de H5 n'était donc pas garanti d'avance ; il résulte de la conjonction avec une composante non définie. |
| A-5 | Préenregistrement partiel ; confirmatoire ≠ campagne (L1 §A.3) | **Déjà traité, à resserrer** | l. 168 limite déjà le préenregistrement à six campagnes. Il manque une phrase : ces campagnes ont été conçues après lecture de résultats antérieurs ; elles sont confirmatoires pour leur campagne, non pour le programme. Le traitement détaillé relève de l'Agent C. |
| A-6 | QR et hypothèses ne se correspondent pas ; QR4 sans hypothèse ni mesure (L2 §2.1) | **Fondé** | `tab:nature-qr`, ligne QR4 : « l'utilité pour l'analyste n'est pas mesurée », colonne Hyp. « --- ». La réponse à QR4 (conclusion l. 31–32) ne s'appuie que sur la présence de fonctions. |
| A-7 | Aucune hypothèse validée ; sur quoi repose la contribution ? (L1 §A.2 ; L2 §1, §3.1) | **Fondé** | Conclusion l. 126 : « aucune des cinq hypothèses n'est validée ». La contribution est énumérée (« Apports scientifiques et techniques », l. 93–100) sans être formulée comme réponse à une question. C'est le symptôme principal du défaut A-1. |
| A-8 | Titre surestimé : « hétérogènes » au sens multi-source (L2 §2.1, §4.4) | **Partiellement fondé** | Titre (`main.tex` l. 77, l. 202) : « journaux système et réseau hétérogènes ». L'introduction restreint déjà l'hétérogénéité aux formats et exclut l'analyse conjointe (l. 99) ; le résumé dit « de formats hétérogènes » (l. 278). Le titre seul laisse attendre davantage. |
| A-9 | « Multi-agents intelligents » non tenu (L2 §2.3, §4.4) | **Partiellement fondé** | Le titre ne contient pas « intelligents ». Mais l'introduction qualifie les agents d'« intelligents » (l. 58, l. 66), et `spec_utilite.tex` établit que M = 1 pour toute offre émise, que A et L ont la même expression, que le refus pour faible utilité est inactif par défaut (u_min = 0) et que, dans les campagnes Redis, U = 0,65 + 0,30C + 0,20H + 0,05T. La qualification n'est donc pas tenue au sens ordinaire du mot. |
| A-10 | Conclusion « sait normaliser plusieurs sources » (L2 §2.4, §4.4) | **Fondé** | Conclusion générale l. 126 : « Le prototype sait normaliser plusieurs sources ». Le même chapitre écrit (QR1, l. 23) que le remplissage va de 7/7 champs standard (syslog, BGL) à 0 pour les flux réseau tabulaires. La phrase est aussi contredite par « chaîne d'analyse multi-source » (même paragraphe), alors qu'aucune analyse conjointe n'est faite. |
| A-11 | Seul QR6 reçoit une réponse nette, et elle réplique la littérature (L2 §1, §2.6) | **Fondé, déjà reconnu** | Conclusion l. 38 : « il en constitue une réplication sur ces jeux, non une découverte ». Le reproche porte sur l'absence d'un autre résultat net, ce que la thèse proposée au §2 vise à corriger, sans résultat nouveau, en donnant aux comparaisons architecturales existantes le rôle de réponse. |
| A-12 | Objet défendable : étude expérimentale critique, non démonstration de supériorité (L1 §5, 1re objection ; L1 §D) | **Fondé, à adopter** | Le texte l'énonce de façon dispersée (introduction l. 251 et l. 263 ; conclusion l. 98 et l. 126) ; la question centrale ne le porte pas. |

Hors périmètre, à signaler à l'Agent C : le registre (l. 27) indique que le manifeste d'**E-H3B-STRICT-HOLDOUT** enregistre l'empreinte d'origine de `scripts/run_family_routing_ablation.py`, c'est-à-dire du script fautif. Il faut vérifier si la version stricte réutilise ses fonctions de chargement : le résultat UNSW de la comparaison qui sert de référence pourrait être touché par la fuite de `target`.

---

## 2. Question centrale reformulée en thèse falsifiable

### 2.1 Les deux explications concurrentes

Le prototype présente plusieurs propriétés qu'on attribuerait spontanément à son organisation en agents : reprise sans effet dupliqué, attribution adaptée à la charge et à la fiabilité, spécialisation des traitements, détection. Deux explications s'opposent.

- **E1, explication par l'organisation en agents** : ces propriétés tiennent à l'organisation en agents autonomes et à la négociation Contract Net.
- **E2, explication par les mécanismes simples** : elles tiennent à des mécanismes plus simples que le prototype embarque, et qu'une architecture centralisée peut reproduire. Il s'agit du magasin d'idempotence, de la prise en compte de la charge, d'un compteur de fiabilité lissé et, pour la détection, de règles triviales.

### 2.2 Formulation proposée (remplace `chapitre1_introduction.tex` l. 93–97)

> *Les propriétés qu'une architecture multi-agents légère semble conférer à une chaîne d'analyse de journaux — reprise sans effet dupliqué, attribution adaptée à la charge et à la fiabilité, orientation vers un traitement compatible, détection d'anomalies — tiennent-elles à l'organisation en agents et à la négociation, ou à des mécanismes plus simples que cette architecture embarque et qu'une organisation centralisée peut reproduire ?*

Phrase de cadrage à ajouter juste après :

> *La question est examinée sur un prototype, Ariel Logminer, exécuté en laboratoire sur un ou deux hôtes. Chaque propriété est confrontée à une alternative qui conserve le mécanisme simple et retire l'organisation en agents ou la négociation. Le travail ne cherche pas à établir la supériorité d'une architecture ; il cherche à attribuer chaque effet observé à sa cause.*

### 2.3 Prédictions discriminantes et état des preuves existantes

Chaque ligne indique ce que prédit chaque explication et ce que montrent les résultats déjà présents dans le manuscrit. **Aucune expérience nouvelle n'est supposée.**

| Propriété | E1 prédit | E2 prédit | Résultat existant | Source | Verdict |
|---|---|---|---|---|---|
| Reprise sans doublon | Les architectures sans agents dupliquent même avec idempotence | Le magasin suffit, avec ou sans agents | Doublons : A 10, B 10, C 0, D 0 ; A + idempotence et B + idempotence : 0 | `sec:panne-appariee` ; run `agent3_paired_failure_abcd_20261104T141803Z` | **E2.** La condition « agents sans idempotence » n'a pas été exécutée ; elle n'est pas nécessaire pour départager, puisque les architectures sans agents atteignent 0 doublon avec le magasin. |
| Attribution sous pannes et lenteur | Contract Net fait mieux qu'un répartiteur au moindre chargé | Le moindre chargé fait aussi bien | Contract Net contre moindre chargé : `aucun_avantage` sur s1–s4 ; taux d'échec équivalents, débit de Contract Net inférieur de 11 à 14 % | `sec:e-cnp-moindre` ; registre l. 25 (préenregistré, commit `6db45dd`) | **E2**, dans un seul processus. Le comparateur lit directement l'état des agents, sans coût de communication ni information périmée (L1 §C.1) : le verdict ne vaut pas pour une exécution distribuée. |
| Adaptation à la fiabilité | La mémoire des agents améliore l'attribution | (non tranché par E2 seul) | Gain établi seulement à p = 0,9, avec une équité moindre | `sec:e-h5` ; registre l. 21 (préenregistré, `658e639`) | **Indéterminé.** La mémoire est un compteur de Laplace ; aucune expérience ne l'a greffée sur le répartiteur centralisé. On ne peut donc pas attribuer ce gain conditionnel aux agents plutôt qu'au compteur. |
| Orientation compatible | Le routage par famille réduit les exécutions incompatibles | — | Comparaison avec la chaîne sans routage non exécutée | tableau 7.1, H3 | **Non tranché.** |
| Détection | Les modèles dépassent les règles triviales | Des règles triviales font aussi bien | Sur les quatre jeux publics, une règle simple égale ou dépasse le modèle principal | tableau `tab:baselines-par-jeu` ; conclusion l. 38 | **E2.** Réplication de critiques publiées, déjà déclarée comme telle. |
| Coût | — | — | Sur des micro-tâches, le monolithe traite 55 à 72 fois plus de tâches par seconde | `fig:benchmark-abcd` | Propriété opérationnelle, non discriminante : elle mesure le coût fixe des messages (L2 §2.2 ; voir l'Agent B). |

**Réponse que les résultats permettent déjà** : dans le laboratoire étudié, E2 explique trois des propriétés examinées (reprise, attribution, détection). Deux restent non tranchées (adaptation à la fiabilité, routage). Aucune n'est attribuable à E1. Cette réponse est nette, et ne contient aucune revendication de supériorité. Elle n'est pas une réplication de la littérature prédictive : les comparaisons architecturales (idempotence transposée, moindre chargé) sont propres au travail. Il faut toutefois rattacher le résultat moindre chargé contre Contract Net à la littérature d'équilibrage de charge (voir l'Agent D) : il est attendu par cette littérature et ne doit pas être présenté comme surprenant.

### 2.4 Condition d'honnêteté (obligatoire)

L'opposition E1/E2 est **explicitée après** une partie des résultats : E-CNP-LEAST-LOADED a été décidée après lecture d'E-CNP, et la panne appariée n'est pas préenregistrée. La thèse est donc un **cadre d'analyse**, non une hypothèse confirmatoire fixée avant le programme. Phrase à insérer dans la section des hypothèses :

> *L'opposition entre ces deux explications structure l'analyse ; elle n'a pas été fixée avant l'ensemble des expériences. Seules les comparaisons dont le critère a été versionné avant leur exécution (E-H4, E-H5, E-CNP, E-CNP au moindre chargé, E-H3b stricte) la confrontent à un critère posé à l'avance ; les autres résultats l'illustrent sans la tester.*

Cette phrase ne mentionne aucune version du travail : elle respecte la règle 6 des consignes.

---

## 3. Requalification des hypothèses

### 3.1 H1 et H2 → exigences de réalisation R1 et R2

Retirer H1 et H2 de la liste des hypothèses et les placer dans un court paragraphe « Exigences de réalisation », vérifiées par tests et non comptées parmi les hypothèses.

- **R1, lecture et émission** : chaque unité des formats retenus est lue, émise dans le schéma commun et rattachée à sa source. Vérification : 7 001/7 001 unités lues et émises, dont une fixture Apache d'une ligne ; le remplissage du schéma est rapporté comme propriété mesurée (7/7 pour syslog et BGL, 0/7 pour les flux tabulaires) ; la référence vers la source n'est pas mesurée unité par unité. **Statut : satisfaite pour la lecture et l'émission ; non vérifiée pour la traçabilité unitaire.**
- **R2, reprise sans effet dupliqué** : après un arrêt contrôlé entre persistance et émission, la tâche se termine sans perte ni doublon. Vérification : C et D, dix répétitions ; campagne multi-VM. **Statut : satisfaite.** Ce qui était le contenu scientifique de H2 (l'effet tient-il aux agents ?) passe dans la thèse (§2.3, ligne « Reprise ») : la réponse est E2.

Effet sur le décompte : le mémoire ne dira plus « aucune des cinq hypothèses n'est validée », mais : « deux exigences de réalisation sont satisfaites ; des trois hypothèses comparatives, aucune n'est validée ; une est infirmée pour sa composante de supériorité, deux restent non tranchées ». Ce n'est pas une affirmation plus favorable : c'est le même constat, classé correctement. **Risque** : un lecteur pourrait y voir un habillage. Pour le prévenir, conserver la phrase « aucune hypothèse comparative n'est validée » en tête du statut.

### 3.2 H3–H5 : grandeurs proposées

**Règle d'application, à écrire telle quelle dans le manuscrit :** toute grandeur fixée maintenant est postérieure aux résultats existants. Elle **ne sert pas à trancher** ces résultats ; elle ne vaut que pour une expérience future dont le protocole serait versionné avant exécution. Sans cette expérience, l'hypothèse reste non tranchée. Aucun budget n'est fixé rétroactivement.

| Hyp. | Grandeur manquante | Définition proposée (pour une expérience future préenregistrée) | Effet sur les résultats existants |
|---|---|---|---|
| H3, routage | Taux d'exécutions incompatibles | Part des unités pour lesquelles le traitement appelé échoue (exception de schéma, colonnes requises absentes) ou s'exécute sur moins de 50 % de ses caractéristiques attendues, rapportée au nombre d'unités soumises. Critère : réduction absolue ≥ 10 points face à la même chaîne sans routage, borne inférieure de l'IC bootstrap à 95 % > 0. | Aucun. H3 reste non tranchée. |
| H3, routage | Taux d'erreur de référence | F1 macro par famille de la chaîne sans routage sur le même test ; non-infériorité avec la marge −0,01 déjà employée par E-H3b stricte. | Aucun. |
| H3, spécialisation | (fixée avant exécution) | Non-infériorité spécialisé − commun, marge −0,01 (E-H3B-STRICT-HOLDOUT, préenregistré, `8876861`). | **Peut être utilisée** : le critère précède l'exécution. Résultat : non établie (CICIDS, borne −0,0190). Sous réserve de la vérification signalée au §1 (Agent C). |
| H4, modèles | Budget local de temps et de mémoire | Exemple pour une expérience future : temps d'inférence p95 ≤ 1 ms par unité et mémoire résidente ≤ 2 Go sur l'hôte du laboratoire, entraînement ≤ 10 min. Valeurs à fixer par l'auteur. | Aucun. **Ne pas** l'appliquer aux mesures existantes. Statut proposé : « **non validée ; composante de supériorité infirmée sur les quatre jeux ; composante de budget non définie** ». La supériorité ayant échoué, aucun budget ne pourrait de toute façon valider H4 sur ces tests (coordination avec l'Agent B). |
| H5, mémoire | Métrique de priorisation | Scinder H5. **H5a, mémoire d'attribution** : taux d'échec à la première exécution, avec garde-fou de débit (critère d'E-H5, préenregistré, `658e639`). **H5b, priorisation des anomalies** : précision au rang k (k = 20) d'une file d'anomalies ordonnée avec et sans retour de l'analyste mémorisé, à fixer pour une expérience future. **Gouvernance (promotion)** : retirer de H5 et classer en exigence R3, cycle de promotion et de rejet non exécuté. | H5a **peut être tranchée** avec E-H5 : `gain_conditionnel` (p = 0,9 seulement) → **non établie en général**. H5b : non tranchée. R3 : non vérifiée. |

**Hypothèse sur la négociation** : la comparaison Contract Net / moindre chargé n'a pas d'hypothèse dans l'introduction (elle est dans QR2). La rattacher comme **H-CNP**, en précisant qu'elle est posée au niveau de la campagne : « la négociation réduit les échecs à la première exécution sans perte de débit supérieure à 5 %, face à un répartiteur au moindre chargé ». C'est la règle du protocole E-CNP-LEAST-LOADED, l. 31, versionnée avant exécution. **Statut : réfutée dans un seul processus** (`aucun_avantage`, s1 à s4). L'ajouter est honnête à une condition : la présenter comme hypothèse de campagne, et non comme hypothèse initiale du programme. Question à l'auteur Q2.

---

## 4. Tableau unique QR ↔ hypothèse ↔ mesure ↔ statut ↔ source

Proposition : **cinq QR au lieu de six**. QR4 (tableau de bord) est supprimée comme question de recherche ; la description des fonctions de l'interface reste au chapitre de conception ou d'implémentation, et sa limite (aucune mesure auprès d'analystes) passe dans la section unique des limites. Motif : aucune mesure ni hypothèse, et elle ne relève pas de la thèse. Le rattachement à H5b serait artificiel tant que la priorisation n'est pas mesurée.

Ce tableau remplace à la fois `tab:nature-qr` (introduction) et `tab:statut-hypotheses` (tableau 7.1). L'introduction en donne les quatre premières colonnes ; la conclusion le reprend avec le statut et la source.

| QR | Question | Hyp. / exigence | Mesure | Statut | Source |
|---|---|---|---|---|---|
| QR1 | Quels formats les adaptateurs lisent-ils, et quelle part du schéma commun chaque source remplit-elle ? | R1 (exigence) ; propriété mesurée | Unités lues et émises ; champs standard remplis par source | R1 satisfaite (lecture, émission) ; remplissage de 7/7 à 0/7 ; traçabilité unitaire non mesurée ; aucune analyse conjointe | `fig:couverture-multiformat` ; run `agent5_multiformat_20261104T150111Z` |
| QR2 | Quel coût l'organisation en agents ajoute-t-elle, et l'exécution sur deux machines augmente-t-elle la capacité ? | Propriétés opérationnelles | Débit A–D sur micro-tâches ; part de la seconde VM en saturation | Coût mesuré (monolithe 55 à 72 fois plus rapide sur micro-tâches) ; la seconde VM traite 1,23 % des tâches réussies, sans gain de capacité observé | `fig:benchmark-abcd` ; `sec:cnp-multivm` ; `agent3_saturation_multivm_20261104T142325Z` |
| QR3 (thèse) | Reprise et attribution tiennent-elles aux agents et à la négociation, ou à l'idempotence et à la prise en compte de la charge ? | R2 ; H-CNP ; H5a | Doublons après panne A–D ± idempotence ; Contract Net contre table et contre moindre chargé ; mémoire activée ou non sous fiabilité hétérogène | R2 satisfaite, effet dû au magasin ; H-CNP réfutée dans un seul processus ; H5a non établie en général (gain à p = 0,9 seulement) | `sec:panne-appariee` ; `sec:e-cnp` ; `sec:e-cnp-moindre` ; `sec:e-h5` |
| QR4 (ancienne QR3) | Le routeur oriente-t-il chaque source vers un traitement compatible, et la spécialisation vaut-elle un modèle commun ? | H3 (routage, spécialisation) | Rejet et faux rejet open-set ; non-infériorité spécialisé − commun | Routage : non tranchée (comparateur non exécuté) ; rejet 20/20 inconnus, faux rejet 3/46. Spécialisation : non-infériorité non établie (CICIDS) | `fig:routeur-open-set` ; `sec:e-h3b` |
| QR5 (ancienne QR6) | Les scores de détection sur des jeux publics dépendent-ils du protocole et de l'unité d'analyse, et dépassent-ils des règles triviales ? | H4 | F1 sur test tenu à l'écart contre la meilleure règle simple sur le même test | Non validée : supériorité infirmée sur les quatre jeux ; budget non défini | `tab:baselines-par-jeu` ; `sec:cicids-resultats` ; `tab:hdfs-block-baselines` ; `sec:bgl-resultats` ; `sec:csecic-raccourci` |
| — | Exigence de gouvernance des modèles | R3 (exigence) | Promotion conforme à la règle | Non vérifiée : implémentation et dry-run, aucun cycle complet | `tab:statut-model-update` |
| — | Priorisation des anomalies | H5b | Précision au rang k (à définir) | Non tranchée : non mesurée | — |

Les valeurs citées sont celles du manuscrit actuel (tableau 7.1, conclusion, `ETAT_CHANTIER.md` §3 du HANDOFF) ; aucun chiffre nouveau.

---

## 5. Titre et conclusion recadrés

### 5.1 Propositions de titre

1. **« Ariel Logminer : conception et évaluation critique, en laboratoire, d'une architecture multi-agents légère pour l'analyse de journaux système et réseau »** — retire « hétérogènes », annonce l'évaluation critique, conserve l'objet. **Recommandé** : changement minimal, fidèle à L1 §D (« le titre reste acceptable puisqu'il annonce une conception et une évaluation ») et répond à L2 §4.4.
2. « Agents ou mécanismes simples ? Évaluation critique d'une architecture multi-agents légère pour l'analyse de journaux — le cas d'Ariel Logminer » — porte la thèse dans le titre. Plus fort, mais la forme interrogative peut sembler journalistique pour un TFE.
3. « Architecture multi-agents légère pour l'analyse de journaux de formats multiples : conception et évaluation en laboratoire d'Ariel Logminer » — garde la structure actuelle, remplace « hétérogènes » par « de formats multiples ». Plus prudent, moins informatif.

Le titre a été arrêté par l'auteur (décision D1 du HANDOFF). Tout changement exige son accord, et le verdict de l'Agent 8 recommande l'avis des co-directeurs. À propager : `main.tex` l. 77 (`pdftitle`), page de titre (l. 199–209), éventuellement le résumé (l. 278).

### 5.2 Corrections ponctuelles

| Passage actuel | Fichier | Correction proposée |
|---|---|---|
| « Ariel Logminer montre qu'une chaîne d'analyse multi-source peut être organisée autour d'agents capables de poursuivre des objectifs bornés et de prendre des décisions locales » | `chapitre6_conclusion.tex`, conclusion générale | « Ariel Logminer montre qu'une chaîne d'analyse de journaux de formats multiples peut être organisée en agents qui poursuivent des objectifs bornés, et que chaque effet de cette organisation peut être confronté à un mécanisme plus simple. » |
| « Le prototype sait normaliser plusieurs sources, les router, […] » | idem | « Le prototype lit et émet dans un schéma commun les unités de huit sources, qu'il remplit inégalement — entièrement pour syslog et BGL, pas du tout pour les flux réseau tabulaires —, oriente les sources connues et rejette les inconnues du corpus, attribue, délègue et reprend des tâches, et conserve les traces nécessaires à leur audit. » |
| « aucune des cinq hypothèses n'est validée, et les expériences désignent, pour plusieurs mécanismes, une alternative plus simple qui fait aussi bien ou mieux » | idem | « Aucune hypothèse comparative n'est validée. Pour la reprise, l'attribution des tâches et la détection, les expériences attribuent l'effet observé à un mécanisme plus simple — magasin d'idempotence, prise en compte de la charge, règle triviale — que l'organisation en agents ne fait qu'embarquer. Le routage et l'adaptation à la fiabilité restent non tranchés. » |
| « intelligent » comme qualificatif des agents | `chapitre1_introduction.tex` l. 58 et l. 66 ; `chapitre3_modele_propose.tex` ; `chapitre4_implementation.tex` ; `main.tex` (3 occurrences, à vérifier une à une) | Remplacer la définition l. 66 par : « Les agents ne sont pas qualifiés d'intelligents au sens ordinaire : leur décision d'offre repose sur une utilité à poids fixes, dont deux composantes sont constantes ou redondantes dans les campagnes (section~\ref{sec:spec-utilite}). On parlera d'agents à **politique de décision locale**. » Conserver le nom de classe `MultiTaskIntelligentAgent`, qui est un identifiant de code, en le signalant comme tel. |
| « hétérogènes » sans qualification | 35 occurrences environ dans `main.tex` et les chapitres (décompte par grep) | Garder « de formats hétérogènes » ou « hétérogénéité des formats » ; retirer ou qualifier les emplois qui suggèrent un bénéfice multi-source. Le travail ligne à ligne relève de l'Agent E. |
| Bilan, l. 8 : « organisation d'une chaîne traçable qui associe poursuite bornée d'objectifs, normalisation, routage open-set, […] » | `chapitre6_conclusion.tex` | Faire suivre la phrase de : « Sa contribution est une étude expérimentale critique : elle attribue chaque effet observé à sa cause, sans nouveauté algorithmique. » (coordination avec l'Agent D sur la formulation de la contribution). |

---

## 6. Effet estimé sur le volume

Estimations en pages du PDF, à partir de la densité observée dans l'introduction (p. 1–15) et la conclusion (p. 135–141).

| Proposition | Effet |
|---|---|
| Nouvelle question centrale et cadrage (§2.2, §2.4) | +0,3 p. |
| Hypothèses : H1/H2 → R1/R2, suppression des paragraphes explicatifs l. 170–180, ajout de H-CNP et de la règle sur les grandeurs | −0,7 p. |
| Tableau unique : fusion de `tab:nature-qr` et du tableau 7.1, dont les cellules longues migrent vers les sections de résultats déjà citées | −1,0 p. |
| Réponses aux QR de la conclusion (≈ 2 p.) réduites à un paragraphe par QR, renvoyant au tableau | −1,0 p. |
| Suppression de QR4 (question et réponse) | −0,3 p. |
| Objectifs spécifiques ramenés de dix à cinq, alignés sur les QR | −0,5 p. |
| « Contributions du travail » de l'introduction resserrée autour de la thèse | −0,4 p. |
| Titre, corrections ponctuelles de la conclusion | 0 |
| **Total** | **≈ −3,6 p.** |

**Risque principal** : le reclassement de H1/H2 et la scission de H5 pourraient être lus comme un remaniement des hypothèses après les résultats (L1 §5). Parade : conserver dans le texte l'énoncé initial des critères, dire explicitement que le reclassement ne change aucun statut, et n'utiliser que des critères versionnés avant leur exécution (E-H5, E-CNP-LL, E-H3B strict, E-H4).

---

=== PASSATION ===
Agent : A — Resserrement de l'objet scientifique
Statut : terminé
Livrable : `revision_reports/refonte_150p/agent_A/LIVRABLE_A.md`
Points ouverts :
- Agent C : vérifier si E-H3B-STRICT-HOLDOUT réutilise les fonctions de chargement fautives (l'empreinte d'origine figure dans son manifeste, registre l. 27). Le statut de H3 (spécialisation) en dépend.
- Agent D : rattacher le résultat moindre chargé contre Contract Net à la littérature d'équilibrage (JSQ, power of two choices), pour que la thèse E1/E2 ne le présente pas comme inattendu.
- Agent B : statut de H4 et absence de budget rétroactif (aligné ici) ; benchmark A–D, non discriminant pour la thèse.
- Agent E : passe sur les quelque 35 occurrences de « hétérogène » et sur les occurrences de « intelligent ».
- Intégration : le tableau unique du §4 remplace `tab:nature-qr` et `tab:statut-hypotheses` ; les numéros de QR changent (QR6 → QR5, QR3 → QR4) et tous les renvois sont à mettre à jour.
Questions à l'auteur :
- Q1 : quel titre adopter (§5.1) ? La proposition 1 est recommandée ; elle revient sur la décision D1 et mérite l'avis des co-directeurs.
- Q2 : accepter d'ajouter H-CNP comme hypothèse de campagne (§3.2), et de reclasser H1/H2 en exigences R1/R2 ?
- Q3 : supprimer QR4 comme question de recherche, ou la conserver comme exigence de réalisation (R4) sans statut d'hypothèse ?
- Q4 : accepter la phrase du §2.4 qui déclare que l'opposition E1/E2 a été explicitée après une partie des résultats ? Elle est nécessaire à l'honnêteté du cadrage.
=== FIN PASSATION ===
