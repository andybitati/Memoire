# Évaluation du rejet open-set du routeur

Run : `final_router_open_set_20260911T000746Z`.

## Calibrage

Les seuils sont sélectionnés exclusivement sur des folds leave-one-family-out construits à partir des familles connues. Dans chaque fold, la famille tenue à l’écart est traitée comme pseudo-inconnue en retirant sa capacité de la liste des scores candidats. Les trois sources open-set finales ne participent ni au calibrage ni au choix de la politique.

Politique figée : `top_score >= 100.0`, `decision_margin >= 0.0` et au moins `0` règle compatible. `decision_margin` est un score heuristique de séparation, pas une probabilité.

## Test final

| Métrique | Valeur |
| --- | ---: |
| Known accuracy | 1.000000 |
| Known macro-F1 | 1.000000 |
| Unknown rejection rate | 1.000000 |
| False rejection rate on known | 0.000000 |
| Fallback rate | 0.000000 |
| Coverage | 0.903226 |
| Selective accuracy | 1.000000 |

La courbe de compromis est un diagnostic postérieur au gel du seuil. Elle ne sert pas à resélectionner la politique sur le test final.

## Limite

Le test final ne compte que trois fichiers inconnus locaux. Le résultat soutient le fonctionnement du rejet dans ce corpus, pas une capacité open-set générale.
