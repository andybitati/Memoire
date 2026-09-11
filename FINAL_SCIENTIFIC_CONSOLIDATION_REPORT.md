# Rapport final de consolidation scientifique d’Ariel Logminer

## 1. Objectif

Cette phase ferme quatre critiques encore traitables sans alourdir le prototype : audit du résultat externe CSE-CIC-IDS2018, rejet open-set, inférence effective des modèles routés et sensibilité du résultat HDFS au niveau bloc. Les expériences antérieures jugées solides ne sont pas relancées.

## 2. État avant consolidation

La LR externe atteignait un F1 moyen de 0,999212 après un contrôle de doublons exacts. Le routeur reconnaissait 28 fichiers connus mais rejetait 0/3 inconnus. Le replay CNP de 1 401 unités exécutait une règle légère malgré les recommandations de modèles. HDFS atteignait 0,892308 au niveau bloc sur seulement 29 positifs test.

## 3. Audit LR CSE-CIC-IDS2018

Le run `final_csecic_lr_forensic_20260911T000140Z` réutilise les pools figés du run `external_csecicids2018_20260910T230136Z` : apprentissage le 15 février 2018, test le 16 février, 78 caractéristiques numériques, cinq graines et 10 000 observations par classe dans chaque partition. La conclusion retenue est B : performance très dépendante de quelques features.

Les contrôles exécutés n’ont pas mis en évidence de fuite triviale correspondant aux mécanismes testés.

Cette phrase ne signifie pas qu’aucune fuite est possible et ne dépasse pas les contrôles réalisés.

## 4. Permutation labels

La permutation de `y_train` conserve X_train, X_test et y_test. Le F1 moyen tombe à 0,339867, le MCC à 0,119281. La PR-AUC moyenne vaut 0,744143, avec une forte dispersion jusqu’à 0,997411. Le contrôle détruit la qualité de décision au seuil fixé mais pas systématiquement le classement, ce qui renforce le constat de variables dominantes.

## 5. Analyse mono-feature

Parmi les 78 modèles mono-feature, `Dst Port` atteint à elle seule un F1 moyen de 0,999720 et une PR-AUC de 0,999228. Cette séparation doit être décrite comme propre à la composition des deux journées et scénarios évalués.

## 6. Coefficients LR

Les coefficients proviennent d’une LR précédée d’un `StandardScaler` ajusté sur le train uniquement. Les plus fortes valeurs absolues moyennes concernent `Dst Port`, `Fwd Seg Size Min`, `PSH Flag Cnt`, `Fwd Header Len` et `Pkt Len Var`. Elles signalent une association discriminante dans le modèle, pas une cause de l’attaque.

## 7. Ablation features

Les retraits top-1/3/5/10 sont fixés avant exécution et classés sur le modèle train de chaque graine. Le F1 passe de 0,999212 avec 78 variables à 0,657859 après retrait des dix premières ; le FPR passe de 0,001580 à 0,969560. La performance dépend donc fortement d’un petit sous-ensemble de caractéristiques.

## 8. Router open-set

Le run `final_router_open_set_20260911T000746Z` sélectionne `top_score >= 100` sur 196 observations leave-one-family-out issues exclusivement des 28 sources connues. Le test final, consulté après gel, donne une known accuracy de 1,000000, une macro-F1 connue de 1,000000, un rejet inconnu de 1,000000, un faux rejet connu de 0,000000, une coverage de 0,903226 et une selective accuracy de 1,000000. `decision_margin` reste un score heuristique de séparation.

## 9. E2E avec modèles réellement routés

Le run `multisource_cnp_model_inference_20260911T003432Z` exécute deux conditions de 1 401 tâches. H applique 1 401 fois la règle légère. M appelle réellement un artefact compatible sur 1400 unités, utilise 1 fallback Apache, produit 0 erreur et 0 réattribution. La latence moyenne passe de 0,031027 s à 0,105420 s ; le P95 passe de 0,068247 s à 0,181044 s. Les refus CNP (2602) proviennent des agents sans capability compatible et ne sont pas des erreurs d’exécution.

Les temps processus mesurés valent 42,609375 s pour H et 131,625000 s pour M. Le RSS après condition vaut 229826560 octets pour H et 361304064 octets pour M. Ces valeurs sont des instantanés du même processus ; M garde sept artefacts en cache. Elles ne décrivent ni un pic isolé ni une consommation de production.

