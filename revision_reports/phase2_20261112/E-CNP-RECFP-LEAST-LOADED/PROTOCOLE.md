# Protocole préenregistré : E-CNP-RECFP-LEAST-LOADED

Rédigé le 2026-11-12 et versionné dans le dépôt **avant** l'exécution. Tout écart sera
ajouté au registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md`
sans modifier ce fichier.

## 1. Question

E-CNP-LEAST-LOADED a conclu à l'absence d'avantage de Contract Net face au répartiteur au
moindre chargé. Le coordinateur comparé contenait un défaut : sa liste de repli était fixée
au premier appel d'offres et ne contenait que les agents qui avaient proposé ; un agent
occupé à cet instant n'était jamais ressollicité, d'où des tâches perdues (5 sous fiabilité
hétérogène). Le répartiteur et la table examinent, eux, tous les agents à chaque tentative.
La conclusion tient-elle avec un coordinateur corrigé ? Cette expérience a été décidée
après lecture d'E-CNP-LEAST-LOADED et des critiques d'un relecteur.

## 2. Correction et contrôles techniques (avant ce dépôt)

- `src/logminer/agents/contract_net.py` : paramètre `fallback_policy`. Valeur par défaut
  `recfp` : une fois les offres en cours épuisées après un refus ou un échec, nouvel appel
  d'offres aux agents non encore tentés ; chaque agent est tenté au plus une fois. La valeur
  `frozen` conserve le comportement historique.
- Tests unitaires (`tests/test_true_multi_agent.py`, 14 tests, tous réussis) : ressollicitation
  d'un agent occupé au premier CFP ; comportement historique en `frozen` ; aucun agent tenté
  deux fois.
- Équivalence : `check_frozen_equivalence.py` compare l'ancien coordinateur (commit
  `b92ea2e`) au mode `frozen` sur les cinq scénarios, graines réservées 1 et 2, 200 tâches,
  un worker : 10 exécutions, 0 écart sur les compteurs indépendants du temps.
- Essai technique du runner (`--smoke`, graines 1 et 2, 40 tâches) : invariants vérifiés ;
  aucune métrique affichée ni consultée.

## 3. Programmes gelés

- Runner : `revision_reports/phase2_20261112/E-CNP-RECFP-LEAST-LOADED/run_e_cnp_recfp_least_loaded.py`
  (empreinte au registre). Il reprend sans modification
  `revision_reports/chantier_20261105/agent_5/scripts/run_e_cnp_least_loaded.py` et
  `run_e_h5_e_cnp.py`, et refuse de s'exécuter si le coordinateur par défaut n'est pas `recfp`.
- Coordinateur : `src/logminer/agents/contract_net.py` dans l'état du commit de ce protocole.

## 4. Comparateurs, scénarios, graines

Identiques à E-CNP-LEAST-LOADED : bras `least_loaded`, `C` (Contract Net, mémoire
désactivée, **repli corrigé**), `static` ; trois coordinateurs concurrents ; cinq scénarios
(`s0` hors règle, `s1` à `s4`) ; 1 000 tâches par exécution. **30 graines nouvelles**,
20261305 à 20261334, jamais utilisées ; 450 exécutions ; ordre des bras alterné.

## 5. Métriques et règle de décision (inchangées)

Primaires : taux d'échec à la première exécution et rapport de débit, IC de Student à 95 %.
Règle par scénario identique à E-CNP-LEAST-LOADED (favorable / défavorable / indéterminé,
seuils 0,95 et 1,05, tolérance 0,01). **Contraste principal : C − least_loaded**, décision
globale sur s1 à s4. Contrastes secondaires : `least_loaded − static`, `C − static`.

Critère secondaire, fixé à l'avance : nombre total d'échecs finaux (tâches perdues) de C
sur s1 à s4, comparé à celui de `least_loaded`. Prédiction de la correction : C ne perd pas
plus de tâches que le répartiteur.

## 6. Conséquences préfixées

- `aucun_avantage` pour C − least_loaded : la conclusion d'E-CNP-LEAST-LOADED ne tient pas
  au défaut de repli ; le manuscrit le dit et cite les deux campagnes.
- `avantage_conditionnel` ou `avantage_general` : le manuscrit corrige la conclusion
  antérieure, nomme les scénarios favorables et attribue l'écart à la correction du repli.
- Échecs finaux de C supérieurs à ceux du répartiteur : la correction est déclarée
  insuffisante, et la cause est recherchée avant toute autre interprétation.

## 7. Portée

Inchangée : un seul processus, tâches synthétiques, sans courtier réseau ; le répartiteur
lit l'état des agents sans coût. Le coordinateur Redis (`redis_contract_net.py`) n'est pas
modifié par cette correction et n'est pas évalué ici.

## 8. Commande

```powershell
.venv\Scripts\python.exe revision_reports\phase2_20261112\E-CNP-RECFP-LEAST-LOADED\run_e_cnp_recfp_least_loaded.py
```

Artefacts : `experiments/phase_revision_20261112/E-CNP-RECFP-LEAST-LOADED/` (`runs.csv`,
`summary.json`, `MANIFEST_SHA256.csv`).
