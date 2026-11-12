# Protocole préenregistré — E-H2-MEMORY-CENTRAL

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit du protocole**.

## Question

Le gain conditionnel du compteur de fiabilité observé avec Contract Net dépend-il de la négociation entre agents, ou le même compteur lissé produit-il également un gain lorsqu'il est greffé sur un répartiteur centralisé au moindre chargé ? Cette expérience est décidée après lecture d'E-H5-MEMORY-RELIABILITY et répond au comparateur manquant signalé pour H2.

## Programmes et essai technique

- Runner : `revision_reports/phase3_20261112/E-H2-MEMORY-CENTRAL/run_e_h2_memory_central.py`.
- Instrumentation, scénarios, injections, contrastes et règle de décision réutilisés sans modification depuis `revision_reports/chantier_20261105/agent_5/scripts/run_e_h5_e_cnp.py`.
- Répartiteur sans mémoire réutilisé depuis `revision_reports/chantier_20261105/agent_5/scripts/run_e_cnp_least_loaded.py`.
- Un essai technique est autorisé avant le dépôt sur les graines réservées 1 et 2, avec 40 tâches. Il vérifie les invariants, l'écriture des artefacts temporaires et la logique de décision ; ses métriques ne sont ni conservées ni interprétées comme résultat.

Les empreintes de ces programmes, des sources communes et des artefacts seront inscrites au manifeste final.

## Comparateurs

1. `least_loaded` : répartiteur centralisé au moindre chargé, sans mémoire. En cas d'égalité, la confiance déclarée puis l'identifiant déterminent l'ordre.
2. `least_loaded_mem` : même répartiteur ; entre agents également chargés, il classe d'abord la fiabilité lissée par couple (agent, type de tâche), définie par `(succès + 1) / (exécutions + 2)`. Le compteur part donc de 0,5 et est mis à jour après chaque exécution réelle.
3. `D` : Contract Net avec mémoire, comparateur de référence d'E-H5.

Les trois bras emploient les mêmes agents, tâches, durées de service et échecs potentiels appariés par graine. Chaque exécution part d'un état neuf.

## Conditions, taille et graines

- Trois agents, trois coordinateurs concurrents et deux places parallèles par agent, comme dans E-H5.
- Trois niveaux d'échec du meilleur agent déclaré : p = 0,3 ; 0,6 ; 0,9.
- 1 000 tâches par exécution.
- 30 graines nouvelles, de 20261601 à 20261630.
- Trois scénarios × 30 graines × trois bras, soit 270 exécutions. L'ordre des bras alterne selon la graine.

## Métriques et décision

- Métrique primaire : taux d'échec à la première exécution.
- Garde-fou : rapport de débit entre bras par graine.
- Secondaires : échecs finaux, exécutions par tâche, latence p95, indice de Jain et réattributions.
- IC bilatéraux de Student à 95 % sur les différences appariées par graine.
- Gain à un niveau, identique à E-H5 : borne supérieure de l'IC du delta du taux d'échec strictement négative et borne inférieure de l'IC du rapport de débit au moins égale à 0,95.
- Décision principale `least_loaded_mem - least_loaded` : `gain_general` si les trois niveaux montrent un gain, `gain_conditionnel` si un ou deux niveaux le montrent, `aucun_gain` sinon.
- Contrastes secondaires : `least_loaded_mem - D` et `D - least_loaded`, rapportés avec la même règle sans remplacer la décision principale.

## Conséquences préfixées

- `gain_general` ou `gain_conditionnel` : le compteur lissé apporte aussi son effet dans un répartiteur centralisé ; le gain ne peut donc pas être attribué à la négociation ou au caractère multi-agents. Les niveaux favorables et défavorables sont tous rapportés.
- `aucun_gain` alors que `D - least_loaded` reproduit un gain : le protocole fournit un indice en faveur d'une interaction avec l'architecture D, sans l'établir au-delà de cette simulation.
- `aucun_gain` dans les deux contrastes : le gain antérieur n'est pas répliqué sur les nouvelles graines.

Dans tous les cas, H2 reste appréciée séparément pour l'idempotence. Cette expérience porte uniquement sur la mémoire de fiabilité et ne permet pas d'attribuer un résultat à l'autonomie des agents.

## Portée

Exécution dans un seul processus, tâches synthétiques, échecs injectés et compteur central en mémoire vive. Le protocole ne mesure ni le coût d'un stockage partagé de la fiabilité, ni les délais d'information en environnement distribué, ni un apprentissage de politique.

## Commande après commit

```powershell
.venv\Scripts\python.exe revision_reports\phase3_20261112\E-H2-MEMORY-CENTRAL\run_e_h2_memory_central.py
```

Artefacts attendus dans `experiments/phase_revision_20261112/E-H2-MEMORY-CENTRAL/` : `runs.csv`, `summary.json`, `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
