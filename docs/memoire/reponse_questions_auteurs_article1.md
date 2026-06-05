# Reponse aux questions des auteurs/reviewers - Article 1

## 1. Choix des poids du routeur et sensibilite

Nous avons ajoute une mini-analyse de sensibilite locale sur les cinq sources distinctes de la campagne `SupervisorAgent`. Apres parsing/normalisation, les constantes additives du routeur ont ete perturbees de +/-10 %. Les familles selectionnees restent stables: CEF/LEEF, CloudTrail, Apache et l'entree corrompue restent en `fallback`, tandis que Linux/auth reste route vers `linux`.

Nous n'avons pas retenu une normalisation probabiliste dans cette premiere version parce que les scores ne sont pas des probabilites apprises. Ce sont des preuves additives explicables et heterogenes: colonnes, marqueurs, subtype, chemin, format inconnu/corrompu. Une softmax ou une normalisation MinMax rendrait les nombres plus comparables en apparence, mais pourrait amplifier du bruit lorsque toutes les familles ont peu de preuves. Le choix actuel privilegie donc des seuils explicites, des raisons auditables et un fallback conservateur. Une calibration probabiliste reste une piste future.

Formulation courte possible:

> We added a local +/-10% sensitivity replay on the five distinct SupervisorAgent sources. The selected families remained unchanged. We did not use probabilistic normalization because the routing constants are auditable evidence weights rather than calibrated probabilities; normalizing them could overstate weak evidence when all family scores are low. Calibrated routing is therefore left as future work.

## 2. Evaluation du routeur

Nous pouvons fournir une petite matrice de confusion du routeur au niveau source, separee des metriques de detection d'intrusion. Sur les cinq sources distinctes evaluees par le `SupervisorAgent`, le protocole attendu est:

| Route attendue | Pred. fallback | Pred. linux |
| --- | ---: | ---: |
| fallback | 4 | 0 |
| linux | 0 | 1 |

Interpretation: precision de routage distinct-source = 5/5. Sur les 30 cycles repetes de la campagne, les routes sont egalement stables: 30/30. Il faut toutefois preciser que cette matrice evalue le choix de famille/fallback, pas la detection d'attaque.

## 3. Persistance des modeles et reproductibilite Docker

Nous devons repondre positivement, mais prudemment. Les avertissements de compatibilite `scikit-learn` montrent une menace de reproductibilite. La bonne reponse est de dire que les scores actuels restent des mesures locales du prototype, et que la diffusion reproductible devra republisher les artefacts entraines dans un environnement epingle.

Mise a jour a signaler explicitement: le depot GitHub mentionne dans l'article contient maintenant `Dockerfile`, `requirements-container.txt`, `requirements.txt`, `requirements-ai.txt`, `docker-compose.redis.yml` et `docker-compose.mqtt.yml`. Les grands datasets, exports locaux et binaires de modeles peuvent rester externes selon les contraintes de taille, licence ou confidentialite.

Formulation courte possible:

> Yes. The GitHub repository now includes the Dockerfile, pinned container requirements and Redis/MQTT Compose descriptors. The compatibility warnings are treated as a model-persistence validity threat: the current scores are local prototype measurements, and exact replication still requires retraining or republishing the model artifacts under the pinned container environment.

Cela reste article 1: reproductibilite experimentale. Ce n'est pas encore une revendication de deploiement scalable, donc cela n'empiete pas sur l'article 2.

## 4. Fenetre de correlation Delta t

Il faut reconnaitre que la fenetre 15-20 min n'a pas encore ete optimisee par une analyse qualite labellisee. Elle est definie comme parametre de politique:

- 15 min par defaut pour la lecture analyste locale;
- 20 min lorsque le fallback domine, afin de regrouper davantage de signaux faibles;
- 30 min possible pour familles sequentielles HDFS/BGL dans le superviseur, mais l'article 1 ne revendique pas une evaluation de qualite sur cette partie.

Formulation courte possible:

> The 15-minute default was chosen as a conservative analyst-triage window for local experiments. The SupervisorAgent can raise it to 20 minutes when fallback routes dominate, and to 30 minutes for sequential system-log families. We did not conduct an analyst-labeled window-size quality study in this article; this is now stated as future work together with incorrect-merge and incident-quality analysis.

## Position generale a tenir

La reponse doit etre: nous avons ajoute ce qui est mesurable maintenant, et nous avons borne ce qui ne l'est pas encore. Ne pas promettre une evaluation SOC, ni une scalabilite multi-machine, ni une correlation validee par analystes dans l'article 1. L'article 1 defend le routeur auditable, la specialisation controlee, le fallback et la reproductibilite experimentale; l'article 2 gardera le stress, la file Redis/MQTT, la resilience et l'exploitation prolongee.
