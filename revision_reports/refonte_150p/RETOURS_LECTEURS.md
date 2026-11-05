# Rapports de lecture sur la version de 180 pages (fournis par l'auteur le 2026-11-05)

Texte recopié tel que fourni ; seuls les résidus de rendu d'un graphique (axes, légende) ont été omis. Les numéros de page et de section renvoient au PDF de 180 pages.

---

# Lecteur 1 — 12,50/20

Version examinée : 180 pages, année académique 2025–2026.

Méthode : évaluation du fond scientifique, des protocoles, des résultats, de l'argumentation, de la reproductibilité et de l'originalité, en reprenant la grille de la précédente évaluation.

## 1. Synthèse globale : verdict

Cette nouvelle version corrige plusieurs lacunes méthodologiques importantes de la précédente, notamment en introduisant des comparaisons avec des règles simples, un répartiteur au moindre chargé et des expériences préenregistrées. Le problème scientifique fondamental demeure cependant : aucune des cinq hypothèses n'est intégralement validée, et les expériences ne démontrent pas de supériorité propre de l'architecture multi-agents. Les résultats négatifs sont désormais mieux identifiés et documentés, mais leur analyse constitue davantage une étude critique des architectures et des protocoles d'évaluation qu'une démonstration de l'efficacité supérieure d'Ariel Logminer. Le mémoire devient plus rigoureux dans ses conclusions, sans pour autant résoudre toutes les faiblesses de sa problématique initiale.

NOTE ATTRIBUÉE À LA NOUVELLE VERSION : 12,50/20 — Réserves majeures. Ancienne version : 11,00/20 ; +1,50 point. Note indicative de lecture scientifique, non note officielle de soutenance.

Le relèvement de la note ne récompense pas le volume supplémentaire du document. Il résulte de comparateurs ajoutés, de critères expérimentaux explicites et d'une interprétation plus rigoureuse des résultats défavorables.

## 2. Comparaison avec la version précédente

| Dimension | Ancienne version | Nouvelle version |
|---|---|---|
| Comparaison aux règles simples | Incomplète | Étendue aux quatre datasets |
| Évaluation Contract Net | Principalement fonctionnelle | Comparaisons avec table statique et moindre chargé |
| Mémoire persistante | Gain non démontré | Gain conditionnel mesuré |
| Spécialisation | Gain incertain | Comparaison appariée et non-infériorité testée |
| Préenregistrement | Ambiguïtés | Périmètre mieux délimité |
| H3, H4 et H5 | Non tranchées | Toujours non tranchées |
| Originalité scientifique | Limitée | Toujours limitée |
| Reproductibilité | Traçabilité documentaire | Traçabilité renforcée, reproduction indépendante non certifiée |

La différence la plus importante se situe dans le chapitre 4, notamment les sections 4.8, 4.10 et 4.15. La nouvelle version teste plus sérieusement des explications alternatives aux résultats du prototype.

## 3. Critique détaillée par axe

### A. Problématisation et formulation des hypothèses (gravité élevée)

**A.1. Une problématique toujours trop dispersée.** Le mémoire cherche simultanément à traiter l'hétérogénéité des journaux, l'autonomie des agents, l'orchestration distribuée, la détection d'anomalies, le routage spécialisé, la persistance des états et l'assistance à l'analyste. Le chapitre introductif reconnaît maintenant que les hypothèses n'ont pas toutes la même nature. À la page 8, l'auteur précise que H1 et H2 relèvent essentiellement d'exigences de réalisation, tandis que H3, H4 et H5 relèvent de comparaisons expérimentales. Cette distinction est correcte, mais elle révèle une faiblesse de conception du protocole de recherche : des exigences fonctionnelles ont été présentées comme des hypothèses scientifiques au même titre que des propositions comparatives. Un programme qui lit correctement des données satisfait une spécification logicielle. Cela ne constitue pas nécessairement une contribution scientifique.

**A.2. Aucune des cinq hypothèses n'est entièrement validée.** Le tableau 7.1, page 138, présente les statuts suivants :

| Hypothèse | Statut | Évaluation |
|---|---|---|
| H1 — Lecture et normalisation | Partiellement soutenue | Lecture testée, complétude insuffisante |
| H2 — Architecture et reprise | Partiellement soutenue | Fonctionnement testé, effet spécifique des agents non isolé |
| H3 — Routage spécialisé | Non tranchée | Comparateur principal absent |
| H4 — Modèles légers | Non tranchée | Supériorité prédictive infirmée dans les tests retenus |
| H5 — Mémoire et gouvernance | Non tranchée | Gain conditionnel, validation incomplète |

L'auteur écrit explicitement : « Aucune hypothèse n'est validée. » Cette formulation est cohérente avec les limites présentées. Elle impose toutefois une question au jury : si les hypothèses centrales ne sont pas établies, sur quelle contribution scientifique précisément repose la défense du mémoire ? Un mémoire n'a pas l'obligation de confirmer ses hypothèses. Leur réfutation peut constituer un résultat scientifique valable. Mais il doit produire une connaissance suffisamment précise, contrôlée et utile pour dépasser une simple constatation d'échec. Le manuscrit commence à satisfaire cette exigence grâce aux comparaisons supplémentaires, sans l'atteindre complètement.

