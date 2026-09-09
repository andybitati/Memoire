# Tentative de campagne CNP multi-VM — 2026-09-09

## Résultat

Statut : **NON CORRIGÉ — campagne CNP multi-VM non exécutée**.

## Vérifications effectuées

| Vérification | Debian | Ubuntu |
|---|---|---|
| VM enregistrée dans VirtualBox | oui | oui |
| État observé après démarrage | `running` | `running` |
| Réseau principal | NAT | NAT |
| Redirection SSH | `127.0.0.1:2222 → guest:22` | `127.0.0.1:2223 → guest:22` |
| Port hôte ouvert après boot | oui | oui |
| Guest Additions RunLevel observé | 1 | 2 |
| Bannière SSH exploitable | non | non |
| Agent CNP lancé dans la VM | non | non |

Les tentatives SSH non interactives ont échoué pendant l'échange de bannière : `kex_exchange_identification` / `banner exchange: Unknown error`. Aucun identifiant invité utilisable n'était exposé dans l'environnement courant. Aucune tentative de mot de passe par supposition ou force brute n'a été effectuée.

## Conséquence scientifique

Les VM ont été détectées et démarrées, mais elles n'ont émis aucun `CFP`, `PROPOSE`, `REFUSE`, `AWARD`, `ACCEPT`, `RESULT` ou `FEEDBACK` dans la nouvelle campagne. Les anciennes campagnes Redis restent des preuves de consommateurs distribués; elles ne sont pas requalifiées en preuve du nouveau Contract Net.

Le critère « fonctionnement multi-VM réel du protocole autonome » reste donc non satisfait.

## Condition de reprise

Fournir un accès invité autorisé — clé SSH ou identifiants Guest Control — puis déployer :

- `src/logminer/agents/redis_contract_net.py`;
- `src/logminer/agents/intelligent_runtime.py`;
- `src/logminer/agents/idempotency.py`;
- `scripts/logminer_redis_cnp_agent.py`.

La campagne ne pourra être déclarée réussie qu'après production de traces où Debian et Ubuntu calculent chacune des offres ou refus, reçoivent des attributions et exécutent au moins une tâche via Redis.
