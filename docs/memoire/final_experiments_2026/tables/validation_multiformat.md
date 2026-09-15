# Validation fonctionnelle multiformat

| Format | N brut | N parsé | N normalisé | Erreurs | Perdus | Taux parsing | Conservation message |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Windows Event | 1000 | 1000 | 1000 | 0 | 0 | 1.000 | 0.000 |
| Linux/auth tabulaire | 1000 | 1000 | 1000 | 0 | 0 | 1.000 | 1.000 |
| Wazuh/Elastic CSV | 1000 | 1000 | 1000 | 0 | 0 | 1.000 | 1.000 |
| Syslog Linux | 1000 | 1000 | 1000 | 0 | 0 | 1.000 | 0.000 |
| Apache access | 1 | 1 | 1 | 0 | 0 | 1.000 | 1.000 |
| HDFS | 1000 | 0 | 0 | 1000 | 1000 | 0.000 | 0.000 |
| BGL | 1000 | 0 | 0 | 1000 | 1000 | 0.000 | 0.000 |
| Flux réseau tabulaires | 1000 | 1000 | 1000 | 0 | 0 | 1.000 | n/a |

Statut : VALIDATION FONCTIONNELLE MULTIFORMAT. Ce tableau ne démontre pas une robustesse universelle.
