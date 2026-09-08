# Rapport expérimental final pour Luna

Ce document est un dossier de preuve et de consignes. Il ne constitue pas une réécriture du mémoire. Toute formulation future doit rester dans les limites indiquées ici et dans `final_claim_evidence_matrix.md`.

# 1. Environnement final

Environnement principal gelé le 7 septembre 2026:

- commit de départ: `37bccf083f3c8e92a11377cf758cf1e9e183dee9`;
- OS: `Windows-10-10.0.26200-SP0`, version `10.0.26200`;
- Python: `3.11.9`, 64 bits;
- environnement virtuel principal: aucun;
- CPU: `Intel64 Family 6 Model 142 Stepping 10, GenuineIntel`;
- 4 cœurs physiques, 8 processeurs logiques;
- RAM: `8 425 529 344` octets;
- scikit-learn `1.7.2`, pandas `2.3.2`, NumPy `2.2.3`, SciPy `1.16.1`, psutil `7.2.2`, joblib `1.5.2`, client Redis Python `8.0.1`.

Drain3 a été isolé dans `.venv-final-experiments` avec Drain3 `0.9.11` et cachetools `4.2.1`. Cet environnement utilise les paquets scientifiques système et ne doit pas exécuter Streamlit. L'environnement principal a été restauré avec cachetools `7.1.2`.

Version GPU: `INFORMATION À VÉRIFIER.`

Version du serveur Redis: `INFORMATION À VÉRIFIER.`

Preuve: `environment_final_experiments.json`, E0008 et E0009.

# 2. Datasets réellement utilisés

| Dataset/corpus | Usage | Unité | Statut de provenance |
| --- | --- | --- | --- |
| 8 CSV locaux attribués à CICIDS2017 | Phases 1, 2 et préparation phase 4 | Flux tabulaire | Copies locales hashées; provenance officielle non démontrée |
| HDFS.log + anomaly_label.csv | Phase 3 et voie pipeline phase 5/6 | Événement portant un `block_id`; labels au bloc | Copies locales hashées; provenance officielle non démontrée |
| BGL.log | Phase 3 et voie pipeline phase 5/6 | Ligne de log | Copie locale hashée; provenance officielle non démontrée |
| Application.evtx | Phase 5/6 | Enregistrement EVTX | Échantillon local |
| linux_auth_logs_labeled.csv | Phase 5/6 | Ligne CSV | Corpus local étiqueté |
| 06-20-October.csv | Phase 5/6 | Ligne d'export Wazuh/Elastic | Export local |
| Linux_2k.log | Phase 5/6 | Ligne de log | Corpus local |
| apache_access.log | Phase 5/6 | Ligne Apache | Fixture synthétique existant d'une seule ligne |
| Corpus dérivé de neuf sources | Phase 6 | Fichier/chunk de 100 lignes, sauf Apache N=1 | Dérivé local; chunks non indépendants |
| 19 événements synthétiques contrôlés | Phase 8 | Événement; évaluation sur 120 paires anomales | Créé explicitement pour tester les règles du corrélateur |
| `UNSWNB15.zip` historique | Audit P0 seulement; exclu des nouvelles campagnes | Dix CSV DDoS dérivés | Ni UNSW-NB15 officiel ni CIC-DDoS2019 officiel démontré |

La provenance officielle de toutes les copies prioritaires du manifeste est: `INFORMATION À VÉRIFIER.`

# 3. Manifestes et hashes

Le manifeste final contient 11 entrées. Ces SHA-256 identifient les copies locales; ils ne prouvent pas leur provenance officielle.

| Fichier | Lignes | Colonnes | SHA-256 |
| --- | ---: | ---: | --- |
| Friday DDoS | 225 745 | 79 | `6ff1580f5f81c0ae28a26f7631721018577f5f7c5e0feac28b795fcfe7b411ee` |
| Friday PortScan | 286 467 | 79 | `ca1824c51bfbb7b3c72290a11be04366ba8815878c6a1cc5c44cb1cee269e99b` |
| Friday Morning | 191 033 | 79 | `53a41c24d570ea83b7ac55b2e94df94e7a8216aeb80a2af0246b6bc8bb543000` |
| Monday | 529 918 | 79 | `852c4beb34eda186f32561fa79df7a0747e92e1a6535b01270820dd9ffe17f34` |
| Thursday Infilteration | 288 602 | 79 | `6bcda3857c2504676034e3ea57762d38393cc734cb377a726bd5cb153961b1b5` |
| Thursday WebAttacks | 170 366 | 79 | `d67066211fb1689c78406f1506f4c44704ecb92088353d5c96d96d6474eb819d` |
| Tuesday | 445 909 | 79 | `52b8692ae8c7d2ed04671fe2b98335693c0a92c7ab157d8c8b534d6523080851` |
| Wednesday | 692 703 | 79 | `893c27dc968bf7a8adef1689f90be55ca4a4dc3088fb63d6ff247ac56856df2a` |
| HDFS anomaly_label.csv | 575 061 | 2 | `1c711ed6c8848fc3243fb4d092f172f31d128c8a6ec7f26ebba72ab931885ed8` |
| HDFS.log | 11 175 629 | 1 | `0783096174d7832c618337f9609e06e04abd86ddd7089b3c12b407e63bfebc52` |
| BGL.log | 4 747 963 | 1 | `666130b15ef44eb32fd02bd053e6c6e007c37696b5e7e8b9d8e45b729876a5d2` |