**A.3. Le préenregistrement reste partiel.** À la page 8, l'auteur reconnaît qu'aucun des critères généraux de H1 à H5 n'a été préenregistré. Ce sont certains protocoles complémentaires qui l'ont été. Les grandeurs manquantes comprennent notamment le taux d'exécutions incompatibles de H3, le budget de ressources de H4 et la métrique de priorisation de H5. L'affirmation de préenregistrement doit donc rester limitée aux campagnes concernées. Par ailleurs, un protocole rédigé et commité avant son exécution peut être préenregistré au niveau d'une campagne donnée, même si cette campagne a été conçue après la lecture d'expériences antérieures. Ce n'est toutefois pas équivalent à une hypothèse confirmatoire fixée avant l'ensemble du programme de recherche.

### B. Méthodologie expérimentale et résultats prédictifs (gravité élevée)

**B.1. Les modèles ne surpassent pas les règles simples sur les tests retenus.** C'est le résultat le plus problématique pour une revendication de supériorité prédictive. Le tableau 4.15, page 116, montre :

| Dataset et protocole | Meilleure règle simple | Modèle principal |
|---|---|---|
| CICIDS2017 — holdout scénario | 0,4733 | 0,2337 |
| CICIDS2017 — temporel | 0,6667 | 0,5566 |
| HDFS — niveau bloc | 0,8724 | 0,8684 |
| BGL — événement | 0,9137 | 0,9137 |
| CSE-CIC-IDS2018 | 0,9997 | 0,9992 |

Valeurs F1. Modèles : régression logistique, Histogram ou autres modèles principaux selon le corpus. Les règles ne sont pas des détecteurs opérationnels recommandés. Source : tableau 4.15, page 116 du mémoire.

Il faut interpréter ces chiffres sans exagération. Ils ne démontrent pas que tous les modèles d'apprentissage automatique sont inutiles, ni qu'Ariel Logminer ne possède aucune valeur. Ils montrent que les modèles principaux choisis n'apportent pas de gain F1 sur les règles simples retenues, dans les protocoles présentés. Cela suffit à contester leur supériorité expérimentale dans ce périmètre.

**B.2. La spécialisation ne résout pas la généralisation inter-attaques.** La section 4.8, pages 102–103, introduit une nouvelle comparaison sur 18 catégories d'attaques et cinq graines, avec un modèle commun et des modèles spécialisés.

| Famille | F1 commun | F1 spécialisé | Différence |
|---|---|---|---|
| CICIDS | 0,1349 | 0,1514 | +0,0165 |
| Linux/auth | 0,0528 | 0,2197 | +0,1669 |
| UNSW | 0,7817 | 0,7910 | +0,0093 |

Ces résultats montrent une amélioration dans certaines familles, mais pas une validation générale de la spécialisation. La non-infériorité globale échoue parce que la borne inférieure de l'intervalle de confiance de CICIDS descend à −0,0190, sous la marge préétablie de −0,01. Sur CICIDS et Linux/auth, les deux modèles restent également très faibles en valeur absolue. Une autre limitation est importante : le modèle spécialisé reçoit la famille correcte. Le protocole teste donc une attribution parfaite, et non les erreurs réelles du routeur. Le gain du modèle spécialisé et le gain du routage effectif restent deux questions différentes.

**B.3. Une expérience antérieure comporte une contamination de données reconnue.** À la page 103, l'auteur indique que l'expérience E-H3b n'est pas retenue parce que son chargement inclut l'étiquette dans le résumé numérique d'UNSW et réduit CICIDS à un sous-ensemble inadéquat. C'est un défaut expérimental sérieux, car inclure la variable cible dans les caractéristiques peut invalider l'évaluation. Le résultat concerné est heureusement exclu des conclusions principales et ses artefacts sont conservés. Mais cela conduit à une exigence supplémentaire : le jury doit demander un audit systématique du pipeline de préparation des données et des tests automatisés empêchant toute réintroduction de la cible parmi les variables prédictives.

**B.4. La validation multiformat reste superficielle.** La page 103 indique que 7 001 unités ont été traitées, mais qu'Apache est représenté par une seule ligne synthétique. Le mémoire reconnaît aussi qu'aucun champ standard n'est rempli pour certaines sources tabulaires réseau. Le succès de lecture et d'émission ne prouve donc pas la fidélité sémantique de la normalisation. La difficulté devient plus grave au regard du titre du mémoire : aucune expérience ne démontre l'analyse conjointe d'un même incident à partir de journaux système et réseau. La pluralité des formats acceptés n'est pas équivalente à une véritable corrélation inter-source.

### C. Évaluation de l'architecture multi-agents (criticité très élevée)

**C.1. Le mécanisme central de Contract Net ne démontre pas d'avantage propre.** La nouvelle section 4.10.4, page 109, compare Contract Net à un répartiteur au moindre chargé, sans négociation.

| Scénario | Débit du répartiteur | Débit Contract Net | Rapport |
|---|---|---|---|
| Nominal, 2 ms | 1 098 | 955 | 0,870 |
| Fiabilité hétérogène | 962 | 824 | 0,859 |
| Panne silencieuse | 882 | 783 | 0,890 |
| Agent lent, 10 ms | 832 | 733 | 0,881 |

