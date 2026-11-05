# Retours des trois lecteurs (fournis par l'auteur le 2026-11-05, texte intégral)

Les numéros de page renvoient au PDF compilé le 2026-11-05 (`ARIEL_LOGMINER_MEMOIRE_FINAL/main.pdf`, 166 pages). Un fragment de graphique, mal collé, a été conservé tel quel dans le retour du lecteur 1 (A.3).

---

## Retour Lecteur 1

### 1. Synthèse globale : verdict du jury

Le mémoire présente une réalisation d'ingénierie logicielle accompagnée de campagnes expérimentales, mais la démonstration scientifique reste incomplète sur plusieurs revendications centrales. Deux des cinq hypothèses demeurent non tranchées, et une troisième n'est que partiellement soutenue malgré l'absence d'un critère de décision préenregistré ; la normalisation, la spécialisation, la mémoire persistante et l'intérêt propre de l'architecture multi-agents ne sont donc pas tous établis avec le niveau de preuve annoncé. Les expériences révèlent également des dépendances problématiques aux caractéristiques des datasets, des scénarios artificiels et une absence de démonstration robuste du bénéfice opérationnel. La contribution apparaît principalement comme une intégration technique et une étude de protocoles expérimentaux, plutôt que comme une avancée théorique ou algorithmique clairement établie.

Verdict provisoire : recevabilité académique possible avec réserves scientifiques majeures, mais pas validation sans corrections substantielles.

La note définitive sera donnée après l'examen détaillé des six axes. L'évaluation porte sur le manuscrit fourni ; le dépôt source, les CSV, les JSON et les exécutions expérimentales ne sont pas joints, ce qui empêche leur audit indépendant.

### 2. Critique détaillée par axe

#### A. Méthodologie et validité expérimentale — Criticité élevée

**A.1. Des hypothèses centrales ne sont pas effectivement testées**

À la page 6, H3 affirme :
« Le routage par famille réduit le taux d'exécutions incompatibles par rapport à la même chaîne sans routage, sans accroître le taux d'erreur prédictive fixé par le protocole. »

Or, à la page 127, le tableau 7.1 indique explicitement :
« Le comparateur sans routage manque et le gain prédictif n'est pas systématique. »

C'est une défaillance méthodologique majeure : l'expérience déterminante pour trancher H3 n'a pas été exécutée. L'évaluation du routeur sur des fichiers connus et inconnus ne remplace pas une comparaison contrôlée avec une chaîne sans routage.

De même, H5 exige un gain de priorisation mesurable, sans dégradation des autres métriques principales, ainsi qu'une procédure de promotion contrôlée des modèles. Le tableau 7.1 reconnaît qu'aucun gain quantitatif ni cycle complet répété de promotion et de rejet n'est démontré.

Conséquence : les revendications relatives au bénéfice de la spécialisation et de la mémoire restent des propositions architecturales insuffisamment validées. Leur existence dans le code ne constitue pas une preuve d'efficacité.

**A.2. Contradiction entre préenregistrement annoncé et protocole réalisé**

À la page 7, l'auteur affirme :
« Les seuils numériques et les budgets sont fixés dans le protocole avant l'exécution, et non choisis après lecture des résultats. »

Pourtant, le tableau 7.1, page 127, précise pour H4 :
« Le budget local n'est pas un critère de décision préenregistré. »

Les deux affirmations ne sont pas compatibles si elles portent sur le budget de H4. Cette contradiction doit être corrigée : soit les critères ont réellement été fixés et leur trace doit être fournie, soit ils ne l'ont pas été et la revendication de préenregistrement doit être restreinte.

Il ne suffit pas de rapporter un score F1 supérieur à une baseline lorsque l'hypothèse exige aussi un budget de temps et de mémoire.

**A.3. Les résultats prédictifs ne démontrent pas une généralisation solide**

À la page 82, CICIDS2017 montre une chute du F1 du Random Forest de 0,995142 avec partition aléatoire à 0,157744 sous holdout par scénario.

> [Fragment de graphique tel que collé] CICIDS2017 — F1 du Random Forest — 00,250,50,751AléatoireHoldout scénario — Source : mémoire, chapitre 4, section 4.2.

Cela ne signifie pas que l'ensemble du prototype échoue. Cela signifie que le modèle évalué généralise mal à certaines familles d'attaques tenues hors entraînement.

La distinction est fondamentale : un F1 presque parfait sous un protocole favorable n'est pas une preuve de robustesse face à des attaques ou environnements nouveaux.

L'auteur identifie cette fragilité. Le défaut scientifique résiduel est l'absence d'une stratégie démontrée permettant à Ariel Logminer de la corriger.

**A.4. Le résultat BGL est dominé par une propriété triviale des données**

À la page 87, le mémoire indique :
« Cette décision coïncide exactement avec la règle “sévérité absente de l'entraînement normal”, qui produit la même matrice de confusion et le même F1. »

Le F1 de 0,913698 ne démontre donc pas que l'algorithme Histogram apprend une structure comportementale profonde. Dans ce protocole, une règle fondée sur une sévérité inconnue reproduit exactement ses décisions.

C'est une limite de validité de construit : la métrique mesure essentiellement la capacité à reconnaître un changement de sévérité, et non nécessairement la capacité à détecter des comportements anormaux complexes.

Le manuscrit reconnaît le problème, ce qui évite de lui attribuer une interprétation erronée. Mais cela réduit la portée de la contribution prédictive.

**A.5. Le dataset CSE-CIC-IDS2018 présente un raccourci de décision majeur**

À la page 92 :
« Dst Port, utilisé seul, atteint déjà un F1 moyen de 0,999720. »

La section 4.6.4, page 95, établit que les performances sont largement déterminées par la répartition des ports de destination et les particularités des journées étudiées.

Le tableau 4.6 montre notamment :

| Protocole | F1 LR |
|---|---|
| 15 février vers 16 février, 78 variables | 0,994345 |
| Même protocole sans Dst Port | 0,728397 |
| 16 février vers 15 février | 0,234195 |
| Intra-journée 15 février | 0,989686 |

