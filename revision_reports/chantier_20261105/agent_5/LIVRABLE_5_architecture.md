# Livrable 5 — Architecture multi-agents : preuves et limites

## 1. Périmètre et sources

Périmètre : §3.5.1, §4.9 à §4.11, résumés, §5.7, plus les points C5 de l'Agent 5 (benchmark sans chiffres, endurance « preuve directe », politique comparée à un ordonnanceur déterministe, distribution de la décision seule).

Sources : `RETOURS_LECTEURS.md` ; `src/logminer/agents/contract_net.py` ; `src/logminer/agents/intelligent_runtime.py` ; `experiments/phase_multi_agent/aggregated/ma_20260909T160812Z_34016__statistics.csv` et `__paired_memory_effects.csv` ; `experiments/phase_revision_20261105/E-H5-MEMORY-RELIABILITY/` ; `experiments/phase_revision_20261105/E-CNP-STATIC-ASSIGNMENT/`.

## 2. Synthèse

| Revendication | Verdict | Preuve |
|---|---|---|
| Les agents coûtent cher sur microtâches | Établi : A traite 55 à 72 fois plus de tâches/s que C et D | `__statistics.csv`, tableau `tab:benchmark-debit` |
| La mémoire apporte un gain | Conditionnel : établi seulement pour p = 0,9 | E-H5, tableau `tab:e-h5` |
| Contract Net bat une table statique | Conditionnel, et instable sur deux scénarios | E-CNP, tableau `tab:e-cnp` ; E-CNP-LEAST-LOADED |
| La négociation apporte un avantage propre | **Non établi : défavorable sur les quatre scénarios face au moindre chargé** | E-CNP-LEAST-LOADED, tableau `tab:e-cnp-moindre` |
| Idempotence propre aux agents | Non : transposable à A et B | `tab:panne-appariee` |
| Réattribution propre aux agents | Non : relève du transport et de l'orchestrateur | Agent 3, discussion « Reprise, livraison et idempotence » |
| Distribution de la charge | Non démontrée : 1,23 % en saturation, 0 % en HDFS distribué | §4.11 |
| Auditabilité | Non mesurée : des traces existent, leur valeur pour un audit n'a pas été testée | conclusion corrigée |

## 3. E-H5 : mémoire sous fiabilité hétérogène

Protocole : `protocoles/E-H5-MEMORY-RELIABILITY.md`, commit `658e639`. Manifeste 8/8 vérifié. Décision préenregistrée : **`gain_conditionnel`**.

| p | Échec initial C | D | Delta D − C [IC 95 %] | Rapport de débit [IC 95 %] | Gain |
|---|---:|---:|---|---|---|
| 0,3 | 0,1096 | 0,1069 | −0,0027 [−0,0086 ; 0,0031] | 0,972 [0,954 ; 0,991] | non |
| 0,6 | 0,2405 | 0,2103 | −0,0302 [−0,0389 ; −0,0215] | 0,975 [0,942 ; 1,008] | non (garde-fou de débit) |
| 0,9 | 0,3729 | 0,0736 | −0,2993 [−0,3138 ; −0,2848] | 1,210 [1,194 ; 1,225] | oui |

Conséquence préfixée par le protocole : **H5 passe de RÉFUTÉE à NON TRANCHÉE**, avec gain de mémoire conditionnel. Le statut favorise H5 par rapport à l'état antérieur ; il résulte de la règle écrite avant l'exécution, non d'un choix après lecture. H5 n'est pas déclarée soutenue : la priorisation des anomalies n'est pas mesurée et aucun cycle de promotion n'est éprouvé.

Lecture à ne pas surestimer :

- La confiance déclarée est volontairement fausse. Le gain mesure la correction d'une déclaration erronée, non un apprentissage général.
- L'indice de Jain recule à p = 0,9 (−0,037 [−0,041 ; −0,033]).
- La sensibilité séquentielle (hors décision) montre un effet bien plus fort à tous les niveaux, mais une forte concentration (Jain −0,37 à −0,41). L'explication par fixation sur le premier agent qui réussit vient de la lecture du code et de la répartition observée ; elle n'a pas été testée séparément.

## 4. E-CNP : Contract Net contre table statique

Protocole : `protocoles/E-CNP-STATIC-ASSIGNMENT.md`, commit `472d5e7`. Manifeste 8/8 vérifié. Décision préenregistrée pour C − table : **`avantage_conditionnel`** (s2, s3, s4 favorables ; s1 défavorable). D − table : `avantage_conditionnel` (s2, s3 favorables ; s1 défavorable ; s4 indéterminé).

| Scénario | Débit table / C | C/table [IC 95 %] | Échec initial table / C | Échecs finaux table / C / D | Décision C / D |
|---|---|---|---|---|---|
| s0 coût pur | 13 283 / 2 704 | 0,211 [0,193 ; 0,229] | 0 / 0 | 0 / 0 / 0 | hors règle |
| s1 nominal | 1 103 / 956 | 0,867 [0,856 ; 0,878] | 0 / 0 | 0 / 0 / 0 | défavorable / défavorable |
| s2 p = 0,3 | 856 / 865 | 1,011 [1,001 ; 1,020] | 0,2971 / 0,1095 | 0 / 4 / 8 | favorable / favorable |
| s3 panne silencieuse | 825 / 801 | 0,971 [0,964 ; 0,977] | 0,3500 / 0,2101 | 0 / 0 / 50 | favorable / favorable |
| s4 gamma lent | 636 / 736 | 1,157 [1,149 ; 1,165] | 0 / 0 | 0 / 0 / 0 | favorable / indéterminé |

