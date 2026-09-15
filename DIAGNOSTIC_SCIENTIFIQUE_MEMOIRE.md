# Diagnostic scientifique et plan de correction du mémoire Ariel Logminer

Périmètre audité : projet LaTeX `memoire_logminer_latex_overleaf`, chapitres, annexes, bibliographie, figures, captures, tableaux Markdown et principaux artefacts de preuve présents dans le dépôt. Ce rapport ne réécrit pas le mémoire et ne modifie aucune valeur numérique.

## 1. Diagnostic exécutif

Le mémoire possède un noyau scientifique défendable : une contribution d'intégration architecturale, un prototype effectivement implémenté, des artefacts expérimentaux nombreux et une prudence déjà explicite sur les anomalies candidates, la généralisation et l'absence de gain automatique des agents. Le contraste CICIDS2017 entre séparation aléatoire et holdout strict est le résultat méthodologique le plus fort.

Le document n'est toutefois pas prêt pour dépôt. Les risques principaux sont :

1. une contradiction sur le statut multi-VM entre le résumé, le chapitre 8 et les annexes ;
2. des résultats annoncés dans le résumé ou la discussion mais absents du chapitre 5, notamment LogisticRegression à 0,233670, l'ablation du routage et la campagne multi-VM d'une heure ;
3. un contrat de message décrit au §3.14 qui ne correspond pas exactement à la structure `AgentMessage` implémentée ;
4. une narration V1/V2/V3 encore présente dans le texte, un tableau et plusieurs captures/figures ;
5. une reproductibilité surtout prescriptive : le chapitre 8 dit ce qu'il faudrait figer, sans fournir systématiquement le commit, les versions, le matériel et les empreintes effectivement utilisés ;
6. l'absence d'attribution dans les légendes de toutes les figures et de tous les tableaux ;
7. l'absence de déclaration d'assistance par IA générative ;
8. des figures obsolètes ou scientifiquement ambiguës ;
9. une bibliographie cohérente au niveau des clés, mais insuffisante pour plusieurs technologies et jeux de données décrits ;
10. de fortes répétitions entre les chapitres 5, 6, 7 et 9.

Verdict : contribution crédible, présentation scientifique encore fragile. Les P0 doivent être fermés avant toute réécriture stylistique.

## 2. Forces réelles du mémoire

- La contribution est correctement recentrée sur l'architecture d'intégration, et non sur un nouvel algorithme (chapitre 1, §1.6 ; conclusion, §9.1).
- Le manuscrit distingue généralement anomalie candidate, alerte, incident et intrusion confirmée (chapitre 3, §3.13 ; chapitre 5, §§5.5–5.7).
- Le résultat négatif CICIDS2017 est exposé et interprété, sans être masqué (chapitre 5, tableaux 5.5 et 5.6).
- La comparaison monolithique/agents reconnaît explicitement le surcoût d'orchestration et l'absence de gain de débit sur la faible charge étudiée (chapitre 5, tableau 5.13).
- La campagne Redis de six heures fournit une preuve directe de consommation concurrente, d'acquittement et de reprise locale après panne simulée (chapitre 5, tableau 5.12).
- HDFS/BGL distinguent désormais une phase exploratoire d'une évaluation entraînement–test avec Drain3 (chapitre 5, tableaux 5.10 et 5.11).
- Les scripts, CSV, JSON et tableaux de preuve constituent une base sérieuse de traçabilité.
- Les limites sur l'industrialisation, l'étude utilisateur et la généralisation sont souvent formulées avec prudence.
- Les 29 clés citées existent toutes dans la bibliographie ; aucune entrée bibliographique n'est non citée et aucune citation textuelle n'est orpheline.

## 3. Faiblesses de présentation

- Le chapitre 5 est une succession de jeux de données et de campagnes plutôt qu'une réponse structurée à des questions scientifiques.
- Le résumé est trop long et contient des résultats non développés dans le corps.
- Le lecteur doit attendre les chapitres 6 et 7 pour comprendre quels résultats sont réellement majeurs.
- Les tableaux et figures sont presque jamais appelés dans le texte : 43 labels ont été relevés, mais seulement cinq renvois `\ref` sont présents ; 38 labels ne sont jamais référencés.
- Les légendes décrivent souvent le thème sans rappeler le protocole indispensable à l'interprétation.
- Plusieurs figures utilisent l'anglais dans un mémoire français.
- Les sections « Rôle du chapitre », « Objectif du chapitre » et plusieurs phrases méta-rédactionnelles expliquent la fabrication du document au lieu de porter l'argument scientifique.
- Le terme `Logminer` est stable via la macro, mais les captures affichent aussi « ARIEL LOGMINER DIGITAL DATA MINING », « SOC V2 », « Services V2 », « Détecteur IA » et « Modèles IA », ce qui crée des registres terminologiques différents.

## 4. Problèmes scientifiques

| Priorité | Localisation | Extrait minimal | Problème | Action |
|---|---|---|---|---|
| P0 | Résumé, `main.tex:214` | « LogisticRegression… 0,233670 » | Résultat absent du chapitre 5. | Ajouter l'expérience complète au chapitre 5 ou retirer cette revendication du résumé. |
| P0 | Résumé, `main.tex:218` | « campagne… multi-VM » | Le chapitre 5 ne présente ni protocole ni tableau multi-VM. | Intégrer protocole, preuve et limites, ou supprimer du résumé. |
| P0 | Ch. 8, §8.7, lignes 235–239 ; annexes §A.7 | « servaient… future évolution » / « expériences multi-VM montrent » | Contradiction interne sur l'existence d'une preuve multi-VM. | Établir une chronologie factuelle des campagnes éligibles. **INFORMATION À VÉRIFIER**. |
| P0 | Ch. 3, §3.14, lignes 440–450 ; `src/logminer/agents/bus.py:29–39` | « identifiant… métadonnées » | Le texte ne correspond pas au contrat implémenté : le code expose `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`, sans champ `metadata` ni identifiant d'événement autonome. | Aligner exactement le mémoire sur le code ou versionner/étendre le contrat, puis tester. |
| P0 | Ch. 5, §5.4 | « ablation modèle global/familles » | L'ablation est annoncée dans la configuration et discutée aux ch. 6–7, mais ses résultats ne figurent pas au ch. 5. | Insérer le résultat contrôlé et distinguer l'ablation à espace commun de la comparaison opérationnelle. |
| P0 | Ch. 5, §5.4, lignes 221–225 | « jeu compatible avec CIC-DDoS2019 » | Provenance scientifique ambiguë du score 0,999965 ; l'expression ne garantit pas qu'il provient du jeu officiel. | Documenter précisément le fichier/source, ou conserver uniquement le résultat strict traçable. **INFORMATION À VÉRIFIER**. |
| P0 | Ch. 6, §6.6, dernière phrase | « apprentissage continu auditable » | Contradiction avec les passages qui disent que le système ne réalise pas d'apprentissage continu automatique. | Reclasser comme boucle de mise à jour contrôlée, tant qu'une campagne complète n'est pas démontrée. |
| P1 | Ch. 4, §4.7 et ch. 8, §8.6 | mise à jour mensuelle | Le mécanisme est implémenté, mais aucune campagne de promotion/rejet de modèle n'est présentée. | Classer `IMPLÉMENTÉ / NON ÉVALUÉ`, sauf preuve additionnelle. |
| P1 | Ch. 4, §4.6 ; conclusion §9.3 | « mémoire adaptative » | L'effet réel des retours analyste n'est pas évalué ; l'ablation disponible utilise 0 décision réelle et 15 décisions simulées. | Distinguer mémoire persistante, règle de priorisation et effet sur les modèles. |
| P1 | Ch. 5, §5.14 | « validation progressive » | Configurations, volumes et charges non appariés ; ce n'est pas une ablation. | Supprimer du corps ou déplacer en annexe comme validation fonctionnelle. |
| P1 | Ch. 5, §5.15 | « robustesse » | La figure repose sur 1 ou 2 lignes normalisées par format ; cela démontre un smoke test, pas une robustesse générale. | Renommer le statut de preuve ou renforcer expérimentalement. |
| P1 | Ch. 7, §7.2 | « améliore… modularité » | Modularité et traçabilité sont des propriétés de conception, pas des gains mesurés. | Employer « vise/facilite » ou définir des métriques architecturales. |
| P1 | Ch. 5, §5.8–5.10 | latence/CPU/RAM | Matériel, OS, versions et dispersion ne sont pas suffisamment fournis dans le corps. | Ajouter la fiche expérimentale réellement utilisée. |
| P1 | Ch. 5, §5.7 | Wazuh | Le recouvrement n'est pas une vérité terrain et la figure ne représente pas clairement un recouvrement ensembliste. | Définir les ensembles, le dénominateur et la métrique de recouvrement. |
| P1 | Ch. 3, §§3.6 et 3.15 | corrélation | Fonction implémentée, mais qualité des regroupements non évaluée. | Classer comme validation fonctionnelle, pas comme efficacité démontrée. |