Hashes Drain3 finaux:

- HDFS: `18bc825effd29a8c4cd957d41d9a4502a2e47f905738dd6b193017056905ebd2`;
- BGL: `43ef590469a379daf21f7b644b3fc2592ca66e74643353254e60659baf27db82`.

Hash du test DDoS gelé phase 4: `23019860997b8071e0922c52c1710e10b017adcc20f53121872e3875dc5a3126`.

# 4. Expériences réalisées

| Phase | Expérience | Statut | Runs/résultats | Conclusion courte |
| ---: | --- | --- | ---: | --- |
| 0 | Environnement, manifeste, runner | TERMINÉE | 11 fichiers | Reproductibilité locale gelée |
| 1 | CICIDS holdouts multi-seeds + contrôle random | TERMINÉE | 30/30 | Forte dépendance au split/scénario |
| 2 | Cinq modèles CICIDS multi-seeds | TERMINÉE | 125/125 | LR meilleur F1 macro seulement |
| 3 | HDFS/BGL strict Drain3 train-only | TERMINÉE | 36/36 | Résultats indépendants du test pour le réglage |
| 4 | Mise à jour contrôlée end-to-end | TERMINÉE | 3/3 | Promotion et deux rejets réellement observés |
| 5 | Validation multiformat | TERMINÉE | 8/8 voies | Fonctionnelle mais partielle |
| 6 | Routeur réel | TERMINÉE | 81/81 | 80 corrects; pas de preuve de gain prédictif |
| 7 | Résilience complémentaire | SKIPPED | 0 | Preuve existante suffisante pour avant traitement/ACK; fenêtre suivante non évaluée |
| 8 | Corrélation synthétique contrôlée | TERMINÉE | 1 run, 120 paires | F1 pairwise 0,812500; deux modes d'échec |
| 9 | Statistiques transversales | TERMINÉE | 228+4+20 lignes | Descriptif sans pseudo-réplication |
| 10 | Matrice affirmation→preuve | TERMINÉE | 31 affirmations | Frontières de preuve explicites |
| 11 | Hypothèses/questions | TERMINÉE | 5+6 | Statuts prudents établis |

Expériences antérieures retenues: trois campagnes multi-VM, ablation du routage, benchmark monolithique/agents. L'expérience historique `0,999965` est auditée mais exclue.

# 5. Protocoles complets

## 5.1 CICIDS phase 1

- Seeds: 42–46.
- Scénarios tenus hors entraînement: DDoS, PortScan, Bot, Infiltration, WebAttacks.
- Label: `BENIGN=0`, tout autre label=1.
- 78 caractéristiques numériques après exclusions des identifiants, IP, timestamp, label et index; non-finis remplacés par zéro; clipping `[-1e12, 1e12]`.
- Holdout: fichier/scénario complet exclu du train; maximum 8 000 observations par classe au train et 4 000 par classe au test; lecture de deux chunks de 100 000 lignes maximum par fichier.
- Random control: pool fixe de 12 000 lignes par classe, puis split stratifié 2/3–1/3 pour chaque seed; pool seed 2026.
- RandomForest: 100 arbres, profondeur 28, `min_samples_leaf=2`, `class_weight=balanced`, `n_jobs=1`.
- Aucun seuil ajusté sur le test.

## 5.2 Comparaison de modèles phase 2

Même échantillonnage, mêmes scénarios et seeds que la phase 1. Candidats: RandomForest, ExtraTrees, HistGradientBoosting, LogisticRegression et SGDLogistic. Les deux modèles linéaires utilisent un `StandardScaler` ajusté sur le train uniquement. Métriques: précision, rappel, F1, PR-AUC, MCC, FPR, matrice de confusion et temps.

## 5.3 HDFS/BGL strict phase 3

