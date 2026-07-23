"""Compare supervised model candidates on CICIDS2017 strict holdouts.

The goal is to test whether another lightweight supervised model generalizes
better than the current RandomForest when complete CICIDS2017 files/scenarios
are held out. The script keeps the same sampling and feature extraction helpers
used by the controlled split experiment, then varies only the classifier.
"""

from __future__ import annotations

import argparse
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from evaluate_supervised_strict_splits import _network_feature_columns, collect_network_sample


@dataclass(frozen=True)
class CandidateResult:
    dataset: str
    model: str
    seed: int
    split: str
    heldout_file: str
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
    duration_sec: float
    notes: str


def _candidate_models(seed: int) -> dict[str, object]:
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=100,
            max_depth=28,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=seed,
            n_jobs=1,
        ),
        "ExtraTrees": ExtraTreesClassifier(
            n_estimators=140,
            max_depth=32,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=seed,
            n_jobs=1,
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            max_iter=120,
            learning_rate=0.08,
            max_leaf_nodes=31,
            l2_regularization=0.05,
            random_state=seed,
        ),
        "LogisticRegression": Pipeline(
            steps=[
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
        "SGDLogistic": Pipeline(
            steps=[
                ("scale", StandardScaler()),
                (
                    "model",
                    SGDClassifier(
                        loss="log_loss",
                        alpha=0.0001,
                        max_iter=1500,
                        tol=1e-3,
                        class_weight="balanced",
                        random_state=seed,
                    ),
                ),
            ]
        ),
    }


def _score(model: object, x_test: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(x_test)
        return np.asarray(proba)[:, 1]
    if hasattr(model, "decision_function"):
        values = np.asarray(model.decision_function(x_test), dtype=float)
        if values.ndim > 1:
            values = values[:, 0]
        return values
    return np.asarray(model.predict(x_test), dtype=float)


def _metrics(
    *,
    model_name: str,
    seed: int,
    heldout_file: str,
    x_train: pd.DataFrame,
    y_train: pd.Series,
    x_test: pd.DataFrame,
    y_test: pd.Series,
    y_pred: np.ndarray,
    y_score: np.ndarray,
    duration_sec: float,
    notes: str,
) -> CandidateResult:
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    return CandidateResult(
        dataset="CICIDS2017",
        model=model_name,
        seed=seed,
        split="file_or_scenario_holdout",
        heldout_file=heldout_file,
        feature_count=int(x_train.shape[1]),
        train_rows=int(len(y_train)),
        test_rows=int(len(y_test)),
        train_positive_rate=float(y_train.mean()) if len(y_train) else 0.0,
        test_positive_rate=float(y_test.mean()) if len(y_test) else 0.0,
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
        duration_sec=float(duration_sec),
        notes=notes,
    )


def evaluate(
    *,
    input_dir: Path,
    seeds: list[int],
    max_train_per_class: int,
    max_test_per_class: int,
    chunksize: int,
    max_chunks_per_file: int,
) -> list[CandidateResult]:
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {input_dir}")
    feature_columns = _network_feature_columns(files[0])
    attack_files = [path for path in files if "monday" not in path.name.lower()]
    rows: list[CandidateResult] = []
    for seed in seeds:
        heldout = attack_files[seed % len(attack_files)]
        train_files = [path for path in files if path != heldout]
        x_train, y_train, _ = collect_network_sample(
            train_files,
            feature_columns,
            max_negative=max_train_per_class,
            max_positive=max_train_per_class,
            chunksize=chunksize,
            max_chunks_per_file=max_chunks_per_file,
            seed=seed,
        )
        x_test, y_test, label_counts = collect_network_sample(
            [heldout],
            feature_columns,
            max_negative=max_test_per_class,
            max_positive=max_test_per_class,
            chunksize=chunksize,
            max_chunks_per_file=max_chunks_per_file,
            seed=seed,
        )
        for model_name, model in _candidate_models(seed).items():
            started = time.perf_counter()
            model.fit(x_train, y_train)
            y_pred = np.asarray(model.predict(x_test), dtype=int)
            y_score = _score(model, x_test)
            rows.append(
                _metrics(
                    model_name=model_name,
                    seed=seed,
                    heldout_file=heldout.name,
                    x_train=x_train,
                    y_train=y_train,
                    x_test=x_test,
                    y_test=y_test,
                    y_pred=y_pred,
                    y_score=y_score,
                    duration_sec=time.perf_counter() - started,
                    notes=f"test_labels={label_counts}",
                )
            )
    return rows


def write_summary(frame: pd.DataFrame, output: Path) -> pd.DataFrame:
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = (
        frame.groupby(["dataset", "model", "split"], as_index=False)
        .agg(
            seeds=("seed", "nunique"),
            test_rows=("test_rows", "mean"),
            precision_mean=("precision", "mean"),
            recall_mean=("recall", "mean"),
            f1_mean=("f1", "mean"),
            f1_std=("f1", "std"),
            pr_auc_mean=("pr_auc", "mean"),
            mcc_mean=("mcc", "mean"),
            fp_mean=("fp", "mean"),
            fn_mean=("fn", "mean"),
            duration_sec_mean=("duration_sec", "mean"),
        )
        .sort_values(["f1_mean", "pr_auc_mean", "mcc_mean"], ascending=[False, False, False])
    )
    summary.to_csv(output, index=False, encoding="utf-8-sig")
    return summary


def write_table(summary: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        "# Comparaison De Modeles CICIDS2017 En Holdout Strict",
        "",
        "| Modele | Seeds | Test moy. | Precision | Rappel | F1 mu+-sigma | PR-AUC | MCC | FP moy. | FN moy. | Duree moy. |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in summary.iterrows():
        rows.append(
            "| {model} | {seeds:.0f} | {test_rows:.0f} | {precision_mean:.6f} | {recall_mean:.6f} | {f1_mean:.6f} +- {f1_std:.6f} | {pr_auc_mean:.6f} | {mcc_mean:.6f} | {fp_mean:.1f} | {fn_mean:.1f} | {duration_sec_mean:.4f} s |".format(
                **row
            )
        )
    rows.extend(
        [
            "",
            "Note: les modeles utilisent les memes fichiers tenus hors entrainement, les memes features et les memes plafonds d'echantillonnage. Le test compare des candidats legers disponibles dans scikit-learn; il ne couvre pas XGBoost/LightGBM faute de dependances figees dans l'environnement de base.",
        ]
    )
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare supervised CICIDS2017 candidates on strict holdouts")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"))
    parser.add_argument("--seeds", default="42,43,44,45,46")
    parser.add_argument("--max-train-per-class", type=int, default=8000)
    parser.add_argument("--max-test-per-class", type=int, default=4000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--max-chunks-per-file", type=int, default=2)
    parser.add_argument("--output", type=Path, default=Path("data/processed/cicids_model_candidates_metrics.csv"))
    parser.add_argument("--summary-out", type=Path, default=Path("data/processed/cicids_model_candidates_summary.csv"))
    parser.add_argument("--table-out", type=Path, default=Path("docs/memoire/tables/table_cicids_model_candidates.md"))
    args = parser.parse_args(argv)

    seeds = [int(seed.strip()) for seed in args.seeds.split(",") if seed.strip()]
    rows = evaluate(
        input_dir=args.input_dir,
        seeds=seeds,
        max_train_per_class=args.max_train_per_class,
        max_test_per_class=args.max_test_per_class,
        chunksize=args.chunksize,
        max_chunks_per_file=args.max_chunks_per_file,
    )
    frame = pd.DataFrame([asdict(row) for row in rows])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False, encoding="utf-8-sig")
    summary = write_summary(frame, args.summary_out)
    write_table(summary, args.table_out)
    print(f"Metrics: {args.output}")
    print(f"Summary: {args.summary_out}")
    print(f"Table: {args.table_out}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
