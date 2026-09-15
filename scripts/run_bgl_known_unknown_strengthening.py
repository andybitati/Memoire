"""Quantifie la performance BGL sur templates connus et inconnus du train."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from dataset_strengthening_common import (  # noqa: E402
    PHASE_ROOT,
    append_ledger,
    binary_metrics,
    ensure_phase_dirs,
    git_commit,
    load_config,
    metrics_from_prediction,
    relative,
    run_id,
    select_threshold,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)


GROUPS = ("ALL", "KNOWN_TEMPLATE", "UNKNOWN_TEMPLATE")


def group_masks(template_ids: np.ndarray) -> dict[str, np.ndarray]:
    identifiers = np.asarray(template_ids, dtype=np.int64)
    return {
        "ALL": np.ones(len(identifiers), dtype=bool),
        "KNOWN_TEMPLATE": identifiers != 0,
        "UNKNOWN_TEMPLATE": identifiers == 0,
    }


def evaluate_groups(
    truth: np.ndarray,
    scores: np.ndarray,
    template_ids: np.ndarray,
    threshold: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    unknown_prediction = (np.asarray(template_ids) == 0).astype(np.int8)
    for group, mask in group_masks(template_ids).items():
        if not np.any(mask):
            continue
        hist = binary_metrics(truth[mask], scores[mask], threshold)
        rows.append({"model": "Histogram", "group": group, **hist})
        baseline = metrics_from_prediction(truth[mask], unknown_prediction[mask], unknown_prediction[mask])
        rows.append({"model": "UnknownTemplateBaseline", "group": group, "threshold": 1.0, **baseline})
    return rows


def make_figures(rows: list[dict[str, Any]]) -> list[Path]:
    import matplotlib.pyplot as plt

    frame = pd.DataFrame(rows)
    groups = list(GROUPS)
    first = PHASE_ROOT / "figures" / "dataset_03_bgl_known_unknown_f1.png"
    histogram = frame[frame["model"] == "Histogram"].set_index("group")
    fig, axis = plt.subplots(figsize=(9, 5.2))
    values = [float(histogram.loc[group, "f1"]) for group in groups]
    bars = axis.bar(groups, values, color=["#4C78A8", "#59A14F", "#E45756"])
    for bar, value in zip(bars, values):
        axis.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.4f}", ha="center")
    axis.set_ylim(0, 1.08)
    axis.set_ylabel("F1")
    axis.set_title("BGL Histogram — templates connus et inconnus du train")
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(first, dpi=180)
    plt.close(fig)

    second = PHASE_ROOT / "figures" / "dataset_04_bgl_novelty_baseline.png"
    all_rows = frame[frame["group"] == "ALL"].set_index("model")
    metrics = ["precision", "recall", "f1", "pr_auc", "mcc"]
    x = np.arange(len(metrics))
    fig, axis = plt.subplots(figsize=(9.5, 5.4))
    axis.bar(x - 0.18, [float(all_rows.loc["Histogram", metric]) for metric in metrics], width=0.36, label="Histogram")
    axis.bar(
        x + 0.18,
        [float(all_rows.loc["UnknownTemplateBaseline", metric]) for metric in metrics],
        width=0.36,
        label="UnknownTemplateBaseline",
    )
    axis.set_xticks(x, [metric.upper().replace("_", "-") for metric in metrics])
    axis.set_ylim(-0.05, 1.08)
    axis.set_title("BGL — modèle Histogram contre baseline de nouveauté")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(second, dpi=180)
    plt.close(fig)
    return [first, second]


def execute() -> dict[str, Any]:
    ensure_phase_dirs()
    protocol = load_config()["bgl_known_unknown"]
    identifier = run_id("ds_bgl_known_unknown")
    experiment_id = "dataset_strengthening_bgl_known_unknown"
    started = utc_now()
    bundle_path = ROOT / protocol["feature_bundle"]
    prepared = ROOT / protocol["prepared_events"]
    append_ledger(
        experiment_id=experiment_id,
        phase=2,
        run_id=identifier,
        dataset="BGL",
        protocol="known_unknown_template_analysis",
        status="RUNNING",
        started_at=started,
        command="scripts/run_bgl_known_unknown_strengthening.py",
    )
    try:
        bundle = np.load(bundle_path)
        validation = pd.read_csv(prepared / "bgl_validation_events.csv", low_memory=False)
        test = pd.read_csv(prepared / "bgl_test_events.csv", low_memory=False)
        validation_ids = np.asarray(bundle["template_id_validation"], dtype=np.int64)
        test_ids = np.asarray(bundle["template_id_test"], dtype=np.int64)
        if not np.array_equal(validation["drain_cluster_id"].to_numpy(dtype=np.int64), validation_ids):
            raise AssertionError("Validation template IDs disagree between CSV and NPZ")
        if not np.array_equal(test["drain_cluster_id"].to_numpy(dtype=np.int64), test_ids):
            raise AssertionError("Test template IDs disagree between CSV and NPZ")
        y_validation = np.asarray(bundle["y_validation"], dtype=np.int8)
        y_test = np.asarray(bundle["y_test"], dtype=np.int8)
        validation_scores = np.asarray(bundle["hist_validation"], dtype=np.float64)
        test_scores = np.asarray(bundle["hist_test"], dtype=np.float64)
        threshold, validation_metrics = select_threshold(y_validation, validation_scores)
        rows = evaluate_groups(y_test, test_scores, test_ids, threshold)
        raw_path = PHASE_ROOT / "raw" / f"{identifier}__bgl_group_metrics.csv"
        write_csv(raw_path, rows)
        figures = make_figures(rows)

        frame = pd.DataFrame(rows)
        histogram_all = frame[(frame["model"] == "Histogram") & (frame["group"] == "ALL")].iloc[0]
        baseline_all = frame[(frame["model"] == "UnknownTemplateBaseline") & (frame["group"] == "ALL")].iloc[0]
        hist_prediction = test_scores >= threshold
        unknown = test_ids == 0
        hist_true_positive = hist_prediction & (y_test == 1)
        tp_unknown = int(np.sum(hist_true_positive & unknown))
        quantification = {
            "unknown_template_rate": float(np.mean(unknown)),
            "anomaly_rate_unknown_group": float(np.mean(y_test[unknown])) if np.any(unknown) else None,
            "anomaly_rate_known_group": float(np.mean(y_test[~unknown])) if np.any(~unknown) else None,
            "histogram_true_positives_on_unknown": tp_unknown,
            "histogram_true_positives_total": int(np.sum(hist_true_positive)),
            "fraction_histogram_true_positives_on_unknown": float(tp_unknown / max(np.sum(hist_true_positive), 1)),
            "novelty_baseline_f1_over_histogram_f1": float(baseline_all["f1"] / max(float(histogram_all["f1"]), 1e-15)),
            "novelty_baseline_recall": float(baseline_all["recall"]),
            "histogram_recall": float(histogram_all["recall"]),
        }
        summary = {
            "schema_version": 1,
            "run_id": identifier,
            "generated_at": utc_now(),
            "git_commit": git_commit(),
            "protocol": protocol,
            "inputs": {
                "feature_bundle": relative(bundle_path),
                "feature_bundle_sha256": sha256_file(bundle_path),
                "validation_events_sha256": sha256_file(prepared / "bgl_validation_events.csv"),
                "test_events_sha256": sha256_file(prepared / "bgl_test_events.csv"),
            },
            "threshold": threshold,
            "threshold_selected_on": "validation_only",
            "validation_metrics": validation_metrics,
            "test_rows": len(y_test),
            "group_metrics": rows,
            "quantification": quantification,
            "assertions": {
                "groups_exhaustive": int(np.sum(unknown) + np.sum(~unknown)) == len(y_test),
                "groups_disjoint": True,
                "template_ids_match_prepared_csv": True,
                "test_not_used_for_threshold": True,
            },
            "artifacts": [relative(raw_path), *[relative(path) for path in figures]],
        }
        result_path = PHASE_ROOT / "raw" / f"{identifier}__bgl_known_unknown_result.json"
        write_json(result_path, summary)
        report_path = PHASE_ROOT / "reports" / "BGL_KNOWN_UNKNOWN_ANALYSIS.md"
        report_path.write_text(
            "\n".join(
                [
                    "# BGL — templates connus et inconnus",
                    "",
                    f"- Run : `{identifier}`",
                    f"- Seuil Histogram choisi sur validation : `{threshold:.9f}`.",
                    f"- Test : `{len(y_test)}` événements ; templates inconnus : `{quantification['unknown_template_rate']:.4%}`.",
                    f"- F1 Histogram (ALL) : `{float(histogram_all['f1']):.6f}`.",
                    f"- F1 UnknownTemplateBaseline (ALL) : `{float(baseline_all['f1']):.6f}`.",
                    f"- Rappel baseline nouveauté : `{float(baseline_all['recall']):.6f}`.",
                    f"- Part des vrais positifs Histogram située sur des templates inconnus : `{quantification['fraction_histogram_true_positives_on_unknown']:.4%}`.",
                    "",
                    "La baseline ne prouve pas que toute nouveauté est une anomalie. Elle quantifie la part du résultat compatible avec une simple règle de nouveauté structurelle.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        completed = utc_now()
        append_ledger(
            experiment_id=experiment_id,
            phase=2,
            run_id=identifier,
            dataset="BGL",
            protocol="known_unknown_template_analysis",
            status="COMPLETED",
            started_at=started,
            completed_at=completed,
            command="scripts/run_bgl_known_unknown_strengthening.py",
            raw_result_path=relative(result_path),
            summary_path=relative(report_path),
            figure_path=";".join(relative(path) for path in figures),
            notes=f"unknown_rate={quantification['unknown_template_rate']:.6f}; histogram_f1={float(histogram_all['f1']):.6f}; baseline_f1={float(baseline_all['f1']):.6f}",
        )
        return summary
    except Exception as exc:
        error_path = PHASE_ROOT / "logs" / f"{identifier}__bgl_known_unknown_error.txt"
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=experiment_id,
            phase=2,
            run_id=identifier,
            dataset="BGL",
            protocol="known_unknown_template_analysis",
            status="FAILED",
            started_at=started,
            completed_at=utc_now(),
            command="scripts/run_bgl_known_unknown_strengthening.py",
            error_path=relative(error_path),
            notes=f"{type(exc).__name__}: {exc}",
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.dry_run:
        protocol = load_config()["bgl_known_unknown"]
        result = {
            "status": "DRY_RUN",
            "bundle_exists": (ROOT / protocol["feature_bundle"]).exists(),
            "prepared_events_exists": (ROOT / protocol["prepared_events"]).exists(),
        }
    else:
        result = execute()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
