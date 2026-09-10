# Carte de données — CSE-CIC-IDS2018

## Identité et provenance

- Nom : CSE-CIC-IDS2018.
- Producteurs : Communications Security Establishment et Canadian Institute
  for Cybersecurity, Université du Nouveau-Brunswick.
- Source officielle : https://www.unb.ca/cic/datasets/ids-2018.html
- Stockage officiel utilisé : `s3://cse-cic-ids2018/`, région AWS
  `ca-central-1`.
- Date de récupération locale : 10 septembre 2026.
- Licence indiquée par la source : redistribution et miroir autorisés sous
  réserve de citer le dataset et sa page officielle.
- Référence demandée par la source : I. Sharafaldin, A. H. Lashkari et
  A. A. Ghorbani, « Toward Generating a New Intrusion Detection Dataset and
  Intrusion Traffic Characterization », ICISSP, 2018.

## Copies locales utilisées

| Partition | Objet officiel | Taille locale | SHA-256 local |
| --- | --- | ---: | --- |
| Train | `Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv` | 375 945 899 octets | `fa2947a8256d81ee9103ae16139d62d0e17aa23e696ee80d9e76fb51c01c9c4b` |
| Test | `Friday-16-02-2018_TrafficForML_CICFlowMeter.csv` | 333 723 605 octets | `1a4919faa0c49c7af97230b0c2d076eba23ee6dd81103a3801d51ac316355d8b` |

Les tailles correspondent aux valeurs `Content-Length` obtenues directement
sur les objets AWS officiels. Les ETag multipart et les URL exactes sont
conservés dans le manifeste du run.

Exact match des objets officiels téléchargés : **OUI**, pour les deux objets
identifiés ci-dessus, sur la base de la récupération directe, de la taille et
du SHA-256 local nouvellement calculé. Aucun hash SHA-256 publié par le
producteur n’a été trouvé pour effectuer une comparaison avec une somme de
contrôle officielle indépendante.

## Structure et utilisation

- Format : CSV de flux réseau CICFlowMeter-V3.
- Taille publique annoncée pour l’ensemble du dataset : INFORMATION À VÉRIFIER.
- Granularité des labels : flux réseau.
- Unité de prédiction : flux réseau.
- Classes utilisées : `Benign` contre toute étiquette DoS observée.
- Apprentissage : journée du 15 février 2018, attaques GoldenEye et Slowloris.
- Test : journée du 16 février 2018, attaques SlowHTTPTest et Hulk.
- Caractéristiques : intersection de 78 colonnes numériques.
- Exclusions : label, timestamp et identifiants réseau textuels.
- Prétraitement : valeurs non finies remplacées par zéro, bornage dans
  `[-1e12, 1e12]`; `StandardScaler` ajusté sur le train uniquement pour
  LogisticRegression.
- Sous-échantillonnage : pools stratifiés de 50 000 observations par classe,
  puis 10 000 par classe et par graine, sans remise. Les cinq graines partagent
  les pools parents.
- Utilisation dans Logminer : validation externe méthodologique de
  LogisticRegression et RandomForest; aucun modèle de production n’est promu.

## Limites

- Deux journées et quatre sous-scénarios DoS seulement.
- Échantillons équilibrés, donc prévalence non opérationnelle.
- Répétitions corrélées par les pools parents.
- Analyse de sensibilité aux doublons décidée après le résultat principal.
- Aucun transfert direct des poids CICIDS2017 vers CSE-CIC-IDS2018.
- Validité industrielle : NON DÉMONTRÉ.