Ces écarts interdisent de présenter le score initial comme une mesure générale de détection d'intrusions transférable.

L'auteur a mené des contrôles complémentaires qui mettent précisément ce problème en évidence. Le reproche n'est donc pas d'avoir dissimulé cette faiblesse, mais de ne pas avoir démontré un mécanisme capable de la dépasser.

**A.6. La démonstration multi-agent reste partiellement découplée de la détection réelle**

La section 4.11.4, page 104, précise :
« Les scores ne sont pas recalculés dans les machines virtuelles : l'expérience évalue la chaîne de décision distribuée, non un parsing distribué. »

Cela signifie que les machines virtuelles ne réalisent pas toute la chaîne d'analyse. Elles reçoivent des scores déjà calculés et exécutent une décision à partir d'un seuil.

Le passage de messages et l'absence d'altération de prédictions sont bien testés. En revanche, la distribution effective du parsing, de l'extraction des caractéristiques et de l'inférence complète n'est pas démontrée par cette campagne.

La même section indique que les 2 000 tâches de décision sont toutes attribuées à un seul agent.

Par conséquent, la distribution logicielle est observable, mais l'équilibrage réel de cette charge entre plusieurs machines n'est pas établi.

**A.7. Des résultats de performance défavorables à l'architecture proposée**

À la page 104, le test de saturation montre que la seconde machine ne permet pas d'augmenter la capacité observée. La latence p95 dépasse 100 secondes à forte charge et trois tâches expirent.

La section 4.9 indique parallèlement que le monolithe domine les microtâches dans le benchmark retenu.

Aucune supériorité générale de performance ne peut donc être attribuée à l'architecture multi-agents sur la base des expériences présentées. L'auteur ne prétend d'ailleurs pas avoir démontré cette supériorité.

Le problème scientifique est plus précis : le mémoire ne définit pas suffisamment une situation expérimentale dans laquelle la complexité supplémentaire de l'architecture se traduit par un bénéfice opérationnel quantifié et spécifique.

#### B. Faiblesses théoriques et état de l'art — Criticité importante

**B.1. Une lacune scientifique insuffisamment démontrée**

La section 1.23, page 38, justifie le projet par la fragmentation des fonctions : détection, parsing, routage, corrélation et supervision.

L'auteur écrit :
« Il existe donc un espace entre le prototype algorithmique et la plateforme opérationnelle complète. »

Cette affirmation est plausible, mais elle ne constitue pas, à elle seule, une démonstration de nouveauté scientifique.

Le tableau 1.2, page 37, compare principalement des algorithmes, des datasets et quelques architectures historiques. Il ne confronte pas systématiquement Ariel Logminer aux plateformes modernes qui réunissent déjà ingestion de journaux, normalisation, détection, règles, corrélation et restitution.

Il manque notamment une comparaison fonctionnelle et expérimentale approfondie avec des systèmes existants tels que Wazuh, Elastic Security ou OpenSearch Security Analytics.

Ces produits ne constituent pas automatiquement des comparateurs équivalents à un prototype de recherche. Néanmoins, leur existence rend nécessaire une justification plus précise de ce qu'Ariel Logminer apporte au-delà de l'intégration de fonctionnalités connues.

**B.2. La notion d'intelligence est définie de manière opérationnelle, mais son intérêt n'est pas démontré**

À la page 4, l'intelligence de l'agent est associée à une fonction d'utilité :
\[ U=0,30C+0,20H+0,20M+0,15A+0,10L+0,05T \]

Les coefficients sont fixés avant les expériences, mais le manuscrit précise qu'ils ne constituent pas une combinaison optimale.

La définition opérationnelle est acceptable. En revanche, deux questions théoriques restent insuffisamment résolues : pourquoi cette combinaison plutôt qu'une autre, et dans quelle mesure cette politique surpasse-t-elle un ordonnanceur déterministe plus simple ?

Une politique heuristique pondérée n'est pas scientifiquement nouvelle par le seul fait d'être exécutée dans un agent.

La mémoire et la négociation sont des propriétés logicielles observables. Leur présence ne démontre ni apprentissage autonome ni capacité d'adaptation supérieure.

**B.3. Une intégration de technologies connues ne suffit pas à établir une contribution originale**

Le manuscrit reprend notamment Contract Net, Redis Streams, Drain3, Random Forest, régression logistique et plusieurs mécanismes classiques de persistance.

L'intégration constitue une contribution technique possible. Pour établir une contribution scientifique plus forte, il faudrait démontrer, par exemple, un gain reproductible de robustesse, une nouvelle règle d'allocation justifiée théoriquement ou un bénéfice mesuré de l'orchestration sur des tâches représentatives.

Les preuves actuelles ne permettent pas d'attribuer un tel gain général au système proposé.

#### C. Problématisation, questions et hypothèses — Criticité importante

**C.1. Une question centrale trop large pour une validation complète**

La question centrale, page 5, associe autonomie, distribution, modularité, exploitation par l'analyste, détection, priorisation, hétérogénéité et agents multitâches.

Cette accumulation produit un projet d'ingénierie ambitieux, mais affaiblit la précision de l'objet scientifique.

Il manque une variable principale de performance clairement priorisée. Le mémoire cherche simultanément à établir la validité d'une architecture, la qualité des modèles prédictifs, la robustesse de la distribution et l'utilité de la restitution.

Ces dimensions ne se réduisent pas à un test expérimental unique. Le manuscrit le reconnaît, mais son protocole n'apporte pas les preuves requises pour toutes.

**C.2. Certaines questions sont essentiellement descriptives**

QR2 demande comment organiser des agents spécialisés ; QR4 demande comment présenter des anomalies dans un tableau de bord ; QR6 demande comment évaluer le prototype.

Ce sont des questions légitimes de conception. Elles ne correspondent cependant pas toutes à des hypothèses explicatives ou comparatives.

La problématisation gagnerait à distinguer trois catégories : les exigences de réalisation logicielle, les hypothèses scientifiques vérifiables et les propriétés opérationnelles à mesurer.

