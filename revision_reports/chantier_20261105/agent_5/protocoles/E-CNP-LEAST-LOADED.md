# Protocole préenregistré — E-CNP-LEAST-LOADED

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit C13-proc**.

## Question

La négociation Contract Net apporte-t-elle un avantage mesurable face à un répartiteur qui observe seulement la charge des agents, sans échange d'offres ? E-CNP a montré un avantage conditionnel sur une table qui ignore la charge, sans pouvoir séparer la négociation de la prise en compte de la charge. Cette expérience comble ce manque ; elle a été décidée après lecture d'E-CNP, ce que le manuscrit doit indiquer.

## Entrées et programmes gelés

- Programme : `revision_reports/chantier_20261105/agent_5/scripts/run_e_cnp_least_loaded.py`, SHA-256 `5b48ed0bc6e1eb5529b1484d7c6ee83f4b1f83a04bccb77177520af2923d26f2`.
- Programme réutilisé sans modification : `revision_reports/chantier_20261105/agent_5/scripts/run_e_h5_e_cnp.py`, SHA-256 `0975d87982dad3c6588be0dd7ae11d9cec5b9a8af18d032c0939989aa6313aba` (instrumentation, scénarios, contrastes, règle de décision).
- Un essai technique a vérifié le programme avant ce dépôt, sur les graines réservées 1 et 2 et 40 tâches. Ses métriques n'ont pas été consultées ni conservées comme résultat.

## Comparateurs

1. `least_loaded` : pour chaque tentative, l'agent non encore essayé dont le taux d'occupation est le plus faible ; confiance déclarée puis identifiant en départage. En cas de refus ou d'échec, il passe à l'agent suivant parmi tous les agents restants. Ni offre, ni mémoire, ni message de protocole.
2. `C` : Contract Net, mémoire désactivée.
3. `static` : la table d'E-CNP, comme témoin.

Mêmes agents et même code d'exécution ; trois coordinateurs concurrents ; agents neufs à chaque exécution.

## Scénarios, taille et graines

Les cinq scénarios d'E-CNP, inchangés : `s0_cost_no_service` (hors règle), `s1_nominal`, `s2_best_declared_failure_p30`, `s3_silent_gamma_failure`, `s4_slow_gamma`. 1 000 tâches par exécution ; 30 graines nouvelles, de 20261205 à 20261234, non utilisées par E-CNP ; soit 450 exécutions. L'ordre des bras alterne selon la graine.

## Métriques et critère numérique

- Primaires, inchangées : taux d'échec à la première exécution et rapport de débit par graine, avec IC de Student à 95 %.
- Secondaires : échecs finaux, exécutions par tâche, latence p95, indice de Jain, messages par tâche.
- Règle par scénario, identique à E-CNP : **favorable** si (borne supérieure de l'IC du delta d'échec < 0 et borne inférieure de l'IC du rapport de débit >= 0,95) ou (borne inférieure de l'IC du rapport de débit > 1,05 et borne supérieure de l'IC du delta d'échec <= 0,01) ; **défavorable**, à défaut, si (borne inférieure de l'IC du delta d'échec > 0) ou (borne supérieure de l'IC du rapport de débit < 0,95 et borne supérieure de l'IC du delta d'échec >= 0) ; **indéterminé** sinon.
- **Contraste principal : C - least_loaded.** Décision globale sur s1 à s4 : `avantage_general`, `avantage_conditionnel` ou `aucun_avantage`, comme dans E-CNP.
- Contrastes secondaires, même règle : `least_loaded - static` et `C - static`.

## Conséquences préfixées

- `aucun_avantage` pour C - least_loaded : aucun avantage de la négociation sur la simple prise en compte de la charge n'est établi dans ce protocole.
- `avantage_conditionnel` ou `avantage_general` : l'avantage est énoncé avec les scénarios nommés, comme propre à l'utilité composite de Contract Net par rapport au moindre chargé. Il n'établit pas la supériorité sur d'autres répartiteurs.
- Si `least_loaded - static` est favorable sur les scénarios où `C - static` l'est aussi, le manuscrit conclut que la prise en compte de la charge suffit à y produire un gain face à la table.

## Portée

Tous les contrastes sont rapportés. L'expérience s'exécute dans un seul processus, sur des tâches synthétiques, sans courtier réseau. Le répartiteur lit directement l'état des agents, sans coût de transport ni information périmée ; en exécution distribuée, cet avantage de construction pourrait disparaître. Elle ne compare pas Contract Net à Celery, à Kafka ou à un moteur de workflow.

## Commande

Depuis la racine du dépôt :

```powershell
.venv\Scripts\python.exe revision_reports\chantier_20261105\agent_5\scripts\run_e_cnp_least_loaded.py
```

## Artefacts attendus

Dossier `experiments/phase_revision_20261105/E-CNP-LEAST-LOADED/` : `runs.csv`, `summary.json`, `MANIFEST_SHA256.csv`.

Tout écart éventuel sera ajouté au registre `PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
