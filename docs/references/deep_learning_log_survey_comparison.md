# Analyse Critique - Reference Deep Learning For Anomaly Detection In Log Data

Reference analysee:

> Max Landauer, Sebastian Onder, Florian Skopik, Markus Wurzenberger,
> *Deep Learning for Anomaly Detection in Log Data: A Survey*, Machine Learning
> with Applications, 2023.

Ce document compare la reference avec le travail realise dans Logminer/TFE.

## Nature De La Reference

L'article est une revue systematique de la litterature. Il ne propose pas un
outil operationnel unique, mais analyse les approches existantes de detection
d'anomalies dans les logs avec deep learning.

Les dimensions principales etudiees sont:

- architectures deep learning: RNN, LSTM, Bi-LSTM, GRU, CNN, Autoencoders,
  GAN, Transformers, attention;
- pretraitement: parsing, log keys, templates, tokenisation, embeddings,
  sequences, count vectors;
- modes d'apprentissage: supervise, semi-supervise, non supervise;
- techniques de detection: prediction du prochain evenement, reconstruction,
  scores, seuils, top-k;
- datasets d'evaluation: HDFS, BGL, Thunderbird, OpenStack, Hadoop;
- metriques: precision, recall, F1-score, accuracy, false positive rate.

L'article insiste aussi sur des limites recurrentes:

- dependance excessive a quelques datasets publics;
- reproductibilite imparfaite;
- manque d'evaluation en contexte operationnel;
- difficulte de traiter des logs heterogenes et instables;
- besoin d'explicabilite et d'adaptation aux changements.

## Points Communs Avec Notre Travail

| Axe | Reference | Travail Logminer/TFE |
| --- | --- | --- |
| Detection d'anomalies dans les logs | Sujet central | Sujet central |
| Utilisation HDFS/BGL | Datasets frequents dans la litterature | HDFS/BGL utilises pour validation |
| Deep learning | LSTM, Autoencoders, Transformers, etc. | LSTM TensorFlow/PyTorch et Autoencoder MLP |
| Modeles non supervises/semi-supervises | Fortement discutes | Isolation Forest, k-Means, LOF, One-Class SVM, Autoencoder |
| Pretraitement des logs | Parsing, templates, tokenisation, embeddings | Parsing multi-format, normalisation CSV, features ML |
| Evaluation quantitative | Precision, recall, F1, accuracy | Precision, recall, F1, accuracy, specificity, TP/FP/FN/TN |
| Seuils et scores | Seuils, top-k, scores d'anomalie | Seuils, z-score, IQR, histogramme, entropie, score multicritere |
| Sequences d'evenements | Point fort des RNN/LSTM | Prototype LSTM sur signal evenement/source/severite |
| Limites des labels | Soulignees | HDFS/BGL labellises, Windows non labellise, simulation avec labels injectes |

Notre travail s'inscrit donc clairement dans le meme champ scientifique.

## Differences Principales

### 1. Revue Scientifique Vs Prototype Operationnel

La reference analyse la litterature et classe les approches. Elle ne construit
pas une chaine complete de collecte, parsing, detection, correlation et
visualisation.

Notre travail, lui, produit un prototype executable:

- collecte Windows;
- parsing/normalisation;
- detection multi-modeles;
- correlation en incidents;
- dashboard;
- bus local entre agents;
- sauvegarde `joblib` pour entrainement cloud.

### 2. Deep Learning Central Vs Approche Hybride

La reference est centree sur le deep learning. Elle montre que les RNN/LSTM sont
tres presents dans la litterature, notamment a partir de DeepLog.

Notre approche est hybride:

- methodes traditionnelles: regles, seuils, entropie;
- statistiques: z-score, IQR, histogramme;
- machine learning: Isolation Forest, k-Means, One-Class SVM, LOF;
- deep learning leger: Autoencoder MLP, LSTM TensorFlow/PyTorch;
- ensembles: `ensemble_global`, `ensemble_selected`.

Cette difference est importante: le TFE ne suppose pas que le deep learning est
toujours le meilleur choix. Il compare aussi les methodes simples, rapides et
explicables.

### 3. Pretraitement Par Log Keys Vs Schema Normalise Multi-Format

Beaucoup d'approches de la litterature transforment les logs en `log keys` ou
templates, puis apprennent des sequences de templates.

Logminer adopte une autre strategie:

- detection du format;
- parsing specialise;
- normalisation vers un schema commun;
- extraction de features numeriques/categorielles;
- conservation du message brut.

Cela rend le systeme plus generaliste pour des sources heterogenes:

- Windows Event;
- HDFS;
- BGL;
- Linux/Syslog;
- tcpdump/reseau;
- Apache/autres formats prevus.

### 4. Evaluation De La Litterature Vs Validation Locale Reproductible

La reference souligne que beaucoup de travaux utilisent HDFS/BGL et des
metriques comme F1, precision et recall.

Notre travail reproduit cette logique, mais avec un pipeline executable:

- `validation_hdfs.csv`;
- `validation_bgl.csv`;
- `validation_simulated_windows.csv`;
- `validation_hdfs_metrics.csv`;
- `validation_bgl_metrics.csv`;
- `validation_simulated_windows_metrics.csv`;
- `validation_selection_summary.csv`.

Nous ajoutons aussi:

- `memory_peak_mb`;
- `duration_sec`;
- `adaptability_score`;
- `selection_score`;
- matrice de confusion.