**C.3. Un glissement entre hypothèses réfutables et hypothèses partiellement soutenues**

Les hypothèses H1 à H5 sont formulées avec des critères de réfutation. Il serait donc incorrect de prétendre qu'elles sont toutes non falsifiables.

Le défaut réside dans le traitement final de leur statut.

Par exemple, H3 est déclarée « NON TRANCHÉE », ce qui est cohérent avec le comparateur manquant. H4 est déclarée « PARTIELLEMENT SOUTENUE » bien que tous les critères conjoints annoncés n'aient pas été vérifiés.

La catégorie « partiellement soutenue » doit être distinguée d'une validation formelle de l'hypothèse originale. Les résultats favorables à une composante ne valident pas nécessairement une proposition conjonctive.

#### D. Argumentation, interprétation et discussion

**D.1. L'intérêt architectural est affirmé plus fortement que son utilité mesurée**

Dans le résumé, page vii, l'auteur écrit :
« Leur intérêt est architectural : autonomie locale, négociation, séparation des responsabilités, réattribution, idempotence et auditabilité. »

Ces caractéristiques sont réelles au niveau de la conception ou des tests décrits. Mais elles ne possèdent pas toutes le même niveau de démonstration comparative.

L'exemple le plus net est l'idempotence : à la page 100, l'ablation montre que le monolithe et les workers centralisés peuvent également éviter les doublons lorsqu'ils disposent du même magasin d'idempotence.

Le bénéfice ne provient donc pas spécifiquement du caractère multi-agent.

**D.2. Absence de démonstration de l'utilité pour les analystes**

La section consacrée à QR4, page 126, reconnaît qu'aucune étude d'utilisabilité n'a mesuré le temps d'investigation ou la charge cognitive.

Il est donc possible d'affirmer que le tableau de bord existe et offre certaines fonctionnalités. Il est impossible d'affirmer qu'il améliore effectivement le travail d'un analyste.

Cela demanderait une étude avec des utilisateurs et des critères prédéfinis : temps d'identification d'incident, exactitude du triage, taux d'erreurs, charge perçue ou qualité des décisions.

**D.3. Le protocole de corrélation repose principalement sur des incidents synthétiques**

La section 4.12, page 105, utilise un corpus synthétique initial, puis des corpus générés sur vingt graines.

L'expérience montre que les règles de corrélation peuvent être vérifiées dans des situations contrôlées. Elle révèle aussi que, lorsque les incidents traversent plusieurs catégories d'événements, la variante simplifiée dépasse le corrélateur proposé en F1 : 0,7268 contre 0,6496.

Le problème ne réside pas dans l'utilisation de données synthétiques en elle-même. Il réside dans l'absence de validation externe de la corrélation sur des incidents multi-étapes authentifiés.

#### E. Qualité formelle et traçabilité

**E.1. Des erreurs documentaires vérifiables**

| Localisation | Constat | Conséquence |
|---|---|---|
| Page 101, section 4.10 | Présence de « 0,031027s̃ » et « 0,105420s̃ » | Défaut de composition mathématique ou typographique |
| Page 135, annexe A.8 | Le rejet open-set est encore décrit comme portant sur trois inconnus | Formulation incomplète face à l'évaluation étendue à 20 inconnus, page 96 |
| Page 127, tableau 7.1 | H4 sans budget préenregistré | Incohérence avec l'annonce générale de la page 7 |
| Page 104, section 4.11.3 | « délai imparti, Il remporte » | Défaut ponctuel de ponctuation |

Le cas de l'annexe A.8 ne signifie pas que le résultat de 20 inconnus est inventé : la section 4.7 distingue bien la calibration initiale et l'extension. Il s'agit d'un défaut de mise à jour et de cohérence documentaire.

**E.2. Reproductibilité annoncée, mais non vérifiable à partir du seul PDF**

Le chapitre 7 et l'annexe A recensent des identifiants de campagnes, des paramètres et des artefacts expérimentaux.

Il existe donc une documentation de traçabilité. Toutefois, je ne dispose pas du dépôt Git, de la matrice de preuves exécutable ni des fichiers CSV et JSON correspondants.

Je ne peux pas certifier que les résultats ont été reproduits indépendamment, ni qu'un tiers peut reconstruire intégralement l'environnement à partir du manuscrit seul.

La distinction à maintenir est :
- Traçabilité décrite : présente.
- Reproductibilité indépendante : non vérifiée dans cet examen.

**E.3. Plagiat et usage de l'intelligence artificielle**

Le mémoire contient une déclaration explicite d'utilisation d'outils d'IA, pages iv–v.

L'utilisation déclarée d'une IA pour la rédaction, le code ou la mise en forme ne constitue pas, à elle seule, une preuve de fraude ou de plagiat.

Aucun plagiat ne peut être établi sans comparaison avec les sources originales et vérification des emprunts textuels, des références et des artefacts logiciels.

Il serait académiquement injustifié de prononcer une accusation de plagiat sur la seule base de ce PDF.

#### F. Originalité et apport scientifique

La principale contribution revendiquée, page 127, réside dans une intégration architecturale et méthodologique.

Cette contribution doit être évaluée à son niveau réel.

Le manuscrit ne démontre pas l'invention d'un nouvel algorithme de détection, d'une nouvelle théorie multi-agent ou d'une méthode universellement meilleure de traitement des journaux.

Il présente plutôt un assemblage logiciel instrumenté, accompagné de comparaisons de modèles et de protocoles.

La partie qui possède le plus de valeur scientifique identifiable est l'analyse critique de la validité des benchmarks : chute de performance en holdout, dépendance à Dst Port, effet des templates et des sévérités, et séparation entre performance prédictive et fonctionnement architectural.

Mais ces observations doivent être positionnées par rapport aux travaux existants. Leur redécouverte expérimentale ne suffit pas à établir leur originalité conceptuelle.

Verdict sur l'apport : contribution d'intégration et d'évaluation méthodologique ; originalité scientifique limitée et insuffisamment différenciée de l'état de l'art.

