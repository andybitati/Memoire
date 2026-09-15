# Rapport final — transformation multi-agents d’Ariel Logminer

Date de clôture locale : 2026-09-09  
Run principal retenu : `ma_20260909T160812Z_34016`  
Run Redis inter-processus : `redis_cnp_20260909T162814Z_47940`
Run Redis multi-VM : `multivm_cnp_20260909T202632Z_37592`

## 1. État initial

Le projet disposait de classes nommées agents, de plusieurs handlers par worker, d’une mémoire locale et de Redis Streams. L’allocation Redis restait toutefois celle d’un groupe de consommateurs : le premier worker compatible qui lisait une entrée la réservait. Aucun cycle `CFP → PROPOSE/REFUSE → AWARD/REJECT` ne comparait des offres calculées par plusieurs agents. Le superviseur historique choisissait une source puis exécutait le workflow.

L’analyse antérieure aux changements est conservée dans `docs/MULTI_AGENT_GAP_ANALYSIS.md`.

## 2. Critiques scientifiques visées

Les corrections ont ciblé sept faiblesses : agents assimilables à des workers, autonomie locale insuffisante, influence de la mémoire non isolée, benchmark limité à 60 tâches, panne testée seulement avant traitement, absence de chaîne bout en bout et distribution limitée. La haute disponibilité de Redis et le déploiement industriel ne faisaient pas partie des affirmations autorisées.

## 3. Modifications architecturales

- `ContractNetCoordinator` réalise la négociation locale.
- `RedisContractNetCoordinator` et `RedisContractNetTransport` transportent la négociation entre processus distincts.
- `MultiTaskIntelligentAgent` expose état, capacité, santé, charge, disponibilité des modèles et dépendances.
- `SQLiteIdempotencyStore` et `RedisIdempotencyStore` partagent le même contrat d’idempotence.
- Le superviseur/coordinateur tient le registre, diffuse les appels, classe les offres reçues et audite; il ne calcule pas l’utilité à la place des agents.
- Le workflow centralisé historique reste disponible comme référence B et n’est pas maquillé en protocole autonome.

`AgentMessage` conserve exactement `run_id`, `source`, `target`, `message_type`, `payload`, `status`, `timestamp`. Les identifiants Redis Streams restent dans l’enveloppe du transport; les métadonnées CNP sont placées dans `payload`.

## 4. Définition du nouvel agent

Un agent Logminer est une entité logicielle disposant d’un état, de capacités, d’une politique locale et d’une mémoire. Il peut percevoir une tâche, vérifier s’il peut la traiter, calculer une utilité, proposer ou refuser, accepter une attribution, exécuter l’un de ses handlers et apprendre du résultat.

L’autonomie désigne ici la décision locale d’offre ou de refus, sans affectation impérative systématique par le superviseur. L’intelligence revendiquée est uniquement une adaptation opérationnelle interprétable fondée sur l’état et l’historique. Elle n’est ni cognitive ni générale.

## 5. Protocole de négociation

Les messages implémentés sont `CFP`, `PROPOSE`, `REFUSE`, `AWARD`, `REJECT`, `ACCEPT`, `RESULT`, `FAIL` et `FEEDBACK`. Une négociation nominale avec trois proposants produit dix messages.

La fonction locale est :

```text
U = 0,30 × capacité
  + 0,20 × historique
  + 0,20 × modèle
  + 0,15 × disponibilité
  + 0,10 × charge
  + 0,05 × latence
```

Chaque composante est bornée entre 0 et 1. Les poids sont configurables, mais ni appris ni présentés comme optimaux. Les refus normalisés sont `capability_missing`, `model_missing`, `agent_overloaded`, `agent_unhealthy`, `low_expected_utility` et `dependency_unavailable`.

## 6. Mémoire et adaptation

La fiabilité suit `(s+1)/(s+f+2)`. Le mode OFF maintient la composante historique à 0,5 et n’enregistre pas de nouvel apprentissage. Le mode ON conserve succès, échecs et durées.

L’expérience d’adaptation comprend 120 tâches. Alpha réussit les 60 tâches de la première phase. Après le changement de spécialité, gamma réussit les 60 tâches suivantes. Huit réattributions sont nécessaires au début de la seconde phase; à l’index 67, l’utilité de gamma atteint 0,947776 contre 0,946808 pour alpha et les réattributions cessent.

Cette expérience montre que la mémoire influence la décision dans un scénario contrôlé. Elle ne prouve pas de gain prédictif sur des journaux réels.

## 7. Idempotence et récupération

