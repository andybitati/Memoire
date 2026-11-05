# PATCH NOTES — Agent 3, distribution et architecture

**Effort estimé d'intégration :** 2 à 3 heures pour le texte (nouvelle sous-section 5.x, reformulation de l'endurance, ligne A.2).

**Blocages et réserves :**

1. Le run `agent3_access_audit_20261104` (BLOCKERS.json) est **caduc** : VM et Redis ont été démarrés ensuite. Cause technique résiduelle corrigée : Debian n'a que l'interface host-only (192.168.56.102) ; l'URL invitée est donc `redis://192.168.56.1:6379/0` et non `10.0.2.2`. Le lancement passe par `guestcontrol start` (détaché).
2. La campagne HDFS distribuée transporte des **scores figés** : les VM appliquent le seuil, elles ne rejouent ni Drain3 ni le calcul du score. Elle valide la chaîne détection → décision distribuée, pas un parsing distribué.
3. **Toutes les tâches HDFS ont été attribuées à Debian (2 000/0).** Les deux agents ont le même profil (`hdfs-equal-confidence`) et proposent la même utilité, 0,845, à chaque appel d'offres ; le coordinateur départage par ordre lexicographique (`src/logminer/agents/redis_contract_net.py:234`, `sorted(..., key=(-utilité, agent_id))`). Comme chaque négociation est séquentielle, la charge `L` reste nulle au moment de l'offre et ne départage jamais. Ce résultat doit être rapporté tel quel.
4. **Saturation exécutée** (`agent3_saturation_multivm_20261104T142325Z`) avec un producteur en boucle ouverte et 32 coordinateurs concurrents, mais avec 3 répétitions et des débits de 1 à 64 tâches/s au lieu des 10 répétitions et 0,5–32 tâches/s de `PROTOCOL_CONFIG.json` (durée bornée). Le coude se situe entre 8 et 16 tâches/s. Le goulot n'est pas isolé : l'attente côté coordinateur domine, mais la boucle mono-thread de l'agent Debian, qui remporte presque toutes les tâches, y contribue probablement ; aucune instrumentation côté VM ne permet de trancher.
5. **Panne appariée A/B/C/D exécutée** (`agent3_paired_failure_abcd_20261104T141803Z`), en processus local et non sur Redis/VM. Elle **contredit en partie** la lecture « l'architecture à agents est plus robuste » : A et B dupliquent l'effet à chaque répétition, C et D jamais, mais A et B dotés du même magasin d'idempotence (ablation A+I, B+I) n'en dupliquent pas non plus. Le gain provient du magasin d'idempotence, que l'architecture C/D intègre, et non du Contract Net en soi. Statut proposé pour H2 : PARTIELLEMENT SOUTENUE (voir §5).

## Registre des preuves

| Élément | `run_id` | Source |
|---|---|---|
| HDFS via CNP sur deux VM | `hdfs_multivm_cnp_20261104T135345Z` | `revision_reports/agent_3/hdfs_multivm_cnp_20261104T135345Z__hdfs_multivm_summary.json`, `…__hdfs_multivm_tasks.csv` |
| Scores HDFS figés (entrée) | `ds_hdfs_block_20260910T081756Z` | `experiments/phase_final_scientific_consolidation/processed/hdfs_test_block_frozen_mean_scores.csv` |
| Référence centralisée, mêmes blocs | — | `experiments/phase_final_scientific_consolidation/aggregated/hdfs_block_robustness_summary.json` (F1 0,892308) |
| Endurance multi-VM | `cnp_endurance_multivm_20260918T130822Z` | `experiments/phase_cnp_endurance/raw/cnp_endurance_multivm_20260918T130822Z__task_metrics.csv` |
| Profils de capacité | — | `scripts/logminer_redis_cnp_agent.py:28-32` |

## Résultats nouveaux

### HDFS distribué (`hdfs_multivm_cnp_20261104T135345Z`)

- Topologie : coordinateur `andy-aaron` (hôte), Redis 7.4 sur l'hôte ; `debian-alpha` (hôte `andy`, Python 3.13.5) et `ubuntu-beta` (hôte `andy-VirtualBox`, Python 3.8.10), deux hôtes distincts vérifiés au registre.
- 2 000/2 000 blocs traités (29 positifs), seuil gelé 1,2729429339548877 (agrégateur `mean`).
- TP 29, FP 7, TN 1 964, FN 0 ; précision 0,805556, rappel 1,000000, F1 0,892308.
- Contrôle d'équivalence : recalcul centralisé sur le même CSV et le même seuil → 29/7/1 964/0, F1 identique. La distribution n'altère pas les prédictions.
- Durée 134,02 s ; débit 14,92 blocs/s (débit **atteint**, négociation séquentielle) ; latence moyenne 66,87 ms, médiane 57,69 ms, p95 104,23 ms, p99 236,23 ms.
- Répartition : `debian-alpha` 2 000, `ubuntu-beta` 0 (cf. réserve 3).

