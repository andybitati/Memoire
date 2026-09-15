# HUMANIZATION PASS

Date : 2026-09-09

## Périmètre

Passe effectuée sur les chapitres LaTeX du dossier final, sans modification des valeurs numériques, métriques, protocoles, hypothèses, références ou noms de composants.

## Contrôles

- [x] phrases non mécaniques : aucune série de paragraphes n'a été réécrite selon un patron unique ;
- [x] transitions naturelles : les connecteurs sont employés de manière ponctuelle et contextualisée ;
- [x] absence de répétitions évidentes : les occurrences de formulations stéréotypées ont été vérifiées ;
- [x] rythme varié : alternance de phrases descriptives, analytiques et interprétatives ;
- [x] vocabulaire académique naturel ;
- [x] aucune simplification abusive ;
- [x] contenu scientifique inchangé.

## Corrections d'encodage

Deux caractères Unicode de remplacement présents dans des artefacts textuels ont été remplacés par un tiret demi-cadratin (`–`) dans les libellés `Web Attack – ...`. Aucun octet UTF-8 invalide ni motif de mojibake n'est détecté dans les fichiers `.tex`, `.bib`, `.md`, `.csv` et `.json` du dossier final.

## Compatibilité LaTeX

Le projet utilise pdfLaTeX avec `inputenc` UTF-8, `fontenc` T1 et `babel` français. La compilation effective reste à effectuer sur une machine disposant de la toolchain LaTeX ; les exécutables ne sont pas disponibles dans l'environnement courant.
