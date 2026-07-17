# Memoire Logminer LaTeX Overleaf

Ce dossier contient une redaction LaTeX complete du memoire Logminer, preparee
pour Overleaf.

## Fichier Principal

Compiler `main.tex`.

## Compilation Overleaf

Reglage conseille:

- Compiler: pdfLaTeX
- Bibliographie: BibTeX automatique Overleaf

Overleaf peut compiler directement le projet apres upload du dossier complet.

## Structure

- `main.tex`: page de titre, resume, table des matieres et inclusion des chapitres.
- `frontmatter/`: epigraphe, dedicace, remerciements, acronymes et abreviations.
- `chapters/`: chapitres du memoire.
- `figures/`: figures PNG pretes a inserer.
- `captures/`: captures dashboard.
- `tables/`: tableaux Markdown sources conserves pour reference.
- `references.bib`: bibliographie BibTeX.
- `IMAGE_ASSETS.md`: justification de l'usage exclusif d'images locales.
- `COMPARAISON_DANIEL_MABANZA.md`: ecarts constates et corrections appliquees
  apres comparaison avec le memoire de Daniel Mabanza.

## Remarques

La redaction suit le plan directeur officiel du memoire. Les affirmations sont
cadrees prudemment:

- les sorties non supervisees sont des anomalies candidates;
- la baseline fail2ban-like n'est pas fail2ban officiel;
- Redis/MQTT sont presentes comme extensions locales et perspectives;
- la distribution multi-machine stricte reste une perspective.

La version courante contient aussi un chapitre de discussion generale ajoute
avant la conclusion afin de developper l'interpretation des resultats, les
limites scientifiques et techniques, la valeur pratique du prototype et les
perspectives de deploiement.

Elle contient egalement un chapitre de reproductibilite et de deploiement avec
le lien GitHub du projet: `https://github.com/andybitati/Memoire/tree/version_3`.

## Images

Le projet n'utilise aucune image distante. Toutes les figures et captures sont
locales et issues du prototype ou des resultats experimentaux. Voir
`IMAGE_ASSETS.md`.
