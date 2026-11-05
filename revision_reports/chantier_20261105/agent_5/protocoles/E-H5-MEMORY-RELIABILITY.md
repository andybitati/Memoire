# Protocole préenregistré — E-H5-MEMORY-RELIABILITY

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit C13-proc**.

## Question

À tâches, agents et échecs identiques, l'activation de la mémoire (architecture D) réduit-elle la part des tâches dont la première exécution échoue, par rapport à la mémoire désactivée (architecture C), lorsque la fiabilité réelle des agents diffère de leur confiance déclarée ?

## Entrées et programme gelés

- Programme : `revision_reports/chantier_20261105/agent_5/scripts/run_e_h5_e_cnp.py`, SHA-256 `0975d87982dad3c6588be0dd7ae11d9cec5b9a8af18d032c0939989aa6313aba` ; commande `E-H5`.
- Réutilisés sans modification : `build_agents`, `generate_workload`, `synthetic_effect` et `percentile` de `scripts/run_true_multi_agent_experiments.py` ; `src/logminer/agents/contract_net.py` ; `src/logminer/agents/intelligent_runtime.py` ; poids et seuil de `experiments/phase_multi_agent/configs/agent_policy.json`. Leurs empreintes seront inscrites au manifeste.
- Un essai technique a vérifié le programme avant ce dépôt, sur les graines réservées 1 et 2 et 40 tâches, hors de l'ensemble ci-dessous. Il a contrôlé les invariants et la logique de décision. Ses métriques n'ont pas été consultées ni conservées comme résultat.

## Comparateurs

1. `C` : Contract Net, mémoire désactivée.
2. `D` : Contract Net, mémoire activée.

Chaque exécution part d'agents neufs : la mémoire de D n'est pas amorcée.

## Conditions expérimentales

- Trois agents, leurs profils de confiance déclarée et deux places parallèles par agent, comme au benchmark A--D.
- Durée de service synthétique de 2 ms par exécution, afin que les exécutions se chevauchent et que le terme de charge de l'utilité agisse.
- Injection d'échecs : pour chaque type de tâche, seul l'agent de plus forte confiance déclarée échoue, avec une probabilité p. Le tirage dépend uniquement de (graine, tâche, agent) ; C et D subissent donc les mêmes échecs potentiels. Les autres couples ne reçoivent aucun échec.
- Trois niveaux préfixés : p = 0,3 ; 0,6 ; 0,9.

## Taille et graines

- 1 000 tâches par exécution.
- Analyse principale : trois coordinateurs concurrents, 30 graines, de 20261105 à 20261134, soit 180 exécutions. L'ordre des bras alterne selon la graine.
- Sensibilité : exécution séquentielle (un coordinateur), 10 premières graines, soit 60 exécutions. Elle est rapportée et ne modifie pas la décision.

## Métriques et critère numérique

- Métrique primaire : taux d'échec à la première exécution, défini comme la part des tâches dont la première exécution réelle échoue.
- Garde-fou : rapport de débit D/C par graine.
- Secondaires : échecs finaux, exécutions par tâche, latence p95, indice de Jain des exécutions.
- Intervalles : IC bilatéral de Student à 95 % sur les différences appariées par graine.
- **Gain à un niveau** : la borne supérieure de l'IC du delta D - C du taux primaire est strictement négative **et** la borne inférieure de l'IC du rapport de débit est au moins égale à 0,95.
- **Décision globale** : `gain_general` si les trois niveaux montrent un gain ; `gain_conditionnel` si un ou deux niveaux le montrent, en les nommant ; `aucun_gain` sinon.

## Conséquence préfixée sur H5

H5 reste jugée sur son énoncé. La métrique primaire fixée ici porte sur la priorisation de l'attribution entre agents et non sur la priorisation des anomalies, qui reste non mesurée. La composante de promotion reste non tranchée.

- `aucun_gain` : le statut RÉFUTÉE est maintenu.
- `gain_conditionnel` ou `gain_general` : le constat « aucun gain n'est observé » cesse d'être exact pour la composante mémoire. Le statut de H5 devient NON TRANCHÉE, car la composante de promotion n'a pas été éprouvée, et le gain est énoncé avec les niveaux où il est observé. H5 n'est pas déclarée soutenue.

## Analyse prévue et portée

Tous les niveaux sont rapportés, y compris défavorables. L'expérience s'exécute dans un seul processus, sur des tâches synthétiques et des échecs injectés. Elle ne mesure ni une exécution distribuée ni une charge réelle, et ne compare pas la mémoire à une autre méthode de sélection des agents.

## Commande

Depuis la racine du dépôt :

```powershell
.venv\Scripts\python.exe revision_reports\chantier_20261105\agent_5\scripts\run_e_h5_e_cnp.py E-H5
```

## Artefacts attendus

Dossier `experiments/phase_revision_20261105/E-H5-MEMORY-RELIABILITY/` : `runs.csv`, `summary.json`, `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