### Explication de la répartition 451 / 1 349 de l'endurance

Décompte par type de tâche et vainqueur dans `…130822Z__task_metrics.csv` :

| Type | Debian (`alpha`) | Ubuntu (`beta`) |
|---|---|---|
| `parse.synthetic` | 450 | 1 |
| `route.synthetic` | 1 | 449 |
| `detect.synthetic` | 0 | 450 |
| `correlate.synthetic` | 0 | 450 |

Les quatre types sont soumis en rotation (`scripts/run_cnp_endurance_multivm.py:286`). Les confiances configurées sont `alpha = (0,95 ; 0,82 ; 0,70 ; 0,72)` et `beta = (0,78 ; 0,96 ; 0,88 ; 0,82)` pour (parse, route, detect, correlate). Debian n'est favorisée que sur `parse` : la fonction d'utilité attribue donc un quart des tâches à Debian. Les deux exceptions correspondent à la panne contrôlée et à sa réattribution. **La version de Python ne joue aucun rôle observable** ; la charge non plus (une tâche toutes les 2 s, durée de traitement de quelques dizaines de ms).

## 1. Endurance : charge offerte et répartition

**Fichier :** `ARIEL_LOGMINER_MEMOIRE_FINAL/chapters/chapitre5_resultats.tex` — section « Campagne Contract Net multi-VM », sous-section « Résultats »

**Texte actuel exact :**

```latex
La durée observée atteint $3\,605{,}110$~s pour une cible de $3\,600$~s. Les $1\,800$ tâches planifiées se terminent toutes avec succès, soit un débit moyen de $0{,}499291$ tâche/s. La latence moyenne vaut $88{,}250280$~ms, la médiane $53{,}983$~ms, le p95 $156{,}3017$~ms et le p99 $836{,}72528$~ms.
```

**Texte proposé :**

```latex
La durée observée atteint $3\,605{,}110$~s pour une cible de $3\,600$~s. Les $1\,800$ tâches planifiées se terminent toutes avec succès. Le débit de $0{,}499291$ tâche/s correspond à la charge offerte, une tâche toutes les deux secondes : il ne mesure pas une capacité maximale. La latence moyenne vaut $88{,}250280$~ms, la médiane $53{,}983$~ms, le p95 $156{,}3017$~ms et le p99 $836{,}72528$~ms.

La répartition de 451 tâches pour Debian et $1\,349$ pour Ubuntu découle de la fonction d'utilité et des profils de capacité configurés. Les quatre types de tâches sont soumis en rotation ; le profil de Debian a la confiance la plus élevée pour l'analyse syntaxique ($0{,}95$ contre $0{,}78$), celui d'Ubuntu pour le routage, la détection et la corrélation. Le décompte par type confirme cette règle : Debian remporte 450 tâches d'analyse syntaxique, Ubuntu 449 à 450 tâches de chacun des trois autres types ; les deux exceptions relèvent du scénario de panne. Ni la version de Python ni la charge n'expliquent donc cette répartition.
```

**Et dans le tableau `tab:cnp-endurance` :**

```latex
Débit moyen & $0{,}499291$ tâche/s \\
```
→
```latex
Charge offerte (débit observé) & $0{,}499291$ tâche/s \\
```

**Preuve :** `run_id=cnp_endurance_multivm_20260918T130822Z`, `task_metrics.csv` ; `scripts/logminer_redis_cnp_agent.py:28-32`.

## 2. Nouvelle sous-section : détection HDFS en mode distribué

**Fichier :** `chapitre5_resultats.tex`, insérer avant `\section{Corrélation d’incidents}` (après le paragraphe sur Redis point central).

**Texte proposé :**