- Ranges chronologiques disjoints: train 0–60 %, validation 60–80 %, test 80–100 %; échantillons centrés respectivement à 0,3, 0,7 et 0,9.
- Volumes cibles avant filtrage: 50 000/20 000/20 000.
- HDFS observé: 50 000 train, 20 000 validation, 20 000 test, aucun `block_id` partagé après déduplication inter-partitions.
- BGL observé: 49 999 train, 17 764 validation, 19 908 test.
- Sélection des plages sans labels.
- Drain3 `0.9.11` ajusté uniquement au train, `sim_th=0,4`, profondeur 4, 100 enfants maximum, nombres paramétrés.
- Validation/test par `match(full_search_strategy='always')`, jamais `add_log_message`.
- Fenêtres passées de 30 minutes, état réinitialisé à chaque partition; fréquences template/source du train uniquement; scaler sur train normal uniquement.
- Seuil sélectionné sur validation par F1 maximal, départages FPR minimal, MCC maximal, seuil maximal; aucune prévalence ni distribution du test utilisée.
- Méthodes: IsolationForest, ZScore, IQR, Histogram, AutoencoderMLP, ensemble calibré train. Méthodes stochastiques seeds 42–46; méthodes déterministes N=1.

## 5.4 Mise à jour contrôlée phase 4

- Train DDoS: 16 000 lignes; évaluation gelée: 8 000; 78 features; prévalence 0,5.
- Trois copies isolées de modèles, aucun fichier sous `models/` modifié.
- Cas promotion: ExtraTrees courant contre RandomForest candidat.
- Cas rejet: RandomForest courant contre SGDLogistic candidat.
- Cas gain insuffisant: ExtraTrees courant contre LogisticRegression, `min_delta=0,02`.
- Pour chaque cas: entraînement réel du candidat, score courant/candidat sur le même test gelé, décision, audit, hashes courant avant/candidat/backup/après.

## 5.5 Validation multiformat phase 5

Huit voies du code existant, maximum 1 000 unités en ordre source, aucune duplication: Windows EVTX, Linux/auth tabulaire, Wazuh CSV, syslog, Apache, HDFS, BGL et réseau tabulaire. Mesures: brut, lu, parsé, normalisé, erreur, perdu, complétude de sept champs et conservation exacte du message si testable. Routage évalué séparément en phase 6.

## 5.6 Routeur réel phase 6

Neuf sources hashées; chunks de 100 lignes, noms neutres, Apache N=1; 81 fichiers. Vérité famille fixée avant routage. Appel direct de `agents.model_router.route_model`; enregistrement famille vraie/prédite, modèle, scores, raisons, marge, fallback, erreur et existence du modèle. `confidence` est une marge entière entre les deux meilleurs scores, pas une probabilité.

## 5.7 Résilience multi-VM retenue

Protocole exact transmissible au chapitre 5:

1. Hôte Windows avec PowerShell, VirtualBox et Docker; Redis `redis:7-alpine`, port 6379, AOF, `appendfsync everysec`, 512 MB, `noeviction`.
2. VM `Debian` et `Ubuntu` en NAT, accès invité `redis://10.0.2.2:6379/0`; accès hôte `redis://localhost:6379/0`.
3. Run principal `redis-vbox-1h-20260722153650`; stream `logminer:agent_tasks:vbox_1h:20260722153650`; groupe `logminer-intelligent-agents`.
4. Un worker par VM, parallélisme 1, `block-ms=1000`, `claim-idle-ms=1000`, durée configurée 3 720 s incluant 120 s de drain.
5. Pendant une cible de 3 600 s, lot de trois tâches toutes les 15 s: `discover.logs`, `parse.logs`, `route.model`; 175 lots observés, soit 525 entrées.
6. Relances supervisées nécessaires après interruptions `guestcontrol`; identités `debian-worker-1h-r2` et `ubuntu-worker-1h-r2` à signaler.
7. Vérification par `XINFO GROUPS`, `XLEN`, `XPENDING`; événements completed/failed conservés séparément.
8. Résultat: 525 enfilées, lues et acquittées par le groupe; lag final 0; pending final 0. Ne pas écrire 525 succès applicatifs.

Contrôles complémentaires: campagne équilibrée `redis-vbox-balanced-20260722145314`, 12/12 tâches uniques terminées; reprise `redis-vbox-recovery-20260722150924`, 1 tâche prise par Debian avant traitement/ACK puis reprise par Ubuntu, 3/3 terminées, pending 0.

Durée réelle de bout en bout et versions exactes Windows/Debian/Ubuntu: `INFORMATION À VÉRIFIER.`

## 5.8 Corrélation phase 8

Corpus pré-spécifié: 19 événements, 16 anomalies, six incidents vrais, trois bruits. Fenêtre fixe 15 minutes; huit clés réelles. Vérité dans un fichier séparé absent de l'entrée. Cas: groupes stables, séparation par hôte, incident traversant 10:15, deux incidents distincts indiscernables par les clés, bruit. Évaluation exhaustive des 120 paires.

## 5.9 Statistiques phase 9

