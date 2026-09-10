"""Utilitaires partagés par les campagnes de renforcement des datasets."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
)


ROOT = Path(__file__).resolve().parents[1]
PHASE_ROOT = ROOT / "experiments" / "phase_dataset_strengthening"
CONFIG_PATH = PHASE_ROOT / "configs" / "dataset_strengthening_protocol.json"
PHASE_LEDGER = PHASE_ROOT / "LEDGER.csv"
GLOBAL_LEDGER = ROOT / "state" / "EXPERIMENT_LEDGER.csv"
LEDGER_FIELDS = [
    "experiment_id",
    "phase",
    "run_id",
    "dataset",
    "protocol",
    "status",
    "started_at",
    "completed_at",
    "command",
    "config_path",
    "raw_result_path",
    "summary_path",
    "figure_path",
    "error_path",
    "git_commit",
    "notes",
]


def ensure_phase_dirs() -> None:
    for name in ("raw", "processed", "aggregated", "figures", "logs", "reports", "manifests"):
        (PHASE_ROOT / name).mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "INFORMATION À VÉRIFIER."


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    data = list(rows)
    if fieldnames is None:
        fieldnames = list(data[0]) if data else []
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(data)


def append_ledger(**values: Any) -> None:
    row = {field: values.get(field, "") for field in LEDGER_FIELDS}
    row["config_path"] = row["config_path"] or relative(CONFIG_PATH)
    row["git_commit"] = row["git_commit"] or git_commit()
    for ledger in (PHASE_LEDGER, GLOBAL_LEDGER):
        ledger.parent.mkdir(parents=True, exist_ok=True)
        write_header = not ledger.exists() or ledger.stat().st_size == 0
        with ledger.open("a", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, extrasaction="ignore")
            if write_header:
                writer.writeheader()
            writer.writerow(row)


def binary_metrics(truth: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, Any]:
    y_true = np.asarray(truth, dtype=np.int8)
    y_score = np.asarray(scores, dtype=np.float64)
    prediction = (y_score >= float(threshold)).astype(np.int8)
    tn, fp, fn, tp = confusion_matrix(y_true, prediction, labels=[0, 1]).ravel()
    return {
        "n": int(len(y_true)),
        "prevalence": float(y_true.mean()) if len(y_true) else math.nan,
        "precision": float(precision_score(y_true, prediction, zero_division=0)),
        "recall": float(recall_score(y_true, prediction, zero_division=0)),
        "f1": float(f1_score(y_true, prediction, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, y_score)) if len(np.unique(y_true)) > 1 else math.nan,
        "mcc": float(matthews_corrcoef(y_true, prediction)) if len(y_true) else math.nan,
        "fpr": float(fp / max(fp + tn, 1)),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "predicted_positive": int(prediction.sum()),
        "threshold": float(threshold),
    }


def metrics_from_prediction(truth: np.ndarray, prediction: np.ndarray, score: np.ndarray | None = None) -> dict[str, Any]:
    y_true = np.asarray(truth, dtype=np.int8)
    y_pred = np.asarray(prediction, dtype=np.int8)
    y_score = np.asarray(score if score is not None else y_pred, dtype=np.float64)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "n": int(len(y_true)),
        "prevalence": float(y_true.mean()) if len(y_true) else math.nan,
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, y_score)) if len(np.unique(y_true)) > 1 else math.nan,
        "mcc": float(matthews_corrcoef(y_true, y_pred)) if len(y_true) else math.nan,
        "fpr": float(fp / max(fp + tn, 1)),
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "predicted_positive": int(y_pred.sum()),
    }


def select_threshold(truth: np.ndarray, scores: np.ndarray) -> tuple[float, dict[str, Any]]:
    y_true = np.asarray(truth, dtype=np.int8)
    y_score = np.asarray(scores, dtype=np.float64)
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    if len(thresholds) == 0:
        threshold = float(np.max(y_score) + np.finfo(float).eps)
        return threshold, binary_metrics(y_true, y_score, threshold)
    f1_values = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-15)
    best_f1 = float(np.nanmax(f1_values))
    candidates = np.flatnonzero(np.isclose(f1_values, best_f1, rtol=0, atol=1e-12))
    ranked: list[tuple[float, float, float, float, dict[str, Any]]] = []
    for index in candidates:
        threshold = float(thresholds[index])
        metrics = binary_metrics(y_true, y_score, threshold)
        ranked.append((float(metrics["fpr"]), -float(metrics["mcc"]), -threshold, threshold, metrics))
    _, _, _, threshold, metrics = min(ranked)
    return threshold, metrics


def descriptive(values: Iterable[float]) -> dict[str, Any]:
    array = np.asarray(list(values), dtype=np.float64)
    n = int(len(array))
    if n == 0:
        return {"n": 0}
    mean = float(array.mean())
    std = float(array.std(ddof=1)) if n > 1 else math.nan
    half = float(1.96 * std / math.sqrt(n)) if n > 1 else math.nan
    return {
        "n": n,
        "mean": mean,
        "sample_std": std,
        "median": float(np.median(array)),
        "min": float(array.min()),
        "max": float(array.max()),
        "ci95_low": mean - half if n > 1 else math.nan,
        "ci95_high": mean + half if n > 1 else math.nan,
    }