```latex
\subsection{Détection HDFS en mode distribué}

Le run \texttt{hdfs\_multivm\_cnp\_20261104T135345Z} fait passer par le Contract Net les $2\,000$ blocs HDFS de test du protocole \texttt{ds\_hdfs\_block\_20260910T081756Z}, dont 29 positifs. Chaque tâche transporte l'identifiant du bloc, son étiquette et son score moyen calculé avec l'état Drain3 gelé ; l'agent attributaire applique le seuil figé $1{,}272943$ et renvoie sa prédiction. Les scores ne sont pas recalculés dans les machines virtuelles : l'expérience évalue la chaîne de décision distribuée, non un parsing distribué.

Les $2\,000$ tâches aboutissent. La matrice de confusion vaut TP~$=29$, FP~$=7$, TN~$=1\,964$, FN~$=0$, soit une précision de $0{,}805556$, un rappel de $1$ et un F1 de $0{,}892308$, identiques au calcul centralisé sur les mêmes scores. La latence de négociation est de $57{,}69$~ms en médiane, $104{,}23$~ms au p95 et $236{,}23$~ms au p99, pour un débit atteint de $14{,}92$ blocs/s en négociation séquentielle.

Toutes les tâches sont attribuées à \texttt{debian-alpha}. Les deux agents ayant le même profil, ils proposent une utilité identique ($0{,}845$) et le coordinateur départage par ordre d'identifiant ; la charge, nulle au moment de chaque appel d'offres séquentiel, ne les distingue pas. Cette expérience démontre donc que la détection traverse le protocole sans perte ni altération des prédictions, mais pas un partage effectif de la charge de détection entre les deux hôtes. Un départage aléatoire ou fondé sur l'historique, ou des appels d'offres concurrents, seraient nécessaires pour l'établir.
```

**Preuve :** `run_id=hdfs_multivm_cnp_20261104T135345Z`, summary JSON et CSV des tâches.

## 3. Annexe A.2 : matrice résultats–preuves

**Fichier :** `chapters/annexes.tex` — ajouter après la ligne « Endurance CNP multi-VM » :

```latex
Détection HDFS via CNP multi-VM & $2\,000/2\,000$ ; F1 $0{,}892308$ ; Debian $2\,000$, Ubuntu 0 & \texttt{hdfs\_multivm\_cnp\_20261104T135345Z\_\_hdfs\_multivm\_summary.json} \\
Saturation CNP multi-VM & coude entre 8 et 16 t/s ; plafond 8,4--15,0 t/s & \texttt{agent3\_saturation\_multivm\_20261104T142325Z\_\_saturation\_summary.json} \\
Panne appariée A/B/C/D & doublons A 10, B 10, C 0, D 0 ; A+I, B+I 0 & \texttt{agent3\_paired\_failure\_abcd\_20261104T141803Z\_\_summary.json} \\
```

## Saturation (`agent3_saturation_multivm_20261104T142325Z`)

Tâches `hdfs.block.evaluate` sur les scores HDFS figés, fenêtre de 30 s par palier, latence mesurée depuis l'instant planifié. Plage sur les trois répétitions :

| Débit offert (t/s) | Débit atteint (t/s) | Latence p50 (ms) | Latence p95 (ms) | Échecs | Tâches Ubuntu |
|---|---|---|---|---|---|
| 1 | 1,01–1,03 | 73,8–215,3 | 244,1–2 128,8 | 0 | 0 |
| 2 | 2,02–2,03 | 64,5–104,1 | 180,0–430,2 | 0 | 0 |
| 4 | 4,02 | 75,5–92,3 | 149,5–348,1 | 0 | 0 |
| 8 | 7,20–8,01 | 81,2–181,8 | 250,5–3 882,8 | 0 | 0 |
| 16 | 8,44–10,85 | 6 618,5–17 684,7 | 14 420,3–26 818,1 | 1 | 0–5 |
| 32 | 9,07–15,04 | 17 723,0–48 329,6 | 32 362,6–74 095,3 | 1 | 0–71 |
| 64 | 8,99–12,68 | 65 207,0–81 755,2 | 116 231,1–168 150,0 | 1 | 5–32 |

Source : `revision_reports/agent_3/agent3_saturation_multivm_20261104T142325Z__saturation_summary.json` et `__saturation_tasks.csv`. Au total, 3 échecs (expiration de délai) sur 10 080 tâches, aucune perte silencieuse.

**Texte proposé (chapitre 5, après le tableau `tab:cnp-endurance`) :**

```latex
Un test de saturation en boucle ouverte (\texttt{agent3\_saturation\_multivm\_20261104T142325Z}) soumet des tâches de décision HDFS à des débits croissants de 1 à 64 tâches/s, sur des fenêtres de 30~s répétées trois fois. Jusqu'à 8 tâches/s, le débit atteint suit la charge offerte et la latence médiane reste inférieure à 0,2~s. À partir de 16 tâches/s, le débit atteint plafonne entre $8{,}4$ et $15{,}0$ tâches/s et la latence p95 croît jusqu'à plus de 100~s, sous l'effet de l'attente côté coordinateur. La capacité soutenue de cette topologie se situe donc entre 8 et 16 tâches/s ; la charge de $0{,}5$ tâche/s de l'endurance en est très éloignée. Trois tâches sur $10\,080$ échouent par expiration de délai. L'agent Ubuntu ne reçoit des tâches qu'en saturation, lorsque l'agent Debian ne répond plus dans le délai imparti.
```