## 5. Problèmes éditoriaux

- `main.tex:210` emploie « journaux systèmes et réseaux » alors que le titre emploie correctement « journaux système et réseau ». Uniformiser les adjectifs.
- Le nom des fichiers `chapitre6_*`/`chapitre7_*` ne suit pas le numéro réel des chapitres ; ce n'est pas visible dans le PDF, mais augmente le risque d'erreur de maintenance.
- Les chapitres 6 et 7 répètent presque mot pour mot les valeurs CICIDS2017, HDFS/BGL, Redis et monolithique/agents.
- Le chapitre 8 contient des consignes de mise en page, d'Overleaf et de relecture qui ne relèvent pas du contenu scientifique.
- L'annexe contient une checklist personnelle « Vérifications avant le dépôt » à supprimer entièrement du PDF.
- Les figures 3.1, 5.1–5.8 ne disposent d'aucune phrase de source dans la légende.
- La figure A.1 n'a pas de `\label`.
- Les titres génériques « Résultats principaux », « Validation progressive » ou « Robustesse » ne précisent pas la variable ou le protocole.
- Les chemins Windows absolus du chapitre 8 sont utiles seulement si présentés comme environnement observé, pas comme commande portable.

## 6. Problèmes d'autonomie documentaire

Le test du lecteur isolé échoue sur les points suivants :

- environnement expérimental exact non fourni : version de Python, versions effectivement utilisées, OS précis, CPU, RAM et commit ;
- provenance/empreinte des datasets et fichiers exacts non systématiquement indiquée ;
- ablation de routage, comparaison de candidats CICIDS2017 et campagne multi-VM seulement accessibles via des fichiers du dépôt, alors qu'elles sont revendiquées dans le PDF ;
- tableaux Markdown « conservés dans le dossier » non visibles pour le lecteur du seul PDF ;
- contrat de message renvoyant implicitement au code sans tableau de correspondance exact ;
- figure de robustesse sans taille d'échantillon explicite dans la légende ;
- propriétés de Redis, MQTT, FastAPI, Wazuh et des datasets non toutes soutenues par des références ;
- origine des figures, captures, logo et éventuelles illustrations IA non déclarée ;
- procédure de mise à jour des modèles décrite comme opérationnelle sans résultat d'exécution présenté.

## 7. Références externes implicites à supprimer

| Localisation | Dépendance | Statut | Action |
|---|---|---|---|
| Ch. 1, §1.5, ligne 73 | « conformément à notre cahier des charges » | Externe inutile | Supprimer la dépendance ; relier les objectifs aux questions et hypothèses. |
| Ch. 1, §1.8, ligne 147 | « structure définie dans le document directeur » | Externe inutile | Présenter directement l'organisation du mémoire. |
| Ch. 3, §3.17, ligne 548 | « objectif… défini dans le document directeur » | Externe inutile | Justifier l'adaptation par Q5/H5 et par l'architecture décrite. |
| Annexes, §A.7, ligne 225 | « cohérent… avec… document directeur » | Checklist privée | Supprimer toute la section du manuscrit. |

L'expression « document de référence » au chapitre 8, §8.2 désigne le manuscrit lui-même ; elle n'est pas une dépendance externe et peut être conservée si nécessaire.

## 8. Occurrences V1/V2/V3/version locale/version distribuée

Classification : A = nécessaire scientifiquement ; B = historique inutile ; C = ambiguë.

| Localisation | Extrait | Classe | Action |
|---|---|---:|---|
| Ch. 1, §1.3, ligne 27 | « version avancée du prototype » | B | Décrire directement l'exécution multiprocessus Redis. |
| Ch. 1, §1.4, ligne 57 | « progression fonctionnelle » | B | Remplacer par les expériences réellement comparables. |
| Ch. 1, §1.7, ligne 137 | « implémentation progressive » | B | Présenter la méthode de conception sans chronologie de versions. |
| Ch. 3, §3.7, ligne 265 | « version locale » | B | Nommer le mécanisme : fichiers CSV/JSONL. |
| Ch. 3, §3.7, ligne 267 | « version V2 » | B | Nommer FastAPI et le tableau de bord comme composants finaux. |
| Ch. 3, tableau 3.3 | « V1 / V2 / V3 » | B | Remplacer par un tableau composants–rôles–preuves–statut. |
| Ch. 3, §3.11, ligne 388 | « Dans la version locale » | B | Décrire les modes d'échange existants. |
| Ch. 3, §3.14, ligne 448 | « Dans la version locale » | B | Cartographier le contrat vers objets/JSONL/Redis/MQTT. |
| Ch. 3, §3.14, ligne 450 | « version plus distribuée » | B | Redis est déjà implémenté ; MQTT est optionnel et testé seulement par smoke test. |
| Ch. 4, §4.3, ligne 45 | « dans sa version locale » | B | Dire que `pipeline.py` orchestre le mode synchrone/local. |
| Ch. 4, §4.5, ligne 138 | « version avancée » | B | Décrire l'environnement d'agents comme implémentation finale. |
| Ch. 4, §4.9, ligne 235 | « services de la V2 » | B | Employer « services API et bus ». |
| Ch. 5, §5.13, ligne 777 | « avait auparavant… prévalidation » | B | Garder seulement la campagne principale ; déplacer le smoke test en annexe. |
| Ch. 5, §5.14, lignes 883–958 | « validation progressive… évolution » | B | Supprimer du corps ou reclasser comme historique de tests fonctionnels. |
| Ch. 6, §6.2, ligne 33 | « résultat exploratoire historique » | B/C | Retirer si la provenance reste ambiguë. |
| Ch. 8, §8.10, ligne 371 | « versions successives du système » | B | Parler de cycles de maintenance. |
| Ch. 8, §8.11, lignes 387–390 ; ch. 7, lignes 190–192 ; ch. 9, §9.4 | versions de modèles | A | Conserver : il s'agit du versionnement scientifique des artefacts ML, pas de l'histoire du produit. |
| Ch. 8, §8.12, ligne 423 | « version actuelle du mémoire » | B | Supprimer la méta-rédaction sur les articles. |
| Figure 3.1 | « V1 CLI », « V2 FastAPI », « V3 Redis/MQTT » | B, P0 | Remplacer la figure. Elle contient aussi des `\n` littéraux visibles. |
| Captures ch. 4/A | « SOC V2 », « Services V2 » | B | Régénérer les captures sans balises de version. |

## 9. Analyse détaillée du §3.7

Diagnostic : la section est effectivement un journal de développement. Elle mélange quatre dimensions différentes : stockage reproductible, API, bus de tâches et perspectives. Le tableau 3.3 accentue cette lecture générationnelle.

Décision sur le tableau : **C — remplacer** par un tableau de l'architecture finale.

Structure conceptuelle recommandée :

