#!/usr/bin/env python3
"""Campagne CICIDS2017 temporelle, légère et reproductible.

Le pool d'apprentissage est construit sur lundi--jeudi et le pool de test sur
vendredi. Les fichiers/jours servent exclusivement au partitionnement. Un seul
balayage par partition construit un pool à priorités aléatoires figé; chaque
graine tire ensuite un sous-échantillon équilibré sans remise dans ce pool.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dataset_strengthening_common import (  # noqa: E402
    PHASE_ROOT,
    append_ledger,
    descriptive,
    ensure_phase_dirs,
    metrics_from_prediction,
    relative,
    run_id,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)
from evaluate_supervised_strict_splits import (  # noqa: E402
    _clean_columns,
    _label_column,
    _network_feature_columns,
    _network_features,
)

EXPERIMENT_ID = "dataset_03_cicids_temporal"


def temporal_files(directory: Path) -> tuple[list[Path], list[Path]]:
    files = sorted(directory.glob("*.csv"))
    train = [path for path in files if not path.name.lower().startswith("friday")]
    test = [path for path in files if path.name.lower().startswith("friday")]
    if not train or not test:
        raise RuntimeError("Le découpage lundi--jeudi / vendredi ne peut pas être construit.")
    overlap = {path.resolve() for path in train} & {path.resolve() for path in test}
    if overlap:
        raise AssertionError(f"Fichiers présents dans les deux partitions: {overlap}")
    return train, test


def build_priority_pool(
    files: list[Path], feature_columns: list[str], *, per_class: int, seed: int, chunksize: int
) -> tuple[pd.DataFrame, dict[str, int]]:
    """Conserve les ``per_class`` plus petites priorités d'un balayage complet."""

    rng = np.random.default_rng(seed)
    reservoirs: dict[int, pd.DataFrame] = {0: pd.DataFrame(), 1: pd.DataFrame()}
    label_counts: dict[str, int] = {}
    for path in files:
        source_row = 0
        for chunk in pd.read_csv(
            path, dtype=str, keep_default_na=False, chunksize=chunksize, encoding_errors="ignore"
        ):
            chunk = _clean_columns(chunk)
            label_column = _label_column(chunk.columns)
            labels = chunk[label_column].astype(str).str.strip()
            for label, count in labels.value_counts().items():
                label_counts[str(label)] = label_counts.get(str(label), 0) + int(count)
            targets = labels.str.upper().ne("BENIGN").astype(np.int8)
            features = _network_features(chunk, feature_columns)
            features["target"] = targets.to_numpy()
            features["__source_file"] = path.name
            features["__source_row"] = np.arange(source_row, source_row + len(chunk), dtype=np.int64)
            features["__priority"] = rng.random(len(chunk))
            source_row += len(chunk)
            for target in (0, 1):
                candidate = features.loc[features["target"] == target]
                if candidate.empty:
                    continue
                merged = pd.concat([reservoirs[target], candidate], ignore_index=True)
                reservoirs[target] = merged.nsmallest(per_class, "__priority").reset_index(drop=True)
    if reservoirs[0].empty or reservoirs[1].empty:
        raise RuntimeError("Une classe CICIDS manque dans le pool temporel.")
    pool = pd.concat([reservoirs[0], reservoirs[1]], ignore_index=True)
    return pool, label_counts


def seed_sample(pool: pd.DataFrame, *, per_class: int, seed: int) -> pd.DataFrame:
    parts = []
    for target in (0, 1):
        group = pool.loc[pool["target"] == target]
        parts.append(group.sample(n=min(per_class, len(group)), replace=False, random_state=seed + target))
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


def candidate_models(seed: int) -> dict[str, Any]:
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=120,
            max_depth=28,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=seed,
            n_jobs=1,
        ),
        "LogisticRegression": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        solver="lbfgs",
                        random_state=seed,
                    ),
                ),
            ]
        ),
    }


def score_model(model: Any, x_test: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return np.asarray(model.predict_proba(x_test), dtype=float)[:, 1]
    values = np.asarray(model.decision_function(x_test), dtype=float)
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40, 40)))


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    output: list[dict[str, Any]] = []
    for model, group in frame.groupby("model", sort=True):
        row: dict[str, Any] = {"dataset": "CICIDS2017", "protocol": "temporal_holdout", "model": model}
        row["seeds"] = ",".join(str(value) for value in sorted(group["seed"].unique()))
        for metric in ("precision", "recall", "f1", "pr_auc", "mcc", "fpr", "train_time_sec", "test_time_sec"):
            stats = descriptive(group[metric].astype(float))
            for key, value in stats.items():
                row[f"{metric}_{key}"] = value
        output.append(row)
    return output