## Panne contrôlée appariée (`agent3_paired_failure_abcd_20261104T141803Z`)

Protocole : charge appariée de 40 tâches (`generate_workload`, graines 42 à 51, 10 répétitions par architecture) ; panne injectée sur la tâche d'indice 9 après l'effet durable et sa persistance, avant `RESULT` ; rejeu unique sur un worker vivant (redémarrage pour A). Délai de détection commun, non simulé, exclu de la latence. C et D utilisent le vrai `ContractNetCoordinator` et les agents `alpha`, `beta`, `gamma` du benchmark ; l'agent défaillant est retiré du registre.

| Arch. | Magasin d'idempotence | Pertes | Effets dupliqués | Reprises | Rejeux idempotents | Latence de reprise médiane / max (ms) |
|---|---|---|---|---|---|---|
| A | non | 0 | 10 | 10/10 | 0 | 0,022 / 0,027 |
| B | non | 0 | 10 | 10/10 | 0 | 0,021 / 0,055 |
| C | oui | 0 | 0 | 10/10 | 10 | 5,819 / 18,286 |
| D | oui | 0 | 0 | 10/10 | 10 | 5,864 / 8,423 |
| A+I | oui | 0 | 0 | 10/10 | 10 | 5,070 / 10,782 |
| B+I | oui | 0 | 0 | 10/10 | 10 | 4,716 / 5,864 |

Source : `revision_reports/agent_3/agent3_paired_failure_abcd_20261104T141803Z__summary.json` et `__runs.csv`.

## 4bis. Chapitre 5 : comparaison de la panne contrôlée

**Fichier :** `chapitre5_resultats.tex`, à insérer dans la section consacrée à la comparaison agents/monolithe (après le résultat de reprise `ma_20260909T160812Z_34016`).

**Texte proposé :**

```latex
Pour comparer la robustesse, la même panne est rejouée sur les quatre architectures (\texttt{agent3\_paired\_failure\_abcd\_20261104T141803Z}). Sur une charge appariée de 40 tâches et dix graines, le worker s'arrête après l'effet durable et sa persistance, avant l'émission du résultat ; la tâche est rejouée une fois sur un worker vivant. Aucune architecture ne perd de tâche. Le monolithe A et les workers centralisés B dupliquent l'effet dans les dix répétitions, alors que les architectures C et D, qui partagent un magasin d'idempotence, rejouent le résultat persistant sans effet dupliqué, pour une latence de reprise médiane d'environ 6~ms. Une ablation dotant A et B du même magasin supprime également les doublons. L'avantage observé provient donc du mécanisme d'idempotence intégré à l'architecture par agents, et non de la négociation Contract Net elle-même.
```

## 5. Chapitre 7 (conclusion) — statut de H2

En cohérence avec l'agent 1 (§10), remplacer pour H2 le statut « NON TRANCHÉE » par :

```latex
H2 & Reprise sans perte ni doublon, comparée à A/B. &
PARTIELLEMENT SOUTENUE &
Sous la même panne, C et D reprennent sans perte ni doublon, contrairement à A et B qui dupliquent l'effet ; une ablation montre que l'avantage provient du magasin d'idempotence, transposable à A et B. \\
```

**Preuve :** `run_id=agent3_paired_failure_abcd_20261104T141803Z`.

## 6. Chapitre 7 (reproductibilité), ligne 77

**Fichier :** `chapters/chapitre7_reproductibilite_deploiement.tex`

**Texte actuel exact :**

```latex
Un partage égal des tâches n'est pas une condition de validité : le run observé attribue 451 tâches à Debian et $1\,349$ à Ubuntu. L'ordonnancement peut varier d'une exécution à l'autre.
```

**Texte proposé :**

```latex
Un partage égal des tâches n'est pas une condition de validité : la répartition observée, 451 tâches pour Debian et $1\,349$ pour Ubuntu, découle des profils de capacité configurés (section~\ref{sec:cnp-multivm}). Elle est reproductible tant que ces profils et la rotation des types de tâches sont conservés.
```

*(Ajouter `\label{sec:cnp-multivm}` après `\section{Campagne Contract Net multi-VM}` au chapitre 5.)*
