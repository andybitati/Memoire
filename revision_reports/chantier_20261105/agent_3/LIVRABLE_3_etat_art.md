# LIVRABLE 3 — État de l'art et positionnement

Agent : 3 — État de l'art et positionnement  
Date : 2026-11-05  
Statut : **complet**  
Périmètre : chapitre 1 du PDF (`chapitre2_etat_art.tex`), §1.23/positionnement et chapitre 6 (`chapitre6_discussion.tex`), avec C5 et C12. Aucun `.tex` du manuscrit n'a été modifié.

## 1. Diagnostic traité

Les trois retours convergent sur cinq défauts de l'état de l'art actuel :

1. Le lecteur 1, B.1, relève que la lacune est « plausible » mais insuffisamment démontrée et demande une comparaison avec Wazuh, Elastic Security et OpenSearch Security Analytics.
2. Le lecteur 2, §2.2, qualifie le chapitre 1 de « manuel » : cadres intégrés, ECS/OCSF, corrélation d'alertes, sémantique de livraison/idempotence, gouvernance/MLOps et critiques de CSE-CIC-IDS2018 sont absents ; le chapitre 6 ne cite aucune référence.
3. Le lecteur 2 demande de comparer l'architecture multi-agents à son vrai concurrent : file de tâches et routage statique (Celery, Kafka, Redis, moteurs de workflow).
4. Le lecteur 3 conteste que l'intégration soit une contribution nouvelle et observe que le prototype se rapproche d'une file avec routeur à règles.
5. C5 affecte à l'Agent 3 la gouvernance/MLOps, l'insuffisance bibliographique et le caractère non contradictoire du chapitre ; C12 impose de reprendre dans le tableau 1.3 les restrictions rédigées par l'Agent 2.

Le diagnostic de fond est accepté : l'existence de plateformes intégrées interdit d'affirmer un vide fonctionnel. Le positionnement défendable est celui d'un **prototype d'intégration instrumenté pour l'étude critique de chaînes légères**, sans nouvel algorithme, nouveau schéma ou preuve de supériorité multi-agent.

## 2. Corrections proposées

### 2.1 CSE-CIC-IDS2018

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__csecic_critiques.tex`.

Le paragraphe actuel ne cite que les producteurs du jeu. La nouvelle sous-section ajoute Liu et al. (IEEE CNS 2022), qui documentent des erreurs d'orchestration, de génération des caractéristiques, de documentation et d'étiquetage dans CICIDS2017 et CSE-CIC-IDS2018. Elle positionne les expériences du mémoire comme un audit local de validité externe, non comme une preuve générale de transfert.

### 2.2 Normalisation : ECS et OCSF

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__normalisation_ecs_ocsf.tex`.

La section actuelle définit un noyau local sans le confronter aux standards existants. La nouvelle version :

- distingue parsing, projection et normalisation sémantique ;
- compare ECS, OCSF et le contrat local dans un tableau ;
- rappelle que les extensions et la conservation du brut sont nécessaires ;
- définit une preuve de conformité champ par champ (présence, type, sémantique, provenance, taux de remplissage) ;
- rattache le constat 0/7 champs sur les flux tabulaires à une **projection commune partielle**, sans revendiquer une conformité ECS/OCSF.

### 2.3 Cadres intégrés et bibliothèques

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__cadres_integres.tex`.

La section compare :

- Wazuh : agents, serveur d'analyse, indexeur, dashboard et déploiements en grappe ;
- Elastic Security : ECS, règles, corrélation, alertes et investigation ;
- OpenSearch Security Analytics : types de journaux, détecteurs, règles, constats, alertes et corrélation ;
- LogAI : prétraitement et tâches d'analyse sous interface commune ;
- Loglizer : boîte à outils de détection d'anomalies sur journaux.

La comparaison est fonctionnelle, pas expérimentale. Elle dit explicitement qu'Ariel Logminer n'a pas été comparé à ces cadres et ne peut donc revendiquer de les remplacer ou de les dépasser.

### 2.4 Multi-agents, vrais concurrents et livraison

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__multiagents_concurrents_livraison.tex`.

Il remplace les deux sections descriptives « Systèmes multi-agents » et « Bus de messages » par une discussion contradictoire :

- propriétés théoriques d'un agent selon Wooldridge ;
- Contract Net de Smith et actes FIPA ;
- comparaison avec table statique, files nommées, groupes de consommateurs et moteurs de workflow ;
- tableau des décisions d'affectation et questions comparatives ;
- distinction au-plus-une-fois / au-moins-une-fois / exactement-une-fois ;
- séparation du rôle du broker, du magasin d'idempotence et de l'effet métier.

La conclusion est restrictive : sans ablation changeant uniquement la politique d'affectation, l'échange Contract Net est une réalisation, pas une preuve de supériorité. L'idempotence est une propriété de l'opération ou du magasin, transposable au monolithe et aux workers.

