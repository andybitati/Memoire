# Tableau de vérification des références (agent 6)

Date de vérification : 4 novembre 2026. Chaque ligne indique la source consultée. « PDF lu » signifie que les pages concernées du document ont été lues directement (et non un résumé).

## Références nouvelles (fichier `references_proposees.bib`)

| Clé | Référence | Vérifiée par | Statut |
|---|---|---|---|
| `smith1980contract` | R. G. Smith, « The Contract Net Protocol: High-Level Communication and Control in a Distributed Problem Solver », *IEEE Trans. Computers*, C-29(12), 1104–1113, déc. 1980, DOI 10.1109/TC.1980.1675516 | Crossref (api.crossref.org/works/10.1109/TC.1980.1675516 : revue, volume, numéro, pages, déc. 1980) ; IEEE Xplore 1675516 ; ACM DL | Confirmée. Prénom « Reid G. » d'après IEEE Xplore et les usages bibliographiques ; à contrôler une fois sur IEEE Xplore si le jury exige l'exactitude du prénom. |
| `fipa2002contractnet` | FIPA, *Contract Net Interaction Protocol Specification*, SC00029H, Standard, 2002-12-03 | PDF lu (compilation des IP FIPA, eecis.udel.edu/~decker/.../FIPA-ips.pdf, p. 28–30 : diagramme et explication du flux) ; page fipa.org/specs/fipa00029 (répond 403 au fetch automatique, référencée par la recherche) | Confirmée. Actes : `cfp`, `refuse`, `propose`, `reject-proposal`, `accept-proposal`, `failure`, `inform-done`, `inform-result` ; date limite via `reply-by` ; `conversation-id` obligatoire. |
| `fipa2002aclmessage` | FIPA, *ACL Message Structure Specification*, SC00061G, Standard, 2002-12-03 | fipa.org/specs/fipa00061/SC00061G.html (résultat de recherche : 13 paramètres, seul `performative` obligatoire) | Confirmée (titre, numéro, date, statut). |
| `fipa2002cal` | FIPA, *Communicative Act Library Specification*, SC00037J, Standard, 2002-12-03 | fipa.org/specs/fipa00037/SC00037J.html (résultat de recherche) ; renvoyée comme [FIPA00037] par SC00029H (PDF lu) | Confirmée. |
| `wooldridge2009introduction` | M. Wooldridge, *An Introduction to MultiAgent Systems*, 2ᵉ éd., John Wiley & Sons, 2009, ISBN 978-0-470-51946-2 | Page de l'auteur (cs.ox.ac.uk/people/michael.wooldridge/pubs/imas/ : « Published May 2009 by John Wiley & Sons, ISBN-13 978-0470519462 ») ; page Wiley | Confirmée. |
| `cic2018csecicids` | CIC/CSE, « CSE-CIC-IDS2018 on AWS », UNB | Page unb.ca/cic/datasets/ids-2018.html (lue) | Confirmée. **Point important** : la page demande de citer Sharafaldin, Habibi Lashkari, Ghorbani, ICISSP 2018, c'est-à-dire la même publication que CICIDS2017 (`sharafaldin2018cicids`, déjà présente). Il n'existe pas d'article distinct décrivant IDS2018 que les auteurs demandent de citer ; la page de distribution est donc ajoutée comme `@misc`. |
| `he2016experience` | S. He, J. Zhu, P. He, M. R. Lyu, « Experience Report: System Log Analysis for Anomaly Detection », ISSRE 2016, 207–218, DOI 10.1109/ISSRE.2016.21 | Crossref (api.crossref.org/works/10.1109/ISSRE.2016.21) | Confirmée. |
| `le2022logbased` | V.-H. Le, H. Zhang, « Log-based Anomaly Detection with Deep Learning: How Far Are We? », ICSE 2022, 1356–1367, DOI 10.1145/3510003.3510155 | Crossref (api.crossref.org/works/10.1145/3510003.3510155) ; PDF lu (arXiv:2202.04301, p. 5–7, tableaux 1, 2, 4) | Confirmée. |
| `landauer2023deep` | M. Landauer, S. Onder, F. Skopik, M. Wurzenberger, « Deep learning for anomaly detection in log data: A survey », *Machine Learning with Applications* 12, 100470, 2023, DOI 10.1016/j.mlwa.2023.100470 | Recherche (arXiv:2207.03820 ; ScienceOpen) ; le DOI résout vers Elsevier (PII S2666827023000233) | Confirmée (Crossref a renvoyé 429 ; DOI résolu). |
| `yu2024deep` | B. Yu et al., « Deep Learning or Classical Machine Learning? An Empirical Study on Log-Based Anomaly Detection », ICSE 2024, art. 35, DOI 10.1145/3597503.3623308 | Recherche (ACM DL, Semantic Scholar) ; ACM et Crossref ont refusé le fetch (403/429) | Confirmée pour auteurs, titre, venue, DOI ; pagination « art. 35, 13 p. » d'après la notice ACM indexée — à recontrôler si nécessaire. |
| `arp2022dos` | D. Arp et al., « Dos and Don'ts of Machine Learning in Computer Security », USENIX Security 2022, 3971–3988 | Recherche (UCL Discovery, KCL, Turing Institute, arXiv:2010.09470) | Confirmée. |

## Références demandées déjà présentes dans `references.bib`

| Demande | Clé existante | Vérification | Remarque |
|---|---|---|---|
| CICIDS2017 | `sharafaldin2018cicids` | Page unb.ca/cic/datasets/ids-2017.html (lue) | Correcte. Sert aussi de référence officielle pour CSE-CIC-IDS2018. |
| Loghub | `zhu2023loghub` | Entrée cohérente (ISSRE 2023, DOI 10.1109/ISSRE59848.2023.00071) | Non revérifiée en ligne au-delà de l'existant. |
| Drain (He et al. 2017) | `he2016drain` | ICWS 2017, DOI 10.1109/ICWS.2017.13 | La clé contient « 2016 » mais l'entrée indique 2017 : sans incidence sur le rendu (`plain` affiche le champ `year`). |
| DeepLog | `du2017deeplog` | PDF lu (users.cs.utah.edu/~lifeifei/papers/deeplog.pdf, p. 9–10) | Chiffres utilisés dans PATCH_NOTES. |
| LogBERT | `guo2021logbert` | PDF lu (arXiv:2103.04475, p. 7–8, tableau 2) | Chiffres utilisés dans PATCH_NOTES. |

## Références examinées mais non retenues

| Élément | Raison |
|---|---|
| Tableau de résultats du dépôt GitHub `logpai/loglizer` (p. ex. Isolation Forest F1 0,802 sur HDFS) | README logiciel, protocole de partition non documenté : non citable comme résultat publié. |
| Valeur LogAnomaly HDFS de Le & Zhang (2022), tableau 4 (P 0,886 ; R 0,893 ; F1 0,966) | Incohérence interne telle qu'imprimée (la moyenne harmonique de 0,886 et 0,893 vaut environ 0,889) : à ne pas citer. |
