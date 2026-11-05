# Protocole préenregistré — E-CNP-STATIC-ASSIGNMENT

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit C13-proc**.

## Question

Sur le même flux de tâches et avec les mêmes agents, la négociation Contract Net apporte-t-elle un avantage mesurable face à une table d'affectation statique dotée du même repli ?

## Entrées et programme gelés

- Programme : `revision_reports/chantier_20261105/agent_5/scripts/run_e_h5_e_cnp.py`, SHA-256 `0975d87982dad3c6588be0dd7ae11d9cec5b9a8af18d032c0939989aa6313aba` ; commande `E-CNP`.
- Réutilisés sans modification : `build_agents`, `generate_workload`, `synthetic_effect` et `percentile` de `scripts/run_true_multi_agent_experiments.py` ; `src/logminer/agents/contract_net.py` ; `src/logminer/agents/intelligent_runtime.py` ; poids et seuil de `experiments/phase_multi_agent/configs/agent_policy.json`. Leurs empreintes seront inscrites au manifeste.
- Un essai technique a vérifié le programme avant ce dépôt, sur les graines réservées 1 et 2 et 40 tâches, hors de l'ensemble ci-dessous. Il a contrôlé les invariants et la logique de décision. Ses métriques n'ont pas été consultées ni conservées comme résultat.

## Comparateurs

1. `static` : table type de tâche vers liste d'agents, ordonnée par confiance déclarée décroissante, identifiant en départage. La tâche va au premier agent de la liste ; en cas de refus d'attribution ou d'échec, elle passe au suivant. Ni négociation, ni mémoire, ni message de protocole. La table utilise donc la même information déclarée que le Contract Net.
2. `C` : Contract Net, mémoire désactivée. **Contraste principal C - static** : il isole la négociation.
3. `D` : Contract Net, mémoire activée. **Contraste secondaire D - static**, soumis à la même règle.

Les trois bras utilisent les mêmes agents et le même code d'exécution, avec trois coordinateurs concurrents. Chaque exécution part d'agents neufs.

## Scénarios

- `s0_cost_no_service` : aucune durée de service, aucun échec. Mesure du coût d'orchestration seul, **hors règle de décision**, car un gain n'y est pas attendu.
- `s1_nominal` : 2 ms de service, aucun échec.
- `s2_best_declared_failure_p30` : 2 ms ; l'agent de plus forte confiance déclarée pour chaque type échoue avec p = 0,3, selon un tirage dépendant uniquement de (graine, tâche, agent).
- `s3_silent_gamma_failure` : 2 ms ; à partir de la tâche d'indice 300, `agent-gamma` échoue sur toutes ses exécutions tout en continuant de se déclarer sain.
- `s4_slow_gamma` : 2 ms pour les autres agents, 10 ms pour `agent-gamma`, aucun échec.

## Taille et graines

1 000 tâches par exécution ; 30 graines, de 20261105 à 20261134 ; soit 450 exécutions. L'ordre des bras alterne selon la graine.

## Métriques et critère numérique

- Primaires : taux d'échec à la première exécution ; rapport de débit par graine (bras / static).
- Secondaires : échecs finaux, exécutions par tâche, latence p95, indice de Jain, messages par tâche.
- Intervalles : IC bilatéral de Student à 95 % sur les valeurs appariées par graine.
- Décision par scénario, pour chaque contraste :
  - **favorable** si (borne supérieure de l'IC du delta d'échec < 0 et borne inférieure de l'IC du rapport de débit >= 0,95) ou (borne inférieure de l'IC du rapport de débit > 1,05 et borne supérieure de l'IC du delta d'échec <= 0,01) ;
  - **défavorable**, à défaut, si (borne inférieure de l'IC du delta d'échec > 0) ou (borne supérieure de l'IC du rapport de débit < 0,95 et borne supérieure de l'IC du delta d'échec >= 0) ;
  - **indéterminé** sinon.
- Décision globale sur s1 à s4 : `avantage_general` si les quatre scénarios sont favorables ; `avantage_conditionnel` si un à trois le sont, en les nommant ; `aucun_avantage` sinon. La conclusion principale sur la négociation repose sur C - static.

## Analyse prévue et portée

Tous les scénarios et contrastes sont rapportés, y compris défavorables. Le résultat remplace le constat « aucune expérience ne compare Contract Net à une affectation statique », quel que soit son sens. L'expérience s'exécute dans un seul processus, sans courtier réseau, sur des tâches synthétiques. Elle ne compare pas Contract Net à Celery, Kafka ou à un moteur de workflow, et ne mesure pas une exécution distribuée.

## Commande

Depuis la racine du dépôt :

```powershell
.venv\Scripts\python.exe revision_reports\chantier_20261105\agent_5\scripts\run_e_h5_e_cnp.py E-CNP
```

## Artefacts attendus

Dossier `experiments/phase_revision_20261105/E-CNP-STATIC-ASSIGNMENT/` : `runs.csv`, `summary.json`, `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