### 3. Les dix faiblesses majeures, hiérarchisées

| Rang | Faiblesse | Gravité |
|---|---|---|
| 1 | H3 et H5 non tranchées faute de comparateurs ou de campagnes décisives | Critique |
| 2 | Absence de bénéfice opérationnel quantifié et spécifique à l'architecture multi-agents | Critique |
| 3 | H4 évaluée sans critère budgétaire préenregistré malgré sa formulation conjonctive | Critique |
| 4 | Généralisation prédictive très fragile entre scénarios et journées | Élevée |
| 5 | Résultat BGL reproductible par une règle simple de nouveauté de sévérité | Élevée |
| 6 | Distribution de la décision testée sans distribution complète du calcul prédictif | Élevée |
| 7 | Originalité architecturale insuffisamment comparée aux plateformes intégrées existantes | Élevée |
| 8 | Validation auprès d'analystes et sur des incidents opérationnels réels absente | Élevée |
| 9 | Hétérogénéité de normalisation non accompagnée d'une preuve complète de conservation des champs utiles | Importante |
| 10 | Reproductibilité indépendante non certifiable sans les artefacts et le dépôt | Importante |

### 4. Points de non-recevabilité

Il faut distinguer les défauts qui justifient une correction obligatoire des motifs qui empêcheraient formellement la délivrance du diplôme. Ces derniers dépendent des règles de la Faculté, qui ne sont pas fournies.

En tant que membre d'un jury exigeant, je formulerais les objections suivantes avant d'accepter une validation scientifique sans réserves.

- **Hypothèses non démontrées.** H3 et H5 ne peuvent pas être déclarées validées. Il faut soit exécuter les expériences manquantes, soit réduire explicitement les contributions revendiquées.
- **Critère de décision incomplet.** Le statut de H4 ne peut pas être renforcé sans preuve du respect des contraintes de ressources prévues initialement.
- **Contribution scientifique insuffisamment isolée.** Il faut distinguer ce qui provient des algorithmes existants, des mécanismes classiques de persistance et des choix véritablement propres à Ariel Logminer.
- **Audit indépendant des résultats non réalisé.** La transmission du dépôt, des artefacts et des instructions de reproduction est nécessaire pour une certification expérimentale complète. Leur absence de cet examen ne prouve pas leur absence du projet.

Décision de recevabilité : je ne recommanderais pas une acceptation sans modifications. Je recommanderais une validation conditionnelle à une révision majeure des revendications scientifiques et à la vérification des preuves, plutôt qu'un rejet définitif fondé uniquement sur le manuscrit.

---

## Retour Lecteur 2

### 1. Synthèse globale

Ce mémoire est un travail d'intégration logicielle. L'auteur reconnaît lui-même qu'il n'apporte aucun algorithme nouveau ; or l'apport architectural qu'il revendique à la place n'est pas démontré non plus. Plusieurs résultats mis en avant ne font pas mieux qu'une règle triviale :

- BGL : le détecteur se réduit à une règle sur la sévérité ;
- CSE-CIC-IDS2018 : un simple seuil sur le port de destination donne le même score ;
- CICIDS2017 en split temporel : les modèles supervisés font moins bien qu'une prédiction « tout positif ».

La couche multi-agents est environ 60 à 80 fois plus lente que le monolithe. Son seul bénéfice mesuré, l'idempotence, se transpose tel quel aux architectures de référence. Sa « distribution » repose sur une seconde machine qui traite 1,23 % des tâches. La transparence sur les limites est réelle, mais elle sert à énumérer des non-résultats plutôt qu'à les corriger. Enfin, le résumé et la conclusion contredisent le corps du texte sur des points factuels, et l'essentiel des campagnes décisives a été exécuté par un agent d'IA la veille de la compilation du PDF.

### 2. Critique détaillée par axe

#### 2.1 Problématisation

**La question centrale est fourre-tout (p. 5).** Elle cumule plus de dix attributs : autonome, distribué, modulaire, exploitable, détecter, prioriser, hétérogènes, traitements périodiques, micro-lots, agents multitâches. Une question qui embrasse tout ne peut pas être tranchée.

**La priorisation n'est jamais évaluée.** Elle figure dans la question centrale et dans H5 (« au moins une métrique de priorisation fixée à l'avance »). Aucune métrique de priorisation n'est définie ni mesurée dans tout le document. Les traitements « périodiques » et « par micro-lots » ne sont pas évalués non plus (§2.23.2 seulement).

**Les questions de recherche sont des questions de conception, pas de recherche.** QR1 à QR5 commencent par « Comment construire / organiser / présenter… » : elles appellent une description, pas une réfutation. QR6 (« Comment évaluer le prototype par métriques, captures… ») est une question méthodologique sur le mémoire lui-même. La déclarer « la mieux couverte » (p. 126) relève de l'autosatisfaction circulaire.

**Les hypothèses sont tautologiques ou réfutées sans être déclarées comme telles.**
- H2 (p. 6) affirme qu'un magasin d'idempotence évite les doublons « contrairement à la même exécution sans idempotence ». C'est vrai par construction, et l'expérience ne fait que vérifier la définition du mécanisme.
- H1 est vérifiée sur un corpus de formats choisi par l'auteur, avec 1 000 unités par source et une « fixture » Apache d'une seule ligne. Elle est quasiment infalsifiable. Pire : les flux réseau remplissent 0 champ standard sur 7 du noyau commun (Fig. 4.13). Les déclarer « conformes au noyau commun » vide la notion de conformité de son sens.
- H5 : l'auteur fixe lui-même le critère « réfutée si aucun gain n'est observé » (p. 7). Il n'observe aucun gain (p. 98, 116), mais classe H5 « NON TRANCHÉE » (tableau 7.1). C'est un contournement du critère qu'il a lui-même fixé.
- H3 : le comparateur « sans routage » n'a jamais été exécuté (tableau 7.1). L'hypothèse centrale du routage n'a donc tout simplement pas été testée.

