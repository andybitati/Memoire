# CSE-CIC-IDS2018 — validation externe légère

Run : `external_csecicids2018_20260910T230136Z`.

## Protocole

Le fichier officiel du 15 février 2018 est utilisé uniquement pour l’apprentissage; celui du 16 février est utilisé uniquement pour le test. Les scénarios DoS diffèrent entre les deux journées. Les timestamps ne sont pas des caractéristiques. Le seuil de décision reste fixé à `0,5` et aucun modèle n’est choisi sur le test.

## Résultats

| Modèle | F1 moyen | PR-AUC moyenne | MCC moyen | Rappel moyen | FPR moyen | N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| RandomForest | 0.4013747437 | 0.7215456902 | 0.0180090742 | 0.4192400000 | 0.4478800000 | 5 |
| LogisticRegression | 0.9992120133 | 0.9993577608 | 0.9984240141 | 1.0000000000 | 0.0015800000 | 5 |

La moyenne masque une instabilité importante du RandomForest : son F1 varie de
`0,1296053862` à `0,6223790404` selon la graine. À l’inverse, le F1 de la
régression logistique reste compris entre `0,9968598913` et `0,9998500225`.

## Audit des données

- lignes d’apprentissage balayées : `1048575` ;
- lignes de test balayées : `1048574` ;
- en-têtes répétés écartés : train `0`, test `1` ;
- caractéristiques numériques communes : `78` ;
- cinq graines sont évaluées, mais elles partagent les mêmes pools parents figés.

Les labels réellement observés sont :

- apprentissage : `996 077` Benign, `41 508` DoS attacks-GoldenEye et
  `10 990` DoS attacks-Slowloris ;
- test : `446 772` Benign, `139 890` DoS attacks-SlowHTTPTest et `461 912`
  DoS attacks-Hulk.

Les fichiers complets ont respectivement les SHA-256
`fa2947a8256d81ee9103ae16139d62d0e17aa23e696ee80d9e76fb51c01c9c4b` et
`1a4919faa0c49c7af97230b0c2d076eba23ee6dd81103a3801d51ac316355d8b`.

## Sensibilité aux vecteurs répétés

L’audit post hoc `external_csecicids2018_sensitivity_20260910T231423Z` trouve
`96 150` vecteurs uniques sur `100 000` dans le pool d’apprentissage et
`75 675` sur `100 000` dans le pool de test. Aucun vecteur exact n’est partagé
entre les deux partitions et aucun hash ne porte des labels contradictoires.

Après déduplication de l’apprentissage et du test, le F1 moyen vaut
`0,9988632299` pour LogisticRegression et `0,5472257978` pour RandomForest.
La performance linéaire n’est donc pas expliquée par les seuls vecteurs répétés.
Cette analyse reste exploratoire : elle a été décidée après observation du
résultat principal et ne le remplace pas.

## Interprétation autorisée

La campagne mesure la robustesse de deux familles de modèles légers face à un changement de journée et de sous-scénarios DoS dans un dataset officiel indépendant de CICIDS2017. Comme dans le holdout temporel CICIDS2017, LogisticRegression dépasse RandomForest. Seule cette conclusion méthodologique comparative est transférable.

## Limites

Elle ne constitue pas un transfert direct des poids appris sur CICIDS2017. Elle ne démontre pas une généralisation à toutes les attaques de CSE-CIC-IDS2018, ni une validité industrielle. Les sous-échantillons équilibrés ne reproduisent pas la prévalence opérationnelle.

Manifeste : `experiments/phase_dataset_strengthening/manifests/external_csecicids2018_20260910T230136Z_manifest.json`.
