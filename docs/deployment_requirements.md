# Exigences De Deploiement - Logminer

Ce document rassemble les exigences a respecter apres stabilisation du code
scientifique et des resultats experimentaux.

## Objectif General

Transformer Logminer en application installable capable de demarrer ses agents
automatiquement, de decouvrir les logs pertinents de l'environnement cible et
de fonctionner en mode performance avec Redis/workers.

## Windows

- fournir un installateur ou executable `.exe`;
- fournir une installation offline autonome;
- verifier avant installation que Docker et Redis sont disponibles;
- demander a l'administrateur d'installer Docker/Redis avant Logminer si l'un
  des deux manque;
- creer un raccourci bureau;
- lancer l'application sans configuration manuelle lourde;
- demarrer les agents et le dashboard au lancement.

## Linux

- fournir une installation conforme aux pratiques Linux;
- produire un paquet `.deb` et/ou `.rpm` selon la distribution cible;
- integrer un service `systemd`;
- utiliser les chemins standards `/opt`, `/etc`, `/var/lib` et `/var/log`;
- fournir une installation offline via paquet local ou depot local signe;
- verifier Docker/Redis avant activation du mode performance.

## Docker Et Redis

Redis est requis pour le mode performance/distribue:

- workers paralleles;
- file de jobs;
- bus evenementiel;
- meilleure separation API/traitement.

Si Docker/Redis n'est pas pret, l'application doit bloquer ou degrader
explicitement le mode performance et expliquer l'action attendue.

## Decouverte Automatique Des Logs

Logminer doit trouver automatiquement tous les logs pour lesquels ses agents
sont concus.

La decouverte doit couvrir:

- journaux systeme standards;
- logs applicatifs;
- sous-dossiers applicatifs `Logs`, `LogFiles`, `log` et chemins declares par
  profil;
- SIEM/HIDS/agents;
- Wazuh/OSSEC;
- logs web;
- logs cloud/export JSON;
- logs reseau;
- volumes montes;
- repertoires declares par l'administrateur;
- chemins definis par profils de deploiement.

Les racines tres larges doivent rester controlees par profil ou configuration
administrateur afin d'eviter les scans couteux et les fichiers systeme
inaccessibles.

## Extensions A Rechercher

Les extensions cibles incluent:

- `.evtx`;
- `.xml`;
- `.log`;
- `.txt`;
- `.json`;
- `.jsonl`;
- `.ndjson`;
- `.csv`;
- `.parquet`;
- `.cef`;
- `.leef`;
- `.audit`;
- `.trace`;
- `.out`;
- `.err`;
- `.pcap`;
- `.pcapng`;
- `.tcpdump`.

## Profils Et Configuration

La decouverte doit etre configurable sans modifier le code:

- `LOGMINER_LOG_ROOTS`;
- `LOGMINER_EXTRA_LOG_ROOTS`;
- fichiers de configuration par OS;
- profils par famille de logs;
- profils par environnement client.

## UX Administrateur

Au demarrage, l'administrateur doit voir:

- etat Docker/Redis;
- agents actifs;
- sources detectees;
- erreurs de permissions;
- derniere analyse;
- anomalies candidates;
- incidents;
- chemins des rapports.

## Installation Offline

Le paquet offline doit inclure:

- application;
- dependances;
- modeles `.joblib`;
- assets dashboard;
- configuration par defaut;
- image Redis ou procedure Redis locale;
- checksums;
- documentation.

## Validation Avant Livraison

- installation Windows propre;
- installation Linux propre;
- installation offline;
- preflight Docker/Redis;
- decouverte automatique OS + applications;
- fonctionnement avec logs applicatifs;
- fonctionnement degrade clair sans Redis;
- generation de rapports;
- desinstallation propre.