**Le titre annoncé ne correspond pas au titre réel.** Le texte affirme : « Le titre du mémoire emploie les termes autonome, distribuée et agents intelligents multitâches » (p. 4). Aucun de ces termes ne figure dans le titre actuel. C'est le vestige d'une version antérieure.

#### 2.2 Cadre théorique

**Le chapitre 1 (p. 14–41) est un manuel, pas un état de l'art critique.** Ses définitions sont génériques (Random Forest, régression logistique, LOF, One-Class SVM), sans lien avec les choix du travail. On n'y trouve aucun débat contradictoire entre auteurs.

**La lacune revendiquée n'est pas établie.** Le §1.23.1 affirme un « espace entre le prototype algorithmique et la plateforme opérationnelle ». Or des cadres intégrés d'analyse de logs pour la recherche existent : la boîte à outils Loglizer associée à He et al. [18], cité pour un tout autre usage, ou LogAI (Salesforce, 2023), entre autres. Le mémoire ne les mentionne ni ne les discute. La lacune est affirmée, pas démontrée.

**Le choix d'une architecture multi-agents n'est pas justifié face à son vrai concurrent.** Le seul ancrage théorique est une phrase sur Wooldridge et le Contract Net de 1980. Le vrai concurrent, c'est une file de tâches avec table de routage statique (Celery, groupes de consommateurs Kafka/Redis, moteurs de workflow). Il n'est jamais discuté. L'architecture B, qui en est l'équivalent, est 5 à 15 fois plus rapide que les agents (Fig. 4.14).

**Des pans entiers de littérature manquent :**
- schémas de normalisation (ECS, OCSF) : rien, alors que QR1 porte précisément sur ce point ;
- corrélation d'alertes (travaux classiques de Cuppens et Miège, de Valeur et al.) : rien ;
- sémantique de livraison et idempotence dans les systèmes distribués : rien ;
- gouvernance et MLOps : rien ;
- critiques de CSE-CIC-IDS2018 : rien, alors que les critiques de CICIDS2017 [11, 24] sont citées.

**La bibliographie est mince.** 39 références pour 166 pages, dont une part notable de standards (FIPA ×3, RFC, NIST) et de références anciennes (1980, 1987, 1998, 2000).

**Le chapitre 6 (Discussion) ne cite aucune référence.** Le plan (p. 13) promettait de mettre les résultats « en relation avec la littérature ». La promesse n'est pas tenue.

#### 2.3 Méthodologie

**CICIDS2017**
- La version du jeu utilisée (originale ou corrigée selon Engelen et al. [11]) n'est jamais précisée, alors que l'auteur cite les travaux qui documentent ses erreurs d'étiquetage.
- Le test moyen ne compte que 6 435,6 lignes (p. 82) pour un corpus de plusieurs millions de flux. Ce sous-échantillonnage massif n'est pas justifié.
- La comparaison des cinq modèles se fait « au seuil retenu », jamais défini ni calibré. HistGradientBoosting obtient un F1 de 0,0036 mais une PR-AUC de 0,569 (p. 83). Le classement repose donc sur un artefact de seuil, pas sur la capacité des modèles.

**HDFS**
- Seuls 6 000 des 345 036 blocs d'entraînement (1,7 %) servent à construire l'état du parseur et les histogrammes. Le reste de l'entraînement n'est pas utilisé, sans justification.
- Les cinq graines produisent une matrice de confusion strictement identique (p. 85). Le « cinq graines » n'apporte donc aucune information de variabilité.
- Aucune baseline forte n'est évaluée au niveau bloc sous le même protocole. Les seuls comparateurs internes sont des Isolation Forest au niveau événement (p. 90), c'est-à-dire sur une unité que l'auteur juge lui-même inadéquate.

**BGL : le résultat principal n'est pas une détection**
- Les 49 999 événements d'entraînement sont tous de sévérité INFO. Le seuil retenu vaut ln 49 999, le score maximal possible.
- La décision « coïncide exactement avec la règle sévérité absente de l'entraînement normal » (p. 87). Le F1 de 0,913698, mis en avant dans le résumé et la conclusion, est donc celui d'une règle d'une ligne.
- Le protocole G, qui sauve le résultat (0,941927), est conçu en connaissant la position des familles d'anomalies : « sa conception tient compte de la position des familles d'anomalies » (p. 89). C'est une fuite d'information dans la conception du protocole.
- Le tableau 4.4 présente huit protocoles avec des F1 allant de 0,599 à 0,942. Explorer autant de variantes sans plan préalable invalide toute lecture confirmatoire.

**CSE-CIC-IDS2018**
- Seules deux journées sont utilisées, au motif qu'elles étaient « les deux seules disponibles localement » (p. 90). C'est un échantillon de commodité alors que le jeu en compte dix.
- Les deux fichiers comptent « exactement 1 048 575 lignes » (p. 96). C'est précisément la limite de lignes d'Excel (2²⁰ − 1 lignes de données), signe classique de troncature. L'auteur se contente de noter que cela « appelle une vérification ». Toute l'analyse repose donc sur des données dont l'intégrité n'est pas établie.

**Préenregistrement contredit**
- L'introduction affirme : « Les seuils numériques et les budgets sont fixés dans le protocole avant l'exécution » (p. 7).
- Le tableau 7.1 admet que « le budget local n'est pas un critère de décision préenregistré ».
- Aucun document de préenregistrement n'est fourni.

**Origine des campagnes décisives**

La déclaration d'IA (p. iv) indique que Claude Code a exécuté des « campagnes complémentaires » en novembre 2026. Les artefacts portent des noms agent2_… à agent6_…, horodatés au 4 novembre 2026. Le PDF a été généré le 5 novembre 2026 à 11 h 10. Relèvent de ces exécutions :
- le résultat HDFS principal (test complet) ;
- toute l'analyse BGL ;
- l'audit du raccourci CSE-CIC ;
- le routeur open-set étendu ;
- la panne appariée, c'est-à-dire la preuve de H2 ;
- la saturation ;
- la détection HDFS distribuée ;
- les Isolation Forest de contrôle ;
- la corrélation étendue.

