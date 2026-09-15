"""Train a real phase-4 candidate from the frozen CICIDS train bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from evaluate_cicids_model_candidates import _candidate_models


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def train(bundle_path: Path, model_name: str, output_path: Path) -> dict[str, object]:
    bundle = np.load(bundle_path, allow_pickle=False)
    feature_columns = bundle["feature_columns"].astype(str).tolist()
    x_train = pd.DataFrame(bundle["X_train"], columns=feature_columns)
    y_train = bundle["y_train"].astype(int)
    candidates = _candidate_models(seed=42)
    if model_name not in candidates:
        raise ValueError(f"Unknown candidate: {model_name}")
    model = candidates[model_name]
    model.fit(x_train, y_train)
    artifact = {
        "model": model,
        "model_type": f"supervised_tabular_{model_name.lower()}",
        "estimator_name": model_name,
        "feature_columns": feature_columns,
        "seed": 42,
        "training_bundle": str(bundle_path),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)
    result = {
        "model": model_name,
        "model_path": str(output_path),
        "sha256": sha256_file(output_path),
        "train_rows": int(len(y_train)),
        "positive_rate": float(y_train.mean()),
    }
    output_path.with_suffix(".training.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument(
        "--model",
        required=True,
        choices=["RandomForest", "ExtraTrees", "HistGradientBoosting", "LogisticRegression", "SGDLogistic"],
    )
    parser.add_argument("--model-out", required=True, type=Path)
    args = parser.parse_args()
    result = train(ROOT / args.bundle if not args.bundle.is_absolute() else args.bundle, args.model, ROOT / args.model_out if not args.model_out.is_absolute() else args.model_out)
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