### Réserves à conserver avec cette décision

1. **Le protocole surestime ce qu'il isole.** Il écrit que le contraste C − table « isole la négociation ». Les résultats montrent que c'est inexact : C n'a pas de mémoire, ignore les échecs, et ses gains accompagnent l'étalement dû au terme de charge (nominal : C 33,3 % par agent ; table 25,0 / 25,7 / 49,3 %). La table testée n'observe pas la charge. Ce point a depuis été tranché : voir §4 bis. La décision préenregistrée est rapportée telle quelle, et l'écart d'interprétation est consigné au registre.
2. **Le plan d'injection favorise structurellement l'étalement.** s2, s3 et s4 visent les agents que la table sollicite le plus. Le protocole l'énonçait, mais sa conséquence n'a été mesurée qu'après exécution (analyse descriptive des parts d'exécution, non préenregistrée).
3. **Faiblesse de Contract Net révélée.** La table ne perd aucune tâche ; Contract Net en perd (4 et 8 en s2, 50 pour D en s3, sur 30 000). Cause d'après le code : un agent occupé lors de l'appel d'offres ne propose pas et n'entre pas dans la liste de repli (`contract_net.py`, boucle sur `ranked`). Le code n'a pas été modifié : ce comportement est un résultat.

## 4 bis. E-CNP-LEAST-LOADED : la négociation contre le moindre chargé

Protocole : `protocoles/E-CNP-LEAST-LOADED.md`, commit `6db45dd`, décidé après lecture d'E-CNP. Manifeste 9/9 vérifié. Décision préenregistrée pour C − répartiteur : **`aucun_avantage`**.

| Scénario | Débit répartiteur / C | C/répartiteur [IC 95 %] | Échec initial répartiteur / C | Décision |
|---|---|---|---|---|
| s0 coût pur | 8 402 / 2 598 | 0,321 [0,298 ; 0,343] | 0 / 0 | hors règle |
| s1 nominal | 1 098 / 955 | 0,870 [0,857 ; 0,883] | 0 / 0 | défavorable |
| s2 p = 0,3 | 962 / 824 | 0,859 [0,821 ; 0,897] | 0,1093 / 0,1094 | défavorable |
| s3 panne silencieuse | 882 / 783 | 0,890 [0,869 ; 0,912] | 0,2103 / 0,2099 | défavorable |
| s4 gamma lent | 832 / 733 | 0,881 [0,868 ; 0,894] | 0 / 0 | défavorable |

- La prise en compte de la charge suffit : répartiteur − table est favorable sur s2, s3 et s4, indéterminé sur s1.
- **Non-reproduction :** sur les nouvelles graines, C − table passe de favorable à indéterminé sur s2 et s3. La baisse des échecs est stable ; c'est le garde-fou de débit qui échoue (bornes 0,935 et 0,939).
- Réserve : le répartiteur lit l'état des agents sans coût ; l'exécution distribuée, non testée, est la dernière condition où la négociation pourrait regagner un avantage.

## 5. Avis et décisions

| # | Décision | Justification |
|---|---|---|
| A5-1 | C6, campagne de 60 tâches : **option A définitive** ; l'option B de l'Agent 1 n'est pas appliquée. | La revendication de refus n'est pas nécessaire : §5.7 ne l'affirme plus. L'artefact reste disponible pour la soutenance. |
| A5-2 | « Preuve directe de l'endurance » retirée ; la charge de 0,5 tâche/s est située par rapport à la capacité mesurée. | L2 §2.4 : 16 à 32 fois sous le coude de saturation. |
| A5-3 | Trace de messages déplacée de la section HDFS distribuée vers la campagne d'endurance. | LIVRABLE_1 §6 : paragraphe mal placé. |
| A5-4 | Tableau de débit avec IC ajouté au benchmark ; D − C chiffré. | L2 §2.4 : ni chiffre, ni barre d'erreur. |
| A5-5 | Résumés fondés sur les versions de l'Agent 2, amendées pour E-H4, E-H5 et E-CNP. | C7, C8 : tout chiffre figure dans le corps. |

## 6. Sections et intégration

Sections dans `agent_5/sections/` : benchmark, E-H5 et E-CNP, baselines par jeu, trois résumés. Lot **A5-a intégré** (voir `ETAT_CHANTIER.md`).

## 7. Points en suspens

- **Bokuse** : les phrases nouvelles en lingala ont été rédigées sans relecture par un locuteur. À valider par l'auteur (D3).
- Coût sur tâches réelles : E-CNP utilise des tâches de 2 et 10 ms ; aucune inférence réelle n'est comparée.
- Comparateurs non testés : Celery, Kafka, moteur de workflow, exécution distribuée.

=== PASSATION ===
Agent : 5 — Architecture multi-agents
Statut : terminé
Livrables : `agent_5/LIVRABLE_5_architecture.md`, `agent_5/protocoles/`, `agent_5/scripts/run_e_h5_e_cnp.py`, `agent_5/sections/`, artefacts sous `experiments/phase_revision_20261105/`
Prochain agent recommandé : 7 — Forme
Raison : les agents de fond sont clos, sous réserve des compléments restants de l'Agent 4 consignés dans `ETAT_CHANTIER.md`.
Points de vigilance pour le repreneur : ne pas citer l'avantage conditionnel d'E-CNP sans E-CNP-LEAST-LOADED ; H5 est NON TRANCHÉE et non soutenue ; faire relire le lingala.
=== FIN PASSATION ===
