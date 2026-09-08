# PHASE 7 COMPLETED

Objectif: Décider si une campagne de résilience complémentaire apporterait une preuve scientifique nouvelle.

Protocole: Audit ciblé du scénario multi-VM panne/reprise, de l'ordre traitement/publication/ACK du runtime et de la disponibilité locale de Redis. Aucun ancien artefact n'a été modifié ou rejoué.

Runs prévus: 0 après décision NO-GO.

Runs terminés: 0.

Runs échoués: 0.

Résultats principaux:

- La campagne existante prouve une reprise après sortie contrôlée avant traitement et ACK: 3 tâches enfilées, 3 terminées, 3 uniques, 1 tâche reprise, 0 échec, pending final 0.
- Un scénario après traitement mais avant ACK apporterait une information nouvelle sur les doublons et l'idempotence.
- Cette campagne complémentaire n'a pas été lancée: Redis était indisponible et l'injection requise n'existe pas dans le runtime courant.

Résultat négatif éventuel: Les garanties d'absence de doublons après panne dans la fenêtre traitement→ACK restent non évaluées.

Artefacts:

- `experiment_resilience_complementary_summary.md`.
- `scripts/run_vbox_redis_recovery_campaign.ps1`.
- `data/processed/vbox_redis_recovery_campaign.json`.
- `docs/memoire/tables/table_vbox_redis_recovery_campaign.md`.

Problèmes:

- Docker Desktop non démarré et aucun Redis sur `localhost:6379` lors de l'audit.
- Le scénario existant simule une sortie contrôlée du programme; il ne constitue pas un kill externe du processus.
- Aucun temps de reprise ni lag final n'est enregistré dans son résumé.

Conclusion scientifique: Phase optionnelle classée `SKIPPED`. La preuve conservable demeure une reprise multi-VM de laboratoire avant traitement/ACK. L'idempotence après traitement avant ACK reste non évaluée.

Impact probable sur le mémoire: Conserver la formulation limitée de D002. Ne pas revendiquer une absence générale de pertes/doublons, une haute disponibilité ou une résilience industrielle.