La clé `idempotency_key` est lue avant tout handler. Après succès, le résultat est rendu durable avant l’ACK. Une reprise trouve soit une réservation active, soit un résultat terminé; dans ce dernier cas, le handler n’est pas rappelé.

Dans le harnais local post-traitement/pré-ACK :

| Mesure | Valeur |
|---|---:|
| Effets persistants | 1 |
| Effets dupliqués | 0 |
| Tâches récupérées | 1 |
| Latence de reprise | 0,004405 s |
| Pending final | 0 |
| Lag final | 0 |

Une seconde vérification via Redis attribue d’abord l’effet à `redis-alpha`, puis rejoue la même clé sur `redis-beta`. Les deux agents sont des processus distincts; le compteur Redis reste à 1 et le résultat de beta porte `_idempotency_replayed=true`.

Le harnais pending local valide le point de panne demandé. Le replay Redis multi-VM confirme l'unicité de l'effet entre Debian et Ubuntu, mais il ne constitue pas encore un test `XPENDING/XAUTOCLAIM` post-traitement avec arrêt forcé d'un processus invité.

## 8. Protocole expérimental

La matrice principale compare : A monolithe, B trois workers centralisés, C trois agents autonomes mémoire OFF et D trois agents autonomes mémoire ON. Les charges 100, 500, 1 000 et 5 000 sont répétées dix fois. Un couple charge/répétition utilise la même graine et le même workload pour A, B, C et D; l’ordre des architectures tourne entre les répétitions.

L’unité expérimentale est un run architecture × charge × répétition. Les tâches sont des microcharges déterministes de douze entiers. Elles isolent le coût d’allocation, pas la performance d’une inférence de cybersécurité.

La campagne Redis utilise 60 tâches et trois processus Python enregistrés sous les PID 45400, 22104 et 34288. Redis 7.4.9 fournit les boîtes de messages et le registre. Tous les processus s’exécutent sur l’hôte `andy-aaron`.

## 9. Résultats

La matrice principale contient 160 runs et 264 000 traitements, soit 66 000 par architecture. Aucun traitement n’a échoué.

### Charge de 5 000 tâches

| Architecture | Débit moyen (tâches/s) | IC 95 % | p95 moyen (ms) | CPU machine (%) | RSS max. (MiB) | Messages/tâche | Jain |
|---|---:|---:|---:|---:|---:|---:|---:|
| A | 84 727,541 | [79 652,063 ; 89 803,019] | 0,012762 | 13,788524 | 283,966016 | 0 | 1,000000 |
| B | 14 713,635 | [13 059,108 ; 16 368,162] | 0,017880 | 12,674879 | 284,554297 | 0 | 1,000000 |
| C | 1 200,901 | [1 124,049 ; 1 277,753] | 1,352725 | 12,447620 | 288,957031 | 10,000000 | 0,891839 |
| D | 1 178,304 | [1 124,299 ; 1 232,308] | 1,263840 | 12,547859 | 294,118359 | 9,999860 | 0,888885 |

### Mémoire OFF contre ON

| Charge | Débit C | Débit D | Différence appariée D−C | IC 95 % de la différence | p95 C (ms) | p95 D (ms) |
|---:|---:|---:|---:|---:|---:|---:|
| 100 | 1 308,873 | 1 249,106 | −59,767 | [−251,619 ; 132,085] | 8,378 | 7,863 |
| 500 | 1 248,006 | 1 185,601 | −62,405 | [−235,899 ; 111,089] | 6,352 | 4,604 |
| 1 000 | 1 297,767 | 1 185,104 | −112,662 | [−229,290 ; 3,965] | 3,002 | 2,616 |
| 5 000 | 1 200,901 | 1 178,304 | −22,597 | [−114,011 ; 68,816] | 1,353 | 1,264 |

Les 40 runs C émettent 659 998 messages CNP; les 40 runs D, 659 889. Aucun run principal ne demande une nouvelle attribution après `AWARD`.

### Redis inter-processus

| Mesure | Valeur |
|---|---:|
| Tâches réussies | 60/60 |
| Durée | 2,504343 s |
| Débit | 23,958378 tâches/s |
| Latence moyenne | 41,651117 ms |
| Médiane | 38,172500 ms |
| p95 | 59,871450 ms |
| p99 | 85,894290 ms |
| Répartition | alpha 15, beta 15, gamma 30 |

Les résultats proviennent bien des trois PID enregistrés. La répartition suit les utilités de spécialité, pas un round-robin.

### Redis multi-VM

