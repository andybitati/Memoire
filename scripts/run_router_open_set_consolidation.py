#!/usr/bin/env python3
"""Calibre puis évalue un rejet open-set léger sans fuite du test final."""

from __future__ import annotations

import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "scripts", ROOT / "src"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from final_consolidation_common import (  # noqa: E402
    CONFIG_PATH, PHASE_ROOT, append_ledger, ensure_phase_dirs, relative,
    run_id, sha256_file, utc_now, write_csv, write_json,
)
from logminer.agents.model_router import apply_open_set_rejection, route_dataframe  # noqa: E402

EXPERIMENT_ID = "final_p2_router_open_set"
SOURCE_PHASE = ROOT / "experiments" / "phase_dataset_strengthening"
ROUTER_CONFIG = SOURCE_PHASE / "configs" / "router_independent_sources.json"


def route_statistics(scores: dict[str, Any], excluded_family: str | None = None) -> tuple[str, float, float, float]:
    priority = ["windows", "hdfs", "bgl", "wazuh", "network_cicids", "network", "linux_auth", "linux", "fallback"]
    candidates = [family for family in priority if family != excluded_family]
    ranked = sorted(candidates, key=lambda family: float(scores.get(family, 0.0)), reverse=True)
    top = float(scores.get(ranked[0], 0.0))
    second = float(scores.get(ranked[1], 0.0))
    return ranked[0], top, second, top - second


