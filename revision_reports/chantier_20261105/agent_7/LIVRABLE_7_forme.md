# Livrable 7 — Forme, style et coquilles

Statut : **partiel**. Les corrections mécaniques et ciblées sont faites et compilées. La relecture de style de l'ensemble du document ne l'est pas et relève de l'auteur (§3).

## 1. Corrections appliquées (lot A7-a)

| Point de la mission | Traitement |
|---|---|
| « 0,031027s̃ », « 0,105420s̃ » | Corrigés |
| « imparti, Il remporte » | Déjà clos par l'Agent 0 |
| Références BibTeX en anglais | Style `plain-fr` au lieu de `plain` |
| Surcharge de précision | 229 scores à six décimales ramenés à quatre, hors annexes ; seuil BGL 10,82 au lieu de 14 décimales ; latences à deux décimales. Valeurs inférieures à 0,001 conservées. La matrice de preuves de l'annexe garde six décimales pour le recoupement avec les artefacts |
| Identifiants de campagne dans les résumés | Absents des versions intégrées |
| Redondance des résumés | Paragraphes corrélation, CNP multi-source et procédure de mise à jour retirés des trois résumés ; contenu conservé dans le corps. Résumé français : 1 134 mots avant ; environ 990 après |
| Formules défensives | Reformulées : chapitre 1 (« Cette qualification… ») ; chapitre 3 (deux « Il serait… incorrect… ») |
| Anglicismes et accords | « le run » remplacé ; « le baseline » devenu « la baseline » ; `pairwise` retiré avec le paragraphe de corrélation |
| §7.7 pdfLaTeX | Déjà supprimé par l'Agent 6 |

Sauvegarde locale avant le lot : dossier de scratchpad de la session, non pérenne. Le dernier état commité reste `b9cb234`.

## 2. Vérifications

Cycle `pdflatex`, `bibtex`, `pdflatex` × 2 : 181 pages, sans erreur, référence ou citation indéfinie, ni débordement horizontal.

## 3. Non fait

- **Résumé encore long.** Environ 990 mots : la plupart des mémoires visent bien moins. Le réduire davantage suppose un choix de ce qui compte le plus, qui revient à l'auteur.
- **Style.** Le lecteur 3 relève une rédaction marquée par l'assistance d'une IA. Aucun remplacement automatique ne corrige cela : il subsiste par exemple 121 « donc », 28 « ainsi » et 12 « plutôt que ». Une reformulation par un nouvel outil aggraverait le problème. **L'auteur doit relire et récrire de sa main au moins l'introduction, la discussion et la conclusion**, ce qui sert aussi la soutenance.
- **Répétition des chiffres entre chapitres.** Réduite dans les résumés seulement.
- **Figures.** Les images peuvent afficher plus de décimales que le texte ; elles n'ont pas été régénérées.
- **Bokuse.** Non relu par un locuteur (C19).

=== PASSATION ===
Agent : 7 — Forme
Statut : partiel
Livrables : `agent_7/LIVRABLE_7_forme.md` ; modifications dans `main.tex` et `chapters/`
Prochain agent recommandé : 8 — Verdict
Raison : ce qui reste relève de l'auteur.
Points de vigilance pour le repreneur : ne pas lancer de réécriture automatique du style ; toute citation d'une valeur doit rester cohérente avec la matrice de l'annexe à l'arrondi près.
=== FIN PASSATION ===