Ces criteres repondent directement a l'objectif 2 du memoire: choisir selon la
precision, le temps, l'adaptation et la consommation memoire.

### 5. Datasets Publics Vs Logs Windows Reels

La reference se concentre surtout sur des datasets publics connus:

- HDFS;
- BGL;
- Thunderbird;
- OpenStack;
- Hadoop.

Notre travail ajoute une dimension locale et pratique:

- collecte reelle de journaux Windows depuis `C:\Windows\System32\winevt\Logs`;
- traitement des copies `.evtx`;
- detection sur `windows_copies_pipeline.csv`;
- anomalies candidates et incidents;
- logs simules Windows avec anomalies injectees.

Cet ajout est un apport important, car il rapproche la recherche de la realite
d'une machine Windows concrete.

## Apport Specifique Du Travail Logminer/TFE

### 1. Chaine Complete Multi-Agent

L'apport principal n'est pas seulement un modele IA. C'est une chaine complete:

```text
collecte -> parsing -> normalisation -> detection -> correlation -> dashboard
```

Cette chaine est structuree en agents:

- collecteur;
- parseur;
- normaliseur;
- detecteur;
- correlateur;
- visualiseur.

La reference discute les methodes de detection, mais ne fournit pas cette
architecture multi-agent operationnelle.

### 2. Comparaison Plus Large Que Le Deep Learning

Le travail compare:

- regles;
- seuils;
- entropie;
- z-score;
- IQR;
- histogramme;
- Isolation Forest;
- k-Means;
- One-Class SVM;
- LOF;
- Autoencoder;
- LSTM;
- ensembles.

Cela permet de montrer que des methodes simples peuvent etre tres competitives
sur certains datasets, ce que la reference mentionne indirectement en parlant
des benchmarks classiques, mais sans construire une grille locale unifiee.

### 3. Selection Multicritere

La reference insiste sur les evaluations, mais signale que les travaux ne
considerent pas toujours assez les contraintes pratiques.

Notre travail introduit un score de selection:

```text
selection_score = qualite + temps + memoire + adaptabilite
```

Ce score evite de choisir un modele uniquement sur F1-score. Pour un systeme de
surveillance, un modele leger, adaptable et rapide peut etre preferable a un
modele legerement plus precis mais couteux.

### 4. Preparation Pour Le Cloud

Le projet integre:

- dossier `cloud_upload/logminer_cloud_data`;
- separation `train/`, `validation/`, `metadata/`;
- fusion de datasets avec `build_cloud_training_dataset.py`;
- sauvegarde des modeles avec `joblib`;
- inference locale avec `--model-in`.

Cela donne une strategie pratique:

```text
entrainement lourd sur cloud -> modele joblib -> inference locale Windows
```

Cette dimension de deploiement n'est pas l'objet de la revue, mais elle apporte
une valeur concrete au TFE.

### 5. Visualisation Et Exploitabilite Humaine

Le dashboard Logminer presente:

- evenements;
- anomalies;
- incidents;
- messages agents;
- resultats de validation.

La reference parle de detection, mais pas de presentation operationnelle des
alertes pour un analyste. Notre travail ajoute donc une couche d'exploitation.

## Analyse Critique De Notre Travail Par Rapport A La Reference

### Forces

- Le prototype est executable et couvre toute la chaine d'analyse.
- Il combine methodes traditionnelles, ML et deep learning.
- Il utilise les datasets de reference HDFS/BGL.
- Il ajoute des journaux Windows reels et des logs simules.
- Il mesure plus que la precision: temps, memoire, adaptabilite.
- Il prepare l'entrainement cloud et la reutilisation locale.

### Limites

- Le LSTM implemente reste simple par rapport aux approches type DeepLog,
  LogAnomaly ou LogBERT.
- Le systeme ne construit pas encore de vrais embeddings semantiques ou
  template2Vec.
- Les sequences temporelles sont encore rudimentaires.
- La validation HDFS/BGL utilise des echantillons equilibres, pas encore le
  dataset complet.
- Les logs Windows reels ne sont pas labellises; ils servent surtout a
  l'entrainement non supervise et a la demonstration.
- Le dashboard est local; les agents ne sont pas encore exposes comme services
  distribues FastAPI/Redis/MQTT.

## Positionnement Scientifique

Le travail Logminer/TFE peut etre positionne comme une contribution appliquee:

> Alors que la litterature recente explore surtout des architectures deep
> learning sophistiquees pour la detection d'anomalies dans les logs, ce travail
> propose un prototype multi-agent complet, combinant methodes traditionnelles,
> machine learning, deep learning leger et selection multicritere, avec une
> attention particuliere a la normalisation multi-format, a l'exploitation
> humaine et au deploiement cloud/local.

## Conclusion

La reference justifie scientifiquement l'interet du deep learning pour les logs,
en particulier les approches sequence comme LSTM/RNN et les Autoencoders.

Notre travail reprend ces idees, mais les replace dans un systeme plus large:

- ingestion multi-source;
- agents specialises;
- detection comparative;
- evaluation supervisée et simulée;
- correlation en incidents;
- dashboard;
- entrainement cloud et inference locale.

L'apport du TFE n'est donc pas de battre tous les modeles de la litterature,
mais de construire une architecture integree, reproductible et exploitable,
capable de comparer plusieurs familles de methodes et de choisir un compromis
realiste entre precision, cout, adaptabilite et lisibilite.