Débits en tâches par seconde. Comparaison sur 30 graines appariées.

Contract Net présente un débit inférieur dans les quatre scénarios. Les taux d'échec à la première exécution sont essentiellement identiques entre les deux solutions. Les gains observés auparavant face à une table statique sont donc largement explicables par la prise en compte de la charge, plutôt que par la négociation. Cette expérience isole mieux la contribution propre du protocole. La conclusion qui en découle est sévère : dans le protocole testé, Contract Net ajoute un coût sans procurer de bénéfice supplémentaire mesurable par rapport à un répartiteur plus simple. Il serait cependant incorrect d'en déduire que Contract Net est inutile dans tout environnement distribué. Le comparateur accède directement à l'état des agents dans un seul processus, sans coût de communication ni information périmée. Cet avantage expérimental doit être conservé dans l'interprétation.

**C.2. La mémoire persistante ne produit un gain que dans un cas extrême.** La section 4.10.2, tableau 4.11, page 107, teste une mémoire activée et désactivée lorsque les agents possèdent des probabilités de défaillance différentes.

| Probabilité d'échec | Réduction d'échec initial | Rapport de débit D/C | Gain établi |
|---|---|---|---|
| 0,3 | −0,0027 | 0,972 | Non |
| 0,6 | −0,0302 | 0,975 | Non |
| 0,9 | −0,2993 | 1,210 | Oui |

Le mémoire applique un critère conjoint portant sur la diminution des échecs et la préservation du débit. Le gain n'est confirmé qu'à une probabilité d'échec de 90 %. De plus, l'indice d'équité de Jain se dégrade dans cette condition. La mémoire aide à éviter l'agent peu fiable, mais peut concentrer davantage la charge ailleurs. Ce résultat n'établit pas une propriété générale de l'apprentissage des agents. Il démontre un effet conditionnel dans une simulation où la confiance déclarée est volontairement éloignée de la fiabilité réelle.

**C.3. Le protocole de reprise présente encore une faiblesse fonctionnelle.** À la page 108, l'auteur relève que certains agents occupés au moment de l'appel d'offres n'entrent pas dans la liste de repli. Dans une campagne de 30 000 tâches, les pertes finales restent rares, mais ne sont pas nulles pour Contract Net, alors que la table statique effectue parfois toutes les tâches. Cela impose une question technique précise : pourquoi un système conçu pour gérer le refus, la réattribution et la reprise peut-il perdre des tâches alors qu'un mécanisme de repli plus simple les termine ? Un jury devrait exiger une analyse causale de ces pertes, et non seulement un pourcentage global de succès.

**C.4. La distribution sur deux machines ne démontre pas de montée en charge.** Le résumé et la section 4.12 indiquent qu'en saturation la deuxième machine virtuelle ne traite que 1,23 % des tâches réussies. L'architecture est distribuée sur le plan de l'exécution et des messages. Mais l'ajout de cette seconde machine n'augmente pas la capacité observée dans la configuration testée. Une propriété fonctionnelle de distribution n'équivaut pas à une propriété de scalabilité.

### D. Cadre théorique et originalité (criticité importante)

Le chapitre 1 a été renforcé. Il comprend désormais des comparaisons avec les cadres intégrés d'analyse de journaux, les moteurs de workflow, les files de tâches et les différentes politiques d'orchestration. Cela réduit l'une des faiblesses de la première version. Néanmoins, la contribution demeure principalement fondée sur l'intégration de mécanismes connus. L'auteur reconnaît dans son résumé, page vi : « Le travail n'introduit aucun nouvel algorithme ». Cette absence de nouveauté algorithmique n'est pas automatiquement éliminatoire pour un mémoire en génie informatique. Une architecture, une méthode d'évaluation ou une étude expérimentale peut constituer une contribution scientifique. Mais l'originalité doit alors venir de la connaissance obtenue. Ici, plusieurs constats sont déjà documentés dans la littérature : vulnérabilité aux raccourcis statistiques, limites des datasets de cybersécurité, fragilité de la généralisation et nécessité de comparer les modèles à des règles simples. Le manuscrit lui-même qualifie certains résultats de réplication de critiques publiées. Sa contribution scientifique défendable est donc plus étroite : une étude expérimentale de mécanismes d'intégration et d'orchestration, sur un prototype donné, sous contraintes de laboratoire. Le titre du mémoire reste acceptable, puisqu'il annonce une conception et une évaluation, non une supériorité. En revanche, toute revendication d'une architecture plus intelligente, plus performante ou plus robuste que les alternatives exigerait des preuves supplémentaires.

### E. Validité statistique et reproductibilité

**E.1. Les comparaisons appariées renforcent la rigueur, sans éliminer les biais de conception.** Les nouvelles campagnes utilisent trente graines appariées et des intervalles de confiance à 95 %. Cela améliore la précision des comparaisons dans les conditions retenues. Toutefois, des graines différentes ne créent pas trente environnements de production indépendants. Elles ne reproduisent pas nécessairement la diversité des charges, des réseaux, des machines et des défaillances réelles. La validité externe reste donc limitée. De même, dans E-H3B-STRICT-HOLDOUT, les mesures par graine et catégorie d'attaque peuvent partager les mêmes observations et les mêmes structures de données. Il faut veiller à ne pas traiter artificiellement ces mesures corrélées comme autant d'expériences indépendantes.

