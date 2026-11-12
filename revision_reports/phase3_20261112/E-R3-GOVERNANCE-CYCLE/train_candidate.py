"""Entraine un candidat d'E-R3-GOVERNANCE-CYCLE a partir d'un paquet d'entrainement fige.

Appele par `scripts/monthly_model_retraining.py` (commande `train_command` du plan),
exactement comme un reentrainement reel. Les noms de candidats sont fixes par le
protocole ; aucun hyperparametre n'est choisi apres lecture d'un resultat.
"""

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
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from evaluate_cicids_model_candidates import _candidate_models  # noqa: E402

CANDIDATES = (
    "LogisticRegression",
    "Stump",
    "RandomForest",
    "RandomForest_small",
    "ExtraTrees",
    "HistGradientBoosting",
)
SMALL_FRACTION = 0.01


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_model(name: str, seed: int):
    if name == "Stump":
        return DecisionTreeClassifier(max_depth=1, random_state=seed)
    if name == "RandomForest_small":
        return _candidate_models(seed=seed)["RandomForest"]
    return _candidate_models(seed=seed)[name]


def train(bundle_path: Path, name: str, seed: int, output_path: Path) -> dict[str, object]:
    bundle = np.load(bundle_path, allow_pickle=False)
    feature_columns = bundle["feature_columns"].astype(str).tolist()
    x_train = pd.DataFrame(bundle["X_train"], columns=feature_columns)
    y_train = pd.Series(bundle["y_train"].astype(int))
    if name == "RandomForest_small":
        x_train, _, y_train, _ = train_test_split(
            x_train, y_train, train_size=SMALL_FRACTION, stratify=y_train, random_state=seed
        )
    model = build_model(name, seed)
    model.fit(x_train, y_train.to_numpy())
    artifact = {
        "model": model,
        "model_type": f"supervised_tabular_{name.lower()}",
        "estimator_name": name,
        "feature_columns": feature_columns,
        "seed": seed,
        "training_bundle": str(bundle_path),
        "train_rows": int(len(y_train)),
        "trained_at": datetime.now(timezone.utc).isoformat(),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, output_path)
    result = {
        "candidate": name,
        "seed": seed,
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
    parser.add_argument("--candidate", required=True, choices=CANDIDATES)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--model-out", required=True, type=Path)
    args = parser.parse_args()
    result = train(args.bundle.resolve(), args.candidate, args.seed, args.model_out.resolve())
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
