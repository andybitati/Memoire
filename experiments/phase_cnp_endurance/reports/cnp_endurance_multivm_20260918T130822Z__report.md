# Campagne d'endurance CNP Redis multi-VM

- Run : `cnp_endurance_multivm_20260918T130822Z`
- Statut : `COMPLETED`
- Duree cible/observee : `3600.000` / `3605.110` s
- Taches reussies : `1800/1800`
- Debit : `0.499291` tache/s
- Latence p95/p99 : `156.3017` / `836.72528` ms
- Repartition : `{"debian-alpha": 451, "ubuntu-beta": 1349}`
- Hotes agents : `["andy", "andy-VirtualBox"]`
- Test post-persistance/pre-RESULT : `PASSED`
- Effets persistants/dupliques : `1` / `0`

Portee : endurance et reprise du Contract Net dans la topologie de laboratoire. Redis reste centralise ; la haute disponibilite et les partitions reseau ne sont pas evaluees.

## Complétude de la trace de messages

La trace conserve la fenêtre terminale de `10001` événements. Les compteurs de types de messages ne décrivent donc pas l'heure complète et ne sont pas utilisés pour les conclusions scientifiques. Les métriques par tâche, le résultat de reprise et le magasin d'idempotence restent complets.

