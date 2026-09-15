# État de la consolidation scientifique finale

Dernière mise à jour : 2026-09-11.

## Périmètre gelé

- P1 : audit anti-fuite et explicabilité du résultat LR CSE-CIC-IDS2018.
- P2 : rejet open-set léger du routeur, calibré sans les trois sources finales.
- P3 : campagne CNP distincte avec inférence réelle uniquement sur schémas compatibles.
- P4 : robustesse HDFS au niveau bloc avec seuil gelé.
- P5/P6 : claim–evidence final et recommandations de rédaction, sans modifier le manuscrit.

## État courant

- [x] Lecture des rapports, matrices, ledgers, architecture et scripts existants.
- [x] Création de `docs/FINAL_SCIENTIFIC_GAP_ANALYSIS.md` limitée aux quatre points autorisés.
- [x] Protocoles P1–P4 figés, matérialisés et testés.
- [x] Script P1 créé et validation syntaxique réussie.
- [x] P1 exécuté : run `final_csecic_lr_forensic_20260911T000140Z`, conclusion B. Un premier run échoué par sérialisation NumPy reste conservé dans le ledger.
- [x] P2 exécuté : run `final_router_open_set_20260911T000746Z`, seuil `top_score=100` calibré sur pseudo-open connu uniquement ; rejet final 3/3, faux rejet connu 0/28.
- [x] P3 exécuté : run définitif `multisource_cnp_model_inference_20260911T003432Z`, 1 400/1 401 inférences réelles en condition M, un fallback Apache, zéro erreur. Le run `multisource_cnp_model_inference_20260911T001644Z` est conservé mais marqué `SUPERSEDED` à cause d’un calcul incomplet des incidents H.
- [x] P4 exécuté : run `hdfs_block_robustness_20260911T002351Z`, F1 bloc reproduit à `0,892308`, 1 000 bootstraps par `block_id` et 29 retraits d’un positif, sans réajustement du seuil.
- [x] Tests de non-régression exécutés : 37 réussis, 0 échec, 0 erreur, 0 ignoré ; trois avertissements attendus sur des réplications bootstrap à classe unique.
- [x] Manifeste SHA-256, matrice claim–evidence et rapports finaux produits une première fois ; régénération définitive prévue après ce point de reprise pour intégrer le run P3 corrigé.

## Résultats P3 à conserver

- Condition H : 1 401 tâches heuristiques, 139 anomalies candidates, 24 incidents candidats, latence moyenne `0,031027 s`, RSS après condition `229 826 560 octets`.
- Condition M : 1 400 inférences réelles, un fallback, 142 anomalies candidates, 44 incidents candidats, latence moyenne `0,105420 s`, RSS après condition `361 304 064 octets`.
- Les mesures RSS sont des instantanés d’un même processus qui conserve sept artefacts en cache ; elles ne constituent pas des pics isolés ni des mesures de production.

## Résultats P4 à conserver

- Test gelé : 2 000 blocs, 29 positifs, TP=29, FP=7, TN=1 964, FN=0, seuil moyen fixe `1,2729429339548877`.
- Bootstrap descriptif du F1 : médiane `0,894737`, intervalle percentile 2,5–97,5 % `[0,800000 ; 0,961039]`.
- La largeur `0,161039` dépasse le critère gelé de `0,15` : résultat qualifié de variable.

## Contraintes de reprise

- Ne pas modifier `ARIEL_LOGMINER_MEMOIRE_FINAL` pendant les expériences.
- Ne pas relancer les campagnes historiques déjà solides, sauf régression constatée.
- Ne jamais calibrer le rejet du routeur sur les trois fichiers open-set finaux.
- Ne jamais sélectionner ou réajuster le seuil HDFS sur le test ou dans le bootstrap.
- Conserver les résultats négatifs et les statuts `NON SOUTENU`, `NON ÉVALUÉ` et `INFORMATION À VÉRIFIER` lorsqu’ils s’appliquent.
- Pour toute commande longue : un contrôle au plus toutes les 300 secondes.
- `graphify update .` a de nouveau échoué avec `[WinError 5] Accès refusé` après l’ajout du script P1 ; cet échec n’affecte pas les artefacts expérimentaux.
- Le registre P3 est figé : sept sources avec artefact compatible et Apache en fallback heuristique explicite. Un smoke test d’inférence réelle a réussi pour les sept artefacts.
