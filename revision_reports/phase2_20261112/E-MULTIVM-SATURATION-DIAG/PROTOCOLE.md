# Protocole préenregistré : E-MULTIVM-SATURATION-DIAG

Rédigé le 2026-11-12 et versionné **avant** l'exécution.

## 1. Origine et hypothèse

La saturation sur deux VM (`agent3_saturation_multivm_20261104T142325Z`) plafonne entre 8,4
et 15,0 tâches/s ; le goulot n'avait pas été isolé. Une relecture de la trace par tâche
(non préenregistrée, avant ce protocole) montre : négociation médiane d'environ 90 ms à
faible charge ; part d'Ubuntu nulle jusqu'à 16 tâches/s et de 1 à 3 % au-delà. Le code de
l'agent (`revision_reports/agent_3/hdfs_redis_agent.py`) traite sa boîte de réception dans
une seule boucle, une tâche à la fois (`max_parallel_tasks=1`) ; les deux agents déclarent
la même confiance (0,9) et le coordinateur départage les utilités égales par l'identifiant.

**Hypothèse H-SERIE** : le plafond est la capacité d'un seul agent qui exécute en série
(Debian gagne presque toutes les attributions) ; la seconde VM n'ajoute presque pas de
capacité. Question secondaire : la capacité d'un agent seul diffère-t-elle entre Debian
(Python 3.13.5) et Ubuntu (Python 3.8.10) ?

## 2. Dispositif

- Runner de bras : `run_saturation_arm.py`, copie de `revision_reports/agent_3/run_saturation_multivm.py`
  dont seuls changent le dossier de sortie et l'autorisation d'un agent unique. Producteur en
  boucle ouverte, 32 coordinateurs concurrents, tâche `hdfs.block.evaluate` sur scores HDFS
  gelés, délai de réponse 5 s : inchangés.
- Agents : `revision_reports/agent_3/hdfs_redis_agent.py` inchangé, lancé par
  `start_agents.ps1` (Redis de l'hôte via l'interface host-only 192.168.56.1).
- Bras exécutés successivement : **both** (Debian et Ubuntu), **debian** (Debian seule),
  **ubuntu** (Ubuntu seule). Débits offerts 2, 4, 8, 16, 32 tâches/s ; fenêtres de 20 s ;
  3 répétitions ; orchestration `run_diag.ps1`, analyse `analyse_diag.py`.
- Essai technique préalable : Debian seule, 2 tâches/s, 3 s, 1 répétition (6 tâches,
  0 échec) ; sortie supprimée, aucune métrique de capacité consultée.

## 3. Mesures

Capacité d'un bras : médiane, sur les 3 répétitions, du débit atteint (tâches réussies /
instant de la dernière fin) au débit offert de 32 tâches/s. Part d'Ubuntu dans le bras
both, aux débits 2, 4 et 8 et sur tous les débits. Échecs par bras.

## 4. Règle de décision (fixée avant exécution)

Soit `R = capacité(both) / capacité(debian)` et `S` la part d'Ubuntu dans both aux débits
2, 4 et 8 :
- `R ≤ 1,2` et `S ≤ 0,10` → `goulot_agent_serie_confirme` ;
- `R ≥ 1,5` → `goulot_agent_serie_refute` ;
- sinon → `indetermine`.
La question secondaire est rapportée par `capacité(ubuntu) / capacité(debian)`, sans règle
de décision ; un écart ne pourra pas être attribué à la seule version de Python (machines,
système et ressources diffèrent aussi).

## 5. Conséquences préfixées

- `goulot_agent_serie_confirme` : le manuscrit explique le plafond par l'agent unique en
  série et le départage déterministe, et précise que le dispositif ne pouvait pas montrer un
  partage de charge.
- `goulot_agent_serie_refute` : le manuscrit retire cette explication et rapporte la
  capacité ajoutée par la seconde VM.
- `indetermine` : mesures rapportées sans explication causale.

## 6. Portée

Un hôte et deux VM VirtualBox de laboratoire, Redis local en conteneur ; aucune
modification de l'agent ni du coordinateur Redis. La trace d'endurance tronquée n'est pas
traitée par cette campagne.
