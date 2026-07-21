"""Compare random and scenario/file holdout splits under matched settings.

This script is intentionally narrow: it controls model family, features,
hyperparameters, seeds and per-class sampling caps, then changes only the split
mechanism as much as the public CSV layout permits.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split

from evaluate_supervised_strict_splits import (
    _network_feature_columns,
    _rf_numeric,
    collect_network_sample,
)


@dataclass(frozen=True)
class ControlledResult:
    dataset: str
    split: str
    seed: int
    model: str
    n_estimators: int
    max_depth: int
    min_samples_leaf: int
    class_weight: str
    feature_count: int
    train_rows: int
    test_rows: int
    train_positive_rate: float
    test_positive_rate: float
    tn: int
    fp: int
    fn: int
    tp: int
    precision: float
    recall: float
    f1: float
    accuracy: float
    pr_auc: float
    mcc: float
    notes: str


def _metrics(
    *,
    dataset: str,
    split: str,
    seed: int,
    n_estimators: int,
    max_depth: int,
    feature_count: int,
    y_train: pd.Series,
    y_test: pd.Series,
    y_pred: np.ndarray,
    y_score: np.ndarray,
    notes: str,
) -> ControlledResult:
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    return ControlledResult(
        dataset=dataset,
        split=split,
        seed=seed,
        model="RandomForest",
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=2,
        class_weight="balanced",
        feature_count=feature_count,
        train_rows=int(len(y_train)),
        test_rows=int(len(y_test)),
        train_positive_rate=float(y_train.mean()),
        test_positive_rate=float(y_test.mean()),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        precision=float(precision_score(y_test, y_pred, zero_division=0)),
        recall=float(recall_score(y_test, y_pred, zero_division=0)),
        f1=float(f1_score(y_test, y_pred, zero_division=0)),
        accuracy=float(accuracy_score(y_test, y_pred)),
        pr_auc=float(average_precision_score(y_test, y_score)) if y_test.nunique() > 1 else np.nan,
        mcc=float(matthews_corrcoef(y_test, y_pred)),
        notes=notes,
    )


def _fit_score(
    *,
    dataset: str,
    split: str,
    seed: int,
    n_estimators: int,
    max_depth: int,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    notes: str,
) -> ControlledResult:
    model = _rf_numeric(seed, n_estimators=n_estimators, max_depth=max_depth)
    model.fit(x_train, y_train)
    y_pred = model.predict(x_test)
    y_score = model.predict_proba(x_test)[:, 1]
    return _metrics(
        dataset=dataset,
        split=split,
        seed=seed,
        n_estimators=n_estimators,
        max_depth=max_depth,
        feature_count=x_train.shape[1],
        y_train=y_train,
        y_test=y_test,
        y_pred=y_pred,
        y_score=y_score,
        notes=notes,
    )


def evaluate_dataset(
    *,
    dataset: str,
    input_dir: Path,
    seeds: list[int],
    max_train_per_class: int,
    max_test_per_class: int,
    chunksize: int,
    max_chunks_per_file: int,
    n_estimators: int,
    max_depth: int,
) -> list[ControlledResult]:
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    feature_columns = _network_feature_columns(files[0])
    attack_files = [path for path in files if "monday" not in path.name.lower()]
    rows: list[ControlledResult] = []
    for seed in seeds:
        heldout = attack_files[seed % len(attack_files)]
        train_files = [path for path in files if path != heldout]
        x_train_h, y_train_h, _ = collect_network_sample(
            train_files,
            feature_columns,
            max_negative=max_train_per_class,
            max_positive=max_train_per_class,
            chunksize=chunksize,
            max_chunks_per_file=max_chunks_per_file,
            seed=seed,
        )
        x_test_h, y_test_h, label_counts = collect_network_sample(
            [heldout],
            feature_columns,
            max_negative=max_test_per_class,
            max_positive=max_test_per_class,
            chunksize=chunksize,
            max_chunks_per_file=max_chunks_per_file,
            seed=seed,
        )
        rows.append(
            _fit_score(
                dataset=dataset,
                split="file_or_scenario_holdout",
                seed=seed,
                n_estimators=n_estimators,
                max_depth=max_depth,
                x_train=x_train_h,
                y_train=y_train_h,
                x_test=x_test_h,
                y_test=y_test_h,
                notes=f"heldout_file={heldout.name}; test_labels={label_counts}",
            )
        )

        x_all, y_all, _ = collect_network_sample(
            files,
            feature_columns,
            max_negative=max_train_per_class + max_test_per_class,
            max_positive=max_train_per_class + max_test_per_class,
            chunksize=chunksize,
            max_chunks_per_file=max_chunks_per_file,
            seed=seed,
        )
        x_train_r, x_test_r, y_train_r, y_test_r = train_test_split(
            x_all,
            y_all,
            train_size=len(y_train_h),
            test_size=len(y_test_h),
            random_state=seed,
            stratify=y_all,
        )
        rows.append(
            _fit_score(
                dataset=dataset,
                split="random_stratified_matched",
                seed=seed,
                n_estimators=n_estimators,
                max_depth=max_depth,
                x_train=x_train_r,
                y_train=y_train_r,
                x_test=x_test_r,
                y_test=y_test_r,
                notes=(
                    f"matched_to_holdout_train={len(y_train_h)}; "
                    f"matched_to_holdout_test={len(y_test_h)}; source_files=all"
                ),
            )
        )
    return rows


def write_summary(frame: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = (
        frame.groupby(["dataset", "split"], as_index=False)
        .agg(
            seeds=("seed", "nunique"),
            test_rows=("test_rows", "mean"),
            f1_mean=("f1", "mean"),
            f1_std=("f1", "std"),
            pr_auc_mean=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
            mcc_mean=("mcc", "mean"),
            mcc_std=("mcc", "std"),
            recall_mean=("recall", "mean"),
            recall_std=("recall", "std"),
        )
        .sort_values(["dataset", "split"])
    )
    summary.to_csv(output, index=False, encoding="utf-8-sig")


def write_table(summary_csv: Path, output: Path) -> None:
    summary = pd.read_csv(summary_csv)
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        "# Comparaison Controlee Des Splits",
        "",
        "| Dataset | Split | Seeds | Test moy. | F1 mu+-sigma | PR-AUC mu+-sigma | MCC mu+-sigma | Rappel mu+-sigma |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in summary.iterrows():
        rows.append(
            "| {dataset} | {split} | {seeds:.0f} | {test_rows:.0f} | {f1_mean:.6f} +- {f1_std:.6f} | {pr_auc_mean:.6f} +- {pr_auc_std:.6f} | {mcc_mean:.6f} +- {mcc_std:.6f} | {recall_mean:.6f} +- {recall_std:.6f} |".format(
                **row
            )
        )
    rows.extend(
        [
            "",
            "Note: les variantes utilisent les memes features, hyperparametres, seeds et plafonds d'echantillonnage. Le split aleatoire est apparie aux tailles train/test du holdout pour chaque seed.",
        ]
    )
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Controlled random-vs-holdout split comparison")
    parser.add_argument("--dataset", choices=["cicids", "cicddos"], default="cicids")
    parser.add_argument("--input-dir", type=Path, default=None)
    parser.add_argument("--seeds", default="42,43,44,45,46")
    parser.add_argument("--max-train-per-class", type=int, default=8000)
    parser.add_argument("--max-test-per-class", type=int, default=4000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--max-chunks-per-file", type=int, default=2)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=28)
    parser.add_argument("--output", type=Path, default=Path("data/processed/controlled_split_comparison_metrics.csv"))
    parser.add_argument("--summary-out", type=Path, default=Path("data/processed/controlled_split_comparison_summary.csv"))
    parser.add_argument("--table-out", type=Path, default=Path("docs/memoire/tables/table_controlled_split_comparison.md"))
    args = parser.parse_args(argv)

    default_dir = {
        "cicids": Path("data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"),
        "cicddos": Path("data/raw/Datasets/UNSWNB15"),
    }[args.dataset]
    dataset_name = {"cicids": "CICIDS2017", "cicddos": "CIC-DDoS2019"}[args.dataset]
    seeds = [int(seed.strip()) for seed in args.seeds.split(",") if seed.strip()]
    rows = evaluate_dataset(
        dataset=dataset_name,
        input_dir=args.input_dir or default_dir,
        seeds=seeds,
        max_train_per_class=args.max_train_per_class,
        max_test_per_class=args.max_test_per_class,
        chunksize=args.chunksize,
        max_chunks_per_file=args.max_chunks_per_file,
        n_estimators=args.n_estimators,
        max_depth=args.max_depth,
    )
    frame = pd.DataFrame([asdict(row) for row in rows])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False, encoding="utf-8-sig")
    write_summary(frame, args.summary_out)
    write_table(args.summary_out, args.table_out)
    print(f"Metrics: {args.output}")
    print(f"Summary: {args.summary_out}")
    print(f"Table: {args.table_out}")
    print(frame[["dataset", "split", "seed", "f1", "pr_auc", "mcc", "recall"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
