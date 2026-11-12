# Protocole préenregistré : E-QR2-REAL-INFERENCE

Rédigé le 2026-11-12 et versionné **avant** l'exécution. Tout écart sera ajouté au
registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md`.

## 1. Question

Sur des microtâches presque vides, le monolithe A traite 55 à 72 fois plus de tâches par
seconde que les architectures à agents C et D. Une estimation, non mesurée, en déduit un
surcoût d'environ 0,8 ms par tâche, soit moins de 1 % d'une inférence réelle de 105 ms,
**à condition que ce surcoût soit additif**, c'est-à-dire indépendant de la durée de la
tâche. Cette campagne mesure le surcoût sur une tâche d'inférence réelle et teste
l'hypothèse d'additivité. Elle a été décidée après lecture du benchmark et d'une critique
de relecteur.

## 2. Dispositif

- Runner : `revision_reports/phase2_20261112/E-QR2-REAL-INFERENCE/run_e_qr2_real_inference.py`
  (empreinte au registre). Il réutilise sans modification `scripts/run_true_multi_agent_experiments.py`
  (architectures A, B, C, D, agents alpha, beta, gamma, coordinateur Contract Net corrigé) ;
  seul l'effet exécuté par tâche est remplacé.
- Deux types de tâche : **micro** (effet synthétique d'origine) ; **réelle** : même effet,
  puis appel de `decision_function` du modèle Isolation Forest HDFS du prototype
  (`models/isolation_forest_hdfs_colab.joblib`, 21 variables) sur un vecteur dérivé des
  valeurs de la tâche. Le calcul est celui du modèle réel ; l'entrée est synthétique. Durée
  mesurée lors d'un contrôle préalable : environ 16 ms par appel isolé.
- Nombre de workers : **1** (exécution séquentielle, plan principal : le surcoût n'est pas
  confondu avec le parallélisme) et **3** (configuration du benchmark d'origine, plan
  secondaire).
- 200 tâches par exécution ; 10 répétitions ; graines nouvelles 20261401 à 20261410 ;
  ordre des architectures alterné par graine. Soit 160 exécutions.

## 3. Mesures

Par exécution : débit, latence médiane et p95, messages par tâche. Par graine et par
configuration : temps de service de A, `1000/débit`, en ms ; surcoût absolu de X (B, C, D)
sur A, `1000/débit_X − 1000/débit_A`, en ms par tâche ; surcoût relatif ; rapport de débit.
IC de Student à 95 % sur les 10 graines.

## 4. Règle de décision (fixée avant exécution)

Plan principal (1 worker). Pour C et pour D, soit `S_micro` le surcoût absolu moyen mesuré
sur microtâches **dans la même exécution**, et `B = 2 × S_micro` :
- borne supérieure de l'IC du surcoût absolu sur tâche réelle ≤ B → `surcout_additif_confirme` ;
- borne inférieure > B → `surcout_non_additif` ;
- sinon → `indetermine`.
Conclusion : verdict commun à C et D, sinon `mixte`.

## 5. Conséquences préfixées

- `surcout_additif_confirme` : l'estimation de surcoût relatif devient une mesure ; le
  manuscrit rapporte le surcoût absolu et relatif mesurés sur la tâche réelle et retire la
  mention « non mesurée » ; l'extrapolation à 105 ms reste présentée comme telle.
- `surcout_non_additif` : l'estimation de moins de 1 % est retirée du manuscrit et des
  résumés ; le surcoût mesuré sur tâche réelle est rapporté.
- `indetermine` ou `mixte` : les deux mesures sont rapportées, sans conclusion sur
  l'additivité ; l'estimation reste qualifiée de non vérifiée.
Le plan secondaire (3 workers) est rapporté dans tous les cas, sans règle de décision.

## 6. Déclarations préalables

- Essai technique (`--smoke`, graines réservées 1 et 2, 20 tâches) : 32 exécutions, aucune
  métrique affichée ni écrite.
- Le modèle a été sérialisé avec scikit-learn 1.6.1 et est chargé avec la version 1.8.0
  (avertissement `InconsistentVersionWarning`). Le coût d'appel peut différer de celui de
  l'environnement d'origine ; les versions sont inscrites dans `summary.json`.
- Un seul hôte, un seul processus, sans Redis ; machine non dédiée.

## 7. Commande et artefacts

```powershell
.venv\Scripts\python.exe revision_reports\phase2_20261112\E-QR2-REAL-INFERENCE\run_e_qr2_real_inference.py
```

`experiments/phase_revision_20261112/E-QR2-REAL-INFERENCE/` : `runs.csv`, `summary.json`,
`MANIFEST_SHA256.csv`.