CICIDS groupé par scénario–modèle; HDFS/BGL par dataset–méthode; N=5 pour stochastique, N=1 pour déterministe. Moyenne, écart-type échantillonnal, médiane, min, max et IC95 Student uniquement N≥2. Comparaisons de modèles descriptives sur cinq moyennes de scénarios. Aucun test inférentiel.

# 6. Résultats bruts importants

- Ledger append-only: `state/EXPERIMENT_LEDGER.csv`.
- CICIDS phase 1: `cicids_holdout_multiseed_raw.csv`, `cicids_random_multiseed_raw.csv`.
- CICIDS phase 2: `cicids_model_multiseed_raw.csv` et 125 JSON sous `phase_2/`.
- HDFS/BGL: `hdfs_strict_drain3_raw.csv`, `bgl_strict_drain3_raw.csv`, 36 JSON et états Drain3.
- Mise à jour: `phase_4/model_update_end_to_end_report.json`, rapports par cas, audit et rapport d'intégrité.
- Multiformat: `multiformat_validation_raw.csv`, complétude et échecs.
- Routeur: `router_evaluation_raw.csv` et matrice de confusion.
- Corrélation: entrée, vérité, incidents et 120 paires sous `phase_8/`.
- Statistiques: `transversal_repeated_statistics.csv`, effets scénario et évaluations uniques.
- Multi-VM: trois JSON `vbox_redis_*_campaign.json`.
- Benchmark architecture: `controlled_monolith_vs_agents.csv`.

# 7. Résultats agrégés

| Expérience | Résultat principal | N/portée |
| --- | --- | --- |
| CICIDS random RF | F1 `0,995142 ± 0,001013`; IC95 `[0,993884; 0,996400]` | 5 seeds |
| CICIDS holdout RF macro | F1 `0,157744` | 5 scénarios × 5 seeds |
| DDoS RF holdout | F1 `0,778774 ± 0,001342`; rappel `0,637700`; FP moyen 0 | 5 seeds |
| PortScan RF | F1 `0,009947`; rappel `0,005000`; PR-AUC `0,881982` | 5 seeds |
| Bot RF | F1/rappel 0; PR-AUC `0,322471` | 5 seeds; 1 966 attaques/test |
| Infiltration RF | F1/rappel 0 | 5 seeds; seulement 32 attaques/test |
| WebAttacks RF | F1/rappel 0; PR-AUC `0,654341` | 5 seeds; 2 180 attaques/test |
| Modèles CICIDS | LR F1 macro `0,233670`; MCC `0,186858`; HGB PR-AUC macro `0,567697` | 5 modèles × 5 scénarios × 5 seeds |
| HDFS strict Histogram | F1 `0,269307`, 68 TP, 319 FP sur 118 anomalies | N=1 déterministe |
| BGL strict Histogram | F1 `0,913698`, FPR `0,032016` | N=1 déterministe |
| Mise à jour | deltas `+0,067845`, `-0,063163`, `+0,009016<0,02` | 3 cas |
| Multiformat | 5 001 normalisées / 7 001; 2 000 perdues | 8 voies |
| Routeur | 80/81; exactitude `0,987654`; F1 macro union `0,883598` | 81 fichiers dérivés |
| Corrélation | précision `0,764706`; rappel `0,866667`; F1 `0,812500` | 120 paires |
| Multi-VM principal | 525 lues/acquittées; lag 0; pending 0 | 175 lots |
| Benchmark monolithe | 36,6815 s; 1,6357 tâche/s; CPU 121,339 %; RSS max 189,074 MiB | 60 tâches |
| Benchmark agents | 38,1803 s; 1,5715 tâche/s; CPU 165,746 %; RSS max 234,777 MiB | 60 tâches |
| Agents avec reprise | 39,3000 s; 1,5267 tâche/s; CPU 117,598 %; RSS max 189,395 MiB | 60 tâches |

# 8. Résultats majeurs

1. Le protocole de séparation domine fortement les scores CICIDS: random élevé, holdout par scénario faible et hétérogène.
2. La campagne multi-seeds confirme que cette chute n'est pas un accident d'une seed.
3. LogisticRegression relève le F1 macro à `0,233670`, mais ne domine ni tous les scénarios ni toutes les métriques.
4. Drain3 strict train-only ferme la fuite méthodologique; les résultats sont plus crédibles même lorsqu'ils sont faibles.
5. La mise à jour contrôlée est réellement exécutée de bout en bout avec intégrité vérifiée.
6. Le routeur réel fonctionne sur le corpus dérivé, mais l'ablation ne montre aucun gain prédictif systématique.
7. La preuve multi-VM est réelle au niveau laboratoire/transport, pas industrielle.
8. La corrélation synthétique révèle qu'un nombre correct d'incidents peut masquer simultanément fragmentation et fusion.

# 9. Résultats négatifs

