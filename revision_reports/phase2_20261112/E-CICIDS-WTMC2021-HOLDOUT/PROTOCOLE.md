# Protocole préenregistré : E-CICIDS-WTMC2021-HOLDOUT

Rédigé le 2026-11-12 et versionné **avant** l'exécution.

## 1. Question

Le critère préenregistré de H4 (F1 face à la prédiction systématiquement positive, holdout
par scénario de CICIDS2017, E-CICIDS-HOLDOUT-FIX) a été évalué sur les CSV d'origine, dont
Engelen, Rimmer et Joosen (WTMC 2021) ont montré les défauts de génération des flux et
d'étiquetage. Le verdict « aucun modèle ne bat la règle » tient-il sur leur version
régénérée et réétiquetée ?

## 2. Données

- Archive officielle `https://intrusion-detection.distrinet-research.be/WTMC2021/Dataset/dataset.zip`,
  téléchargée le 2026-11-12 (333 841 436 octets, Last-Modified 24/11/2021), SHA-256
  `4d535da19795d85376ae1397d161329e3b06fc47d9a5a68cd9be2cd7ecee0f2a`, extraite dans
  `data/raw/external/CICIDS2017-WTMC2021/csv/` (5 fichiers journaliers, 2 100 814 flux,
  84 colonnes ; empreintes au `run_metadata.json`).
- Étiquettes : la version corrigée ajoute des flux « - Attempted » (attaque tentée sans
  effet). Ils sont **exclus** des deux classes.

## 3. Dispositif

- Runner : `run_e_cicids_wtmc2021_holdout.py` (empreinte au registre), qui importe sans
  modification le tirage, la lecture, l'assemblage, les métriques, la règle de décision, les
  cinq modèles et leurs hyperparamètres d'E-CICIDS-HOLDOUT-FIX ; plafonds 8 000 lignes par
  classe à l'entraînement et 4 000 au test ; graines 42 à 46.
- Scénarios, définis par leurs étiquettes : DDoS, PortScan, Bot (vendredi) ; Infiltration,
  WebAttacks (jeudi). Test : attaques du scénario et bénins de son jour. Entraînement :
  bénins des autres jours ; attaques de tous les autres scénarios, tous jours confondus.
  Écart au protocole d'origine : celui-ci excluait de l'entraînement le seul fichier du
  scénario, ici l'entraînement exclut tous les bénins du jour du scénario.
- Variables : colonnes du fichier moins Flow ID, Src IP, Src Port, Dst IP, Protocol,
  Timestamp et Label, pour rester proche des variables du CSV d'origine (qui contenait
  Destination Port, mais ni IP, ni port source, ni protocole, ni horodatage).
- Essai à blanc (`--dry-run`) exécuté avant ce dépôt : composition seulement (fichier
  `sample_composition.csv`), aucun modèle entraîné ni métrique calculée.

## 4. Règle de décision (identique à E-CICIDS-HOLDOUT-FIX)

Un modèle bat la règle si son F1 moyen sur les 25 évaluations dépasse celui de la
prédiction systématiquement positive de plus de 0,01 **et** s'il la dépasse sur au moins 4
scénarios sur 5. Décision : `au_moins_un_modele_bat_la_regle` ou
`aucun_modele_ne_bat_la_regle`. MCC et PR-AUC sont rapportés comme mesures secondaires.

## 5. Conséquences préfixées

- `aucun_modele_ne_bat_la_regle` : la réfutation de H4 sous son critère préenregistré tient
  sur la version corrigée de CICIDS2017 ; le manuscrit le dit et retire la réserve « CSV
  d'origine non corrigés » de ce résultat.
- `au_moins_un_modele_bat_la_regle` : le manuscrit rapporte que la réfutation dépend des
  défauts du jeu d'origine et révise le statut de H4.

## 6. Exécution

Lancée après la fin d'E-MULTIVM-SATURATION-DIAG, pour ne pas perturber ses mesures de débit
sur l'hôte.
