# DECISIONS SCIENTIFIQUES FIGÉES

## D001

Decision: Exclure le F1 = 0,999965 des résultats scientifiques et des nouvelles campagnes.

Evidence: Provenance dataset insuffisamment démontrée.

Reason: L'archive employée ne peut être réattribuée ni à UNSW-NB15 ni au CIC-DDoS2019 officiel.

Affected sections: Résumés, résultats supervisés, discussion et conclusion.

Do not reconsider unless: Une chaîne de provenance officielle, complète et vérifiable apparaît.

## D002

Decision: Qualifier la preuve multi-VM de preuve de laboratoire uniquement.

Evidence: Hôte Windows, VirtualBox, VM Debian, VM Ubuntu, Redis hôte, 525 entrées lues et acquittées, lag final 0 et pending final 0 ; campagne distincte de reprise après panne simulée.

Reason: Les artefacts ne démontrent pas 525 succès applicatifs individuellement traçables.

Affected sections: Architecture expérimentale, résultats multi-VM, annexes et conclusion.

Do not reconsider unless: Une nouvelle campagne traçant chaque tâche de bout en bout est produite.

## D003

Decision: Décrire `AgentMessage` avec sept champs métier seulement : `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`.

Evidence: Implémentation active dans `src/logminer/agents/bus.py`.

Reason: Aucun champ direct `event_id`, `message_id` ou `metadata`; les identifiants Redis relèvent du transport.

Affected sections: Contrat d'échange et figures d'architecture.

Do not reconsider unless: Le contrat actif est explicitement versionné et modifié.

## D004

Decision: Classer l'ancienne expérience Drain3 HDFS/BGL comme EXPLORATOIRE.

Evidence: Drain3 et certaines statistiques ont été construits séparément sur les partitions de test.

Reason: Le protocole ne constitue pas une validation train-vers-test indépendante.

Affected sections: Méthodologie, résultats HDFS/BGL, discussion et conclusion.

Do not reconsider unless: Un protocole strict avec état appris sur train, validation et test gelé est exécuté.

## D005

Decision: Conclure à l'absence de gain prédictif systématique du routage spécialisé.

Evidence: Deltas F1 : CICIDS2017 +0,000201 ; Linux/auth -0,003050 ; UNSW-NB15 -0,000264.

Reason: Deux familles sur trois régressent et l'expérience ne mesure pas le routeur réel.

Affected sections: Résultats d'ablation, discussion et contribution architecturale.

Do not reconsider unless: Une expérience différente, préenregistrée et correctement contrôlée apporte une nouvelle preuve.

## D006

Decision: Qualifier LogisticRegression de meilleur F1 moyen parmi cinq candidats dans l'ancien holdout CICIDS2017, sans généralisation au-delà.

Evidence: F1 moyen 0,233670, très variable selon le scénario et non dominant sur toutes les métriques.

Reason: Les cinq scénarios ne sont pas cinq répétitions identiques.

Affected sections: Protocole et résultats de comparaison des modèles.

Do not reconsider unless: La campagne multi-seeds produit une preuve plus robuste.

## D007

Decision: Classer la mise à jour contrôlée comme IMPLÉMENTÉE et vérifiée en DRY-RUN, mais NON ÉVALUÉE de bout en bout.

Evidence: Aucun candidat réel entraîné, aucune comparaison, promotion ou rejection réelle prouvée.

Reason: Une procédure présente dans le code n'est pas une performance démontrée.

Affected sections: Architecture, résultats, discussion et perspectives.

Do not reconsider unless: Des cas end-to-end avec scores, décisions, audits et hashes sont exécutés.

## D008

Decision: Conserver le benchmark monolithique-vers-agents comme preuve de surcoût à la charge testée.

Evidence: Monolithique 1,6357 tâche/s ; agents 1,5715 ; agents avec reprise 1,5267. CPU en pourcentage d'un cœur logique équivalent, RAM RSS en MiB.

Reason: Aucun gain de débit n'est démontré avec les agents à cette charge.

Affected sections: Méthode de mesure, tableau de performances et discussion.

Do not reconsider unless: Une nouvelle campagne comparable et correctement instrumentée est exécutée.

## D009

Decision: Utiliser les SHA-256 du manifeste pour identifier les copies locales, sans les présenter comme preuve de provenance officielle.

Evidence: Onze fichiers prioritaires ont été hashés et dimensionnés ; aucun fichier du dépôt ne fournit une chaîne de téléchargement officielle vérifiable pour ces copies.

