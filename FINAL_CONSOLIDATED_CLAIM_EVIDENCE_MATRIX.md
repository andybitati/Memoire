# Matrice claim–evidence consolidée

| Claim | Avant | Nouvelle preuve | Résultat | Limite | Statut final |
| --- | --- | --- | --- | --- | --- |
| LR externe non triviale | LR F1 moyen 0,999212 ; absence de vecteurs exacts inter-jour | Permutation, 78 mono-features, coefficients standardisés, ablations train-only | `Dst Port` seule : F1 0,999720 ; après retrait top-10 : F1 0,657859 ; conclusion B | Deux jours et quatre scénarios DoS ; PR-AUC de permutation instable ; causalité non établie | PARTIELLEMENT SOUTENU |
| Router open-set | Rejet 0/3 | Seuil `top_score=100` sélectionné sur 196 observations de validation pseudo-open connues, puis test final gelé | Rejet 3/3 ; faux rejet connu 0/28 ; coverage 0,903226 | Trois fichiers inconnus locaux seulement ; pas de généralisation open-set | PARTIELLEMENT SOUTENU |
| E2E modèles réels | 1 401 tâches avec `e2e_lightweight_candidate_rule_v1` | Registre de compatibilité et traces par tâche avec modèle chargé, hash et marqueur d’inférence | 1 400/1 401 inférences réelles, 1 fallback explicite, 0 erreur | Local ; artefacts historiques ; métriques prédictives H non évaluables sans circularité | SOUTENU |
| HDFS block robustness | F1 bloc 0,892308 sur 29 positifs | 1 000 bootstraps par `block_id`, seuil gelé et 29 retraits d’un positif | Médiane F1 0,894737, intervalle descriptif [0,800000 ; 0,961039] ; résultat variable | Bootstrap descriptif, non preuve d’indépendance ; 29 positifs | PARTIELLEMENT SOUTENU |
| Multi-agent autonomy | acquis | Non réévalué inutilement ; tests CNP et idempotence conservés | Architecture légère, décisions, refus, attributions, mémoire et transport Redis déjà prouvés dans le périmètre laboratoire | Pas de causalité nouvelle sur performance ou résilience industrielle | SOUTENU |
| Industrial deployment | perspective | Non testé dans cette phase | NON ÉVALUÉ | Haute disponibilité, multi-site, partitions et très grande échelle non évalués | HORS PÉRIMÈTRE |

Les statuts portent sur les claims formulés dans le périmètre exact des artefacts cités, pas sur une validité industrielle générale.
