# NEXT ACTION

## PROCHAINE ACTION EXACTE — MISSION MULTI-AGENTS

1. Créer `scripts/run_true_multi_agent_experiments.py`.
2. Comparer A monolithe, B workers centralisés, C agents autonomes mémoire OFF et D agents autonomes mémoire ON sur des workloads appariés.
3. Mesurer durée, débit, latences, CPU, RSS, messages CNP, réattributions, équité de Jain, succès, échecs, reprises et doublons.
4. Exécuter au moins 10 répétitions par charge raisonnable et enregistrer les données brutes avant toute agrégation.
5. Ajouter l’adaptation en deux phases, l’expérience post-traitement/pré-ACK et le pipeline bout en bout avec `end_to_end_run_id`.
6. Générer les agrégats, figures, rapports et manifestes SHA-256 sans modifier les artefacts historiques.

Document de référence déjà produit : `docs/MULTI_AGENT_GAP_ANALYSIS.md`.

Critère de sortie de la prochaine phase : artefacts bruts et agrégés reproductibles, statistiques descriptives complètes, dix figures demandées ou échec documenté pour chacune.

## ACTION LATEX CONSERVÉE POUR REPRISE ULTÉRIEURE

Ne pas refaire la première passe pdfLaTeX et ne pas rescanner le dépôt.

1. Depuis `ARIEL_LOGMINER_MEMOIRE_FINAL/build`, exécuter :

```powershell
& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\bibtex.exe' --include-directory=.. main
```

2. Depuis `ARIEL_LOGMINER_MEMOIRE_FINAL`, exécuter deux fois :

```powershell
& 'C:\Users\aoliv\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe' -enable-installer -interaction=nonstopmode -file-line-error -halt-on-error -output-directory=build main.tex
```

3. Vérifier dans `build/main.log` : citations indéfinies, références indéfinies, erreurs et warnings sévères.
4. Relever le nombre final de pages.
5. Après succès seulement, copier/renommer `build/main.pdf` en `build/Memoire_Ariel_Logminer_Final.pdf`.

Warnings déjà observés à examiner après stabilisation : commandes d'accent signalées en mode mathématique, nombreuses boîtes `Underfull`, et `Infinite glue shrinkage` dans `chapters/annexes.tex` autour de la ligne 1153.

Phase: FINAL DELIVERY PREPARATION

Experiment: Aucun

Last completed step: PHASE 13A completed; autonomous delivery folder created and static audit run.

Next exact step: Compile `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex` when a LaTeX toolchain is available, then perform visual PDF audit.

Command to run: recherches officielles et `scripts/verify_public_dataset_copies.py` uniquement.

Expected output: `build/Memoire_Ariel_Logminer_Final.pdf` and a completed visual audit.

Files that must be read: manifeste final, chemins CICIDS concernés et sources publiques officielles.

Files that DO NOT need to be reread: mémoire complet, résultats expérimentaux et JSON de runs.

Success criterion: statut CICIDS conforme à la preuve, fichiers de comparaison et état de reprise mis à jour.

If failure: Revenir au chemin précis dans `ARTIFACT_INDEX.json`; ne pas rescanner tout le dépôt.
