# Campagne CNP Redis multi-VM

- Run : `multivm_cnp_20260909T202632Z_37592`
- Redis : `7.4.9` sur l'hôte de laboratoire `redis://localhost:6379/0`
- Hôtes agents : `['andy', 'andy-VirtualBox']`
- Tâches réussies : `60/60`
- Débit : `22.120187` tâches/s
- Latence p95 : `63.02985` ms
- Répartition : `{"debian-alpha": 30, "ubuntu-beta": 30}`
- Refus explicites : `15` ; réattributions après échec : `1`
- Replay idempotent : `True` ; effets persistants : `1`
- Statut : `ok`

Cette expérience démontre des décisions et exécutions d'agents sur deux VM. Redis reste centralisé sur l'hôte Windows du laboratoire ; aucune haute disponibilité ni portée industrielle n'est revendiquée.
