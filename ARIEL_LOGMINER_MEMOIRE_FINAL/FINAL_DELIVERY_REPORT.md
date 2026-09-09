# Rapport de livraison finale

## Dossier final

`ARIEL_LOGMINER_MEMOIRE_FINAL/`

## Structure vérifiée

- Fichier LaTeX principal : `main.tex`
- Introduction non numérotée : `chapters/chapitre1_introduction.tex`
- Premier chapitre numéroté : `chapters/chapitre2_etat_art.tex`
- Conclusion non numérotée : `chapters/chapitre6_conclusion.tex`
- Bibliographie : `references.bib`
- Annexes : `chapters/annexes.tex`
- Preuves de traçabilité : `evidence/data_traceability/`
- Matrice des affirmations : `evidence/claim_evidence/`
- Hypothèses et questions de recherche : `evidence/hypotheses/`, `evidence/research_questions/`
- Reproductibilité : `evidence/reproducibility/`
- Rapports et état : `revision_reports/`

## Résultat de compilation

PDF final : **NON DISPONIBLE DANS CET ENVIRONNEMENT**. Les exécutables `pdflatex` et `tectonic` ne sont pas installés. La procédure reproductible est décrite dans `COMPILATION.md` et doit être exécutée dans un environnement LaTeX externe.

## Contrôles exécutés

- vérification des copies publiques et calculs SHA-256 ;
- contrôle des références de figures et des chemins relatifs ;
- retrait du score 0,999965 du texte scientifique final ;
- retrait des affirmations non traçables CIC-DDoS2019 du corpus de résultats ;
- séparation explicite des campagnes Redis locale et VirtualBox multi-VM ;
- conservation des limites de preuve dans les rapports d'évidence.
- passe de rédaction humanisée : `revision_reports/HUMANIZATION_PASS.md` ;
- contrôle UTF-8 complet des fichiers textuels du dossier final.

## Limites conservées

- La copie BGL locale n'est pas démontrée bit-à-bit avec l'archive publique.
- L'identité publique exacte des Parquets UNSW-NB15 locaux n'est pas démontrée bit-à-bit.
- L'origine du fichier `linux_auth_logs_labeled.csv` reste partiellement documentée.
- La compilation PDF et les avertissements LaTeX finaux restent à vérifier sur une machine disposant de la toolchain.

Le dossier est prêt pour revue manuelle et compilation externe. Aucun ZIP n'est créé ici.
