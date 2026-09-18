# Campagne d'endurance CNP Redis multi-VM

- Run : `cnp_endurance_multivm_20260918T124034Z`
- Statut : `FAILED`
- Duree cible/observee : `30.000` / `30.078` s
- Taches reussies : `150/150`
- Debit : `4.987034` tache/s
- Latence p95/p99 : `96.01125` / `190.53887` ms
- Repartition : `{"ubuntu-beta": 150}`
- Hotes agents : `["andy", "andy-VirtualBox"]`
- Test post-persistance/pre-RESULT : `FAILED`
- Effets persistants/dupliques : `1` / `0`

Portee : endurance et reprise du Contract Net dans la topologie de laboratoire. Redis reste centralise ; la haute disponibilite et les partitions reseau ne sont pas evaluees.