| Hypothèse initiale | Observation | Soutenue ? | Enseignement | Conséquence mémoire |
| --- | --- | --- | --- | --- |
| Les agents améliorent le débit | 1,5715 contre 1,6357 tâche/s | Non à cette charge | L'orchestration a un coût | Conserver le surcoût |
| Le routage spécialisé améliore toujours le F1 | 1 delta positif minime, 2 négatifs | Non | Intérêt surtout architectural | Supprimer toute supériorité générale |
| Les modèles généralisent entre scénarios CICIDS | F1 nul ou quasi nul sur plusieurs holdouts | Non | Le split random est optimiste | Centrer la discussion sur généralisation |
| Cinq modèles résolvent Bot | Aucun TP | Non | Changer de modèle seul ne suffit pas | Rapporter l'échec complet |
| Le pipeline normalise HDFS/BGL | 0/1 000 chacun | Non | Parseurs courants incomplets | Dire validation multiformat partielle |
| Le brut est toujours conservé | 0/1 000 exact Windows/syslog | Non | Le contrat de conservation n'est pas général | Retirer la revendication |
| Le corrélateur évite fragmentation/fusion | 1 de chaque sur six vérités | Non | Fenêtre et clés imposent des limites | Inclure les modes d'échec |
| Un candidat supérieur est toujours promu | `+0,009016` rejeté sous `0,02` | Non, volontairement | Le seuil de gouvernance fonctionne | Présenter comme résultat fonctionnel positif |
| Résilience couvre la fenêtre traitement→ACK | Non testée | Non évaluée | Idempotence encore ouverte | Ajouter aux limites |

# 10. Résultats exploratoires

- Ancien HDFS/BGL Drain3: exploratoire, parce que Drain3 et des statistiques du test interviennent dans les features/réglages.
- Score historique `0,999965`: artefact reproductible en interne, mais corpus de provenance non démontrée; exclu des résultats scientifiques.
- Deltas de l'ablation UNSW: à conserver avec prudence car provenance UNSW fragile.
- Captures dashboard: preuves fonctionnelles visuelles, pas étude d'utilisabilité.
- Campagnes Redis locales longues autres que multi-VM: preuves d'endurance locale, pas haute disponibilité.

# 11. Résultats invalidés ou supprimés

- Supprimer `0,999965` des résumés, abstract, résultats, discussion, conclusion, tableaux et figures scientifiques.
- Ne l'attribuer ni à UNSW-NB15 officiel ni au CIC-DDoS2019 officiel.
- Ne pas présenter l'ancien HDFS/BGL comme validation indépendante.
- Ne pas présenter 525 entrées comme 525 succès applicatifs individuels.
- Ne pas présenter l'ablation du routage comme gain prédictif systématique.
- Ne pas utiliser les temps internes HDFS/BGL par méthode: chronométrage non comparable.

# 12. Affirmations désormais autorisées

- « Le prototype a été évalué sur des copies locales hashées; leur provenance officielle reste non démontrée. »
- « Le holdout par scénario CICIDS révèle une forte fragilité inter-scénarios persistante sur cinq seeds. »
- « LogisticRegression obtient le meilleur F1 macro parmi cinq candidats (`0,233670`), sans domination toutes métriques. »
- « Drain3 est ajusté sur le train uniquement, puis gelé pour validation et test dans le protocole strict. »
- « La procédure contrôlée de mise à jour est implémentée et testée fonctionnellement de bout en bout. »
- « La validation multiformat est fonctionnelle mais partielle. »
- « Le routeur attribue correctement 80/81 fichiers sur un corpus local dérivé. »
- « Aucun gain prédictif systématique du routage spécialisé n'est observé dans l'ablation. »
- « La campagne multi-VM constitue une preuve de laboratoire: 525 entrées lues/acquittées, lag et pending nuls. »
- « La corrélation est validée sur des scénarios synthétiques contrôlés, avec F1 pairwise `0,812500`. »
- « À 60 tâches, l'architecture agents n'améliore pas le débit face au monolithe. »

# 13. Affirmations interdites

- « F1 `0,999965` sur UNSW-NB15/CIC-DDoS2019 officiel. »
- « 525 tâches applicatives toutes réussies. »
- « Haute disponibilité », « scalabilité industrielle », « SOC distribué opérationnel » ou « multi-site ».
- « AgentMessage contient event_id/message_id/metadata ».
- « L'ancien HDFS/BGL est une validation train→test indépendante. »
- « LogisticRegression est universellement le meilleur modèle. »
- « Le routage spécialisé augmente systématiquement la performance. »
- « Robustesse universelle multiformat » ou « conservation intégrale de tout brut ».
- « Apprentissage continu autonome » ou « mise à jour en production ». 
- « Validation SOC réelle de la corrélation ».
- Toute significativité statistique transversale non calculée.

