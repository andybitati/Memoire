# Evaluation Des Remarques Bastion Lab - Article 1

Date: 2026-06-04

Objet: evaluation des remarques attribuees a Bastion Lab par rapport a l'etat
actuel de l'article 1 et du prototype Logminer.

Remarque preliminaire: aucun fichier nomme explicitement `bastion_lab` n'a ete
trouve dans le depot. Cette evaluation s'appuie donc sur les deux documents de
critiques et reponses disponibles localement:

- `docs/memoire/reponse_critiques_article_1.md`;
- `docs/memoire/reponse_reviewers_article_1_round2.md`.

## Verdict Global

Les remarques principales sont maintenant largement couvertes. L'article 1 ne
se presente plus comme une victoire universelle du routage ni comme un systeme
multi-agent cognitif. Il est repositionne comme une contribution systeme:
routage familial auditable, specialisation controlee, fallback explicable,
ablation mesuree et limites clairement formulees.

Le point le plus fragile restant n'est plus l'honnetete scientifique, mais la
reproductibilite stricte: il manque encore une analyse multi-seeds, une
sensibilite des poids de routage et un package public fige avec versions des
modeles.

## Matrice D'evaluation

| Remarque Bastion Lab / reviewers | Etat actuel | Preuve dans le travail actuel | Reste a faire |
| --- | --- | --- | --- |
| Ajouter une ablation du routage familial | Couvert | Article 1 contient une ablation commune et une ablation operationnelle; les resultats montrent que le routage seul ne gagne pas toujours | Ajouter plus tard une ablation factorielle stricte routage/features/modele |
| Eviter de pretendre que le routage ameliore toujours le F1 | Couvert | Le manuscrit dit explicitement que la strategie est une specialisation controlee, pas une garantie universelle | Aucun blocage majeur |
| Clarifier que l'innovation n'est pas un nouvel algorithme ML | Couvert | La section `Scientific Claim` presente la contribution comme une couche auditable de specialisation | Garder cette formulation dans toute version soumise |
| Clarifier le terme agent / multi-agent | Couvert | L'introduction et la section superviseur disent que les agents sont des modules logiciels, pas des agents cognitifs, FIPA, RL ou LLM | Eventuellement remplacer certains titres par `software-agent` si un reviewer reste strict |
| Repositionner le SupervisorAgent comme autonomie bornee | Couvert | Le superviseur est maintenant decrit comme couche de controle et d'audit, pas comme contribution adaptative principale | Article 2 peut approfondir stabilite, stress et degradation |
| Montrer que le routeur est auditable | Couvert | Formalisation avec score, confiance, raison de routage; table `Routing Audit Evidence`; fallback avec score 141 sur entree corrompue | Ajouter une vraie route accuracy si les labels famille sont disponibles |
| Expliquer les poids du routeur | Partiellement couvert | Table des constantes et texte expliquant que ce sont des preuves additives non calibrees | Sensibilite des poids encore absente |
| Traiter le fallback comme degradation controlee | Couvert | Section `Fallback Routing`; entree corrompue conservee, routee fallback, 0 candidat, 0 incident | Ajouter un tableau plus large fallback precision si possible |
| Reconnaitre la faiblesse HDFS | Couvert | Le manuscrit presente HDFS comme limite structurelle des features row-level et recommande Drain/temporal windows | Ne pas comparer favorablement HDFS a DeepLog/LogAnomaly |
| Ajouter la litterature Drain, DeepLog, LogAnomaly, LogRobust, LogBERT | Couvert | Related Work contient ces references et positionne Logminer par rapport aux logs sequentiels | Verifier le style bibliographique final |
| Repondre a la critique ELK/Wazuh/fail2ban | Couvert | Section comparative avec table qualitative: Logminer est complement analytique, pas remplacement SOC | Eventuellement ajouter Elastic/Kibana si demande par reviewer |
| Clarifier l'echelle et la complexite | Couvert pour article 1 | Cout du routeur donne en O(k x c x s); profil direct: routeur 0.9%; trace FastAPI: routage moyen 0.2466 s | Garder CPU/RAM et stress detaille pour article 2 |
| Eviter que l'article 1 empiete sur l'article 2 | Couvert apres recentrage | Article 1 reserve explicitement stress, ressources, scalabilite et stabilite superviseur a une etude operationnelle separee | Article 2 doit assumer ce terrain avec plus de profondeur |
| Ajouter des figures en anglais | Couvert selon les artefacts | Documents de reponse indiquent que les SVG et exports article ont ete convertis | Verifier visuellement les exports finaux avant soumission |
| Declarer les sorties non supervisees comme candidates | Couvert | Abstract, introduction, implementation et limites parlent d'anomaly candidates, pas d'intrusions confirmees | Aucun blocage majeur |
| Eviter l'impression de magouille sur les resultats eleves | Couvert partiellement | Menaces a la validite discutent class imbalance, duplicate flows, temporal split/leakage et versions scikit-learn | Idealement ajouter multi-seeds et splits temporels pour reseau |
| Reproductibilite stricte | Partiellement couvert | Artefacts locaux, CSV, tables et figures sont preserves; avertissements de version scikit-learn reconnus | Figer environnement, retrainer modeles, documenter seeds, publier un package |

## Evaluation Par Niveau De Risque

### Risque faible

- Positionnement prudent du routage.
- Distinction entre anomalie candidate et intrusion confirmee.
- Fallback explicable.
- HDFS reconnu comme limite.
- Comparaison honnete avec Wazuh, OSSEC, ELK et fail2ban.

### Risque moyen

- Les poids du routeur restent empiriques.
- L'ablation operationnelle combine routage, features et modeles.
- Les resultats reseau tres eleves peuvent etre attaques si le reviewer suspecte
  un biais de dataset ou une fuite train-test.
- Les modeles ont ete charges avec des versions scikit-learn differentes de
  celles d'entrainement.

### Risque a reporter vers l'article 2

- Scalabilite reelle.
- Stress longue duree.
- CPU/RAM par agent.
- Degradation sous source problematique.
- Back-pressure, files de messages, Kafka/MQTT/Redis Streams.
- Stabilite approfondie du SupervisorAgent.

## Conclusion

Par rapport aux remarques Bastion Lab / reviewers, l'article 1 est maintenant
defendable. Il ne donne plus l'impression de vendre un systeme magique ou une
amelioration universelle. Il assume son vrai apport: rendre le routage entre
familles de logs explicite, auditable et compatible avec des detecteurs
specialises.

La meilleure strategie de soumission est de garder l'article 1 court sur les
ressources et le stress, puis de consacrer l'article 2 a l'evaluation
operationnelle complete. Ainsi, les critiques sont traitees sans vider le
deuxieme article de son interet scientifique.

