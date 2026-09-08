# Compilation

La compilation utilise le moteur disponible dans l'environnement de travail. Depuis ce dossier :

```text
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Si le moteur ou une dépendance LaTeX n'est pas disponible, la compilation est marquée `NOT AVAILABLE` dans le rapport de livraison; aucune commande alternative n'est inventée.

