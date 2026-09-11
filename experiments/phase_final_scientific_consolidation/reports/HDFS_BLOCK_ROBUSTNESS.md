# Robustesse descriptive du résultat HDFS au niveau bloc

Run : `hdfs_block_robustness_20260911T002351Z`. Le test gelé contient `2000` blocs, dont `29` positifs. Le modèle, l’agrégateur `mean` et le seuil `1.2729429339548877` restent inchangés.

## Bootstrap par block_id

| Métrique | Médiane | Percentile 2,5 % | Percentile 97,5 % | IQR |
| --- | ---: | ---: | ---: | ---: |
| f1 | 0.894737 | 0.800000 | 0.961039 | 0.052185 |
| precision | 0.809524 | 0.666667 | 0.925000 | 0.085303 |
| recall | 1.000000 | 1.000000 | 1.000000 | 0.000000 |
| mcc | 0.897903 | 0.814008 | 0.961034 | 0.048713 |
| fpr | 0.003550 | 0.001514 | 0.006572 | 0.002013 |

Les intervalles sont descriptifs. Les réplications bootstrap ne constituent pas une preuve d’indépendance statistique.

## Retrait d’un bloc positif

Les 29 retraits donnent un F1 compris entre `0.888889` et `0.888889`, et un rappel compris entre `1.000000` et `1.000000`.

## Conclusion

Le score block-level reste variable sous les analyses de sensibilité réalisées.

Le F1 observé de `0,892308` décrit ce test gelé ; il ne doit pas être présenté comme une valeur exacte universelle de HDFS.