# 14. Statut de la contribution architecturale

Contribution principale: architecture logicielle modulaire reliant collecte, parsing, normalisation, routage, détection, corrélation, visualisation, mémoire, audit et bus. Le contrat métier et les enveloppes de transport sont identifiables. Des workers séparés et Redis Streams fonctionnent sur deux VM de laboratoire.

Niveau: PARTIELLEMENT SOUTENU à DÉMONTRÉ selon la sous-propriété. Modularité/traçabilité sont soutenues par le code et les artefacts; extensibilité reste principalement une propriété de conception; haute disponibilité et échelle industrielle ne sont pas démontrées.

Contrat exact `AgentMessage` à présenter au §3.14:

```text
AgentMessage(
  run_id,
  source,
  target,
  message_type,
  payload,
  status,
  timestamp
)
```

Il n'existe aucun champ direct `event_id`, `message_id` ou `metadata`. `run_id` corrèle une exécution. Toute métadonnée supplémentaire se trouve dans `payload`. Redis ajoute ses propres identifiants de stream pour le transport/ACK; l'enveloppe job Redis est distincte. MQTT sérialise le contrat mais n'ajoute pas un identifiant métier d'événement.

# 15. Statut de la contribution méthodologique

Contribution la plus solide: mise en évidence et correction de protocoles fragiles par séparation scénario/fichier, multi-seeds, scaler train-only, Drain3 train-only, validation séparée pour le seuil, test gelé, hashes, ledger append-only et conservation des échecs.

Niveau: DÉMONTRÉ dans le dépôt. La comparaison ancien/strict HDFS/BGL n'est toutefois pas une ablation causale, car plusieurs dimensions changent ensemble.

# 16. Statut de la contribution expérimentale

Contribution: ensemble de résultats positifs et négatifs traçables, 30 runs phase 1, 125 phase 2, 36 phase 3, trois cas phase 4, huit voies phase 5, 81 décisions phase 6 et une corrélation pairwise phase 8.

Niveau: OBSERVÉ/DÉMONTRÉ dans les protocoles locaux. Généralisation externe limitée par la provenance, les sous-échantillons, N=1 de certaines méthodes, la dépendance des chunks et l'absence de sites réels.

# 17. Statut de la contribution logicielle

| Élément | Statut exact |
| --- | --- |
| Pipeline principal | IMPLÉMENTÉ; testé fonctionnellement selon plusieurs voies |
| `AgentMessage` et bus local/Redis/MQTT | IMPLÉMENTÉS |
| Routeur réel | IMPLÉMENTÉ et ÉVALUÉ sur corpus dérivé |
| Corrélateur | IMPLÉMENTÉ et ÉVALUÉ sur scénarios synthétiques contrôlés |
| Mise à jour contrôlée | IMPLÉMENTÉE et TESTÉE FONCTIONNELLEMENT DE BOUT EN BOUT |
| Apprentissage continu autonome | PERSPECTIVE |
| Parseurs HDFS/BGL du pipeline multiformat | IMPLÉMENTATION INCOMPLÈTE; 0 sortie observée |
| Résilience avant traitement/ACK | TESTÉE en laboratoire sur une panne simulée |
| Résilience après traitement/avant ACK | NON ÉVALUÉE |
| Haute disponibilité production | NON ÉVALUÉE |

# 18. Statut des hypothèses

Les cinq hypothèses sont `PARTIELLEMENT SOUTENUES`.

- H1: normalisation partielle, perte HDFS/BGL et brut non universel.
- H2: modularité/traçabilité et reprise soutenues; débit inférieur, robustesse industrielle absente.
- H3: routeur fonctionnel; bénéfice prédictif systématique absent.
- H4: modèles légers parfois utiles; échecs majeurs et validation humaine non évaluée.
- H5: mémoire et mise à jour implémentées; bénéfice causal de la mémoire et autonomie non évalués.

Référence détaillée: `final_hypothesis_status.md`.

# 19. Réponses aux questions de recherche

- QR1 normalisation: RÉPONSE PARTIELLE.
- QR2 organisation multi-agents: RÉPONSE PARTIELLE.
- QR3 sélection automatique par famille: RÉPONSE PARTIELLE.
- QR4 tableau de bord analyste: RÉPONSE PARTIELLE; aucune étude utilisateur.
- QR5 mémoire et mise à jour: RÉPONSE PARTIELLE.
- QR6 méthode d'évaluation: RÉPONSE FORTE dans le périmètre du prototype.

La question centrale reçoit une réponse partielle. Les mots autonome, distribué et exploitable doivent être qualifiés respectivement par orchestration logicielle, laboratoire et prototype.

# 20. Limites finales

