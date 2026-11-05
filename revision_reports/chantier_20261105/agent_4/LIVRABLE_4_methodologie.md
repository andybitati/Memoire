# Livrable 4 — Méthodologie expérimentale et baselines

## Synthèse

Les expériences complémentaires C13 sont terminées. Elles distinguent trois questions :

- E-H3 compare la décision du routeur à une table statique. Elle n'a pas été exécutée : le corpus local ne permet pas de constituer les 90 sources indépendantes prévues.
- E-H3b compare des modèles communs et spécialisés sous affectation parfaite de la famille. La non-infériorité n'est pas établie, car `linux_auth` échoue au critère préenregistré.
- E-H4 compare Histogram aux règles simples au niveau `block_id` HDFS. La meilleure baseline simple dépasse Histogram ; selon le critère préenregistré, le résultat est dominé par cette règle.

Les analyses et corrections antérieures de CICIDS2017, BGL, CSE-CIC-IDS2018 et corrélation sont détaillées dans `revision_reports/agent_4/PATCH_NOTES.md` et sont reprises dans les sections expérimentales du manuscrit.

## E-H3b — modèles communs et spécialisés

Le protocole `protocoles/E-H3B-FAMILY-MODELS.md` a été préenregistré avant l'exécution. Pour les familles CICIDS, Linux/auth et UNSW, un modèle Random Forest commun est comparé à un modèle par famille, dans le même espace de 17 variables et avec les mêmes hyperparamètres. Chaque graine utilise une partition stratifiée 75/25 et les deux variantes sont évaluées sur les mêmes 3 000 observations de test par famille. La famille correcte est donnée au modèle spécialisé : cette expérience isole la spécialisation du classifieur, pas la décision du routeur.

| Famille | F1 commun | F1 spécialisé | Delta apparié | IC à 95 % | Décision |
|---|---:|---:|---:|---:|---|
| CICIDS | 0,998999 | 0,999266 | +0,000268 | [−0,000476 ; 0,001011] | Non-infériorité établie |
| `linux_auth` | 0,822980 | 0,815454 | −0,007526 | [−0,012326 ; −0,002726] | Échec |
| UNSW | 0,993145 | 0,991880 | −0,001265 | [−0,002902 ; 0,000372] | Non-infériorité établie |

La marge était de −0,01 pour la borne inférieure de l'IC apparié de chaque famille. Comme `linux_auth` passe sous cette marge, le critère global de non-infériorité échoue. Le delta macro moyen est de −0,002841 (IC à 95 % : [−0,004705 ; −0,000977]), en faveur du modèle commun. Les différences par graine et les métriques secondaires sont conservées dans `experiments/phase_revision_20261105/E-H3B-FAMILY-MODELS/`; les 17 empreintes du manifeste ont été vérifiées.

## E-H4 — baselines HDFS au niveau bloc

Le protocole `protocoles/E-H4-HDFS-BLOCK-BASELINES.md` compare, sur la partition chronologique gelée, Histogram à trois règles simples. Les 115 013 blocs de test comprennent 1 679 positifs. Le résultat principal Histogram est comparé sans réajustement ; le seuil de la baseline de surprise moyenne des templates est choisi sur validation.

| Règle | F1 moyen sur cinq graines |
|---|---:|
| Tout positif | 0,028777 |
| Au moins un template inédit | 0,019076 |
| Surprise moyenne du template | 0,872434 |
| Histogram (template, source, sévérité) | 0,868373 |

La meilleure baseline dépasse Histogram de 0,004061 en F1 ; le protocole exigeait une avance d'au moins 0,01 pour conclure à un avantage d'Histogram. La règle simple produit le même rappel (1,0) et moins de faux positifs (491 contre 509). La conclusion prévue est donc : résultat dominé par une règle simple. Les valeurs par graine figurent dans `metrics_by_seed.csv` et sont reproduites au tableau annexe du mémoire. Les huit empreintes du manifeste, dont les données, le protocole, le runner et les sorties, ont été vérifiées.