def comparison_rows(temporal_summary: list[dict[str, Any]]) -> list[dict[str, Any]]:
    random_path = ROOT / "data/processed/final_experiments_2026/cicids_random_multiseed_summary.csv"
    scenario_path = ROOT / "data/processed/final_experiments_2026/cicids_random_vs_holdout_summary.csv"
    rows: list[dict[str, Any]] = []
    random = pd.read_csv(random_path).iloc[0]
    scenario = pd.read_csv(scenario_path)
    scenario = scenario.loc[scenario["split"] == "file_or_scenario_holdout"].iloc[0]
    for name, source in (("Random stratifié (historique)", random), ("Holdout scénario (historique)", scenario)):
        rows.append(
            {
                "protocol": name,
                "model": "RandomForest",
                "n": int(source["n"]),
                "f1": float(source["f1_mean"]),
                "pr_auc": float(source["pr_auc_mean"]),
                "mcc": float(source["mcc_mean"]),
                "recall": float(source["recall_mean"]),
                "fpr": float(source["fpr_mean"]),
                "comparability": "question_statistique_différente",
            }
        )
    for source in temporal_summary:
        rows.append(
            {
                "protocol": "Holdout temporel lundi-jeudi→vendredi",
                "model": source["model"],
                "n": int(source["f1_n"]),
                "f1": source["f1_mean"],
                "pr_auc": source["pr_auc_mean"],
                "mcc": source["mcc_mean"],
                "recall": source["recall_mean"],
                "fpr": source["fpr_mean"],
                "comparability": "nouveau_protocole_temporel",
            }
        )
    return rows


