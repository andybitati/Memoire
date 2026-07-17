# Guide D'installation Linux - Logminer

Ce guide decrit la cible d'installation Linux a preparer apres stabilisation du
prototype. Contrairement a Windows, Linux doit respecter les conventions de
paquet, de service, de configuration et de journalisation du systeme.

Exigences transversales: voir `docs/deployment_requirements.md`.

## Objectif

Fournir une installation Linux propre, administrable et conforme aux pratiques
serveur: paquet `.deb` ou `.rpm`, service `systemd`, fichiers de configuration
separes, donnees persistantes dans des chemins standards et decouverte
automatique des logs.

## Livrables Attendus

- paquet `.deb` pour Debian/Ubuntu et/ou `.rpm` pour RHEL/Fedora selon la cible;
- service `systemd` pour les agents Logminer;
- fichier de configuration dans `/etc/logminer/`;
- donnees et modeles dans `/var/lib/logminer/` ou `/opt/logminer/` selon le
  choix final;
- journaux applicatifs dans `/var/log/logminer/`;
- commande de verification de sante;
- procedure d'installation offline via paquet local ou depot local signe.

## Prerequis Linux

- distribution Linux cible documentee;
- droits `root` ou `sudo` pour l'installation;
- Docker Engine et Docker Compose disponibles si Redis est execute par Docker;
- Redis disponible via Docker ou service local avant l'installation du mode
  performance;
- acces lecture aux journaux cibles selon les permissions systeme;
- espace disque suffisant pour les exports et rapports.

L'installateur Linux doit verifier Docker/Redis avant d'activer le mode
performance. Si Docker ou Redis manque, il doit demander a l'administrateur de
les installer avant de poursuivre l'installation complete.

## Chemins Standards

Proposition de structure:

- `/opt/logminer/`: application et binaires embarques;
- `/etc/logminer/`: configuration;
- `/var/lib/logminer/`: modeles, etat local, exports persistants;
- `/var/log/logminer/`: logs applicatifs;
- `/usr/lib/systemd/system/logminer.service`: service systemd;
- `/usr/bin/logminer`: commande wrapper.

## Service systemd

Le service doit:

- verifier Docker/Redis au demarrage;
- demarrer les agents collecteur, parseur, routeur, detecteur, correlateur et
  audit;
- exposer le dashboard/API selon la configuration;
- redemarrer automatiquement en cas d'echec controle;
- ecrire ses logs dans journald et/ou `/var/log/logminer/`.

## Decouverte Automatique Des Logs Linux

Les agents doivent rechercher automatiquement:

- `/var/log`;
- journaux syslog/auth selon distribution;
- journald si accessible;
- logs web usuels;
- logs applicatifs sous `/opt`, `/srv` ou chemins configures;
- logs Wazuh/OSSEC sous `/var/ossec/logs`;
- logs de conteneurs autorises;
- volumes montes et chemins ajoutes par l'administrateur.

La decouverte doit etre pilotee par profils de deploiement afin de couvrir tous
les logs pour lesquels Logminer est concu, sans se limiter aux exemples du
laboratoire.

## Installation Offline

Pour un serveur sans Internet, fournir:

- paquet `.deb` ou `.rpm` local;
- dependances empaquetees ou depot local;
- image Docker Redis exportee si necessaire;
- modeles `.joblib`;
- assets dashboard;
- checksums et signature du paquet;
- guide d'importation des images et dependances.

## Commandes Cibles

Exemples attendus:

```bash
sudo dpkg -i logminer_<version>_amd64.deb
sudo systemctl enable --now logminer
sudo systemctl status logminer
logminer health
logminer discover
logminer uninstall
```

## Desinstallation

La desinstallation doit:

- arreter le service;
- desactiver systemd;
- supprimer les fichiers applicatifs;
- demander si les donnees dans `/var/lib/logminer` et `/var/log/logminer`
  doivent etre conservees;
- produire un rapport si necessaire.

## A Valider Avant Livraison

- installation sur machine Linux propre;
- installation offline;
- verification Docker/Redis;
- fonctionnement degrade si Redis manque;
- service systemd stable apres redemarrage;
- decouverte automatique des logs standards;
- respect des permissions et des chemins Linux;
- generation d'un rapport d'analyse complet.