Une tentative intermédiaire a échoué avant l'écriture des résultats sur l'adaptation d'une clé JSON (`results` au lieu de `per_seed`). Aucun score de cette tentative n'a été émis ni consulté. Le problème et le SHA-256 du runner corrigé sont consignés dans `PROTOCOLES_PREENREGISTRES.md` ; l'interprétation ci-dessus se rapporte uniquement à l'exécution corrigée et à son manifeste.

## E-H3 — faisabilité de la comparaison du routeur

L'artefact open-set contient 68 chemins distincts déjà évalués : 46 connus, 20 inconnus et 2 ambigus. L'inventaire local hors de cet ensemble laisse au plus 44 fichiers dans `data/raw/` et un échantillon dans `data/samples/`, soit 45 candidats au maximum pour les 90 sources indépendantes planifiées. Plusieurs candidats sont des archives, des fichiers de configuration ou des doublons. Constituer un nouvel ensemble de cette taille à partir des dérivés déjà utilisés introduirait une pseudo-réplication. E-H3 n'a donc pas été exécutée ; aucun résultat comparant le routeur à une table statique n'est revendiqué.

## Intégration et portée

Les résultats E-H3b et E-H4, la non-faisabilité d'E-H3 et leurs limites sont intégrés dans les chapitres 5 à 7, la conclusion et les annexes. E-H3b ne teste ni une famille absente ni le routeur. E-H4 ne fixe pas rétroactivement le budget global de H4 ; le statut de H4 reste non tranché, même si sa supériorité sur une règle simple est infirmée sur quatre jeux.

## Correction de la reprise : E-H3b n'est plus retenue

Les défauts suivants, découverts après la rédaction ci-dessus, invalident la lecture d'E-H3b donnée plus haut. Le runner importe `scripts/run_family_routing_ablation.py`, dont `load_unsw` inclut `target` dans le résumé numérique et dont `load_cicids` et `load_linux_auth` retiennent les premières lignes. La famille CICIDS ne contient donc que des DDoS d'un seul fichier, et le F1 UNSW est gonflé (0,9926 contre 0,9000 sur trois graines de diagnostic). Le script n'est pas modifié, car le manifeste d'E-H3b enregistre son empreinte ; **il reste à corriger avant toute réutilisation.**

Comparaison de référence : `protocoles/E-H3B-STRICT-HOLDOUT.md`, commit `8876861`, runner `run_e_h3b_strict.py`.

| Famille | F1 commun | F1 spécialisé | Delta [IC à 95 %] | Critère |
|---|---:|---:|---|---|
| CICIDS | 0,1349 | 0,1514 | +0,0165 [−0,0190 ; 0,0520] | échoué, par imprécision |
| Linux/auth | 0,0528 | 0,2197 | +0,1669 [0,1081 ; 0,2256] | satisfait |
| UNSW | 0,7817 | 0,7910 | +0,0093 [0,0050 ; 0,0135] | satisfait |

La non-infériorité globale n'est pas établie. Sur CICIDS et Linux/auth, les deux modèles restent très sous la prédiction systématiquement positive (0,666667). L'échec d'E-H3b sur Linux/auth disparaît avec un échantillonnage par graine (borne inférieure −0,0076 en référence aléatoire).

## Périmètre restant de l'Agent 4

Déjà comblés par la reprise : tableau des baselines par jeu (`tab:baselines-par-jeu`), version de CICIDS2017, 0,473265, 1 048 575 lignes. **Restent à faire :** justifier les sous-échantillonnages CICIDS2017 et HDFS ; traiter les huit protocoles BGL explorés sans plan préalable ; donner l'avis de faisabilité E-HET ; proposer des pistes face au « résultat négatif » ; décider si la section CSE-CIC-IDS2018 devient un audit de jeu de données ; déposer des sections dans `agent_4/sections/`. Statut : **partiel**.
