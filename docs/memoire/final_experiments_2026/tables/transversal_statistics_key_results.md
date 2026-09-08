| Expérience | Dataset/scénario | Méthode | N | Moyenne F1 | Écart-type | Médiane | Min | Max | IC95 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| CICIDS scenario holdout | CICIDS2017 local copy/DDoS | LogisticRegression | 5 | 0.720357 | 0.000000 | 0.720357 | 0.720357 | 0.720357 | [0.720357; 0.720357] |
| CICIDS scenario holdout | CICIDS2017 local copy/DDoS | RandomForest | 5 | 0.778774 | 0.001342 | 0.779371 | 0.776384 | 0.779558 | [0.777107; 0.780441] |
| CICIDS random stratified control | CICIDS2017 local copy/RandomStratified | RandomForest | 5 | 0.995142 | 0.001013 | 0.995493 | 0.993859 | 0.996372 | [0.993884; 0.996401] |
| Strict train-only Drain3 | HDFS/chronological train-validation-test | EnsembleTrainCalibrated | 5 | 0.242946 | 0.010487 | 0.245931 | 0.226230 | 0.254682 | [0.229924; 0.255967] |
| Strict train-only Drain3 | HDFS/chronological train-validation-test | Histogram | 1 | 0.269307 | N/A | 0.269307 | 0.269307 | 0.269307 | N/A |
| Strict train-only Drain3 | BGL/chronological train-validation-test | AutoencoderMLP | 5 | 0.278511 | 0.000997 | 0.278045 | 0.277885 | 0.280245 | [0.277273; 0.279749] |
| Strict train-only Drain3 | BGL/chronological train-validation-test | Histogram | 1 | 0.913698 | N/A | 0.913698 | 0.913698 | 0.913698 | N/A |