Reason: L'identité binaire locale et la provenance officielle sont deux propriétés distinctes.

Affected sections: Reproductibilité, description des datasets et limites.

Do not reconsider unless: Des URL, versions, checksums éditeur et preuves de téléchargement concordantes sont retrouvés.

## D010

Decision: Considérer PortScan tenu hors entraînement comme une quasi-défaillance au seuil de décision fixe du RandomForest, tout en distinguant cette défaillance de la qualité de classement des scores.

Evidence: Sur cinq seeds, F1 moyen 0,009947, rappel 0,005000, 3 980 faux négatifs sur 4 000 attaques par run, tandis que la PR-AUC moyenne vaut 0,881982.

Reason: Le F1 et le rappel mesurent les décisions au seuil utilisé ; la PR-AUC indique qu'une information de classement subsiste. Aucun seuil ne doit être ajusté sur le test tenu à l'écart.

Affected sections: Résultats CICIDS holdout, discussion sur la généralisation et limites du seuil fixe.

Do not reconsider unless: Un seuil sélectionné uniquement sur validation, puis évalué une fois sur un test gelé, donne une preuve différente.

## D011

Decision: Classer le holdout Bot comme échec de généralisation du RandomForest strict dans ce protocole.

Evidence: Cinq seeds donnent F1=0, rappel=0 et aucun vrai positif sur 1 966 attaques Bot par run ; PR-AUC moyenne 0,322471 pour une prévalence positive de 0,329534.

Reason: Ni la décision au seuil courant ni le classement des scores ne fournissent ici une performance utile démontrée.

Affected sections: Résultats CICIDS holdout, limites et résultats négatifs.

Do not reconsider unless: Un protocole distinct avec validation indépendante et test gelé apporte une nouvelle preuve.

## D012

Decision: Rapporter le F1 nul d'Infiltration comme observation négative sur l'échantillon lu, sans conclure à une estimation robuste du scénario complet.

Evidence: Les cinq runs manquent les 32 attaques présentes dans les deux chunks autorisés ; F1=0, rappel=0, PR-AUC moyenne 0,015396, prévalence 0,007937.

Reason: Le plafond de deux chunks fournit trop peu de positifs pour une généralisation statistique forte au scénario Infiltration.

Affected sections: Résultats CICIDS holdout, tableau des tailles de test et limites.

Do not reconsider unless: Une évaluation préspécifiée couvrant davantage d'attaques Infiltration est exécutée sur un test gelé.

## D013

Decision: Considérer WebAttacks comme une défaillance complète au seuil de décision fixe, sans nier l'information de classement observée.

Evidence: Sur cinq seeds, aucun vrai positif parmi 2 180 attaques par run, F1=0 et rappel=0 ; PR-AUC moyenne 0,654341 pour une prévalence 0,352751.

Reason: Le seuil courant ne produit aucune détection utile, mais la PR-AUC interdit de conclure que les scores sont entièrement aléatoires. Aucun seuil n'a été ajusté sur le test.

Affected sections: Résultats CICIDS holdout, discussion des seuils et résultats négatifs.

Do not reconsider unless: Un seuil sélectionné sur validation indépendante est évalué une seule fois sur un test WebAttacks gelé.

## D014

Decision: Retenir que la chute CICIDS en holdout persiste sur cinq seeds par scénario et que la variabilité est principalement inter-scénarios.

Evidence: F1 random moyen 0,995142 contre F1 holdout macro 0,157744 ; écart-type des moyennes de scénarios 0,347193 contre écart-type intra-scénario combiné 0,000600 ; 30/30 runs terminés.

Reason: Les résultats changent massivement selon le scénario tenu hors entraînement, tandis que les répétitions de seed restent presque identiques au sein d'un même scénario.

Affected sections: Protocole CICIDS, résultats, discussion de la généralisation, limites et conclusion.

Do not reconsider unless: Un protocole plus complet, préspécifié et strictement comparable fournit une preuve contradictoire.

## D015

Decision: Conclure qu'aucun des cinq modèles comparés ne généralise utilement à PortScan au seuil courant dans ce protocole.

Evidence: F1 moyens : RandomForest 0,009947 ; ExtraTrees 0,008955 ; LogisticRegression 0,000497 ; HistGradientBoosting 0 ; SGDLogistic 0. Chaque modèle est évalué sur cinq seeds et 4 000 attaques par run.