**E.2. Le traitement de la préinscription expérimentale doit rester rigoureux.** La déclaration relative à l'IA, page v, précise les protocoles versionnés avant exécution et distingue les campagnes exploratoires. C'est une amélioration documentaire, mais deux vérifications sont nécessaires : les commits des protocoles doivent réellement précéder les exécutions correspondantes ; les modifications du runner doivent être vérifiables et ne pas avoir modifié les critères après lecture des résultats. Le PDF ne permet pas à lui seul de certifier ces deux conditions.

**E.3. L'intégrité des artefacts ne garantit pas la reproductibilité.** Le chapitre 7 décrit une matrice de preuves, des identifiants de campagnes, des paramètres et des empreintes SHA-256. Une empreinte établit que le contenu d'un fichier n'a pas changé par rapport à la version de référence. Elle ne démontre pas que son calcul est correct. Pour certifier la reproductibilité, il faut pouvoir reprendre les données, reconstruire l'environnement, exécuter les scripts et obtenir les métriques correspondantes. Je ne dispose pas du dépôt ni de ses artefacts exécutables dans cette évaluation. Je ne peux donc pas vérifier indépendamment les résultats numériques.

### F. Qualité formelle, références et intégrité académique

La nouvelle version présente une structure complète : introduction, état de l'art, conception, implémentation, résultats, validité scientifique, discussion, reproductibilité, conclusion et annexes. L'organisation est identifiable, mais elle demeure très fragmentée. Les 26 sections du chapitre 1 et les 26 sections du chapitre 2 produisent une succession de développements parfois courts qui pourrait être rationalisée. Un défaut de fond demeure également : la discussion scientifique consacrée à la contribution propre des agents est dispersée entre les chapitres 4, 5, 6 et 7. Le lecteur doit reconstruire lui-même la distinction entre propriétés implémentées, propriétés testées et propriétés effectivement supérieures. Sur l'intégrité académique, la déclaration des outils ChatGPT, Codex, Copilot SDK et Claude Code est explicite. La mention de leur assistance à la programmation et à l'exécution de campagnes expérimentales nécessite un contrôle de provenance des scripts, mais ne prouve aucune fraude. Je n'identifie pas de preuve de plagiat à partir du document seul. Un contrôle textuel externe et une vérification des références seraient nécessaires pour conclure sur ce point.

## 4. Les huit faiblesses les plus graves

| Rang | Défaillance scientifique | Localisation | Priorité |
|---|---|---|---|
| 1 | Aucune hypothèse intégralement validée | Tableau 7.1, p. 138 | Critique |
| 2 | Aucune supériorité prédictive des modèles principaux face aux règles simples | Tableau 4.15, p. 116 | Critique |
| 3 | Pas d'avantage propre de Contract Net face au moindre chargé | §4.10.4, p. 109 | Critique |
| 4 | Pas d'analyse conjointe d'incidents système et réseau | §4.9 et §5.8 | Élevée |
| 5 | H3 non tranchée, comparateur sans routage absent | §4.8 et tableau 7.1 | Élevée |
| 6 | Mémoire bénéfique uniquement sous défaillance extrême dans l'expérience | Tableau 4.11, p. 107 | Élevée |
| 7 | Validation distribuée insuffisante pour démontrer la scalabilité | §4.12 | Élevée |
| 8 | Originalité méthodologique encore trop proche de critiques déjà publiées | §1.24 et §6.7 | Importante |

## 5. Points susceptibles d'empêcher une validation sans réserves

Le manuscrit ne permet pas de prononcer une non-recevabilité institutionnelle automatique : cette décision dépend des critères de l'Université et du jury. En revanche, quatre objections justifient une révision majeure.

- Première objection — L'objet scientifique doit être resserré. Le mémoire ne peut pas être défendu comme la démonstration d'une architecture multi-agents plus performante que les alternatives. Il peut être défendu comme une étude expérimentale critique de l'intégration, de l'orchestration et de la validité des évaluations.
- Deuxième objection — La normalisation hétérogène doit être démontrée au-delà de la lecture. Le fait de traiter 7 001 unités ne prouve ni la fidélité des champs ni la capacité de relier les événements de différents formats à un même incident.
- Troisième objection — Les hypothèses doivent être closes rigoureusement. H3 et H5 nécessitent les expériences qui manquent. H4 doit être présentée comme non validée avec une composante de supériorité infirmée, sans laisser entendre qu'un budget de ressources peut être fixé rétrospectivement.
- Quatrième objection — Les expériences doivent être auditables. Les commits de préenregistrement, le code, les partitions, les graines et les artefacts doivent être accessibles au jury pour permettre au moins une reproduction ciblée.

Ces objections ne justifient pas d'effacer les résultats négatifs ou de remplacer les hypothèses par de nouvelles affirmations favorables. Cela reviendrait à affaiblir davantage la validité du mémoire.

## 6. Note finale et justification

