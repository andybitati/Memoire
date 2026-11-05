# Livrable 7 — Forme, style et coquilles

Statut : **partiel**. Les corrections mécaniques et ciblées sont faites et compilées, ainsi qu'une relecture de fond (§4). La reformulation personnelle du style relève de l'auteur (§3).

## 1. Corrections appliquées (lot A7-a)

| Point de la mission | Traitement |
|---|---|
| « 0,031027s̃ », « 0,105420s̃ » | Corrigés |
| « imparti, Il remporte » | Déjà clos par l'Agent 0 |
| Références BibTeX en anglais | Style `plain-fr` au lieu de `plain` |
| Surcharge de précision | 229 scores à six décimales ramenés à quatre, hors annexes ; seuil BGL 10,82 au lieu de 14 décimales ; latences à deux décimales. Valeurs inférieures à 0,001 conservées. La matrice de preuves de l'annexe garde six décimales pour le recoupement avec les artefacts |
| Identifiants de campagne dans les résumés | Absents des versions intégrées |
| Redondance des résumés | Paragraphes corrélation, CNP multi-source et procédure de mise à jour retirés des trois résumés ; contenu conservé dans le corps. Résumés français et anglais ensuite récrits : 1 134 mots avant, 441 après pour le français |
| Formules défensives | Reformulées : chapitre 1 (« Cette qualification… ») ; chapitre 3 (deux « Il serait… incorrect… ») |
| Anglicismes et accords | « le run » remplacé ; « le baseline » devenu « la baseline » ; `pairwise` retiré avec le paragraphe de corrélation |
| §7.7 pdfLaTeX | Déjà supprimé par l'Agent 6 |

Sauvegarde locale avant le lot : dossier de scratchpad de la session, non pérenne. Le dernier état commité avant la relecture est `8106113`.

## 2. Vérifications

Cycle `pdflatex`, `bibtex`, `pdflatex` × 2 : 180 pages, sans erreur, référence ou citation indéfinie, ni débordement horizontal.

## 3. Non fait

- **Bokuse plus long que les deux autres résumés.** Il reste une version plus détaillée, faute de locuteur pour le récrire.
- **Style.** Le lecteur 3 relève une rédaction marquée par l'assistance d'une IA. Aucun remplacement automatique ne corrige cela : il subsiste par exemple 121 « donc », 28 « ainsi » et 12 « plutôt que ». Une reformulation par un nouvel outil aggraverait le problème. **L'auteur doit relire et récrire de sa main au moins l'introduction, la discussion et la conclusion**, ce qui sert aussi la soutenance.
- **Répétition des chiffres entre chapitres.** Réduite dans les résumés seulement.
- **Figures.** Les images peuvent afficher plus de décimales que le texte ; elles n'ont pas été régénérées.
- **Bokuse.** Non relu par un locuteur (C19).

## 4. Relecture de fond (lot R-a)

Lus en entier : introduction, chapitre 4, validité, limites, conclusion, discussion. Lus pour l'essentiel : chapitres 3 et 5. Annexes et chapitre 2 : contrôle de toutes les mentions du prototype et du mémoire, par recherche.

Corrections : formule défensive citée par le lecteur 3 ; contributions et validité actualisées ; risque d'audit de code déclaré ; bilan, apports, perspectives et conclusion générale alignés sur les résultats ; références à une version du travail retirées du chapitre 2 ; tableau de positionnement corrigé pour la mémoire. Corrigés au chapitre 2 : « détecte, priorise » (priorisation non évaluée) et une « lacune retenue » contraire au positionnement. **Reste non relu ligne à ligne :** la partie purement bibliographique du chapitre 2 ; l'exactitude des citations n'a pas été revérifiée dans cette passe.

=== PASSATION ===
Agent : 7 — Forme
Statut : partiel
Livrables : `agent_7/LIVRABLE_7_forme.md` ; modifications dans `main.tex` et `chapters/`
Prochain agent recommandé : 8 — Verdict
Raison : ce qui reste relève de l'auteur.
Points de vigilance pour le repreneur : ne pas lancer de réécriture automatique du style ; toute citation d'une valeur doit rester cohérente avec la matrice de l'annexe à l'arrondi près.
=== FIN PASSATION ===
