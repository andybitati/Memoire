# NEXT ACTION

## RÈGLE DE COMPILATION — À CONSERVER

Toutes les prochaines compilations doivent utiliser
`E:\Cours\TFE\ARIEL_LOGMINER_MEMOIRE_FINAL` comme répertoire de travail de la commande.
Le PDF et les fichiers auxiliaires restent produits sous `build/`. Ne pas compiler depuis
la racine `E:\Cours\TFE`.

Avant la prochaine compilation complète, intégrer ou écarter explicitement les nouveaux
résultats multi-agents selon
`revision_reports/MULTI_AGENT_RESULTS_INTEGRATION_AUDIT.md` afin de ne pas stabiliser un
PDF dont le résumé et les chapitres 3 à 7 décrivent encore l'ancienne campagne.

## PROCHAINE ACTION EXACTE — MISSION MULTI-AGENTS

La phase demandée est terminée. Les runs de référence sont :

1. `ma_20260909T160812Z_34016` pour la matrice A/B/C/D et le pipeline 8/8;
2. `redis_cnp_20260909T162814Z_47940` pour les trois processus sur l'hôte local;
3. `multivm_cnp_20260909T202632Z_37592` pour Debian/Ubuntu, 15 refus et une réattribution après échec.

Ne pas réexécuter ces campagnes sans nouvelle demande. L'extension encore légitime est un test `XPENDING/XAUTOCLAIM` avec arrêt forcé d'un agent invité après effet persistant et avant ACK. Tant qu'il n'existe pas, conserver la résilience post-traitement multi-VM au statut `PARTIELLEMENT CORRIGÉ`.

Les identifiants VM sont stockés sous chiffrement DPAPI dans `.secrets/`; ne jamais les ajouter à Git ni les recopier dans un rapport.
Pour les consulter volontairement sous le même compte Windows : `powershell -File scripts/show_vm_credential.ps1 -VM Ubuntu -RevealPassword` (remplacer `Ubuntu` par `Debian` si nécessaire).

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