Reason: Même le meilleur F1 correspond à un rappel de seulement 0,005. Les PR-AUC parfois élevées doivent être rapportées séparément comme information de classement, sans ajuster de seuil sur le test.

Affected sections: Comparaison des modèles CICIDS, résultats négatifs et discussion des seuils.

Do not reconsider unless: Une procédure avec validation indépendante sélectionne le seuil avant une évaluation unique sur un test PortScan gelé.

## D016

Decision: Conclure qu'aucun des cinq modèles comparés ne détecte Bot au seuil courant dans ce protocole.

Evidence: RandomForest, ExtraTrees, HistGradientBoosting, LogisticRegression et SGDLogistic ont tous F1=0, rappel=0 et zéro vrai positif sur 1 966 attaques par run, chacun sur cinq seeds.

Reason: Les différences de PR-AUC et de faux positifs ne produisent aucune détection correcte au seuil utilisé.

Affected sections: Comparaison des modèles CICIDS et résultats négatifs.

Do not reconsider unless: Une procédure avec validation indépendante ou une représentation nouvelle est évaluée sur un test Bot gelé.

## D017

Decision: Rapporter la meilleure performance Infiltration de LogisticRegression comme un résultat local fragile, sans généralisation au scénario complet.

Evidence: LogisticRegression obtient F1 0,372881, rappel 0,343750, PR-AUC 0,356763 et MCC 0,369642 sur les cinq seeds ; le test plafonné ne contient que 32 attaques. SGDLogistic varie fortement (F1 moyen 0,111097 ± 0,181391) et les trois modèles d'arbres ont F1 nul.

Reason: La répétition des métriques de LogisticRegression ne compense pas la très petite taille de l'échantillon positif ni le plafonnement à deux chunks.

Affected sections: Comparaison des modèles CICIDS, tailles d'échantillon, résultats négatifs et limites.

Do not reconsider unless: Une évaluation préspecifiée couvrant davantage de positifs Infiltration est effectuée sur un test gelé.

## D018

Decision: Retenir LogisticRegression comme meilleur candidat uniquement selon le F1 macro du protocole phase 2, sans lui attribuer une domination globale.

Evidence: Sur 25 résultats par candidat, F1 macro LogisticRegression 0,233670, SGDLogistic 0,165406, RandomForest 0,157744, ExtraTrees 0,143191 et HistGradientBoosting 0,003362. HistGradientBoosting a la meilleure PR-AUC macro (0,567697), ExtraTrees le plus faible FPR macro (0,000100) et SGDLogistic le fit moyen le plus court (0,149185 s).

Reason: Les métriques, coûts et scénarios désignent des gagnants différents ; le F1 macro est une agrégation descriptive à poids égal des scénarios.

Affected sections: Chapitre 5, comparaison des candidats, discussion, limites et conclusion.

Do not reconsider unless: Un critère de sélection préspecifié différent ou une nouvelle évaluation comparable apporte une preuve contradictoire.

## D019

Decision: Figer la phase 3 sur des fenêtres sources contiguës, disjointes et choisies sans labels, avec Drain3 et toutes les statistiques appris sur train, seuil choisi sur validation et test gelé.

Evidence: `configs/strict_sequence_protocol.json` a été écrit avec le statut `FROZEN_BEFORE_LABEL_DISTRIBUTION_INSPECTION` avant l'extraction des nouvelles fenêtres ; le dry-run annonce 36 résultats.

Reason: Ce protocole ferme les fuites identifiées dans l'ancien pipeline tout en gardant un volume calculable et une chronologie explicite.

Affected sections: Protocole et résultats HDFS/BGL, limites, annexes expérimentales.

Do not reconsider unless: Une impossibilité technique empêche l'extraction ; toute adaptation devra être enregistrée avant d'examiner les résultats du test.

## D020

Decision: Retenir Histogram comme meilleur résultat HDFS strict par F1 dans ce test gelé, sans revendiquer une performance générale ni comparer les durées par méthode.

Evidence: Histogram F1 0,269307, IQR 0,268775, ensemble 0,242946 ± 0,010487 ; test de 20 000 événements dont 118 anomalies. La construction du bundle de scores est mutualisée par seed, donc les durées internes ne sont pas attribuables individuellement.

Reason: Le résultat est reproductible et sans fuite test identifiée, mais il dépend d'une fenêtre locale à faible prévalence et d'un seuil supervisé sur validation.

Affected sections: Résultats HDFS/BGL, discussion, limites et annexe de protocole.

