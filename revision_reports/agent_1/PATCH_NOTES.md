# PATCH NOTES — Agent 1, cohérence et forme

**Effort estimé d'intégration :** 4 à 6 heures, dont une passe de cohérence trilingue, la régénération éventuelle de la figure CICIDS et trois compilations LaTeX.

**Blocages et réserves :**

1. L'ancien agrégat CICIDS donnant 0,157827 ne possède pas de `run_id`. Il doit être qualifié d'artefact antérieur et ne plus porter le résultat principal.
2. La reformulation lingala proposée doit être relue par un locuteur compétent avant dépôt définitif.
3. Les critères falsifiables de H2, H3 et H5 exigent encore des comparaisons absentes : panne A/B contre C/D, routage contre absence de routage, mémoire activée contre désactivée et cycle complet de promotion/rejet. Les statuts proposés sont donc volontairement prudents.
4. La figure CICIDS associée à l'ancien tableau à cinq observations doit être vérifiée et, si nécessaire, régénérée à partir des 125 runs de phase 2.

## Registre minimal des preuves numériques

| Élément | `run_id` | Source CSV/JSON |
|---|---|---|
| Endurance multi-VM | `cnp_endurance_multivm_20260918T130822Z` | `experiments/phase_cnp_endurance/aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json` |
| Run multi-VM court | `multivm_cnp_20260909T202632Z_37592` | `experiments/phase_multi_agent/raw/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.json` |
| CICIDS RF, agrégat complet | `e1_holdout_<scenario>_seed<42..46>` | `data/processed/final_experiments_2026/cicids_holdout_multiseed_raw.csv` |
| CICIDS, cinq candidats | `e2_models_<scenario>_seed<42..46>_<model>` | `data/processed/final_experiments_2026/cicids_model_multiseed_raw.csv` |
| Multiformat | `multiformat_balanced_20260910T094422Z` | `experiments/phase_dataset_strengthening/aggregated/multiformat_balanced_summary.csv` |
| Routeur open-set | `final_router_open_set_20260911T000746Z` | `experiments/phase_final_scientific_consolidation/aggregated/router_open_set_summary.json` |
| BGL | `ds_bgl_known_unknown_20260910T082706Z` | `experiments/phase_dataset_strengthening/raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv` |

## 1. Titre ajusté à la portée démontrée

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** métadonnées PDF et page de garde

**Texte actuel exact :**

```latex
pdftitle={Détection autonome et distribuée d’anomalies dans les journaux système et réseau à l’aide d’agents intelligents multitâches — Conception et évaluation locale du prototype Ariel Logminer},
```

et :

```latex
Détection autonome et distribuée d’anomalies
dans les journaux système et réseau
à l’aide d’agents intelligents multitâches
...
— Conception et évaluation locale du prototype
Ariel \logminer
```

**Texte proposé :**

```latex
pdftitle={Architecture multi-agents légère pour l’analyse de journaux système et réseau hétérogènes — Conception et évaluation en laboratoire d’Ariel Logminer},
```

et :

```latex
Architecture multi-agents légère pour l’analyse
de journaux système et réseau hétérogènes
\par}

\vspace{0.4cm}

{\Large
— Conception et évaluation en laboratoire
d’Ariel \logminer
```

**Justification :** la détection n'est pas évaluée sur des données étiquetées distribuées entre les deux VM. Le titre proposé décrit exactement la contribution architecturale et le périmètre de laboratoire.

## 2. Résumé français : campagne multi-VM principale

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** Résumé

**Texte actuel exact :**

```latex
La campagne multi-VM (\texttt{multivm\_cnp\_20260909T202632Z\_37592})
exécute 60/60 tâches sur Debian et Ubuntu, réparties 30/30, avec Redis
centralisé sur l'hôte de laboratoire. Elle comprend 15 refus, un échec
contrôlé, une réattribution réussie et un replay idempotent sans effet
dupliqué. La campagne valide ces mécanismes dans la topologie de laboratoire
étudiée. La haute disponibilité industrielle n'a pas été évaluée.
```

**Texte proposé :**

