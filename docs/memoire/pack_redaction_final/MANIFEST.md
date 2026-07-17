# Manifest Du Pack Redaction Finale

Date: 2026-06-05

## Documents

- `00_lire_en_premier/checklist_redaction_finale.md`
- `00_lire_en_premier/verification_assets_articles.md`
- `PROMPT_CHATGPT_REDACTION_MEMOIRE.md`
- `01_plan_et_redaction/PLAN_DIRECTEUR_OFFICIEL.md`
- `01_plan_et_redaction/plan.md`
- `01_plan_et_redaction/pack_redaction_memoire.md`
- `01_plan_et_redaction/synthese_resultats_pour_memoire_articles.md`
- `01_plan_et_redaction/etat_lieu_exigences_techniques.md`
- `01_plan_et_redaction/comparaison_avancement_document_directeur.md`
- `01_plan_et_redaction/COMPARAISON_DANIEL_MABANZA.md`
- `02_methodologie_architecture/taxonomie_journaux.md`
- `02_methodologie_architecture/message_contract.md`
- `02_methodologie_architecture/model_registry.md`

## Figures

Les figures sont disponibles en PNG/PDF/SVG dans `04_figures_png_pdf/`:

- `fig_architecture_logminer`
- `fig_validation_selection_f1`
- `fig_supervised_models_f1`
- `fig_false_positive_rates`
- `fig_realtime_workflow_latency`
- `fig_resource_campaign_multicycle`
- `fig_robustness_multiformat`
- `fig_wazuh_logminer_overlap`
- `fig_model_portfolio_scale`
- `fig_family_routing_ablation`

## Tableaux

Tous les tableaux Markdown sont dans `03_resultats_tableaux/`. Les principaux
a inserer dans le corps du memoire sont:

- `table_resultats_principaux.md`
- `table_datasets_scenarios.md`
- `table_realtime_benchmark.md`
- `table_resource_campaign_multicycle.md`
- `table_false_positives.md`
- `table_wazuh_logminer_summary.md`
- `table_wazuh_logminer_overlap.md`
- `table_comparaison_outils_standards.md`
- `table_operational_tool_comparison.md`

## Captures

- `05_captures_dashboard/dashboard_vue_ensemble.png`
- `05_captures_dashboard/dashboard_longue_vue.png`
- `05_captures_dashboard/dashboard_resultats_detail_incident.png`
- `05_captures_dashboard/dashboard_ressources_audit.png`

## Preuves CSV

- `06_reproductibilite_preuves/realtime_workflow_benchmark_20260604.csv`
- `06_reproductibilite_preuves/resource_campaign.csv`
- `06_reproductibilite_preuves/resource_campaign_20260604.csv`
- `06_reproductibilite_preuves/family_routing_ablation.csv`
- `06_reproductibilite_preuves/standard_tools_wazuh_logminer_overlap.csv`
- `06_reproductibilite_preuves/standard_tools_fail2ban_like_baseline.csv`
- `06_reproductibilite_preuves/random_forest_linux_auth_metrics.csv`
- `06_reproductibilite_preuves/random_forest_network_cicids_metrics.csv`
- `06_reproductibilite_preuves/random_forest_unsw_80_20_metrics.csv`

## Code Et Scripts

- `09_code_et_scripts_preuves/pipeline.py`
- `09_code_et_scripts_preuves/api.py`
- `09_code_et_scripts_preuves/model_router.py`
- `09_code_et_scripts_preuves/model_compare.py`
- `09_code_et_scripts_preuves/detector.py`
- `09_code_et_scripts_preuves/correlator.py`
- `09_code_et_scripts_preuves/bus.py`
- `09_code_et_scripts_preuves/resource_monitor.py`
- `09_code_et_scripts_preuves/audit.py`
- `09_code_et_scripts_preuves/benchmark_realtime_workflow.py`
- `09_code_et_scripts_preuves/run_resource_campaign.py`
- `09_code_et_scripts_preuves/run_family_routing_ablation.py`
- `09_code_et_scripts_preuves/generate_memoire_assets.py`
- `09_code_et_scripts_preuves/export_memoire_figures.py`

## Projet LaTeX Overleaf

Le projet LaTeX corrige apres comparaison avec le memoire de Daniel Mabanza est
disponible dans `10_latex_overleaf/`:

- `10_latex_overleaf/main.tex`
- `10_latex_overleaf/frontmatter/`
- `10_latex_overleaf/chapters/`
- `10_latex_overleaf/chapters/chapitre7_reproductibilite_deploiement.tex`
- `10_latex_overleaf/figures/`
- `10_latex_overleaf/captures/`
- `10_latex_overleaf/references.bib`
- `10_latex_overleaf/COMPARAISON_DANIEL_MABANZA.md`
