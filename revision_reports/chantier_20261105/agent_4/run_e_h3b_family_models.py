"""E-H3b: modèle commun contre modèles spécialisés par famille, cinq graines."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/phase_revision_20261105/E-H3B-FAMILY-MODELS"
PROTOCOL = ROOT / "revision_reports/chantier_20261105/agent_4/protocoles/E-H3B-FAMILY-MODELS.md"
SCRIPT = Path(__file__).resolve()
SOURCE_SCRIPT = ROOT / "scripts/run_family_routing_ablation.py"
SEEDS = (42, 43, 44, 45, 46)
PER_CLASS = 6000
NON_INFERIORITY_MARGIN = -0.01


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_source_module():
    spec = importlib.util.spec_from_file_location("family_ablation_source", SOURCE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Impossible de charger le script source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def paired_interval(values: np.ndarray) -> dict[str, float]:
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    t_critical = 2.7764451051977987
    half = t_critical * sd / math.sqrt(len(values))
    return {"mean": mean, "sd": sd, "ci95_lower": mean - half, "ci95_upper": mean + half}


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    source = load_source_module()
    linux_path = ROOT / "data/raw/Datasets/linux_auth_logs_labeled.csv"
    cicids_dir = ROOT / "data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"
    unsw_train = ROOT / "data/raw/Datasets/UNSW_NB15_training-set.parquet"
    unsw_test = ROOT / "data/raw/Datasets/UNSW_NB15_testing-set.parquet"

    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        frames = [
            source.load_linux_auth(linux_path, normal=PER_CLASS, anomaly=PER_CLASS, random_state=seed),
            source.load_cicids(cicids_dir, normal=PER_CLASS, anomaly=PER_CLASS, random_state=seed),
            source.load_unsw(unsw_train, unsw_test, normal=PER_CLASS, anomaly=PER_CLASS, random_state=seed),
        ]
        dataset = pd.concat(frames, ignore_index=True).sample(frac=1, random_state=seed)
        dataset = dataset.replace([np.inf, -np.inf], np.nan)
        train_parts = []
        test_parts = []
        from sklearn.model_selection import train_test_split

        for _family, group in dataset.groupby("family"):
            train, test = train_test_split(
                group, test_size=0.25, stratify=group["target"].astype(str), random_state=seed
            )
            train_parts.append(train)
            test_parts.append(test)
        train_df = pd.concat(train_parts, ignore_index=True)
        test_df = pd.concat(test_parts, ignore_index=True)

        global_model = source.make_model(seed)
        global_model.fit(train_df[source.COMMON_FEATURES], train_df["target"])
        for family, test_group in test_df.groupby("family"):
            features = test_group[source.COMMON_FEATURES]
            prediction = global_model.predict(features)
            rows.append(source._metric_row(
                "global_common_model", family, test_group["target"], prediction, len(test_group),
                seed=seed, y_score=source._positive_scores(global_model, features),
            ))

        for family, train_group in train_df.groupby("family"):
            model = source.make_model(seed)
            model.fit(train_group[source.COMMON_FEATURES], train_group["target"])
            test_group = test_df[test_df["family"] == family]
            features = test_group[source.COMMON_FEATURES]
            prediction = model.predict(features)
            rows.append(source._metric_row(
                "family_aware_models", family, test_group["target"], prediction, len(test_group),
                seed=seed, y_score=source._positive_scores(model, features),
            ))
        print(f"seed {seed} complete", flush=True)

    metrics = pd.DataFrame(rows)
    metrics_path = OUT / "metrics_by_seed_family.csv"
    metrics.to_csv(metrics_path, index=False, encoding="utf-8")
    pivot = metrics.pivot(index=["seed", "family"], columns="variant", values="f1").reset_index()
    pivot["delta_family_minus_global"] = pivot["family_aware_models"] - pivot["global_common_model"]
    deltas_path = OUT / "paired_f1_deltas.csv"
    pivot.to_csv(deltas_path, index=False, encoding="utf-8")

    family_results = {}
    for family, group in pivot.groupby("family"):
        interval = paired_interval(group["delta_family_minus_global"].to_numpy(dtype=float))
        interval["non_inferior_margin"] = NON_INFERIORITY_MARGIN
        interval["non_inferior"] = bool(interval["ci95_lower"] >= NON_INFERIORITY_MARGIN)
        family_results[str(family)] = interval
    overall_by_seed = pivot.groupby("seed")["delta_family_minus_global"].mean().to_numpy(dtype=float)
    overall = paired_interval(overall_by_seed)
    criterion_met = all(item["non_inferior"] for item in family_results.values())
    summary = {
        "experiment_id": "E-H3B-FAMILY-MODELS",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "seeds": list(SEEDS),
        "per_class_per_family": PER_CLASS,
        "common_features": list(source.COMMON_FEATURES),
        "paired_f1_delta_family_minus_global": family_results,
        "overall_macro_family_delta": overall,
        "criterion": "Pour chaque famille, borne inférieure de l'IC t apparié à 95 % du delta F1 >= -0,01.",
        "criterion_met": criterion_met,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    input_paths = [linux_path, unsw_train, unsw_test, *sorted(cicids_dir.glob("*.csv"))]
    manifest_rows = []
    for role, path in [
        ("protocol", PROTOCOL), ("runner", SCRIPT), ("source_script", SOURCE_SCRIPT),
        *(("input", path) for path in input_paths),
        ("artifact", metrics_path), ("artifact", deltas_path), ("artifact", summary_path),
    ]:
        manifest_rows.append({"role": role, "path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest_path = OUT / "MANIFEST_SHA256.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "path", "sha256", "bytes"])
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