```latex
La campagne d'endurance multi-VM
(\texttt{cnp\_endurance\_multivm\_20260918T130822Z}) exécute avec succès
$1\,800/1\,800$ tâches sur Debian et Ubuntu, dont 451 sont attribuées à
Debian et $1\,349$ à Ubuntu. Le scénario de panne contrôlée produit une
réattribution réussie et un rejeu idempotent : un seul effet persistant est
observé, sans effet dupliqué. Cette campagne valide l'endurance du protocole,
la reprise et l'idempotence dans la topologie de laboratoire étudiée ; elle
n'établit pas une haute disponibilité industrielle.
```

**Preuve :** `run_id=cnp_endurance_multivm_20260918T130822Z`, JSON indiqué dans le registre.

## 3. Abstract anglais : campagne multi-VM principale

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** Abstract

**Texte actuel exact :**

```latex
The multi-VM campaign (\texttt{multivm\_cnp\_20260909T202632Z\_37592})
executes 60/60 tasks on Debian and Ubuntu, split 30/30, with Redis
centralized on the laboratory host. It includes 15 refusals, one
controlled failure, one successful reassignment, and an idempotent replay
with no duplicated effect. The campaign validates these mechanisms in the
laboratory topology; industrial high availability was not evaluated.
```

**Texte proposé :**

```latex
The multi-VM endurance campaign
(\texttt{cnp\_endurance\_multivm\_20260918T130822Z}) successfully completes
$1,800/1,800$ tasks on Debian and Ubuntu, with 451 tasks assigned to Debian
and $1,349$ to Ubuntu. The controlled-failure scenario yields a successful
reassignment and an idempotent replay: one persistent effect is observed,
with no duplicated effect. This campaign validates protocol endurance,
recovery, and idempotence in the studied laboratory topology; it does not
establish industrial high availability.
```

**Preuve :** même JSON d'endurance.

## 4. Résumé lingala : campagne multi-VM principale

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** Bokuse

**Texte actuel exact :**

```latex
Campagne multi-VM
(\texttt{multivm\_cnp\_20260909T202632Z\_37592}) esali 60/60 tâches na
Debian mpe Ubuntu, oyo ekabolami 30/30, na Redis centralisé na hôte ya
laboratoire. Ezali na 15 refus, échec contrôlé moko, réattribution moko
oyo elongaki mpe replay idempotent kozanga effet dupliqué. Campagne yango
endimisi fonctionnement ya mécanismes oyo na topologie ya laboratoire
oyo eyekolamaki. Haute disponibilité industrielle emekamaki te.
```

**Texte proposé :**

```latex
Campagne d'endurance multi-VM
(\texttt{cnp\_endurance\_multivm\_20260918T130822Z}) esilisi na elonga
$1\,800/1\,800$ tâches na Debian mpe Ubuntu : Debian ezwi 451 mpe Ubuntu
$1\,349$. Na scénario ya panne contrôlée, tâche epesami lisusu na agent
mosusu mpe replay idempotent esalemi : effet persistant moko kaka emonani,
kasi effet dupliqué moko te. Campagne oyo endimisi endurance ya protocole,
reprise mpe idempotence na topologie ya laboratoire oyo eyekolamaki ;
endimisi te haute disponibilité industrielle.
```

**Preuve :** même JSON d'endurance. **Réserve :** relecture linguistique requise.

