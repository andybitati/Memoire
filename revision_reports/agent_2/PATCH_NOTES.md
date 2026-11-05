# PATCH NOTES — Agent 2, Histogram et HDFS

**Effort estimé d'intégration :** 3 à 4 heures (nouvelle sous-section Histogram au chapitre 4, réécriture de la section HDFS du chapitre 5, propagation du nouveau F1 dans les résumés, la conclusion et l'annexe A.2 ; la figure bootstrap HDFS devient secondaire).

**Blocages et réserves :**

1. **Le F1 principal HDFS change.** Sur la partition de test complète (115 013 blocs, 1 679 positifs), F1 = 0,868373, contre 0,892308 sur l'échantillon de 2 000 blocs. La valeur 0,892308 est **hors** de l'IC à 95 % du test complet [0,856771 ; 0,879493] : l'échantillon surestimait la performance. Conformément à la règle 2, on corrige l'affirmation, pas le résultat.
2. **L'écart de prévalence n'est pas un artefact d'échantillonnage.** Il persiste sur les partitions complètes (train 3,2339 %, validation 3,4788 %, test 1,4598 %) : il provient de la partition chronologique par première apparition. La remarque du jury attendait l'inverse ; il faut l'écrire tel quel.
3. **Variabilité nulle entre graines.** Les cinq graines (42–46) donnent la même matrice de confusion ; seuls les seuils et la PR-AUC varient légèrement. L'IC de Student entre graines est de largeur nulle et ne doit pas être présenté comme incertitude ; on rapporte des IC sur les blocs de test (Clopper-Pearson, bootstrap multinomial).
4. **BGL n'utilise pas de fenêtres.** Le score Histogram BGL est calculé par événement (ligne de journal) : `scripts/run_strict_sequence_experiments.py:388-409`, scores stockés tels quels dans `bgl_feature_bundle.npz` et évalués sans agrégation par `scripts/run_bgl_known_unknown_strengthening.py:139-142`. Les « unités » BGL (19 908) sont des événements. Le texte « fondé sur des fenêtres » est inexact.
5. Reproductibilité vérifiée : deux exécutions indépendantes (`agent2_hdfs_full_20261104T131314Z` et `agent2_hdfs_full_20261104T134240Z`) donnent des états Drain3 de même sha256 et des métriques identiques pour chaque graine.

## Registre des preuves

| Élément | `run_id` | Source |
|---|---|---|
| HDFS test complet, 5 graines | `agent2_hdfs_full_20261104T131314Z` | `revision_reports/agent_2/agent2_hdfs_full_20261104T131314Z__result.json`, `__seed_metrics.csv`, `__partition_prevalence.csv` |
| Réplication indépendante | `agent2_hdfs_full_20261104T134240Z` | `revision_reports/agent_2/agent2_hdfs_full_20261104T134240Z__result.json` |
| IC sur les blocs de test | `agent2_hdfs_full_20261104T131314Z__test_block_ci` | `revision_reports/agent_2/agent2_hdfs_full_20261104T131314Z__test_block_ci.json` (script `hdfs_full_confidence_intervals.py`) |
| Partition source | `ds_hdfs_block_20260910T081756Z` | `experiments/phase_dataset_strengthening/processed/ds_hdfs_block_20260910T081756Z__hdfs_full_block_partitions.txt.gz` |

## Résultats

Protocole : partition 60/20/20 des 575 061 blocs par première apparition (identique au run source). Pour chaque graine, 6 000 blocs du train sont échantillonnés de façon stratifiée (194 positifs) ; Drain3 (`sim_th=0.4`, profondeur 4, 100 enfants) est ajusté sur ces blocs, persisté, rechargé, puis utilisé en `match` seul. Validation (115 012 blocs) et test (115 013 blocs) sont complets. Agrégateur et seuil choisis sur validation uniquement ; le test n'est utilisé qu'une fois par graine.

| Mesure | Valeur | IC 95 % |
|---|---|---|
| Agrégateur retenu (5/5 graines) | moyenne | — |
| Seuil bloc | 1,272927 à 1,274817 selon la graine | — |
| TP / FP / TN / FN | 1 679 / 509 / 112 825 / 0 | — |
| Précision | 0,767367 | [0,749084 ; 0,784932] (Clopper-Pearson) |
| Rappel | 1,000000 | [0,997805 ; 1] (Clopper-Pearson) |
| FPR | 0,004491 | [0,004110 ; 0,004898] (Clopper-Pearson) |
| F1 | 0,868373 | [0,856771 ; 0,879493] (bootstrap, 20 000 réplications) |
| MCC | 0,874026 | [0,863629 ; 0,884107] (bootstrap) |
| PR-AUC (moyenne des graines) | 0,848676 | min 0,844940, max 0,850179 |
| Clusters Drain3 selon la graine | 24 à 36 | — |
| Événements incohérents / blocs manquants | 0 / 0 | — |