| Mesure | Valeur |
|---|---:|
| VM | Debian et Ubuntu |
| Hôtes invités | `andy`, `andy-VirtualBox` |
| PID invités | 2787, 4305 |
| Tâches réussies | 60/60 |
| Durée | 2,712455 s |
| Débit | 22,120187 tâches/s |
| Latence moyenne | 45,120333 ms |
| p95 | 63,029850 ms |
| Répartition | Debian 30, Ubuntu 30 |
| Refus explicites | 15 |
| Réattributions après échec | 1 |
| Effets dupliqués au replay | 0 |

Le run `multivm_cnp_20260909T202632Z_37592` enregistre deux systèmes Linux, deux noms d'hôte et deux PID invités distincts. Debian refuse `correlate.synthetic` faute de capacité déclarée. Ubuntu échoue une fois de manière contrôlée sur `route.synthetic`; le coordinateur attribue alors la même tâche à Debian, qui la termine. Le replay d'une même clé d'idempotence est exécuté successivement par les deux VM et ne produit qu'un effet persistant.

### Pipeline bout en bout

Le run `e2e-ma_20260909T160812Z_34016` termine 8/8 étapes : découverte, parsing, routage, détection, corrélation, feedback, audit persistant et snapshot de l’API. Les compteurs sont : une entrée XML, une ligne parsée et normalisée, une source routée vers `windows`, une ligne évaluée, zéro anomalie candidate, zéro incident candidat, zéro erreur et zéro fallback. La latence bout en bout est 8,980957 s.

L’absence d’anomalie sur cet échantillon n’est pas transformée en performance prédictive; aucune vérité terrain n’a été fabriquée.

## 10. Analyse statistique

Pour chaque architecture et charge, les agrégats fournissent moyenne, écart-type, médiane, minimum, maximum et IC à 95 % par approximation normale. Pour C contre D, l’appariement porte sur la même charge, répétition et graine. Le fichier `paired_memory_effects.csv` fournit la différence moyenne, son intervalle et `Cohen dz`.

Aucun test de significativité ni p-value n’est rapporté : N=10 et la distribution des différences de ce microbenchmark ne justifient pas une hypothèse paramétrique non vérifiée. Les quatre intervalles de débit D−C contiennent zéro. Le constat reste descriptif : aucun gain systématique de débit dû à la mémoire n’est démontré.

Les latences A/B mesurent le handler; C/D incluent négociation et exécution après prise en charge par un thread. L’attente préalable dans l’exécuteur n’est pas incluse. `cpu_core_equivalent_percent` vaut temps CPU/temps mural × 100; `cpu_machine_normalized_percent` divise cette valeur par les huit processeurs logiques. La RSS est celle du processus Python en MiB, échantillonnée toutes les 5 ms.

## 11. Résultats négatifs

- Le CNP autonome est beaucoup plus lent que A et B sur les microtâches.
- Le protocole consomme environ dix messages par tâche.
- La mémoire ON ne produit aucun gain systématique de débit, latence ou équité.
- L’équité de C/D est plus faible que le round-robin B, car la spécialisation concentre certaines tâches.
- Le premier smoke test a échoué sur un séparateur `auto`; il est conservé.
- Un premier run complet a révélé un biais RSS lié à l’accumulation des latences; il est conservé mais non retenu.
- La première tentative multi-VM a échoué faute d'accès invité; cet échec est conservé séparément avant la campagne corrigée.

## 12. Limites

Le benchmark principal repose sur des microcharges synthétiques locales. Le pipeline réel n’a qu’une entrée et une répétition. La reprise pending post-traitement est un harnais contrôlé; Redis inter-processus et multi-VM valident l'échange et l'idempotence, mais pas `XAUTOCLAIM` à ce point de panne. Redis reste central sur l'hôte Windows et aucune haute disponibilité n'est démontrée.

La campagne multi-VM porte sur deux VM VirtualBox d'un même ordinateur physique, 60 microtâches synthétiques et une seule répétition. Elle démontre la distribution entre systèmes invités dans le laboratoire, pas une généralisation réseau, une tolérance aux partitions, un déploiement cloud ni une portée industrielle. L'échec d'accès initial reste documenté dans `reports/MULTIVM_CNP_ATTEMPT_20260909.md`.

## 13. Impact sur H1–H5

