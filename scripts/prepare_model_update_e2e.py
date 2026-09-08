"""Prepare isolated current models and a frozen CICIDS DDoS evaluation for phase 4."""

from __future__ import annotations

import hashlib
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from evaluate_cicids_model_candidates import _candidate_models
from run_final_experiments import load_holdout


PHASE_DIR = ROOT / "data" / "processed" / "final_experiments_2026" / "phase_4"
LEDGER_PATH = ROOT / "docs" / "memoire" / "final_experiments_2026" / "state" / "EXPERIMENT_LEDGER.csv"


def register_plans() -> None:
    with LEDGER_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        columns = list(rows[0]) if rows else []
    existing = {row["experiment_id"] for row in rows if row["phase"] == "4"}
    with LEDGER_PATH.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        for case in ("promotion", "rejection", "min_delta"):
            experiment_id = f"e4_model_update_{case}"
            if experiment_id in existing:
                continue
            values = {
                "experiment_id": experiment_id,
                "phase": "4",
                "run_id": experiment_id,
                "dataset": "CICIDS2017",
                "scenario": "DDoS_holdout_seed42",
                "seed": "42",
                "model": "controlled_model_update",
                "status": "PLANNED",
                "command": "scripts/monthly_model_retraining.py --plan docs/memoire/final_experiments_2026/configs/model_update_e2e_plan.json --promote",
                "config_path": "docs/memoire/final_experiments_2026/configs/model_update_e2e_plan.json",
                "raw_result_path": f"data/processed/final_experiments_2026/phase_4/model_update_{case}_case.json" if case != "min_delta" else "data/processed/final_experiments_2026/phase_4/model_update_min_delta_case.json",
                "summary_path": "data/processed/final_experiments_2026/phase_4/model_update_integrity_report.json",
                "notes": "isolated functional branch test registered before candidate training",
            }
            writer.writerow({column: values.get(column, "") for column in columns})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_artifact(model_name: str, x_train: pd.DataFrame, y_train: pd.Series, path: Path) -> dict[str, object]:
    model = _candidate_models(seed=42)[model_name]
    model.fit(x_train, y_train)
    artifact = {
        "model": model,
        "model_type": f"supervised_tabular_{model_name.lower()}",
        "estimator_name": model_name,
        "feature_columns": list(x_train.columns),
        "seed": 42,
        "training_protocol": "CICIDS2017 DDoS file holdout, phase-2-compatible settings",
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, path)
    return {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256_before": sha256_file(path), "estimator": model_name}


def main() -> int:
    register_plans()
    x_train, y_train, x_test, y_test, details = load_holdout(SimpleNamespace(scenario="DDoS", seed=42))
    PHASE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        PHASE_DIR / "frozen_ddos_train_bundle.npz",
        X_train=x_train.to_numpy(dtype=float),
        y_train=y_train.to_numpy(dtype=int),
        feature_columns=np.asarray(list(x_train.columns)),
    )
    evaluation = x_test.copy()
    evaluation["label"] = y_test.to_numpy(dtype=int)
    evaluation.to_csv(PHASE_DIR / "frozen_ddos_evaluation.csv", index=False, encoding="utf-8-sig")

    current_models = {
        "promotion": write_artifact("ExtraTrees", x_train, y_train, PHASE_DIR / "cases" / "promotion" / "current.joblib"),
        "rejection": write_artifact("RandomForest", x_train, y_train, PHASE_DIR / "cases" / "rejection" / "current.joblib"),
        "min_delta": write_artifact("ExtraTrees", x_train, y_train, PHASE_DIR / "cases" / "min_delta" / "current.joblib"),
    }
    payload = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": "CICIDS2017 local files",
        "scenario": "DDoS file holdout",
        "seed": 42,
        "train_rows": int(len(y_train)),
        "test_rows": int(len(y_test)),
        "feature_count": int(x_train.shape[1]),
        "train_positive_rate": float(y_train.mean()),
        "test_positive_rate": float(y_test.mean()),
        "evaluation_sha256": sha256_file(PHASE_DIR / "frozen_ddos_evaluation.csv"),
        "bundle_sha256": sha256_file(PHASE_DIR / "frozen_ddos_train_bundle.npz"),
        "details": details,
        "current_models": current_models,
        "candidate_models_before_execution": "ABSENT",
        "production_models_touched": False,
    }
    (PHASE_DIR / "model_update_preparation.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
