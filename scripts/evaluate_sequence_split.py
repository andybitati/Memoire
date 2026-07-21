"""Evaluation train -> test pour logs sequentiels HDFS/BGL enrichis.

Contrairement a `model_compare.py`, ce script ajuste les detecteurs sur le CSV
train puis score le CSV test. Il sert aux validations HDFS/BGL avec split
chronologique ou par groupe.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler

import sys

BASE_DIR = Path(__file__).resolve().parents[1] / "src" / "logminer"
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from features.event_features import build_feature_frame, load_events


def _labels(frame: pd.DataFrame, label_column: str) -> pd.Series:
    if label_column not in frame:
        raise ValueError(f"Colonne label introuvable: {label_column}")
    values = frame[label_column].astype(str).str.strip().str.lower()
    numeric = pd.to_numeric(values, errors="coerce")
    positive = values.isin({"1", "true", "yes", "anomaly", "abnormal", "attack", "failure", "fail", "*"})
    labels = positive.astype(int)
    labels = labels.mask(numeric.notna(), (numeric.fillna(0) != 0).astype(int))
    return labels.astype(int)


def _align(train_features: pd.DataFrame, test_features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = train_features.astype(float)
    test = test_features.reindex(columns=list(train.columns), fill_value=0).astype(float)
    return train, test


def _top_by_score(scores: pd.Series, quota: float, higher_is_anomalous: bool) -> pd.Series:
    limit = max(1, int(round(len(scores) * min(max(float(quota), 0.001), 0.5))))
    selected = scores.nlargest(limit) if higher_is_anomalous else scores.nsmallest(limit)
    labels = pd.Series(0, index=scores.index, dtype=int)
    labels.loc[selected.index] = 1
    return labels


def _summarize(model: str, scores: pd.Series, predictions: pd.Series, truth: pd.Series, notes: str) -> dict[str, object]:
    tn, fp, fn, tp = confusion_matrix(truth, predictions, labels=[0, 1]).ravel()
    specificity = tn / max(tn + fp, 1)
    return {
        "model": model,
        "events": int(len(truth)),
        "anomalies": int(predictions.sum()),
        "anomaly_rate": round(float(predictions.mean()), 6),
        "score_min": round(float(scores.min()), 6),
        "score_mean": round(float(scores.mean()), 6),
        "score_max": round(float(scores.max()), 6),
        "precision": round(float(precision_score(truth, predictions, zero_division=0)), 6),
        "recall": round(float(recall_score(truth, predictions, zero_division=0)), 6),
        "f1": round(float(f1_score(truth, predictions, zero_division=0)), 6),
        "accuracy": round(float(accuracy_score(truth, predictions)), 6),
        "specificity": round(float(specificity), 6),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn),
        "notes": notes,
    }


def _rank_strength(scores: pd.Series, lower_is_anomalous: bool) -> pd.Series:
    values = -scores if lower_is_anomalous else scores
    return values.rank(method="average", pct=True).fillna(0.0)


def _histogram_scores(train_events: pd.DataFrame, test_events: pd.DataFrame) -> pd.Series:
    columns = [column for column in ("event", "source", "severity", "category", "subcategory", "host") if column in train_events]
    scores = pd.Series(0.0, index=test_events.index)
    for column in columns:
        frequencies = train_events[column].fillna("").astype(str).value_counts(dropna=False, normalize=True)
        values = test_events.get(column, pd.Series("", index=test_events.index)).fillna("").astype(str)
        scores += values.map(lambda value: -np.log(max(float(frequencies.get(value, 1e-12)), 1e-12)))
    return scores / max(len(columns), 1)


def evaluate_split(
    train_csv: Path,
    test_csv: Path,
    output_csv: Path,
    *,
    sep: str = ";",
    label_column: str = "label",
    contamination: str | float = "train",
    random_state: int = 42,
) -> Path:
    train_events = load_events(train_csv, sep=sep)
    test_events = load_events(test_csv, sep=sep)
    train_truth = _labels(train_events, label_column)
    test_truth = _labels(test_events, label_column)
    if str(contamination).lower() == "train":
        quota = max(float(train_truth.mean()), 1 / max(len(train_truth), 1))
    elif str(contamination).lower() == "test":
        quota = max(float(test_truth.mean()), 1 / max(len(test_truth), 1))
    else:
        quota = float(contamination)

    train_features, test_features = _align(build_feature_frame(train_events), build_feature_frame(test_events))
    rows: list[dict[str, object]] = []

    iso = IsolationForest(n_estimators=200, contamination=min(max(quota, 0.001), 0.5), random_state=random_state, n_jobs=1)
    iso.fit(train_features)
    iso_scores = pd.Series(iso.decision_function(test_features), index=test_events.index)
    iso_predictions = _top_by_score(iso_scores, quota, higher_is_anomalous=False)
    rows.append(_summarize("isolation_forest_train_test", iso_scores, iso_predictions, test_truth, "Fit train, score test"))

    scaler = StandardScaler()
    train_scaled = pd.DataFrame(scaler.fit_transform(train_features), index=train_features.index, columns=train_features.columns)
    test_scaled = pd.DataFrame(scaler.transform(test_features), index=test_features.index, columns=test_features.columns)
    z_scores = test_scaled.abs().max(axis=1)
    z_predictions = _top_by_score(z_scores, quota, higher_is_anomalous=True)
    rows.append(_summarize("z_score_train_test", z_scores, z_predictions, test_truth, "Standardisation apprise sur train"))

    q1 = train_features.quantile(0.25)
    q3 = train_features.quantile(0.75)
    iqr = (q3 - q1).replace(0, 1)
    iqr_scores = ((q1 - 1.5 * iqr - test_features).clip(lower=0).div(iqr) + (test_features - q3 - 1.5 * iqr).clip(lower=0).div(iqr)).sum(axis=1)
    iqr_predictions = _top_by_score(iqr_scores, quota, higher_is_anomalous=True)
    rows.append(_summarize("iqr_train_test", iqr_scores, iqr_predictions, test_truth, "Bornes IQR apprises sur train"))

    hist_scores = _histogram_scores(train_events, test_events)
    hist_predictions = _top_by_score(hist_scores, quota, higher_is_anomalous=True)
    rows.append(_summarize("histogram_train_test", hist_scores, hist_predictions, test_truth, "Frequences apprises sur train"))

    hidden = max(4, min(32, train_scaled.shape[1] // 2 or 4))
    sample = train_scaled.sample(12000, random_state=random_state) if len(train_scaled) > 12000 else train_scaled
    ae = MLPRegressor(
        hidden_layer_sizes=(hidden,),
        activation="relu",
        solver="adam",
        max_iter=80,
        random_state=random_state,
        early_stopping=True,
        n_iter_no_change=8,
    )
    ae.fit(sample, sample)
    reconstructed = ae.predict(test_scaled)
    ae_scores = pd.Series(((test_scaled.to_numpy() - reconstructed) ** 2).mean(axis=1), index=test_events.index)
    ae_predictions = _top_by_score(ae_scores, quota, higher_is_anomalous=True)
    rows.append(_summarize("autoencoder_mlp_train_test", ae_scores, ae_predictions, test_truth, "Autoencoder fit train, score test"))

    ensemble_scores = pd.concat(
        [
            _rank_strength(iso_scores, lower_is_anomalous=True),
            _rank_strength(z_scores, lower_is_anomalous=False),
            _rank_strength(hist_scores, lower_is_anomalous=False),
            _rank_strength(ae_scores, lower_is_anomalous=False),
        ],
        axis=1,
    ).mean(axis=1)
    ensemble_predictions = _top_by_score(ensemble_scores, quota, higher_is_anomalous=True)
    rows.append(_summarize("ensemble_train_test", ensemble_scores, ensemble_predictions, test_truth, "Moyenne des rangs IF/Z/hist/AE"))

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output_csv, sep=sep, index=False, encoding="utf-8-sig")
    return output_csv


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evalue des detecteurs sequentiels fit train -> score test")
    parser.add_argument("--train", required=True, type=Path)
    parser.add_argument("--test", required=True, type=Path)
    parser.add_argument("-o", "--output", required=True, type=Path)
    parser.add_argument("--sep", default=";")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--contamination", default="train", help="'train', 'test' ou valeur numerique")
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args(argv)

    output = evaluate_split(
        args.train,
        args.test,
        args.output,
        sep=args.sep,
        label_column=args.label_column,
        contamination=args.contamination,
        random_state=args.random_state,
    )
    print(f"Evaluation train/test: {output}")
    print(pd.read_csv(output, sep=args.sep).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