| Hypothèse | Impact des nouveaux résultats | Statut recommandé |
|---|---|---|
| H1 — normalisation hétérogène | Inchangé; le pipeline E2E vérifie seulement une entrée Windows. | PARTIELLEMENT SOUTENUE |
| H2 — agents spécialisés, modularité, traçabilité, robustesse | Renforcée par le CNP, les processus Redis, le coût mesuré, l'idempotence et deux VM réelles. La portée industrielle reste absente. | PARTIELLEMENT SOUTENUE |
| H3 — routage par famille | Inchangé scientifiquement; un routage Windows sans fallback est observé sur N=1. | PARTIELLEMENT SOUTENUE |
| H4 — modèles légers | Inchangé; aucune nouvelle vérité terrain prédictive. | PARTIELLEMENT SOUTENUE |
| H5 — mémoire persistante et adaptation | Renforcée causalement dans le scénario contrôlé; aucun gain général ni adaptation sur logs réels. | PARTIELLEMENT SOUTENUE |

## 14. Impact sur QR1–QR6

| Question | Impact | Niveau recommandé |
|---|---|---|
| QR1 | Aucun changement général; une chaîne Windows est traçable. | RÉPONSE PARTIELLE |
| QR2 | Réponse plus précise : capacités communes, refus, offres, registre, Redis inter-processus et deux VM sont exécutés. | RÉPONSE PARTIELLE, renforcée |
| QR3 | Le pipeline route correctement l’échantillon Windows; aucune généralisation nouvelle. | RÉPONSE PARTIELLE |
| QR4 | Snapshot API produit, sans test utilisateur ni serveur HTTP externe. | RÉPONSE PARTIELLE |
| QR5 | L’influence décisionnelle de la mémoire est isolée; le bénéfice métier reste non démontré. | RÉPONSE PARTIELLE, renforcée |
| QR6 | 160 runs appariés, latences brutes, ressources, IC, effets appariés, logs et hashes renforcent la reproductibilité. | RÉPONSE FORTE |

## 15. Affirmations désormais soutenables

- Logminer implémente un système multi-agents léger à décision locale, exécuté sur deux VM dans le laboratoire.
- Trois processus agents distincts négocient réellement via Redis Streams.
- Deux agents invités sur Debian et Ubuntu proposent, refusent, acceptent et exécutent via Redis; une tâche est réattribuée après un échec contrôlé.
- Les agents peuvent proposer, refuser, accepter, exécuter et recevoir un feedback.
- La mémoire modifie l’utilité et permet une réorientation dans le scénario contrôlé.
- L’idempotence évite un second effet dans les scénarios local et Redis testés.
- L’autonomie a un coût de débit important sur la microcharge.
- Le pipeline local traçable termine 8/8 étapes.

## 16. Affirmations toujours non démontrées

- Haute disponibilité ou absence garantie de perte : **NON DÉMONTRÉ**.
- Gain général apporté par la mémoire : **NON DÉMONTRÉ**.
- Gain prédictif apporté par le routage ou les agents : **NON DÉMONTRÉ** par cette phase.
- Robustesse industrielle, SOC réel ou généralisation externe : **NON DÉMONTRÉ**.
- Optimalité des poids : **NON DÉMONTRÉ**.

## 17. Fichiers modifiés

- `src/logminer/agents/intelligent_runtime.py`
- `src/logminer/agents/contract_net.py`
- `src/logminer/agents/redis_contract_net.py`
- `src/logminer/agents/idempotency.py`
- `src/logminer/agents/__init__.py`
- `scripts/run_true_multi_agent_experiments.py`
- `scripts/logminer_redis_cnp_agent.py`
- `scripts/run_redis_cnp_process_campaign.py`
- `scripts/run_redis_cnp_multivm_campaign.py`
- `scripts/generate_multi_agent_architecture_diagrams.py`
- `tests/test_true_multi_agent.py`
- `docs/MULTI_AGENT_GAP_ANALYSIS.md`
- `docs/TRUE_MULTI_AGENT_ARCHITECTURE.md`

Aucun chapitre du mémoire n’a été réécrit pendant cette phase.

## 18. Artefacts générés

Les fichiers de référence portent `ma_20260909T160812Z_34016` sous `experiments/phase_multi_agent/`. Ils comprennent runs, 264 000 latences, workloads JSONL, agrégats, analyse appariée, adaptation, reprise, E2E, logs, environnement, dix figures et manifeste SHA-256. Le manifeste inclut aussi la configuration, le script et le modèle Windows routé.

Le run Redis `redis_cnp_20260909T162814Z_47940` fournit JSON, CSV par tâche, messages JSONL, logs des trois processus, rapport et manifeste SHA-256. Le run `multivm_cnp_20260909T202632Z_37592` ajoute les résultats bruts, les 60 lignes par tâche, les messages CNP, le rapport multi-VM et son manifeste. Le ledger reste append-only.

Deux diagrammes sont produits dans `docs/architecture/` : `true_multi_agent_architecture.png` et `contract_net_sequence.png`.