def validation_records(known_routes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Construit des folds pseudo-open exclusivement à partir des familles connues."""

    records: list[dict[str, Any]] = []
    families = sorted({str(row["true_family"]) for row in known_routes})
    for heldout in families:
        for row in known_routes:
            scores = dict(row["scores"])
            if row["true_family"] == heldout:
                predicted, top, second, margin = route_statistics(scores, excluded_family=heldout)
                expected = "unknown"
                pseudo_open = True
            else:
                predicted, top, second, margin = route_statistics(scores)
                expected = str(row["true_family"])
                pseudo_open = False
            records.append({
                "fold_heldout_family": heldout,
                "source_id": row["source_id"],
                "expected": expected,
                "predicted_before_rejection": predicted,
                "top_score": top,
                "second_score": second,
                "decision_margin": margin,
                "compatible_rule_count": len(row["reasons"]),
                "pseudo_open": pseudo_open,
            })
    return records


def apply_policy_to_record(row: dict[str, Any], policy: dict[str, Any]) -> tuple[str, bool]:
    rejected = (
        float(row["top_score"]) < float(policy["min_top_score"])
        or float(row["decision_margin"]) < float(policy["min_decision_margin"])
        or int(row["compatible_rule_count"]) < int(policy["min_compatible_rules"])
    )
    return ("unknown" if rejected else str(row["predicted_before_rejection"])), rejected


def validation_metrics(records: list[dict[str, Any]], policy: dict[str, Any]) -> dict[str, Any]:
    predictions: list[str] = []
    expected: list[str] = []
    rejected: list[bool] = []
    pseudo_open: list[bool] = []
    for row in records:
        prediction, is_rejected = apply_policy_to_record(row, policy)
        predictions.append(prediction)
        expected.append(str(row["expected"]))
        rejected.append(is_rejected)
        pseudo_open.append(bool(row["pseudo_open"]))
    known_mask = np.logical_not(pseudo_open)
    open_mask = np.asarray(pseudo_open, dtype=bool)
    rejected_array = np.asarray(rejected, dtype=bool)
    correct = np.asarray([truth == pred for truth, pred in zip(expected, predictions, strict=True)], dtype=bool)
    accepted = ~rejected_array
    return {
        **policy,
        "validation_n": len(records),
        "known_n": int(known_mask.sum()),
        "pseudo_open_n": int(open_mask.sum()),
        "pseudo_unknown_rejection_rate": float(rejected_array[open_mask].mean()),
        "false_rejection_rate_on_known": float(rejected_array[known_mask].mean()),
        "known_accuracy": float(correct[known_mask].mean()),
        "coverage": float(accepted.mean()),
        "selective_accuracy": float(correct[accepted].mean()) if accepted.any() else math.nan,
    }


def calibrate_policy(known_routes: list[dict[str, Any]], config: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    records = validation_records(known_routes)
    candidates: list[dict[str, Any]] = []
    for top, margin, rules in itertools.product(
        config["candidate_min_top_scores"],
        config["candidate_min_decision_margins"],
        config["candidate_min_compatible_rules"],
    ):
        candidates.append(validation_metrics(records, {
            "min_top_score": float(top),
            "min_decision_margin": float(margin),
            "min_compatible_rules": int(rules),
        }))
    ranked = sorted(candidates, key=lambda row: (
        -row["pseudo_unknown_rejection_rate"],
        row["false_rejection_rate_on_known"],
        -row["selective_accuracy"] if not math.isnan(row["selective_accuracy"]) else math.inf,
        -row["coverage"],
        int(row["min_compatible_rules"] > 0) + int(row["min_decision_margin"] > 0),
        row["min_top_score"], row["min_decision_margin"], row["min_compatible_rules"],
    ))
    return dict(ranked[0]), candidates, records


def final_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    known = [row for row in rows if row["true_family"] != "unknown_family"]
    unknown = [row for row in rows if row["true_family"] == "unknown_family"]
    known_truth = [row["true_family"] for row in known]
    known_pred = [row["predicted_family"] for row in known]
    all_truth = ["unknown" if row["true_family"] == "unknown_family" else row["true_family"] for row in rows]
    all_pred = [row["predicted_family"] for row in rows]
    accepted = [row for row in rows if not row["rejected"]]
    accepted_correct = [
        ("unknown" if row["true_family"] == "unknown_family" else row["true_family"]) == row["predicted_family"]
        for row in accepted
    ]
    return {
        "n": len(rows), "known_n": len(known), "unknown_n": len(unknown),
        "known_accuracy": float(accuracy_score(known_truth, known_pred)),
        "known_macro_f1": float(f1_score(known_truth, known_pred, average="macro", zero_division=0)),
        "unknown_rejection_rate": float(np.mean([row["rejected"] for row in unknown])),
        "false_rejection_rate_on_known": float(np.mean([row["rejected"] for row in known])),
        "fallback_rate": float(np.mean([row["original_family"] == "fallback" for row in rows])),
        "coverage": len(accepted) / len(rows),
        "selective_accuracy": float(np.mean(accepted_correct)) if accepted_correct else math.nan,
        "overall_accuracy_with_unknown_class": float(accuracy_score(all_truth, all_pred)),
    }


def main() -> int:
    ensure_phase_dirs()
    full_config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    p2_config = full_config["p2"]
    source_config = json.loads(ROUTER_CONFIG.read_text(encoding="utf-8"))
    previous = pd.read_csv(SOURCE_PHASE / "raw" / "router_independent_20260910T094257Z_routes.csv")
    source_by_id = {row["source_id"]: row for row in source_config["sources"]}
    current_run = run_id("final_router_open_set")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID, phase="P2", run_id=current_run, dataset="router_multifamily",
        protocol="known_family_leave_one_out_then_frozen_open_set_test", status="RUNNING",
        started_at=started_at, command="python scripts/run_router_open_set_consolidation.py",
        error_path=relative(error_path),
    )
    try:
        routes: list[dict[str, Any]] = []
        for item in previous.to_dict(orient="records"):
            source = source_by_id[str(item["source_id"])]
            neutral_path = ROOT / str(item["neutral_artifact"])
            frame = pd.read_csv(neutral_path)
            route = route_dataframe(frame)
            routes.append({
                "source_id": source["source_id"], "source_group": source["source_group"],
                "true_family": source["true_family"], "path": source["path"],
                "neutral_artifact": relative(neutral_path), "scores": dict(route["scores"]),
                "reasons": list(route["reasons"]), "route": route,
            })

        known_routes = [row for row in routes if row["true_family"] != "unknown_family"]
        final_open_routes = [row for row in routes if row["true_family"] == "unknown_family"]
        if len(final_open_routes) != int(p2_config["final_open_set_count"]):
            raise AssertionError("Le test open-set final ne contient pas exactement trois sources gelées.")
        selected, validation_grid, validation_fold_rows = calibrate_policy(known_routes, p2_config)
        policy = {key: selected[key] for key in ("min_top_score", "min_decision_margin", "min_compatible_rules")}

        final_rows: list[dict[str, Any]] = []
        for row in routes:
            decision = apply_open_set_rejection(row["route"], policy)
            final_rows.append({
                "run_id": current_run, "source_id": row["source_id"], "source_group": row["source_group"],
                "true_family": row["true_family"], "predicted_family": decision["family"],
                "original_family": decision["original_family"], "rejected": decision["rejected"],
                "top_score": decision["top_score"], "second_score": decision["second_score"],
                "decision_margin": decision["decision_margin"],
                "compatible_rule_count": decision["compatible_rule_count"],
                "rejection_reasons": " | ".join(decision["rejection_reasons"]),
                "decision_margin_is_probability": False,
            })
        metrics = final_metrics(final_rows)

        raw_path = PHASE_ROOT / "raw" / f"{current_run}_routes.csv"
        folds_path = PHASE_ROOT / "processed" / "router_open_set_validation_folds.csv"
        grid_path = PHASE_ROOT / "aggregated" / "router_open_set_validation_grid.csv"
        summary_path = PHASE_ROOT / "aggregated" / "router_open_set_summary.json"
        policy_path = PHASE_ROOT / "configs" / "router_open_set_selected_policy.json"
        report_path = PHASE_ROOT / "reports" / "ROUTER_OPEN_SET_EVALUATION.md"
        figure_path = PHASE_ROOT / "figures" / "dataset_16_router_open_set_tradeoff.png"
        write_csv(raw_path, final_rows)
        write_csv(folds_path, validation_fold_rows)
        write_csv(grid_path, validation_grid)
        write_json(policy_path, {
            "run_id": current_run, "selected_on": "known_sources_leave_one_family_out_validation_only",
            "final_open_set_used_for_calibration": False, "policy": policy,
            "validation_metrics": {key: selected[key] for key in selected if key not in policy},
        })

        tradeoff: list[dict[str, Any]] = []
        for threshold in p2_config["candidate_min_top_scores"]:
            diagnostic_policy = dict(policy, min_top_score=float(threshold))
            diagnostic_rows = []
            for row in routes:
                decision = apply_open_set_rejection(row["route"], diagnostic_policy)
                diagnostic_rows.append({
                    "true_family": row["true_family"], "predicted_family": decision["family"],
                    "original_family": decision["original_family"], "rejected": decision["rejected"],
                })
            tradeoff.append({"min_top_score": threshold, **final_metrics(diagnostic_rows)})
        tradeoff_path = PHASE_ROOT / "aggregated" / "router_open_set_final_tradeoff_diagnostic.csv"
        write_csv(tradeoff_path, tradeoff)
        trade_frame = pd.DataFrame(tradeoff)
        fig, ax = plt.subplots(figsize=(8.8, 5.4))
        ax.plot(trade_frame["min_top_score"], trade_frame["known_accuracy"], marker="o", label="Known accuracy")
        ax.plot(trade_frame["min_top_score"], trade_frame["unknown_rejection_rate"], marker="s", label="Unknown rejection")
        ax.plot(trade_frame["min_top_score"], trade_frame["coverage"], marker="^", label="Coverage")
        ax.axvline(policy["min_top_score"], color="black", linestyle="--", label="Seuil figé sur validation")
        ax.set_ylim(-0.03, 1.03)
        ax.set_xlabel("Seuil minimal de top_score")
        ax.set_ylabel("Taux")
        ax.set_title("Routeur open-set — diagnostic après gel du seuil")
        ax.grid(alpha=0.25)
        ax.legend()
        fig.tight_layout()
        fig.savefig(figure_path, dpi=180)
        plt.close(fig)

        summary = {
            "run_id": current_run, "policy": policy,
            "calibration": {
                "method": "leave_one_known_family_out_pseudo_open",
                "known_source_count": len(known_routes),
                "known_family_count": len({row["true_family"] for row in known_routes}),
                "final_open_set_used_for_calibration": False,
                "selected_validation_metrics": selected,
            },
            "final_test": metrics,
            "final_open_set_sources": [row["source_id"] for row in final_open_routes],
            "decision_margin_semantics": "score heuristique de séparation, non une probabilité",
            "tradeoff_is_post_selection_diagnostic": True,
        }
        write_json(summary_path, summary)
        report_path.write_text("\n".join([
            "# Évaluation du rejet open-set du routeur", "",
            f"Run : `{current_run}`.", "", "## Calibrage", "",
            "Les seuils sont sélectionnés exclusivement sur des folds leave-one-family-out construits à partir des familles connues. Dans chaque fold, la famille tenue à l’écart est traitée comme pseudo-inconnue en retirant sa capacité de la liste des scores candidats. Les trois sources open-set finales ne participent ni au calibrage ni au choix de la politique.", "",
            f"Politique figée : `top_score >= {policy['min_top_score']}`, `decision_margin >= {policy['min_decision_margin']}` et au moins `{policy['min_compatible_rules']}` règle compatible. `decision_margin` est un score heuristique de séparation, pas une probabilité.", "",
            "## Test final", "",
            "| Métrique | Valeur |", "| --- | ---: |",
            f"| Known accuracy | {metrics['known_accuracy']:.6f} |",
            f"| Known macro-F1 | {metrics['known_macro_f1']:.6f} |",
            f"| Unknown rejection rate | {metrics['unknown_rejection_rate']:.6f} |",
            f"| False rejection rate on known | {metrics['false_rejection_rate_on_known']:.6f} |",
            f"| Fallback rate | {metrics['fallback_rate']:.6f} |",
            f"| Coverage | {metrics['coverage']:.6f} |",
            f"| Selective accuracy | {metrics['selective_accuracy']:.6f} |", "",
            "La courbe de compromis est un diagnostic postérieur au gel du seuil. Elle ne sert pas à resélectionner la politique sur le test final.", "",
            "## Limite", "",
            "Le test final ne compte que trois fichiers inconnus locaux. Le résultat soutient le fonctionnement du rejet dans ce corpus, pas une capacité open-set générale.",
        ]) + "\n", encoding="utf-8")

        artifacts = [raw_path, folds_path, grid_path, tradeoff_path, summary_path, policy_path, report_path, figure_path]
        manifest_path = PHASE_ROOT / "manifests" / f"{current_run}_manifest.json"
        write_json(manifest_path, {
            "run_id": current_run, "status": "COMPLETED",
            "config": {"path": relative(CONFIG_PATH), "sha256": sha256_file(CONFIG_PATH)},
            "router_sources_config": {"path": relative(ROUTER_CONFIG), "sha256": sha256_file(ROUTER_CONFIG)},
            "final_open_set_used_for_calibration": False,
            "input_artifacts": [{"path": row["neutral_artifact"], "sha256": sha256_file(ROOT / row["neutral_artifact"])} for row in routes],
            "artifacts": [{"path": relative(path), "sha256": sha256_file(path)} for path in artifacts],
        })
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P2", run_id=current_run, dataset="router_multifamily",
            protocol="known_family_leave_one_out_then_frozen_open_set_test", status="COMPLETED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/run_router_open_set_consolidation.py",
            raw_result_path=relative(raw_path), summary_path=relative(summary_path), figure_path=relative(figure_path),
            error_path=relative(error_path), notes=f"Thresholds validation-only; unknown rejection={metrics['unknown_rejection_rate']:.6f}.",
        )
        print(json.dumps({"status": "COMPLETED", "run_id": current_run, "policy": policy, "metrics": metrics}, ensure_ascii=False))
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P2", run_id=current_run, dataset="router_multifamily",
            protocol="known_family_leave_one_out_then_frozen_open_set_test", status="FAILED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/run_router_open_set_consolidation.py",
            error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