Sur Linux/auth, seule source sélectionnée contenant deux classes et une unité compatible, la condition M donne un F1 descriptif de 0,390244. BGL et CICIDS ne contiennent qu’une classe dans leurs 200 premières unités : NON ÉVALUÉ. Les métriques H sont NON ÉVALUÉES car la règle historique lit directement les labels disponibles. Aucune accuracy globale n’est fabriquée.

## 10. Robustesse HDFS block-level

Le run `hdfs_block_robustness_20260911T002351Z` reproduit le F1 0,892308 sur 2 000 blocs, dont 29 positifs, avec l’état Drain3 inchangé, l’agrégateur `mean` et le seuil 1.2729429339548877. Sur 1 000 bootstraps de `block_id`, la médiane est 0,894737, l’intervalle descriptif 2,5–97,5 % [0,800000 ; 0,961039] et l’IQR 0,052185. Les 29 retraits d’un bloc positif donnent tous un F1 0,888889 et un rappel 1,000000. Le score block-level reste variable sous les analyses de sensibilité réalisées.

## 11. Résultats négatifs

- La LR externe est fortement dominée par quelques caractéristiques ; son score ne justifie pas une généralisation large.
- La PR-AUC du contrôle permuté ne s’effondre pas de manière stable selon la graine.
- L’inférence réelle Linux/auth n’atteint qu’un F1 descriptif de 0,390244 sur les 200 premières lignes.
- Le test HDFS reste variable sous bootstrap malgré un rappel stable.
- Trois artefacts IsolationForest Colab émettent un avertissement de compatibilité scikit-learn 1.6.1 vers 1.7.2 ; les appels réussissent, mais cette limite doit rester visible.

- Le premier run P3 (`multisource_cnp_model_inference_20260911T001644Z`) est SUPERSEDED : son calcul d’incidents H était incomplet. Ses sorties raw sont conservées, mais seules les valeurs du run définitif `multisource_cnp_model_inference_20260911T003432Z` soutiennent les claims finaux.

## 12. Statistiques

P1 rapporte moyenne, écart-type d’échantillon, médiane, extrema et IC normal approximatif sur cinq graines corrélées par pools parents. P2 est une évaluation sur fichiers et groupes, sans IC. P3 rapporte latences moyennes/P95 et métriques par source uniquement. P4 utilise des percentiles bootstrap descriptifs au niveau bloc ; ils ne prouvent pas l’indépendance statistique.

## 13. Tests de non-régression

Le fichier JUnit atteste `37` tests, `0` échec, `0` erreur et `0` test ignoré. Les garde-fous couvrent AgentMessage, CNP, idempotence, splits, Drain3, scalers, calibration, schémas, marqueurs d’inférence et seuil HDFS gelé.

## 14. Claim–evidence final

La matrice consolidée est `FINAL_CONSOLIDATED_CLAIM_EVIDENCE_MATRIX.md`. Elle retient : LR externe partiellement soutenue, open-set partiellement soutenu, E2E réel soutenu, robustesse HDFS partiellement soutenue, autonomie multi-agent soutenue dans le laboratoire et industrialisation hors périmètre.

## 15. Impact H1–H5

| Hypothèse | Impact final | Statut recommandé |
| --- | --- | --- |
| H1 | Aucun changement de couverture ; HDFS reste évalué au bloc et le pipeline multiformat est préservé | PARTIELLEMENT SOUTENUE |
| H2 | Le CNP exécute désormais les modèles compatibles sur 1 400 unités, sans nouvelle preuve de débit ou de résilience | PARTIELLEMENT SOUTENUE |
| H3 | Le rejet fonctionne sur 3/3 inconnues après calibrage connu-only, mais le test est très petit | PARTIELLEMENT SOUTENUE |
| H4 | L’audit LR impose une forte requalification ; l’inférence réelle est prouvée mais l’utilité prédictive générale ne l’est pas | PARTIELLEMENT SOUTENUE |
| H5 | Aucun nouvel effet causal de la mémoire n’est mesuré | PARTIELLEMENT SOUTENUE, inchangée |

## 16. Impact QR1–QR6