## 5. Annexe A.2 : conserver la trace du run court existant

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/annexes.tex`  
**Section :** Matrice résultats--preuves

**Texte actuel exact :** aucune ligne ne décrit le run court ; seule la ligne suivante existe :

```latex
Endurance CNP multi-VM & $1\,800/1\,800$ ; 1 h & \texttt{cnp\_endurance\_multivm\_20260918T130822Z\_\_summary.json} \\
```

**Texte proposé :** conserver cette ligne et ajouter immédiatement avant elle :

```latex
CNP multi-VM fonctionnel & 60/60 ; Debian 30, Ubuntu 30 ; 15 refus &
\texttt{experiments/phase\_multi\_agent/raw/multivm\_cnp\_20260909T202632Z\_37592\_\_redis\_cnp\_multivm.json} \\
```

**Preuve :** `run_id=multivm_cnp_20260909T202632Z_37592`, JSON indiqué dans le registre.

## 6. Terminologie CICIDS et explication de l'écart d'agrégation

### 6.1 Résumé français

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** Résumé, CICIDS2017

**Texte actuel exact :**

```latex
Lorsque cinq scénarios sont successivement tenus hors
entraînement, le F1 macro tombe à
...
La comparaison de cinq modèles légers montre
que Logistic Regression obtient le meilleur F1 macro, soit
$0{,}233670$, alors que HistGradientBoosting obtient une PR-AUC macro de
$0{,}567697$.
```

**Texte proposé :**

```latex
Lorsque cinq scénarios sont successivement tenus hors entraînement, le F1
binaire moyen, calculé sur cinq scénarios et cinq graines, tombe à
...
La comparaison de cinq modèles légers sur les mêmes 25 couples
scénario--graine montre que Logistic Regression obtient le meilleur F1 moyen,
soit $0{,}233670$, tandis que HistGradientBoosting obtient une PR-AUC moyenne
de $0{,}567697$.
```

**Preuves :** runs `e1_holdout_<scenario>_seed<42..46>` et `e2_models_<scenario>_seed<42..46>_<model>`, CSV bruts du registre.

### 6.2 Abstract anglais

**Texte actuel exact :**

```latex
When five scenarios are successively held out from
training, the macro F1-score falls to
...
models shows that Logistic Regression achieves the highest macro
F1-score, $0.233670$, while HistGradientBoosting reaches a macro PR-AUC
of $0.567697$.
```

**Texte proposé :**

```latex
When five scenarios are successively held out from training, the mean binary
F1-score over five scenarios and five seeds falls to
...
Across the same 25 scenario--seed pairs, Logistic Regression achieves the
highest mean F1-score, $0.233670$, while HistGradientBoosting reaches a mean
PR-AUC of $0.567697$.
```

### 6.3 Résumé lingala

**Texte actuel exact :**

```latex
Tango ba scénarios mitano elongolami moko na
moko na entraînement, F1 macro ekiti kino
...
ete Logistic Regression ezwi F1 macro ya malamu koleka, oyo ezali
$0{,}233670$, nzokande HistGradientBoosting ezwi PR-AUC macro ya
$0{,}567697$.
```

**Texte proposé :**

```latex
Tango ba scénarios mitano elongolami moko na moko na entraînement, moyenne ya
F1 binaire na ba scénarios mitano mpe ba graines mitano ekiti kino
...
Na ba couples 25 ya scénario mpe graine yango moko, Logistic Regression ezwi
F1 moyen ya malamu koleka, $0{,}233670$, nzokande HistGradientBoosting ezwi
PR-AUC moyen ya $0{,}567697$.
```

### 6.4 Chapitre des résultats : remplacer l'agrégat ancien

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre5_resultats.tex`  
**Section :** CICIDS2017 — Comparaison de cinq candidats

**Texte actuel exact :**

```latex
Une expérience distincte compare \texttt{LogisticRegression}, \texttt{RandomForest}, \texttt{SGDLogistic}, \texttt{ExtraTrees} et \texttt{HistGradientBoosting} dans un espace commun. La partition est un holdout fichier ou scénario, les graines sont 42 à 46 et le nombre moyen de lignes de test est $6\,435{,}6$. Les transformations, tailles et graines sont appariées afin que le modèle soit la principale différence.
```

et le tableau actuel contient notamment :

```latex
LogisticRegression & 0,233670 & 0,189932 & 0,312455 \\
RandomForest & 0,157827 & 0,128650 & 0,347377 \\
SGDLogistic & 0,143598 & 0,112100 & 0,319155 \\
ExtraTrees & 0,143265 & 0,110900 & 0,317571 \\
HistGradientBoosting & 0,003568 & 0,001800 & 0,007978 \\
```

**Texte proposé :**

```latex
Une expérience distincte compare \texttt{LogisticRegression},
\texttt{RandomForest}, \texttt{SGDLogistic}, \texttt{ExtraTrees} et
\texttt{HistGradientBoosting} dans un espace commun de 78 caractéristiques.
Pour chaque candidat, cinq scénarios sont évalués avec les graines 42 à 46,
soit 25 résultats par modèle. Les transformations, les tailles et les graines
sont appariées afin que le modèle soit la principale différence. Un ancien
tableau, calculé sur cinq couples scénario--graine seulement, donnait
$0{,}157827$ pour le Random Forest ; l'agrégat complet des 25 runs donne
$0{,}157744$. Cet écart provient du nombre d'observations agrégées, et non
d'un espace de caractéristiques différent.
```

