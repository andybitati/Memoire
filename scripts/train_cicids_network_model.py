"""Entraine un modele reseau supervise pour CICIDS/MachineLearningCVE.

Les CSV `MachineLearningCVE/*.csv` viennent de CICFlowMeter et contiennent une
colonne `Label`. Ce script entraine un RandomForest binaire BENIGN/attaque en
echantillonnant les gros fichiers par chunks, puis sauvegarde un artefact
compatible avec le routeur Logminer.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


DROP_COLUMNS = {"label", "flow id", "source ip", "destination ip", "timestamp"}


def _clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()
    frame.columns = [str(column).strip().lstrip("\ufeff") for column in frame.columns]
    return frame


def _to_features(frame: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    frame = _clean_columns(frame)
    features = frame.drop(columns=[column for column in frame.columns if column.lower() in DROP_COLUMNS], errors="ignore")
    features = features.reindex(columns=feature_columns, fill_value=0)
    features = features.replace(["Infinity", "INF", "inf", "-inf", "-Infinity", "NaN", "nan"], np.nan)
    for column in features.columns:
        features[column] = features[column].astype(str).str.replace(",", ".", regex=False)
    features = features.apply(pd.to_numeric, errors="coerce")
    return features.replace([np.inf, -np.inf], np.nan).fillna(0).clip(lower=-1e12, upper=1e12).astype("float64")


def _label_column(columns: list[str]) -> str:
    for column in columns:
        if str(column).strip().lower() == "label":
            return column
    raise ValueError("Colonne Label introuvable")


def _feature_columns(path: Path) -> list[str]:
    header = pd.read_csv(path, nrows=0, encoding_errors="ignore")
    columns = [str(column).strip().lstrip("\ufeff") for column in header.columns]
    return [column for column in columns if column.lower() not in DROP_COLUMNS]


def collect_sample(
    input_dir: Path,
    *,
    max_benign: int,
    max_attack: int,
    max_per_attack_label: int,
    chunksize: int,
    random_state: int,
) -> tuple[pd.DataFrame, pd.Series, list[str], dict[str, int]]:
    files = sorted(input_dir.glob("*.csv"))
    if not files:
        raise ValueError(f"Aucun CSV trouve dans {input_dir}")

    feature_columns = _feature_columns(files[0])
    benign_parts: list[pd.DataFrame] = []
    attack_parts: list[pd.DataFrame] = []
    label_counts: dict[str, int] = {}
    attack_kept_by_label: dict[str, int] = {}
    benign_count = 0
    attack_count = 0

    for file_index, path in enumerate(files):
        for chunk_index, chunk in enumerate(pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunksize, encoding_errors="ignore")):
            chunk = _clean_columns(chunk)
            label_col = _label_column(list(chunk.columns))
            labels = chunk[label_col].astype(str).str.strip()
            for label, count in labels.value_counts().items():
                label_counts[label] = label_counts.get(label, 0) + int(count)

            chunk = chunk.assign(target=(labels.str.upper() != "BENIGN").astype(int))
            benign = chunk[chunk["target"] == 0]
            attack = chunk[chunk["target"] == 1]

            if max_benign == 0 or benign_count < max_benign:
                remaining = len(benign) if max_benign == 0 else max_benign - benign_count
                take = benign.head(max(0, remaining))
                if not take.empty:
                    benign_parts.append(take)
                    benign_count += len(take)

            if max_attack == 0 or attack_count < max_attack:
                for label, group in attack.groupby(label_col):
                    clean_label = str(label).strip()
                    kept_for_label = attack_kept_by_label.get(clean_label, 0)
                    if max_per_attack_label > 0 and kept_for_label >= max_per_attack_label:
                        continue
                    remaining_total = len(group) if max_attack == 0 else max_attack - attack_count
                    remaining_label = len(group) if max_per_attack_label == 0 else max_per_attack_label - kept_for_label
                    take = group.head(max(0, min(remaining_total, remaining_label)))
                    if not take.empty:
                        attack_parts.append(take)
                        attack_count += len(take)
                        attack_kept_by_label[clean_label] = kept_for_label + len(take)
                    if max_attack > 0 and attack_count >= max_attack:
                        break

    sample = pd.concat(benign_parts + attack_parts, ignore_index=True).sample(frac=1, random_state=random_state)
    y = sample["target"].astype(int)
    x = _to_features(sample, feature_columns)
    return x, y, feature_columns, label_counts


def train_model(
    input_dir: Path,
    model_out: Path,
    metrics_out: Path,
    *,
    max_benign: int,
    max_attack: int,
    max_per_attack_label: int,
    chunksize: int,
    test_size: float,
    random_state: int,
) -> dict[str, object]:
    x, y, feature_columns, label_counts = collect_sample(
        input_dir,
        max_benign=max_benign,
        max_attack=max_attack,
        max_per_attack_label=max_per_attack_label,
        chunksize=chunksize,
        random_state=random_state,
    )
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, stratify=y, random_state=random_state)
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=28,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=1,
    )
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)
    tn, fp, fn, tp = confusion_matrix(y_test, predictions, labels=[0, 1]).ravel()
    metrics = {
        "dataset": str(input_dir),
        "model": "random_forest_cicids",
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "benign_rows_used": int((y == 0).sum()),
        "attack_rows_used": int((y == 1).sum()),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1": float(f1_score(y_test, predictions, zero_division=0)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }
    artifact = {
        "model_type": "random_forest_cicids",
        "model": model,
        "feature_columns": feature_columns,
        "metadata": {
            **metrics,
            "input_dir": str(input_dir),
            "label_counts_seen": label_counts,
            "trained_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, model_out)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([metrics]).to_csv(metrics_out, index=False, encoding="utf-8-sig")
    return metrics


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Entraine un RandomForest reseau CICIDS")
    parser.add_argument("--input-dir", required=True, type=Path, help="Dossier MachineLearningCVE")
    parser.add_argument("--model-out", default=Path("models/random_forest_network_cicids.joblib"), type=Path)
    parser.add_argument("--metrics-out", default=Path("data/processed/random_forest_network_cicids_metrics.csv"), type=Path)
    parser.add_argument("--max-benign", default=150000, type=int, help="0 = toutes les lignes benign disponibles")
    parser.add_argument("--max-attack", default=150000, type=int, help="0 = toutes les lignes attaque disponibles")
    parser.add_argument("--max-per-attack-label", default=30000, type=int, help="0 = pas de limite par type d'attaque")
    parser.add_argument("--chunksize", default=100000, type=int)
    parser.add_argument("--test-size", default=0.2, type=float)
    parser.add_argument("--random-state", default=42, type=int)
    args = parser.parse_args(argv)

    metrics = train_model(
        args.input_dir,
        args.model_out,
        args.metrics_out,
        max_benign=args.max_benign,
        max_attack=args.max_attack,
        max_per_attack_label=args.max_per_attack_label,
        chunksize=args.chunksize,
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
