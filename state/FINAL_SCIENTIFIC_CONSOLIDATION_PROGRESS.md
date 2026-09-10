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
- [ ] Protocoles P1–P4 figés et testés. Le protocole maître et P1 sont figés ; P2–P4 restent à matérialiser.
- [x] Script P1 créé et validation syntaxique réussie.
- [ ] P1 exécuté.
- [ ] P2 exécuté.
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