La transparence de la déclaration doit être relevée. Mais elle pose deux problèmes de fond :
- La propriété intellectuelle du cœur expérimental. Le jury devra vérifier en soutenance que l'auteur maîtrise chacun de ces protocoles.
- L'impossibilité d'un protocole fixé a priori. Des protocoles conçus la veille, après lecture des résultats précédents, ne peuvent pas l'avoir été avant l'exécution.

#### 2.4 Argumentation

**Les baselines triviales ne sont appliquées que là où elles arrangent.** Sur le test temporel CICIDS2017, l'auteur note qu'une prédiction systématiquement positive obtient un F1 de 0,666667 (p. 84). Il s'en sert pour disqualifier l'Isolation Forest. Il omet de constater que la régression logistique (0,556615) et le Random Forest (0,437429), sur le même test, font moins bien que cette baseline triviale. Sous split temporel, aucun modèle supervisé n'apprend donc quoi que ce soit d'exploitable. H4 est réfutée sur ce jeu, et le mémoire la déclare « partiellement soutenue ».

**H4 ne tient sur aucun jeu.**
- BGL : Histogram égale une règle de sévérité.
- CSE-CIC : la régression logistique égale une règle fixe « port < 1024 » (p. 92).
- CICIDS temporel : modèles inférieurs à la baseline triviale.
- HDFS : aucune baseline déclarée au même niveau.

**La valeur architecturale des agents est revendiquée sans preuve.** Le résumé l'énumère : « autonomie locale, négociation, séparation des responsabilités, réattribution, idempotence et auditabilité » (p. vii). Chaque élément est démenti ou non spécifique aux agents :
- l'idempotence se transpose à A et B (tableau 4.7, de l'aveu même de l'auteur) ;
- la réattribution est une fonction du broker (pending/ACK) ;
- la séparation des responsabilités relève de la conception modulaire, pas des agents ;
- l'auditabilité n'est jamais mesurée.

**« L'intelligence » des agents est fictive.** Selon le §3.5.1 (p. 73–74) :
- M = 1 pour toute offre, et A = L : deux des six composantes sont constantes ou redondantes ;
- dans les campagnes Redis, le seuil minimum_utility est inactif, donc aucun refus pour faible utilité n'est possible ;
- la répartition 451/1 349 de l'endurance « découle des profils de capacité configurés » (p. 103) : une table de correspondance statique donnerait exactement le même résultat ;
- en HDFS distribué, les deux agents proposent la même utilité (0,845) et 100 % des tâches vont à Debian par tri alphabétique (p. 105).

Aucune expérience ne compare le Contract Net à une affectation statique. La négociation ne démontre donc rien.

**La « distribution » n'est pas démontrée.** En saturation, l'agent Ubuntu traite 1,23 % des tâches (p. 104). L'auteur conclut lui-même que « la seconde machine n'augmente donc pas la capacité observée ». La campagne d'endurance tourne à 0,5 tâche/s, soit 16 à 32 fois sous le point de saturation. Parler de « preuve directe de l'endurance » (p. 103) pour une heure à cette charge est abusif.

**Le coût des agents est euphémisé.** Le texte dit « pas plus rapides » (p. vii). La figure 4.14 montre environ 80 000 tâches/s pour le monolithe contre environ 1 000 tâches/s pour les agents C et D, soit près de deux ordres de grandeur. Aucun chiffre de débit, aucune barre d'erreur et aucun test statistique n'accompagnent ce benchmark, malgré dix répétitions.

**La corrélation est évaluée en circuit fermé.** Le générateur synthétique est écrit par l'auteur, avec des « clés stables » qui reprennent les sept clés du corrélateur. Le résumé ne rapporte que le petit corpus favorable (16 anomalies, F1 0,8125). Sur le corpus étendu, le rappel tombe à 0,597. Dès que 30 % des incidents sont multi-étapes, une variante simplifiée « hôte + fenêtre » bat le corrélateur proposé sur les 20 graines (0,7268 contre 0,6496, p. 106). Le design proposé est dominé par une baseline plus simple.

**La contradiction n'est pas résolue entre les chapitres 4 et 5.** Le §4.6.4 établit un raccourci par le port de destination, propre à la journée de test. Le §5.2 affirme que les contrôles « ne mettent pas en évidence de fuite triviale ».

**L'ablation du routage est invoquée deux fois sans aucun résultat** (p. 97 et 115) : ni tableau, ni chiffre, ni artefact dans la matrice A.2.

**Un comportement est affirmé sur la base de données que l'auteur a lui-même écartées.** Le §5.7 affirme que, dans la campagne multi-VM, les agents « proposent ou refusent des tâches ». Or les compteurs de messages de cette campagne sont déclarés « non conclusifs » (tableau A.4) : aucun nombre de refus n'y est établi.

#### 2.5 Forme

**Le résumé contredit le corps du texte. C'est une faute grave.**
- Le résumé (p. vii), l'abstract et le Bokuse décrivent une campagne multi-VM `multivm_cnp_20260909T202632Z_37592` : 60/60 tâches, 30/30, 15 refus. Cette campagne n'apparaît nulle part dans le corps. Le chapitre 4 et l'annexe A.4 présentent `cnp_endurance_multivm_20260918T130822Z` (1 800 tâches, 451/1 349, refus non comptés).
- Le résumé affirme : « Les cinq hypothèses de recherche sont partiellement soutenues » (p. viii). Le tableau 7.1 en classe deux « NON TRANCHÉE ».

D'autres incohérences internes s'y ajoutent :
- F1 macro du Random Forest en holdout : 0,157744 dans le résumé, la conclusion et le tableau A.2, contre 0,157827 dans le tableau 4.2, présentés comme la même grandeur.
- Le tableau A.3, intitulé « Configuration HDFS vérifiée », décrit l'ancien protocole sur échantillon (6 000/2 000/2 000 blocs, TP 29, FP 7). Il ne correspond pas au résultat principal sur 115 013 blocs.
- La réponse à QR3 dans la conclusion (p. 126) reprend les chiffres de calibration (28 connus, 3 inconnus) et non ceux du test étendu.
- Le §1.8.2 renvoie à la « section 6.2 » pour la chute du F1 CICIDS. Ce résultat se trouve au §4.2.