Remplacer le contenu numérique du tableau par :

```latex
LogisticRegression & 0,233670 & 0,189932 & 0,285231 \\
RandomForest & 0,157744 & 0,128540 & 0,316943 \\
SGDLogistic & 0,165406 & 0,129440 & 0,293837 \\
ExtraTrees & 0,143191 & 0,110260 & 0,287744 \\
HistGradientBoosting & 0,003362 & 0,001700 & 0,008175 \\
```

Remplacer également la source de la légende :

```latex
Source : \texttt{data/processed/final\_experiments\_2026/cicids\_model\_multiseed\_summary.csv}.
```

**Preuve :** les 125 lignes de `data/processed/final_experiments_2026/cicids_model_multiseed_raw.csv`, chacune avec son `run_id`.  
**Réserve de traçabilité :** l'ancien CSV donnant 0,157827 ne contient pas de `run_id` ; ce manque doit être signalé si la valeur antérieure est mentionnée.

### 6.5 Annexe

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/annexes.tex`  
**Section :** Matrice résultats--preuves

**Texte actuel exact :**

```latex
CICIDS scénario RF & F1 macro 0,157744 & Même synthèse, protocole holdout scénario. \\
```

**Texte proposé :**

```latex
CICIDS scénario RF & F1 moyen 0,157744 sur 25 runs & Même synthèse, protocole holdout scénario. \\
```

## 7. Phrase française signalée comme cassée

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** Résumé, BGL

**Texte actuel exact :**

```latex
Sur BGL, le F1 vaut $0{,}913698$,
mais 89,8081\,% des templates de test sont inconnus du train et la
baseline « template inconnu » n'atteint que $0{,}277885$.
```

**Texte proposé :** aucun changement. La phrase est grammaticalement complète dans l'état audité.  
**Preuve :** `run_id=ds_bgl_known_unknown_20260910T082706Z`, CSV du registre.

## 8. Décompte explicite : cinq hypothèses et six questions

### 8.1 Résumé français

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`  
**Section :** fin du Résumé

**Texte actuel exact :**

```latex
Les cinq hypothèses de recherche sont partiellement
soutenues. Les trois premières questions reçoivent des réponses
partielles renforcées, les quatrième et cinquième des réponses partielles,
et la sixième une réponse forte dans le périmètre du laboratoire.
```

**Texte proposé :**

```latex
Le travail confronte cinq hypothèses à six questions de recherche.
L'évaluation apporte des éléments de réponse à chacune d'elles, sans permettre
une validation générale au-delà du périmètre de laboratoire ; le statut
détaillé des hypothèses est présenté dans le tableau de conclusion.
```

### 8.2 Abstract anglais

**Texte actuel exact :**

```latex
All five research hypotheses are partially supported. The
first three research questions receive strengthened partial answers, the
fourth and fifth receive partial answers, and the sixth receives a strong
answer within the laboratory scope.
```

**Texte proposé :**

```latex
The study examines five hypotheses through six research questions. The
evaluation provides evidence relevant to each of them, without supporting
general validation beyond the laboratory scope; the conclusion reports the
detailed status of every hypothesis.
```

### 8.3 Résumé lingala

**Texte actuel exact :**

```latex
Ba hypothèses mitano ya recherche esimbami kaka na ndambo. Ba questions
misato ya liboso ezwi biyano partielles oyo esimbami makasi koleka,
question ya minei mpe ya mitano ezwi biyano partielles, mpe question ya
motoba ezwi eyano makasi na kati ya périmètre ya laboratoire.
```

**Texte proposé :**

```latex
Mosala oyo etali ba hypothèses mitano na nzela ya ba questions motoba ya
recherche. Évaluation epesi ba éléments ya eyano mpo na moko na moko, kasi
endimisi te généralisation na libanda ya périmètre ya laboratoire ; tableau
ya conclusion emonisi statut ya hypothèse mokomoko.
```