Do not reconsider unless: Une nouvelle fenêtre ou une mesure de temps isolée par méthode est exécutée selon un protocole préspecifié.

## D021

Decision: Retenir Histogram comme meilleur résultat BGL strict dans la fenêtre test gelée, et classer les autres méthodes comme défaillantes au seuil sélectionné.

Evidence: Histogram F1 0,913698, précision 0,841108, rappel 1, MCC 0,902319 et FPR 0,032016. Les cinq méthodes restantes ont F1 entre 0,253473 et 0,278511 et FPR entre 0,877859 et 0,998285. Le test comporte 19 908 événements, dont 2 885 anomalies, et 89,808 % de templates inconnus par rapport au train.

Reason: Histogram conserve une séparation utile malgré le déplacement temporel ; les autres seuils sélectionnés sur une validation à prévalence différente généralisent mal au test.

Affected sections: Résultats BGL, comparaison des méthodes, discussion des dérives et limites.

Do not reconsider unless: Une nouvelle fenêtre temporelle indépendante ou un protocole de calibration préspecifié apporte une preuve différente.

## D022

Decision: Utiliser les anciens résultats HDFS/BGL uniquement comme comparatif exploratoire et les nouveaux résultats stricts comme preuve principale locale.

Evidence: L'ancien pipeline réajuste Drain3 et certaines statistiques sur chaque partition et calibre les décisions via le classement du test. Le nouveau pipeline a 36 artefacts valides, un état Drain3 train-only inchangé et un seuil choisi uniquement sur validation.

Reason: La séparation des données et du réglage de seuil est nécessaire pour une évaluation indépendante du test.

Affected sections: Résumé, chapitre 5, discussion, conclusion et annexes HDFS/BGL.

Do not reconsider unless: L'ancien pipeline est reproduit sans ces fuites, ce qui en ferait une nouvelle expérience distincte.

## D023

Decision: Tester la procédure de mise à jour sur trois copies de modèles isolées et un holdout DDoS déjà évalué, exclusivement comme validation fonctionnelle des branches de décision.

Evidence: Le plan figé compare ExtraTrees à RandomForest pour la promotion, RandomForest à SGDLogistic pour le rejet et ExtraTrees à LogisticRegression avec `min_delta=0,02` pour le gain positif insuffisant. Ces relations proviennent des résultats phase 2, sans sélection de seed autre que 42.

Reason: L'objectif phase 4 est de prouver entraînement, comparaison, décision, backup, promotion/rejet et audit réels, pas d'apporter une nouvelle estimation indépendante de généralisation.

Affected sections: Mise à jour des modèles, statut logiciel, limites et annexes de preuve.

Do not reconsider unless: Les deltas réels ne déclenchent pas les trois branches prévues ; le résultat doit alors être conservé tel quel sans modifier les scores.

## D024

Decision: Classer la procédure contrôlée de mise à jour comme `IMPLÉMENTÉE` et `TESTÉE FONCTIONNELLEMENT DE BOUT EN BOUT`, mais non évaluée comme mécanisme prédictif indépendant ou système de production ; l'apprentissage continu autonome reste une perspective.

Evidence: Trois candidats ont été réellement entraînés puis comparés sur le même holdout gelé. Une promotion avec backup est observée pour un delta F1 `+0,067845`; un candidat inférieur est rejeté à `-0,063163`; un gain positif est rejeté à `+0,009016` car inférieur au seuil `0,02`. Les hashes montrent que le backup égale le courant avant promotion, que le courant après promotion égale le candidat, et que les deux courants rejetés restent inchangés.

Reason: Les branches essentielles du mécanisme sont désormais exécutées réellement, mais les cas utilisent des relations déjà connues en phase 2 et des copies isolées. Cela prouve le fonctionnement logiciel contrôlé, pas une généralisation nouvelle, un fonctionnement périodique en service ou une autonomie d'apprentissage.

Affected sections: Mise à jour des modèles, statut de la contribution logicielle, chapitre 5, limites et annexes de preuve.

Do not reconsider unless: Une évaluation indépendante, une exécution périodique réelle ou une preuve de production correctement instrumentée apporte un niveau de preuve supérieur.

## D025

Decision: Classer la phase 5 comme validation fonctionnelle multiformat partielle, et interdire les affirmations de robustesse universelle ou de conservation générale du message brut.