## 1. Nouvelle sous-section : définition formelle du détecteur Histogram

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre4_implementation.tex`, section « Parsing HDFS et BGL » — insérer après le paragraphe sur l'agrégation par `block_id` (ligne 76).

**Texte proposé :**

```latex
\subsection{Détecteur Histogram}
\label{subsec:histogram}

Le détecteur Histogram attribue à chaque événement un score de rareté calculé à partir des seuls événements normaux de l'entraînement. Soit $N$ le nombre d'événements normaux d'entraînement et, pour un événement $e$, $\tau(e)$ son template Drain3, $s(e)$ sa source et $v(e)$ sa sévérité. Pour chaque attribut $a \in \{\tau, s, v\}$, on note $n_a(x)$ le nombre d'événements normaux d'entraînement prenant la valeur $x$ et l'on définit la fréquence lissée
\[
  \tilde{p}_a(x) = \frac{\max\bigl(n_a(x), 1\bigr)}{N}.
\]
Le score de rareté de l'événement est la moyenne des log-raretés :
\[
  r(e) = -\frac{1}{3}\Bigl[\log \tilde{p}_\tau\bigl(\tau(e)\bigr) + \log \tilde{p}_s\bigl(s(e)\bigr) + \log \tilde{p}_v\bigl(v(e)\bigr)\Bigr].
\]
Une valeur jamais observée, en particulier un template inconnu du parseur gelé, reçoit le compte plancher 1 et donc la rareté maximale $\log N$ pour cet attribut.

Pour HDFS, dont les labels portent sur le bloc, les scores sont agrégés par \texttt{block\_id}. Trois agrégateurs sont comparés sur la validation : le maximum, la moyenne $R(b) = \frac{1}{|b|}\sum_{e \in b} r(e)$ et la proportion d'événements dont le score dépasse un seuil événementiel. Pour BGL, l'unité évaluée est l'événement lui-même : aucune fenêtre ni agrégation n'est appliquée.

Le seuil $\theta$ est choisi sur la validation parmi les points de la courbe précision–rappel, en maximisant le F1 ; les ex æquo sont départagés par le FPR le plus faible, puis le MCC le plus élevé, puis le seuil le plus élevé. Une unité est déclarée anormale si son score est supérieur ou égal à $\theta$.

\begin{verbatim}
Entrée : événements train/validation/test, état Drain3 gelé
N  <- nombre d'événements normaux du train
pour a dans {template, source, sévérité} :
    n_a <- comptes de a sur les événements normaux du train
pour chaque événement e :
    r(e) <- -(1/3) * somme_a log(max(n_a[a(e)], 1) / N)
si HDFS : R(b) <- agrégat_g(r(e) pour e dans b), g choisi sur validation
si BGL  : R(e) <- r(e)
theta <- argmax_F1 sur la validation (départage FPR, MCC, seuil)
prédiction(u) <- [R(u) >= theta]
\end{verbatim}