| Critère | Maximum | Points obtenus | Points perdus |
|---|---|---|---|
| Fond : problématisation, théorie, méthode, résultats, interprétation | 12 | 7,25 | −4,75 |
| Structure, rédaction scientifique et documentation | 4 | 3,25 | −0,75 |
| Originalité et apport scientifique | 2 | 0,75 | −1,25 |
| Rigueur, traçabilité et reproductibilité | 2 | 1,25 | −0,75 |
| Total | 20 | 12,50 | −7,50 |

Fond — 7,25/12. Les comparaisons supplémentaires apportent des connaissances expérimentales vérifiables dans le cadre décrit. Mais les hypothèses demeurent non résolues, la contribution prédictive est limitée et les gains de l'architecture ne sont pas démontrés au-delà de conditions spécifiques.

Forme — 3,25/4. Le document est organisé, mais trop fragmenté et parfois répétitif. Les limites, résultats et conclusions sont maintenant plus cohérents.

Originalité — 0,75/2. L'apport est essentiellement architectural et méthodologique. Les observations sur les datasets et les mécanismes de distribution prolongent des résultats déjà connus, sans innovation théorique démontrée.

Rigueur — 1,25/2. Les protocoles supplémentaires, les comparaisons appariées, les intervalles de confiance et la matrice de preuves justifient la progression. La certification reste limitée par l'absence d'audit indépendant et par des critères initiaux non préenregistrés.

---

# Lecteur 2 — 9,25/20

Évaluation du mémoire « Architecture multi-agents légère pour l'analyse de journaux système et réseau hétérogènes — Ariel Logminer » (MARHEGANE BITATI A. O., FP/UNIKIN, 2025–2026)

## 1. Synthèse globale

Le mémoire annonce une architecture multi-agents intelligente, distribuée et multi-source. Ses propres expériences montrent que cette architecture n'apporte rien de mesurable par rapport à des solutions plus simples. Aucune des cinq hypothèses n'est validée. Les deux hypothèses « partiellement soutenues » (H1, H2) sont, de l'aveu de l'auteur, des exigences de réalisation vraies par construction. La seule question qui reçoit une réponse nette (QR6, la dépendance des scores au protocole) reproduit des critiques déjà publiées par Sommer & Paxson, Arp et al., Engelen et al. et Le & Zhang, et l'auteur le reconnaît lui-même. L'honnêteté du compte rendu est réelle, mais elle ne remplace pas une contribution : un mémoire qui démontre avec rigueur que son objet ne sert à rien n'en reste pas moins sans résultat positif. S'ajoutent un problème sérieux de paternité intellectuelle : une large part des campagnes a été conçue et exécutée par des agents d'IA, dans les 48 heures qui précèdent la compilation du PDF. Et aucun dépôt de code accessible n'est fourni.

## 2. Critique détaillée par axe

### 2.1 Problématisation

- La question centrale est descriptive, pas problématique (p. 5). « Dans quelle mesure… peut-elle lire… et que coûte cette organisation » appelle un inventaire, pas une thèse. Rien n'y oppose deux explications concurrentes.
- H1 et H2 sont des tautologies. L'auteur écrit lui-même (p. 8) que, sans magasin d'idempotence, le rejeu répète l'effet « par construction ». Une hypothèse qui ne peut être réfutée que par un bug n'est pas une hypothèse scientifique.
- H3, H4 et H5 n'ont pas été rendues opérationnelles avant les expériences. Le texte l'admet (p. 8) : le « taux d'exécutions incompatibles » (H3), le « budget local de temps et de mémoire » (H4) et la « métrique de priorisation » (H5) n'ont jamais été fixés. Elles ne sont donc pas falsifiables telles que formulées. Le statut « non tranché » du tableau 7.1 (p. 138) ne découle pas de l'expérience : il était garanti dès la rédaction de l'introduction.
- Questions et hypothèses ne se correspondent pas. Il y a six QR pour cinq hypothèses ; QR4 (tableau de bord) n'a ni hypothèse ni mesure (tableau 2, p. 7).
- Le titre promet ce que le travail exclut. On y lit « journaux système et réseau hétérogènes ». Or l'auteur précise (p. vi, p. 5) qu'aucun incident n'est analysé conjointement à partir des deux types de sources. L'« hétérogénéité » se réduit à lire plusieurs formats séparément.

### 2.2 Méthodologie

Ce qui est solide. Le parseur est ajusté sur l'entraînement puis gelé, avec contrôle par empreinte (p. 89). Les seuils sont choisis sur la validation. Les modèles sont comparés à des règles triviales sur le même test (tableau 4.15). L'ablation de l'idempotence sur les architectures A et B est bien construite (tableau 4.10).

Ce qui ne l'est pas :

