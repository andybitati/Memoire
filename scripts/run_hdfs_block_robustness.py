#!/usr/bin/env python3
"""Robustesse descriptive du résultat HDFS avec resampling au niveau bloc."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "scripts", ROOT / "src"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from dataset_strengthening_common import binary_metrics  # noqa: E402
from final_consolidation_common import (  # noqa: E402
    CONFIG_PATH, PHASE_ROOT, append_ledger, ensure_phase_dirs, relative,
    run_id, sha256_file, utc_now, write_csv, write_json,
)
from run_hdfs_block_strengthening import assign_templates, drain_config  # noqa: E402

EXPERIMENT_ID = "final_p4_hdfs_block_robustness"
SOURCE_PHASE = ROOT / "experiments" / "phase_dataset_strengthening"
SOURCE_RUN = "ds_hdfs_block_20260910T081756Z"


def frozen_event_scores(train: pd.DataFrame, test: pd.DataFrame, train_templates: np.ndarray, test_templates: np.ndarray) -> np.ndarray:
    normal_mask = train["label"].astype(int).to_numpy() == 0
    normal_count = max(int(normal_mask.sum()), 1)
    template_counts = Counter(train_templates[normal_mask].tolist())
    source_counts = Counter(train.loc[normal_mask, "source"].astype(str))
    severity_counts = Counter(train.loc[normal_mask, "severity"].astype(str))
    values: list[float] = []
    for template_id, source, severity in zip(
        test_templates, test["source"].astype(str), test["severity"].astype(str), strict=True,
    ):
        probabilities = (
            max(template_counts.get(int(template_id), 0), 1) / normal_count,
            max(source_counts.get(source, 0), 1) / normal_count,
            max(severity_counts.get(severity, 0), 1) / normal_count,
        )
        values.append(float(sum(-math.log(value) for value in probabilities) / 3.0))
    return np.asarray(values, dtype=np.float64)


def block_mean_frame(events: pd.DataFrame, scores: np.ndarray) -> pd.DataFrame:
    work = events[["block_id", "label"]].copy()
    work["mean_score"] = scores
    grouped = work.groupby("block_id", sort=False)
    result = grouped.agg(
        label=("label", "first"), event_count=("mean_score", "size"), mean_score=("mean_score", "mean"),
        label_variants=("label", "nunique"),
    ).reset_index()
    if int(result["label_variants"].max()) != 1:
        raise AssertionError("Labels contradictoires dans un block_id.")
    return result.drop(columns="label_variants")


def bootstrap_block_metrics(blocks: pd.DataFrame, threshold: float, replicates: int, seed: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    truth = blocks["label"].astype(int).to_numpy()
    scores = blocks["mean_score"].astype(float).to_numpy()
    rows: list[dict[str, Any]] = []
    for replicate in range(1, replicates + 1):
        indices = rng.integers(0, len(blocks), size=len(blocks))
        metrics = binary_metrics(truth[indices], scores[indices], threshold)
        rows.append({"replicate": replicate, "resampling_unit": "block_id", **metrics})
    return rows


def describe_bootstrap(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    output: list[dict[str, Any]] = []
    for metric in ("f1", "precision", "recall", "mcc", "fpr"):
        values = frame[metric].astype(float).to_numpy()
        output.append({
            "metric": metric, "replicates": len(values), "median": float(np.median(values)),
            "percentile_2_5": float(np.percentile(values, 2.5)),
            "percentile_97_5": float(np.percentile(values, 97.5)),
            "iqr": float(np.percentile(values, 75) - np.percentile(values, 25)),
        })
    return output


def leave_one_positive_out(blocks: pd.DataFrame, threshold: float) -> list[dict[str, Any]]:
    positives = blocks.loc[blocks["label"].astype(int) == 1, "block_id"].astype(str).tolist()
    rows: list[dict[str, Any]] = []
    for block_id in positives:
        remaining = blocks.loc[blocks["block_id"].astype(str) != block_id]
        metrics = binary_metrics(
            remaining["label"].astype(int).to_numpy(), remaining["mean_score"].astype(float).to_numpy(), threshold,
        )
        rows.append({"removed_positive_block_id": block_id, "remaining_blocks": len(remaining), **metrics})
    return rows


def main() -> int:
    ensure_phase_dirs()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))["p4"]
    source_result_path = SOURCE_PHASE / "raw" / f"{SOURCE_RUN}__hdfs_block_result.json"
    source_result = json.loads(source_result_path.read_text(encoding="utf-8"))
    events_path = SOURCE_PHASE / "raw" / f"{SOURCE_RUN}__hdfs_selected_events.csv.gz"
    state_path = SOURCE_PHASE / "processed" / f"{SOURCE_RUN}__hdfs_drain3_train_state.bin"
    selected_blocks_path = SOURCE_PHASE / "processed" / f"{SOURCE_RUN}__hdfs_selected_blocks.csv"
    threshold = float(config["threshold"])
    if source_result["block_selection"]["selected_aggregator"] != config["aggregator"]:
        raise AssertionError("L’agrégateur figé ne correspond pas au run HDFS source.")
    if not math.isclose(float(source_result["block_selection"]["selected_threshold"]), threshold, rel_tol=0, abs_tol=1e-15):
        raise AssertionError("Le seuil figé ne correspond pas au run HDFS source.")

    current_run = run_id("hdfs_block_robustness")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID, phase="P4", run_id=current_run, dataset="HDFS",
        protocol="frozen_block_mean_bootstrap_and_positive_LOO", status="RUNNING", started_at=started_at,
        command="python scripts/run_hdfs_block_robustness.py", error_path=relative(error_path),
    )
    try:
        events = pd.read_csv(events_path)
        train = events.loc[events["partition"] == "train"].reset_index(drop=True)
        test = events.loc[events["partition"] == "test"].reset_index(drop=True)
        state_before = sha256_file(state_path)
        miner = TemplateMiner(
            persistence_handler=FilePersistence(str(state_path)),
            config=drain_config(source_result["protocol"]),
        )
        clusters_before = len(miner.drain.clusters)
        train_templates = assign_templates(miner, train)
        test_templates = assign_templates(miner, test)
        state_after = sha256_file(state_path)
        clusters_after = len(miner.drain.clusters)
        if state_before != state_after or clusters_before != clusters_after:
            raise AssertionError("L’état Drain3 a changé pendant l’inférence match-only.")

        scores = frozen_event_scores(train, test, train_templates, test_templates)
        blocks = block_mean_frame(test, scores)
        if len(blocks) != int(source_result["selected_block_counts"]["test"]):
            raise AssertionError("Nombre de blocs test reconstruit inattendu.")
        positive_count = int(blocks["label"].astype(int).sum())
        if positive_count != int(source_result["selected_positive_blocks"]["test"]):
            raise AssertionError("Nombre de blocs positifs test inattendu.")
        baseline = binary_metrics(blocks["label"].astype(int).to_numpy(), blocks["mean_score"].to_numpy(), threshold)
        if not math.isclose(float(baseline["f1"]), float(source_result["block_selection"]["test_f1"]), rel_tol=0, abs_tol=1e-12):
            raise AssertionError("La reconstruction ne reproduit pas le F1 HDFS source.")

        bootstrap_rows = bootstrap_block_metrics(
            blocks, threshold, int(config["bootstrap_replicates"]), int(config["bootstrap_seed"]),
        )
        bootstrap_summary = describe_bootstrap(bootstrap_rows)
        loo_rows = leave_one_positive_out(blocks, threshold)
        if len(loo_rows) != int(config["positive_leave_one_out"]):
            raise AssertionError("Le leave-one-positive-out ne contient pas 29 évaluations.")

        blocks_path = PHASE_ROOT / "processed" / "hdfs_test_block_frozen_mean_scores.csv"
        bootstrap_path = PHASE_ROOT / "raw" / f"{current_run}_bootstrap_replicates.csv"
        loo_path = PHASE_ROOT / "raw" / f"{current_run}_positive_leave_one_out.csv"
        aggregate_path = PHASE_ROOT / "aggregated" / "hdfs_block_bootstrap_summary.csv"
        summary_path = PHASE_ROOT / "aggregated" / "hdfs_block_robustness_summary.json"
        report_path = PHASE_ROOT / "reports" / "HDFS_BLOCK_ROBUSTNESS.md"
        figure_bootstrap = PHASE_ROOT / "figures" / "dataset_19_hdfs_block_bootstrap.png"
        figure_loo = PHASE_ROOT / "figures" / "dataset_20_hdfs_positive_sensitivity.png"
        write_csv(blocks_path, blocks.to_dict(orient="records"))
        write_csv(bootstrap_path, bootstrap_rows)
        write_csv(loo_path, loo_rows)
        write_csv(aggregate_path, bootstrap_summary)

        f1_summary = next(row for row in bootstrap_summary if row["metric"] == "f1")
        interval_width = f1_summary["percentile_97_5"] - f1_summary["percentile_2_5"]
        stability = "stable" if interval_width <= float(config["descriptive_stability_max_f1_interval_width"]) else "variable"
        loo_frame = pd.DataFrame(loo_rows)
        summary = {
            "run_id": current_run, "source_run_id": SOURCE_RUN, "baseline": baseline,
            "test_blocks": len(blocks), "test_positive_blocks": positive_count,
            "aggregator": "mean", "threshold": threshold, "threshold_source": "source_run_validation_only",
            "bootstrap": {"resampling_unit": "block_id", "replicates": len(bootstrap_rows), "seed": int(config["bootstrap_seed"]), "descriptive_intervals": bootstrap_summary},
            "leave_one_positive_out": {
                "evaluations": len(loo_rows),
                "f1_min": float(loo_frame["f1"].min()), "f1_max": float(loo_frame["f1"].max()),
                "recall_min": float(loo_frame["recall"].min()), "recall_max": float(loo_frame["recall"].max()),
            },
            "stability_wording": stability,
            "assertions": {
                "resampling_unit_is_block_id": True, "threshold_frozen": True,
                "threshold_refit_in_bootstrap": False, "aggregator_refit_in_bootstrap": False,
                "drain_state_unchanged": True, "drain_cluster_count_unchanged": True,
                "baseline_reproduces_source_f1": True,
            },
        }
        write_json(summary_path, summary)

        boot_frame = pd.DataFrame(bootstrap_rows)
        fig, ax = plt.subplots(figsize=(8.6, 5.3))
        ax.hist(boot_frame["f1"], bins=30, color="#2a7185", alpha=0.85)
        ax.axvline(baseline["f1"], color="black", linestyle="--", label=f"F1 observé {baseline['f1']:.4f}")
        ax.axvspan(f1_summary["percentile_2_5"], f1_summary["percentile_97_5"], color="#e2a03f", alpha=0.2, label="Percentiles 2,5–97,5 %")
        ax.set_xlabel("F1 par réplication")
        ax.set_ylabel("Fréquence")
        ax.set_title("HDFS bloc — bootstrap descriptif au niveau block_id")
        ax.legend()
        fig.tight_layout()
        fig.savefig(figure_bootstrap, dpi=180)
        plt.close(fig)

        fig, axes = plt.subplots(2, 1, figsize=(9.2, 6.8), sharex=True)
        x = np.arange(1, len(loo_frame) + 1)
        axes[0].plot(x, loo_frame["f1"], marker="o", markersize=3, color="#2a7185")
        axes[0].axhline(baseline["f1"], color="black", linestyle="--")
        axes[0].set_ylabel("F1")
        axes[1].plot(x, loo_frame["recall"], marker="o", markersize=3, color="#b04a5a")
        axes[1].axhline(baseline["recall"], color="black", linestyle="--")
        axes[1].set_ylabel("Rappel")
        axes[1].set_xlabel("Bloc positif retiré (ordre du test)")
        fig.suptitle("HDFS bloc — sensibilité leave-one-positive-block-out")
        fig.tight_layout()
        fig.savefig(figure_loo, dpi=180)
        plt.close(fig)

        report_lines = [
            "# Robustesse descriptive du résultat HDFS au niveau bloc", "",
            f"Run : `{current_run}`. Le test gelé contient `{len(blocks)}` blocs, dont `{positive_count}` positifs. Le modèle, l’agrégateur `mean` et le seuil `{threshold:.16f}` restent inchangés.", "",
            "## Bootstrap par block_id", "",
            "| Métrique | Médiane | Percentile 2,5 % | Percentile 97,5 % | IQR |", "| --- | ---: | ---: | ---: | ---: |",
        ]
        for row in bootstrap_summary:
            report_lines.append(f"| {row['metric']} | {row['median']:.6f} | {row['percentile_2_5']:.6f} | {row['percentile_97_5']:.6f} | {row['iqr']:.6f} |")
        report_lines.extend([
            "", "Les intervalles sont descriptifs. Les réplications bootstrap ne constituent pas une preuve d’indépendance statistique.", "",
            "## Retrait d’un bloc positif", "",
            f"Les 29 retraits donnent un F1 compris entre `{loo_frame['f1'].min():.6f}` et `{loo_frame['f1'].max():.6f}`, et un rappel compris entre `{loo_frame['recall'].min():.6f}` et `{loo_frame['recall'].max():.6f}`.", "",
            "## Conclusion", "",
            f"Le score block-level reste {stability} sous les analyses de sensibilité réalisées.", "",
            "Le F1 observé de `0,892308` décrit ce test gelé ; il ne doit pas être présenté comme une valeur exacte universelle de HDFS.",
        ])
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        artifacts = [blocks_path, bootstrap_path, loo_path, aggregate_path, summary_path, report_path, figure_bootstrap, figure_loo]
        manifest_path = PHASE_ROOT / "manifests" / f"{current_run}_manifest.json"
        write_json(manifest_path, {
            "run_id": current_run, "status": "COMPLETED",
            "config": {"path": relative(CONFIG_PATH), "sha256": sha256_file(CONFIG_PATH)},
            "source_result": {"path": relative(source_result_path), "sha256": sha256_file(source_result_path)},
            "input_artifacts": [
                {"path": relative(events_path), "sha256": sha256_file(events_path)},
                {"path": relative(state_path), "sha256": sha256_file(state_path)},
                {"path": relative(selected_blocks_path), "sha256": sha256_file(selected_blocks_path)},
            ],
            "artifacts": [{"path": relative(path), "sha256": sha256_file(path)} for path in artifacts],
        })
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P4", run_id=current_run, dataset="HDFS",
            protocol="frozen_block_mean_bootstrap_and_positive_LOO", status="COMPLETED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/run_hdfs_block_robustness.py",
            raw_result_path=relative(bootstrap_path), summary_path=relative(summary_path),
            figure_path=f"{relative(figure_bootstrap)} | {relative(figure_loo)}", error_path=relative(error_path),
            notes=f"bootstrap={len(bootstrap_rows)} block_id; positive_LOO={len(loo_rows)}; {stability}.",
        )
        print(json.dumps({"status": "COMPLETED", "run_id": current_run, "baseline_f1": baseline["f1"], "bootstrap_f1": f1_summary, "stability": stability}, ensure_ascii=False))
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P4", run_id=current_run, dataset="HDFS",
            protocol="frozen_block_mean_bootstrap_and_positive_LOO", status="FAILED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/run_hdfs_block_robustness.py",
            error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
