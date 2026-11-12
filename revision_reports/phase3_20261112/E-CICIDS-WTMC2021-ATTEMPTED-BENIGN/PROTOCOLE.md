# Protocole préenregistré : E-CICIDS-WTMC2021-ATTEMPTED-BENIGN

Rédigé le 2026-11-12 et versionné **avant** l'exécution.

## 1. Question

E-CICIDS-WTMC2021-HOLDOUT a exclu les flux « - Attempted » (attaques tentées sans effet)
de la version corrigée de CICIDS2017. Les auteurs du jeu (Liu, Engelen et al., page
`Dataset_Download.html` du projet CNS 2022) recommandent de les compter comme bénins et de
ne pas en faire une classe. Le verdict de H4 sous son critère préenregistré change-t-il si
l'on suit cette recommandation ? Campagne décidée après lecture du résultat
d'E-CICIDS-WTMC2021-HOLDOUT et d'une remarque du jury.

## 2. Dispositif

- Runner : `run_attempted_benign.py`, qui importe sans modification le runner
  d'E-CICIDS-WTMC2021-HOLDOUT et ne remplace que `build_plans` : un flux « - Attempted »
  appartient à la classe bénigne (réservoirs d'entraînement des autres jours, bénins de
  test du jour du scénario), y compris lorsque l'attaque tentée est celle du scénario.
- Données, scénarios, variables, tirage, cinq modèles, hyperparamètres, graines 42 à 46,
  plafonds 8 000 / 4 000 : inchangés. Le champ `protocol` de `run_metadata.json` reprend
  le nom de la campagne parente (code importé) ; le dossier de sortie est propre.
- Essai à blanc (`--dry-run`) avant ce dépôt : composition seulement, mêmes effectifs que la
  campagne parente.

## 3. Règle de décision

Identique à E-CICIDS-HOLDOUT-FIX : un modèle bat la règle si son F1 moyen dépasse celui de
la prédiction systématiquement positive de plus de 0,01 et s'il la dépasse sur au moins 4
scénarios sur 5. MCC et PR-AUC en mesures secondaires.

## 4. Conséquences préfixées

- Même décision que la campagne parente : le manuscrit indique que le verdict ne dépend pas
  du traitement des flux tentés et présente les deux variantes.
- Décision différente : le manuscrit rapporte que le verdict sur la version corrigée dépend
  de ce traitement, retient la variante recommandée par les auteurs comme principale et
  révise le statut de H4 en conséquence.
