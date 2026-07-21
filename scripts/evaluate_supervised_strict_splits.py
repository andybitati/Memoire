"""Evaluate stricter supervised splits for Logminer datasets.

The goal is not to replace the exploratory training artifacts. This script
produces complementary evidence with less leakage-prone splits:

- Linux/auth: hold out whole servers.
- CICIDS2017: hold out whole capture/scenario CSV files.
- CIC-DDoS2019-compatible files: hold out whole attack-family CSV files.

Outputs are intended for the thesis tables, not for production deployment.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from train_linux_auth_model import (
    CATEGORICAL_FEATURES as LINUX_CATEGORICAL,
    FEATURE_COLUMNS as LINUX_FEATURES,
    NUMERIC_FEATURES as LINUX_NUMERIC,
    prepare_linux_auth_frame,
)


DROP_COLUMNS = {
    "unnamed: 0",
    "label",
    "flow id",
    "source ip",
    "destination ip",
    "timestamp",
    "simillarhttp",
}


@dataclass(frozen=True)
class EvalConfig:
    dataset: str
    seed: int
    split: str
    train_rows: int
    test_rows: int
    train_positive_rate: float
    test_positive_rate: float
    precision: float
    recall: float
    f1: float
    accuracy: float
    pr_auc: float
    mcc: float
    tn: int
    fp: int
    fn: int
    tp: int
    notes: str


def _clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).strip().lstrip("\ufeff") for column in frame.columns]
    return frame


def _label_column(columns: Iterable[str]) -> str:
    for column in columns:
        if str(column).strip().lower() == "label":
            return str(column)
    raise ValueError("Label column not found")


def _network_feature_columns(path: Path) -> list[str]:
    header = _clean_columns(pd.read_csv(path, nrows=0, encoding_errors="ignore"))
    return [column for column in header.columns if column.lower() not in DROP_COLUMNS]


def _network_features(frame: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    frame = _clean_columns(frame)
    features = frame.drop(columns=[column for column in frame.columns if column.lower() in DROP_COLUMNS], errors="ignore")
    features = features.reindex(columns=feature_columns, fill_value=0)
    features = features.replace(["Infinity", "INF", "inf", "-inf", "-Infinity", "NaN", "nan"], np.nan)
    for column in features.columns:
        features[column] = features[column].astype(str).str.replace(",", ".", regex=False)
    features = features.apply(pd.to_numeric, errors="coerce")
    return features.replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=-1e12, upper=1e12).astype("float64")


def _rf_numeric(seed: int, *, n_estimators: int = 100, max_depth: int = 28) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=seed,
        n_jobs=1,
    )


def _linux_model(seed: int, *, n_estimators: int = 120) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), LINUX_NUMERIC),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
                    ]
                ),
                LINUX_CATEGORICAL,
            ),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=n_estimators,
                    max_depth=24,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=seed,
                    n_jobs=1,
                ),
            ),
        ]
    )


def _sample_by_class(frame: pd.DataFrame, *, target: str, max_negative: int, max_positive: int, seed: int) -> pd.DataFrame:
    negative = frame[frame[target] == 0]
    positive = frame[frame[target] == 1]
    if max_negative > 0 and len(negative) > max_negative:
        negative = negative.sample(max_negative, random_state=seed)
    if max_positive > 0 and len(positive) > max_positive:
        positive = positive.sample(max_positive, random_state=seed)
    return pd.concat([negative, positive], ignore_index=True).sample(frac=1, random_state=seed)


def _metric_row(
    *,
    dataset: str,
    seed: int,
    split: str,
    y_train: pd.Series,
    y_test: pd.Series,
    y_pred: np.ndarray,
    y_score: np.ndarray,
    notes: str,
) -> EvalConfig:
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    return EvalConfig(
        dataset=dataset,
        seed=seed,
        split=split,
        train_rows=int(len(y_train)),
        test_rows=int(len(y_test)),
        train_positive_rate=float(y_train.mean()) if len(y_train) else 0.0,
        test_positive_rate=float(y_test.mean()) if len(y_test) else 0.0,
        precision=float(precision_score(y_test, y_pred, zero_division=0)),
        recall=float(recall_score(y_test, y_pred, zero_division=0)),
        f1=float(f1_score(y_test, y_pred, zero_division=0)),
        accuracy=float(accuracy_score(y_test, y_pred)),
        pr_auc=float(average_precision_score(y_test, y_score)) if y_test.nunique() > 1 else np.nan,
        mcc=float(matthews_corrcoef(y_test, y_pred)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        notes=notes,
    )


def evaluate_linux_auth(path: Path, seeds: list[int], *, max_train_per_class: int, max_test_per_class: int, n_estimators: int) -> list[EvalConfig]:
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    prepared = prepare_linux_auth_frame(raw)
    labels = prepared["anomaly_label"].str.lower().str.strip()
    prepared = prepared[labels.ne("")].copy()
    prepared["target"] = labels[labels.ne("")].ne("normal").astype(int)
    rows: list[EvalConfig] = []
    for seed in seeds:
        splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=seed)
        train_idx, test_idx = next(splitter.split(prepared, prepared["target"], groups=prepared["server"]))
        train = _sample_by_class(prepared.iloc[train_idx], target="target", max_negative=max_train_per_class, max_positive=max_train_per_class, seed=seed)
        test = _sample_by_class(prepared.iloc[test_idx], target="target", max_negative=max_test_per_class, max_positive=max_test_per_class, seed=seed)
        model = _linux_model(seed, n_estimators=n_estimators)
        model.fit(train[LINUX_FEATURES], train["target"])
        y_pred = model.predict(test[LINUX_FEATURES])
        y_score = model.predict_proba(test[LINUX_FEATURES])[:, 1]
        heldout = ",".join(sorted(test["server"].astype(str).unique()))
        rows.append(
            _metric_row(
                dataset="Linux/auth",
                seed=seed,
                split="server_holdout",
                y_train=train["target"],
                y_test=test["target"],
                y_pred=y_pred,
                y_score=y_score,
                notes=f"heldout_servers={heldout}",
            )
        )
    return rows


def collect_network_sample(
    files: list[Path],
    feature_columns: list[str],
    *,
    max_negative: int,
    max_positive: int,
    chunksize: int,
    max_chunks_per_file: int,
    seed: int,
) -> tuple[pd.DataFrame, pd.Series, dict[str, int]]:
    negative_parts: list[pd.DataFrame] = []
    positive_parts: list[pd.DataFrame] = []
    label_counts: dict[str, int] = {}
    negative_count = 0
    positive_count = 0
    for path in files:
        for chunk_index, chunk in enumerate(pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunksize, encoding_errors="ignore")):
            if max_chunks_per_file > 0 and chunk_index >= max_chunks_per_file:
                break
            chunk = _clean_columns(chunk)
            label_col = _label_column(chunk.columns)
            labels = chunk[label_col].astype(str).str.strip()
            for label, count in labels.value_counts().items():
                label_counts[label] = label_counts.get(label, 0) + int(count)
            target = labels.str.upper().ne("BENIGN").astype(int)
            chunk = chunk.assign(target=target)
            negative = chunk[chunk["target"] == 0]
            positive = chunk[chunk["target"] == 1]
            if max_negative == 0 or negative_count < max_negative:
                take = negative.head(len(negative) if max_negative == 0 else max_negative - negative_count)
                if not take.empty:
                    negative_parts.append(take)
                    negative_count += len(take)
            if max_positive == 0 or positive_count < max_positive:
                take = positive.head(len(positive) if max_positive == 0 else max_positive - positive_count)
                if not take.empty:
                    positive_parts.append(take)
                    positive_count += len(take)
            positive_ok = max_positive == 0 or positive_count >= max_positive
            negative_ok = max_negative == 0 or negative_count >= max_negative
            if positive_ok and negative_ok:
                break
    if not negative_parts and not positive_parts:
        raise ValueError("No rows collected for network sample")
    sample = pd.concat(negative_parts + positive_parts, ignore_index=True).sample(frac=1, random_state=seed)
    y = sample["target"].astype(int)
    x = _network_features(sample, feature_columns)
    return x, y, label_counts


def _evaluate_network_holdout(
    *,
    dataset: str,
    files: list[Path],
    seeds: list[int],
    max_train_per_class: int,
    max_test_per_class: int,
    chunksize: int,
    max_chunks_per_file: int,
    n_estimators: int,
    max_depth: int,
) -> list[EvalConfig]:
    feature_columns = _network_feature_columns(files[0])
    attack_files = [path for path in files if "monday" not in path.name.lower()]
    rows: list[EvalConfig] = []
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
        model = _rf_numeric(seed, n_estimators=n_estimators, max_depth=max_depth)
        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)
        y_score = model.predict_proba(x_test)[:, 1]
        rows.append(
            _metric_row(
                dataset=dataset,
                seed=seed,
                split="file_or_scenario_holdout",
                y_train=y_train,
                y_test=y_test,
                y_pred=y_pred,
                y_score=y_score,
                notes=f"heldout_file={heldout.name}; test_labels={label_counts}",
            )
        )
    return rows


def evaluate_cicids(input_dir: Path, seeds: list[int], *, max_train_per_class: int, max_test_per_class: int, chunksize: int, max_chunks_per_file: int, n_estimators: int) -> list[EvalConfig]:
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        return []
    return _evaluate_network_holdout(
        dataset="CICIDS2017",
        files=files,
        seeds=seeds,
        max_train_per_class=max_train_per_class,
        max_test_per_class=max_test_per_class,
        chunksize=chunksize,
        max_chunks_per_file=max_chunks_per_file,
        n_estimators=n_estimators,
        max_depth=28,
    )


def evaluate_cicddos(input_dir: Path, seeds: list[int], *, max_train_per_class: int, max_test_per_class: int, chunksize: int, max_chunks_per_file: int, n_estimators: int) -> list[EvalConfig]:
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        return []
    return _evaluate_network_holdout(
        dataset="CIC-DDoS2019",
        files=files,
        seeds=seeds,
        max_train_per_class=max_train_per_class,
        max_test_per_class=max_test_per_class,
        chunksize=chunksize,
        max_chunks_per_file=max_chunks_per_file,
        n_estimators=n_estimators,
        max_depth=28,
    )


def write_table(frame: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    summary = (
        frame.groupby(["dataset", "split"], as_index=False)
        .agg(
            seeds=("seed", "nunique"),
            test_rows=("test_rows", "mean"),
            precision=("precision", "mean"),
            recall=("recall", "mean"),
            f1=("f1", "mean"),
            pr_auc=("pr_auc", "mean"),
            mcc=("mcc", "mean"),
            fp=("fp", "mean"),
            fn=("fn", "mean"),
        )
        .sort_values(["dataset", "split"])
    )
    rows = [
        "# Splits Supervises Stricts",
        "",
        "| Dataset | Split | Seeds | Test moy. | Precision | Rappel | F1 | PR-AUC | MCC | FP moy. | FN moy. |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in summary.iterrows():
        rows.append(
            "| {dataset} | {split} | {seeds:.0f} | {test_rows:.0f} | {precision:.6f} | {recall:.6f} | {f1:.6f} | {pr_auc:.6f} | {mcc:.6f} | {fp:.1f} | {fn:.1f} |".format(
                **row
            )
        )
    rows.extend(
        [
            "",
            "Note: ces resultats completent les scores supervises. Les splits par serveur, fichier ou scenario reduisent le risque d'observations quasi identiques entre entrainement et test, mais ne constituent pas encore une validation industrielle multi-environnement.",
        ]
    )
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate stricter supervised splits")
    parser.add_argument("--seeds", default="42,43,44")
    parser.add_argument("--linux-auth", type=Path, default=Path("data/raw/Datasets/linux_auth_logs_labeled.csv"))
    parser.add_argument("--cicids-dir", type=Path, default=Path("data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"))
    parser.add_argument("--cicddos-dir", type=Path, default=Path("data/raw/Datasets/UNSWNB15"))
    parser.add_argument("--max-train-per-class", type=int, default=30000)
    parser.add_argument("--max-test-per-class", type=int, default=15000)
    parser.add_argument("--chunksize", type=int, default=100000)
    parser.add_argument("--max-chunks-per-file", type=int, default=3)
    parser.add_argument("--n-estimators", type=int, default=40)
    parser.add_argument("--only", choices=["all", "linux", "cicids", "cicddos"], default="all")
    parser.add_argument("--output", type=Path, default=Path("data/processed/supervised_strict_split_metrics.csv"))
    parser.add_argument("--table-out", type=Path, default=Path("docs/memoire/tables/table_supervised_strict_splits.md"))
    args = parser.parse_args(argv)

    seeds = [int(seed.strip()) for seed in args.seeds.split(",") if seed.strip()]
    rows: list[EvalConfig] = []
    if args.only in {"all", "linux"}:
        rows.extend(evaluate_linux_auth(args.linux_auth, seeds, max_train_per_class=args.max_train_per_class, max_test_per_class=args.max_test_per_class, n_estimators=args.n_estimators))
    if args.only in {"all", "cicids"}:
        rows.extend(evaluate_cicids(args.cicids_dir, seeds, max_train_per_class=args.max_train_per_class, max_test_per_class=args.max_test_per_class, chunksize=args.chunksize, max_chunks_per_file=args.max_chunks_per_file, n_estimators=args.n_estimators))
    if args.only in {"all", "cicddos"}:
        rows.extend(evaluate_cicddos(args.cicddos_dir, seeds, max_train_per_class=args.max_train_per_class, max_test_per_class=args.max_test_per_class, chunksize=args.chunksize, max_chunks_per_file=args.max_chunks_per_file, n_estimators=args.n_estimators))

    frame = pd.DataFrame([row.__dict__ for row in rows])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.output, index=False, encoding="utf-8-sig")
    write_table(frame, args.table_out)
    print(f"Metrics: {args.output}")
    print(f"Table: {args.table_out}")
    print(frame[["dataset", "seed", "split", "f1", "precision", "recall", "mcc", "notes"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