L'implémentation correspond à la fonction \texttt{histogram\_scores} de \texttt{scripts/run\_strict\_sequence\_experiments.py} et de \texttt{scripts/run\_hdfs\_block\_strengthening.py}, et à \texttt{select\_threshold} de \texttt{scripts/dataset\_strengthening\_common.py}.
```

## 2. BGL : « fenêtres » → événements

**Fichier :** `chapters/chapitre4_implementation.tex`, ligne 78.

**Texte actuel exact :**

```latex
BGL suit un protocole différent, fondé sur des fenêtres. L'évaluation Histogram est complétée par une séparation entre templates connus et inconnus ainsi que par le baseline \texttt{UnknownTemplateBaseline}.
```

**Texte proposé :**

```latex
BGL suit un protocole différent : l'unité évaluée est l'événement, sans fenêtre ni agrégation (sous-section~\ref{subsec:histogram}). L'évaluation Histogram est complétée par une séparation entre templates connus et inconnus ainsi que par le baseline \texttt{UnknownTemplateBaseline}.
```

**Fichier :** `chapters/chapitre5_resultats.tex`, ligne 35 (tableau des unités).

**Texte actuel exact :** `BGL & fenêtre/template & Apport d’Histogram au-delà d’un baseline de nouveauté. \\`
**Texte proposé :** `BGL & événement/template & Apport d’Histogram au-delà d’un baseline de nouveauté. \\`

**Fichier :** `chapters/chapitre5_resultats.tex`, ligne 167 : remplacer « évalué sur $19\,908$ unités » par « évalué sur $19\,908$ événements » et « $17\,879$ unités » par « $17\,879$ événements ».

## 3. Chapitre 5 : section HDFS

**Fichier :** `chapters/chapitre5_resultats.tex`, section « HDFS : décision au niveau bloc ».

**Texte actuel exact (l. 129) :**

```latex
Le fichier HDFS contient $11\,175\,629$ lignes et $575\,061$ blocs annotés. Les blocs sont ordonnés par première apparition, puis répartis selon des proportions 60/20/20. Le protocole échantillonne $6\,000$ blocs d’entraînement, $2\,000$ de validation et $2\,000$ de test avec la graine 42. Ces ensembles contiennent respectivement 194, 70 et 29 blocs positifs.
```

**Texte proposé :**

```latex
Le fichier HDFS contient $11\,175\,629$ lignes et $575\,061$ blocs annotés. Les blocs sont ordonnés par première apparition, puis répartis selon des proportions 60/20/20 : $345\,036$ blocs d'entraînement, $115\,012$ de validation et $115\,013$ de test, dont respectivement $11\,158$, $4\,001$ et $1\,679$ positifs. La prévalence vaut donc $3{,}23\,\%$, $3{,}48\,\%$ et $1{,}46\,\%$ : la baisse au test tient à l'ordre chronologique de la partition et non à un échantillonnage. Pour chacune des graines 42 à 46, $6\,000$ blocs d'entraînement (194 positifs) sont tirés de façon stratifiée pour ajuster le parseur ; la validation et le test sont utilisés en entier.
```

**Texte actuel exact (l. 131, début) :** `Drain3 est ajusté uniquement sur les $126\,368$ événements d’entraînement avec`
**Texte proposé :** `Pour chaque graine, Drain3 est ajusté uniquement sur les événements des blocs d'entraînement tirés avec` — et remplacer « le nombre de 28 clusters » par « le nombre de clusters (24 à 36 selon la graine) ».

**Texte actuel exact (l. 145) :**

```latex
L’agrégateur retenu est la moyenne et le seuil gelé vaut $1{,}2729429339548877$. Sur les $2\,000$ blocs testés, la matrice de confusion est : 29 vrais positifs, 7 faux positifs, $1\,964$ vrais négatifs et aucun faux négatif. Le F1 atteint $0{,}892308$. Le faible nombre de positifs impose néanmoins de quantifier l’incertitude.
```

**Texte proposé :**

```latex
La validation retient la moyenne pour les cinq graines, avec un seuil compris entre $1{,}272927$ et $1{,}274817$. Sur les $115\,013$ blocs de test, les cinq graines produisent la même matrice de confusion : $1\,679$ vrais positifs, 509 faux positifs, $112\,825$ vrais négatifs et aucun faux négatif. La précision vaut $0{,}767367$ (IC exact à 95~\% : $[0{,}749084\,;\,0{,}784932]$), le rappel $1$ ($[0{,}997805\,;\,1]$), le FPR $0{,}004491$ et le F1 $0{,}868373$ (IC bootstrap à 95~\% : $[0{,}856771\,;\,0{,}879493]$). La PR-AUC varie de $0{,}844940$ à $0{,}850179$ selon la graine. Le F1 de $0{,}892308$ obtenu antérieurement sur un échantillon de $2\,000$ blocs, dont 29 positifs, se situe hors de cet intervalle : l'échantillon surestimait la performance.
```

**Sous-section « Bootstrap par bloc » (l. 147-161) :** la remplacer par une phrase de renvoi, la figure pouvant passer en annexe :

```latex
\subsection{Incertitude}

Le choix de la graine d'échantillonnage du parseur n'induit aucune variation de la matrice de confusion. L'incertitude rapportée porte donc sur les blocs de test : intervalles exacts de Clopper-Pearson pour la précision, le rappel et le FPR, et bootstrap multinomial de $20\,000$ réplications pour le F1 et le MCC. Le bootstrap antérieur sur les $2\,000$ blocs (médiane $0{,}894737$, intervalle $[0{,}800000\,;\,0{,}961039]$) est conservé en annexe comme trace de l'échantillon initial.
```

**Texte actuel exact (l. 163) :** `Le protocole soutient donc une détection efficace sur l’échantillon de blocs testé, avec un parseur et un seuil isolés du test. La portée reste limitée par l’échantillonnage de $2\,000$ blocs et par 29 positifs seulement.`
**Texte proposé :** `Le protocole soutient donc une détection efficace sur la partition de test complète, avec un parseur et un seuil isolés du test : aucun bloc anormal n'est manqué, au prix d'environ un faux positif pour trois alertes.`

## 4. Résumés (FR, EN, lingala), conclusion, chapitre 6, annexe