## 19. Commandes exactes de reproduction

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/run_true_multi_agent_experiments.py --loads 100,500,1000,5000 --repetitions 10 --workers 3
python scripts/run_redis_cnp_process_campaign.py --tasks 60 --timeout-sec 10
# Dans Debian, avec PYTHONPATH pointant vers le paquet Redis déployé :
python3 scripts/logminer_redis_cnp_agent.py --redis-url redis://192.168.56.1:6379/0 --event-stream logminer:events:multivm_cnp_20260909T202632Z_37592 --namespace logminer:cnp:multivm_cnp_20260909T202632Z_37592 --run-id multivm_cnp_20260909T202632Z_37592 --agent-id debian-alpha --profile alpha --memory on --disable-task-types correlate.synthetic --idle-timeout-sec 120
# Dans Ubuntu, avec le même run et le même Redis :
python3 scripts/logminer_redis_cnp_agent.py --redis-url redis://192.168.56.1:6379/0 --event-stream logminer:events:multivm_cnp_20260909T202632Z_37592 --namespace logminer:cnp:multivm_cnp_20260909T202632Z_37592 --run-id multivm_cnp_20260909T202632Z_37592 --agent-id ubuntu-beta --profile beta --memory on --fail-once-task-types route.synthetic --idle-timeout-sec 120
# Sur l'hôte Windows :
python scripts/run_redis_cnp_multivm_campaign.py --redis-url redis://localhost:6379/0 --run-id multivm_cnp_20260909T202632Z_37592 --agents debian-alpha,ubuntu-beta --tasks 60
python scripts/generate_multi_agent_architecture_diagrams.py
```

Redis doit répondre sur `redis://localhost:6379/0`. La reproduction multi-VM exige le lancement préalable des deux agents invités avec le même `run_id` et le même namespace. Les identifiants locaux sont chiffrés par DPAPI dans `.secrets/`, dossier exclu de Git; aucun mot de passe n'est écrit dans les rapports ou commandes versionnées.

## 20. Recommandations pour le mémoire

Ne pas modifier le manuscrit automatiquement. Transmettre à Luna uniquement les résultats du run principal, du run Redis local et du run multi-VM retenu, avec les limites ci-dessus. Présenter la décision distribuée, l’adaptation contrôlée, l’auditabilité et l’idempotence comme contributions; ne pas promettre un débit supérieur. Conserver la formulation « agents exécutés sur Debian et Ubuntu, avec transport Redis central sur l'hôte du laboratoire ».

## Tableau final de fermeture des critiques

| Critique du jury | Avant | Modification | Expérience | Résultat | Statut après correction |
|---|---|---|---|---|---|
| agents = simples workers | Consommation Redis au premier lecteur compatible | état, capacités, offre/refus, CNP et handlers multiples | tests + Redis local + Debian/Ubuntu | offres, refus, attributions et exécutions sur deux VM | CORRIGÉ |
| autonomie trop faible | superviseur impératif | score calculé localement; superviseur limité au registre et à l’arbitrage | matrice C/D + Redis | exécutant choisi parmi les offres | CORRIGÉ |
| mémoire non démontrée | mémoire présente dans le code | ablation OFF/ON et rupture en deux phases | 120 tâches adaptatives | changement d’offre; huit réattributions puis zéro | CORRIGÉ |
| benchmark 60 tâches | une seule petite charge | 100/500/1 000/5 000, dix répétitions, quatre architectures | 160 runs | 264 000 tâches, 0 échec | CORRIGÉ |
| résilience pré-ACK seulement | crash avant traitement | résultat durable avant ACK et replay inter-processus | harnais pending + Redis idempotent | 0 doublon, 1 reprise; pas de `XAUTOCLAIM` multi-VM | PARTIELLEMENT CORRIGÉ |
| pas de bout-en-bout | composants isolés | chaîne source → API avec audit | `e2e-ma_20260909T160812Z_34016` | 8/8 étapes, 0 erreur, 0 fallback | CORRIGÉ |
| distribution limitée | consumers Redis | CNP Redis inter-processus et multi-VM | `multivm_cnp_20260909T202632Z_37592` | 60/60 tâches, deux OS/hôtes/PID, 15 refus, 1 réattribution | CORRIGÉ |

Selon les critères techniques du prompt, le système est désormais défendable comme architecture multi-agents légère distribuée dans le laboratoire : deux VM exécutent des agents autonomes et communiquent via un CNP Redis explicite. Cette clôture ne couvre ni la haute disponibilité, ni les partitions réseau, ni une exploitation industrielle; la critique de résilience post-traitement par `XAUTOCLAIM` reste donc **PARTIELLEMENT CORRIGÉE**.
