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
- [ ] Protocoles P1–P4 figés et testés. P1–P3 sont matérialisés ; P4 reste à matérialiser.
- [x] Script P1 créé et validation syntaxique réussie.
- [x] P1 exécuté : run `final_csecic_lr_forensic_20260911T000140Z`, conclusion B. Un premier run échoué par sérialisation NumPy reste conservé dans le ledger.
- [x] P2 exécuté : run `final_router_open_set_20260911T000746Z`, seuil `top_score=100` calibré sur pseudo-open connu uniquement ; rejet final 3/3, faux rejet connu 0/28.
- [ ] P3 exécuté.
- [ ] P4 exécuté.
- [ ] Tests de non-régression exécutés.
- [ ] Manifeste SHA-256 et rapports finaux produits.

## Contraintes de reprise

- Ne pas modifier `ARIEL_LOGMINER_MEMOIRE_FINAL` pendant les expériences.
- Ne pas relancer les campagnes historiques déjà solides, sauf régression constatée.
- Ne jamais calibrer le rejet du routeur sur les trois fichiers open-set finaux.
- Ne jamais sélectionner ou réajuster le seuil HDFS sur le test ou dans le bootstrap.
- Conserver les résultats négatifs et les statuts `NON SOUTENU`, `NON ÉVALUÉ` et `INFORMATION À VÉRIFIER` lorsqu’ils s’appliquent.
- Pour toute commande longue : un contrôle au plus toutes les 300 secondes.
- `graphify update .` a de nouveau échoué avec `[WinError 5] Accès refusé` après l’ajout du script P1 ; cet échec n’affecte pas les artefacts expérimentaux.
- Le registre P3 est figé : sept sources avec artefact compatible et Apache en fallback heuristique explicite. Un smoke test d’inférence réelle a réussi pour les sept artefacts.
