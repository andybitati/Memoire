# Protocole préenregistré — E-MULTIVM-DYNAMIC-ALLOCATION

Statut au dépôt : **à exécuter après enregistrement des empreintes et commit du protocole**.

## Question

Le partage dynamique d'une charge d'allocation dans Redis corrige-t-il le départage alphabétique observé entre les deux agents HDFS, sans modifier ni alourdir leurs modèles de détection ? La politique dynamique fondée sur l'utilité puis la charge se comporte-t-elle comme un répartiteur distribué au moindre chargé lorsque les utilités sont égales ?

Cette campagne est décidée après le diagnostic E-MULTIVM-SATURATION-DIAG, qui a attribué toutes les tâches du bras à deux VM à `debian-alpha` : les deux agents proposaient la même utilité et le coordinateur historique départageait par identifiant.

## Programmes gelés

- `run_dynamic_arm.py` réutilise sans modification le générateur de charge et les métriques de `revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/run_saturation_arm.py` ; il ne change que `selection_policy` lors de la construction du coordinateur.
- `run_campaign.ps1` redémarre les mêmes agents sur Debian et Ubuntu avant chaque politique, avec un `run_id` distinct.
- `analyse_dynamic.py` calcule les agrégats et applique les décisions ci-dessous.
- Les agents emploient `revision_reports/agent_3/hdfs_redis_agent.py` et le coordinateur `src/logminer/agents/redis_contract_net.py`.

Les empreintes de ces fichiers sont inscrites au registre avant l'exécution et au manifeste après l'exécution.

## Politiques comparées

1. `utility_agent_id` : politique historique, utilité décroissante puis identifiant ; aucun compteur d'allocation partagé.
2. `utility_load` : utilité maximale d'abord ; entre propositions d'utilité égale, choix atomique du plus faible rapport contrats en vol / capacité déclarée.
3. `least_loaded` : choix atomique du plus faible rapport contrats en vol / capacité parmi toutes les propositions ; l'utilité ne départage que les charges égales.

Les deux agents déclarent la même confiance de 0,9 et une capacité de 1. Dans cette configuration, `utility_load` et `least_loaded` doivent donc différer seulement par le bruit d'exécution. Le modèle HDFS, le seuil, les tâches, le magasin d'idempotence et la boucle mono-thread restent inchangés.

## Plan d'exécution

- Deux VM VirtualBox distinctes : Debian (`debian-alpha`) et Ubuntu (`ubuntu-beta`).
- Redis sur l'hôte, joint depuis les VM par `192.168.56.1:6379`.
- Débits offerts : 8, 16 et 32 tâches/s.
- Fenêtre : 15 s ; trois répétitions par débit et par politique.
- 32 threads coordinateurs ; même fichier HDFS gelé et même seuil que le diagnostic antérieur.
- Politiques exécutées séquentiellement dans l'ordre historique, `utility_load`, `least_loaded`, avec redémarrage des agents et espace Redis distinct avant chaque bras.
- Aucune autre campagne chronométrée ne doit tourner en parallèle.

Un essai technique est autorisé après le commit avec un débit de 1 tâche/s, une fenêtre de 2 s et une répétition. Il vérifie uniquement le démarrage, l'écriture des artefacts et le retour des compteurs à zéro ; ses métriques ne sont pas retenues.

## Métriques et règles de décision

Métriques principales : capacité médiane atteinte au débit offert de 32 tâches/s, part des tâches de chaque agent sur l'ensemble des niveaux et nombre d'échecs. Les latences et débits par niveau produits par le runner restent des métriques secondaires.

Pour `utility_load` face au mode historique :

- `allocation_dynamique_confirmee` si aucun échec n'est observé, si Ubuntu reçoit au moins 25 % des tâches et si le rapport des capacités médianes `utility_load / utility_agent_id` atteint au moins 1,20 ;
- `partage_confirme_sans_gain_capacite` si les deux premières conditions sont remplies mais pas la troisième ;
- `allocation_dynamique_non_confirmee` sinon.

Pour `utility_load` face à `least_loaded` sous utilités égales, l'équivalence descriptive est retenue si le rapport des capacités appartient à [0,90 ; 1,10] et si l'écart maximal entre leurs parts par agent ne dépasse pas 0,10. Ce contrôle ne constitue pas un test d'équivalence statistique.

## Portée et conséquences

- Si le partage est confirmé, le défaut d'attribution alphabétique est corrigé sans apprentissage supplémentaire : l'allocation change, pas les détecteurs légers.
- Un gain de capacité montrerait que le départage historique empêchait d'exploiter la seconde boucle d'agent dans cet environnement ; son absence n'annulerait pas un partage effectivement observé.
- L'équivalence avec `least_loaded` ne vaut que pour des utilités égales. Elle ne démontre pas que les politiques sont équivalentes lorsque les confiances ou capacités diffèrent.
- La campagne reste limitée à deux VM locales, Redis sur l'hôte, un agent mono-thread par VM et un ordre séquentiel fixe des bras. Elle ne mesure ni un cluster de production, ni TLS, ni une panne réseau.

## Commande après commit

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File revision_reports\phase3_20261112\E-MULTIVM-DYNAMIC-ALLOCATION\run_campaign.ps1
```

Artefacts attendus : `experiments/phase_revision_20261112/E-MULTIVM-DYNAMIC-ALLOCATION/`, avec les CSV/JSON de chaque bras, `summary.json` et `MANIFEST_SHA256.csv`.
