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


REV = "experiments/phase_revision_20261104"
HDFS_FULL = f"{REV}/agent_2_hdfs/agent2_hdfs_full_20261104T131314Z__result.json"
HDFS_CI = f"{REV}/agent_2_hdfs/agent2_hdfs_full_20261104T131314Z__test_block_ci.json"
HDFS_SAMPLE = "experiments/phase_dataset_strengthening/raw/ds_hdfs_block_20260910T081756Z__hdfs_block_result.json"
HDFS_SAMPLE_BOOT = "experiments/phase_final_scientific_consolidation/raw/hdfs_block_robustness_20260911T002351Z_bootstrap_replicates.csv"
BGL_GROUPS = f"{REV}/agent_4_bgl/agent4_bgl_second_protocol_20261104T142629Z__group_metrics.csv"
ROUTES = f"{REV}/agent_5_router_open_set/routes.csv"
ROUTER_RESULT = f"{REV}/agent_5_router_open_set/result.json"
MULTIFORMAT = f"{REV}/agent_5_multiformat/result.json"
NNBSP = " "


def thousands(n: int) -> str:
    return f"{n:,}".replace(",", NNBSP)


def hdfs_bgl_figures() -> None:
    full = json.loads((REPO / HDFS_FULL).read_text(encoding="utf-8"))
    seeds = full["per_seed"]
    event_f1 = [float(s["event_test"]["f1"]) for s in seeds]
    aggs: dict[str, list[float]] = {}
    for s in seeds:
        for a in s["aggregators"]:
            aggs.setdefault(a["aggregator"], []).append(float(a["test"]["f1"]))
    ci = json.loads((REPO / HDFS_CI).read_text(encoding="utf-8"))
    cm = ci["confusion_matrix_all_seeds"]
    # L'agrégateur retenu est celui dont le F1 de test vaut le F1 publié pour toutes les graines.
    selected = [k for k, v in aggs.items() if all(abs(x - ci["f1"]["value"]) < 1e-12 for x in v)]
    assert selected == ["mean"], selected
    order = ["maximum", "abnormal_ratio", "mean"]
    names = {"maximum": "Bloc\nmaximum", "abnormal_ratio": "Bloc\nproportion\nanormale", "mean": "Bloc\nmoyenne"}
    labels = ["Événement"] + [names[k] for k in order]
    values = [float(np.mean(event_f1))] + [float(np.mean(aggs[k])) for k in order]
    fig, ax = plt.subplots(figsize=(10, 6.4))
    bars = ax.bar(labels, values, color=["#9ca3af", "#93c5fd", "#93c5fd", "#2563eb"])
    bar_labels(ax, bars)
    top = bars[-1]
    ax.annotate("retenu sur validation", (top.get_x() + top.get_width() / 2, values[-1]),
                xytext=(0, 26), textcoords="offset points", ha="center", fontsize=12, color="#1e3a8a")
    ax.set_ylabel("F1 de test (moyenne des 5 graines)"); ax.set_ylim(0, 1.05)
    ax.set_title(f"HDFS, test complet ({thousands(int(cm['n']))} blocs) : unité et agrégation")
    ax.grid(axis="y", alpha=.25)
    save(fig, "fig_hdfs_event_vs_block.png", HDFS_FULL,
         "F1 de test au niveau événement et pour les trois agrégations par bloc ; la moyenne, choisie sur la validation, est la décision retenue.")

    boot = ci["bootstrap"]
    counts = np.array([cm["tp"], cm["fp"], cm["tn"], cm["fn"]], dtype=float)
    rng = np.random.default_rng(int(boot["seed"]))
    draws = rng.multinomial(int(cm["n"]), counts / counts.sum(), size=int(boot["replicates"]))
    f1_full = 2 * draws[:, 0] / (2 * draws[:, 0] + draws[:, 1] + draws[:, 3])
    lo, hi = (float(v) for v in np.quantile(f1_full, [0.025, 0.975]))
    ref_lo, ref_hi = ci["f1"]["ci95_bootstrap_percentile"]
    assert abs(lo - ref_lo) < 1e-12 and abs(hi - ref_hi) < 1e-12, (lo, hi, ref_lo, ref_hi)
    sample = csv(HDFS_SAMPLE_BOOT).f1.astype(float)
    sample_point = float(json.loads((REPO / HDFS_SAMPLE).read_text(encoding="utf-8"))["block_selection"]["test_f1"])
    fig, ax = plt.subplots(figsize=(11, 6.4))
    bins = np.linspace(0.70, 1.0, 121)
    ax.hist(sample, bins=bins, density=True, color="#9ca3af", alpha=.75,
            label=f"échantillon de 2{NNBSP}000 blocs ({thousands(len(sample))} réplications)")
    ax.hist(f1_full, bins=bins, density=True, color="#2563eb", alpha=.85,
            label=f"test complet ({thousands(int(cm['n']))} blocs, {thousands(len(f1_full))} réplications)")
    ax.axvspan(lo, hi, color="#2563eb", alpha=.12, label=f"IC 95 % du test complet [{lo:.3f} ; {hi:.3f}]")
    ax.axvline(ci["f1"]["value"], color="#1e3a8a", linewidth=2.2, label=f"F1 test complet = {ci['f1']['value']:.3f}")
    ax.axvline(sample_point, color="#dc2626", linestyle="--", linewidth=2.2, label=f"F1 échantillon = {sample_point:.3f}")
    ax.set_xlabel("F1 bootstrap"); ax.set_ylabel("Densité"); ax.set_xlim(0.70, 1.0)
    ax.set_title("HDFS bloc : incertitude selon la taille du test")
    ax.legend(loc="upper right", fontsize=11.5); ax.grid(axis="y", alpha=.2)
    save(fig, "fig_hdfs_bootstrap_distribution.png", f"{HDFS_CI} ; {HDFS_SAMPLE_BOOT}",
         "Le bootstrap du test complet est bien plus resserré que celui de l'échantillon de 2 000 blocs, dont le F1 ponctuel sort de l'intervalle du test complet.")

    b = csv(BGL_GROUPS)
    b = b[b.protocol.eq("R0_reproduction")]
    hist = b[b.model.eq("Histogram")].set_index("group").loc[["KNOWN_TEMPLATE", "UNKNOWN_TEMPLATE"]]
    xl = []
    for g, r in hist.iterrows():
        kind = "connu" if g == "KNOWN_TEMPLATE" else "inconnu"
        pos = int(r.positives)
        xl.append(f"Template {kind}\n(n = {thousands(int(r.n))}, {thousands(pos)} positif{'s' if pos > 1 else ''})")
    fig, ax = plt.subplots(figsize=(9.5, 6))
    bars = ax.bar(xl, hist.f1.astype(float), color=["#9ca3af", "#2563eb"])
    for bar, (g, r) in zip(bars, hist.iterrows()):
        if int(r.positives) == 0:
            ax.text(bar.get_x() + bar.get_width() / 2, 0.05, "F1 non estimable :\naucune anomalie",
                    ha="center", va="bottom", fontsize=12, color="#374151")
        else:
            bar_labels(ax, [bar])
    ax.set_ylabel("F1 d'Histogram"); ax.set_ylim(0, 1.05)
    ax.set_title("BGL : performance selon la nouveauté du template")
    ax.grid(axis="y", alpha=.25)
    save(fig, "fig_bgl_known_unknown.png", BGL_GROUPS,
         "Le F1 est entièrement porté par les templates inconnus ; le groupe connu ne contient aucune anomalie dans ce test.")

    all_rows = b[b.group.eq("ALL")].set_index("model").loc[["UnknownTemplateBaseline", "SeverityNoveltyBaseline", "Histogram"]]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(["Règle « template\ninconnu »", "Règle « sévérité\nabsente du train »", "Histogram"],
                  all_rows.f1.astype(float), color=["#d97706", "#9ca3af", "#2563eb"])
    bar_labels(ax, bars); ax.set_ylabel("F1 de test"); ax.set_ylim(0, 1.05)
    ax.set_title("BGL : Histogram face à deux règles de nouveauté")
    ax.grid(axis="y", alpha=.25)
    save(fig, "fig_bgl_histogram_vs_unknown_baseline.png", BGL_GROUPS,
         "Histogram dépasse la règle du template inconnu mais obtient exactement le F1 de la règle de sévérité absente de l'entraînement.")


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
    r = csv(ROUTES)
    res = json.loads((REPO / ROUTER_RESULT).read_text(encoding="utf-8"))
    frozen = float(res["policy"]["min_top_score"])
    d = r[r["mode"].eq("P") & r.stratum.isin(["U", "K"])].copy()
    # Règle de rejet du routeur : score maximal sous le seuil, ou route de repli.
    assert ((d.top_score < frozen) | d.original_family.eq("fallback")).eq(d.rejected.astype(bool)).all()
    thresholds = np.arange(0, 221, 5)

    def rates(sub):
        u, k = sub[sub.stratum.eq("U")], sub[sub.stratum.eq("K")]
        rej = lambda x, t: ((x.top_score < t) | x.original_family.eq("fallback")).mean()
        return (np.array([rej(u, t) for t in thresholds]), np.array([rej(k, t) for t in thresholds]), len(u), len(k))

    cu, ck, nu0, nk0 = rates(d[d.origin.eq("original_31")])
    au, ak, nu, nk = rates(d)
    comb = res["summary"]["P"]["combined"]
    i = int(np.where(thresholds == frozen)[0][0])
    assert f"{round(au[i] * nu)}/{nu}" == comb["unknown_files_rejected"]
    assert f"{round(ak[i] * nk)}/{nk}" == comb["known_files_falsely_rejected"]
    fig, ax = plt.subplots(figsize=(11, 6.6))
    ax.plot(thresholds, cu, color="#dc2626", alpha=.35, linewidth=2, label=f"Rejet des inconnus, calibration ({nu0} fichiers)")
    ax.plot(thresholds, ck, color="#2563eb", alpha=.35, linewidth=2, label=f"Faux rejet des connus, calibration ({nk0} fichiers)")
    ax.plot(thresholds, au, color="#dc2626", marker="o", markersize=5, label=f"Rejet des inconnus, ensemble ({nu} fichiers)")
    ax.plot(thresholds, ak, color="#2563eb", marker="s", markersize=5, label=f"Faux rejet des connus, ensemble ({nk} fichiers)")
    ax.axvline(frozen, color="#111827", linestyle="--", label=f"seuil gelé = {frozen:.0f}")
    ax.annotate(f"{comb['unknown_files_rejected']} inconnus rejetés", (frozen, au[i]), xytext=(10, -24),
                textcoords="offset points", fontsize=12, color="#991b1b")
    ax.annotate(f"{comb['known_files_falsely_rejected']} connus rejetés à tort", (frozen, ak[i]), xytext=(-12, 16), ha="right",
                textcoords="offset points", fontsize=12, color="#1e3a8a")
    ax.set_xlabel("Seuil min_top_score"); ax.set_ylabel("Proportion de fichiers"); ax.set_ylim(-.03, 1.05)
    ax.set_title(f"Routeur open-set : rejet selon le seuil ({nu + nk} fichiers)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=11); ax.grid(alpha=.25)
    save(fig, "fig_router_open_set_tradeoff.png", ROUTES,
         "Le seuil, calibré sur 31 fichiers puis gelé, rejette les 20 inconnus et 3 des 46 connus de l'ensemble élargi ; le balayage est un diagnostic a posteriori.")

    mf = json.loads((REPO / MULTIFORMAT).read_text(encoding="utf-8"))
    names = {"windows_event": "Windows Event", "linux_auth": "Linux auth", "wazuh": "Wazuh", "syslog": "Syslog",
             "apache": "Apache (fixture)", "hdfs": "HDFS", "bgl": "BGL", "network_tabular": "Flux réseau"}
    src = mf["per_source"]
    labels = [names.get(s["source_id"], s["source_id"]) for s in src]
    read = [int(s["read"]) for s in src]
    norm = [int(s["normalized"]) for s in src]
    fields = [int(str(s["standard_fields_complete_7"]).split("/")[0]) for s in src]
    assert sum(read) == mf["total_read"] and sum(norm) == mf["total_normalized"]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.6))
    x = np.arange(len(src)); w = .38
    axes[0].bar(x - w / 2, read, width=w, label="lues", color="#93c5fd")
    axes[0].bar(x + w / 2, norm, width=w, label="émises dans le schéma", color="#2563eb")
    axes[0].set_xticks(x, labels, rotation=30, ha="right"); axes[0].set_ylabel("Unités"); axes[0].set_ylim(0, 1150)
    for xi, v in zip(x, norm):
        if v < 50:  # la fixture Apache (1 unité) serait sinon invisible
            axes[0].annotate(f"{v} unité", (xi, v), xytext=(0, 6), textcoords="offset points",
                             ha="center", va="bottom", fontsize=12, color="#1e3a8a")
    axes[0].set_title("Unités traitées par source");axes[0].legend(fontsize=11, loc="upper right"); axes[0].grid(axis="y", alpha=.2)
    bars = axes[1].bar(x, fields, color=["#dc2626" if v == 0 else "#0f766e" for v in fields])
    for bar, v in zip(bars, fields):
        axes[1].annotate(f"{v}/7", (bar.get_x() + bar.get_width() / 2, v), xytext=(0, 5),
                         textcoords="offset points", ha="center", va="bottom", fontsize=12)
    axes[1].set_xticks(x, labels, rotation=30, ha="right"); axes[1].set_ylabel("Champs standard complets (sur 7)"); axes[1].set_ylim(0, 7.9)
    axes[1].set_title("Remplissage du schéma commun"); axes[1].grid(axis="y", alpha=.2)
    fig.suptitle("Multi-format : intégration complète, remplissage inégal")
    save(fig, "fig_multiformat_coverage_by_source.png", MULTIFORMAT,
         "Toutes les unités présentes sont émises dans le schéma commun, mais le nombre de champs standard complets varie de 7/7 à 0/7.")


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