1. **Persistance et audit** : CSV/JSONL pour les résultats, traces et artefacts inspectables ; préciser qu'ils ne constituent pas le bus de workers distribués.
2. **Interface de services** : FastAPI déclenche/consulte les traitements et alimente le tableau de bord ; ce n'est pas un bus.
3. **Bus persistant de tâches** : Redis Streams, consumer groups, ACK, pending et `XAUTOCLAIM` ; preuve locale de six heures et, si retenue après vérification, preuve multi-VM distincte.
4. **Communication optionnelle** : MQTT est bien implémenté dans `MqttMessageBus`, exposé via `/mqtt/health` et `/mqtt/publish`, avec un smoke test local ; il n'a ni relecture historique ni campagne de performance. Statut : `IMPLÉMENTÉ / TEST FONCTIONNEL COURT / NON ÉVALUÉ À L'ÉCHELLE`.
5. **Limites** : sécurité du broker, authentification, chiffrement, back-pressure, dead-letter queue, partitions réseau et haute disponibilité non démontrés.

Colonnes du nouveau tableau : composant ; rôle ; support ; preuve d'implémentation ; expérience ; résultat ; statut (`DÉMONTRÉ`, `OBSERVÉ`, `NON ÉVALUÉ`, `PERSPECTIVE`) ; limite.

## 10. Analyse détaillée du §3.14

La structure logique proposée est pertinente, mais elle doit être alignée sur l'implémentation.

Contrat réellement visible dans `src/logminer/agents/bus.py:29–39` :

- `run_id` ;
- `source` ;
- `target` ;
- `message_type` ;
- `payload` ;
- `status` ;
- `timestamp`.

Écarts à corriger :

- le mémoire parle d'un « identifiant » générique, alors que le code porte un identifiant de run ; la traçabilité d'un événement individuel est **INFORMATION À VÉRIFIER** ;
- le mémoire annonce des « métadonnées », mais aucun champ `metadata` distinct n'existe dans `AgentMessage` ; elles peuvent être dans `payload`, ce qui doit être dit et vérifié ;
- `target` et `status`, présents dans le code, sont absents de la description ;
- CSV est une sortie tabulaire et non nécessairement une sérialisation fidèle du même message ; ne pas le présenter comme support équivalent sans mapping explicite ;
- Redis et MQTT sont déjà implémentés, donc la phrase « dans une version plus distribuée… pourrait » est factuellement dépassée ;
- l'identifiant natif Redis du message/job et l'acquittement appartiennent à l'enveloppe de transport et doivent être distingués du contrat métier.

Organisation recommandée : architecture logique commune ; schéma exact ; responsabilité de chaque producteur/consommateur ; mapping JSONL/Redis/MQTT ; propriétés de persistance et reprise ; limites et versionnement du schéma.

## 11. Audit des affirmations et preuves

| Affirmation | Section | Preuve disponible | Expérience/résultat | Confiance | Formulation défendable | Problème |
|---|---|---|---|---|---|---|
| Plusieurs formats sont ingérés | 4.4, 5.15 | Parseurs, pipeline, figure 5.8 | 1–2 lignes par format | OBSERVÉ | Plusieurs formats définis passent un test fonctionnel. | « robuste » est trop fort. |
| Schéma commun conservant l'original | 3.3, 4.4 | `schema/columns.py`, parseurs | Test multiformat | OBSERVÉ | Schéma implémenté et inspecté sur les cas testés. | Pas de mesure de perte d'information. |
| Routage par famille | 3.4, 4.5 | `model_router.py` | Tables Markdown d'ablation | DÉMONTRÉ fonctionnellement | Le routeur sélectionne une famille et un modèle compatible. | Résultats absents du ch. 5. |
| Routage supérieur au modèle global | 1.4, 6.6 | `family_routing_ablation.csv` | Performances proches | NON SOUTENU | Aucun gain systématique dans l'espace commun testé. | Ne pas revendiquer de supériorité. |
| Détection supervisée | 5.4 | CSV de métriques | Linux/auth, CICIDS2017, CIC-DDoS2019 | DÉMONTRÉ dans les protocoles | Performances observées sur les splits déclarés. | Généralisation limitée. |
| Généralisation CICIDS2017 | 5.4 | Tables 5.5–5.6 | 0,999260 vs 0,157827 | DÉMONTRÉ pour ce protocole | Forte dépendance aux scénarios vus à l'entraînement. | Résultat majeur, à mettre au centre. |
| Meilleur candidat LogisticRegression | Résumé | table/CSV candidats | F1 0,233670 | OBSERVÉ | Meilleur parmi les candidats légers testés. | Expérience absente du corps. |
| Détection Wazuh | 5.6 | export/table Wazuh | 3 676/122 563 | OBSERVÉ | Le modèle signale des anomalies candidates. | Pas de vérité terrain. |
| Recouvrement Wazuh | 5.6, fig. 5.3 | table overlap | Comptes par groupes | SUGGÉRÉ | Certains groupes Wazuh concentrent les candidats. | « recouvrement » non défini. |
| Faux positifs comparables | 5.7, fig. 5.4 | métriques agrégées | familles hétérogènes | NON ÉVALUÉ de façon homogène | Rapporter séparément par protocole labellisé. | Comparaison transversale trompeuse. |
| HDFS/BGL séquentiel amélioré par Drain3 | 5.11 | CSV train–test | HDFS 0,652789 ; BGL 1,000000 | OBSERVÉ | Résultats observés sur la partition décrite. | Validation distincte et répétitions manquantes. |
| Corrélation produit des incidents utiles | 3.6, 4.10 | code + captures | Aucun indicateur de qualité | NON ÉVALUÉ | Corrélation fonctionnelle simple. | Utilité analytique non démontrée. |
| Agents multitâches | 4.5, 5.13 | runtime, handlers | tâches `discover/parse/route` | DÉMONTRÉ sur périmètre | Plusieurs types de tâches sont exécutés par les agents testés. | Étendue complète détection/corrélation à vérifier. |
| Redis répartit les tâches localement | 5.12 | JSON campagne | 8 508 tâches ; 709 reprises | DÉMONTRÉ localement | Distribution multiprocessus locale et reprise observées. | Pas industrialisable par extrapolation. |
| Agents améliorent le débit | 5.13 | comparaison contrôlée | débit inférieur | NON SOUTENU | Un surcoût est observé à faible charge. | Résultat négatif à conserver. |
| Multi-VM | Résumé, annexes | trois tables/JSON de preuve | 12 tâches ; reprise ; 525 tâches/1 h | OBSERVÉ dans les artefacts | Une campagne de laboratoire multi-VM semble avoir été exécutée. | Corps absent/contradictoire. **INFORMATION À VÉRIFIER**. |
| Heartbeat | 1.3, 4.5 | runtime/API | état visible | DÉMONTRÉ fonctionnellement | Heartbeat implémenté et observable. | Pas d'évaluation de délai/détection de panne. |
| Audit | 3.7, 4.10 | `audit.py`, dashboard | capture et journaux | DÉMONTRÉ fonctionnellement | Les opérations et décisions prévues sont journalisées. | Exhaustivité/intégrité non testées. |
| Mémoire persistante | 3.17, 4.6 | `AgentMemory`, `SupervisorMemory` | persistance JSON | DÉMONTRÉ fonctionnellement | Historique conservé entre cycles. | Ne pas assimiler à apprentissage. |
| Mémoire améliore la priorisation | 1.4, 4.6 | ablation feedback | 0 décision réelle, 15 simulées | SUGGÉRÉ | Effet de sensibilité observé avec feedback simulé. | Aucun bénéfice réel analyste démontré. |
| Mise à jour contrôlée | 4.6, 8.6 | script + plan | dry-run/artefacts de code | NON ÉVALUÉ | Procédure implémentée pour comparer courant/candidat. | Aucun résultat de promotion/rejet présenté. |
| Tableau de bord exploitable | 4.9, 7.3 | captures/API | validation fonctionnelle | OBSERVÉ | Interface consultable et interactive. | Pas d'étude d'utilisabilité. |
| Reproductibilité | 8, annexes | scripts et artefacts | partielle | SUGGÉRÉ | Plusieurs résultats sont retraçables. | Environnement exact non figé dans le PDF. |
| MQTT | 3.7, 4.8, 8.9 | code, compose, endpoints, smoke test | publication locale | OBSERVÉ fonctionnellement | Bus pub/sub optionnel testé localement. | Pas de benchmark ni de preuve distribuée. |

## 12. Audit des citations

Constat positif : 29 clés citées, 29 entrées BibTeX, aucune clé manquante, aucune entrée non citée, aucun doublon de clé.

Corrections requises :

- ajouter une source primaire pour HDFS et BGL et leur protocole de référence ;
- ajouter la publication/source officielle de CIC-DDoS2019 ;
- citer les documentations officielles pour les propriétés attribuées à Windows Event Log, Apache, Wazuh/OSSEC, FastAPI, Redis Streams/consumer groups/`XAUTOCLAIM`, MQTT et Mosquitto ;
- soutenir ou atténuer l'affirmation générale selon laquelle l'apprentissage profond exige davantage de données et de calcul ;
- soutenir les affirmations comparatives sur la maturité et les fonctions des SOC/HIDS/SIEM ;
- vérifier la notice `axelsson2000intrusion`, actuellement typée `@article` avec `journal={Technical Report}` ;
- vérifier le type BibTeX de `sommer2010outside`, actuellement `@article` alors qu'il s'agit d'une conférence ;
- vérifier l'année/clé `he2016drain` : clé 2016, notice 2017 ; ce n'est pas bloquant techniquement, mais peut troubler la lecture ;
- vérifier intégralement les métadonnées de `vyas2026acnd`. **INFORMATION À VÉRIFIER** ;
- harmoniser l'usage DOI/URL et compléter les champs manquants des conférences.

Ne pas ajouter de citation aux choix propres du prototype lorsqu'ils sont clairement annoncés comme décisions de conception.

## 13. Audit des figures et sources

Seize environnements `figure` sont présents. Aucune légende ne contient une attribution de source. Le fichier externe `IMAGE_ASSETS.md` ne remplace pas une attribution dans le PDF.

| Figure | Diagnostic | Classe | Action |
|---|---|---|---|
| Logo page de garde | Origine et droits non documentés. Aspect potentiellement génératif. | À VÉRIFIER | `SOURCE À IDENTIFIER AVANT DÉPÔT`; déclarer l'IA si applicable. |
| Fig. 3.1 architecture Mermaid | `V1/V2/V3`, `\n` visibles, MQTT amalgamé à Redis. | REMPLACER | Architecture finale uniquement ; source auteur ; mécanismes et statuts distincts. |
| Fig. 3.2 flux TikZ | Plus précise et finale. | CONSERVER/AMÉLIORER | Ajouter source auteur et statuts implémenté/perspective. |
| Fig. 3.3 portefeuille | Volumes en log10 et familles peu comparables. | DÉPLACER EN ANNEXE | Expliquer unités, provenance et rôle scientifique. |
| Fig. 4.1 dashboard | Bonne preuve fonctionnelle, mais « SOC V2 », attaques déclarées et compte d'anomalies incohérent visuellement. | AMÉLIORER | Régénérer ; légende « capture du prototype » et scénario de démonstration. |
| Fig. 4.2 résultats | Montre validation/rejet/reclassement. | CONSERVER/AMÉLIORER | Préciser données simulées ou réelles. **INFORMATION À VÉRIFIER**. |
| Fig. 4.3 technique | « Services V2 », « IA », MQTT OK. | AMÉLIORER | Retirer versioning et termes promotionnels ; préciser snapshot. |
| Fig. 5.1 supervisés | « UNSW/CIC-DDoS », valeur arrondie à 1, protocoles exploratoires non signalés. | REMPLACER, P0 | Séparer datasets et protocoles ; ne pas fusionner UNSW/CIC-DDoS. |
| Fig. 5.2 détecteurs validation | Met en avant des résultats exploratoires/in-sample et Windows simulé. | REMPLACER ou ANNEXE | Montrer le contraste exploratoire/strict et la branche Drain3. |
| Fig. 5.3 Wazuh | Graphique utile, mais le titre « overlap » ne correspond pas clairement à un coefficient de recouvrement. | AMÉLIORER | Nommer les comptes exacts, définir le dénominateur. |
| Fig. 5.4 faux positifs | Compare des protocoles et datasets hétérogènes ; « UNSW/CIC-DDoS ». | REMPLACER | Facetter par expérience labellisée ; exclure les cas non comparables. |
| Fig. 5.5 latence | Titre interne « quasi temps réel » contredit le texte. | REMPLACER, P0 | Employer micro-lots ; indiquer charge et machine. |
| Fig. 5.6 CPU/RAM | La figure ne trace que le CPU alors que la légende annonce CPU et RAM. | REMPLACER, P0 | Ajouter RAM ou corriger le périmètre de la figure. |
| Fig. 5.7 parallèle | CPU lisible, mais style différent et pas de RAM. | AMÉLIORER | Harmoniser ; rappeler 3 workers, 500 événements, 5 cycles. |
| Fig. 5.8 robustesse | 1–2 lignes par format seulement. | REMPLACER/RENOMMER | « Smoke test multiformat » ; ajouter volumes et taux de conservation. |
| Fig. 8.1 boucle modèles | Schéma conceptuel cohérent. | CONSERVER/AMÉLIORER | Source auteur ; marquer les étapes non évaluées. |
| Fig. A.1 dashboard longue | Répète largement les captures du ch. 4 ; pas de label. | SUPPRIMER ou ANNEXE | Garder seulement si elle ajoute un détail, ajouter source et label. |

Toutes les figures générées par script doivent porter « Source : auteur, à partir des résultats de l'expérience … ». Les captures doivent porter « Source : capture du prototype Ariel Logminer réalisé dans ce travail ». Pour toute image IA : déclaration explicite. Si l'origine ne peut être établie : `SOURCE À IDENTIFIER AVANT DÉPÔT`.

## 14. Audit des tableaux

- Tableau 3.3 : remplacer par les composants de l'architecture finale et leurs preuves.
- Tableau 3.4 : conserver, mais citer des sources pour les caractéristiques des outils tiers et éviter une comparaison trop générale.
- Tableau 4.1 : conserver ; ajouter les limites et la taille du test par format.
- Tableau 4.2 : conserver comme preuve d'implémentation, mais ne pas confondre artefact et validation expérimentale.
- Tableau 5.1 : conserver ; ajouter provenance/version, unité d'observation, taille et type de split.
- Tableau 5.2 : conserver ; compléter seuils, prétraitements, tailles, logique de sélection et jeu de validation.
- Tableau 5.3 : améliorer ; il mélange résultats quantitatifs et constats fonctionnels. Ajouter protocole, preuve et statut.
- Tableaux 5.4–5.6 : conserver ; ce sont les tableaux centraux de généralisation. Remplacer « graines » par identifiants de configurations/holdouts lorsque le scénario change.
- Tableau 5.7 : conserver ; ajouter dispersion et environnement.
- Tableaux 5.8–5.9 : conserver ; ajouter matériel et clarifier les unités CPU.
- Tableaux 5.10–5.11 : conserver ensemble, en distinguant explicitement exploratoire et test indépendant.
- Tableau 5.12 : conserver ; préciser l'hôte, Redis, workers, définition de perte et méthode de calcul des latences.
- Tableau 5.13 : conserver comme résultat négatif majeur ; clarifier l'unité CPU `121,339`/`165,746` et sa normalisation. **INFORMATION À VÉRIFIER**.
- Tableau 5.14 : déplacer en annexe ou supprimer ; il raconte une progression non comparable.
- Tableau 6.1 : conserver mais raccourcir ; il doit synthétiser les menaces de validité, sans répéter tous les résultats.
- Tableau 7.1 : conserver ; éviter d'y remettre les mêmes explications qu'aux chapitres 5 et 6.
- Tableau 8.1 : transformer d'une liste de choses « à figer » en fiche réellement remplie.
- Tableau 8.2 : conserver comme protocole, statut `NON ÉVALUÉ` si aucune campagne de mise à jour n'est présentée.
- Tableaux A.1–A.2 : conserver en annexe, mais compléter A.2 avec Redis, multi-VM, monolithique/agents, MQTT, mémoire et mise à jour contrôlée.
- Tous les tableaux : ajouter une attribution. Pour un tableau original : « Source : auteur… ». Pour une synthèse de littérature : « Synthèse de l'auteur à partir de [références] ».

## 15. Audit de la déclaration d'usage de l'IA

Aucune déclaration d'assistance par IA générative n'a été trouvée dans le manuscrit. Risque : élevé, surtout si du texte, du code, le logo ou certaines illustrations ont été générés ou fortement modifiés par IA.

Emplacement recommandé : déclaration dédiée dans les pages liminaires, après les remerciements et avant les résumés, ou selon le règlement de l'établissement.

Formulation courte à faire valider par l'établissement :

> Ce mémoire a bénéficié d'une assistance par intelligence artificielle générative pour la reformulation, l'amélioration linguistique et la structuration de certains passages. OUTIL(S) D'IA À RENSEIGNER PAR L'AUTEUR. Si cela est exact, l'assistance au code et/ou à certaines illustrations doit être déclarée séparément. Les choix scientifiques, l'exécution et la vérification des expériences, le contrôle des sources, l'interprétation des résultats et la responsabilité finale du contenu appartiennent à l'auteur.

Points à renseigner sans invention : outils, dates/périodes, usages rédactionnels, code, revue, débogage, documentation, illustrations. Le logo et la figure d'architecture doivent faire l'objet d'une vérification spécifique de provenance.

## 16. Audit de la terminologie

| Terme | Usage défendable | Incohérence/action |
|---|---|---|
| Ariel Logminer / Logminer | Nom du prototype | Choisir une forme officielle ; garder `Logminer` via macro dans le texte. |
| Journal / log | Trace système/applicative | Employer « journal » dans le texte français ; réserver `log` au code ou aux formats. |
| Flux réseau | Enregistrement tabulaire de flux | Ne pas le présenter comme journal textuel ; préciser le changement d'unité d'observation. |
| Événement brut/parsée/normalisé | Étapes de représentation | Conserver et définir une fois. |
| Anomalie candidate | Sortie nécessitant validation | Terme central correct. |
| Alerte | Signal d'un outil/règle | Ne pas l'assimiler à une anomalie ni à une attaque. |
| Incident | Regroupement de candidats | Employer « incident potentiel/corrélé » tant qu'il n'est pas confirmé. |
| Attaque/intrusion | Label de dataset ou verdict confirmé | Dans les captures, préciser qu'il s'agit de libellés de scénario/règles. |
| Agent fonctionnel | Composant spécialisé | Préférable pour le modèle logique. |
| Agent intelligent multitâche | Runtime avec capacités, mémoire, politique, heartbeat | Définir sans connotation cognitive/LLM. |
| Autonomie | Sélection/routage/exécution sous politiques | Toujours qualifier d'opérationnelle et encadrée. |
| Distribution | Multiprocessus local ou multi-VM de laboratoire | Nommer le niveau exact à chaque occurrence. |
| Mémoire persistante | Historique JSON/JSONL | Ne pas confondre avec apprentissage. |
| Mémoire adaptative | Historique effectivement consulté par une politique | Employer seulement là où l'effet est implémenté et prouvé. |
| Apprentissage continu | Mise à jour en ligne automatique | Ne pas revendiquer ; le système décrit une mise à jour hors ligne contrôlée. |
| Temps réel | Garantie de latence continue | Non démontré ; remplacer toute occurrence graphique par « micro-lots ». |
| Robustesse | Résistance sous variations définies | Réserver aux protocoles avec couverture suffisante ; le test multiformat actuel est un smoke test. |

## 17. Audit du titre

| Élément du titre | Sens dans le mémoire | Implémentation | Évaluation | Limite | Défendabilité |
|---|---|---|---|---|---|
| Détection autonome | Routage et exécution sous politiques | routeur, superviseur, runtime | fonctionnelle, non globale | pas de décision cyber générale | Défendable seulement avec définition opérationnelle proche du titre. |
| Distribuée | Décomposition + Redis | processus/Redis ; multi-VM à vérifier | 6 h locale ; 1 h multi-VM annoncée | pas multi-site/HA/sécurité | Élément le plus risqué. Documenter multi-VM ou atténuer le titre. |
| Anomalies | Candidats algorithmiques | détecteurs supervisés/non supervisés | plusieurs datasets | vérité terrain absente pour Wazuh/Windows | Défendable si « candidates » est rappelé tôt. |
| Journaux système et réseau | Logs Windows/Linux/Wazuh/HDFS/BGL + flux tabulaires | parseurs et pipelines | hétérogène | flux réseau ≠ logs textuels | Défendable avec typologie explicite. |
| Agents intelligents | composants à politique/mémoire/heartbeat | runtime agents | campagne Redis | intelligence limitée à l'orchestration | Défendable mais exposé à la critique terminologique. |
| Multitâches | plusieurs handlers/tâches par agent | discover/parse/route, autres handlers | campagne centrée sur trois tâches | couverture complète à vérifier | Partiellement défendable. |

Le sous-titre « Conception et évaluation locale » protège utilement contre une lecture industrielle, mais ne corrige pas à lui seul l'ambiguïté de « distribuée ».

## 18. Audit questions–hypothèses–objectifs–résultats

### Questions de recherche

| QR | Réponse/preuve | Chapitre | Statut |
|---|---|---|---|
| Q1 normalisation hétérogène | schéma + tests multiformats | 3, 4, 5.15 | PARTIELLE : fonctionnalité montrée, conservation non quantifiée. |
| Q2 agents modulaires/auditables | code, audit, Redis, reprise | 3–5 | PARTIELLE : reprise mesurée, modularité non mesurée. |
| Q3 sélection automatique du modèle | routeur + ablation externe au corps | 3–4, discussion | PARTIELLE : mécanisme prouvé, bénéfice prédictif non soutenu. |
| Q4 tableau de bord analyste | captures + endpoints | 4, 7 | PARTIELLE : fonctions présentes, utilisabilité non évaluée. |
| Q5 mémoire et mise à jour | mémoire + scripts mensuels | 3–4, 8 | PARTIELLE : persistance implémentée, effet réel non évalué. |
| Q6 protocole quantitatif/ressources | modèles, latence, CPU/RAM | 5 | PARTIELLE : nombreuses mesures, environnement incomplet. |

### Hypothèses

| Hypothèse | Expérience | Résultat | Statut recommandé |
|---|---|---|---|
| H1 noyau commun sans perte utile | test multiformat/fallback | plusieurs cas passent, original conservé | PARTIELLEMENT SOUTENUE ; absence de perte non mesurée. |
| H2 agents améliorent modularité, traçabilité, robustesse | mono/agents + reprise Redis | overhead ; reprise réussie | PARTIELLEMENT SOUTENUE ; résilience locale oui, gains architecturaux non quantifiés. |
| H3 routage limite incompatibilités et spécialisation aide | ablation espace commun | résultats proches | PARTIELLEMENT SOUTENUE ; cohérence architecturale oui, supériorité prédictive non. |
| H4 modèles légers utiles localement | évaluations datasets + coûts | résultats contrastés | VALIDÉE DANS LE CADRE ÉVALUÉ, avec généralisation limitée. |
| H5 mémoire soutient adaptation et mise à jour | persistance, feedback simulé, scripts | mécanismes présents | PARTIELLEMENT SOUTENUE ; effet opérationnel réel non testé. |

### Objectifs

- O1 catégoriser/structurer : atteint au niveau du prototype, preuve de couverture limitée.
- O2 étudier les techniques : atteint, mais état de l'art comparatif à densifier.
- O3 architecture multiagent/Redis : atteint localement ; statut multi-VM à harmoniser.
- O4 supervisé/non supervisé/mémoire : modèles évalués ; mémoire seulement partiellement évaluée.
- O5 tableau de bord : implémenté ; pas d'étude utilisateur.
- O6 tester sur données simulées/réelles/publiques : atteint, mais provenance et nature « réelle » à documenter.
- O7 métriques : atteint ; reproductibilité matérielle et incertitudes incomplètes.

## 19. Analyse du chapitre 5

| Expérience | Question | Protocole/métrique | Observation | Interprétation autorisée | Interprétation interdite | Rôle | Importance |
|---|---|---|---|---|---|---|---|
| Supervisé exploratoire | Séparabilité interne ? | split stratifié, F1 | scores élevés | utile comme exploration | généralisation | détection | secondaire |
| CICIDS contrôlé | Le split change-t-il la conclusion ? | aléatoire vs holdout apparié, F1/MCC | forte chute | dépendance aux scénarios | « le modèle ne marche jamais » | méthodologie | majeur |
| Holdouts CICIDS par scénario | Quels scénarios généralisent ? | cinq scénarios | DDoS partiel, autres faibles/nuls | hétérogénéité du défi | effet du seul hasard | méthodologie | majeur |
| Candidats modèles | Un autre modèle léger corrige-t-il la fragilité ? | cinq candidats | meilleur F1 0,233670 | amélioration limitée | problème résolu | méthodologie | majeur, actuellement absent |
| Wazuh | Quels signaux atypiques sont produits ? | Isolation Forest, comptes | 3 676/122 563 | sélectivité et groupes concernés | attaques/faux positifs confirmés | opérationnel | secondaire |
| Faux positifs | Quel bruit sur données labellisées ? | FP/1 000 | très variable | comparaison interne à chaque protocole | classement global des datasets | opérationnel | contrôle/annexe |
| Micro-lots | Quel temps par lot ? | 10 cycles, 8 537 lignes | moyenne/étendue | ordre de grandeur local | temps réel garanti | coût | secondaire |
| CPU/RAM | Quel coût local ? | 30 cycles | moyennes | profil de la machine testée | coût universel | coût | secondaire |
| Parallèle | Le mode s'exécute-t-il avec 3 workers ? | 5 cycles, 500 événements | succès, ressources | faisabilité locale | accélération vs campagne différente | architecture | contrôle |
| HDFS/BGL exploratoire | Le pipeline accepte-t-il ces logs ? | ligne par ligne/in-sample | séparabilité contrastée | intégration | généralisation | ingestion | annexe |
| HDFS/BGL Drain3 | Une représentation structurée aide-t-elle ? | train–test, fenêtres, F1 | HDFS modéré, BGL parfait local | observation sur partition | performance universelle | séquentiel | majeur/secondaire |
| Redis 6 h | Les tâches sont-elles réparties/reprises ? | 3 workers + recovery | toutes terminées | résilience locale | distribution industrielle | architecture | majeur |
| Mono vs agents | Les agents accélèrent-ils ? | 60 tâches appariées | débit inférieur | overhead + reprise | gain automatique | architecture | majeur |
| Multi-VM 1 h | Le bus relie-t-il Debian/Ubuntu ? | artefacts externes au chapitre | 525 lues, 0 lag/pending | laboratoire multi-VM si vérifié | SOC distribué | architecture | majeur, actuellement absent |
| Multiformat | Les formats échouent-ils silencieusement ? | cas unitaires | lignes conservées | smoke test | robustesse générale | ingestion | contrôle |

Organisation recommandée, meilleure que l'actuelle :

1. capacité d'ingestion, normalisation et routage ;
2. performances prédictives et généralisation ;
3. analyse séquentielle HDFS/BGL ;
4. anomalies candidates, Wazuh et bruit ;
5. architecture d'exécution, coût, reprise et multi-VM ;
6. restitution analyste et validation fonctionnelle.

Cette organisation en six axes est plus compacte que les dix axes proposés et évite de séparer artificiellement des expériences dépendantes.

## 20. Analyse du chapitre 6

Le chapitre 6 doit devenir le chapitre de validité et de sensibilité des protocoles. Sa fonction est pertinente, mais il répète trop le chapitre 5.

À conserver : analyse du biais de split, fuite d'information HDFS/BGL, portée des termes du titre, tableau des menaces à la validité.

À raccourcir : toutes les répétitions détaillées des valeurs déjà établies au chapitre 5.

À corriger : la dernière phrase qui transforme la mémoire en « apprentissage continu auditable » ; les développements prospectifs de réentraînement doivent aller au chapitre 7 ou 8.

Structure recommandée : validité interne ; validité de construit ; validité externe ; validité statistique ; sensibilité aux protocoles ; synthèse des affirmations autorisées.

## 21. Analyse du chapitre 7

Le chapitre 7 doit interpréter les apports, pas rejouer les résultats.

À conserver : apport architectural, valeur du résultat négatif mono/agents, rôle humain, limites, perspectives.

À réduire : troisième répétition complète de CICIDS2017, répétition de Redis 8 508/709, répétition de Wazuh 3 676/122 563.

À renforcer : nouveauté relative à l'état de l'art ; pourquoi l'intégration proposée est différente d'une simple juxtaposition de modules ; conséquences concrètes du routage non supérieur ; distinction bénéfices mesurés/bénéfices attendus.

À déplacer depuis le chapitre 6 : implications méthodologiques et priorités de recherche. À déplacer vers le chapitre 8 : protocole détaillé de mise à jour contrôlée.

## 22. Analyse du chapitre 8

Le chapitre mélange reproductibilité, guide d'installation, checklist éditoriale, exploitation, maintenance et perspectives.

À conserver dans le corps : commit/tag réel ; environnement exact ; données et empreintes ; commandes exactes ; mapping résultat–artefact ; conditions Redis et multi-VM ; limites de reproduction.

À déplacer en annexe technique : commandes longues, arborescence, installation, maintenance, détails de la tâche planifiée.

À supprimer du mémoire :

- §8.8 « Vérification des figures et captures » ;
- §8.9 « Contrôle des débordements visuels » ;
- phrases « vérifier après compilation sur Overleaf » ;
- §8.12 « Place des articles scientifiques » ;
- recommandations de tests qui appartiennent aux perspectives si elles ne sont pas réalisées.

Problème central : le tableau 8.1 énumère ce qu'il faudrait figer, mais le chapitre ne remplit pas cette fiche. Il faut remplacer le prescriptif par les valeurs réelles. **INFORMATION À VÉRIFIER** pour le matériel, Python, commit de référence, versions exactes et checksums.

## 23. Analyse des annexes

À conserver : commandes de reproduction ; définitions des métriques ; précautions d'interprétation ; matrice de traçabilité enrichie ; détails secondaires des campagnes.

À supprimer : §A.7 « Vérifications avant le dépôt » ; §A.10 « Exemple d'interprétation scientifique », redondant avec les chapitres 5–7 ; répétition du lien GitHub si déjà au chapitre 8.

À déplacer vers les annexes : tableau 5.14 de progression fonctionnelle, détails des prévalidations, tableaux exhaustifs de faux positifs, portefeuille des modèles.

À remonter dans le corps : tout résultat revendiqué dans le résumé/conclusion, notamment multi-VM, candidats CICIDS2017 et ablation de routage.

La phrase « les tableaux sont conservés au format Markdown » n'est pas suffisante pour un lecteur du PDF. Les tableaux indispensables doivent être insérés dans le PDF.

## 24. Redondances à supprimer

| Information | Conserver ici | Résumer/supprimer ailleurs |
|---|---|---|
| CICIDS aléatoire vs strict | Ch. 5 : protocole + valeurs | Ch. 6 : menace de validité ; ch. 7 : signification ; conclusion : une phrase. |
| Détail par scénarios CICIDS | Ch. 5 | Ch. 6/7 : renvoi interne seulement. |
| HDFS/BGL Drain3 | Ch. 5 | Ch. 6 : fuite/limites ; ch. 7 : implication. |
| Redis 8 508/709 | Ch. 5 | Ch. 6 : portée locale ; ch. 7 : apport ; conclusion : phrase courte. |
| Mono vs agents | Ch. 5 | Ch. 6 : validité ; ch. 7 : coût/bénéfice. |
| Wazuh 3 676/122 563 | Ch. 5 | Ch. 7 : conséquence analyste ; annexe : détail groupes. |
| Définition autonomie/intelligence/distribution | Ch. 1 | Ch. 3 : mise en œuvre ; ch. 6 : limites ; éviter répétition intégrale. |
| Mémoire/mise à jour | Ch. 3 concept, ch. 4 implémentation, ch. 8 reproduction | Ch. 6/7/9 : synthèse seulement. |
| Dashboard | Ch. 4 | Ch. 7 : absence étude utilisateur ; annexe : une capture complémentaire. |

## 25. Éléments à déplacer

- Ch. 5 §5.14 vers annexe technique.
- Ch. 3 figure 3.3 portefeuille vers annexe.
- Ch. 5 figure 5.4 faux positifs vers annexe après correction.
- Ch. 8 commandes longues vers annexe de reproductibilité.
- Ch. 8 maintenance et scénarios de déploiement vers discussion/perspectives ou guide technique.
- Ch. 6 détails prospectifs de réentraînement vers ch. 8.
- Annexes : remonter ablation de routage, candidats CICIDS2017 et multi-VM dans le ch. 5 si revendiqués.

## 26. Éléments à supprimer

- toute narration V1/V2/V3 et « version avancée » ;
- tableau 3.3 sous sa forme actuelle ;
- figure 3.1 actuelle ;
- prévalidation Redis de 150 tâches dans le corps ;
- §8.8 et §8.9 ;
- §8.12 sur les articles en préparation ;
- annexe §A.7 checklist de dépôt ;
- annexe §A.10 exemple pédagogique d'interprétation ;
- déclarations de robustesse non proportionnées au nombre de cas ;
- score historique 0,999965 si sa provenance officielle n'est pas établie ;
- répétitions chiffrées entre chapitres 5, 6, 7 et 9.

## 27. Éléments à renforcer

- comparaison de l'architecture avec les travaux proches ;
- protocole et résultats complets de l'ablation de routage ;
- comparaison des candidats CICIDS2017 ;
- campagne multi-VM, si validée ;
- mapping exact du contrat de message ;
- fiche réelle de reproductibilité ;
- provenance des datasets et des figures ;
- évaluation ou statut explicite de la mémoire, de la corrélation, de l'audit et du heartbeat ;
- définition des métriques de recouvrement Wazuh ;
- environnement et incertitudes des mesures de performance ;
- liens textuels vers chaque figure/tableau.

## 28. Nouvelle narration scientifique proposée

1. Problème : les sources hétérogènes imposent des représentations, modèles et mécanismes d'exploitation différents.
2. Lacune : les modèles isolés ne fournissent pas seuls une chaîne auditable, routée, résiliente et exploitable.
3. Contribution : architecture finale Logminer, contrat commun, agents spécialisés, bus persistant, mémoire contrôlée et interface analyste.
4. Méthode : questions et hypothèses reliées à des expériences explicites.
5. Résultats fonctionnels : ingestion, normalisation, routage, dashboard, audit.
6. Résultats prédictifs : protocoles exploratoires puis stricts, avec CICIDS2017 au centre.
7. Résultats architecturaux : overhead, endurance, reprise, multi-VM si vérifié.
8. Validité : fuite, dépendance aux scénarios, absence de vérité terrain, limites de l'interface.
9. Discussion : ce que l'intégration apporte réellement, ce qu'elle n'apporte pas.
10. Conclusion : faisabilité architecturale locale/laboratoire, généralisation prédictive encore limitée.

Messages centraux :

- Problème résolu : organiser une chaîne locale auditable pour transformer des sources hétérogènes en signaux structurés examinables.
- Système conçu : une architecture d'intégration multiagent combinant parsing, normalisation, routage, détection, corrélation, bus, mémoire et interface.
- Expériences : elles démontrent la faisabilité fonctionnelle, la reprise locale et des performances dépendantes des protocoles ; elles ne démontrent pas un détecteur universel.
- Résultat méthodologique principal : la chute CICIDS2017 montre qu'un split aléatoire peut produire une conclusion excessivement optimiste.
- Limite principale : généralisation et validation opérationnelle multi-environnement insuffisantes.
- Intérêt maintenu : l'architecture rend ces limites visibles, traçables et expérimentalement discutables.

## 29. Nouvelle hiérarchie des contributions

| Rang | Contribution | Nouveauté réelle | Preuve | Limite | Formulation recommandée |
|---:|---|---|---|---|---|
| 1 | Architecturale | intégration cohérente de briques hétérogènes | code, schémas, pipeline, API | nouveauté relative à mieux comparer | Architecture d'intégration conçue et implémentée. |
| 2 | Méthodologique | comparaison exploratoire/holdout révélant le biais de protocole | CICIDS tableaux 5.5–5.6 | un dataset/modèles légers | Résultat méthodologique majeur sur la sensibilité au split. |
| 3 | Logicielle | runtime agents, Redis, audit, dashboard | dépôt et campagnes | prototype de laboratoire | Prototype fonctionnel et auditable. |
| 4 | Expérimentale | évaluation multi-datasets et coûts | chapitre 5 | protocoles hétérogènes | Ensemble d'observations, non benchmark universel. |
| 5 | Opérationnelle | reprise des tâches et présentation analyste | Redis + captures | UX et sécurité non évaluées | Faisabilité locale de reprise et d'inspection. |

Ne pas revendiquer : nouvel algorithme ML ; supériorité générale du routage ; gain de débit multiagent ; détection d'attaques confirmées sur Wazuh ; robustesse universelle ; temps réel strict ; apprentissage continu autonome ; SOC industriel ; scalabilité multi-site.

## 30. Figures à conserver/modifier/remplacer

- Conserver après attribution : figure 3.2, figures dashboard utiles, figure 8.1.
- Modifier : portefeuille, Wazuh, parallèle, dashboard/captures.
- Remplacer prioritairement : figures 3.1, 5.1, 5.2, 5.4, 5.5, 5.6, 5.8.
- Déplacer en annexe : portefeuille, faux positifs détaillés, capture longue.
- Supprimer si non corrigée : figure 3.1 actuelle.

## 31. Tableau des risques devant le jury

| # | Critique probable | Risque | Passage | Correction |
|---:|---|---|---|---|
| 1 | Pourquoi « distribuée » si l'essentiel est local ? | Élevé | titre, ch. 1/5/8 | documenter multi-VM et niveaux de distribution. |
| 2 | Où est la nouveauté face à AAFID/SIEM modernes ? | Élevé | ch. 2–3 | comparaison directe et revendication limitée. |
| 3 | Pourquoi qualifier les agents d'intelligents ? | Élevé | titre, §1.3 | critères opérationnels + limites, sans cognition. |
| 4 | Quelles tâches sont réellement multitâches ? | Moyen | ch. 4–5 | matrice agent–handler–preuve. |
| 5 | Le contrat écrit correspond-il au code ? | Élevé | §3.14 | alignement exact. |
| 6 | Redis prouve-t-il un système distribué ? | Élevé | §5.13, ch. 8 | local vs multi-VM vs production. |
| 7 | MQTT est-il réellement utilisé ? | Moyen | §3.7, ch. 8 | statut smoke test optionnel. |
| 8 | Où sont les résultats multi-VM annoncés ? | Élevé | résumé | intégrer ou retirer. |
| 9 | Pourquoi LogisticRegression n'apparaît-il pas au ch. 5 ? | Élevé | résumé | intégrer l'expérience. |
| 10 | L'ablation de routage est-elle présentée ? | Élevé | intro/ch. 6–7 | ajouter au ch. 5. |
| 11 | Le 0,999965 vient-il de CIC-DDoS officiel ou d'UNSW ? | Élevé | ch. 5, fig. 5.1 | provenance exacte ou suppression. |
| 12 | Pourquoi le split aléatoire est-il si optimiste ? | Moyen | §5.4 | faire du contraste le résultat central. |
| 13 | Les graines sont-elles vraiment des répétitions ? | Élevé | tableaux 5.5–5.6 | nommer les scénarios/holdouts. |
| 14 | BGL à 1,000000 implique-t-il une fuite ? | Élevé | tableau 5.11 | validation distincte, seuil, répétitions. |
| 15 | Drain3 est-il appris uniquement sur train ? | Élevé | §5.11 | expliciter fit/transform et seuil. **INFORMATION À VÉRIFIER**. |
| 16 | Les 3 676 Wazuh sont-ils des attaques ? | Moyen | §5.6 | maintenir « candidats », définir recouvrement. |
| 17 | La mémoire réduit-elle réellement les faux positifs ? | Élevé | ch. 4/9 | classer non évalué avec données réelles. |
| 18 | L'interface est-elle utilisable ? | Moyen | ch. 4/7 | dire seulement fonctionnelle ; prévoir étude. |
| 19 | Peut-on reproduire sans votre machine ? | Élevé | ch. 8 | fiche exacte, commit, versions, matériel, données. |
| 20 | Où sont les sources et la déclaration IA ? | Élevé | toutes figures/frontmatter | attribution complète + déclaration institutionnelle. |

## 32. Corrections P0

1. Résoudre la contradiction multi-VM et intégrer/supprimer la revendication.
2. Présenter au chapitre 5 tout résultat du résumé : LogisticRegression, ablation routage, multi-VM.
3. Aligner le §3.14 sur `AgentMessage` et les enveloppes de transport.
4. Remplacer le §3.7 et le tableau V1/V2/V3 par l'architecture finale.
5. Remplacer la figure 3.1 et les figures scientifiquement ambiguës 5.1, 5.5, 5.6.
6. Éliminer la confusion UNSW/CIC-DDoS et documenter le score 0,999965 ou le retirer.
7. Corriger « apprentissage continu auditable » en statut conforme aux preuves.
8. Ajouter attribution à toutes les figures/images/tableaux.
9. Ajouter la déclaration d'usage de l'IA et vérifier le logo/illustrations.
10. Supprimer les dépendances au document directeur/cahier des charges.
11. Fournir la configuration expérimentale réellement utilisée.
12. Ajouter les sources primaires manquantes pour datasets et technologies.

## 33. Corrections P1

- Réorganiser le chapitre 5 autour des six questions expérimentales.
- Réduire les répétitions entre 5, 6, 7 et 9.
- Requalifier robustesse, temps réel, mémoire adaptative, corrélation et audit.
- Ajouter tous les renvois textuels aux figures/tableaux.
- Compléter la matrice preuve–résultat.
- Transformer le chapitre 8 en protocole factuel de reproductibilité.
- Supprimer/déplacer les checklists et notes de développement.
- Harmoniser terminologie française, titres et captures.
- Renforcer l'état de l'art comparatif et la nouveauté relative.

## 34. Corrections P2

- Uniformiser ponctuation, majuscules, « multiagent/multi-agents », « système/réseau ».
- Harmoniser palette, langue, police et arrondis des figures.
- Raccourcir les titres et phrases méta-rédactionnelles.
- Ajouter labels manquants et légendes autonomes.
- Nettoyer les noms internes de fichiers après stabilisation du PDF.
- Alléger le résumé en conservant problème, méthode, trois résultats majeurs, limites et contribution.

## 35. Plan détaillé de révision

### Phase 1 — Gel des faits

1. Désigner commit et artefacts de référence.
2. Vérifier les trois campagnes multi-VM et décider lesquelles entrent dans le mémoire.
3. Vérifier provenance du score 0,999965 et du jeu nommé « compatible CIC-DDoS2019 ».
4. Vérifier contrat `AgentMessage`, Drain3 train/test, unités CPU et statut de la mise à jour mensuelle.
5. Produire la matrice finale implémenté/évalué/décrit/perspective.

### Phase 2 — Corrections scientifiques

1. Ajouter les expériences manquantes au chapitre 5.
2. Reformuler les statuts des hypothèses et questions.
3. Recentrer les contributions.
4. Compléter protocoles, environnements et preuves.
5. Ajouter les sources primaires manquantes.

### Phase 3 — Architecture narrative

1. Réécrire conceptuellement §§3.7 et 3.14 sans chronologie.
2. Remplacer tableau 3.3.
3. Réorganiser chapitre 5 en six axes.
4. Transformer chapitre 6 en validité ; chapitre 7 en interprétation ; chapitre 8 en reproductibilité réelle.
5. Supprimer les notes de travail des annexes.

### Phase 4 — Visuels et attribution

1. Régénérer les figures obsolètes.
2. Retirer V1/V2/V3 des captures.
3. Ajouter source/protocole à chaque légende.
4. Vérifier confidentialité et statut simulé/réel des captures.
5. Déclarer toute illustration IA.

### Phase 5 — Contrôle final

1. Audit numérique sans changer les valeurs.
2. Vérification croisée résumé–chapitre 5–conclusion.
3. Vérification citations/BibTeX.
4. Compilation et contrôle des renvois.
5. Lecture par un tiers n'ayant accès qu'au PDF.

## 36. Instructions finales à transmettre au modèle de rédaction Luna

1. Ne modifier aucune valeur numérique et ne créer aucune expérience, source ou fonctionnalité.
2. Traiter ce diagnostic comme une liste d'actions, pas comme du texte à copier aveuglément.
3. Commencer par les P0 ; ne pas polir un passage scientifiquement instable.
4. Présenter l'architecture finale directement ; bannir V1/V2/V3, « version avancée », « progression » et l'historique du développement, sauf versionnement des modèles ML.
5. Réécrire le §3.7 selon composants, rôles, supports, preuves et limites.
6. Réécrire le §3.14 sur le schéma réel `run_id/source/target/message_type/payload/status/timestamp`; inscrire `INFORMATION À VÉRIFIER` si l'identifiant événement ou les métadonnées ne sont pas établis.
7. Organiser le chapitre 5 autour de questions scientifiques et faire de CICIDS2017 le résultat méthodologique central.
8. Ne présenter l'ablation de routage, LogisticRegression et le multi-VM qu'avec leur protocole et leurs preuves dans le corps.
9. Séparer systématiquement `DÉMONTRÉ`, `OBSERVÉ`, `SUGGÉRÉ`, `NON ÉVALUÉ`, `PERSPECTIVE`.
10. Ne jamais transformer anomalie candidate, alerte de règle ou libellé de dataset en attaque/incursion confirmée.
11. Employer « distribution locale multiprocessus » ou « multi-VM de laboratoire » selon le cas ; ne pas écrire « distribué » seul.
12. Définir l'autonomie comme exécution encadrée par politiques ; ne pas suggérer une autonomie cyber générale.
13. Définir l'intelligence comme sélection/orchestration/mémoire/heartbeat/handlers ; ne pas suggérer un LLM ou une cognition générale.
14. Distinguer mémoire persistante, priorisation, recalibrage, réentraînement hors ligne et promotion contrôlée.
15. Conserver tous les résultats négatifs et expliciter ce qu'ils invalident, nuancent et enseignent.
16. Réserver le chapitre 5 aux protocoles et observations, le chapitre 6 à la validité, le chapitre 7 à l'interprétation et le chapitre 8 à la reproduction factuelle.
17. Ajouter un renvoi interne avant ou après chaque figure/tableau.
18. Ajouter une source à chaque figure, capture, image et tableau ; écrire `SOURCE À IDENTIFIER AVANT DÉPÔT` si nécessaire.
19. Ajouter la déclaration IA avec `OUTIL(S) D'IA À RENSEIGNER PAR L'AUTEUR` tant que les outils ne sont pas fournis.
20. Supprimer toute checklist privée, TODO, consigne Overleaf et mention du document directeur/cahier des charges.
21. Ne pas prétendre que le dashboard est utilisable au sens UX ; dire seulement que ses fonctions ont été observées, sauf étude utilisateur.
22. Ne pas présenter le smoke test multiformat comme une preuve générale de robustesse.
23. Ne pas présenter MQTT comme preuve de distribution ; statut actuel : implémentation optionnelle et test fonctionnel court.
24. Maintenir une cohérence stricte entre résumé, corps, conclusion, figures et annexes.
25. Pour toute lacune factuelle, écrire exactement `INFORMATION À VÉRIFIER`.

# CHECKLIST DE VALIDATION

- [ ] ne contient plus de narration V1/V2/V3 inutile ;
- [ ] présente directement l'architecture finale ;
- [ ] ne dépend plus du document directeur ;
- [ ] ne dépend plus du cahier des charges ;
- [ ] est autonome pour un lecteur externe ;
- [ ] sépare clairement implémenté / évalué / perspective ;
- [ ] cite toutes les sources externes ;
- [ ] attribue toutes les figures ;
- [ ] attribue toutes les images ;
- [ ] identifie les illustrations IA si elles existent ;
- [ ] contient une déclaration transparente sur l'assistance par IA générative ;
- [ ] ne transforme jamais une anomalie en attaque confirmée sans preuve ;
- [ ] distingue split exploratoire et évaluation stricte ;
- [ ] ne masque pas les résultats négatifs ;
- [ ] ne revendique pas de gain multi-agent non démontré ;
- [ ] distingue multiprocessus, multi-VM et distribution industrielle ;
- [ ] définit clairement l'autonomie ;
- [ ] définit clairement l'intelligence des agents ;
- [ ] rend les contributions immédiatement identifiables ;
- [ ] répond à toutes les questions de recherche ;
- [ ] statue sur toutes les hypothèses ;
- [ ] relie chaque résultat majeur à une preuve ;
- [ ] supprime les TODO et checklists personnelles du corps scientifique ;
- [ ] élimine les répétitions entre chapitres 5, 6 et 7 ;
- [ ] maintient toutes les valeurs numériques inchangées ;
- [ ] ne crée aucune source ni expérience fictive ;
- [ ] est défendable devant un jury extérieur au projet.