## 9. Reformulation falsifiable de H1 à H5

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre1_introduction.tex`  
**Section :** Hypothèses de recherche

**Texte actuel exact :**

```latex
\item[\textbf{H1.}]
Des journaux hétérogènes peuvent être rapprochés par un noyau commun sans supprimer les informations originales utiles à l'audit.

\item[\textbf{H2.}]
Des agents spécialisés peuvent améliorer modularité, traçabilité et robustesse par rapport à une chaîne monolithique.

\item[\textbf{H3.}]
Le routage par famille peut limiter les incompatibilités entre données, features et modèles.

\item[\textbf{H4.}]
Des modèles légers conservent un intérêt dans une chaîne locale reproductible avec métriques, corrélation et validation humaine.

\item[\textbf{H5.}]
Une mémoire persistante peut soutenir l'adaptation progressive, la priorisation et la mise à jour contrôlée.
```

**Texte proposé :**

```latex
\item[\textbf{H1.}]
Pour chaque unité des formats retenus, la normalisation produit un événement
conforme au noyau commun et conserve une référence vérifiable vers la donnée
source ; l'hypothèse est réfutée si une unité présente ne peut être lue,
normalisée ou retracée.

\item[\textbf{H2.}]
Lors d'un arrêt contrôlé d'un worker après persistance et avant émission du
résultat, les architectures à agents avec reprise terminent la tâche sans
perte ni effet dupliqué et obtiennent un résultat strictement meilleur qu'au
moins une architecture de référence A ou B sur la perte, les doublons ou le
temps de reprise ; l'hypothèse est réfutée si cette condition n'est pas
observée.

\item[\textbf{H3.}]
Sur un corpus étiqueté comprenant des familles connues et inconnues, le
routage par famille réduit le taux d'exécutions incompatibles par rapport à
la même chaîne sans routage, sans accroître le taux d'erreur prédictive fixé
par le protocole ; l'hypothèse est réfutée en l'absence de réduction mesurée.

\item[\textbf{H4.}]
Sous une séparation stricte fixée avant l'expérience, au moins un modèle léger
surpasse la baseline déclarée en F1 sur le test tenu à l'écart et reproduit ce
résultat dans le budget local de temps et de mémoire fixé par le protocole ;
l'hypothèse est réfutée si aucun candidat ne satisfait conjointement ces
critères.

\item[\textbf{H5.}]
À protocole et tâches identiques, l'activation de la mémoire persistante
améliore au moins une métrique de priorisation fixée à l'avance sans dégrader
les autres métriques principales, et la procédure de mise à jour ne remplace
le modèle actif que lorsqu'un candidat satisfait la règle de promotion ;
l'hypothèse est réfutée si aucun gain n'est observé ou si une promotion
contraire à la règle se produit.
```

**Note méthodologique à ajouter après la liste :**

```latex
Ces hypothèses définissent désormais une observation susceptible de les
réfuter. Les seuils numériques et budgets doivent être fixés dans le protocole
avant l'exécution, et non choisis après lecture des résultats. Une hypothèse
reste non tranchée lorsque le comparateur requis n'a pas été exécuté.
```

## 10. Tableau 7.1 : critères et statuts cohérents

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre6_conclusion.tex`  
**Section :** Statut des hypothèses

**Texte actuel exact :**

```latex
\begin{tabularx}{\textwidth}{p{0.12\textwidth} p{0.27\textwidth} X}
...
\textbf{Hyp.} & \textbf{Statut} & \textbf{Justification} \\
...
H1 &
PARTIELLEMENT SOUTENUE &
$7\,001/7\,001$ unités présentes traitées ; couverture universelle non testée. \\
H2 &
PARTIELLEMENT SOUTENUE &
Modularité, traçabilité, refus et reprise observés ; comparée à une exécution monolithique (section~6.4), l'architecture par agents n'apporte pas de gain de performance systématique. \\
H3 &
PARTIELLEMENT SOUTENUE &
Routage compatible, rejet 3/3 et faux rejet 0/28 dans un jeu indépendant limité ; sur le plan prédictif, le gain apporté par le routage n'est pas systématique (cf.\ QR3). \\
H4 &
PARTIELLEMENT SOUTENUE &
Modèles légers intégrés et évalués ; performances dépendantes des splits et des sources. \\
H5 &
PARTIELLEMENT SOUTENUE &
Influence décisionnelle observée ; bénéfice et mise à jour contrôlée non évalués. \\
```