Evidence: Sur 7 001 unités, 5 001 sont normalisées et 2 000 perdues. Windows, Linux/auth, Wazuh, syslog et flux réseau produisent 1 000/1 000 sorties ; Apache produit 1/1 sur fixture synthétique ; HDFS et BGL produisent 0/1 000 chacun malgré une détection de type correcte. La ligne complète n'est conservée à l'identique ni pour Windows ni pour syslog. La complétude temporelle Wazuh est nulle dans le préfixe testé.

Reason: La campagne mesure plusieurs voies réelles avec comptabilité événementielle et conserve les échecs, mais un seul préfixe par format, l'hétérogénéité des adaptateurs et le très faible N Apache empêchent toute conclusion universelle.

Affected sections: Validation multiformat, architecture de parsing, conservation du brut, limites, résultats négatifs et annexes.

Do not reconsider unless: Les parseurs HDFS/BGL du pipeline sont réellement réparés puis réévalués, plusieurs fichiers indépendants par format sont testés, ou un champ brut explicite est ajouté et vérifié.

## D026

Decision: Considérer le routeur réel comme fonctionnellement évalué sur un corpus local dérivé, avec 80/81 décisions correctes, tout en maintenant qu'aucun gain prédictif systématique du routage n'est démontré.

Evidence: `route_model` route correctement 80 fichiers sur 81, exactitude 0,987654, F1 macro 0,883598 en incluant la classe fallback prédite sans support vrai. La seule erreur est Apache normalisé, vraie famille network mais prédiction fallback. Aucun fichier ne provoque d'erreur et tous les modèles choisis existent.

Reason: L'expérience mesure directement l'attribution de famille/modèle par l'implémentation réelle, contrairement à D005. Toutefois, les chunks partagent leur source et contiennent souvent des métadonnées familiales ; elle ne prouve ni généralisation universelle ni amélioration des prédictions d'anomalie.

Affected sections: Architecture du routeur, protocole et résultats du chapitre 5, limites, contribution logicielle et annexes.

Do not reconsider unless: Un corpus multi-source indépendant ou une évaluation end-to-end routeur→prédiction avec vérité terrain apporte une preuve plus forte.

## D027

Decision: Classer la phase 7 optionnelle `SKIPPED` et conserver uniquement la preuve existante de reprise multi-VM de laboratoire après sortie contrôlée avant traitement et ACK.

Evidence: La campagne `redis-vbox-recovery-20260722150924` contient 3 tâches enfilées, 3 événements de fin portant 3 identifiants uniques, 0 échec, 1 tâche lue par le worker Debian avant sa sortie, 1 tâche reprise par le worker Ubuntu et 0 pending final. Le code de la panne s'arrête immédiatement après `fetch`, sans exécuter la tâche. Le runtime normal publie le résultat avant l'appel d'ACK, mais aucune injection ni mesure ne couvre cette seconde fenêtre. Docker/Redis étaient indisponibles pendant l'audit.

Reason: Rejouer le scénario existant n'ajouterait aucune preuve. Le scénario scientifiquement nouveau après traitement mais avant ACK exigerait une instrumentation nouvelle et une infrastructure Redis active; il ne doit pas être improvisé pour une phase optionnelle.

Affected sections: Résilience, multi-VM, limites, résultats négatifs et annexes de preuve.

Do not reconsider unless: Une campagne pré-spécifiée injecte une panne entre effet applicatif et ACK et mesure explicitement tâches terminées, récupérées, dupliquées, perdues, temps de reprise, pending et lag.

## D028

Decision: Classer la phase 8 `VALIDATION SUR SCÉNARIOS SYNTHÉTIQUES CONTRÔLÉS`, et non validation SOC réelle.

Evidence: Sur 16 anomalies appartenant à 6 incidents vrais, le corrélateur produit 6 incidents, avec précision pairwise `0,764706`, rappel `0,866667` et F1 `0,812500` (TP=13, FP=4, FN=2, TN=101). Un incident franchissant une frontière de fenêtre de 15 minutes est fragmenté et deux incidents vrais partageant toutes les clés sont fusionnés. Les 3 bruits `is_anomaly=0` sont exclus.

Reason: La vérité terrain a été figée avant exécution et cachée à l'algorithme, ce qui soutient une validation fonctionnelle honnête. Le corpus est toutefois construit pour exercer les règles connues et ne représente ni la variété ni l'incertitude d'un SOC réel.

Affected sections: Corrélation d'incidents, protocole expérimental, résultats, limites, résultats négatifs et annexes.

Do not reconsider unless: Un corpus d'incidents réels annotés indépendamment ou plusieurs familles de scénarios externes apportent une preuve de généralisation.
