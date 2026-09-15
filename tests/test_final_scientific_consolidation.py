"""Garde-fous de la consolidation scientifique finale P1–P4."""

from __future__ import annotations

import inspect
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "scripts", ROOT / "src"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from logminer.agents.model_router import apply_open_set_rejection  # noqa: E402
from run_final_csecicids2018_lr_forensic import permute_training_labels  # noqa: E402
from run_hdfs_block_robustness import bootstrap_block_metrics  # noqa: E402
from run_multisource_cnp_model_inference import validate_registry  # noqa: E402
from run_router_open_set_consolidation import calibrate_policy  # noqa: E402

PHASE = ROOT / "experiments/phase_final_scientific_consolidation"
CONFIG = json.loads((PHASE / "configs/final_scientific_consolidation_protocol.json").read_text(encoding="utf-8"))


def test_label_permutation_changes_order_and_preserves_class_counts() -> None:
    labels = pd.Series(([0, 1] * 100), dtype=np.int8)
    permuted = permute_training_labels(labels, 42)
    assert not np.array_equal(labels.to_numpy(), permuted.to_numpy())
    assert labels.value_counts().to_dict() == permuted.value_counts().to_dict()


def test_single_feature_audit_contains_all_78_features_and_five_seeds() -> None:
    frame = pd.read_csv(PHASE / "aggregated/external_csecicids2018_single_feature_scores.csv")
    assert len(frame) == 78
    assert set(frame["seeds"].astype(str)) == {"42,43,44,45,46"}
    assert {"f1_mean", "pr_auc_mean", "mcc_mean", "recall_mean", "fpr_mean"}.issubset(frame.columns)


def test_feature_ablation_configuration_was_frozen() -> None:
    assert CONFIG["frozen_before_execution"] is True
    assert CONFIG["p1"]["ablation_levels"] == [0, 1, 3, 5, 10]
    assert CONFIG["p1"]["ablation_ranking_source"] == "absolute_coefficients_from_training_fit_only"
    summary = json.loads((PHASE / "aggregated/external_csecicids2018_lr_forensic_summary.json").read_text(encoding="utf-8"))
    assert summary["assertions"]["test_used_for_feature_ranking"] is False


def test_open_set_calibration_api_has_no_final_test_argument() -> None:
    assert set(inspect.signature(calibrate_policy).parameters) == {"known_routes", "config"}
    assert CONFIG["p2"]["final_open_set_sources_used_for_calibration"] is False


def test_selected_open_set_policy_records_validation_only() -> None:
    policy = json.loads((PHASE / "configs/router_open_set_selected_policy.json").read_text(encoding="utf-8"))
    assert policy["selected_on"] == "known_sources_leave_one_family_out_validation_only"
    assert policy["final_open_set_used_for_calibration"] is False


def test_open_set_rejection_preserves_route_and_marks_margin_non_probability() -> None:
    route = {"family": "network", "model": "model", "scores": {"network": 84, "fallback": 1}, "reasons": ["features reseau=7"]}
    result = apply_open_set_rejection(route, {"min_top_score": 100, "min_decision_margin": 0, "min_compatible_rules": 0})
    assert route["family"] == "network"
    assert result["family"] == "unknown"
    assert result["rejected"] is True
    assert result["decision_margin_is_probability"] is False


def test_model_registry_artifacts_and_schemas_are_explicit() -> None:
    entries = json.loads((PHASE / "configs/multisource_model_compatibility_registry.json").read_text(encoding="utf-8"))["entries"]
    observed = validate_registry(entries)
    assert len(observed) == 8
    assert all(row["feature_schema"] and row["expected_input"] and row["output_type"] for row in observed)
    assert sum(bool(row["compatible"]) for row in observed) == 7
    assert next(row for row in observed if row["source_family"] == "apache")["reason_if_incompatible"]


def test_true_inference_marker_has_loaded_model_and_hash() -> None:
    summary = json.loads((PHASE / "aggregated/multisource_cnp_model_inference_summary.json").read_text(encoding="utf-8"))
    traces = pd.read_csv(PHASE / "raw" / f"{summary['run_id']}_unit_trace.csv")
    executed = traces.loc[(traces["condition"] == "M") & traces["inference_executed"]]
    assert len(executed) == 1400
    assert executed["model_loaded"].notna().all()
    assert executed["artifact_sha256"].astype(str).str.fullmatch(r"[0-9a-f]{64}").all()
    assert (executed["prediction_type"].astype(str) != "heuristic_candidate").all()


def test_hdfs_bootstrap_uses_frozen_threshold_for_every_replicate() -> None:
    threshold = float(CONFIG["p4"]["threshold"])
    blocks = pd.DataFrame({"block_id": ["a", "b", "c", "d"], "label": [0, 0, 1, 1], "mean_score": [0.1, 0.2, 2.0, 3.0]})
    rows = bootstrap_block_metrics(blocks, threshold, replicates=20, seed=7)
    assert len(rows) == 20
    assert {row["threshold"] for row in rows} == {threshold}
    assert CONFIG["p4"]["threshold_refit_in_bootstrap"] is False


def test_hdfs_robustness_reproduces_source_and_keeps_drain_frozen() -> None:
    summary = json.loads((PHASE / "aggregated/hdfs_block_robustness_summary.json").read_text(encoding="utf-8"))
    assert summary["test_positive_blocks"] == 29
    assert summary["bootstrap"]["replicates"] == 1000
    assert summary["leave_one_positive_out"]["evaluations"] == 29
    assert summary["assertions"]["baseline_reproduces_source_f1"] is True
    assert summary["assertions"]["threshold_frozen"] is True
    assert summary["assertions"]["drain_state_unchanged"] is True
