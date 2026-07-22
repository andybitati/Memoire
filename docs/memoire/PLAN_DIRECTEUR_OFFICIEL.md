# Plan Directeur Officiel Du Memoire

Source: document directeur local, extrait dans
`document_directeur_extrait.txt`, section "Structure detaillee du memoire".

Ce fichier doit etre considere comme le plan de redaction prioritaire par tout
outil de redaction, y compris ChatGPT. Le fichier `plan.md` du pack est une
adaptation operationnelle alignee sur ce plan directeur et sur les resultats
reels du prototype Logminer.

## Sujet

Detection Autonome et Distribuee d'Anomalies dans les Journaux Systemes et
Reseaux a l'aide d'Agents Intelligents Multi-Taches.

## Objectifs Principaux Du Memoire

1. Comprendre les types et structures de journaux systeme/reseau.
2. Analyser les techniques classiques et modernes de detection d'anomalies.
3. Developper une architecture distribuee d'agents IA specialises.
4. Integrer un mecanisme d'apprentissage pour la detection adaptative.
5. Concevoir un tableau de bord pour visualiser les alertes et anomalies.
6. Tester le systeme sur des logs simules et reels.
7. Evaluer la performance du systeme: precision, rappel, F1-score, latence,
   comparaison avec des outils classiques.

## Structure Detaillee Du Memoire

### Chapitre 1 - Introduction

- Contexte general.
- Problematique.
- Objectifs et contributions.
- Methodologie.
- Plan du memoire.

Points a couvrir:

- importance de la cybersecurite dans les infrastructures modernes;
- role central des journaux systemes et reseaux;
- surcharge de logs et manque de personnel qualifie;
- besoin d'automatisation et d'intelligence dans l'audit de logs;
- formulation de la problematique:
  "Comment concevoir un systeme intelligent, distribue, capable de detecter de
  maniere autonome des anomalies dans des journaux heterogenes, en temps
  quasi-reel ?";
- presentation des objectifs specifiques;
- organisation des chapitres.

### Chapitre 2 - Etat De L'Art

- Journaux systeme et reseau.
- Methodes classiques de detection d'anomalies.
- Intelligence artificielle appliquee aux logs.
- Systemes multi-agents intelligents.
- Synthese comparative.

Points a couvrir:

- formats de logs: syslog, Windows Event Log, Apache, JSON, CSV, reseau;
- detection par regles, seuils, statistiques, heuristiques;
- machine learning et deep learning pour les logs;
- agents intelligents et architectures distribuees;
- limites des approches existantes: faux positifs, heterogeneite, volume,
  besoin de labels, manque d'explicabilite.

### Chapitre 3 - Modele Propose

- Architecture generale.
- Description des agents et de leurs roles.
- Modeles de detection implementes.
- Flot de traitement et diagrammes d'interaction.

Points a couvrir:

- architecture multi-agents Logminer;
- agents: collecte, parsing, normalisation, routage, detection, correlation,
  audit, dashboard;
- schema commun de normalisation;
- routage multi-modeles par famille de journaux;
- communication entre agents;
- passage V1 CLI vers V2 FastAPI;
- Redis Streams et MQTT comme extensions operationnelles locales;
- limites: distribution multi-machine stricte a presenter comme perspective.

### Chapitre 4 - Implementation

- Outils utilises.
- Description du code et scripts.
- Jeux de donnees et tests preliminaires.
- Problemes rencontres.

Points a couvrir:

- organisation du depot;
- modules principaux du code;
- API FastAPI;
- dashboard web Ariel Logminer;
- parsing multi-format;
- modeles charges et registre des modeles;
- scripts d'experimentation;
- audit et decisions analyste;
- captures dashboard.

### Chapitre 5 - Resultats Et Evaluation

- Evaluation quantitative: precision, rappel, F1-score.
- Evaluation qualitative: visualisation, analyse contextuelle.
- Comparaison avec outils existants.

Points a couvrir:

- protocole experimental;
- datasets utilises;
- resultats supervises: Linux/auth, CICIDS2017, UNSW/CIC-DDoS;
- resultats non supervises: Wazuh, HDFS, BGL, Windows;
- benchmark temps reel;
- campagne CPU/RAM multi-cycles;
- robustesse multi-format;
- faux positifs;
- comparaison mesuree avec fail2ban-like, OSSEC/Wazuh et outils standards;
- distinction entre anomalie candidate et intrusion confirmee.

### Chapitre 6 - Conclusion Et Perspectives

- Resume des resultats.
- Apports reels.
- Limites.
- Perspectives futures.

Points a couvrir:

- bilan par rapport aux objectifs;
- apports du prototype Logminer;
- limites scientifiques et techniques;
- distribution multi-machine;
- reduction des faux positifs;
- apprentissage actif ou incremental;
- integration SOC/SIEM;
- cartographie MITRE ATT&CK;
- tests de charge prolonges et resilience.

### Annexes

- Codes.
- Captures de simulation.
- Parametres experimentaux.
- Tableaux complets.
- Figures.
- Commandes de reproduction.
- References.

## Plan De Travail Directeur

Le document directeur prevoit une progression en 7 mois:

| Periode | Taches principales |
| --- | --- |
| Mois 1, S1-S2 | Revue bibliographique sur detection d'anomalies et logs |
| Mois 1, S3-S4 | Collecte et nettoyage de jeux de logs |
| Mois 2, S5-S6 | Implementation de l'architecture multi-agents |
| Mois 2, S7-S8 | Parsing automatique des logs |
| Mois 3, S9-S10 | Implementation des modeles IA |
| Mois 3, S11-S12 | Tests sur logs simules et comparaison baseline |
| Mois 4, S13-S14 | Integration agents et communication |
| Mois 4, S15-S16 | Creation du tableau de bord dynamique |
| Mois 5, S17-S18 | Tests sur logs reels et ajustements |
| Mois 5, S19-S20 | Analyse de performance et metriques |
| Mois 6, S21-S22 | Redaction chapitres 1 a 4 |
| Mois 6, S23-S24 | Article 1 IEEE |
| Mois 7, S25-S26 | Article 2 et finalisation memoire |
| Mois 7, S27-S28 | Relecture, depot final, slides et soutenance |

## Regle De Redaction

La redaction finale doit suivre ce plan directeur, mais les formulations
doivent rester conformes aux preuves disponibles dans le pack. Ne pas inventer
de resultats non presents dans les tableaux, figures, captures ou CSV.


