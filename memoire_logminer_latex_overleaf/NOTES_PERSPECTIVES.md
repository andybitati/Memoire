# Notes Pour Perspectives

## HDFS/BGL : traitement leger par templates

Decision a conserver pour la suite : ne pas ouvrir un chantier LSTM ou deep
learning sequentiel dans ce memoire. Pour rester coherent avec l'esprit du
travail, HDFS et BGL doivent etre traites comme une famille de logs systemes
sequentiels necessitant un agent specialise leger.

Plan retenu :

- utiliser Drain comme methode principale d'extraction de templates ;
- citer Spell, IPLoM et LenMa comme alternatives legeres possibles ;
- transformer chaque ligne HDFS/BGL en `template_id` ;
- regrouper HDFS par `block_id` ;
- regrouper BGL par fenetre temporelle, noeud ou composant ;
- construire des features simples : longueur de sequence, templates distincts,
  templates rares, transitions rares, ratio erreurs/warnings, duree de fenetre ;
- appliquer des regles statistiques et Isolation Forest sur les features
  agregees ;
- eviter de fixer la contamination a partir du taux reel du test ;
- utiliser train, validation et test independants lorsque les donnees le
  permettent ;
- rapporter precision, rappel, F1, faux positifs et matrice de confusion.

Formulation a garder dans la redaction :

> Les resultats HDFS/BGL ne contredisent pas l'architecture Logminer ; ils
> montrent qu'une famille de journaux systemes sequentiels doit etre prise en
> charge par un agent specialise par templates et sequences legeres.
