# Phase CNP endurance

Cette phase contient la campagne d'endurance d'une heure de l'architecture
Contract Net actuelle, son protocole et ses artefacts de preuve.

Campagne canonique :

- deux agents executes sur les VM Debian et Ubuntu ;
- Redis centralise sur l'hote du laboratoire ;
- taches CNP cadencees pendant une heure ;
- checkpoints atomiques toutes les cinq minutes ;
- test terminal d'interruption apres persistance du resultat et avant emission
  de `RESULT` ;
- reattribution a l'autre VM et controle d'unicite de l'effet ;
- ledger append-only et manifeste SHA-256.

Cette campagne evalue l'endurance et la reprise de la topologie de laboratoire.
Elle ne demontre ni la haute disponibilite de Redis ni un deploiement industriel.

## Run canonique

Le run de reference est `cnp_endurance_multivm_20260918T130822Z` :

- 3 605,110 s observes pour une cible de 3 600 s ;
- 1 800 taches reussies sur 1 800 ;
- debit de 0,499291 tache/s ;
- latences mediane/p95/p99 de 53,983/156,3017/836,72528 ms ;
- 451 taches executees par Debian et 1 349 par Ubuntu ;
- crash controle apres persistance et avant `RESULT`, reattribution reussie,
  rejeu idempotent, un effet persistant et zero doublon.

La trace de messages du run conserve seulement sa fenetre terminale de 10 001
evenements en raison de la retention approximative configuree sur les agents.
Ses compteurs par type ne sont donc pas utilises pour les conclusions. Les
metriques par tache, le resultat du test de reprise et l'etat d'idempotence sont
complets.

Les artefacts suivent `experiments/ARTIFACT_NAMING_CONVENTION.md`.