| Question | Impact final | Niveau recommandé |
| --- | --- | --- |
| QR1 | Couverture multiformat inchangée ; robustesse HDFS mieux quantifiée | RÉPONSE PARTIELLE renforcée |
| QR2 | Preuve d’exécution effective des artefacts dans le CNP | RÉPONSE PARTIELLE renforcée |
| QR3 | Rejet open-set ajouté et validé sur trois fichiers | RÉPONSE PARTIELLE renforcée |
| QR4 | Aucun test utilisateur | RÉPONSE PARTIELLE, inchangée |
| QR5 | Aucun gain causal de mémoire nouveau | RÉPONSE PARTIELLE, inchangée |
| QR6 | Protocoles figés, contrôles négatifs, hashes et tests renforcent la reproductibilité | RÉPONSE FORTE dans le périmètre laboratoire |

## 17. Affirmations désormais soutenables

- Le résultat LR externe est reproductible sous son holdout, mais très dépendant de quelques caractéristiques.
- Une politique légère calibrée sans les trois fichiers finaux les rejette tous, sans faux rejet parmi les 28 fichiers connus.
- Les agents CNP chargent et appellent réellement sept artefacts compatibles sur 1 400 des 1 401 unités de la condition M.
- Le F1 HDFS observé est reproduit avec seuil gelé et sa variabilité bootstrap est quantifiée.

## 18. Affirmations toujours non démontrées

- Absence de toute fuite possible dans CSE-CIC-IDS2018 : NON SOUTENU.
- Généralisation de la LR à l’ensemble de CSE-CIC-IDS2018 ou à un SOC : NON SOUTENU.
- Rejet open-set général au-delà des trois fichiers testés : NON SOUTENU.
- Gain prédictif systématique du routage ou de la condition M : NON SOUTENU.
- Accuracy globale multi-source : NON ÉVALUÉ.
- Haute disponibilité, tolérance aux partitions et très grande échelle : NON ÉVALUÉ.

## 19. Perspectives industrielles

Les propriétés industrielles de haute disponibilité, de déploiement multi-site, de tolérance aux partitions et de montée en charge à très grande échelle sont laissées aux perspectives.

Les prolongements nécessaires pour passer d’une validation de laboratoire à un système opérationnel de production comprennent Redis Sentinel/Cluster, le test des partitions réseau et du failover broker, le multi-site, Kubernetes, Prometheus/Grafana, une gestion industrielle des secrets, l’authentification forte, TLS, RBAC, la haute disponibilité, les tests de charge à grande échelle, un SOC réel et une étude utilisateur auprès d’analystes SOC.

## 20. Artefacts

Les configurations, résultats bruts, données préparées, agrégats, figures 12 à 20, rapports et manifests se trouvent sous `experiments/phase_final_scientific_consolidation/`. Les rapports spécialisés P1–P4 y restent séparés des synthèses finales.

## 21. Hashes

`experiments/phase_final_scientific_consolidation/manifests/SHA256_MANIFEST.json` recense les scripts, configurations, modèles, références d’entrée et artefacts. Le manifeste s’exclut lui-même afin d’éviter une dépendance circulaire. La validation machine est conservée séparément.

## 22. Commandes exactes

```powershell
.venv-hdfs-bgl\Scripts\python.exe scripts\run_final_csecicids2018_lr_forensic.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_router_open_set_consolidation.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_multisource_cnp_model_inference.py
.venv-hdfs-bgl\Scripts\python.exe scripts\run_hdfs_block_robustness.py
.venv-hdfs-bgl\Scripts\python.exe -m pytest tests\test_dataset_strengthening.py tests\test_true_multi_agent.py tests\test_final_scientific_consolidation.py -q --junitxml=experiments\phase_final_scientific_consolidation\logs\relevant_tests_junit.xml
.venv-hdfs-bgl\Scripts\python.exe scripts\finalize_scientific_consolidation.py
```

Dans cette session, chaque commande shell a été préfixée par `rtk`, conformément aux instructions du dépôt.

La commande `graphify update .` a été tentée après modification du code et a échoué avec `[WinError 5] Accès refusé`. Cet échec de l’outil de cartographie n’affecte pas les résultats expérimentaux ni leurs empreintes.

## 23. Recommandations de rédaction du mémoire

Les modifications à appliquer après validation sont détaillées dans `experiments/phase_final_scientific_consolidation/reports/MEMOIRE_REVISION_RECOMMENDATIONS.md`. Elles visent les sections expérimentales du chapitre 5, les limites/perspectives du chapitre 8, puis le résumé et la conclusion. Aucun chapitre n’a été modifié par cette phase.