**`main.tex` l. 324-327 (FR) — texte actuel exact :**

```latex
gelé avant les deux partitions suivantes. Au niveau \texttt{block\_id}, Histogram
atteint un F1 de $0{,}892308$ sur 2\,000 blocs HDFS, dont 29 positifs ;
le bootstrap descriptif donne une médiane de $0{,}894737$ et un intervalle
$[0{,}800000\,;\,0{,}961039]$.
```

**Proposé :**

```latex
gelé avant les deux partitions suivantes. Au niveau \texttt{block\_id}, Histogram
atteint un F1 de $0{,}868373$ (IC à 95~\% : $[0{,}856771\,;\,0{,}879493]$) sur les
$115\,013$ blocs de test HDFS, dont $1\,679$ positifs, avec un rappel de $1$ et
une précision de $0{,}767367$, identiques pour cinq graines d'échantillonnage.
```

**`main.tex` l. 444 et suivantes (EN)** : même substitution — « Histogram reaches an F1-score of $0.868373$ (95\% CI $[0.856771;\,0.879493]$) on the $115{,}013$ HDFS test blocks, including $1{,}679$ positives, with a recall of $1$ and a precision of $0.767367$, identical across five sampling seeds. »

**`main.tex` l. 559-564 (lingala)** : remplacer `0{,}892308`, « 2\,000 blocs … 29 positifs » et la phrase bootstrap par « F1 $0{,}868373$ (IC 95~\% $[0{,}856771\,;\,0{,}879493]$) na ba blocs $115\,013$ ya test, kati na yango $1\,679$ positifs ». *Relecture linguistique requise.*

**`chapters/chapitre6_conclusion.tex` l. 11 :** `conduit à un F1 de $0{,}892308$ au niveau bloc` → `conduit à un F1 de $0{,}868373$ au niveau bloc sur la partition de test complète`.

**`chapters/chapitre6_conclusion.tex` l. 101 :** supprimer « Le test HDFS ne contient que 29 blocs positifs. » (limite levée).

**`chapters/chapitre6_conclusion.tex` l. 112 :** supprimer « Dans HDFS, une évaluation sur un plus grand nombre de blocs positifs permettrait de réduire l'incertitude actuelle. » (réalisé).

**`chapters/chapitre6_approfondissements_scientifiques.tex` l. 29 :** `Pour HDFS, l’évaluation finale porte sur $2\,000$ blocs dont seulement 29 sont positifs. Le bootstrap renseigne sur la sensibilité du F1 à cet échantillon ; il ne décrit pas une population universelle de systèmes distribués.` → `Pour HDFS, l’évaluation finale porte sur les $115\,013$ blocs de test d'un seul système ; les intervalles décrivent l'incertitude sur ce corpus, non sur une population de systèmes distribués.`

**`chapitre6_approfondissements_scientifiques.tex` l. 14 :** « Drain3 apprend 28 clusters » → « Drain3 apprend 24 à 36 clusters selon la graine ».

**`chapitre7_reproductibilite_deploiement.tex` l. 48 :** remplacer « les échantillons de $6\,000$, $2\,000$ et $2\,000$ blocs, ainsi que la graine 42 » par « l'échantillon d'entraînement de $6\,000$ blocs tiré avec les graines 42 à 46, la validation et le test complets » et « le seuil $1{,}2729429339548877$ sont gelés » par « le seuil choisi pour chaque graine (entre $1{,}272927$ et $1{,}274817$) sont gelés ».

**`chapters/annexes.tex` l. 61-62 — actuel exact :**

```latex
HDFS bloc & F1 0,892308 & \texttt{ds\_hdfs\_block\_20260910T081756Z\_\_hdfs\_block\_result.json} \\
Bootstrap HDFS & médiane 0,894737 & \texttt{hdfs\_block\_robustness\_20260911T002351Z\_bootstrap\_replicates.csv} \\
```

**Proposé :**

```latex
HDFS bloc, test complet & F1 0,868373 ; IC [0,856771 ; 0,879493] ; 5 graines & \texttt{agent2\_hdfs\_full\_20261104T131314Z\_\_result.json} \\
HDFS bloc, échantillon initial & F1 0,892308 sur 2\,000 blocs ; bootstrap médiane 0,894737 & \texttt{ds\_hdfs\_block\_20260910T081756Z\_\_hdfs\_block\_result.json} \\
```

**Note de cohérence avec l'agent 3 :** la campagne distribuée `hdfs_multivm_cnp_20261104T135345Z` porte sur les 2 000 blocs de l'échantillon initial ; son F1 de 0,892308 doit être présenté comme l'équivalence avec le calcul centralisé sur ce même échantillon, et non comme la performance HDFS de référence.
