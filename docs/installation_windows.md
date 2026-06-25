# Guide D'installation Windows - Logminer

Ce guide decrit la cible d'installation Windows a preparer apres stabilisation
du prototype. Il sert de reference pour construire l'installateur, le mode
offline et la prise en main administrateur.

Exigences transversales: voir `docs/deployment_requirements.md`.

## Objectif

Fournir une application Windows installable, utilisable depuis le bureau et
capable de demarrer les agents Logminer avec le minimum de configuration.

## Livrables Attendus

- installateur Windows ou executable `.exe`;
- raccourci bureau et menu demarrer;
- bundle offline complet;
- modele de configuration par defaut;
- verification Docker/Redis au lancement;
- guide rapide pour administrateur;
- procedure de desinstallation.

## Prerequis Windows

- Windows 10/11 ou Windows Server recent;
- compte administrateur pour l'installation;
- Docker Desktop ou service Docker installe avant l'installation Logminer;
- Redis disponible via Docker ou service local avant l'installation Logminer;
- acces aux journaux Windows selon les permissions locales;
- espace disque suffisant pour les logs, modeles et exports.

L'installateur doit verifier Docker et Redis avant de poursuivre. Si Docker ou
Redis n'est pas installe, il doit demander a l'administrateur de les installer
avant l'installation de Logminer. Cette exigence permet de garantir le mode
performance avec workers paralleles, file de jobs et bus Redis.

Commande de preverification cible:

```powershell
python src\logminer\agents\runtime_agent.py --install-preflight
```

## Installation Offline

Le paquet offline doit contenir:

- application Logminer compilee ou embarquee;
- dependances Python/binaires necessaires;
- modeles `.joblib`;
- assets dashboard;
- configuration par defaut;
- image Redis exportee si Redis passe par Docker;
- fichiers de verification d'integrite;
- documentation minimale en PDF ou Markdown.

Le paquet doit pouvoir etre copie sur une machine sans Internet puis installe
localement.

## Demarrage De L'application

Au premier lancement, l'application doit:

1. verifier les chemins locaux et creer les dossiers de travail;
2. verifier Docker et Redis;
3. demander a l'administrateur de lancer Docker Desktop si Docker/Redis est
   installe mais inactif;
4. demarrer les agents disponibles;
5. decouvrir automatiquement les sources de logs accessibles;
6. afficher l'etat des services et les erreurs de permissions;
7. ouvrir le dashboard.

Si Redis est indisponible, l'application doit afficher clairement que le mode
performance/distribue est degrade ou indisponible.

## Decouverte Automatique Des Logs Windows

Les agents doivent chercher automatiquement:

- journaux Evenements Windows accessibles;
- exports EVTX/XML presents dans les dossiers configures;
- logs applicatifs produits par les logiciels installes sur la machine;
- dossiers applicatifs connus et sous-dossiers de logs, notamment `Logs`,
  `LogFiles`, `log`, IIS, Wazuh/agents, Docker containers et chemins
  applicatifs declares;
- dossiers Wazuh/agents si presents;
- sources de logs ajoutees par l'administrateur.

Les agents doivent chercher tous les fichiers dont les extensions correspondent
aux parseurs disponibles: `.evtx`, `.xml`, `.log`, `.txt`, `.json`, `.jsonl`,
`.ndjson`, `.csv`, `.parquet`, `.cef`, `.leef`, `.audit`, `.trace`, `.out`,
`.err`, `.pcap`, `.pcapng` et `.tcpdump`.

La decouverte ne doit pas se limiter aux chemins d'exemple. Le systeme de
deploiement doit pouvoir definir des profils de recherche couvrant les volumes
locaux, dossiers applicatifs, chemins SIEM/HIDS, repertoires d'agents,
partages ou volumes montes autorises et tout autre emplacement prevu par
l'environnement cible. Les racines tres larges comme `Program Files`,
`ProgramData` ou `AppData` doivent etre utilisees via profil ou configuration
admin lorsqu'elles sont necessaires, afin d'eviter un scan trop lourd ou des
fichiers systeme inaccessibles. L'objectif est que Logminer trouve
automatiquement tous les logs pour lesquels il est concu, sans configuration
manuelle lourde.

Les chemins supplementaires peuvent etre fournis par les variables
`LOGMINER_LOG_ROOTS` ou `LOGMINER_EXTRA_LOG_ROOTS`, separees par `;` sous
Windows.

Les journaux sensibles doivent demander une elevation de privileges uniquement
si necessaire.

## Prise En Main Administrateur

L'ecran initial doit permettre de voir rapidement:

- etat Docker/Redis;
- agents actifs;
- sources detectees;
- derniere analyse;
- anomalies candidates;
- incidents correles;
- erreurs de permissions;
- chemin des rapports et exports.

## Securite Et Maintenance

A prevoir:

- signature de l'executable si possible;
- checksums du paquet offline;
- rotation des fichiers generes;
- stockage local clair des donnees;
- separation configuration/donnees/application;
- journal d'audit consultable;
- procedure de mise a jour offline.

## Desinstallation

Le desinstallateur doit:

- arreter les agents;
- retirer les services eventuels;
- supprimer les fichiers applicatifs;
- proposer de conserver ou supprimer les donnees locales;
- conserver un rapport de desinstallation si necessaire.

## A Valider Avant Livraison

- installation sur machine Windows propre;
- installation offline sans Internet;
- lancement depuis le bureau;
- detection Docker/Redis;
- fonctionnement degrade sans Redis;
- collecte des logs accessibles sans elevation;
- demande claire d'elevation pour logs sensibles;
- generation d'un rapport d'analyse complet.