### 2.5 Corrélation d'alertes

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__correlation_alertes.tex`.

La section actuelle ne cite aucun travail. La nouvelle version mobilise Cuppens et Miège (2002) ainsi que Valeur et al. (2004) pour distinguer gestion, regroupement, fusion, corrélation de scénarios, vérification et priorisation. Elle classe le corrélateur d'Ariel Logminer comme une règle temporelle et contextuelle, non causale, puis relie sa fragmentation des incidents multi-étapes à la baseline « hôte + fenêtre » qui le dépasse.

### 2.6 Gouvernance et MLOps

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__gouvernance_mlops.tex`.

La section ajoute les travaux de Sculley et al. sur la dette technique, Breck et al. sur les tests et le monitoring, Amershi et al. sur le génie logiciel des systèmes ML, et le NIST AI RMF. Elle définit un cycle minimal : provenance et versions, jeu gelé, règle définie avant évaluation, métriques, décision, surveillance, retrait et retour arrière. Le registre et le `dry-run` du prototype sont qualifiés de briques, pas de plateforme MLOps validée.

### 2.7 Lacune et positionnement — reprise C12

Fichier prêt à intégrer : `sections/chapitre2_etat_art.tex__lacunes_positionnement.tex`.

La « fragmentation des fonctions » n'est plus présentée comme une absence de solution. La tension retenue oppose :

- des travaux algorithmiques qui isolent le détecteur ;
- des plateformes intégrées qui ne constituent pas nécessairement des protocoles de recherche contrôlés.

Le positionnement devient une contribution d'ingénierie expérimentale, valable seulement lorsque des comparateurs excluent les explications triviales.

Le tableau 1.3 reprend intégralement les quatre corrections imposées par C12 :

- hétérogénéité limitée à des formats traités séparément ;
- mémoire sans gain d'attribution démontré ;
- priorisation prévue mais non mesurée ;
- dashboard fonctionnel sans étude utilisateur.

Il ajoute normalisation, gouvernance et l'absence d'avantage établi sur une table statique.

### 2.8 Chapitre 6 : discussion référencée

Fichier prêt à intégrer : `sections/chapitre6_discussion.tex__chapitre_complet.tex`.

Le chapitre actuel ne contient aucune citation et répète principalement les résultats. La version proposée remplace tout le fichier et organise la discussion autour de tensions établies dans la littérature :

1. validité du protocole plutôt que score isolé ;
2. intégration existante dans les plateformes ;
3. Contract Net contre affectation statique ;
4. transport, reprise et idempotence ;
5. hétérogénéité, schémas et corrélation ;
6. mémoire, MLOps et rôle de l'analyste ;
7. nature exacte de la contribution et menaces à la validité ;
8. expériences réellement décisives à conduire.

La discussion ne présente pas les résultats négatifs comme une nouveauté conceptuelle : elle les qualifie de réplications et d'audits locaux. Elle distingue systématiquement mécanisme réalisé, bénéfice mesuré et propriété non testée.

## 3. Bibliographie étendue et normée

Fichier : `references_proposees.bib` — **18 nouvelles entrées** BibTeX.

### Publications originales ajoutées

- Cuppens et Miège, IEEE Symposium on Security and Privacy, 2002, DOI `10.1109/SECPRI.2002.1004372`.
- Valeur et al., IEEE TDSC, 2004, DOI `10.1109/TDSC.2004.21`.
- Liu et al., IEEE CNS, 2022, DOI `10.1109/CNS56114.2022.9947235`.
- Cheng et al., LogAI, 2023, DOI `10.48550/arXiv.2301.13415`.
- Sculley et al., NeurIPS, 2015.
- Breck et al., IEEE Big Data, 2017, DOI `10.1109/BigData.2017.8258038`.
- Amershi et al., ICSE-SEIP, 2019, DOI `10.1109/ICSE-SEIP.2019.00042`.
- NIST AI RMF 1.0, DOI `10.6028/NIST.AI.100-1`.

### Documentations officielles ajoutées

