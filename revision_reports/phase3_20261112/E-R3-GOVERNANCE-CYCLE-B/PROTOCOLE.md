# Protocole préenregistré — E-R3-GOVERNANCE-CYCLE-B

Statut au dépôt : **à exécuter après enregistrement du SHA-256 et commit du protocole**.

## Origine : protocole conçu après lecture d'un résultat

Ce protocole est **décidé après lecture** d'E-R3-GOVERNANCE-CYCLE (commit `9461b69`), qui conclut `cycle_non_exerce` : 25 rejets conformes et aucune promotion, parce que le modèle initial (`LogisticRegression`) atteint déjà un F1 de validation de 0,9913 à 0,9931 et qu'aucun candidat ne peut gagner $\delta_{\min} = 0{,}02$. La seule modification de fond est le choix d'un modèle initial faible, pour que la branche de promotion soit atteignable. Les ordres de grandeur des F1 de validation des candidats sont donc **connus** au moment de concevoir ce protocole ; il vérifie la procédure, il ne prédit pas la qualité des candidats. Le premier résultat reste rapporté tel quel.

## Question

Identique à E-R3-GOVERNANCE-CYCLE : la procédure remplace-t-elle le modèle actif seulement lorsqu'un candidat satisfait la règle de promotion, au cours d'un cycle où se succèdent promotions et rejets, avec une validation figée pour décider et des tests indépendants lus après chaque décision ?

## Programmes

- Runner : `revision_reports/phase3_20261112/E-R3-GOVERNANCE-CYCLE-B/run_e_r3_governance_cycle_b.py`, copie du runner d'E-R3-GOVERNANCE-CYCLE dont seuls changent l'identifiant, les graines, le modèle initial, l'ordre des candidats et le chemin de l'entraîneur (différence vérifiable par `diff`).
- Entraîneur des candidats et procédure évaluée inchangés : `revision_reports/phase3_20261112/E-R3-GOVERNANCE-CYCLE/train_candidate.py` ; `run_plan` de `scripts/monthly_model_retraining.py` avec promotion activée.
- Données, partitions (60/20/20 stratifié hors fichier DDoS, test DDoS), contrôles par décision, métrique (F1 de validation), $\delta_{\min} = 0{,}02$ et mesures secondaires : **identiques** à `revision_reports/phase3_20261112/E-R3-GOVERNANCE-CYCLE/PROTOCOLE.md`.
- Essai technique avant dépôt sur la graine réservée 1, en répertoire temporaire : cinq décisions, invariants satisfaits ; aucune métrique affichée ni lue.

## Cycle

- Modèle actif initial : `Stump` (arbre de profondeur 1).
- Candidats, dans cet ordre, chacun comparé au modèle actif du moment : `RandomForest_small`, `LogisticRegression`, `RandomForest`, `Stump`, `HistGradientBoosting`.
- Graines nouvelles : 20261711 à 20261715 (aucune graine d'E-R3-GOVERNANCE-CYCLE n'est réutilisée), soit 25 décisions.

## Décision principale (R3), inchangée

- `R3_verifiee` : tous les contrôles des 25 décisions passent, et chaque graine comporte au moins une promotion et au moins un rejet ;
- `cycle_non_exerce` : tous les contrôles passent, mais une graine au moins n'a pas exercé les deux branches ;
- `R3_non_verifiee` : au moins un contrôle échoue.

Mesures secondaires inchangées : F1 sur chaque test du modèle actif final moins celui du modèle initial (IC de Student à 95 %, 5 graines, `benefice_confirme` si la borne inférieure est strictement positive), promotions nuisibles et manquées sur le test i.i.d., MCC.

## Conséquences préfixées

- `R3_verifiee` : R3 est rapportée « vérifiée dans le périmètre de cette expérience » (un jeu, des candidats supervisés fixés, une métrique), **en signalant que le protocole a été conçu après un premier essai où la branche de promotion n'était pas atteignable**. Le bénéfice mesuré est rapporté séparément : comme le modèle initial est volontairement faible, un gain sur le test i.i.d. montre que les promotions ne dégradent pas le modèle actif, non qu'une mise à jour réelle en exploitation serait bénéfique. Le test DDoS est rapporté sans changer la décision.
- `cycle_non_exerce` ou `R3_non_verifiee` : R3 reste non vérifiée et le texte décrit pourquoi.

## Portée

Celle d'E-R3-GOVERNANCE-CYCLE : un seul jeu, candidats supervisés tabulaires fixés à l'avance, décisions automatiques sans retour d'analyste, ni mise à jour autonome continue ni familles non supervisées.

## Commande après commit

```powershell
$env:PYTHONIOENCODING='utf-8'; .venv\Scripts\python.exe revision_reports\phase3_20261112\E-R3-GOVERNANCE-CYCLE-B\run_e_r3_governance_cycle_b.py
```

Artefacts attendus dans `experiments/phase_revision_20261112/E-R3-GOVERNANCE-CYCLE-B/` : `cycles.csv`, `summary.json`, `split_seed_*.json`, `audit.jsonl`, `MANIFEST_SHA256.csv` ; modèles et partitions dans `_work/` (empreintes au manifeste, non versionnés).

Tout écart éventuel sera ajouté au registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md` sans modifier ce fichier.