- Le benchmark A–D est vidé de sens par sa charge. Des micro-tâches à 72 657 tâches/s pour le monolithe (tableau 4.9, p. 105) mesurent seulement le coût fixe des messages. Conclure que les agents sont 55 à 72 fois plus lents sur des tâches qui ne font rien est trivial. La seule expérience pertinente, avec des tâches d'inférence réalistes, n'est pas faite.
- La comparaison des cinq modèles CICIDS2017 est invalide par construction. Le F1 est calculé au seuil par défaut, sans calibration (p. 87) ; l'auteur concède que le classement « dépend de ce seuil autant que des modèles ». Les échantillons sont plafonnés arbitrairement (8 000/4 000 lignes, p. 86). Le scénario Infiltration, avec 32 attaques, pèse autant que les autres dans la moyenne. Résultat : « tout positif » (0,4733) bat les cinq candidats (p. 88). Ce n'est pas une découverte, c'est le symptôme d'un protocole mal conçu.
- Des données connues pour être erronées ont été utilisées. Le texte cite Engelen et al. et Lanvin et al., puis emploie délibérément les CSV non corrigés (p. 85). Plus loin, il parle des « mêmes données corrigées » (p. 103), ce qui est incohérent.
- Une section entière repose sur des fichiers CSE-CIC-IDS2018 peut-être tronqués. Seules deux journées sont « disponibles localement » (p. 95), et chaque fichier compte exactement 2²⁰−1 lignes, ce qui évoque une troncature par un tableur (p. 101). L'auteur se contente de dire que cela « appelle une vérification ». Un jury ne peut pas accepter un audit de jeu de données mené sur des fichiers dont l'intégrité n'a pas été vérifiée, alors que le jeu complet est public.
- Le protocole BGL principal est dégénéré. Il y a 49 999 lignes d'entraînement, toutes de sévérité INFO, pour 7 clusters Drain3 (p. 92). Le seuil retenu vaut le score maximal possible. Le « détecteur » Histogram revient donc exactement à la règle « sévérité inconnue ». Ensuite, huit variantes sont explorées « sans plan préalable », et le protocole G est conçu après avoir vu la position des anomalies dans le test (p. 94). C'est un cas d'école de recherche à chemins multiples (« garden of forking paths »). L'auteur le reconnaît, mais le tableau 4.5 reste dans le corps du texte.
- La réplication HDFS par graines est fictive. Les cinq graines donnent la même matrice de confusion (p. 90) : il n'y a pas cinq observations indépendantes. Le parseur n'est ajusté que sur 6 000 blocs, soit 1,7 % de l'entraînement, sans justification (p. 90). La prévalence au test (1,46 %) n'est pas la même qu'en validation (3,48 %).
- Le préenregistrement est auto-certifié. Les protocoles sont « versionnés et commités » par l'auteur lui-même (p. v), sans registre externe. E-CNP-LEAST-LOADED a été « décidé après lecture de la comparaison précédente » (p. 109). Les artefacts préenregistrés sont dans phase_revision_20261105 (p. 131–132), la date même de compilation du PDF (5 novembre 2026). Ce préenregistrement ne vaut pas plus qu'un commit git.
- Les comparateurs décisifs n'ont pas été exécutés. H2 : la condition « agents sans idempotence » n'a jamais été lancée (tableau 7.1). H3 : la chaîne sans routage n'a pas été exécutée, au motif que l'inventaire local ne fournit que « 45 candidats pour 90 sources » (p. 123). Ce n'est pas une impossibilité, c'est un défaut de préparation : Loghub à lui seul fournit plus de 16 sources.
- Le routeur est partiellement circulaire. Ses scores intègrent les colonnes dataset et subtype produites par le parseur de format (p. 75) : le routage reprend donc en partie la détection de format. La calibration repose sur 3 fichiers inconnus (IC à 95 % du rejet : [0,292 ; 1], p. 101).
- La corrélation est évaluée en circuit fermé : le corpus synthétique est construit avec les clés mêmes du corrélateur (p. 35, p. 115). Le corpus de référence compte 16 anomalies.
- La distribution n'est pas démontrée. L'endurance tourne à 0,5 tâche/s, très loin de la capacité (p. 112). En saturation, la seconde VM traite 1,23 % des tâches (p. 113). En détection HDFS distribuée, 100 % des tâches vont à debian-alpha (p. 115). La trace des messages est tronquée à 10 001 événements, ce qui invalide les compteurs du protocole (p. 112).
- Un défaut grave a été découvert par hasard, et rien n'indique qu'il soit isolé. L'étiquette d'UNSW fuyait dans les variables d'E-H3b, ce qui n'a été vu qu'en relisant le code (p. 103). L'auteur écrit que les autres campagnes « n'ont pas fait l'objet d'un audit de code aussi poussé » (p. 119). C'est reconnaître que la validité interne de toutes les autres campagnes n'est pas établie.
- Il n'y a aucune correction pour comparaisons multiples, alors que les comparaisons appariées sont nombreuses (E-H5, E-CNP, E-CNP-LL, E-H3b stricte) et les critères multiples.

### 2.3 Cadre théorique

