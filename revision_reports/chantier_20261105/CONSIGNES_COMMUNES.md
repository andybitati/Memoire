# Consignes communes à tous les agents du chantier (2026-11-05)

À lire avant toute action, avec `MISSION.md`, `RETOURS_LECTEURS.md` (en entier) et `ETAT_CHANTIER.md` (décisions C1 à C14 et suivantes, tableau C5, lots intégrés).

## Repères
- Dépôt : `E:\Cours\TFE` (Windows ; Bash/Git Bash et PowerShell). Python : `.venv\Scripts\python.exe` (général, redis) ; `.venv-hdfs-bgl\Scripts\python.exe` (drain3, scipy, pandas). Mettre `PYTHONIOENCODING=utf-8`. Environnement détaillé (Redis, VM) : `revision_reports/HANDOFF.md` §6.
- Manuscrit : `ARIEL_LOGMINER_MEMOIRE_FINAL/main.tex`, `chapters/*.tex`, `frontmatter/*.tex`. PDF : `ARIEL_LOGMINER_MEMOIRE_FINAL/main.pdf`. Les pages et sections citées par les lecteurs renvoient au PDF ; correspondance fichiers / numérotation : `revision_reports/agent_7/PATCH_NOTES.md`, section « Correspondance fichiers / numérotation du PDF » ; s'aider de `main.toc`, `main.aux`, `main.lof`, `main.lot`.
- Des lots ont déjà été intégrés au manuscrit (voir « Lots intégrés » dans `ETAT_CHANTIER.md`) : les numéros de ligne des livrables antérieurs sont décalés. **Repérer les passages par leur texte.**
- Livrables déjà produits : `agent_1/`, `agent_2/` (et les suivants au fil du chantier). Les sections d'un agent postérieur partent des sections d'un agent antérieur sur le même passage, jamais du `.tex` d'origine si une version corrigée existe.
- Les dossiers `revision_reports/agent_<N>/` (sans `chantier_20261105`) appartiennent à une révision antérieure : ce sont des sources, pas des livrables du chantier.
- Artefacts : `experiments/` (notamment `phase_revision_20261104/`, avec manifeste SHA-256).

## Règles impératives
1. **Ne modifier aucun fichier `.tex` du mémoire** (C1). Déposer les sections corrigées dans `agent_<N>/sections/` : un fichier LaTeX par passage, prêt à intégrer, nommé d'après le fichier cible et la section, avec en tête un commentaire `%` donnant le fichier cible, le passage à remplacer (premiers mots exacts), l'agent auteur et les sources.
2. **Aucun chiffre inventé** : chaque nombre vient d'un artefact (run_id + chemin) ou d'une section du corps citée. Si une expérience contredit le texte, on corrige le texte, jamais le résultat (C3).
3. **Aucun chiffre ni résultat dans un résumé ou dans la conclusion qui ne soit présenté dans le corps** (C8).
4. **Un seul travail, résultats finaux** (C4) : aucune référence dans le texte rédigé à des versions, tentatives, campagnes antérieures, « ancien protocole » ni dates d'exécution. La déclaration IA reste factuelle (C4 b). Aucun préenregistrement revendiqué, sauf pour les expériences de C13 réellement préenregistrées (C4 c).
5. **Pas de HARKing** : H1–H5 et leurs critères sont jugés tels qu'écrits ; les statuts sont ceux de `agent_2/` arbitrés par C10.
6. Français soutenu et sobre. Pas de formules défensives répétées (« il serait incorrect d'affirmer… », « ne constitue pas une validation SOC… ») : énoncer la limite une fois, à sa place.
7. Ne pas lancer de sous-agents.
8. **Fichiers partagés** : plusieurs agents peuvent travailler en même temps. Dans `ETAT_CHANTIER.md` et `PROTOCOLES_PREENREGISTRES.md`, ne jamais réécrire le fichier entier : relire le fichier juste avant, puis faire des remplacements ciblés limités à **ta** ligne et à **tes** sections. Ne modifier aucun autre fichier hors de ton dossier `agent_<N>/`, sauf ce que ta mission prévoit explicitement (artefacts d'expérience, registre des protocoles).
9. Git : branche `revision-chantier-20261105`. Seuls les commits de protocoles prévus par C13-proc sont autorisés (`git add` des seuls fichiers du protocole et du registre). Aucun autre commit, aucun push, aucun changement de branche.
10. Expériences (seulement si ta mission en prévoit) : procédure C13-proc de `ETAT_CHANTIER.md`, sans exception. Artefacts dans `experiments/phase_revision_20261105/<ID>/`, avec un `MANIFEST_SHA256.csv`.

## Fin de tâche
1. Mettre à jour `ETAT_CHANTIER.md` (règle 8) : ta ligne du tableau « Périmètres » (statut complet / partiel / bloqué, livrables), une section « Décisions de l'Agent N » (une phrase de justification par décision), tes questions ouvertes (avec l'agent ou la personne concernée), le prochain agent recommandé.
2. Si tu es interrompu : écrire immédiatement dans `ETAT_CHANTIER.md` `INTERROMPU — REPRENDRE À : [fichier, section, passage exact]`, avec ce qui est fait et ce qui reste.
3. Terminer le rapport final par le bloc :

```text
=== PASSATION ===
Agent : [numéro et nom]
Statut : [terminé / partiel / bloqué / interrompu]
Livrables : [liste des fichiers]
Prochain agent recommandé : [numéro et nom]
Raison : [une phrase]
Points de vigilance pour le repreneur : [liste courte]
=== FIN PASSATION ===
```