def plot_comparison(rows: list[dict[str, Any]], output: Path) -> None:
    frame = pd.DataFrame(rows)
    labels = [f"{row.protocol}\n{row.model}" for row in frame.itertuples()]
    x = np.arange(len(frame))
    width = 0.19
    fig, ax = plt.subplots(figsize=(11, 5.8))
    for offset, metric, color in zip((-1.5, -0.5, 0.5, 1.5), ("f1", "pr_auc", "mcc", "recall"), ("#4C78A8", "#F58518", "#54A24B", "#B279A2")):
        ax.bar(x + offset * width, frame[metric], width, label=metric.upper(), color=color)
    ax.set_xticks(x, labels, rotation=12, ha="right")
    ax.set_ylim(-0.1, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("CICIDS2017 — protocoles répondant à des questions distinctes")
    ax.legend(ncol=4)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--chunksize", type=int, default=100_000)
    args = parser.parse_args()
    ensure_phase_dirs()
    directory = ROOT / "data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"
    train_files, test_files = temporal_files(directory)
    feature_columns = _network_feature_columns(train_files[0])
    if len(feature_columns) != 78:
        raise AssertionError(f"78 caractéristiques attendues, {len(feature_columns)} observées")
    plan = {
        "train_files": [relative(path) for path in train_files],
        "test_files": [relative(path) for path in test_files],
        "feature_count": len(feature_columns),
        "seeds": [42, 43, 44, 45, 46],
        "models": ["RandomForest", "LogisticRegression"],
    }
    if args.dry_run:
        print(pd.Series(plan).to_json(force_ascii=False, indent=2))
        return 0

    current_run = run_id("cicids_temporal")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID,
        phase="3/7",
        run_id=current_run,
        dataset="CICIDS2017",
        protocol="temporal_holdout_MonThu_vs_Fri",
        status="RUNNING",
        started_at=started_at,
        command="python scripts/run_cicids_temporal_strengthening.py",
        error_path=relative(error_path),
    )
    try:
        # 50 000 observations par classe permettent cinq tirages de 10 000 sans
        # relire les fichiers; les tirages ne sont pas revendiqués indépendants.
        train_pool, train_labels = build_priority_pool(train_files, feature_columns, per_class=50_000, seed=1042, chunksize=args.chunksize)
        test_pool, test_labels = build_priority_pool(test_files, feature_columns, per_class=50_000, seed=2042, chunksize=args.chunksize)
        train_pool_path = PHASE_ROOT / "processed" / f"{current_run}_train_pool.csv.gz"
        test_pool_path = PHASE_ROOT / "processed" / f"{current_run}_test_pool.csv.gz"
        train_pool.to_csv(train_pool_path, index=False, compression="gzip", encoding="utf-8")
        test_pool.to_csv(test_pool_path, index=False, compression="gzip", encoding="utf-8")
        rows: list[dict[str, Any]] = []
        meta = {"target", "__source_file", "__source_row", "__priority"}
        for seed in plan["seeds"]:
            train = seed_sample(train_pool, per_class=10_000, seed=seed)
            test = seed_sample(test_pool, per_class=10_000, seed=seed)
            x_train = train[[column for column in train.columns if column not in meta]]
            y_train = train["target"].astype(np.int8)
            x_test = test[x_train.columns]
            y_test = test["target"].astype(np.int8)
            for model_name, model in candidate_models(seed).items():
                train_started = perf_counter()
                model.fit(x_train, y_train)
                train_time = perf_counter() - train_started
                test_started = perf_counter()
                prediction = np.asarray(model.predict(x_test), dtype=np.int8)
                scores = score_model(model, x_test)
                test_time = perf_counter() - test_started
                metrics = metrics_from_prediction(y_test.to_numpy(), prediction, scores)
                rows.append(
                    {
                        "run_id": current_run,
                        "dataset": "CICIDS2017",
                        "protocol": "temporal_holdout",
                        "model": model_name,
                        "seed": seed,
                        "feature_count": len(feature_columns),
                        "train_rows": len(train),
                        "test_rows": len(test),
                        "train_files": "|".join(path.name for path in train_files),
                        "test_files": "|".join(path.name for path in test_files),
                        **metrics,
                        "train_time_sec": train_time,
                        "test_time_sec": test_time,
                    }
                )
        raw_path = PHASE_ROOT / "raw" / f"{current_run}_metrics.csv"
        summary_path = PHASE_ROOT / "aggregated" / "cicids_temporal_summary.csv"
        comparison_path = PHASE_ROOT / "aggregated" / "cicids_protocol_comparison.csv"
        figure_path = PHASE_ROOT / "figures" / "dataset_05_cicids_protocol_comparison.png"
        write_csv(raw_path, rows)
        summary = aggregate(rows)
        comparison = comparison_rows(summary)
        write_csv(summary_path, summary)
        write_csv(comparison_path, comparison)
        plot_comparison(comparison, figure_path)
        manifest = {
            "run_id": current_run,
            "protocol": plan,
            "sampling": "single frozen priority pool then five without-replacement subsamples; seeds share the parent pool",
            "preprocessing": "non-finite→0; clip[-1e12,1e12]; StandardScaler fitted inside LR pipeline on train only",
            "train_label_counts_full_scan": train_labels,
            "test_label_counts_full_scan": test_labels,
            "files": [
                {"path": relative(path), "sha256": sha256_file(path), "partition": "train"} for path in train_files
            ] + [{"path": relative(path), "sha256": sha256_file(path), "partition": "test"} for path in test_files],
            "pool_artifacts": [
                {"path": relative(train_pool_path), "sha256": sha256_file(train_pool_path)},
                {"path": relative(test_pool_path), "sha256": sha256_file(test_pool_path)},
            ],
        }
        write_json(PHASE_ROOT / "manifests" / f"{current_run}_manifest.json", manifest)
        append_ledger(
            experiment_id=EXPERIMENT_ID,
            phase="3/7",
            run_id=current_run,
            dataset="CICIDS2017",
            protocol="temporal_holdout_MonThu_vs_Fri",
            status="COMPLETED",
            started_at=started_at,
            completed_at=utc_now(),
            command="python scripts/run_cicids_temporal_strengthening.py",
            raw_result_path=relative(raw_path),
            summary_path=relative(summary_path),
            figure_path=relative(figure_path),
            error_path=relative(error_path),
            notes="Les cinq graines partagent un pool parent figé; aucune date n'est une feature.",
        )
        print(f"COMPLETED {current_run} {summary_path}")
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID,
            phase="3/7",
            run_id=current_run,
            dataset="CICIDS2017",
            protocol="temporal_holdout_MonThu_vs_Fri",
            status="FAILED",
            started_at=started_at,
            completed_at=utc_now(),
            command="python scripts/run_cicids_temporal_strengthening.py",
            error_path=relative(error_path),
            notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
