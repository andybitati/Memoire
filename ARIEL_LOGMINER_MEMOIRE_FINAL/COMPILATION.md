# Compilation

La compilation utilise le moteur disponible dans l'environnement de travail. Depuis ce dossier :

Sur cette machine, MiKTeX est installé ici :

`C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\`

Les exécutables détectés sont `pdflatex.exe`, `latexmk.exe` et `mpm.exe`.

```text
pdflatex -interaction=nonstopmode main.tex
bibtex main
pdflatex -interaction=nonstopmode main.tex
pdflatex -interaction=nonstopmode main.tex
```

Commande Windows équivalente avec le chemin MiKTeX détecté :

```powershell
& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\latexmk.exe' -pdf -interaction=nonstopmode -file-line-error -outdir=build main.tex
```

Si le moteur ou une dépendance LaTeX n'est pas disponible, la compilation est marquée `NOT AVAILABLE` dans le rapport de livraison; aucune commande alternative n'est inventée.
