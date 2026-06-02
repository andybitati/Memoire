# Taxonomie Des Journaux Pour Logminer

Ce document rattache l'objectif 1 du document directeur au prototype Logminer:
identifier, categoriser et structurer les journaux systemes et reseaux utiles a
l'analyse de securite.

## Familles De Journaux

| Famille | Exemples | Format courant | Champs critiques | Support Logminer |
| --- | --- | --- | --- | --- |
| Systeme Windows | Security, System, Application | EVTX, XML exporte | horodatage, provider, event id, utilisateur, machine, message | parseur Windows Event, collecte PowerShell |
| Systeme Linux | syslog, journalctl, auth.log | texte syslog, CSV prepare | timestamp, host, service, utilisateur, severite, message | parseur syslog, modele Linux/syslog |
| Authentification | SSH, sudo, login failures | CSV tabulaire ou syslog | serveur, username, service, statut, tentatives, port | dataset Linux/auth, RandomForest dedie |
| Applicatif web | Apache, NGINX, web-accesslog | texte access log, Wazuh export | IP source, methode, chemin, code HTTP, user-agent | parseur Apache, routage reseau/web |
| Reseau | pcap, tcpdump, UNSW, CICIDS | pcap, texte tcpdump, CSV/Parquet | src/dst IP, ports, protocole, duree, taille, label | parseurs pcap/tcpdump, modeles reseau |
| SIEM/EDR | Wazuh/Elastic | JSON/CSV avec `_source.*` | rule level, decoder, full log, agent, groupes MITRE | routeur Wazuh, Isolation Forest Wazuh |
| Systeme distribue | HDFS, BGL | texte ou CSV annote | bloc, composant, evenement, severite, label | parseurs HDFS/BGL, validations |
| Cloud/audit | CloudTrail | JSON/JSONL | principal, action, ressource, IP source, region | parseur CloudTrail |

## Schéma Normalise

Le schema commun est defini dans `src/logminer/schema/columns.py`. Les champs
les plus importants pour les agents suivants sont:

| Champ | Utilite |
| --- | --- |
| `timestamp_iso` | ordonnancement, timeline, fenetres de correlation |
| `severity` | priorisation et filtrage |
| `event` | code ou type d'evenement |
| `source` | service, provider, capteur ou application |
| `host` | machine concernee |
| `user` | identite associee |
| `src_ip`, `dst_ip`, `src_port`, `dst_port` | contexte reseau |
| `category`, `subcategory` | classification securite |
| `message` | texte interpretable et vectorisable |

## Contraintes Et Limites

- Les journaux Windows sensibles, par exemple `Security.evtx`, peuvent exiger
  des droits administrateur.
- Les logs non structures peuvent perdre des champs si le message brut ne suit
  pas un format stable.
- Les exports SIEM contiennent parfois des colonnes imbriquees qui doivent etre
  conservees telles quelles avant normalisation.
- Les datasets reseau tabulaires ne doivent pas etre confondus avec des logs
  systeme: le routeur multi-modeles evite cette divergence.
- Les timestamps incomplets limitent l'analyse temporelle et le calcul des faux
  positifs par periode.

## Position Dans Le Memoire

Cette taxonomie nourrit:

- le chapitre 1, pour presenter le contexte et l'heterogeneite des journaux;
- le chapitre 2, pour comparer formats et contraintes de detection;
- le chapitre 3, pour justifier le schema normalise et le routage par famille;
- le chapitre 4, pour expliquer les parseurs et scripts de collecte.