- Le chapitre 1 est un catalogue de manuel. LOF et One-Class SVM sont présentés (p. 23) puis jamais utilisés. De même pour Extra Trees et le gradient boosting, introduits sans lien avec une question.
- La littérature qui aurait prédit les résultats est absente. Rien sur l'allocation de tâches et l'équilibrage de charge (« power of two choices », files de type JSQ). C'est précisément ce qui aurait annoncé que le moindre chargé égale Contract Net. Sur les systèmes multi-agents, l'auteur s'en tient à Smith (1980), FIPA (2002), Wooldridge (2009) et AAFID (1998). Il n'y a aucun travail récent sur l'allocation négociée, ni sur les agents pour SOC ou IDS.
- Le détecteur central, « Histogram », n'est rattaché à aucune référence (§3.8.1). C'est un score de rareté fréquentielle naïf, présenté sans filiation.
- La définition « opérationnelle » de l'agent (p. 4) vide le concept de sa substance. La spécification de l'utilité (p. 77–78) le confirme : M = 1 pour toute offre émise ; A = L, deux composantes identiques ; dans les campagnes Redis, U = 0,65 + 0,30C + 0,20H + 0,05T ; le seuil de refus est inactif. L'« intelligence » se réduit à une somme pondérée à poids fixes, dont la moitié des termes sont constants. Le vocabulaire « agents autonomes intelligents » n'est pas tenu.
- Plusieurs jeux de données sont utilisés sans présentation ni référence : UNSW (UNSW-NB15, Moustafa & Slay, absent de la bibliographie), Linux/auth, Solaris BSM et DARPA 1998 (p. 101–103). C'est un manquement bibliographique net.

### 2.4 Argumentation

- Le titre et la conclusion surévaluent ce que montre le corps du texte. La conclusion affirme que le prototype « sait normaliser plusieurs sources » (p. 140), alors que les flux réseau remplissent 0 champ standard sur 7 (p. 104). Le compte de « 7 001 unités » est gonflé par une fixture Apache d'une seule ligne (p. 75).
- Le chapitre 1 contient des résultats. Il cite la section 4.2 (p. 25), anticipe les conclusions (p. 42) et le tableau 1.6 (p. 44) intègre « établi seulement pour une probabilité d'échec de 0,9 ». L'état de l'art a donc été réécrit après les expériences pour coller aux résultats. La distinction entre cadre et constats disparaît.
- E-H5 fabrique les conditions de son seul gain. La confiance déclarée est « volontairement erronée » (p. 108) ; le gain n'apparaît qu'à p = 0,9, une configuration ad hoc sans justification opérationnelle.
- Le chapitre 2 (« modèle proposé ») est formulé au conditionnel (« peut comprendre », « peut notamment », « le système peut… »). Ce sont des listes de possibilités, pas une spécification architecturale vérifiable.

### 2.5 Forme

- Le texte est redondant à l'extrême. Sur 180 pages, j'ai compté dans le texte extrait : « 0,1577 » apparaît 9 fois, « 0,8724 » 14 fois, « 20/20 » 14 fois, « 7 001 » 10 fois. Le résumé, l'abstract, le bokuse, l'introduction, les chapitres 1, 4, 5 et 6 et la conclusion répètent les mêmes chiffres. Le chapitre 7 et l'annexe A.3 redoublent les chapitres 4 et 5. Un tiers du volume pourrait être supprimé sans perte.
- Le résumé est une liste de chiffres (p. vi), illisible pour un lecteur non initié. Le bokuse est plus long et différent du résumé français : il contient des intervalles de confiance absents de celui-ci (p. x–xii).
- Le jargon interne envahit le texte. Des identifiants comme agent4_bgl_second_protocol_20261104T142629Z figurent dans les légendes et le corps. Les préfixes « agent2 à agent6 » désignent des campagnes d'agents automatisés.
- La précision numérique est incohérente : l'auteur annonce quatre décimales, puis écrit « [0,8568 ; 0,879493] » (p. 89, p. 123).
- Beaucoup de références sont des pages de documentation web (Kafka, Celery, Redis, Temporal, Wazuh, Elastic, OpenSearch, OCSF, Loglizer), « consultées le 5 novembre 2026 » (9 occurrences), soit le jour de compilation du PDF. Aucun DOI n'est donné. Sharafaldin et al. sert de référence à deux jeux distincts.
- Plusieurs tableaux sont surchargés au point d'être illisibles (1.4, 1.5, 7.1).

### 2.6 Apport scientifique

L'auteur le dit lui-même : aucun algorithme, aucun schéma, aucun protocole nouveau (p. 42). Les constats prédictifs répliquent la littérature (p. 42, p. 125). Côté architecture, les expériences établissent quatre résultats négatifs : les agents coûtent cher ; l'idempotence ne leur doit rien ; la négociation n'apporte rien face au moindre chargé ; la seconde machine n'ajoute pas de capacité. L'apport restant est un banc d'essai instrumenté dont le code n'est pas accessible au jury (voir §2.7). Pour un TFE d'ingénieur, un tel banc est un exercice d'ingénierie respectable. Ce n'est pas une contribution scientifique.

### 2.7 Autonomie et reproductibilité

