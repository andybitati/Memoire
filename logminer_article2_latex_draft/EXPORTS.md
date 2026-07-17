# Logminer Article 2 - Export Manifest

This folder is prepared for an Overleaf upload of the second article draft.

## Main Files

- `main.tex`: initial IEEE journal-style draft for article 2.
- `references.bib`: optional BibTeX reference file, kept for future conversion if the manuscript moves from inline bibliography to BibTeX.
- `figures/`: exported figures used by `main.tex`.
- `tables/`: Markdown source tables copied from the thesis/article evidence pack.

## Current Article 2 Focus

Director title:

> Adaptive Multi-Agent AI Framework for Real-Time Log Anomaly Detection in Distributed Systems

Director trajectory:

- Article 2 for IEEE Access;
- more technical and in-depth than Article 1;
- oriented toward distributed architecture, scalability, resilience and experimental evaluation;
- planned in month 7, weeks S25-S26, together with thesis pre-finalization.

Adapted writing angle used in this draft:

> Experimental Evaluation, Robustness and Resource Analysis of a Lightweight Multi-Agent Log Anomaly Detection Framework

Scientific angle:

- extended multi-dataset evaluation;
- robustness on multi-format and corrupted logs;
- quasi-real-time FastAPI workflow;
- 30-cycle CPU/RAM resource campaign;
- Wazuh/Logminer complementarity;
- supervisor stability and stress limits;
- explicit discussion of synchronous buffering and future back-pressure.

## Reviewer Lessons Already Integrated

- Claims are cautious: non-supervised outputs are anomaly candidates.
- HDFS false positives are discussed as a structural limitation of row-level features.
- Drain-like parsing and sequence-aware detection are positioned as future HDFS/BGL branch extensions.
- The SupervisorAgent is described as policy-based bounded workflow control, not cognitive autonomy.
- Buffering/back-pressure limitations are stated in the implementation and discussion.
- The Figure 1 caption does not claim vector quality until the architecture graphic is fully verified.

## Figures Included

- `fig_architecture_logminer.pdf`
- `fig_model_portfolio_scale.pdf`
- `fig_validation_selection_f1.pdf`
- `fig_supervised_models_f1.pdf`
- `fig_false_positive_rates.pdf`
- `fig_family_routing_ablation.pdf`
- `fig_robustness_multiformat.pdf`
- `fig_realtime_workflow_latency.pdf`
- `fig_resource_campaign_multicycle.pdf`
- `fig_wazuh_logminer_overlap.pdf`

## Tables Copied

- `table_resultats_principaux.md`
- `table_datasets_scenarios.md`
- `table_realtime_benchmark.md`
- `table_realtime_benchmark_detailed.md`
- `table_resource_campaign_multicycle.md`
- `table_false_positives.md`
- `table_resilience_agent.md`
- `table_fail2ban_like_baseline.md`
- `table_wazuh_logminer_summary.md`
- `table_wazuh_logminer_overlap.md`
- `table_family_routing_ablation.md`
- `table_family_routing_operational_ablation.md`

## Overleaf Upload

Upload the full `logminer_article2_latex_draft` folder. Set `main.tex` as the main file.