- Provenance officielle des copies locales non démontrée.
- Sous-échantillonnage CICIDS limité à deux chunks/fichier.
- Holdouts: scénarios fixes, non échantillon aléatoire de menaces futures.
- Seeds N=5: sensibilité conditionnelle seulement.
- HDFS évalué à l'événement alors que le label provient du bloc.
- BGL train sans anomalie, déplacement massif validation/test et 89,808 % de templates test inconnus.
- Histogram HDFS/BGL déterministe N=1.
- Phase 5: adaptateurs hétérogènes, Apache N=1 synthétique, HDFS/BGL sans sortie.
- Phase 6: chunks partageant une source et métadonnées révélatrices.
- Multi-VM: VirtualBox/NAT/Redis unique, relances manuelles, versions OS et durée réelle incomplètes.
- Résilience traitement→ACK, interruption Redis, partitions réseau et doublons non testés.
- Corrélation: corpus synthétique de 16 anomalies, aucune vérité SOC réelle.
- Dashboard: aucune étude d'utilisabilité.
- Modèle update: cas non indépendants issus de relations phase 2 déjà connues.
- Aucun test inférentiel global.

# 21. Figures à intégrer

Priorité recommandée:

1. `figures/cicids_random_vs_holdout_f1.png` — dépendance au split, N explicites.
2. `figures/cicids_f1_scenario_seed_heatmap.png` — stabilité seed et variation scénario.
3. `figures/cicids_modeles_scenarios_f1.png` — cinq modèles × scénarios.
4. `figures/hdfs_bgl_ancien_vs_strict_f1.png` — à légender comme comparaison de protocoles, non ablation causale.
5. `figures/validation_multiformat.png` — inclure HDFS/BGL à zéro.
6. `figures/router_confusion_matrix.png` — montrer Apache→fallback.
7. `figures/model_update_promotion_rejet.png` — branches de gouvernance.
8. `figures/correlation_synthetic_metrics.png` — uniquement si la corrélation synthétique est intégrée.

Ne jamais réintroduire une figure contenant `0,999965` comme résultat scientifique.

# 22. Tableaux à intégrer

- `tables/cicids_phase1_results.md`.
- `tables/cicids_phase2_model_comparison.md`.
- `tables/hdfs_bgl_old_vs_strict_protocol.md` avec avertissement non causal.
- `tables/model_update_end_to_end.md`.
- `tables/validation_multiformat.md`.
- `tables/router_metrics_by_family.md`.
- `tables/correlation_synthetic_metrics.md`.
- `tables/transversal_statistics_key_results.md`.
- `docs/memoire/tables/table_vbox_redis_1h_campaign.md` et récupération.
- `docs/memoire/tables/table_controlled_monolith_vs_agents.md`, avec CPU `% cœur logique équivalent` et RSS `MiB`.

# 23. Éléments à mettre en annexe

- Environnement complet et `pip freeze`.
- Manifeste avec les 11 SHA-256.
- Configurations JSON figées des phases 1, 3, 4, 5, 6, 8 et 9.
- Run IDs et streams des trois campagnes multi-VM.
- Protocole multi-VM en huit étapes, commandes et limites.
- Hashes Drain3 et modèle update; rapports d'intégrité.
- Matrices de confusion et résultats par seed/scénario.
- Échecs HistGradientBoosting initiaux et explication de reprise.
- 120 paires de corrélation ou, au minimum, vérité et matrice TP/FP/FN/TN.
- Matrices affirmation→preuve, hypothèses et questions.

# 24. Éléments à supprimer de l'ancien mémoire

- Toute occurrence scientifique de `0,999965` et toute attribution UNSW/CIC-DDoS officielle.
- Toute formulation « 525 tâches terminées avec succès ».
- Toute présentation des VM comme uniquement futures: elles ont été testées en laboratoire.
- Toute extrapolation industrielle, multi-site ou haute disponibilité.
- `event_id`, `message_id`, `metadata` comme champs directs d'AgentMessage.
- Ancien HDFS/BGL présenté comme validation indépendante.
- Affirmation que le routage améliore systématiquement les scores.
- Affirmation que LogisticRegression est le meilleur selon toutes les métriques.
- Affirmation de conservation universelle du message brut.
- Affirmation d'apprentissage continu autonome ou de promotion production.
- Significativité statistique ou dispersion inventée pour N=1.

# 25. Modifications nécessaires chapitre par chapitre