- La déclaration sur l'IA (p. iv) est honnête, mais elle est accablante. Claude Code a assuré la « proposition et mise en œuvre de protocoles complémentaires », « l'écriture ou adaptation de scripts » et « l'exécution de campagnes dans l'environnement de l'auteur ». ChatGPT a assuré la « structuration et reformulation du manuscrit ».
- Le calendrier confirme cette délégation. Les artefacts portent 31 fois la date 20261104 et 13 fois la date 20261105. Les comparaisons préenregistrées (E-H3b, E-H4, E-H5, E-CNP, E-CNP-LL, E-H3b stricte), qui portent les conclusions architecturales, datent donc des 48 heures qui précèdent la compilation.
- La part intellectuelle de l'étudiant n'est pas démontrable à partir du document. Seule la soutenance peut l'établir.
- Aucun dépôt n'est fourni. Le texte dit que le dépôt « doit contenir » le code et les scripts (p. 133), mais ne donne ni URL, ni archive, ni DOI. La « matrice résultats–preuves » (annexe A.3) pointe vers des chemins locaux que le jury ne peut pas vérifier. L'auteur admet qu'aucune reproduction par un tiers n'a eu lieu (p. 131, p. 134).

## 3. Faiblesses majeures, par ordre de gravité

1. Aucune contribution scientifique positive. Aucune hypothèse n'est validée, et le seul résultat net (QR6) réplique des travaux publiés.
2. Hypothèses mal construites dès le départ. H1 et H2 sont tautologiques ; H3, H4 et H5 n'ont pas de grandeurs fixées, donc elles ne pouvaient pas être tranchées (p. 8).
3. Paternité des expériences clés incertaine. Elles ont été conçues et exécutées par des agents d'IA, au dernier moment, ce qui rend l'apport personnel invérifiable sur pièces.
4. Le titre n'est pas tenu. Il n'y a ni analyse conjointe système/réseau, ni normalisation effective des flux (0/7 champs), ni distribution réelle (1,23 % ; 100 % sur un seul agent), ni « intelligence » (utilité à termes constants).
5. Comparateurs décisifs non exécutés. C'est le cas de la chaîne sans routage (H3) et des agents sans idempotence (H2).
6. Données au minimum douteuses. CSE-CIC-IDS2018 est peut-être tronqué et n'a pas été vérifié ; CICIDS2017 est utilisé non corrigé en connaissance de cause.
7. Validité interne non établie pour la plupart des campagnes. Une fuite d'étiquette a été trouvée par hasard, et les autres campagnes n'ont pas été auditées (p. 119).
8. Benchmark architectural non pertinent. Les micro-tâches vides tranchent d'avance la comparaison agents/monolithe.
9. Recherche à chemins multiples sur BGL. Le protocole G a été conçu après avoir vu le test, et le protocole principal est dégénéré.
10. Reproductibilité déclarée mais non vérifiable. Le dépôt n'est pas accessible, et le préenregistrement est auto-certifié.

## 4. Points de non-recevabilité en l'état

1. Absence de dépôt accessible (code, scripts, configurations, manifestes). Sans lui, toute la stratégie de preuve du mémoire (« les valeurs proviennent des CSV/JSON identifiés », p. iv) est invérifiable. C'est une condition bloquante.
2. Attestation de l'apport personnel. Le jury doit exiger, en soutenance ou par écrit, que l'étudiant explique et justifie lui-même les protocoles E-H5, E-CNP et E-CNP-LL, la fonction d'utilité et le découpage HDFS/BGL. Faute de quoi le travail ne peut pas être attribué au candidat.
3. Intégrité de CSE-CIC-IDS2018. Il faut soit vérifier les fichiers contre la distribution officielle, soit retirer la section 4.6 et les conclusions qui en dépendent (H4).
4. Mise en cohérence du titre et de la conclusion avec les résultats. Il faut retirer « hétérogènes » au sens multi-source, requalifier « multi-agents intelligents », et corriger l'affirmation « sait normaliser » (p. 140).
5. Références des jeux UNSW, Linux/auth, Solaris BSM et DARPA 1998, absentes de la bibliographie.

## 5. Note finale

| Critère | Barème | Points | Points perdus et justification |
|---|---|---|---|
| Fond : problématisation et hypothèses | 3 | 0,75 | −2,25 : question descriptive ; H1/H2 tautologiques ; H3–H5 sans grandeurs fixées, donc non falsifiables |
| Fond : méthodologie expérimentale | 5 | 2,75 | −2,25 : benchmark sur micro-tâches ; seuils par défaut ; données non vérifiées ; comparateurs H2/H3 absents ; chemins multiples sur BGL ; un seul processus. Crédit pour le parseur gelé, les baselines triviales, l'ablation de l'idempotence et les intervalles de confiance |
| Fond : cadre théorique | 2 | 1 | −1 : catalogue, littérature allocation/équilibrage et MAS récente absente, détecteur central sans référence, jeux de données non cités |
| Fond : argumentation | 2 | 1,25 | −0,75 : conclusions en grande partie calibrées, mais titre et conclusion surévaluent ; résultats injectés dans l'état de l'art |
| Forme | 4 | 2 | −2 : redondance massive, jargon d'identifiants, résumé illisible, précision incohérente, bibliographie dominée par des pages web consultées le jour de compilation |
| Originalité et apport | 2 | 0,5 | −1,5 : aucun apport conceptuel ; constats répliqués ; architecture surpassée par des solutions plus simples |
| Rigueur, autonomie, reproductibilité | 2 | 1 | −1 : traçabilité interne réelle, mais dépôt inaccessible, préenregistrement auto-certifié, exécution déléguée à l'IA |
| Total | 20 | 9,25 | |
