#!/usr/bin/env python3
"""Analyse exploratoire de sensibilité aux vecteurs CSE-CIC-IDS2018 répétés."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dataset_strengthening_common import (  # noqa: E402
    PHASE_ROOT,
    append_ledger,
    descriptive,
    metrics_from_prediction,
    relative,
    run_id,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)
from run_external_csecicids2018_strengthening import (  # noqa: E402
    candidate_models,
    prediction_scores,
    seed_sample,
)

EXPERIMENT_ID = "dataset_07b_external_duplicate_sensitivity"
META_COLUMNS = {"target", "__source_row", "__priority"}


def deduplicate_unambiguous(frame: pd.DataFrame, feature_columns: list[str]) -> tuple[pd.DataFrame, dict[str, int]]:
    result = frame.copy()
    result["__feature_hash"] = pd.util.hash_pandas_object(result[feature_columns], index=False).to_numpy()
    target_counts = result.groupby("__feature_hash")["target"].nunique()
    conflicting = set(target_counts[target_counts > 1].index.tolist())
    conflicting_rows = int(result["__feature_hash"].isin(conflicting).sum())
    result = result.loc[~result["__feature_hash"].isin(conflicting)].drop_duplicates("__feature_hash", keep="first")
    result = result.drop(columns="__feature_hash").reset_index(drop=True)
    return result, {
        "input_rows": len(frame),
        "unique_unambiguous_rows": len(result),
        "conflicting_hashes": len(conflicting),
        "conflicting_rows_dropped": conflicting_rows,
    }


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    output: list[dict[str, Any]] = []
    for (condition, model), group in frame.groupby(["condition", "model"], sort=True):
        row: dict[str, Any] = {
            "dataset": "CSE-CIC-IDS2018",
            "analysis": "duplicate_vector_sensitivity",
            "condition": condition,
            "model": model,
            "seeds": ",".join(str(seed) for seed in sorted(group["seed"].unique())),
        }
        for metric in ("precision", "recall", "f1", "pr_auc", "mcc", "fpr"):
            for name, value in descriptive(group[metric].astype(float)).items():
                row[f"{metric}_{name}"] = value
        output.append(row)
    return output


def main() -> int:
    candidates = sorted(PHASE_ROOT.glob("manifests/external_csecicids2018_*_manifest.json"))
    if not candidates:
        raise FileNotFoundError("Manifeste principal CSE-CIC-IDS2018 absent.")
    principal_manifest = json.loads(candidates[-1].read_text(encoding="utf-8"))
    principal_run = principal_manifest["run_id"]
    train_path = PHASE_ROOT / "processed" / f"{principal_run}_train_pool.csv.gz"
    test_path = PHASE_ROOT / "processed" / f"{principal_run}_test_pool.csv.gz"
    train_pool = pd.read_csv(train_path)
    test_pool = pd.read_csv(test_path)
    features = [column for column in train_pool.columns if column not in META_COLUMNS]
    train_unique, train_audit = deduplicate_unambiguous(train_pool, features)
    test_unique, test_audit = deduplicate_unambiguous(test_pool, features)

    current_run = run_id("external_csecicids2018_sensitivity")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID,
        phase="7b/7",
        run_id=current_run,
        dataset="CSE-CIC-IDS2018",
        protocol="post_hoc_duplicate_vector_sensitivity",
        status="RUNNING",
        started_at=started_at,
        command="python scripts/run_external_csecicids2018_sensitivity.py",
        error_path=relative(error_path),
        notes="Analyse exploratoire post hoc; ne remplace pas le résultat principal.",
    )
    try:
        rows: list[dict[str, Any]] = []
        conditions = {
            "deduplicated_test_only": (train_pool, test_unique),
            "deduplicated_train_and_test": (train_unique, test_unique),
        }
        for condition, (train_source, test_source) in conditions.items():
            for seed in (42, 43, 44, 45, 46):
                train = seed_sample(train_source, per_class=10_000, seed=seed)
                test = seed_sample(test_source, per_class=10_000, seed=seed)
                x_train = train[features]
                y_train = train["target"].astype(np.int8)
                x_test = test[features]
                y_test = test["target"].astype(np.int8)
                for model_name, model in candidate_models(seed).items():
                    started = perf_counter()
                    model.fit(x_train, y_train)
                    prediction = np.asarray(model.predict(x_test), dtype=np.int8)
                    scores = prediction_scores(model, x_test)
                    rows.append(
                        {
                            "run_id": current_run,
                            "condition": condition,
                            "model": model_name,
                            "seed": seed,
                            "train_rows": len(train),
                            "test_rows": len(test),
                            **metrics_from_prediction(y_test.to_numpy(), prediction, scores),
                            "elapsed_sec": perf_counter() - started,
                        }
                    )
        raw_path = PHASE_ROOT / "raw" / f"{current_run}_metrics.csv"
        summary_path = PHASE_ROOT / "aggregated/external_csecicids2018_duplicate_sensitivity.csv"
        manifest_path = PHASE_ROOT / "manifests" / f"{current_run}_manifest.json"
        write_csv(raw_path, rows)
        summary = aggregate(rows)
        write_csv(summary_path, summary)
        write_json(
            manifest_path,
            {
                "run_id": current_run,
                "principal_run_id": principal_run,
                "status": "post_hoc_exploratory_sensitivity",
                "train_pool": {"path": relative(train_path), "sha256": sha256_file(train_path)},
                "test_pool": {"path": relative(test_path), "sha256": sha256_file(test_path)},
                "train_deduplication": train_audit,
                "test_deduplication": test_audit,
                "cross_partition_exact_feature_overlap": 0,
                "conditions": list(conditions),
                "result": relative(summary_path),
            },
        )
        append_ledger(
            experiment_id=EXPERIMENT_ID,
            phase="7b/7",
            run_id=current_run,
            dataset="CSE-CIC-IDS2018",
            protocol="post_hoc_duplicate_vector_sensitivity",
            status="COMPLETED",
            started_at=started_at,
            completed_at=utc_now(),
            command="python scripts/run_external_csecicids2018_sensitivity.py",
            raw_result_path=relative(raw_path),
            summary_path=relative(summary_path),
            error_path=relative(error_path),
            notes="Analyse exploratoire post hoc; vecteurs ambigus écartés; résultat principal inchangé.",
        )
        print(f"COMPLETED {current_run} {summary_path}")
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID,
            phase="7b/7",
            run_id=current_run,
            dataset="CSE-CIC-IDS2018",
            protocol="post_hoc_duplicate_vector_sensitivity",
            status="FAILED",
            started_at=started_at,
            completed_at=utc_now(),
            command="python scripts/run_external_csecicids2018_sensitivity.py",
            error_path=relative(error_path),
            notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
