"""Entraine un modele supervise dedie aux journaux Linux/auth.

Les datasets `linux_auth_logs_*.csv` disposent d'un label metier
`anomaly_label`. Ce script entraine donc un RandomForest binaire:
`normal` contre `anomalie`, puis sauvegarde un artefact joblib compatible avec
le routeur Logminer.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


RAW_COLUMN_ALIASES = {
    "timestamp": ["timestamp", "timestamp_iso"],
    "source_ip": ["source_ip", "src_ip"],
    "server": ["server", "host", "city"],
    "username": ["username", "user"],
    "service": ["service", "source", "component"],
    "attempts": ["attempts"],
    "status": ["status"],
    "port": ["port", "src_port"],
    "protocol": ["protocol", "proto"],
    "comment": ["comment", "message"],
    "anomaly_label": ["anomaly_label", "event", "subcategory"],
}

FEATURE_COLUMNS = ["server", "service", "attempts", "status", "port", "protocol", "hour", "weekday"]
NUMERIC_FEATURES = ["attempts", "port", "hour", "weekday"]
CATEGORICAL_FEATURES = ["server", "service", "status", "protocol"]


def _first_existing(frame: pd.DataFrame, aliases: list[str]) -> pd.Series:
    lower_to_original = {str(column).lower(): column for column in frame.columns}
    for alias in aliases:
        column = lower_to_original.get(alias.lower())
        if column is not None:
            return frame[column].fillna("").astype(str)
    return pd.Series("", index=frame.index, dtype=str)


def prepare_linux_auth_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Ramene les variantes brutes/normalisees vers un schema ML stable."""

    prepared = pd.DataFrame(index=frame.index)
    for target, aliases in RAW_COLUMN_ALIASES.items():
        prepared[target] = _first_existing(frame, aliases)

    timestamps = pd.to_datetime(prepared["timestamp"], errors="coerce", utc=True)
    prepared["hour"] = timestamps.dt.hour.fillna(0).astype(int)
    prepared["weekday"] = timestamps.dt.weekday.fillna(0).astype(int)

    prepared["attempts"] = pd.to_numeric(prepared["attempts"].str.replace(",", ".", regex=False), errors="coerce").fillna(0)
    prepared["port"] = pd.to_numeric(prepared["port"].str.replace(",", ".", regex=False), errors="coerce").fillna(0)
    return prepared


def _balanced_sample(frame: pd.DataFrame, max_normal: int, max_anomaly: int, random_state: int) -> pd.DataFrame:
    normal = frame[frame["target"] == 0]
    anomaly = frame[frame["target"] == 1]
    if max_normal > 0 and len(normal) > max_normal:
        normal = normal.sample(max_normal, random_state=random_state)
    if max_anomaly > 0 and len(anomaly) > max_anomaly:
        anomaly = anomaly.sample(max_anomaly, random_state=random_state)
    return pd.concat([normal, anomaly], ignore_index=True).sample(frac=1, random_state=random_state)


def train_model(
    input_csv: list[Path],
    model_out: Path,
    metrics_out: Path,
    *,
    max_normal: int,
    max_anomaly: int,
    test_size: float,
    random_state: int,
) -> dict[str, object]:
    prepared_frames = []
    for path in input_csv:
        raw = pd.read_csv(path, dtype=str, keep_default_na=False)
        prepared = prepare_linux_auth_frame(raw)
        labels = prepared["anomaly_label"].str.lower().str.strip()
        prepared = prepared[labels.ne("")].copy()
        prepared["target"] = (prepared["anomaly_label"].str.lower().str.strip().ne("normal")).astype(int)
        prepared["source_dataset"] = path.stem
        prepared_frames.append(prepared)
    prepared = pd.concat(prepared_frames, ignore_index=True)
    if prepared["target"].nunique() < 2:
        raise ValueError("Le dataset doit contenir au moins des lignes normal et anomalie.")

    trainable = _balanced_sample(prepared, max_normal=max_normal, max_anomaly=max_anomaly, random_state=random_state)
    x = trainable[FEATURE_COLUMNS]
    y = trainable["target"].astype(int)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, stratify=y, random_state=random_state)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), NUMERIC_FEATURES),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
                    ]
                ),
                CATEGORICAL_FEATURES,
            ),
        ]
    )
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=120,
                    max_depth=24,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=random_state,
                    n_jobs=1,
                ),
            ),
        ]
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metrics = {
        "dataset": " + ".join(str(path) for path in input_csv),
        "model": "random_forest_linux_auth",
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "normal_rows_used": int((trainable["target"] == 0).sum()),
        "anomaly_rows_used": int((trainable["target"] == 1).sum()),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
    }
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    metrics.update({"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)})

    model_out.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model_type": "random_forest_linux_auth",
        "model": model,
        "feature_columns": FEATURE_COLUMNS,
        "metadata": {
            "input_csv": [str(path) for path in input_csv],
            "target": "anomaly_label != normal",
            "max_normal": max_normal,
            "max_anomaly": max_anomaly,
            "test_size": test_size,
            "random_state": random_state,
            "trained_at": datetime.now(timezone.utc).isoformat(),
            **metrics,
        },
    }
    joblib.dump(artifact, model_out)

    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(metrics_out, index=False, encoding="utf-8-sig")
    report_path = metrics_out.with_suffix(".txt")
    report_path.write_text(classification_report(y_test, predictions, target_names=["normal", "anomaly"]), encoding="utf-8")
    return metrics


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Entraine un RandomForest dedie Linux/auth")
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        action="append",
        type=Path,
        help="CSV linux_auth_logs_*.csv ou CSV normalise; option repetable",
    )
    parser.add_argument("--model-out", default=Path("models/random_forest_linux_auth.joblib"), type=Path)
    parser.add_argument("--metrics-out", default=Path("data/processed/random_forest_linux_auth_metrics.csv"), type=Path)
    parser.add_argument("--max-normal", default=100000, type=int, help="0 = toutes les lignes normales")
    parser.add_argument("--max-anomaly", default=100000, type=int, help="0 = toutes les lignes anomalies")
    parser.add_argument("--test-size", default=0.2, type=float)
    parser.add_argument("--random-state", default=42, type=int)
    args = parser.parse_args(argv)

    metrics = train_model(
        args.input,
        args.model_out,
        args.metrics_out,
        max_normal=args.max_normal,
        max_anomaly=args.max_anomaly,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    print(f"Modele sauvegarde: {args.model_out}")
    print(f"Metriques: {args.metrics_out}")
    print(
        "accuracy={accuracy:.6f} precision={precision:.6f} recall={recall:.6f} f1={f1:.6f}".format(
            **metrics
        )
    )
    print(f"tp={metrics['tp']} fp={metrics['fp']} fn={metrics['fn']} tn={metrics['tn']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
