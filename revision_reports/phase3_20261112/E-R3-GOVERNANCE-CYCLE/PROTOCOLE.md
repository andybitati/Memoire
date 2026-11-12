# Protocole préenregistré — E-R3-GOVERNANCE-CYCLE

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit du protocole**.

## Question

La procédure de mise à jour contrôlée remplace-t-elle le modèle actif seulement lorsqu'un candidat satisfait la règle de promotion (exigence R3), au cours d'un cycle complet où se succèdent des candidats meilleurs et moins bons, avec une validation figée pour décider et un test indépendant, jamais lu par la procédure, pour mesurer l'effet des décisions ? Cette expérience répond au comparateur manquant J4(d) du troisième retour du jury. Les essais antérieurs de la phase 4 (`data/processed/final_experiments_2026/phase_4/`) évaluaient courant et candidat sur le même jeu que celui servant au rapport ; ils ne séparaient pas validation et test et ne comportaient pas de succession de décisions.

## Programmes

- Runner : `revision_reports/phase3_20261112/E-R3-GOVERNANCE-CYCLE/run_e_r3_governance_cycle.py`.
- Entraîneur des candidats : `revision_reports/phase3_20261112/E-R3-GOVERNANCE-CYCLE/train_candidate.py`, appelé comme commande d'entraînement du plan.
- Procédure évaluée, **inchangée** : `run_plan` de `scripts/monthly_model_retraining.py` avec `--promote` (entraînement, comparaison sur la validation, règle $\Delta M \ge \delta_{\min}$, sauvegarde puis remplacement, journal d'audit).
- Échantillonnage CICIDS2017 réutilisé sans modification : `load_holdout` de `scripts/run_final_experiments.py` (scénario DDoS : 8 000 négatifs et 8 000 positifs hors fichier DDoS ; 4 000 et 4 000 dans le fichier DDoS).
- Un essai technique a été exécuté avant le dépôt sur la graine réservée 1, dans un répertoire temporaire : il a seulement vérifié que les cinq décisions s'exécutent et que les invariants sont satisfaits ; aucune métrique n'a été affichée ni lue.

## Données et partitions

Pour chaque graine $s$ :

1. Pool hors fichier DDoS (16 000 flux) partagé par stratification avec `random_state = s` en **entraînement** (60 %), **validation figée** (20 %) et **test i.i.d.** (20 %).
2. **Test DDoS** : échantillon du fichier `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`, scénario jamais vu à l'entraînement ni en validation.
3. Les empreintes SHA-256 des quatre partitions sont enregistrées avant le premier cycle ; l'empreinte de la validation est revérifiée à chaque décision.
4. Seule la validation figée figure dans le plan transmis à `run_plan` ; le runner refuse un plan qui mentionne un test. Les tests ne sont lus qu'après chaque décision.

## Cycle

- Modèle actif initial : `LogisticRegression` (configuration de `_candidate_models`).
- Candidats proposés successivement, dans cet ordre fixe, chacun comparé au modèle actif du moment :
  1. `Stump` : arbre de profondeur 1 (candidat attendu moins bon) ;
  2. `RandomForest` (configuration de `_candidate_models`) ;
  3. `RandomForest_small` : même forêt entraînée sur 1 % stratifié de l'entraînement (candidat attendu moins bon) ;
  4. `ExtraTrees` ;
  5. `HistGradientBoosting`.
- Métrique de décision : F1 sur la validation figée ; gain minimal $\delta_{\min} = 0{,}02$ (valeur des essais de la phase 4).
- Graines : 20261701 à 20261705, soit 25 décisions.

Les attentes « meilleur » ou « moins bon » ne servent qu'à garantir que le cycle exerce les deux branches ; elles ne font pas partie du critère.

## Contrôles par décision

Pour chaque décision, le runner recalcule indépendamment les F1 de validation du modèle actif et du candidat (relecture du fichier figé) et vérifie :

- `validation_unchanged` : empreinte de la validation identique à celle de la préparation ;
- `decision_matches_rule` : promotion si et seulement si $\Delta F1_{\text{val}} \ge 0{,}02$ ;
- `delta_matches_code` : écart recalculé égal à celui du code à $10^{-6}$ près ;
- promotion : la sauvegarde a l'empreinte du modèle actif avant décision et le nouveau modèle actif celle du candidat ;
- rejet : le modèle actif est inchangé et aucune sauvegarde n'est créée.

Une décision à moins de $10^{-6}$ du seuil est signalée (`borderline`) et rapportée.

## Décision principale (R3)

- `R3_verifiee` : tous les contrôles des 25 décisions passent, et chaque graine comporte au moins une promotion et au moins un rejet ;
- `cycle_non_exerce` : tous les contrôles passent, mais une graine au moins n'a pas exercé les deux branches ;
- `R3_non_verifiee` : au moins un contrôle échoue.

## Mesures secondaires, rapportées sans changer la décision R3

- Effet du cycle : F1 sur chaque test du modèle actif final moins celui du modèle initial, par graine ; moyenne et IC de Student bilatéral à 95 % sur 5 graines. Étiquette `benefice_confirme` si la borne inférieure est strictement positive, `benefice_non_confirme` sinon ; calculée séparément pour le test i.i.d. et pour le test DDoS.
- Qualité des décisions sur le test i.i.d. : promotions nuisibles (F1 test du candidat promu inférieur à celui du modèle remplacé) et promotions manquées (candidat rejeté dont le F1 test dépasse celui du modèle actif d'au moins 0,02).
- MCC des modèles actifs sur les deux tests.

## Conséquences préfixées

- `R3_verifiee` : R3 passe de « non vérifiée » à « vérifiée » dans le périmètre de cette expérience (un jeu, une famille de modèles supervisés, une métrique, des candidats fixés). Le bénéfice est rapporté séparément : un `benefice_non_confirme` sur le test DDoS signifierait que la sélection sur une validation de la même distribution ne garantit pas le transfert à un scénario nouveau.
- `cycle_non_exerce` : R3 reste non vérifiée ; le texte le dit.
- `R3_non_verifiee` : le défaut est décrit et l'affirmation de conception corrigée.

## Portée

Un seul jeu (CICIDS2017, échantillon équilibré), candidats supervisés tabulaires fixés à l'avance, décisions automatiques sans retour d'analyste. L'expérience ne mesure ni une mise à jour autonome continue en exploitation, ni le réentraînement à partir des retours de l'analyste, ni les familles non supervisées dont le score de stabilité tient lieu de métrique.

## Commande après commit

```powershell
$env:PYTHONIOENCODING='utf-8'; .venv\Scripts\python.exe revision_reports\phase3_20261112\E-R3-GOVERNANCE-CYCLE\run_e_r3_governance_cycle.py
```

Artefacts attendus dans `experiments/phase_revision_20261112/E-R3-GOVERNANCE-CYCLE/` : `cycles.csv`, `summary.json`, `split_seed_*.json`, `audit.jsonl`, `MANIFEST_SHA256.csv` ; modèles et partitions dans `_work/` (empreintes au manifeste, non versionnés).

Tout écart éventuel sera ajouté au registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