- ECS, OCSF, Wazuh, Elastic Security, OpenSearch Security Analytics ;
- Loglizer (dépôt officiel associé à l'article déjà présent) ;
- Apache Kafka, Redis Streams, Celery et Temporal.

Ces documentations servent uniquement à décrire des fonctions et garanties publiées par leurs mainteneurs. Elles ne sont pas utilisées comme preuves d'une supériorité empirique.

## 4. Ordre d'intégration recommandé

1. Fusionner `references_proposees.bib` dans `ARIEL_LOGMINER_MEMOIRE_FINAL/references.bib` en vérifiant l'absence de clés dupliquées.
2. Remplacer la sous-section CSE-CIC-IDS2018.
3. Remplacer la section de normalisation.
4. Insérer la section sur les cadres intégrés avant « Systèmes multi-agents ».
5. Remplacer « Systèmes multi-agents » + « Bus de messages » par le fichier agents/concurrents/livraison.
6. Remplacer la section de corrélation.
7. Remplacer la section de gouvernance.
8. Remplacer « Lacunes identifiées » + « Positionnement » ; ne pas intégrer séparément le fichier C12 de l'Agent 2, déjà absorbé.
9. Remplacer entièrement `chapitre6_discussion.tex`.
10. Compiler `pdflatex → bibtex → pdflatex ×2` et contrôler les doublons de labels `tab:positionnement-logminer`, `tab:schemas-normalisation`, `tab:cadres-integres`, `tab:concurrents-orchestration`.

## 5. Validation

Une compilation isolée a été effectuée dans `agent_3/` avec `validation_agent3.tex`, les 8 sections proposées, la bibliographie actuelle du mémoire et `references_proposees.bib` :

- `pdflatex`, `bibtex`, puis deux passes `pdflatex` ;
- 0 erreur fatale ;
- 0 citation indéfinie ;
- 0 référence indéfinie ;
- 0 débordement horizontal (`Overfull \hbox`).

Les avertissements de boîtes insuffisamment remplies dans les tableaux et les URL ne bloquent pas l'intégration. Le warning MiKTeX `log4cxx ... Accès refusé` concerne son journal global ; la compilation et le PDF de validation ont abouti.

## 6. Points en suspens et dépendances

1. **Agent 4 / coordinateur** : si les expériences C13 modifient le statut de H3/H4 ou introduisent une baseline HDFS forte, mettre à jour les phrases correspondantes du chapitre 6 avant intégration. Le texte fourni décrit fidèlement l'état du corps au moment de la remise.
2. **Agent 5 / coordinateur** : la discussion dit que l'avantage de Contract Net sur l'affectation statique n'est pas établi. Si E-CNP est exécutée après cette remise, remplacer cette phrase par le résultat préenregistré, quel qu'il soit.
3. **Coordinateur** : l'insertion du tableau 1.3 de ce livrable remplace le fichier C12 de l'Agent 2 ; ne pas appliquer les deux.
4. **Agent 7** : les entrées BibTeX utilisent `and` comme séparateur BibTeX normalisé. L'affichage final en français relève du style bibliographique, pas d'une substitution dans les champs `author`.

## 7. Décisions de l'Agent 3

| # | Décision | Justification |
|---|---|---|
| A3-1 | Abandonner la lacune « aucune plateforme intégrée » ; positionner le travail comme banc d'intégration instrumenté. | Wazuh, Elastic Security et OpenSearch couvrent déjà une grande partie de la chaîne. |
| A3-2 | Ne revendiquer ni conformité ECS/OCSF ni normalisation complète. | Le contrat est local et les flux tabulaires renseignent 0/7 champs mesurés. |
| A3-3 | Traiter table statique, files spécialisées, groupes de consommateurs et workflow durable comme concurrents directs de Contract Net. | Ils fournissent allocation, acquittement ou reprise sans négociation multi-agent. |
| A3-4 | Attribuer l'idempotence au magasin/opération, et la réattribution au transport/orchestrateur. | La panne appariée montre que le même magasin protège aussi A et B. |
| A3-5 | Classer le corrélateur comme temporel/contextuel, non causal. | Il regroupe par fenêtre et égalité de clés, sans préconditions ni scénario d'attaque. |
| A3-6 | Qualifier registre, `dry-run` et promotion de support expérimental de gouvernance. | Aucun cycle complet de monitoring, décision, déploiement et rollback n'est démontré. |
| A3-7 | Absorber le tableau C12 de l'Agent 2 dans un tableau 1.3 étendu. | Évite deux modifications concurrentes du même passage et conserve les quatre restrictions imposées. |

=== PASSATION ===
Agent : 3 — État de l'art et positionnement
Statut : terminé
Livrables : `agent_3/LIVRABLE_3_etat_art.md` ; `agent_3/references_proposees.bib` ; `agent_3/sections/` (8 fichiers) ; `agent_3/validation_agent3.tex` et PDF/journal de validation
Prochain agent recommandé : 5 — Architecture multi-agents : preuves et limites
Raison : l'état de l'art établit les comparateurs conceptuels ; l'Agent 5 doit désormais confronter Contract Net à l'affectation statique et actualiser la discussion si E-CNP change le constat.
Points de vigilance pour le repreneur : ne pas intégrer deux fois le tableau C12 ; mettre à jour le chapitre 6 après les expériences C13 ; conserver la distinction broker/magasin/agent ; aucune supériorité sur les plateformes intégrées n'est démontrée.
=== FIN PASSATION ===