| Section | Correction à transmettre à Luna |
| --- | --- |
| Résumé français | Retirer `0,999965`; mentionner la fragilité holdout, le caractère laboratoire multi-VM et les principales limites; ne pas surcharger de scores. |
| Abstract | Aligner exactement sur le résumé et supprimer toute attribution CIC-DDoS/UNSW fragile. |
| Chapitre 1 | Conserver les cinq hypothèses mais leur attribuer le statut partiellement soutenu; QR1–QR5 partielles, QR6 forte dans le prototype. |
| Chapitre 2 | Vérifier uniquement les descriptions de datasets; distinguer nom public et copie locale; ne pas inventer de provenance. |
| Chapitre 3 §3.14 | Remplacer le contrat par les sept champs exacts; séparer enveloppes Redis/MQTT; préciser `run_id` de corrélation. |
| Chapitre 3 parsing | Restreindre la conservation du brut et signaler l'incomplétude HDFS/BGL du pipeline courant. |
| Chapitre 3 routeur | Décrire scores heuristiques, marge non probabiliste, fallback et incohérence Apache. |
| Chapitre 3 mise à jour | Statut exact: implémentée et testée fonctionnellement de bout en bout; autonomie en perspective. |
| Chapitre 5 protocole CICIDS | Ajouter seeds, fichiers holdout, échantillonnage, features, modèles, scaler train-only et métriques. |
| Chapitre 5 CICIDS | Remplacer les conclusions basées sur random par la comparaison random/holdout; intégrer LR `0,233670` avec limites. |
| Chapitre 5 HDFS/BGL | Reclasser l'ancien en exploratoire; présenter le strict avec train/validation/test, Drain3 gelé, fenêtres, seuil validation et N. |
| Chapitre 5 multi-VM | Insérer le protocole exact de §5.7, les trois campagnes et la formulation « lues et acquittées ». |
| Chapitre 5 benchmark | Conserver les trois modes et le résultat de surcoût; unités CPU/RSS explicites. |
| Chapitre 5 multiformat | Ajouter 7 001/5 001/2 000, les deux échecs HDFS/BGL et Apache N=1. |
| Chapitre 5 routeur | Séparer attribution de famille de l'ablation prédictive; ajouter 80/81 et l'erreur Apache. |
| Chapitre 5 corrélation | Optionnel: intégrer uniquement comme validation synthétique contrôlée avec pairwise et deux modes d'échec. |
| Discussion | Organiser autour des résultats négatifs: split, scénarios, overhead, routage, parsing, corrélation, résilience. |
| Chapitre 8/reproductibilité | Remplacer la VM « future » par campagne laboratoire exécutée; maintenir industriel/physique/sécurisé en perspective. |
| Conclusion | Séparer contributions architecturale, méthodologique, expérimentale et logicielle; reprendre les statuts, pas les ambitions initiales. |
| Annexes | Ajouter configurations, hashes, run IDs, ledger, figures/tableaux et limites d'interprétation. |

# 26. Informations encore à vérifier

- Phase 13A: CICIDS2017 est identifié officiellement et ses huit copies locales sont fortement concordantes; HDFS.log et anomaly_label.csv sont des correspondances SHA-256 exactes avec HDFS_v1.zip; Linux_2k.log est une correspondance SHA-256 exacte avec Loghub; BGL reste identifié publiquement mais sa copie locale n'est pas prouvée bit à bit.
- Phase 13A: `Application.evtx` est une collecte locale documentée; `06-20-October.csv` est un export Wazuh/Elastic documenté; `linux_auth_logs_labeled.csv` reste partiellement documenté; Apache et les 19 événements de corrélation sont synthétiques documentés.
- Origine et transformations exactes de `UNSWNB15.zip`: `INFORMATION À VÉRIFIER.`
- Versions exactes Windows, Debian et Ubuntu lors des campagnes multi-VM: `INFORMATION À VÉRIFIER.`
- Durée réelle de bout en bout des trois campagnes multi-VM: `INFORMATION À VÉRIFIER.`
- Version exacte du serveur Redis lors des expériences: `INFORMATION À VÉRIFIER.`
- GPU de la machine expérimentale: `INFORMATION À VÉRIFIER.`
- Comportement après traitement mais avant ACK, doublons et idempotence: `INFORMATION À VÉRIFIER.`
- Robustesse sous panne Redis, partition réseau ou pannes multiples: `INFORMATION À VÉRIFIER.`
- Utilisabilité du dashboard par des analystes: `INFORMATION À VÉRIFIER.`
- Performance de corrélation sur incidents SOC réels annotés: `INFORMATION À VÉRIFIER.`
- Effet causal de la mémoire persistante sur la qualité de priorisation: `INFORMATION À VÉRIFIER.`
- Généralisation industrielle, multi-site et en production: `INFORMATION À VÉRIFIER.`

Références de contrôle finales:

- `FERMETURE_INCERTITUDES_FACTUELLES_P0.md` pour les huit incertitudes initiales au format demandé;
- `state/DECISIONS.md` pour D001–D030;
- `final_claim_evidence_matrix.md`;
- `final_hypothesis_status.md`;
- `final_research_questions_status.md`;
- `state/ARTIFACT_INDEX.json` et `state/EXPERIMENT_LEDGER.csv`.