**Fausse précision et surcharge :**
- seuils à 14 décimales (10,81975828421028, p. 86) ;
- un p99 de 836,72528 ms ;
- des F1 à six décimales sur des tests de quelques milliers de lignes ;
- des run_id dans un résumé ;
- un résumé de trois pages saturé de chiffres, reproduit trois fois.

**Redondance :** les mêmes chiffres (0,995142 / 0,157744 / 0,868373 / 0,913698 / 20/20 / 3/46 / 7 001) sont répétés aux chapitres 4, 5, 6, 7, dans la conclusion, les annexes et les trois résumés. La formule « ne constitue pas une validation SOC / industrielle », ou ses variantes, revient des dizaines de fois. Le §7.7 sur la compilation pdfLaTeX n'a rien à faire dans un mémoire scientifique.

**Coquilles :** « 0,031027s̃ » et « 0,105420s̃ » (p. 101) ; « …imparti, Il remporte » (p. 104) ; références bibliographiques au format BibTeX anglais (« and », « 2 edition ») dans un document francophone.

#### 2.6 Apport scientifique

L'auteur l'écrit lui-même : « La contribution se situe donc dans l'intégration et l'évaluation de mécanismes déjà connus » (p. 117). Or cette intégration n'est pas évaluée contre des alternatives d'intégration : ni file de tâches avec affectation statique, ni outil existant. Le seul apport méthodologique revendiqué, à savoir qu'un score dépend du protocole de séparation, est un constat déjà établi dans la littérature que le mémoire cite lui-même (Sommer et Paxson [32], Arp et al. [1], Le et Zhang [25], Engelen et al. [11]). C'est une redite empirique, pas une contribution.

### 3. Faiblesses majeures, par ordre de gravité

1. Le résumé contredit le corps du texte : campagne 60/60 inexistante dans le corps, et statut des hypothèses faux.
2. Les résultats phares ne battent pas une règle triviale : BGL = règle de sévérité, CSE-CIC = règle sur le port, CICIDS temporel en dessous du « tout positif ». H4 est réfutée et déclarée « partiellement soutenue ».
3. L'architecture multi-agents n'a aucun bénéfice démontré et coûte environ deux ordres de grandeur en débit. La fonction d'utilité est dégénérée (M constante, A = L, refus inactif) et la négociation n'est jamais comparée à une affectation statique.
4. La distribution n'est pas démontrée : 1,23 % de charge sur la seconde VM, 0 % en HDFS distribué.
5. Les hypothèses sont mal construites : H2 tautologique, H1 quasi infalsifiable, H3 non testée, H5 réfutée selon son propre critère mais classée « non tranchée ».
6. Le cœur expérimental a été exécuté par un agent d'IA la veille de la compilation, ce qui pose la question de la maîtrise et rend impossible la revendication d'un protocole fixé a priori.
7. La question centrale n'est pas traitée : priorisation et micro-lots, annoncés dans la question centrale, ne sont jamais mesurés.
8. L'intégrité des données CSE-CIC n'est pas établie : troncature probable à la limite Excel, non vérifiée ; échantillon de commodité de deux journées.
9. La corrélation est évaluée en circuit fermé sur un générateur écrit par l'auteur, et le design proposé est dominé par une variante plus simple sur les incidents multi-étapes.
10. L'état de l'art est un manuel : aucune discussion des cadres intégrés existants ni des schémas de normalisation, et une discussion (chapitre 6) sans aucune référence.

### 4. Points de non-recevabilité en l'état

- **A.** Le résumé, l'abstract et le Bokuse décrivent une expérience absente du corps et un statut des hypothèses contraire au tableau 7.1. Un résumé factuellement faux n'est pas recevable.
- **B.** L'introduction (p. 7) et le tableau 7.1 se contredisent directement sur le caractère préenregistré des seuils et des budgets.
- **C.** Le statut de H5 viole le critère de réfutation fixé par l'auteur lui-même ; celui de H4 ignore les baselines triviales que le mémoire calcule pourtant.
- **D.** La part réelle de l'auteur doit être établie pour les campagnes agent2 à agent6 du 4 novembre 2026, dont dépendent H2 et le résultat HDFS principal. Faute de quoi, le jury ne peut pas attribuer ces résultats au candidat.
- **E.** Le tableau A.3, présenté comme « configuration vérifiée », décrit un autre protocole que le résultat qu'il est censé documenter.

---

## Retour Lecteur 3

### Synthèse globale

Ce mémoire est un paradoxe académique : il fait preuve d'une honnêteté intellectuelle et d'une rigueur protocolaire rares, mais il les met au service d'une contribution scientifique quasi nulle. L'auteur passe 130 pages à démontrer méthodiquement que son architecture multi-agents n'apporte aucun gain prédictif, qu'elle est plus lente qu'une approche monolithique, et que les jeux de données sur lesquels elle est évaluée sont intrinsèquement biaisés ou triviaux. Ce travail s'apparente moins à une thèse de recherche qu'à un rapport d'ingénierie défensif, dont la principale « découverte » est la confirmation de biais déjà documentés dans la littérature. En l'état, il valide une intégration logicielle, mais échoue à produire une connaissance scientifique nouvelle.

### Critique détaillée par axe

**1. Problématisation**

La question centrale est fondamentalement viciée car elle relève du développement logiciel, non de la recherche scientifique.

Preuve : « Comment concevoir un prototype autonome, distribué au sens logiciel, modulaire et exploitable... ? » (p. 5).

Il s'agit d'un cahier des charges, pas d'une question de recherche. Les hypothèses (H1 à H5) sont pour la plupart des vérifications fonctionnelles (ex : H2 sur l'idempotence) ou des constatations d'échec (H4 sur les modèles légers), non des propositions théoriques falsifiables visant à faire avancer la connaissance en cybersécurité ou en systèmes multi-agents.

