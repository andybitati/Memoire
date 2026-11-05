# PATCH NOTES — Agent 7 : reproductibilité, rédaction, utilité, déclaration IA

## En-tête : effort d'intégration et blocages

**Effort estimé :** 3 à 4 h pour les textes, plus 2 à 3 h pour la publication.
- Parties B, C et D (textes du mémoire) : 2 h 30 à 3 h, compilation et
  relecture comprises. Insertion de deux fichiers LaTeX prêts à l'emploi
  (`latex/spec_utilite.tex`, `latex/limites_consolidees.tex`), remplacement
  d'un troisième (`latex/declaration_ia.tex`), une vingtaine de remplacements
  courts.
- Partie A (dépôt public, Zenodo) : 2 à 3 h. Copie sélective, deux copies
  d'artefacts, trois lignes à modifier dans le générateur de figures, release
  et DOI.

**Blocages (décision de l'auteur requise) :**
1. **DOI** : il n'existe qu'après la release Zenodo. Le champ reste
   `[DOI À COMPLÉTER]` (A.6). « Reserve DOI » permet de l'obtenir avant le
   dépôt du PDF (procédure : `public_release/PUBLIC_RELEASE_PLAN.md` §5).
2. **Données personnelles** dans des artefacts suivis par git : journaux de
   sécurité Windows de la machine de l'auteur (nom d'utilisateur, nom d'hôte)
   et adresses IP privées (`PUBLIC_RELEASE_PLAN.md` §3). Il faut choisir entre
   publier, pseudonymiser ou exclure. La pseudonymisation invalide les
   empreintes SHA-256 des manifestes.
3. **Licences des jeux CIC (CICIDS2017, CSE-CIC-IDS2018) et UNSW-NB15** : non
   vérifiées, faute de source locale. Il faut confirmer que la redistribution
   d'extraits et de modèles dérivés est permise (`DATA_LICENSES.md`).
4. **Déclaration IA** : les outils exacts, leurs versions, les périodes
   d'usage et les parties concernées ne peuvent être connus que de l'auteur.
   Les champs `[À COMPLÉTER PAR L'AUTEUR]` sont bloquants.
5. **Bokuse (lingala)** : seules les suppressions sont proposées. La phrase de
   synthèse ajoutée est à traduire ou valider par l'auteur (B.9).
6. **Coordination avec l'agent 1** : il remplace déjà le paragraphe multi-VM
   des résumés et corrige la numérotation 7.11–7.17 de la conclusion
   (`revision_reports/agent_1/PATCH_NOTES.md`, §2–4 et §11). Il faut appliquer
   ses patchs **avant** B.7 et B.9. Les textes « actuels » cités ci-dessous
   sont ceux du dépôt au commit `35da3a9`.

**Vérifications effectuées :**
- Chaque « texte actuel exact » cité ici a été comparé automatiquement au
  contenu des `.tex` au commit `35da3a9` : 39 extraits, tous retrouvés.
- Les trois fichiers de `latex/` ont été compilés avec pdfLaTeX dans un
  document de test hors dépôt, avec un préambule équivalent à celui de
  `main.tex` : ni erreur, ni référence indéfinie, ni dépassement de ligne.
- `CITATION.cff` (YAML) et `.zenodo.json` (JSON) ont été validés
  syntaxiquement.

**Ordre d'intégration conseillé :** agent 1 → C.1 (définit
`sec:spec-utilite`) → B.1 (définit `sec:limites`) → reste de B → C.2–C.4 →
A.1–A.6 → D → deux compilations complètes et recherche de `??` dans le PDF.

## Correspondance fichiers / numérotation du PDF (vérifiée via `main.toc`)

