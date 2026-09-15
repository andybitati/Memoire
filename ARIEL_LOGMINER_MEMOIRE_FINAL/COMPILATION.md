# Compilation

## Répertoire de travail obligatoire

Toutes les prochaines commandes LaTeX, BibTeX et de contrôle du PDF doivent être lancées
avec le répertoire de travail suivant :

`E:\Cours\TFE\ARIEL_LOGMINER_MEMOIRE_FINAL`

Le dossier `build/` reste le répertoire de sortie. Ne pas lancer une compilation depuis la
racine `E:\Cours\TFE`.

La compilation utilise le moteur disponible dans l'environnement de travail.

Sur cette machine, MiKTeX est installé ici :

`C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\`

Les exécutables détectés sont `pdflatex.exe`, `bibtex.exe`, `latexmk.exe` et `mpm.exe`.
Sur cette machine, `latexmk.exe` nécessite Perl et n'est donc pas la voie actuellement
retenue. La chaîne directe MiKTeX est utilisée.

```powershell
& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe' `
  -enable-installer -interaction=nonstopmode -file-line-error -halt-on-error `
  -output-directory=build main.tex

Push-Location .\build
& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\bibtex.exe' `
  --include-directory=.. main
Pop-Location

& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe' `
  -enable-installer -interaction=nonstopmode -file-line-error -halt-on-error `
  -output-directory=build main.tex

& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe' `
  -enable-installer -interaction=nonstopmode -file-line-error -halt-on-error `
  -output-directory=build main.tex
```

Commande `latexmk` équivalente uniquement après installation de Perl :

```powershell
& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\latexmk.exe' -pdf -interaction=nonstopmode -file-line-error -outdir=build main.tex
```

Si le moteur ou une dépendance LaTeX n'est pas disponible, la compilation est marquée `NOT AVAILABLE` dans le rapport de livraison; aucune commande alternative n'est inventée.
