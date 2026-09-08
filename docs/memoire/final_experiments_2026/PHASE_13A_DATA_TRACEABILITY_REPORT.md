# PHASE 13A — DATA TRACEABILITY REPORT

## 1. Objectif

Classer chaque source réellement utilisée, identifier les producteurs publics lorsque la preuve est disponible, et séparer l'identification d'une source publique de la vérification de la copie locale.

## 2. Méthode

Les copies locales ont été lues sans modification. Les comparaisons exactes utilisent SHA-256 sur des objets équivalents. Pour les archives, l'archive et les fichiers extraits sont suivis séparément. Le script `scripts/verify_public_dataset_copies.py` produit `public_dataset_copy_verification.csv`. Aucune expérience n'a été relancée.

## 3. Classification générale

Les corpus CICIDS2017, HDFS_v1, BGL, Linux_2k et UNSW-NB15 sont des sources publiques identifiées. HDFS.log, anomaly_label.csv et Linux_2k.log sont des copies locales exactement vérifiées. CICIDS2017 est fortement concordant par noms, structure, dimensions et contenu de l'archive locale, sans déclaration d'identité binaire avec le téléchargement officiel. BGL est identifié publiquement mais sa copie locale n'a pas reçu de comparaison complète de fichier public dans cette phase. Les journaux Windows et l'export Wazuh/Elastic sont locaux; Apache et la corrélation sont synthétiques.

## 4. CICIDS2017

La page officielle du Canadian Institute for Cybersecurity (University of New Brunswick) décrit CIC-IDS2017, sa période du 3 au 7 juillet 2017, ses flux CSV MachineLearningCSV et ses scénarios d'attaque. Les huit fichiers locaux ont 79 colonnes, les noms canoniques et les dimensions consignées dans le manifeste. L'archive locale `MachineLearningCSV.zip` contient exactement ces huit fichiers et chaque extrait correspond au fichier local par SHA-256. Le statut final est `PUBLIC_LOCAL_COPY_STRONGLY_MATCHED`, pas `EXACT_MATCH` avec la distribution distante.

## 5. HDFS_v1

L'archive officielle Loghub/Zenodo `HDFS_v1.zip` a été téléchargée temporairement; son MD5 publié `76a24b4d9a6164d543fb275f89773260` a été retrouvé. `HDFS.log` et `preprocessed/anomaly_label.csv` extraits ont chacun le même SHA-256 que les fichiers locaux. Le nombre de lignes de HDFS.log est 11 175 629. La vérité terrain est attachée aux traces/blocs identifiés par `block_id`; elle n'est pas une annotation indépendante de chaque ligne d'événement.

## 6. BGL

Loghub identifie BGL comme le journal Blue Gene/L et publie 4 747 963 lignes et 214,7 jours. La copie locale possède 4 747 963 lignes et le SHA-256 `666130…a5d2`. Le fichier public complet n'a pas été comparé dans le dépôt de preuve final; le statut reste `PUBLIC_LOCAL_COPY_MATCH_NOT_PROVEN`.

## 7. Linux_2k

Le fichier brut officiel `logpai/loghub/Linux/Linux_2k.log` a été téléchargé. La copie locale et la copie publique ont 2 000 lignes, 216 485 octets et le SHA-256 `b3e20bc1…e8e173`. Statut: `PUBLIC_LOCAL_COPY_EXACT_MATCH`.

## 8. UNSW-NB15 et distinction avec l'archive historique incorrecte

UNSW Research décrit les fichiers officiels et confirme 175 341 enregistrements d'entraînement et 82 332 de test. Les deux Parquet locaux ont ces nombres de lignes mais sont des conversions locales à 36 colonnes; leur identité avec les CSV officiels n'est pas prouvée. L'archive historique `UNSWNB15.zip` contient des familles DrDoS/UDPLag/SYN et reste exclue. Le score 0,999965 ne doit être attribué à aucun dataset public.

## 9. Données Windows locales

`Application.evtx` est un export EVTX local utilisé pour la validation multiformat. Il est classé `LOCAL_COLLECTION_DOCUMENTED`; aucun nom de poste ou identifiant personnel n'est requis dans le mémoire.

## 10. Linux/auth local ou autre origine vérifiée

`linux_auth_logs_labeled.csv` est un corpus CSV local étiqueté de 500 000 lignes et 11 colonnes. L'utilisation, le format et le hash sont connus; l'acquisition initiale n'est pas établie. Statut: `PARTIALLY_DOCUMENTED`.

## 11. Wazuh/Elastic local

`06-20-October.csv` est un export local Wazuh/Elastic de 4 953 enregistrements et 136 colonnes. Statut: `LOCAL_EXPORT_DOCUMENTED`.

## 12. Données synthétiques

`apache_access.log` est une fixture contrôlée d'une ligne. Les 19 événements de la phase 8 sont des scénarios synthétiques contrôlés avec vérité séparée. Statut: `SYNTHETIC_DOCUMENTED`.

## 13. Comparaisons de hashes

Les résultats reproductibles sont dans `public_dataset_copy_verification.csv`: HDFS.log, anomaly_label.csv et Linux_2k.log sont `PUBLIC_LOCAL_COPY_EXACT_MATCH`. Les autres sources publiques sont explicitement séparées entre concordance forte et correspondance non prouvée.

## 14. Sources bibliographiques

Les références primaires vérifiées sont Sharafaldin et al. (2018, DOI 10.5220/0006639801080116), Xu et al. (2009, DOI 10.1145/1629575.1629587), Oliner & Stearley (2007, DOI 10.1109/DSN.2007.103), Zhu et al. (2023, DOI 10.1109/ISSRE59848.2023.00071) et Moustafa & Slay (2015, DOI 10.1109/MilCIS.2015.7348942).

## 15. Informations toujours inconnues

L'acquisition historique de `UNSWNB15.zip` et l'origine initiale de `linux_auth_logs_labeled.csv` ne sont pas établies par le dépôt. La copie locale BGL n'a pas de hash public complet comparé dans cette phase.

## 16. Formulations autorisées pour Luna

Dire « source publique identifiée » lorsque la page producteur ou la publication le démontre; dire « copie locale exactement vérifiée » seulement pour les trois fichiers SHA-256 égaux; dire « copie fortement concordante » pour CICIDS2017; présenter les collectes/export locaux comme tels et les scénarios Apache/corrélation comme synthétiques.

## 17. Formulations interdites pour Luna

Ne pas dire que toutes les copies sont officielles bit à bit, que BGL local est exact, que le Parquet UNSW est l'original CSV, que `UNSWNB15.zip` est UNSW-NB15, ni que le score historique 0,999965 est un résultat scientifique final.

### Décision par source

Pour chaque ligne de `final_data_source_traceability.csv`, `category`, `traceability_status`, `evidence` et `notes` constituent la décision transmissible à Luna. Les résultats ne doivent pas être extrapolés à un environnement industriel.