| PDF | Fichier |
|---|---|
| Introduction (non numérotée) | `chapters/chapitre1_introduction.tex` |
| Ch. 1 État de l'art | `chapters/chapitre2_etat_art.tex` |
| Ch. 2 Modèle proposé | `chapters/chapitre3_modele_propose.tex` |
| Ch. 3 Implémentation | `chapters/chapitre4_implementation.tex` |
| Ch. 4 Résultats (4.13 = Synthèse) | `chapters/chapitre5_resultats.tex` |
| Ch. 5 Validité scientifique (5.7 = Conclusions soutenues) | `chapters/chapitre6_approfondissements_scientifiques.tex` |
| Ch. 6 Discussion (6.7 = Réponses transversales) | `chapters/chapitre6_discussion.tex` |
| Ch. 7 Reproductibilité | `chapters/chapitre7_reproductibilite_deploiement.tex` |
| Conclusion (sections numérotées à tort 7.11–7.17 ; 7.15 = Limites) | `chapters/chapitre6_conclusion.tex` |
| Annexe A (A.8 = Conditions d'interprétation) | `chapters/annexes.tex` |

La tâche C (« chapitre 3 ») est placée dans le **chapitre 3 du PDF
(Implémentation)**, puisqu'elle décrit le code. Le chapitre 2 (Modèle) et
l'introduction y renvoient (C.2, C.3). Si l'auteur visait le fichier
`chapitre3_modele_propose.tex`, il suffit d'insérer le même bloc après la
ligne 451 de ce fichier.

---

## Partie A — Publication du dépôt

### Fichiers proposés (dans `revision_reports/agent_7/public_release/`)

| Fichier | Destination dans le dépôt public |
|---|---|
| `README_public.md` | `README.md` |
| `LICENSE` | `LICENSE` (MIT, code uniquement) |
| `DATA_LICENSES.md` | `DATA_LICENSES.md` |
| `CITATION.cff` | `CITATION.cff` (validé en YAML) |
| `.zenodo.json` | `.zenodo.json` (validé en JSON) |
| `gitignore_public_additions.txt` | à fusionner dans `.gitignore` |
| `PUBLIC_RELEASE_PLAN.md` | document de travail : structure, exclusions, données sensibles, procédure Zenodo/DOI |

Choix de licence : MIT pour le code, pour sa simplicité et sa compatibilité.
Apache-2.0 serait préférable si une clause explicite sur les brevets est
souhaitée. Les données restent sous les licences d'origine. Seule celle de
Loghub (CC BY 4.0) est vérifiée localement
(`data/verification/public_sources/zenodo_8196385_metadata.json`).

### Inventaire des chemins internes dans les `.tex`

Recherche effectuée sur tous les `.tex` du dossier du mémoire. Motifs :
`pack_redaction`, `revision_reports`, chemins absolus `X:\` et `X:/`,
`docs/memoire`, `data/processed`, `.secrets`, `ARIEL_LOGMINER`, et tout
`\texttt{…/…}` ou nom de fichier `.csv/.json/.py`.
**Aucun chemin absolu (`E:\`, `C:\Users\…`) n'apparaît dans les `.tex`.**

| # | Fichier:ligne | Chemin actuel | Problème | Remplacement |
|---|---|---|---|---|
| P1 | `annexes.tex:60` | `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/cicids_model_candidates_summary.csv` | dossier interne | `experiments/phase_reference_copies/cicids_model_candidates_summary.csv` (SHA-256 identique, `4EDA14B9…0C69`) |
| P2 | `annexes.tex:72` | `data/processed/final_experiments_2026/correlation_synthetic_summary.json` | ignoré par git, **absent du dépôt** | `experiments/phase_reference_copies/correlation_synthetic_summary.json` (`33AEF93F…1B42`) |
| P3 | `annexes.tex:61–71` | noms de fichiers sans dossier | non localisables | chemins complets (A.1) |
| P4 | `chapitre7…:20` | `experiments/phase\_multi\_agent` « contient … la campagne multi-VM » | la campagne de référence se trouve sous `experiments/phase_cnp_endurance/` | A.2 |
| P5 | `chapitre7…:24` | `revision\_reports` | dossier interne | A.2 |
| P6 | `chapitre7…:39` | `revision\_reports/generate\_final\_scientific\_figures.py` | chemin faux (le fichier est sous `ARIEL_LOGMINER_MEMOIRE_FINAL/revision_reports/`) et interne | `memoire/scripts/generate_final_scientific_figures.py` (A.3) |
| P7 | `chapitre7…:89` | `ARIEL\_LOGMINER\_MEMOIRE\_FINAL` | nom de dossier interne | section supprimée (B.10a) ; contenu repris dans le README |
| P8 | `chapitre5_resultats.tex:65–339` (14 légendes) | noms de fichiers seuls | acceptable | aucun changement : l'annexe A.3 donne les chemins complets |

Localisation vérifiée de chaque artefact cité (taille en octets) :

| Artefact | Chemin réel |
|---|---|
| `cicids_protocol_comparison.csv` | `experiments/phase_dataset_strengthening/aggregated/` |
| `ds_hdfs_block_20260910T081756Z__hdfs_block_result.json` | `experiments/phase_dataset_strengthening/raw/` |
| `hdfs_block_robustness_20260911T002351Z_bootstrap_replicates.csv` | `experiments/phase_final_scientific_consolidation/raw/` |
| `ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv` | `experiments/phase_dataset_strengthening/raw/` |
| `external_csecicids2018_20260910T230136Z_metrics.csv` | `experiments/phase_dataset_strengthening/raw/` |
| `external_csecicids2018_feature_ablation.csv`, `…_lr_coefficients.csv`, `…_single_feature_scores.csv` | `experiments/phase_final_scientific_consolidation/aggregated/` |
| `final_csecic_lr_forensic_20260911T000140Z_label_permutation.csv` | `experiments/phase_final_scientific_consolidation/raw/` |
| `router_open_set_final_tradeoff_diagnostic.csv` | `experiments/phase_final_scientific_consolidation/aggregated/` |
| `multiformat_balanced_summary.csv` | `experiments/phase_dataset_strengthening/aggregated/` |
| `multisource_cnp_model_inference_by_source.csv` | `experiments/phase_final_scientific_consolidation/aggregated/` |
| `ma_20260909T160812Z_34016__statistics.csv` | `experiments/phase_multi_agent/aggregated/` |
| `cnp_endurance_multivm_20260918T130822Z__summary.json` | `experiments/phase_cnp_endurance/aggregated/` |

### A.1 — Annexe A.3, matrice résultats–preuves

**Fichier :** `chapters/annexes.tex` — section « Matrice résultats--preuves ».
Pour gagner de la largeur, les chemins sont abrégés par une note unique placée
avant la `longtable`.

**Ajout avant** `\begin{longtable}{p{0.20\textwidth} p{0.18\textwidth} p{0.52\textwidth}}` :

```latex
Les chemins sont relatifs à la racine du dépôt public
(section~\ref{sec:depot-public}). Les abréviations \texttt{DS},
\texttt{FSC}, \texttt{MA}, \texttt{CNP} et \texttt{REF} désignent
respectivement \texttt{experiments/phase\_dataset\_strengthening},
\texttt{experiments/phase\_final\_scientific\_consolidation},
\texttt{experiments/phase\_multi\_agent},
\texttt{experiments/phase\_cnp\_endurance} et
\texttt{experiments/phase\_reference\_copies}.
```

**Texte actuel exact (l. 57–72) puis texte proposé, ligne par ligne :**

| Actuel | Proposé |
|---|---|
| `CICIDS random RF & F1 0,995142 & \texttt{experiments/phase\_dataset\_strengthening/aggregated/cicids\_protocol\_comparison.csv} \\` | `CICIDS random RF & F1 0,995142 & \texttt{DS/aggregated/cicids\_protocol\_comparison.csv} \\` |
| `Sélection CICIDS & LR 0,233670 & \texttt{docs/memoire/pack\_redaction\_final/06\_reproductibilite\_preuves/cicids\_model\_candidates\_summary.csv} \\` | `Sélection CICIDS & LR 0,233670 & \texttt{REF/cicids\_model\_candidates\_summary.csv} \\` |
| `HDFS bloc & F1 0,892308 & \texttt{ds\_hdfs\_block\_20260910T081756Z\_\_hdfs\_block\_result.json} \\` | `HDFS bloc & F1 0,892308 & \texttt{DS/raw/ds\_hdfs\_block\_20260910T081756Z\_\_hdfs\_block\_result.json} \\` |
| `Bootstrap HDFS & médiane 0,894737 & \texttt{hdfs\_block\_robustness\_20260911T002351Z\_bootstrap\_replicates.csv} \\` | `Bootstrap HDFS & médiane 0,894737 & \texttt{FSC/raw/hdfs\_block\_robustness\_20260911T002351Z\_bootstrap\_replicates.csv} \\` |
| `BGL Histogram & F1 0,913698 & \texttt{ds\_bgl\_known\_unknown\_20260910T082706Z\_\_bgl\_group\_metrics.csv} \\` | `BGL Histogram & F1 0,913698 & \texttt{DS/raw/ds\_bgl\_known\_unknown\_20260910T082706Z\_\_bgl\_group\_metrics.csv} \\` |
| `CSE-CIC-IDS2018 & LR 0,999212 ; RF 0,401375 & \texttt{external\_csecicids2018\_20260910T230136Z\_metrics.csv} \\` | `CSE-CIC-IDS2018 & LR 0,999212 ; RF 0,401375 & \texttt{DS/raw/external\_csecicids2018\_20260910T230136Z\_metrics.csv} \\` |
| `Ablation CSE-CIC & top 10 retirées : 0,657859 & \texttt{external\_csecicids2018\_feature\_ablation.csv} \\` | `Ablation CSE-CIC & top 10 retirées : 0,657859 & \texttt{FSC/aggregated/external\_csecicids2018\_feature\_ablation.csv} \\` |
| `Routeur open-set & rejet 3/3 ; faux rejet 0/28 & \texttt{router\_open\_set\_final\_tradeoff\_diagnostic.csv} \\` | `Routeur open-set & rejet 3/3 ; faux rejet 0/28 & \texttt{FSC/aggregated/router\_open\_set\_final\_tradeoff\_diagnostic.csv} \\` |
| `Multiformat & $7\,001/7\,001$ & \texttt{multiformat\_balanced\_summary.csv} \\` | `Multiformat & $7\,001/7\,001$ & \texttt{DS/aggregated/multiformat\_balanced\_summary.csv} \\` |
| `E2E modèles & $1\,400/1\,401$ & \texttt{multisource\_cnp\_model\_inference\_by\_source.csv} \\` | `E2E modèles & $1\,400/1\,401$ & \texttt{FSC/aggregated/multisource\_cnp\_model\_inference\_by\_source.csv} \\` |
| `Benchmark A--D & 160 exécutions ; $264\,000$ tâches & \texttt{ma\_20260909T160812Z\_34016\_\_statistics.csv} \\` | `Benchmark A--D & 160 exécutions ; $264\,000$ tâches & \texttt{MA/aggregated/ma\_20260909T160812Z\_34016\_\_statistics.csv} \\` |
| `Endurance CNP multi-VM & $1\,800/1\,800$ ; 1 h & \texttt{cnp\_endurance\_multivm\_20260918T130822Z\_\_summary.json} \\` | `Endurance CNP multi-VM & $1\,800/1\,800$ ; 1 h & \texttt{CNP/aggregated/cnp\_endurance\_multivm\_20260918T130822Z\_\_summary.json} \\` |
| `Corrélation & F1 0,812500 & \texttt{data/processed/final\_experiments\_2026/correlation\_synthetic\_summary.json} \\` | `Corrélation & F1 0,812500 & \texttt{REF/correlation\_synthetic\_summary.json} (\texttt{run\_id} \texttt{e8\_correlation\_synthetic\_controlled}) \\` |

Les lignes 58–59 et 64 (« Même synthèse… », « Même artefact… ») sont
inchangées.
**Justification :** chaque preuve devient localisable dans le dépôt public.
P2 désigne aujourd'hui un fichier non versionné.

### A.2 — Chapitre 7, section « Organisation des preuves »

**Fichier :** `chapters/chapitre7_reproductibilite_deploiement.tex`, l. 18–24.

**Texte actuel exact :**
```latex
    \item \texttt{experiments/phase\_dataset\_strengthening} regroupe les protocoles HDFS, BGL, multi-format et CSE-CIC-IDS2018 ;

    \item \texttt{experiments/phase\_multi\_agent} contient le benchmark A--D ainsi que la campagne multi-VM ;

    \item \texttt{experiments/phase\_final\_scientific\_consolidation} rassemble les contrôles forensiques, le bootstrap HDFS, le routeur open-set et l'exécution multi-source avec modèles réels ;

    \item \texttt{revision\_reports} conserve les rapports de contrôle, le catalogue des preuves et le générateur des figures finales.
```

**Texte proposé :**
```latex
    \item \texttt{experiments/phase\_dataset\_strengthening} regroupe les protocoles HDFS, BGL, multi-format et CSE-CIC-IDS2018 ;

    \item \texttt{experiments/phase\_multi\_agent} contient le benchmark A--D et les campagnes Contract Net courtes ;

    \item \texttt{experiments/phase\_cnp\_endurance} contient la campagne d'endurance multi-VM de référence ;

    \item \texttt{experiments/phase\_final\_scientific\_consolidation} rassemble les contrôles forensiques, le bootstrap HDFS, le routeur open-set et l'exécution multi-source avec modèles réels ;

    \item \texttt{experiments/phase\_reference\_copies} conserve, avec leur empreinte d'origine, les deux artefacts cités produits hors de ces phases ;

    \item \texttt{state/EXPERIMENT\_LEDGER.csv} associe chaque \texttt{run\_id} à sa commande, à son statut et à ses chemins de sortie.
```
**Justification :** la campagne citée
(`cnp_endurance_multivm_20260918T130822Z`) est sous `phase_cnp_endurance`
(`experiments/README.md`). `revision_reports` ne fera pas partie du dépôt
public, et le registre des exécutions est la pièce qui relie `run_id` et
commande.

### A.3 — Chapitre 7, section « Chaîne de reproduction »

**Fichier :** même fichier, l. 39.

**Texte actuel exact :**
```latex
Le script \texttt{revision\_reports/generate\_final\_scientific\_figures.py} automatise la dernière étape.
```
**Texte proposé :**
```latex
Le script \texttt{memoire/scripts/generate\_final\_scientific\_figures.py} automatise la dernière étape.
```
**Justification :** le chemin actuel est faux et interne. Le déplacement
suppose de modifier trois lignes du script (l. 127, 134, 257 ;
`PUBLIC_RELEASE_PLAN.md` §4).

### A.4 — Chapitre 7 : nouvelle section « Dépôt public et archivage »

**Fichier :** `chapitre7_reproductibilite_deploiement.tex`. **Insertion**
après la section « Organisation des preuves », avant `\section{Chaîne de reproduction}`.

**Texte proposé :**
```latex
\section{Dépôt public et archivage}
\label{sec:depot-public}

Le code, les tests, les configurations, les artefacts expérimentaux et leurs
manifestes SHA-256, le registre des exécutions et les sources du mémoire sont
publiés dans un dépôt public archivé sur Zenodo sous le DOI
\texttt{10.5281/zenodo.[DOI À COMPLÉTER]}. Le code est diffusé sous licence
MIT. Les jeux de données publics ne sont pas redistribués : le dépôt indique
leur source et leurs conditions d'utilisation, et un script compare les copies
locales aux empreintes enregistrées. Les chemins cités dans ce mémoire sont
relatifs à la racine de ce dépôt.
```
**Justification :** demande du jury sur la publication. Cette section fixe
la convention de chemins utilisée en A.1.

### A.5 — Chapitre 7, section « Reproduction de la campagne multi-VM »

**Fichier :** même fichier, l. 79–81.

**Texte actuel exact :**
```latex
Les informations d'accès ne font pas partie des artefacts publiables. Identifiants de connexion et mots de passe doivent être fournis par des variables d'environnement ou par un mécanisme de gestion des secrets.

Le Redis utilisé dans le laboratoire reste centralisé et isolé. Une instance Redis exposée sur le réseau sans mécanisme d'authentification ne constitue pas un mode de déploiement recommandé.
```
**Texte proposé :**
```latex
Les identifiants de connexion aux machines virtuelles ne font pas partie du dépôt public ; ils sont fournis à l'exécution par des variables d'environnement ou un gestionnaire de secrets.
```
**Justification :** allègement. Le caractère central de Redis est traité
dans la section des limites (B.1).

### A.6 — Champ DOI

Le DOI apparaît en trois endroits : A.4, `CITATION.cff`, `.zenodo.json`
(implicite) et le README. Le reporter après la release (procédure :
`PUBLIC_RELEASE_PLAN.md` §5).

---

## Partie B — Limites : une version complète au chapitre 5, renvois ailleurs

### B.0 — Traçabilité des valeurs de la section des limites

| Valeur | Artefact (`run_id`) | Champ |
|---|---|---|
| F1 RF 0,995142 (aléatoire) → 0,157744 (scénario) | `experiments/phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv` | `f1` = 0.9951423171…, 0.1577441435… |
| `Dst Port` seul F1 0,999720 | `experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_single_feature_scores.csv` | `f1_mean` = 0.9997200789… |
| top 10 retirées F1 0,657859 | `…/aggregated/external_csecicids2018_feature_ablation.csv`, `removed_count=10` | `f1_mean` = 0.6578591870… |
| HDFS 29 positifs / 2 000 blocs test | `experiments/phase_dataset_strengthening/raw/ds_hdfs_block_20260910T081756Z__hdfs_block_result.json` | `selected_positive_blocks.test` = 29 ; `selected_block_counts.test` = 2000 |
| BGL connus : 2 029 unités, 0 positif | `experiments/phase_dataset_strengthening/raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv` | ligne `Histogram,KNOWN_TEMPLATE` : `n`=2029, `tp`=`fn`=0 |
| 89,8081 % de templates inconnus | même artefact : 17 879 / 19 908 = 0,898081 | lignes `UNKNOWN_TEMPLATE` et `ALL`, colonne `n` |
| Routeur : 3 inconnus, 28 connus | `experiments/phase_final_scientific_consolidation/aggregated/router_open_set_final_tradeoff_diagnostic.csv` | `unknown_n`=3, `known_n`=28 |
| 2 VM, 3 605,110 s | `experiments/phase_cnp_endurance/aggregated/cnp_endurance_multivm_20260918T130822Z__summary.json` | `distinct_agent_hosts`, `observed_duration_sec` |

### B.1 — Chapitre 5 : section unique des limites (insertion)

**Fichier :** `chapters/chapitre6_approfondissements_scientifiques.tex`.
**Insertion** en fin de fichier, après la section « Conclusions soutenues »,
du contenu de `revision_reports/agent_7/latex/limites_consolidees.tex`
(section `\label{sec:limites}`).
**Justification :** cette section regroupe en une seule formulation complète
les limites dispersées en 4.10, 4.13, 5.3, 5.7, 6.6, 6.7, 7.9, 7.15 et A.8.
Elle dépend de `sec:spec-utilite` (C.1) et de `tab:statut-model-update`
(label existant en annexe).

### B.2 — 5.7 « Conclusions soutenues », dernier paragraphe

**Fichier :** même fichier, l. 119.

**Texte actuel exact :**
```latex
Ces résultats permettent de soutenir le fonctionnement du prototype dans les conditions expérimentales décrites. Ils ne suffisent cependant pas à conclure à une exactitude globale sur des sources hétérogènes, à une supériorité générale du routage spécialisé, à un bénéfice systématique de la mémoire, à une mise à jour autonome des modèles ou à une disponibilité industrielle.
```
**Texte proposé :**
```latex
Ces résultats soutiennent le fonctionnement du prototype dans les conditions expérimentales décrites. Ce qu'ils ne permettent pas de conclure est précisé à la section~\ref{sec:limites}.
```

### B.3 — 5.3 « Validité externe », fin du paragraphe multi-VM (facultatif)

**Fichier :** même fichier, l. 33.

**Texte actuel exact :**
```latex
Une heure améliore la preuve d’endurance du protocole, mais ne renseigne pas sur les partitions réseau, le multi-site, un vieillissement sur plusieurs jours ou la haute disponibilité du broker.
```
**Texte proposé :**
```latex
Cette durée renforce la preuve d’endurance du protocole sans étendre sa portée au-delà de la topologie étudiée (section~\ref{sec:limites}).
```

### B.4 — 4.13 « Synthèse des résultats »

**Fichier :** `chapters/chapitre5_resultats.tex`.

(a) l. 420, **texte actuel exact :**
```latex
La poursuite bornée d'un objectif, l'enchaînement de sous-tâches, la délégation et la reprise d'état sont vérifiés fonctionnellement par les tests du noyau ; aucun gain de débit, de latence ou de qualité prédictive ne leur est attribué sans campagne quantitative dédiée.
```
**Texte proposé :**
```latex
La poursuite bornée d'un objectif, l'enchaînement de sous-tâches, la délégation et la reprise d'état sont vérifiés fonctionnellement par les tests du noyau.
```

(b) l. 422, **texte actuel exact :**
```latex
La contribution expérimentale réside donc moins dans un score unique que dans cette mise en relation entre résultat, protocole et preuve. Rien dans ces campagnes ne permet de conclure à une performance globale multi-source, à une supériorité universelle des agents ou à une validation d’infrastructure industrielle.
```
**Texte proposé :**
```latex
La contribution expérimentale réside donc moins dans un score unique que dans cette mise en relation entre résultat, protocole et preuve. La portée de ces résultats est discutée au chapitre suivant, et leurs limites sont rassemblées à la section~\ref{sec:limites}.
```

### B.5 — 4.10 « Campagne Contract Net multi-VM », dernier paragraphe (facultatif)

**Fichier :** même fichier, l. 402.

**Texte actuel exact :**
```latex
Redis demeure par ailleurs un point central : aucun basculement du broker, aucune partition réseau, aucun fonctionnement multi-site et aucune charge industrielle ne sont testés. La campagne valide des mécanismes de distribution en laboratoire, pas une architecture hautement disponible.
```
**Texte proposé :**
```latex
La campagne valide des mécanismes de distribution dans une topologie de laboratoire à Redis central.
```

### B.6 — Chapitre 6 : 6.6 « Portée opérationnelle » et 6.7 « Réponses transversales »

**Fichier :** `chapters/chapitre6_discussion.tex`.

(a) 6.6, l. 54–56, **texte actuel exact :**
```latex
Cela correspond à un prototype fonctionnel d’intégration et d’expérimentation. Plusieurs éléments nécessaires à une exploitation SOC complète restent absents ou non démontrés : redondance et basculement de Redis, contrôle d’accès complet, gestion industrielle des secrets, sécurité renforcée des échanges et observabilité distribuée sur de longues périodes.

La distinction est importante. Le prototype montre la faisabilité et le comportement de la chaîne dans un laboratoire contrôlé ; il ne constitue pas encore une plateforme opérationnelle prête à être déployée dans un SOC de production.
```
**Texte proposé :**
```latex
Cela correspond à un prototype fonctionnel d’intégration et d’expérimentation, qui montre la faisabilité et le comportement de la chaîne dans un laboratoire contrôlé. Les éléments manquants pour une exploitation en SOC sont recensés à la section~\ref{sec:limites}.
```

(b) 6.7, l. 67, **texte actuel exact :**
```latex
Enfin, les résultats négatifs contribuent directement à la validité du travail. Le faible F1 des holdouts CICIDS2017 montre les limites du transfert. L’absence de positifs parmi les templates BGL connus interdit certaines conclusions sur le rappel. L’instabilité observée après permutation sur CSE-CIC-IDS2018 aide à circonscrire la portée du score principal.
```
**Texte proposé :**
```latex
Enfin, les résultats négatifs contribuent directement à la validité du travail : ils délimitent la portée des scores principaux au lieu de l’affaiblir, comme le détaille la section~\ref{sec:limites}.
```

(c) 6.8, l. 80, dernière phrase, **texte actuel exact :**
```latex
À plus long terme, le passage vers une architecture de production demanderait de travailler la réplication et le basculement Redis, les partitions réseau, la sécurité des communications, le contrôle d’accès, la gestion des secrets et l’observabilité. La campagne d’une heure apporte une première preuve d’endurance ; des campagnes de plusieurs jours resteraient nécessaires pour étudier le vieillissement du système.
```
**Texte proposé :**
```latex
À plus long terme, le passage vers une architecture de production demanderait de lever les limites d’exploitation recensées à la section~\ref{sec:limites}, en commençant par la réplication du transport, les tests de partition et des campagnes de plusieurs jours.
```

### B.7 — Conclusion, section « Limites » (7.15 du PDF)

**Fichier :** `chapters/chapitre6_conclusion.tex`, l. 97–107 (après
application du patch §11 de l'agent 1, la ligne de titre devient
`\section*{Limites}` suivie de `\addcontentsline`).

**Texte actuel exact (corps, l. 99–107) :**
```latex
Les premières limites concernent les données. Les corpus utilisés ne couvrent qu'une partie des environnements possibles. CICIDS2017 montre précisément cette difficulté : la performance se dégrade fortement lorsque les scénarios de test sont séparés de ceux rencontrés pendant l'entraînement. Sur CSE-CIC-IDS2018, quelques caractéristiques jouent un rôle particulièrement important dans la séparation observée.

Les résultats HDFS et BGL doivent eux aussi être replacés dans leurs échantillons. Le test HDFS ne contient que 29 blocs positifs. Pour BGL, aucun exemple positif n'est présent parmi les templates connus, ce qui empêche d'y mesurer le rappel. L'évaluation open-set du routeur repose pour sa part sur seulement trois fichiers inconnus.

La validation distribuée reste également limitée au laboratoire. Redis est centralisé, deux machines virtuelles sont utilisées et la campagne dure une heure. Ni panne du broker, ni partition réseau, ni charge industrielle ni vieillissement sur plusieurs jours ne sont testés. Les métriques CPU et mémoire décrivent des processus locaux et ne représentent pas la consommation d'une infrastructure complète.

Il n'existe par ailleurs pas d'exactitude globale pour la campagne multi-source, puisque les sources ne partagent pas une vérité terrain homogène. Une telle valeur donnerait une impression de comparabilité que les données ne permettent pas de soutenir.

Enfin, la mémoire ne produit pas de gain systématique dans le benchmark. La poursuite d'objectifs, l'enchaînement, la délégation et la reprise sont couverts par des tests fonctionnels, mais leur coût et leur bénéfice ne sont pas mesurés par une campagne quantitative dédiée. La procédure de mise à jour contrôlée dispose d'une implémentation et d'un mode \textit{dry-run}, mais son intérêt n'a pas été mesuré à travers une série complète de promotions, rejets et évaluations ultérieures. Ariel Logminer reste donc un prototype expérimental et non un système autonome prêt pour une exploitation de production.
```
**Texte proposé :**
```latex
Les limites du travail sont exposées à la section~\ref{sec:limites}. Elles tiennent principalement à la portée des jeux de données et à la taille de certains échantillons de test, à l'absence de vérité terrain commune entre sources, à une validation distribuée limitée au laboratoire, et à l'absence de campagne quantitative sur la mémoire, la poursuite d'objectifs et la mise à jour des modèles. Ariel Logminer reste un prototype expérimental.
```
**Justification :** cette section était la principale répétition. Son contenu
est intégralement repris en B.1.

### B.8 — Annexe A.8 « Conditions d'interprétation des résultats »

**Fichier :** `chapters/annexes.tex`, l. 154–156.

**Texte actuel exact :**
```latex
\section{Conditions d’interprétation des résultats}

Le périmètre expérimental exclut la haute disponibilité Redis, la tolérance aux partitions, la sécurité opérationnelle complète et les performances à très grande échelle. Le routage open-set porte sur trois inconnus. Le F1 BGL ne fournit aucun rappel pour les anomalies à template connu. Le score CSE-CIC-IDS2018 dépend fortement de certaines caractéristiques. La mémoire influence une décision, mais n’améliore pas systématiquement les métriques. Aucune exactitude globale multi-source n’est disponible.
```
**Texte proposé :** suppression de la section. Aucun `\ref` n'y renvoie, car
la section n'a pas de label. A.9 devient A.8.

### B.9 — Résumé, Abstract, Bokuse (`main.tex`)

Le jury relève l'accumulation de réserves dans les résumés. On conserve les
qualifications indispensables à la lecture d'un résultat, on supprime les
réserves redondantes, puis on ajoute une phrase de synthèse unique. **Ne pas
toucher** au paragraphe multi-VM, que l'agent 1 remplace.

(a) Résumé, l. 339–344, **texte actuel exact :**
```latex
Ce résultat mesure la couverture fonctionnelle des formats testés ; il
n'établit ni la complétude de tous les champs ni la conservation universelle
du contenu brut. Une politique
open-set calibrée uniquement sur les sources connues rejette $3/3$ fichiers
inconnus sans faux rejet parmi $28$ fichiers connus ; la couverture est
$0{,}903226$ et la marge de décision n'est pas une probabilité calibrée.
```
**Proposé :**
```latex
Ce résultat mesure la couverture fonctionnelle des formats testés. Une politique
open-set calibrée uniquement sur les sources connues rejette $3/3$ fichiers
inconnus sans faux rejet parmi $28$ fichiers connus ; la couverture est
$0{,}903226$.
```

(b) Résumé, l. 371–374, **texte actuel exact :**
```latex
Le dépôt contient aussi une procédure de comparaison des modèles et un
mode dry-run. Les tests couvrent certaines branches, mais pas un cycle
complet et répété de promotion et de rejet. Le bénéfice global de cette
procédure n'a pas été évalué.
```
**Proposé :**
```latex
Le dépôt contient aussi une procédure de comparaison des modèles et un
mode dry-run, dont le bénéfice n'a pas été évalué. Les principales limites
tiennent à la taille de certains échantillons de test, à l'absence de vérité
terrain commune entre sources, à une validation distribuée limitée au
laboratoire et à l'absence de campagne quantitative sur la mémoire et la
poursuite d'objectifs.
```

(c) Abstract, l. 458–462, **texte actuel exact :**
```latex
units. This result measures functional coverage of the tested formats; it
does not establish field completeness or universal preservation of raw data.
An open-set policy calibrated only on known sources
rejects $3/3$ unknown files without falsely rejecting any of the 28 known
files; coverage is $0.903226$, and the decision margin is not a calibrated
probability.
```
**Proposé :**
```latex
units. This result measures functional coverage of the tested formats.
An open-set policy calibrated only on known sources
rejects $3/3$ unknown files without falsely rejecting any of the 28 known
files; coverage is $0.903226$.
```

(d) Abstract, l. 488–490, **texte actuel exact :**
```latex
The repository also contains a model-comparison procedure and a dry-run mode.
The tests cover some branches, but not a complete and repeated
promotion/rejection cycle. Its overall benefit was not evaluated.
```
**Proposé :**
```latex
The repository also contains a model-comparison procedure and a dry-run mode,
whose benefit was not evaluated. The main limitations are the size of some
test samples, the lack of a common ground truth across sources, a
laboratory-only distributed validation, and the absence of a quantitative
campaign on memory and goal pursuit.
```

(e) Bokuse, l. 579–584, **texte actuel exact :**
```latex
ya ba formats oyo emekamaki ; ezali te kolakisa ete ba champs nyonso
ezali complets, mpe ezali mpe te kolakisa ete contenu brut nyonso
ebatelami na ndenge ya universel. Politique open-set oyo ecalibramaki
kaka na ba sources oyo eyebani eboyi $3/3$ fichiers inconnus kozanga
faux rejet kati na $28$ fichiers connus ; couverture ezali
$0{,}903226$, mpe marge ya décision ezali te probabilité calibrée.
```
**Proposé (suppressions seules) :**
```latex
ya ba formats oyo emekamaki. Politique open-set oyo ecalibramaki
kaka na ba sources oyo eyebani eboyi $3/3$ fichiers inconnus kozanga
faux rejet kati na $28$ fichiers connus ; couverture ezali
$0{,}903226$.
```

(f) Bokuse, l. 614–617 : remplacer la phrase finale
`Litomba globale ya procédure oyo emekamaki te.` par
`[À TRADUIRE PAR L'AUTEUR : équivalent lingala de la phrase de synthèse (b)]`.
Faute de traduction validée, garder le texte actuel de l'Abstract et du
Bokuse sur ce point.

### B.10 — Allègement du chapitre 7

(a) **Suppression** de la section « Compilation du mémoire » (7.7),
l. 84–91. Texte actuel exact :
```latex
\section{Compilation du mémoire}

Le mémoire est compilé avec pdfLaTeX en UTF-8, avec encodage de police T1 et prise en charge du français. La bibliographie est générée entre les différentes passes LaTeX. Deux passes supplémentaires permettent ensuite de stabiliser les références croisées, la table des matières et les listes.

La compilation est lancée depuis le dossier
\texttt{ARIEL\_LOGMINER\_MEMOIRE\_FINAL}.

La vérification finale ne consiste pas uniquement à obtenir un PDF. Elle porte aussi sur les références non résolues, les débordements de mise en page significatifs, les labels dupliqués, les caractères corrompus et la présence effective de toutes les figures attendues.
```
Proposé : suppression. La commande de compilation est reprise dans le
`README_public.md`. **Justification :** cette section n'a pas de valeur
scientifique (remarque du jury).

(b) **Remplacement** de la section « Contrôles d'intégrité documentaire »
(7.10), l. 116–140. Texte actuel exact : de `\section{Contrôles d'intégrité documentaire}`
à `… ou de compilation du mémoire.` (liste de huit items : encodage UTF-8,
comparaison des valeurs, identification des jeux, unicité des labels LaTeX,
lisibilité A4, compilation de la bibliographie et accents, cohérence
résultat/périmètre, absence de secrets).
Proposé : supprimer la section et ajouter à la fin de la section « Principe
de reproductibilité » (après la l. 9) :
```latex
Avant livraison, les valeurs reprises dans le texte, les tableaux et les figures ont été comparées aux artefacts correspondants, et l'absence d'identifiants d'accès dans les éléments publiés a été vérifiée.
```
**Justification :** seuls deux contrôles ont une portée scientifique ou de
sécurité. Les contrôles sur l'UTF-8, les accents et les labels relèvent de
l'édition.

(c) **Condensation** de « Frontière d'industrialisation » (7.9), l. 105–113.
Texte actuel exact :
```latex
\section{Frontière d'industrialisation}

Le passage du prototype vers une exploitation en production demanderait plusieurs mécanismes qui n'ont pas été évalués dans ce mémoire. Parmi eux figurent TLS, la gestion des secrets, le contrôle d'accès, une journalisation protégée contre l'altération, la réplication de Redis, les tests de partition réseau, les sauvegardes, la reprise après sinistre, la surveillance continue et une politique de rétention adaptée.

Une orchestration par conteneurs pourrait simplifier le déploiement et la gestion des composants. Elle ne résoudrait cependant pas, à elle seule, les questions de validité prédictive ou de généralisation des modèles.

La montée en charge devrait également être étudiée avec des tâches d'inférence représentatives, sur des durées plus longues et en introduisant volontairement des pannes du transport. Les objectifs de latence, de disponibilité et de reprise devraient être définis avant ces campagnes afin de disposer de critères d'acceptation explicites.

Tant que ces validations ne sont pas réalisées, Ariel Logminer doit être considéré comme un prototype de laboratoire et non comme une plateforme industrielle.
```
Proposé :
```latex
\section{Frontière d'industrialisation}

Les mécanismes d'exploitation non évalués sont recensés à la section~\ref{sec:limites}. Une orchestration par conteneurs simplifierait le déploiement sans résoudre les questions de validité prédictive. Une étude de montée en charge devrait définir au préalable ses objectifs de latence, de disponibilité et de reprise, puis utiliser des tâches d'inférence représentatives, des durées plus longues et des pannes injectées du transport.
```

### B.11 — Allègement de la conclusion

(a) « Apports scientifiques et techniques », l. 92. **Texte actuel exact :**
```latex
Sur le plan architectural, \texttt{MultiTaskIntelligentAgent} matérialise les propriétés du modèle proposé : capacités déclarées, état, mémoire, pluralité de handlers et poursuite bornée d'objectifs. \texttt{ActionOutcome}, \texttt{GoalState} et \texttt{AutonomyLimits} rendent explicites l'enchaînement, la persistance et les garde-fous. Le protocole Contract Net rend les étapes d'attribution et de délégation visibles, tandis que les bus local et Redis séparent la logique métier du mécanisme de transport. L'idempotence est prise en charge par les magasins SQLite et Redis pour les effets instrumentés par les campagnes.
```
**Proposé :**
```latex
Sur le plan architectural, l'agent réunit capacités déclarées, état, mémoire, pluralité de handlers et poursuite bornée d'objectifs, avec des garde-fous explicites. Le protocole Contract Net rend visibles l'attribution et la délégation, le transport est séparé de la logique métier, et les effets instrumentés sont protégés contre la réexécution.
```
**Justification :** les noms de classes relèvent du chapitre 3.

(b) « Perspectives », l. 112–118 : le troisième paragraphe (gouvernance des
modèles) reprend presque mot pour mot le 6.8. **Texte actuel exact :**
```latex
La gouvernance des modèles constitue une deuxième perspective importante. Une campagne dédiée pourrait utiliser des candidats volontairement meilleurs et moins bons, un jeu de validation gelé et un test indépendant. Chaque candidat serait évalué, accepté ou rejeté selon la règle définie, puis son effet serait mesuré après la décision. Cette expérience permettrait de dépasser le constat d'une infrastructure disponible pour mesurer réellement le bénéfice du mécanisme.
```
**Proposé :**
```latex
La gouvernance des modèles constitue une deuxième perspective : la campagne décrite à la section~6.8 mesurerait le bénéfice réel des décisions de promotion et de rejet.
```
Si possible, remplacer `section~6.8` par un `\ref` en ajoutant
`\label{sec:priorites-prolongement}` sous `\section{Priorités de prolongement}`
dans `chapitre6_discussion.tex`.

---

## Partie C — Spécification formelle de la fonction d'utilité

Constats tirés du code (commit `35da3a9`,
`src/logminer/agents/intelligent_runtime.py`). Ils sont tous intégrés au
fichier proposé.

- Poids par défaut l. 60–65. Validation (poids ≥ 0, somme = 1 ± 1e-9)
  l. 67–72. Calcul dans `evaluate` l. 613–659 ; `score_task` l. 701–726 ;
  `_advance_goal` l. 926–1039. **Les numéros de ligne indiqués dans la
  consigne sont exacts.**
- **$M$ vaut toujours 1** pour une offre émise (l. 638) : la compatibilité de
  modèle n'est qu'un filtre de refus (`model_missing`).
- **$A$ et $L$ sont identiques**, $\max(0, 1-\rho)$ (l. 639–640).
- $T = 1/(1+\bar d)$, où $\bar d$ est en secondes et ne dépend d'aucune durée
  de référence. Elle vaut 1/2 sans mémoire ou sans historique.
- Avec les poids par défaut, toute offre vérifie
  $U = 0{,}20 + 0{,}30C + 0{,}20H + 0{,}25(1-\rho) + 0{,}05T$. Avec
  `max_parallel_tasks=1` (agents Redis,
  `scripts/logminer_redis_cnp_agent.py:79`), on obtient
  $U = 0{,}65 + 0{,}30C + 0{,}20H + 0{,}05T$.
- `minimum_utility` vaut 0 par défaut et n'est pas transmis par
  `scripts/logminer_redis_cnp_agent.py` : le refus `low_expected_utility` est
  inactif dans les campagnes Redis.
- Les messages `FEEDBACK` ne mettent pas à jour la mémoire (l. 215–216 du
  script agent). La mise à jour se fait par `learn()` après exécution.
- La tâche déléguée par `pursue_goal` est `pending[0]` (l. 945), sans que $U$
  intervienne dans ce choix.

### C.1 — Insertion de la spécification

**Fichier :** `chapters/chapitre4_implementation.tex` (chapitre 3 du PDF),
section « Implémentation des agents ».
**Insertion** après la l. 51 (paragraphe se terminant par
`… pour les tâches non exécutables localement.`), avant
`\section{Idempotence et reprise}` : contenu de
`revision_reports/agent_7/latex/spec_utilite.tex` (sous-section
`\label{sec:spec-utilite}`, tableau `tab:spec-utilite`).
**Justification :** le jury demande une définition opérationnelle de chaque
composante. Le texte actuel ne donne que la formule et $H$.

### C.2 — Chapitre 2 (Modèle), renvoi

**Fichier :** `chapters/chapitre3_modele_propose.tex`, l. 447–449.
**Texte actuel exact :**
```latex
avec des composantes bornées entre 0 et 1. La fiabilité historique est calculée par
$H_i=(s_i+1)/(s_i+f_i+2)$. Les poids sont configurables et fixés avant les campagnes ;
ils ne sont pas appris et ne sont pas présentés comme optimaux.
```
**Proposé :**
```latex
avec des composantes bornées entre 0 et 1, où $C$ désigne la confiance de capacité,
$H$ la fiabilité historique, $M$ la compatibilité de modèle, $A$ la disponibilité,
$L$ la charge et $T$ la latence observée. Les poids sont configurables et fixés avant
les campagnes ; ils ne sont pas appris et ne sont pas présentés comme optimaux. Le
calcul exact de chaque composante, les règles de refus et l'usage de $U$ dans le
Contract Net et la poursuite d'objectifs sont spécifiés à la
section~\ref{sec:spec-utilite}.
```
**Justification :** les lettres n'étaient définies nulle part. La formule de
$H$ est déplacée vers la spécification, ce qui évite un doublon avec
l'introduction.

### C.3 — Introduction, renvoi

**Fichier :** `chapters/chapitre1_introduction.tex`, l. 78.
**Texte actuel exact :**
```latex
Les poids sont fixés avant les campagnes expérimentales. Ils constituent des paramètres de fonctionnement et ne sont pas présentés comme une combinaison optimale.
```
**Proposé :**
```latex
Les poids sont fixés avant les campagnes expérimentales. Ils constituent des paramètres de fonctionnement et ne sont pas présentés comme une combinaison optimale ; leur mise en œuvre est spécifiée à la section~\ref{sec:spec-utilite}.
```

### C.4 — Annexe A.2, sémantique de `FEEDBACK` (correction factuelle)

**Fichier :** `chapters/annexes.tex`, l. 40.
**Texte actuel exact :**
```latex
\texttt{FEEDBACK} & Retour utilisable par la mémoire de l’agent. \\
```
**Proposé :**
```latex
\texttt{FEEDBACK} & Notification de l’issue au contractant ; la mémoire de l’agent est mise à jour localement après exécution, et non à partir de ce message. \\
```
**Justification :** voir `contract_net.py:219–231` et
`scripts/logminer_redis_cnp_agent.py:215–216` ; `learn()` est appelé dans
`execute_task` (`intelligent_runtime.py:822`).

### C.5 — Observations sur le code (aucune modification proposée dans le mémoire)

1. `evaluate`, l. 630–633 : si `required_capability` désigne une capacité
   existante qui ne supporte pas `task_type`, `can_handle` réussit (il
   compare le nom seulement, l. 580–581) mais `matching` est vide, et
   `max()` lève `ValueError`. Il s'agit d'un cas limite non couvert par les
   tests.
2. `execute_task`, l. 768 : une capacité déclarée sans handler correspondant
   produit une `KeyError`, convertie en résultat `error` (l. 806–819).
3. `contract_net.py:149` interroge les agents dans l'ordre lexicographique.
   L'égalité d'utilité est départagée par l'identifiant (l. 171) : à utilité
   égale, l'agent de plus petit identifiant est toujours favorisé.

---

## Partie D — Déclaration d'usage de l'IA

**Déclaration actuelle :** `frontmatter/declaration_ia.tex` (incluse par
`main.tex:270`). Elle est générique : aucun outil, aucune période, aucune
partie précise, aucun mode de vérification concret.

**Proposé :** remplacer intégralement le fichier par
`revision_reports/agent_7/latex/declaration_ia.tex`. Ce fichier contient un
tableau des outils, les parties concernées, la nature de l'aide, le mode de
vérification et la responsabilité.

Indices factuels utilisés, sans extrapolation :
- configuration d'OpenAI Codex dans le dépôt (`.codex/`, `AGENTS.md`) ;
- notes de travail `Workflow usage modèle GPT.txt` et `Prompt pour Luna.txt`
  (outil « Luna » non identifié) ;
- présente révision réalisée avec Claude Code (Anthropic), modèle Claude
  Opus, rapports dans `revision_reports/agent_*/`.

Tous les autres éléments sont des champs `[À COMPLÉTER PAR L'AUTEUR]`.
**Aucun champ entre crochets ne doit subsister dans le PDF déposé.**

---

## Observations hors périmètre (à transmettre)

1. **PR-AUC de HistGradientBoosting** : le résumé indique $0{,}567697$, alors
   que `cicids_model_candidates_summary.csv` (SHA-256 `4EDA14B9…`) donne
   `pr_auc_mean = 0.5690020372…`. L'artefact source de $0{,}567697$ n'a pas
   été localisé : la recherche a été interrompue pour éviter un parcours
   lourd de `data/`. Ce point est peut-être traité par l'agent 1, §6
   (« écart d'agrégation »).
2. **Chapitre 7, l. 20** : il présente la campagne multi-VM comme relevant de
   `phase_multi_agent`. Corrigé en A.2.
3. **Générateur de figures** : il produit encore
   `fig_multi_agent_task_distribution.png` à partir du run court
   `multivm_cnp_20260909T202632Z_37592` (l. 225–229 du script). Vérifier que
   cette figure n'est plus citée si le texte bascule sur la campagne
   d'endurance (agent 1).
