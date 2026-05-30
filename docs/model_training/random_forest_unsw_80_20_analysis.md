# Analyse du modele reseau RandomForest UNSWNB15 80/20

## Contexte experimental

Le modele `random_forest_network_unsw_80_20_sampled.joblib` a ete entraine pour
l'agent reseau a partir des fichiers CSV volumineux contenus dans
`data/raw/Datasets/UNSWNB15`.

Les fichiers exploites correspondent aux flux reseau DDoS suivants:

- `DrDoS_DNS_data_1_per.csv`
- `DrDoS_LDAP_data_2_0_per.csv`
- `DrDoS_MSSQL_data_1_3_per.csv`
- `DrDoS_NetBIOS_data_1_3_per.csv`
- `DrDoS_NTP_data_data_5_per.csv`
- `DrDoS_SNMP_data_1_3_per.csv`
- `DrDoS_SSDP_data_2_per.csv`
- `DrDoS_UDP_data_2_per.csv`
- `syn_data.csv`
- `UDPLag_data_2_0_per.csv`

L'ensemble a ete separe en `80 %` pour l'entrainement et `20 %` pour le test.
Comme les fichiers sont tres volumineux, le modele RandomForest a ete entraine
sur un echantillon equilibre du train, puis evalue par morceaux sur le test
complet.

## Artefact produit

Modele:

```text
models/random_forest_network_unsw_80_20_sampled.joblib
```

Caracteristiques de l'artefact:

```text
Type: RandomForestClassifier
Nombre d'arbres: 50
Nombre de features: 82
Lignes d'entrainement utilisees: 75 182
Normaux utilises: 25 182
Attaques utilisees: 50 000
Taille du modele: environ 0,851 Mo
```

Le modele sauvegarde contient:

- le classifieur `RandomForestClassifier`;
- la liste des colonnes de features;
- les metadonnees de l'experience.

## Resultats du test

Les resultats enregistres dans `data/random_forest_unsw_80_20_metrics.csv` sont:

```text
events: 1 474 193
anomalies detectees: 1 472 925
anomaly_rate: 0.999140
accuracy: 0.999931
precision: 0.999999
recall: 0.999932
f1: 0.999965
specificity: 0.998291
tp: 1 472 923
fp: 2
fn: 100
tn: 1 168
```

Ces resultats indiquent que le modele RandomForest detecte presque toutes les
attaques presentes dans le jeu de test, avec tres peu de faux positifs et tres
peu de faux negatifs.

## Comparaison avec Isolation Forest

Le modele reseau precedent base sur Isolation Forest avait donne les resultats
suivants sur le meme type d'experience:

```text
accuracy: 0.366605
precision: 0.505657
recall: 0.397571
f1-score: 0.445147
```

La comparaison montre une amelioration tres nette avec RandomForest:

```text
Isolation Forest -> F1-score: 0.445147
RandomForest     -> F1-score: 0.999965
```

Cette difference s'explique par la nature des deux approches. Isolation Forest
est un modele non supervise: il isole les comportements rares sans exploiter la
verite terrain. RandomForest est un modele supervise: il apprend directement la
frontiere entre trafic normal et trafic attaque a partir de la colonne `label`.

Pour les donnees reseau labellisees, RandomForest est donc plus adapte.
Isolation Forest reste utile comme baseline non supervisee et comme solution de
secours lorsque les labels ne sont pas disponibles.

## Critique et limites

Les performances du RandomForest sont tres elevees, mais elles doivent etre
interpretees avec prudence.

Le jeu de test est fortement desequilibre:

```text
Attaques reelles: 1 473 023
Normaux reels: 1 170
```

Cela signifie que la majorite des evenements du test sont des attaques. Dans ce
contexte, l'accuracy seule n'est pas suffisante pour juger le modele. Les
metriques les plus importantes sont donc le recall, le F1-score, la specificity
et la matrice de confusion.

Le modele reste neanmoins solide sur ce test:

- seulement `100` attaques ratees sur plus de `1,47 million`;
- seulement `2` faux positifs;
- `1168` evenements normaux correctement reconnus sur `1170`.

Une autre limite vient de l'entrainement: le modele a ete entraine sur un
echantillon de `75 182` lignes, et non sur l'integralite du train. Ce choix a
ete fait pour eviter les plantages memoire sur Colab. Pour une experience plus
complete, il serait possible d'augmenter progressivement l'echantillon ou de
tester des modeles optimises pour les gros volumes comme LightGBM ou XGBoost.

## Positionnement dans l'architecture Logminer

La strategie multi-modeles retenue devient:

```text
Windows / Security logs -> Isolation Forest Windows
HDFS                    -> Isolation Forest HDFS
BGL                     -> Isolation Forest BGL
Linux / syslog          -> Isolation Forest Linux
Reseau / DDoS           -> RandomForest reseau
Fallback inconnu        -> Isolation Forest general
```

Le RandomForest ne remplace donc pas tous les modeles existants. Il devient le
meilleur candidat pour l'agent reseau, car les donnees reseau utilisees sont
labellisees et tabulaires.

## Formulation exploitable pour le memoire

Les premiers essais avec Isolation Forest ont confirme l'interet d'une approche
non supervisee pour la detection d'anomalies, mais ses performances sur les
flux reseau labellises restent limitees. Sur le jeu de test reseau, Isolation
Forest obtient un F1-score de `0.445147`, tandis que le RandomForest atteint un
F1-score de `0.999965`.

Cette amelioration s'explique par l'utilisation des labels disponibles dans le
dataset reseau. Le RandomForest apprend directement la distinction entre trafic
normal et trafic attaque a partir des variables numeriques de flux, alors
qu'Isolation Forest se limite a rechercher les observations atypiques.

Ainsi, RandomForest est retenu comme meilleur candidat pour l'agent reseau
labellise, tandis qu'Isolation Forest reste conserve comme baseline
non supervisee et comme modele de secours pour les sources non labellisees.