DIST = f"{REV}/agent_3_distribution"
PAIRED = f"{DIST}/agent3_paired_failure_abcd_20261104T141803Z__summary.json"
PAIRED_RUNS = f"{DIST}/agent3_paired_failure_abcd_20261104T141803Z__runs.csv"
SATURATION = f"{DIST}/agent3_saturation_multivm_20261104T142325Z__saturation_summary.json"


def revision_distribution_figures() -> None:
    s = json.loads((REPO / PAIRED).read_text(encoding="utf-8"))["summary"]
    runs = csv(PAIRED_RUNS)
    order = ["A", "B", "C", "D", "A+I", "B+I"]
    for arch in order:  # le résumé doit correspondre aux exécutions unitaires
        sub = runs[runs.architecture.eq(arch)]
        assert int(sub.duplicate_effects.sum()) == s[arch]["duplicate_effects_total"], arch
        assert int(sub.lost_tasks.sum()) == s[arch]["lost_tasks_total"], arch
    labels = {"A": "A\nmonolithe", "B": "B\nworkers", "C": "C\nagents", "D": "D\nagents\n+ mémoire",
              "A+I": "A + I\nmonolithe", "B+I": "B + I\nworkers"}
    idem = [bool(runs[runs.architecture.eq(a)].idempotency_store.all()) for a in order]
    colors = ["#2563eb" if v else "#dc2626" for v in idem]
    dup = [s[a]["duplicate_effects_total"] for a in order]
    reps = [s[a]["repetitions"] for a in order]
    lat = [s[a]["recovery_latency_median_ms"] for a in order]
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.4), gridspec_kw={"width_ratios": [1.25, 1]})
    x = np.arange(len(order))
    bars = axes[0].bar(x, dup, color=colors)
    for b, v, n in zip(bars, dup, reps):
        axes[0].annotate(f"{v}/{n}", (b.get_x() + b.get_width() / 2, v), xytext=(0, 5),
                         textcoords="offset points", ha="center", va="bottom", fontsize=13)
    axes[0].set_xticks(x, [labels[a] for a in order], fontsize=12)
    axes[0].set_ylabel("Effets dupliqués après reprise"); axes[0].set_ylim(0, max(reps) * 1.18)
    axes[0].set_title("Doublons selon l'architecture"); axes[0].grid(axis="y", alpha=.2)
    axes[0].bar([0], [0], color="#dc2626", label="sans magasin d'idempotence")
    axes[0].bar([0], [0], color="#2563eb", label="avec magasin d'idempotence")
    axes[0].legend(loc="upper right", fontsize=11.5)
    bars = axes[1].bar(x, lat, color=colors)
    for b, v in zip(bars, lat):
        axes[1].annotate(f"{v:.2f}" if v < 1 else f"{v:.1f}", (b.get_x() + b.get_width() / 2, v),
                         xytext=(0, 5), textcoords="offset points", ha="center", va="bottom", fontsize=12)
    axes[1].set_yscale("log"); axes[1].set_ylim(0.01, 40)
    axes[1].set_xticks(x, [a for a in order], fontsize=12)
    axes[1].set_ylabel("Latence de reprise médiane (ms, échelle log.)")
    axes[1].set_title("Coût du rejeu"); axes[1].grid(axis="y", alpha=.2, which="both")
    lost = sum(s[a]["lost_tasks_total"] for a in order)
    assert lost == 0, lost
    fig.suptitle("Panne après persistance, avant RESULT : aucune tâche perdue, doublons selon l'idempotence")
    save(fig, "fig_paired_failure_abcd.png", PAIRED,
         "Les doublons disparaissent dès qu'un magasin d'idempotence est présent, y compris pour le monolithe et les workers centralisés ; le gain ne vient pas du Contract Net.")

    t = json.loads((REPO / SATURATION).read_text(encoding="utf-8"))
    lv = pd.DataFrame(t["levels"])
    lv["ubuntu"] = lv.tasks_by_agent.apply(lambda d: d.get("ubuntu-beta", 0))
    lv["share_ubuntu"] = lv.ubuntu / lv.completed_ok
    tasks = csv(SATURATION.replace("_summary.json", "_tasks.csv"))
    assert int(lv.submitted.sum()) == len(tasks) and int(lv.failed.sum()) == int(tasks.status.ne("ok").sum())
    # tasks_by_agent ne compte que les tâches réussies ; les trois échecs sont attribués à Ubuntu.
    assert int(lv.ubuntu.sum()) == int((tasks.winner.eq("ubuntu-beta") & tasks.status.eq("ok")).sum())
    fig, axes = plt.subplots(3, 1, figsize=(10, 12.5), sharex=True)
    rates = sorted(lv.offered_tasks_sec.unique())
    axes[0].plot(rates, rates, color="#9ca3af", linestyle="--", linewidth=2, label="débit offert")
    palette = ["#2563eb", "#16a34a", "#d97706"]
    for (rep, grp), color in zip(lv.groupby("repetition"), palette):
        g = grp.sort_values("offered_tasks_sec")
        axes[0].plot(g.offered_tasks_sec, g.completed_tasks_sec, marker="o", color=color, label=f"répétition {rep}")
        axes[1].plot(g.offered_tasks_sec, g.latency_p95_ms / 1000, marker="o", color=color, label=f"répétition {rep}")
        axes[2].plot(g.offered_tasks_sec, 100 * g.share_ubuntu, marker="o", color=color, label=f"répétition {rep}")
    for ax in axes:
        ax.axvspan(8, 16, color="#fde68a", alpha=.35, zorder=0)
        ax.grid(alpha=.25, which="both")
    axes[0].set_xscale("log", base=2); axes[0].set_yscale("log", base=2)
    axes[0].set_xticks(rates, [f"{r:g}" for r in rates])
    axes[0].set_yticks([1, 2, 4, 8, 16, 32, 64], ["1", "2", "4", "8", "16", "32", "64"])
    axes[0].set_ylabel("Débit atteint (tâches/s)"); axes[0].legend(loc="upper left", fontsize=11)
    axes[0].set_title("Débit atteint : plafond au-delà de 8 tâches/s")
    axes[1].set_yscale("log"); axes[1].set_ylabel("Latence p95 (s, échelle log.)")
    axes[1].set_title("Latence p95 : attente côté coordinateur")
    axes[2].set_ylabel("Tâches traitées par Ubuntu (%)"); axes[2].set_ylim(-0.5, 10)
    axes[2].set_title("Part de l'agent Ubuntu : marginale, et seulement en saturation")
    axes[2].set_xlabel("Débit offert (tâches/s, échelle log.)")
    axes[2].text(8.3, 8.6, "zone du coude (8–16 tâches/s)", fontsize=12, color="#92400e")
    fig.suptitle("Saturation sur deux VM (3 répétitions, fenêtres de 30 s)", y=0.995)
    fig.tight_layout()
    save(fig, "fig_saturation_multivm.png", SATURATION,
         "Le débit atteint suit la charge jusqu'à 8 tâches/s puis plafonne ; la latence p95 explose et l'agent Ubuntu ne traite qu'une part marginale des tâches, en saturation seulement.")


GROUPS = {
    "architecture": architecture_figures, "cicids": cicids_figures, "hdfs_bgl": hdfs_bgl_figures,
    "cse": cse_figures, "routing": routing_and_pipeline_figures, "distributed": distributed_and_e2e_figures,
    "revision_distribution": revision_distribution_figures,
}


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=sorted(GROUPS),
                        help="ne régénérer que ces groupes (les schémas d'architecture ont été retouchés à la main)")
    args = parser.parse_args()
    for name in (args.only or list(GROUPS)):
        GROUPS[name]()
    if not args.only:
        lines = ["# Catalogue des figures scientifiques finales", "", "Toutes les figures sont produites par `revision_reports/generate_final_scientific_figures.py`, à 360 dpi, avec une taille de police minimale de 12 pt pour rester lisibles après réduction A4.", ""]
        for name, source, caption in CATALOGUE:
            lines.extend([f"## `{name}`", f"- Source : `{source}`", f"- Caption proposée : {caption}", ""])
        (TARGET / "revision_reports" / "FIGURE_CATALOGUE.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {len(CATALOGUE)} figures in {OUT}")
    for name, source, _ in CATALOGUE:
        print(f"  {name} <- {source}")


if __name__ == "__main__":
    main()
