"""Generate the final scientific figures from validated experiment artefacts.

The script deliberately reads CSV/JSON/report files instead of embedding result
values.  Figure typography is intentionally large (A4 readable, 360 dpi) so that
the plots remain legible after reduction in the manuscript.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


HERE = Path(__file__).resolve()
TARGET = HERE.parents[1]
REPO = TARGET.parent
OUT = TARGET / "figures" / "final"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 15,
        "axes.titlesize": 18,
        "axes.labelsize": 16,
        "xtick.labelsize": 13,
        "ytick.labelsize": 13,
        "legend.fontsize": 13,
        "figure.titlesize": 20,
        "axes.linewidth": 1.4,
        "lines.linewidth": 2.8,
        "lines.markersize": 8,
        "savefig.dpi": 360,
    }
)

CATALOGUE: list[tuple[str, str, str]] = []


def csv(rel: str) -> pd.DataFrame:
    return pd.read_csv(REPO / rel)


def save(fig: plt.Figure, name: str, source: str, caption: str) -> None:
    fig.savefig(OUT / name, dpi=360, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    CATALOGUE.append((name, source, caption))


def bar_labels(ax, bars, fmt="{:.3f}"):
    for b in bars:
        value = b.get_height()
        ax.annotate(fmt.format(value), (b.get_x() + b.get_width() / 2, value),
                    xytext=(0, 5), textcoords="offset points", ha="center",
                    va="bottom", fontsize=12, rotation=0)


def architecture_figures() -> None:
    fig, ax = plt.subplots(figsize=(9, 9))
    ax.set_xlim(0, 9); ax.set_ylim(0, 9); ax.axis("off")
    nodes = [
        (0.2, 6.8, 2.6, 1.35, "Sources\nEVTX · CSV\nlogs", "#dbeafe"),
        (3.2, 6.8, 2.6, 1.35, "Normalisation\nparsing · schéma\nprovenance", "#dcfce7"),
        (6.2, 6.8, 2.6, 1.35, "Routeur\nopen-set\nfamille", "#fef3c7"),
        (0.2, 3.9, 2.6, 1.35, "Contract Net\nCFP · offres\nattribution", "#ede9fe"),
        (3.2, 3.9, 2.6, 1.35, "Agents\ncapacités · refus\nhandlers", "#fee2e2"),
        (6.2, 3.9, 2.6, 1.35, "Détection\nmodèle compatible\nou fallback", "#dcfce7"),
        (0.2, 1.0, 2.6, 1.35, "Redis Streams\nACK · reprise\nidempotence", "#e0f2fe"),
        (3.2, 1.0, 2.6, 1.35, "Corrélation\nanomalies vers\nincidents", "#fef3c7"),
        (6.2, 1.0, 2.6, 1.35, "Preuves\nCSV · JSON\nmétriques", "#f3f4f6"),
    ]
    for x, y, w, h, text, color in nodes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                                    facecolor=color, edgecolor="#1f2937", linewidth=1.8))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
                weight="bold", fontsize=14)
    arrows = [
        ((2.8, 7.48), (3.2, 7.48)), ((5.8, 7.48), (6.2, 7.48)),
        ((7.5, 6.8), (1.5, 5.25)), ((2.8, 4.58), (3.2, 4.58)),
        ((5.8, 4.58), (6.2, 4.58)), ((1.5, 3.9), (1.5, 2.35)),
        ((7.5, 3.9), (4.5, 2.35)), ((5.8, 1.68), (6.2, 1.68)),
    ]
    for start, end in arrows:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18,
                                     linewidth=2.0, color="#374151"))
    ax.set_title("Architecture multi-agents réellement évaluée")
    save(fig, "fig_architecture_multi_agent_global.png", "code/classes + chapitre 3",
         "Le schéma relie les sources, la normalisation, le routage, le Contract Net et les artefacts de preuve ; il décrit le prototype évalué, sans extrapoler une architecture industrielle.")

    fig, ax = plt.subplots(figsize=(13, 4.8)); ax.set_xlim(0, 10); ax.set_ylim(0, 2); ax.axis("off")
    steps = ["CFP", "PROPOSE", "REFUSE", "AWARD", "REJECT", "ACCEPT", "RESULT", "FAIL", "FEEDBACK"]
    colors = ["#dbeafe", "#dcfce7", "#fee2e2", "#fef3c7", "#fee2e2", "#ede9fe", "#dcfce7", "#fee2e2", "#e0f2fe"]
    xvals = np.linspace(0.35, 9.65, len(steps))
    for i, (x, label, color) in enumerate(zip(xvals, steps, colors)):
        ax.add_patch(FancyBboxPatch((x - 0.42, 0.75), 0.84, 0.58,
                                    boxstyle="round,pad=0.03,rounding_size=0.05",
                                    facecolor=color, edgecolor="#1f2937", linewidth=1.4))
        ax.text(x, 1.04, label, ha="center", va="center", weight="bold", fontsize=12)
        if i < len(steps) - 1:
            ax.add_patch(FancyArrowPatch((x + 0.43, 1.04), (xvals[i + 1] - 0.43, 1.04),
                                         arrowstyle="-|>", mutation_scale=15, linewidth=1.8,
                                         color="#374151"))
    ax.set_title("Séquence Contract Net observée dans le transport Redis")
    save(fig, "fig_contract_net_sequence.png", "implémentation ContractNetCoordinator/RedisContractNetTransport",
         "La séquence explicite les messages métier observés lors d'une attribution, d'un refus, d'une reprise et d'un échec contrôlé.")


def cicids_figures() -> None:
    d = csv("experiments/phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv")
    labels = [f"{r.protocol}\n{r.model}" for r in d.itertuples()]
    fig, ax = plt.subplots(figsize=(12, 6.5))
    bars = ax.bar(np.arange(len(d)), d.f1.astype(float), color=["#2563eb", "#dc2626", "#d97706", "#16a34a"])
    bar_labels(ax, bars)
    ax.set_xticks(np.arange(len(d)), labels, rotation=12, ha="right")
    ax.set_ylabel("F1 macro (moyenne des seeds)"); ax.set_ylim(0, 1.08)
    ax.set_title("CICIDS2017 : sensibilité du F1 au protocole de séparation")
    ax.grid(axis="y", alpha=.25); save(fig, "fig_cicids_protocol_comparison.png",
        "experiments/phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv",
        "Les mêmes familles de trafic produisent des performances très différentes selon la séparation ; la figure documente la validité externe limitée du protocole aléatoire.")

    d = csv("docs/memoire/pack_redaction_final/06_reproductibilite_preuves/cicids_model_candidates_summary.csv")
    fig, ax = plt.subplots(figsize=(11, 6.5))
    bars = ax.bar(d.model, d.f1_mean.astype(float), color="#2563eb")
    bar_labels(ax, bars); ax.set_xticklabels(d.model, rotation=20, ha="right")
    ax.set_ylabel("F1 macro moyen"); ax.set_ylim(0, 0.3)
    ax.set_title("CICIDS2017 : comparaison des cinq candidats (holdout scénario)")
    ax.grid(axis="y", alpha=.25); save(fig, "fig_cicids_model_comparison.png",
        "docs/memoire/pack_redaction_final/06_reproductibilite_preuves/cicids_model_candidates_summary.csv",
        "La régression logistique est le meilleur candidat selon le F1 macro moyen de ce protocole, sans supprimer la fragilité du holdout.")


def hdfs_bgl_figures() -> None:
    hpath = REPO / "experiments/phase_dataset_strengthening/raw/ds_hdfs_block_20260910T081756Z__hdfs_block_result.json"
    h = json.loads(hpath.read_text(encoding="utf-8"))
    event_f1 = float(h["historical_reference"]["f1"])
    block_f1 = float(h["block_selection"]["test_f1"])
    fig, ax = plt.subplots(figsize=(8.5, 6))
    bars = ax.bar(["Événement\n(protocole historique)", "Bloc\n(protocole final)"], [event_f1, block_f1], color=["#9ca3af", "#2563eb"])
    bar_labels(ax, bars); ax.set_ylabel("F1"); ax.set_ylim(0, 1.05)
    ax.set_title("HDFS : effet de l'unité d'évaluation")
    ax.grid(axis="y", alpha=.25); save(fig, "fig_hdfs_event_vs_block.png", str(hpath.relative_to(REPO)),
        "Le niveau bloc est l'unité alignée sur les labels finaux ; la valeur événementielle est conservée comme référence historique non équivalente.")

    boot = csv("experiments/phase_final_scientific_consolidation/raw/hdfs_block_robustness_20260911T002351Z_bootstrap_replicates.csv")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.hist(boot.f1.astype(float), bins=28, color="#2563eb", alpha=.82, edgecolor="white")
    ax.axvline(boot.f1.astype(float).median(), color="#dc2626", linestyle="--", label=f"médiane = {boot.f1.median():.3f}")
    ax.set_xlabel("F1 bootstrap (n = 1000 ré-échantillonnages par block_id)"); ax.set_ylabel("Nombre de réplications")
    ax.set_title("HDFS bloc : distribution bootstrap"); ax.legend(); ax.grid(axis="y", alpha=.2)
    save(fig, "fig_hdfs_bootstrap_distribution.png", str(REPO / "experiments/phase_final_scientific_consolidation/raw/hdfs_block_robustness_20260911T002351Z_bootstrap_replicates.csv"),
         "La dispersion bootstrap quantifie l'incertitude liée aux blocs testés ; elle complète le F1 ponctuel par une distribution et un intervalle empirique.")

    b = csv("experiments/phase_dataset_strengthening/raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv")
    hist = b[b.model.eq("Histogram") & b.group.isin(["KNOWN_TEMPLATE", "UNKNOWN_TEMPLATE"])]
    fig, ax = plt.subplots(figsize=(9.5, 6))
    bars = ax.bar(hist.group, hist.f1.astype(float), color=["#9ca3af", "#2563eb"])
    bar_labels(ax, bars); ax.set_ylabel("F1"); ax.set_ylim(0, 1.05)
    ax.set_title("BGL : performance selon la nouveauté du template")
    ax.grid(axis="y", alpha=.25); save(fig, "fig_bgl_known_unknown.png", str(REPO / "experiments/phase_dataset_strengthening/raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv"),
         "Le F1 élevé est porté par les templates inconnus ; le groupe connu ne contient aucune anomalie dans ce test et ne permet pas d'estimer un rappel d'anomalies connu.")
    all_rows = b[b.group.eq("ALL")]
    fig, ax = plt.subplots(figsize=(8.5, 6))
    bars = ax.bar(all_rows.model, all_rows.f1.astype(float), color=["#2563eb", "#d97706"])
    bar_labels(ax, bars); ax.set_ylabel("F1"); ax.set_ylim(0, 1.05); ax.set_xticklabels(all_rows.model, rotation=12, ha="right")
    ax.set_title("BGL : Histogram et baseline UnknownTemplate")
    ax.grid(axis="y", alpha=.25); save(fig, "fig_bgl_histogram_vs_unknown_baseline.png", str(REPO / "experiments/phase_dataset_strengthening/raw/ds_bgl_known_unknown_20260910T082706Z__bgl_group_metrics.csv"),
         "La comparaison montre que le score d'Histogram dépasse le baseline fondé uniquement sur l'inconnu, tout en restant dépendant de la composition du test.")


def cse_figures() -> None:
    m = csv("experiments/phase_dataset_strengthening/raw/external_csecicids2018_20260910T230136Z_metrics.csv")
    g = m.groupby("model", as_index=False).f1.mean()
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(g.model, g.f1, color=["#2563eb", "#dc2626"])
    bar_labels(ax, bars); ax.set_ylabel("F1 moyen (5 seeds)"); ax.set_ylim(0, 1.05); ax.set_xticklabels(g.model, rotation=12, ha="right")
    ax.set_title("CSE-CIC-IDS2018 : LR contre RF")
    ax.grid(axis="y", alpha=.25); save(fig, "fig_csecic_lr_vs_rf.png", "experiments/phase_dataset_strengthening/raw/external_csecicids2018_20260910T230136Z_metrics.csv",
         "Sur le split train 2018-02-15 / test 2018-02-16, la régression logistique domine la forêt aléatoire selon le F1 moyen ; cette observation ne prouve pas l'absence de fuite.")
    c = csv("experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_lr_coefficients.csv").sort_values("absolute_rank").head(10).sort_values("absolute_coefficient_mean")
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(c.feature, c.coefficient_mean, color=np.where(c.coefficient_mean >= 0, "#2563eb", "#dc2626"))
    ax.axvline(0, color="#111827", linewidth=1); ax.set_xlabel("Coefficient moyen LR"); ax.set_title("CSE-CIC : dix coefficients LR de plus forte amplitude")
    ax.grid(axis="x", alpha=.2); save(fig, "fig_csecic_lr_coefficients.png", "experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_lr_coefficients.csv",
         "Les coefficients décrivent les associations apprises par LR ; ils ne constituent pas à eux seuls une preuve causale.")
    s = csv("experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_single_feature_scores.csv").nlargest(10, "f1_mean").sort_values("f1_mean")
    fig, ax = plt.subplots(figsize=(10, 7)); bars = ax.barh(s.feature, s.f1_mean, color="#0f766e")
    ax.set_xlabel("F1 moyen mono-feature (5 seeds)"); ax.set_xlim(0, 1.05); ax.set_title("CSE-CIC : scores mono-feature les plus élevés")
    for b, v in zip(bars, s.f1_mean): ax.text(v + .01, b.get_y() + b.get_height()/2, f"{v:.3f}", va="center", fontsize=12)
    ax.grid(axis="x", alpha=.2); save(fig, "fig_csecic_lr_single_feature.png", "experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_single_feature_scores.csv",
         "La performance mono-feature signale une dépendance forte à certaines variables et motive les contrôles de robustesse.")
    a = csv("experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_feature_ablation.csv")
    fig, ax = plt.subplots(figsize=(8.5, 6)); ax.plot(a.removed_count, a.f1_mean, marker="o", color="#2563eb")
    ax.set_xlabel("Nombre de caractéristiques retirées"); ax.set_ylabel("F1 moyen"); ax.set_ylim(0, 1.05); ax.set_title("CSE-CIC : ablation des caractéristiques")
    ax.grid(alpha=.25); save(fig, "fig_csecic_lr_ablation.png", "experiments/phase_final_scientific_consolidation/aggregated/external_csecicids2018_feature_ablation.csv",
         "Le retrait de variables dégrade le F1 dans les configurations testées ; l'ablation mesure une sensibilité, non une garantie de généralisation.")
    p = csv("experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_label_permutation.csv")
    fig, ax = plt.subplots(figsize=(10, 6)); x = np.arange(len(p)); w = .36
    ax.bar(x - w/2, p.f1, width=w, label="F1", color="#2563eb"); ax.bar(x + w/2, p.pr_auc, width=w, label="PR-AUC", color="#d97706")
    ax.set_xticks(x, [str(v) for v in p.seed]); ax.set_xlabel("Seed"); ax.set_ylabel("Score"); ax.set_ylim(0, 1.05); ax.set_title("CSE-CIC : contrôle par permutation des labels d'entraînement"); ax.legend(); ax.grid(axis="y", alpha=.2)
    save(fig, "fig_csecic_lr_label_permutation.png", "experiments/phase_final_scientific_consolidation/raw/final_csecic_lr_forensic_20260911T000140Z_label_permutation.csv",
         "La permutation détruit la stabilité attendue du F1 selon les seeds ; ce contrôle documente un signal de fragilité, sans identifier à lui seul la cause.")


def routing_and_pipeline_figures() -> None:
    d = csv("experiments/phase_final_scientific_consolidation/aggregated/router_open_set_final_tradeoff_diagnostic.csv")
    fig, ax = plt.subplots(figsize=(10, 6)); ax.plot(d.min_top_score, d.unknown_rejection_rate, marker="o", label="Rejet inconnus", color="#dc2626"); ax.plot(d.min_top_score, d.coverage, marker="s", label="Couverture", color="#2563eb")
    ax.axvline(100, color="#111827", linestyle="--", label="seuil retenu = 100"); ax.set_xlabel("Seuil min_top_score"); ax.set_ylabel("Taux"); ax.set_ylim(-.03, 1.05); ax.set_title("Routeur open-set : compromis rejet / couverture"); ax.legend(); ax.grid(alpha=.25)
    save(fig, "fig_router_open_set_tradeoff.png", "experiments/phase_final_scientific_consolidation/aggregated/router_open_set_final_tradeoff_diagnostic.csv",
         "Le seuil 100 rejette les trois fichiers inconnus tout en conservant les 28 fichiers connus ; la courbe expose le compromis plutôt qu'une probabilité calibrée.")
    f = csv("experiments/phase_dataset_strengthening/aggregated/multiformat_balanced_summary.csv")
    fig, ax = plt.subplots(figsize=(11, 6.5)); x = np.arange(len(f)); w = .24
    for j, col in enumerate(["read", "parsed", "normalized"]): ax.bar(x + (j-1)*w, f[col], width=w, label=col)
    ax.set_xticks(x, f.display_name, rotation=25, ha="right"); ax.set_ylabel("Unités (N = 1000 par source)"); ax.set_ylim(0, 1080); ax.set_title("Couverture multiformat par source"); ax.legend(); ax.grid(axis="y", alpha=.2)
    save(fig, "fig_multiformat_coverage_by_source.png", "experiments/phase_dataset_strengthening/aggregated/multiformat_balanced_summary.csv",
         "La lecture, le parsing et la normalisation sont complets pour les unités effectivement présentes ; Apache reste une fixture d'une seule ligne répétée par le protocole.")


def distributed_and_e2e_figures() -> None:
    jpath = REPO / "experiments/phase_multi_agent/raw/multivm_cnp_20260909T202632Z_37592__redis_cnp_multivm.json"
    j = json.loads(jpath.read_text(encoding="utf-8")); tasks = j["tasks_by_agent"]
    fig, ax = plt.subplots(figsize=(7.5, 6)); bars = ax.bar(tasks.keys(), tasks.values(), color=["#2563eb", "#16a34a"])
    bar_labels(ax, bars, "{:.0f}"); ax.set_ylabel("Tâches terminées"); ax.set_title("Campagne multi-VM retenue : répartition des tâches"); ax.grid(axis="y", alpha=.2)
    save(fig, "fig_multi_agent_task_distribution.png", str(jpath.relative_to(REPO)), "Les deux VM traitent chacune 30 des 60 tâches ; la figure documente la distribution observée, sans prétendre démontrer une haute disponibilité.")
    st = csv("experiments/phase_multi_agent/aggregated/ma_20260909T160812Z_34016__statistics.csv")
    st = st[st.metric.isin(["throughput_tasks_sec", "latency_mean_ms"])]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    for arch, grp in st.groupby("architecture"):
        label = grp.architecture_label.iloc[0]
        for ax, metric, ylabel in zip(axes, ["throughput_tasks_sec", "latency_mean_ms"], ["Débit (tâches/s)", "Latence moyenne (ms)"]):
            q = grp[grp.metric.eq(metric)].sort_values("load"); ax.plot(q["load"], q["mean"], marker="o", label=label)
    axes[0].set_title("Débit selon la charge"); axes[1].set_title("Latence selon la charge")
    for ax, ylabel in zip(axes, ["Débit (tâches/s)", "Latence moyenne (ms)"]): ax.set_xlabel("Charge (tâches)"); ax.set_ylabel(ylabel); ax.grid(alpha=.25)
    axes[1].legend(fontsize=11); fig.suptitle("Benchmark multi-agent : monolithe, agents et reprise")
    save(fig, "fig_multi_agent_throughput_latency.png", "experiments/phase_multi_agent/aggregated/ma_20260909T160812Z_34016__statistics.csv", "Les courbes comparent quatre architectures, quatre charges et dix répétitions ; elles montrent l'absence d'accélération systématique des agents dans le protocole contrôlé.")
    c = csv("experiments/phase_final_scientific_consolidation/aggregated/multisource_cnp_model_inference_by_source.csv")
    m = c[c.condition.eq("M")].copy(); fig, ax = plt.subplots(figsize=(11, 6)); x = np.arange(len(m)); colors = np.where(m.fallback.astype(int) == 1, "#d97706", "#2563eb")
    bars = ax.bar(x, m.model_inference_count.astype(float), color=colors); ax.set_xticks(x, m.source, rotation=30, ha="right"); ax.set_ylabel("Inférences modèle exécutées"); ax.set_title("CNP : couverture des modèles réels par source (condition M)"); ax.grid(axis="y", alpha=.2)
    save(fig, "fig_e2e_real_model_coverage.png", "experiments/phase_final_scientific_consolidation/aggregated/multisource_cnp_model_inference_by_source.csv", "La condition M exécute les modèles réels pour 1400 unités sur 1401 ; une seule unité Apache utilise le fallback.")
    fig, ax = plt.subplots(figsize=(11, 6));
    for condition, color in [("H", "#9ca3af"), ("M", "#2563eb")]:
        q = c[c.condition.eq(condition)].groupby("source", as_index=False).latency_mean.mean(); ax.plot(q.source, q.latency_mean * 1000, marker="o", label=condition, color=color)
    ax.set_xticks(np.arange(len(q)), q.source, rotation=30, ha="right"); ax.set_ylabel("Latence moyenne (ms)"); ax.set_title("CNP : latence moyenne par source, heuristique contre modèles"); ax.legend(title="Condition"); ax.grid(alpha=.25)
    save(fig, "fig_e2e_real_model_latency.png", "experiments/phase_final_scientific_consolidation/aggregated/multisource_cnp_model_inference_by_source.csv", "La comparaison H/M met en regard la voie heuristique et la voie modèles ; les valeurs sont des latences observées, pas des garanties de production.")


def main() -> None:
    architecture_figures(); cicids_figures(); hdfs_bgl_figures(); cse_figures(); routing_and_pipeline_figures(); distributed_and_e2e_figures()
    lines = ["# Catalogue des figures scientifiques finales", "", "Toutes les figures sont produites par `revision_reports/generate_final_scientific_figures.py`, à 360 dpi, avec une taille de police minimale de 12 pt pour rester lisibles après réduction A4.", ""]
    for name, source, caption in CATALOGUE:
        lines.extend([f"## `{name}`", f"- Source : `{source}`", f"- Caption proposée : {caption}", ""])
    (TARGET / "revision_reports" / "FIGURE_CATALOGUE.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {len(CATALOGUE)} figures in {OUT}")


if __name__ == "__main__":
    main()
