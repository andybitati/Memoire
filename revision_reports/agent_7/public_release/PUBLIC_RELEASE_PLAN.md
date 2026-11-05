# Plan de publication du dépôt Ariel Logminer

Constat de départ (commit `35da3a9`, 1 470 fichiers suivis par git). Aucune
action n'a été exécutée sur le dépôt : ce document est une proposition.

## 1. Structure publique proposée

Dépôt public distinct, construit par copie sélective (et non par publication
du dépôt de travail, dont l'historique git contient des fichiers internes).

```text
ariel-logminer/
├── README.md                ← public_release/README_public.md
├── LICENSE                  ← public_release/LICENSE (MIT)
├── DATA_LICENSES.md         ← public_release/DATA_LICENSES.md
├── CITATION.cff             ← public_release/CITATION.cff
├── .zenodo.json             ← public_release/.zenodo.json
├── .gitignore               ← .gitignore actuel + public_release/gitignore_public_additions.txt
├── requirements*.txt        (5 fichiers actuels)
├── Dockerfile, .dockerignore, docker-compose.redis.yml
├── src/logminer/
├── scripts/                 (sauf exclusions §2)
├── tests/
├── web/dashboard/           (interface ; « Stitch web/ » en est un doublon à vérifier)
├── models/                  (11 fichiers .joblib suivis, dont 1 via Git LFS)
├── examples/                (après décision §3)
├── state/EXPERIMENT_LEDGER.csv
├── experiments/
│   ├── README.md, ARTIFACT_NAMING_CONVENTION.md
│   ├── phase_dataset_strengthening/        (82,8 Mo)
│   ├── phase_final_scientific_consolidation/ (47,1 Mo)
│   ├── phase_multi_agent/                  (100,3 Mo)
│   ├── phase_cnp_endurance/                (9,5 Mo)
│   └── phase_reference_copies/             (NOUVEAU, §4)
├── data/verification/public_sources/zenodo_8196385_metadata.json
└── memoire/                 ← ARIEL_LOGMINER_MEMOIRE_FINAL/ renommé
    ├── main.tex, references.bib
    ├── chapters/, frontmatter/, figures/, captures/, tables/
    ├── evidence/            (matrices et vérification des copies publiques)
    └── scripts/generate_final_scientific_figures.py  ← déplacé depuis revision_reports/
```

Tailles mesurées sur le disque de travail le 2026-11-04. Le total
`experiments/` (≈ 240 Mo) reste compatible avec GitHub (fichiers < 100 Mo
chacun, à vérifier par `git lfs`/`find -size +50M`) et avec Zenodo.

## 2. Exclusions

| Élément | Motif |
|---|---|
| `.secrets/` | Identifiants VM chiffrés DPAPI. Déjà ignoré ; vérifier qu'il n'apparaît dans aucun commit (`git log --all -- .secrets`). |
| `.venv/`, `.venv-final-experiments/`, `.venv-hdfs-bgl/` | Environnements locaux. |
| `Debian/`, `Ubuntu/` | Machines virtuelles VirtualBox. |
| `data/raw/` (≈ 23,4 Go), `data/processed/` (≈ 13,6 Go), `data/verification/` hors métadonnées (≈ 1,7 Go), `data/samples/Application.evtx` | Jeux publics à télécharger à la source ; journal Windows local. |
| `docs/` (453 fichiers suivis, dont `docs/memoire/pack_redaction_final/`) | Documentation de travail, chemins absolus, doublons. Ne publier que ce qui est cité par le mémoire (copié en §4). |
| `revision_reports/`, `ARIEL_LOGMINER_MEMOIRE_FINAL/revision_reports/` (sauf le générateur de figures, déplacé) | Rapports internes de révision. |
| `graphify-out/`, `.codex/`, `.agents/`, `.vscode/`, `.pytest_cache/`, `.merge-main-staging` | Outillage local. |
| `memoire_logminer_latex_overleaf/`, `logminer_article1_latex_draft/`, `logminer_article2_latex_draft/` | Versions antérieures et articles non publiés (décision de l'auteur). |
| Notes à la racine : `Remarques.txt`, `Prompt de review.txt`, `Prompt pour Luna.txt`, `Workflow usage modèle GPT.txt`, `reponses_questions_soutenance_precises.txt`, `TRAVAIL_A_FAIRE_ICI.md`, `DIAGNOSTIC_SCIENTIFIQUE_MEMOIRE.md`, `FINAL_*.md`, `FERMETURE_INCERTITUDES_FACTUELLES_P0.md`, `MULTI_AGENT_FINAL_REPORT.md`, `DATASET_STRENGTHENING_FINAL_REPORT.md`, `dataset_strengthening_claim_evidence_matrix.md`, `ANALYSE_POSITIONNEMENT_MARCHE_ET_APPORT_LOGMINER.txt`, `DESCRIPTION_UI_PROJET.txt`, `kaggle_unsw_random_forest_80_20.txt`, `Mémoire_Andy.ipynb` | Notes de travail et échanges de révision. |
| Dans le dossier du mémoire : `*.aux`, `*.log`, `*.toc`, `*.lof`, `*.lot`, `*.out`, `*.bbl`, `*.blg`, `build/`, `COMPILATION.md`, `COMMANDES_COMPILATION_LATEX.txt` (chemins absolus `C:\Users\…`), `CHANGELOG_FINAL.md`, `FINAL_DELIVERY_REPORT.md`, `README.md` interne, `*.pptx` | Fichiers de compilation et de travail. Le PDF final est déposé séparément sur Zenodo. |
| `scripts/show_vm_credential.ps1` | Affiche un identifiant VM ; sans utilité pour un tiers. |

Les scripts `scripts/start_cnp_endurance_multivm_agents.ps1`,
`scripts/finalize_cnp_endurance_multivm_agents.ps1` et
`scripts/run_vbox_redis_*.ps1` passent un mot de passe obtenu à l'exécution
(`$Credential.Password`, `$Password`) ; aucun secret n'y figure en clair
d'après un balayage `git grep` des motifs `password|secret|token|api_key`.
Ils peuvent être publiés après relecture des noms d'hôtes et d'utilisateurs.

## 3. Données personnelles et de sécurité : décision requise

Le balayage des fichiers suivis montre :

- `experiments/phase_dataset_strengthening/processed/router_independent_*/source_003.csv`
  (trois exécutions) : événements de sécurité Windows de la machine de
  laboratoire, avec nom d'utilisateur local et nom d'hôte (33 occurrences du
  nom d'utilisateur dans le fichier de l'exécution `20260910T092757Z`) ;
- fichiers `wazuh.csv` et `source_0xx.csv` du même dossier : adresses IPv4
  privées (`192.168.x.x`) ;
- `examples/windows_event_sample.xml`, `data/samples/Application.evtx` :
  journaux Windows locaux ;
- nombreux artefacts : chemins absolus `E:\Cours\TFE\...` (colonnes de
  provenance).

Options, à trancher par l'auteur :

1. **Publier tel quel** (chemins et noms d'hôtes jugés anodins) — conserve les
   empreintes SHA-256 des manifestes.
2. **Pseudonymiser** les fichiers concernés, recalculer leurs empreintes et
   ajouter un manifeste `*_public_sha256.json` qui documente la
   transformation, en conservant l'empreinte d'origine.
3. **Exclure** les fichiers concernés et le signaler dans le README ; les
   résultats agrégés du routeur restent publiés.

Recommandation : option 3 pour les journaux Windows de la machine personnelle,
option 1 pour les chemins absolus.

## 4. Artefacts cités hors de `experiments/`

| Artefact cité | Emplacement actuel | SHA-256 | Emplacement public proposé |
|---|---|---|---|
| Comparaison des cinq candidats CICIDS2017 | `docs/memoire/pack_redaction_final/06_reproductibilite_preuves/cicids_model_candidates_summary.csv` (copie identique : `data/processed/cicids_model_candidates_summary.csv`, ignoré) | `4EDA14B91D8E1A540BAAA74FEE14AFC6A278FB915EFA62AF01A4BF95EFE20C69` | `experiments/phase_reference_copies/cicids_model_candidates_summary.csv` |
| Corrélation synthétique, `run_id = e8_correlation_synthetic_controlled` | `data/processed/final_experiments_2026/correlation_synthetic_summary.json` (**ignoré par git, absent du dépôt**) | `33AEF93FAECD76DEF8ED0B62CD01429819FF81CCF24E23F2897DCE43EC4A1B42` | `experiments/phase_reference_copies/correlation_synthetic_summary.json` |

`phase_reference_copies/` doit contenir un `README.md` donnant pour chaque
copie l'emplacement d'origine et l'empreinte ci-dessus, ainsi que la
configuration référencée par la corrélation
(`docs/memoire/final_experiments_2026/configs/correlation_synthetic_protocol.json`).

Le générateur de figures lit encore l'ancien chemin
(`ARIEL_LOGMINER_MEMOIRE_FINAL/revision_reports/generate_final_scientific_figures.py`,
l. 127 et 134) et écrit son catalogue dans `revision_reports/` (l. 257). Après
déplacement vers `memoire/scripts/`, `HERE.parents[1]` désigne toujours le
dossier du mémoire et `REPO` la racine : seules ces trois lignes sont à
modifier.

## 5. Procédure Zenodo et DOI

1. Créer le dépôt public (GitHub) à partir de la copie sélective ; vérifier
   `git ls-files` contre les exclusions du §2 et exécuter `python -m pytest tests`.
2. Compiler le mémoire final et joindre `main.pdf` comme fichier de la
   release (le PDF n'est pas suivi dans git).
3. Se connecter à Zenodo avec le compte GitHub, activer l'intégration pour le
   dépôt (Settings → GitHub → interrupteur du dépôt).
4. Vérifier `.zenodo.json` (créateurs, affiliations des co-directeurs,
   licence) ; Zenodo l'utilise à la place des métadonnées déduites.
5. Créer une release GitHub `v1.0.0` ; Zenodo archive automatiquement
   l'instantané et attribue deux DOI : un DOI de version et un DOI de concept
   (toutes versions).
6. Reporter le **DOI de concept** dans `CITATION.cff` (`doi`,
   `preferred-citation.doi`), dans le README et dans le mémoire
   (chapitre 7, section « Dépôt public et archivage », champ
   `[DOI À COMPLÉTER]`), puis publier `v1.0.1` si l'on souhaite que l'archive
   contienne le DOI. Le PDF déposé auprès de l'université doit citer le DOI de
   concept.
7. Option sans GitHub : dépôt manuel sur zenodo.org (Upload → New upload),
   archive `.zip` de la copie sélective, mêmes métadonnées ; utiliser
   « Reserve DOI » pour obtenir le DOI avant publication et l'insérer dans le
   mémoire avant le dépôt définitif.
