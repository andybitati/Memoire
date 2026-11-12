# Protocole préenregistré : E-QR2-OVERHEAD-DIRECT

Rédigé le 2026-11-12 et versionné **avant** l'exécution. Tout écart sera ajouté au
registre `revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md`.

## 1. Origine et question

E-QR2-REAL-INFERENCE a conclu `indetermine` sur l'additivité du surcoût. La relecture de
ses données montre un défaut de conception : le surcoût y est obtenu par différence de
débit entre exécutions distinctes, alors que la durée moyenne d'une tâche réelle varie
d'environ 1 ms d'une exécution à l'autre (écart-type 0,85 à 1,2 ms pour A, C, D ; pics
jusqu'à 32 ms pour B, machine non dédiée), soit davantage que le surcoût à détecter
(environ 0,3 ms). Cette campagne reprend la même question avec une mesure **intra-tâche** :
pour chaque tâche, surcoût = durée totale vue par l'architecture − durée du handler.
Elle a été décidée après lecture des résultats d'E-QR2-REAL-INFERENCE ; elle ne remplace
pas cette campagne, qui reste rapportée.

Question : le surcoût d'orchestration par tâche des architectures à agents est-il le même
sur une tâche réelle que sur une microtâche (surcoût additif) ?

## 2. Dispositif

- Runner : `revision_reports/phase2_20261112/E-QR2-OVERHEAD-DIRECT/run_e_qr2_overhead_direct.py`
  (empreinte au registre). Il réutilise sans modification le benchmark A–D et l'effet
  réel d'E-QR2-REAL-INFERENCE (appel `decision_function` du modèle Isolation Forest HDFS
  du prototype) ; il chronomètre l'appel du handler pour chaque tâche.
- Architectures A (contrôle : le surcoût doit y être quasi nul), C, D ; **1 worker** ;
  tâches micro et réelles ; 200 tâches ; 10 graines nouvelles, 20261501 à 20261510 ; ordre
  des architectures alterné. Soit 60 exécutions.
- Par exécution : médiane, moyenne et p95 du surcoût par tâche ; médiane de la durée du
  handler ; débit.

## 3. Règle de décision (fixée avant exécution)

Pour C et pour D, différence par graine `Δ = surcoût médian (réelle) − surcoût médian
(micro)`, IC de Student à 95 % sur 10 graines ; marge `m = 0,25 ms` :
- borne supérieure de l'IC ≤ m → `surcout_additif_confirme` ;
- borne inférieure > m → `surcout_non_additif` ;
- sinon → `indetermine`.
Conclusion : verdict commun à C et D, sinon `mixte`.

Contrôle de validité : le surcoût médian de A doit rester inférieur à 0,05 ms dans les deux
types de tâche ; sinon la mesure intra-tâche est déclarée non conforme et rapportée telle
quelle.

## 4. Conséquences préfixées

- `surcout_additif_confirme` : le manuscrit rapporte le surcoût intra-tâche mesuré et le
  surcoût relatif sur la tâche réelle ; l'extrapolation à une inférence plus longue peut
  être présentée comme fondée sur un surcoût additif mesuré.
- `surcout_non_additif` : le manuscrit rapporte la croissance mesurée du surcoût avec la
  durée de la tâche et retire toute extrapolation.
- `indetermine` ou `mixte` : mesures rapportées sans conclusion.

## 5. Déclarations préalables

Essai technique (`--smoke`, graines réservées 1 et 2, 20 tâches) : 12 exécutions, aucune
métrique affichée. Mêmes réserves qu'E-QR2-REAL-INFERENCE : entrée synthétique pour un
calcul de modèle réel ; modèle sérialisé avec scikit-learn 1.6.1 et chargé avec 1.8.0 ;
un hôte, un processus, sans Redis, machine non dédiée.

## 6. Commande et artefacts

```powershell
.venv\Scripts\python.exe revision_reports\phase2_20261112\E-QR2-OVERHEAD-DIRECT\run_e_qr2_overhead_direct.py
```

`experiments/phase_revision_20261112/E-QR2-OVERHEAD-DIRECT/` : `runs.csv`, `summary.json`,
`MANIFEST_SHA256.csv`.
