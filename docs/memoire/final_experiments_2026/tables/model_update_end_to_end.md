# Mise à jour contrôlée des modèles — test fonctionnel end-to-end

Dataset local : CICIDS2017, holdout DDoS, seed 42. Métrique de décision : F1. Seuil minimal de gain : 0,02. N = 3 comparaisons fonctionnelles préspécifiées.

| Cas | F1 courant | F1 candidat | Delta | Seuil | Décision | Intégrité |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Promotion | 0.711340 | 0.779185 | +0.067845 | 0.020000 | promu | vérifiée |
| Rejet (candidat inférieur) | 0.779185 | 0.716022 | -0.063163 | 0.020000 | courant conservé | vérifiée |
| Rejet (gain < seuil) | 0.711340 | 0.720357 | +0.009016 | 0.020000 | courant conservé | vérifiée |

Statut scientifique : validation fonctionnelle de la procédure contrôlée. Ces trois cas ne constituent ni une nouvelle évaluation indépendante de généralisation, ni une preuve d'apprentissage continu autonome.
