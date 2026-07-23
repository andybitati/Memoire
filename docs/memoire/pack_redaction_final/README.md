# Pack Redaction Finale Memoire Logminer

Date de preparation: 2026-06-05

Ce dossier rassemble les elements directement utilisables pour rediger le
memoire: plan, textes de base, tableaux, figures, captures dashboard, preuves
experimentales, documents d'architecture, articles et references.

## Verdict

Le pack est pret pour la redaction. Les figures, tableaux, captures dashboard
et preuves principales sont regroupes ici. Le projet LaTeX Overleaf corrige
apres comparaison avec le memoire de Daniel Mabanza est inclus dans
`10_latex_overleaf/`.

## Ordre De Lecture Conseille

1. `00_lire_en_premier/checklist_redaction_finale.md`
2. `01_plan_et_redaction/PLAN_DIRECTEUR_OFFICIEL.md`
3. `PROMPT_CHATGPT_REDACTION_MEMOIRE.md`
4. `01_plan_et_redaction/plan.md`
5. `01_plan_et_redaction/pack_redaction_memoire.md`
6. `01_plan_et_redaction/synthese_resultats_pour_memoire_articles.md`
7. `01_plan_et_redaction/COMPARAISON_DANIEL_MABANZA.md`
8. `10_latex_overleaf/README.md`
9. `06_reproductibilite_preuves/fiche_reproductibilite_experimentale.md`

## Usage Par Chapitre

| Chapitre | Fichiers principaux |
| --- | --- |
| Chapitre 1 - Introduction | `01_plan_et_redaction/PLAN_DIRECTEUR_OFFICIEL.md`, `01_plan_et_redaction/plan.md`, `01_plan_et_redaction/pack_redaction_memoire.md` |
| Chapitre 2 - Etat de l'art | `08_references/exploitation_references.md`, `08_references/deep_learning_log_survey_comparison.md`, PDF de references |
| Chapitre 3 - Methodologie | `02_methodologie_architecture/taxonomie_journaux.md`, `02_methodologie_architecture/message_contract.md`, `04_figures_png_pdf/fig_architecture_logminer.*` |
| Chapitre 4 - Implementation | `02_methodologie_architecture/v1_cli_v2_services.md`, `02_methodologie_architecture/v2_fastapi.md`, `05_captures_dashboard/*.png` |
| Chapitre 5 - Resultats | `03_resultats_tableaux/*.md`, `04_figures_png_pdf/*.png`, `06_reproductibilite_preuves/*.csv` |
| Chapitre 6 - Discussion | `01_plan_et_redaction/synthese_resultats_pour_memoire_articles.md`, `02_methodologie_architecture/comparaison_scientifique_outils_standards.md` |
| Chapitre 7 - Conclusion | `01_plan_et_redaction/pack_redaction_memoire.md`, `01_plan_et_redaction/comparaison_avancement_document_directeur.md` |

## Contenu Du Pack

- `00_lire_en_premier/`: etat final, checklist et verification des assets.
- `01_plan_et_redaction/`: plan officiel du document directeur, plan adapte,
  pack de redaction, synthese et alignement avec le document directeur.
- `02_methodologie_architecture/`: architecture, taxonomie, contrat des
  messages, guide et registre des modeles.
- `03_resultats_tableaux/`: tous les tableaux Markdown prets a inserer.
- `04_figures_png_pdf/`: figures en PNG, PDF et SVG.
- `05_captures_dashboard/`: captures du dashboard et wrappers de regeneration.
- `06_reproductibilite_preuves/`: protocoles, fiche de reproductibilite et CSV
  experimentaux principaux.
- `07_articles_et_reponses/`: documents articles, reponses et cadrage.
- `08_references/`: references exploitees, PDF locaux, document directeur et
  ressources bibliographiques.
- `09_code_et_scripts_preuves/`: fichiers source et scripts a citer pour
  l'implementation, les benchmarks et la generation des assets.
- `10_latex_overleaf/`: memoire LaTeX pret pour Overleaf, avec frontmatter
  academique, chapitres, figures, captures, bibliographie et comparaison
  Daniel Mabanza.

## Version LaTeX Corrigee

Compiler `10_latex_overleaf/main.tex` sur Overleaf avec pdfLaTeX. Cette version
contient maintenant la page de garde institutionnelle, l'epigraphe, la dedicace,
les remerciements, la liste des acronymes/abreviations, les chapitres renforces,
un chapitre de discussion generale, les captures dashboard et les figures
experimentales locales.

La version courante ajoute aussi un chapitre de reproductibilite, deploiement
et exploitation, avec le depot GitHub du projet:
`https://github.com/andybitati/Memoire/tree/main`. Les articles scientifiques seront
ajoutes plus tard lorsqu'ils seront rediges.

## Resultats A Citer

| Resultat | Valeur |
| --- | --- |
| Linux/auth RandomForest | F1 = 0.916602 |
| CICIDS2017 RandomForest | F1 = 0.997163 |
| UNSW/CIC-DDoS RandomForest | F1 = 0.999965 |
| Wazuh | 122 563 evenements, 3 676 anomalies candidates |
| Benchmark temps reel | 10 cycles, 8 537 lignes/cycle, moyenne 8.2012 s |
| Campagne CPU/RAM | 30 cycles, workflow moyen 9.3300 s |
| Robustesse multi-format | logs incomplets conserves |

## Captures Dashboard Disponibles

- `05_captures_dashboard/dashboard_vue_ensemble.png`
- `05_captures_dashboard/dashboard_longue_vue.png`
- `05_captures_dashboard/dashboard_resultats_detail_incident.png`
- `05_captures_dashboard/dashboard_ressources_audit.png`

## Prudence Scientifique

- Presenter les anomalies non supervisees comme des anomalies candidates.
- Ne pas presenter la baseline fail2ban-like comme fail2ban officiel.
- Presenter Redis/MQTT comme extension operationnelle locale, pas comme preuve
  de scalabilite industrielle.
- Distinguer article 1 et article 2 pour les mesures de scalabilite.
- Ne pas sur-vendre l'auto-apprentissage continu: le cadrer en perspective.

## Pour ChatGPT

Le fichier `PROMPT_CHATGPT_REDACTION_MEMOIRE.md` est pret a etre donne a
ChatGPT avec ce dossier. Il impose de suivre d'abord
`01_plan_et_redaction/PLAN_DIRECTEUR_OFFICIEL.md`, puis d'utiliser les autres
documents comme preuves et contenus de redaction.

## Code A Citer

- `09_code_et_scripts_preuves/pipeline.py`
- `09_code_et_scripts_preuves/api.py`
- `09_code_et_scripts_preuves/orchestrator.py`
- `09_code_et_scripts_preuves/model_router.py`
- `09_code_et_scripts_preuves/model_compare.py`
- `09_code_et_scripts_preuves/detector.py`
- `09_code_et_scripts_preuves/correlator.py`
- `09_code_et_scripts_preuves/bus.py`
- `09_code_et_scripts_preuves/benchmark_realtime_workflow.py`
- `09_code_et_scripts_preuves/run_resource_campaign.py`