**2. Cadre théorique**

L'état de l'art est un catalogue descriptif et consensuel (Drain, Isolation Forest, DeepLog, Contract Net). Il n'y a aucune tension théorique, aucune critique profonde des paradigmes existants, si ce n'est pour justifier le choix de la simplicité.

Preuve : La définition de l'« agent intelligent » est vidée de sa substance : il s'agit d'une entité logicielle avec une fonction d'utilité linéaire aux poids fixés arbitrairement (p. 4-5, p. 73). Qualifier cela de « système multi-agents intelligent » est un abus de langage ; c'est une file d'attente de tâches (Redis) avec un routeur à règles.

**3. Méthodologie**

C'est l'axe le plus rigoureux, mais il révèle la faillite du sujet. L'auteur applique un protocole strict (séparation temporelle, gel du parseur) sur des jeux de données dont il sait pertinemment qu'ils sont inadéquats pour valider une architecture hétérogène.

Preuve : L'évaluation de la détection d'intrusion réseau (CICIDS2017) est totalement découplée de l'analyse des journaux système (HDFS/BGL). Le système ne fait jamais d'analyse conjointe ou corrélée entre un flux réseau et un log système pour un même incident. Il traite des silos en parallèle. De plus, valider le « multi-format » avec une « fixture synthétique d'une seule ligne » pour Apache (p. 97) est une faiblesse méthodologique inacceptable.

**4. Argumentation et Résultats**

L'argumentation s'effondre sous le poids de ses propres résultats. L'auteur démontre que son architecture complexe est inutile pour résoudre le problème posé, mais tente de sauver les meubles en invoquant la « valeur architecturale » (modularité, auditabilité).

Preuve 1 : Sur CSE-CIC-IDS2018, une règle heuristique unique (Dst Port < 1024) atteint un F1 de 0,999720 (p. 92). Construire un pipeline multi-agents avec routage, mémoire et corrélation pour résoudre un problème qu'une condition if règle parfaitement est une aberration méthodologique que l'auteur constate sans oser condamner la pertinence même de l'expérience.

Preuve 2 : Sur BGL, l'auteur admet que la performance (F1 0,913) est presque entièrement due à la détection de la « nouveauté de sévérité » et non à une modélisation des journaux, et qu'aucune anomalie n'est détectée sur les templates connus (p. 87-88, p. 136).

**5. Forme et Rédaction**

Le document est bien structuré, mais le style est lourdement marqué par une rédaction assistée par IA (comme l'avoue la déclaration p. iv), se traduisant par un usage excessif de formules défensives et de précautions oratoires qui alourdissent le propos sans apporter de nuance réelle.

Preuve : La répétition obsessive de formules comme « Il serait donc incorrect d'affirmer... » (p. 52), « Cette qualification décrit ce qui fonctionne dans le laboratoire; elle ne constitue pas une certification... » (p. 11). Le texte passe plus de temps à se justifier et à limiter sa propre portée qu'à affirmer des résultats.

**6. Apport scientifique**

L'apport est nul. L'auteur le reconnaît lui-même : « Ariel Logminer n'introduit pas un nouvel algorithme d'apprentissage automatique » (p. 10). L'assemblage de bibliothèques existantes (Scikit-learn, Drain3, Redis) dans un pipeline, même bien documenté, est un travail d'ingénierie logicielle, pas une contribution scientifique. Confirmer que CICIDS2017 fuit (data leakage) n'est pas une découverte (l'auteur cite Engelen et al., 2021 et Lanvin et al., 2023) ; c'est une vérification de routine.

### Liste des faiblesses majeures (hiérarchisées)

1. **Inadéquation fondamentale entre l'ambition et l'évaluation :** Le mémoire prétend traiter des « journaux hétérogènes », mais n'évalue jamais la corrélation ou le traitement conjoint de sources hétérogènes (ex : log système + flux réseau). Les évaluations sont cloisonnées par dataset.
2. **Trivialité du problème résolu sur CSE-CIC-IDS2018 :** Consacrer une architecture complexe à un jeu de données où une seule variable binaire (Dst Port) résout 99,9 % du problème de classification invalide rétrospectivement toute la chaîne de valeur du prototype pour ce cas d'usage.
3. **Fausse promesse du « Multi-Agent » :** Le système est un orchestrateur centralisé avec des workers passifs. La « négociation » Contract Net est une simulation déterministe basée sur une fonction d'utilité à poids fixes, sans apprentissage ni émergence. C'est du distributed computing déguisé en multi-agent system.
4. **Validation « multi-format » pathétique :** Inclure une fixture Apache d'une seule ligne synthétique (p. 97) pour valider la robustesse du parsing multi-format est une tromperie méthodologique. Cela ne valide rien d'autre que le fait que le code ne plante pas sur une chaîne de caractères.
5. **Le piège du « résultat négatif » :** Si le but du mémoire était de prouver que les modèles ne généralisent pas et que les agents ajoutent de la latence, l'objectif est atteint. Mais une thèse doit proposer une piste de solution à ce constat, pas seulement l'acter et s'arrêter là.

### Points de non-recevabilité

- **L'absence de véritable scénario hétérogène :** Un mémoire sur l'analyse de journaux hétérogènes doit démontrer un bénéfice à l'hétérogénéité (ex : corréler un log d'authentification Linux avec un flux réseau CICIDS pour détecter une attaque spécifique). Ici, les sources sont traitées en silos indépendants. Le terme « hétérogène » est utilisé comme un mot-clé marketing, pas comme une propriété évaluée.
- **L'évaluation sur un artefact de données :** Bâtir une partie significative de l'évaluation (chapitre 4.6) sur CSE-CIC-IDS2018, alors que l'auteur a lui-même prouvé que le modèle apprend un artefact de collecte (le port de destination) et non une logique d'attaque, rend cette section scientifiquement invalide. On n'évalue pas un système de détection d'anomalies sur un jeu de données où la vérité terrain est corrélée à un artefact technique trivial.