**Texte proposé :** remplacer le tableau par une version à quatre colonnes :

```latex
\begin{tabularx}{\textwidth}{p{0.07\textwidth} p{0.23\textwidth} p{0.20\textwidth} X}
\toprule
\textbf{Hyp.} & \textbf{Critère de décision} & \textbf{Statut} & \textbf{Éléments observés} \\
\midrule
H1 & Normalisation et traçabilité de chaque unité retenue. &
PARTIELLEMENT SOUTENUE &
$7\,001/7\,001$ unités présentes sont lues et normalisées ; la conservation
champ par champ et la couverture universelle ne sont pas établies. \\
H2 & Reprise sans perte ni doublon, comparée à A/B. &
NON TRANCHÉE &
La panne CNP contrôlée aboutit à un effet persistant et aucun effet dupliqué,
mais la même panne n'est pas mesurée sur A et B. \\
H3 & Réduction des exécutions incompatibles contre une chaîne sans routage. &
NON TRANCHÉE &
Le test open-set rejette 3/3 inconnus sans faux rejet parmi 28 connus, mais le
comparateur sans routage manque et le corpus inconnu est trop restreint. \\
H4 & Gain contre baseline sous split strict et budget local prédéfini. &
PARTIELLEMENT SOUTENUE &
Des modèles légers et des baselines sont évalués ; les gains dépendent du jeu,
du split et du seuil, et le budget local n'est pas un critère de décision
préenregistré. \\
H5 & Gain mémoire activée/désactivée et promotion conforme à la règle. &
NON TRANCHÉE &
La mémoire influence des décisions et le mode dry-run existe, mais aucun gain
quantitatif ni cycle complet répété de promotion et de rejet n'est démontré. \\
\bottomrule
\end{tabularx}
```

**Preuves numériques :**

- H1 : `run_id=multiformat_balanced_20260910T094422Z`, CSV du registre ;
- H2 : `run_id=cnp_endurance_multivm_20260918T130822Z`, JSON du registre ;
- H3 : `run_id=final_router_open_set_20260911T000746Z`, JSON du registre.

Les absences de comparateurs pour H2, H3 et H5 sont des manques expérimentaux, non des valeurs à extrapoler.

## 11. Numérotation 7.11 à 7.17 de la conclusion

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre6_conclusion.tex`  
**Section :** ensemble de la conclusion générale

**Texte actuel exact :**

```latex
\section{Bilan}
\section{Réponse aux questions de recherche}
\section{Statut des hypothèses}
\section{Apports scientifiques et techniques}
\section{Limites}
\section{Perspectives}
\section{Conclusion générale}
```

**Texte proposé :**

```latex
\section*{Bilan}
\addcontentsline{toc}{section}{Bilan}
\section*{Réponse aux questions de recherche}
\addcontentsline{toc}{section}{Réponse aux questions de recherche}
\section*{Statut des hypothèses}
\addcontentsline{toc}{section}{Statut des hypothèses}
\section*{Apports scientifiques et techniques}
\addcontentsline{toc}{section}{Apports scientifiques et techniques}
\section*{Limites}
\addcontentsline{toc}{section}{Limites}
\section*{Perspectives}
\addcontentsline{toc}{section}{Perspectives}
\section*{Conclusion générale}
\addcontentsline{toc}{section}{Conclusion générale}
```

**Justification :** `\chapter*{Conclusion générale et perspectives}` ne remet pas le compteur de chapitre à zéro ; les `\section` actuelles héritent donc du chapitre 7. Les sections étoilées harmonisent la conclusion avec l'introduction générale non numérotée.

## Ordre d'intégration conseillé

1. Mettre à jour le tableau CICIDS et sa source au chapitre des résultats.
2. Reformuler H1–H5 et mettre à jour leur tableau de statut.
3. Corriger les titres de section de la conclusion.
4. Aligner les trois résumés et la page de garde.
5. Ajouter le run court à la matrice de preuves.
6. Vérifier ou régénérer la figure CICIDS, puis compiler trois fois et contrôler la table des matières, la liste des tableaux et les références croisées.

