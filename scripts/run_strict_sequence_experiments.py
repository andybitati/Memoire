"""Run strict HDFS/BGL train-validation-test experiments for the final memoir audit."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import re
import subprocess
import time
from collections import Counter, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence
from drain3.template_miner_config import TemplateMinerConfig
from scipy.stats import t as student_t
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_recall_curve,
    precision_score,
    recall_score,
)
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs" / "memoire" / "final_experiments_2026"
CONFIG_PATH = DOC_ROOT / "configs" / "strict_sequence_protocol.json"
LEDGER_PATH = DOC_ROOT / "state" / "EXPERIMENT_LEDGER.csv"
FINAL_DATA = ROOT / "data" / "processed" / "final_experiments_2026"
PHASE_DIR = FINAL_DATA / "phase_3"
PREPARED_DIR = PHASE_DIR / "prepared"
STATE_DIR = FINAL_DATA / "drain3_train_state"
SEEDS = (42, 43, 44, 45, 46)
STOCHASTIC_METHODS = ("IsolationForest", "AutoencoderMLP", "EnsembleTrainCalibrated")
DETERMINISTIC_METHODS = ("ZScore", "IQR", "Histogram")
ALL_METHODS = STOCHASTIC_METHODS + DETERMINISTIC_METHODS
SPLITS = ("train", "validation", "test")
SEVERITY_RANK = {"": 0, "DEBUG": 1, "VERBOSE": 1, "INFO": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}
BLOCK_RE = re.compile(r"\bblk_-?\d+\b", re.IGNORECASE)
HDFS_RE = re.compile(
    r"^(?P<date>\d{6})\s+(?P<clock>\d{6})\s+\d+\s+(?P<severity>[A-Za-z]+)\s+(?P<source>[^:]+):\s*(?P<message>.*)$"
)
BGL_RE = re.compile(
    r"^(?P<label>\S+)\s+(?P<event_id>\d+)\s+(?P<date_raw>\d{4}\.\d{2}\.\d{2})\s+"
    r"(?P<node>\S+)\s+(?P<timestamp_raw>\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d+)\s+"
    r"(?P<source>\S+)\s+RAS\s+(?P<subsystem>\S+)\s+(?P<severity>[A-Za-z]+)\s+(?P<message>.*)$"
)


@dataclass
class WindowState:
    rows: deque[tuple[pd.Timestamp, int, str, int]] = field(default_factory=deque)
    templates: Counter[int] = field(default_factory=Counter)
    sources: Counter[str] = field(default_factory=Counter)
    errors: int = 0
    warnings: int = 0
    previous_time: pd.Timestamp | None = None
    previous_source: str = ""


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "INFORMATION À VÉRIFIER."


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_config() -> dict[str, object]:
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def sample_ranges(total: int, config: dict[str, object]) -> dict[str, tuple[int, int]]:
    split = config["split"]
    centres = split["sample_centres"]
    sizes = split["sample_rows_before_filtering"]
    ranges: dict[str, tuple[int, int]] = {}
    for name in SPLITS:
        size = int(sizes[name])
        centre = int(round(total * float(centres[name])))
        start = max(1, centre - size // 2)
        ranges[name] = (start, min(total, start + size - 1))
    return ranges


def hdfs_timestamp(date_value: str, clock_value: str) -> str:
    parsed = datetime.strptime(date_value + clock_value, "%y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    return parsed.isoformat()


def parse_hdfs(line: str, lineno: int, labels: dict[str, int]) -> dict[str, object] | None:
    match = HDFS_RE.match(line.rstrip("\r\n"))
    if match is None:
        return None
    message = match.group("message")
    block_match = BLOCK_RE.search(message)
    if block_match is None:
        return None
    block_id = block_match.group(0)
    if block_id not in labels:
        return None
    return {
        "dataset": "HDFS",
        "source_lineno": lineno,
        "timestamp_iso": hdfs_timestamp(match.group("date"), match.group("clock")),
        "source": match.group("source").strip(),
        "host": "",
        "severity": match.group("severity").upper(),
        "message": message,
        "block_id": block_id,
        "label": labels[block_id],
    }


def parse_bgl(line: str, lineno: int) -> dict[str, object] | None:
    match = BGL_RE.match(line.rstrip("\r\n"))
    if match is None:
        return None
    timestamp = datetime.strptime(match.group("timestamp_raw"), "%Y-%m-%d-%H.%M.%S.%f").replace(
        tzinfo=timezone.utc
    )
    return {
        "dataset": "BGL",
        "source_lineno": lineno,
        "timestamp_iso": timestamp.isoformat(),
        "source": match.group("source"),
        "host": match.group("node"),
        "severity": match.group("severity").upper(),
        "message": match.group("message"),
        "block_id": "",
        "label": int(match.group("label") != "-"),
    }


def extract_events(dataset: str, config: dict[str, object]) -> tuple[dict[str, pd.DataFrame], dict[str, object]]:
    dataset_config = config["datasets"][dataset]
    total = int(dataset_config["total_rows_manifest"])
    ranges = sample_ranges(total, config)
    raw_path = ROOT / dataset_config["raw_log"]
    labels: dict[str, int] = {}
    if dataset == "HDFS":
        labels_frame = pd.read_csv(ROOT / dataset_config["labels"], dtype=str)
        labels_frame.columns = [str(column).strip() for column in labels_frame.columns]
        labels = {
            str(row["BlockId"]).strip(): int(str(row["Label"]).strip().lower() == "anomaly")
            for _, row in labels_frame.iterrows()
        }

    selected: dict[str, list[dict[str, object]]] = {name: [] for name in SPLITS}
    parsed_counts = {name: 0 for name in SPLITS}
    max_line = max(end for _, end in ranges.values())
    active_ranges = [(name, start, end) for name, (start, end) in ranges.items()]
    with raw_path.open("r", encoding="utf-8", errors="replace") as handle:
        for lineno, line in enumerate(handle, start=1):
            if lineno > max_line:
                break
            split_name = next((name for name, start, end in active_ranges if start <= lineno <= end), None)
            if split_name is None:
                continue
            row = parse_hdfs(line, lineno, labels) if dataset == "HDFS" else parse_bgl(line, lineno)
            if row is not None:
                selected[split_name].append(row)
                parsed_counts[split_name] += 1

    frames = {name: pd.DataFrame(selected[name]) for name in SPLITS}
    overlap_removed = {"validation": 0, "test": 0}
    if dataset == "HDFS":
        train_groups = set(frames["train"]["block_id"].astype(str))
        validation_overlap = frames["validation"]["block_id"].astype(str).isin(train_groups)
        overlap_removed["validation"] = int(validation_overlap.sum())
        frames["validation"] = frames["validation"].loc[~validation_overlap].reset_index(drop=True)
        earlier_groups = train_groups | set(frames["validation"]["block_id"].astype(str))
        test_overlap = frames["test"]["block_id"].astype(str).isin(earlier_groups)
        overlap_removed["test"] = int(test_overlap.sum())
        frames["test"] = frames["test"].loc[~test_overlap].reset_index(drop=True)

    for name, frame in frames.items():
        if frame.empty:
            raise RuntimeError(f"{dataset} {name}: no parsed labelled event in frozen source range")
        output = PREPARED_DIR / f"{dataset.lower()}_{name}_events.csv"
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False, encoding="utf-8-sig")

    metadata = {
        "dataset": dataset,
        "raw_path": rel(raw_path),
        "raw_sha256": sha256_file(raw_path),
        "source_total_rows_manifest": total,
        "source_ranges_one_based_inclusive": {name: list(value) for name, value in ranges.items()},
        "selection_uses_labels": False,
        "parsed_before_overlap_filter": parsed_counts,
        "overlap_rows_removed": overlap_removed,
        "splits": {
            name: {
                "rows": int(len(frame)),
                "positives": int(frame["label"].astype(int).sum()),
                "positive_rate": float(frame["label"].astype(int).mean()),
                "first_source_lineno": int(frame["source_lineno"].astype(int).min()),
                "last_source_lineno": int(frame["source_lineno"].astype(int).max()),
                "first_timestamp": str(frame["timestamp_iso"].iloc[0]),
                "last_timestamp": str(frame["timestamp_iso"].iloc[-1]),
                "unique_groups": int(frame["block_id"].nunique()) if dataset == "HDFS" else None,
            }
            for name, frame in frames.items()
        },
    }
    return frames, metadata


def drain_config() -> TemplateMinerConfig:
    config = TemplateMinerConfig()
    config.profiling_enabled = False
    config.snapshot_interval_minutes = 0
    config.drain_sim_th = 0.4
    config.drain_depth = 4
    config.drain_max_children = 100
    config.drain_max_clusters = None
    config.parametrize_numeric_tokens = True
    config.snapshot_compress_state = True
    return config


def fit_and_reload_drain(dataset: str, train_messages: pd.Series) -> tuple[TemplateMiner, Path]:
    state_path = STATE_DIR / f"{dataset.lower()}_drain3_state.bin"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    if state_path.exists():
        state_path.unlink()
    miner = TemplateMiner(config=drain_config())
    for message in train_messages.fillna("").astype(str):
        miner.add_log_message(message)
    miner.persistence_handler = FilePersistence(str(state_path))
    miner.save_state("train_complete")
    if not state_path.exists() or state_path.stat().st_size == 0:
        raise RuntimeError(f"Drain3 state was not persisted for {dataset}")
    frozen = TemplateMiner(persistence_handler=FilePersistence(str(state_path)), config=drain_config())
    return frozen, state_path


def assign_templates(miner: TemplateMiner, frame: pd.DataFrame) -> tuple[np.ndarray, list[str]]:
    ids: list[int] = []
    templates: list[str] = []
    for message in frame["message"].fillna("").astype(str):
        cluster = miner.match(message, full_search_strategy="always")
        if cluster is None:
            ids.append(0)
            templates.append("<UNSEEN>")
        else:
            ids.append(int(cluster.cluster_id))
            templates.append(str(cluster.get_template()))
    return np.asarray(ids, dtype=np.int32), templates


def prune_window(state: WindowState, now: pd.Timestamp, window: pd.Timedelta) -> None:
    while state.rows and now - state.rows[0][0] > window:
        _, template_id, source, severity = state.rows.popleft()
        state.templates[template_id] -= 1
        if state.templates[template_id] <= 0:
            del state.templates[template_id]
        state.sources[source] -= 1
        if state.sources[source] <= 0:
            del state.sources[source]
        if severity >= SEVERITY_RANK["ERROR"]:
            state.errors -= 1
        elif severity >= SEVERITY_RANK["WARNING"]:
            state.warnings -= 1


def causal_features(
    dataset: str,
    frame: pd.DataFrame,
    template_ids: np.ndarray,
    template_frequency: Counter[int],
    source_frequency: Counter[str],
    train_rows: int,
) -> tuple[np.ndarray, list[str]]:
    names = [
        "severity_score",
        "message_length",
        "message_words",
        "template_frequency_train",
        "template_ratio_train",
        "template_unseen_train",
        "template_rare_train",
        "source_frequency_train",
        "source_unseen_train",
        "prior_global_window_events",
        "prior_global_window_errors",
        "prior_global_unique_templates",
        "prior_context_window_events",
        "prior_context_window_errors",
        "prior_context_unique_templates",
        "prior_same_template_context",
        "seconds_since_previous_global",
        "seconds_since_previous_context",
        "context_source_switch",
    ]
    values = np.zeros((len(frame), len(names)), dtype=np.float64)
    timestamps = pd.to_datetime(frame["timestamp_iso"], errors="coerce", utc=True)
    fallback = pd.Timestamp("1970-01-01T00:00:00Z") + pd.to_timedelta(np.arange(len(frame)), unit="s")
    timestamps = timestamps.fillna(pd.Series(fallback, index=frame.index))
    global_state = WindowState()
    contexts: dict[str, WindowState] = {}
    window = pd.Timedelta(minutes=30)
    for position, (_, row) in enumerate(frame.iterrows()):
        now = timestamps.iloc[position]
        template_id = int(template_ids[position])
        source = str(row.get("source", ""))
        severity = SEVERITY_RANK.get(str(row.get("severity", "")).upper(), 0)
        context_key = str(row.get("block_id", "")) if dataset == "HDFS" else str(row.get("host", "") or source)
        context = contexts.setdefault(context_key, WindowState())
        prune_window(global_state, now, window)
        prune_window(context, now, window)
        global_gap = 0.0 if global_state.previous_time is None else max((now - global_state.previous_time).total_seconds(), 0.0)
        context_gap = 0.0 if context.previous_time is None else max((now - context.previous_time).total_seconds(), 0.0)
        message = str(row.get("message", ""))
        tf = int(template_frequency.get(template_id, 0)) if template_id else 0
        sf = int(source_frequency.get(source, 0))
        values[position] = [
            severity,
            len(message),
            len(message.split()),
            tf,
            tf / max(train_rows, 1),
            int(template_id == 0 or tf == 0),
            int(tf <= 2),
            sf,
            int(sf == 0),
            len(global_state.rows),
            global_state.errors,
            len(global_state.templates),
            len(context.rows),
            context.errors,
            len(context.templates),
            context.templates.get(template_id, 0),
            global_gap,
            context_gap,
            int(bool(context.previous_source and context.previous_source != source)),
        ]
        for state in (global_state, context):
            state.rows.append((now, template_id, source, severity))
            state.templates[template_id] += 1
            state.sources[source] += 1
            if severity >= SEVERITY_RANK["ERROR"]:
                state.errors += 1
            elif severity >= SEVERITY_RANK["WARNING"]:
                state.warnings += 1
            state.previous_time = now
            state.previous_source = source
    values[~np.isfinite(values)] = 0.0
    return values, names


def histogram_scores(
    frames: dict[str, pd.DataFrame], template_ids: dict[str, np.ndarray]
) -> dict[str, np.ndarray]:
    normal_mask = frames["train"]["label"].astype(int).to_numpy() == 0
    normal_count = max(int(normal_mask.sum()), 1)
    template_counts = Counter(template_ids["train"][normal_mask].tolist())
    source_counts = Counter(frames["train"].loc[normal_mask, "source"].astype(str))
    severity_counts = Counter(frames["train"].loc[normal_mask, "severity"].astype(str))
    outputs: dict[str, np.ndarray] = {}
    for name in SPLITS:
        scores: list[float] = []
        for template_id, source, severity in zip(
            template_ids[name], frames[name]["source"].astype(str), frames[name]["severity"].astype(str)
        ):
            probabilities = (
                max(template_counts.get(int(template_id), 0), 1) / normal_count,
                max(source_counts.get(source, 0), 1) / normal_count,
                max(severity_counts.get(severity, 0), 1) / normal_count,
            )
            scores.append(float(sum(-math.log(value) for value in probabilities) / 3.0))
        outputs[name] = np.asarray(scores, dtype=np.float64)
    return outputs


def prepare_bundle(dataset: str, config: dict[str, object], *, force: bool = False) -> dict[str, object]:
    bundle_path = PREPARED_DIR / f"{dataset.lower()}_feature_bundle.npz"
    metadata_path = PREPARED_DIR / f"{dataset.lower()}_preparation.json"
    if bundle_path.exists() and metadata_path.exists() and not force:
        arrays = np.load(bundle_path, allow_pickle=False)
        return {key: arrays[key] for key in arrays.files} | {
            "metadata": json.loads(metadata_path.read_text(encoding="utf-8"))
        }

    frames, metadata = extract_events(dataset, config)
    miner, state_path = fit_and_reload_drain(dataset, frames["train"]["message"])
    template_ids: dict[str, np.ndarray] = {}
    template_strings: dict[str, list[str]] = {}
    for name in SPLITS:
        template_ids[name], template_strings[name] = assign_templates(miner, frames[name])
        frames[name]["drain_cluster_id"] = template_ids[name]
        frames[name]["drain_template"] = template_strings[name]
        frames[name].to_csv(PREPARED_DIR / f"{dataset.lower()}_{name}_events.csv", index=False, encoding="utf-8-sig")

    train_normal = frames["train"]["label"].astype(int).to_numpy() == 0
    train_template_frequency = Counter(template_ids["train"][train_normal].tolist())
    train_source_frequency = Counter(frames["train"].loc[train_normal, "source"].astype(str))
    matrices: dict[str, np.ndarray] = {}
    feature_names: list[str] = []
    for name in SPLITS:
        matrices[name], feature_names = causal_features(
            dataset,
            frames[name],
            template_ids[name],
            train_template_frequency,
            train_source_frequency,
            int(train_normal.sum()),
        )
    histogram = histogram_scores(frames, template_ids)
    arrays: dict[str, np.ndarray] = {
        "feature_names": np.asarray(feature_names),
    }
    for name in SPLITS:
        arrays[f"X_{name}"] = matrices[name]
        arrays[f"y_{name}"] = frames[name]["label"].astype(int).to_numpy()
        arrays[f"hist_{name}"] = histogram[name]
        arrays[f"template_id_{name}"] = template_ids[name]
    np.savez_compressed(bundle_path, **arrays)

    metadata["drain3"] = {
        "version": importlib.metadata.version("drain3"),
        "cachetools_version": importlib.metadata.version("cachetools"),
        "state_path": rel(state_path),
        "state_sha256": sha256_file(state_path),
        "state_bytes": state_path.stat().st_size,
        "cluster_count": int(len(miner.drain.clusters)),
        "fit_partition": "train_only",
        "inference_updates": 0,
        "parameters": config["drain3"]["parameters"],
        "unknown_template_rate": {
            name: float(np.mean(template_ids[name] == 0)) for name in SPLITS
        },
    }
    metadata["features"] = {
        "count": len(feature_names),
        "names": feature_names,
        "template_statistics_partition": "normal-labelled train only",
        "window_direction": "past_only",
        "partition_state": "reset",
    }
    metadata["generated_at"] = utc_now()
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    refresh_template_manifest()
    return arrays | {"metadata": metadata}


def refresh_template_manifest() -> None:
    datasets: dict[str, object] = {}
    for dataset in ("HDFS", "BGL"):
        path = PREPARED_DIR / f"{dataset.lower()}_preparation.json"
        if path.exists():
            datasets[dataset] = json.loads(path.read_text(encoding="utf-8"))
    manifest = {
        "schema_version": 1,
        "generated_at": utc_now(),
        "fit_policy": "one TemplateMiner per dataset, train messages only",
        "validation_test_policy": "frozen match only; zero add_log_message calls",
        "datasets": datasets,
    }
    (FINAL_DATA / "drain3_template_manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def iqr_scores(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    q1 = np.quantile(reference, 0.25, axis=0)
    q3 = np.quantile(reference, 0.75, axis=0)
    scale = q3 - q1
    scale[scale == 0] = 1.0
    lower = q1 - 1.5 * scale
    upper = q3 + 1.5 * scale
    return (np.maximum(lower - values, 0) / scale + np.maximum(values - upper, 0) / scale).sum(axis=1)


def empirical_percentile(reference: np.ndarray, values: np.ndarray) -> np.ndarray:
    ordered = np.sort(np.asarray(reference, dtype=float))
    return np.searchsorted(ordered, values, side="right") / max(len(ordered), 1)


def prediction_metrics(truth: np.ndarray, scores: np.ndarray, threshold: float) -> dict[str, object]:
    predictions = (scores >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(truth, predictions, labels=[0, 1]).ravel()
    return {
        "precision": float(precision_score(truth, predictions, zero_division=0)),
        "recall": float(recall_score(truth, predictions, zero_division=0)),
        "f1": float(f1_score(truth, predictions, zero_division=0)),
        "pr_auc": float(average_precision_score(truth, scores)) if len(np.unique(truth)) > 1 else math.nan,
        "mcc": float(matthews_corrcoef(truth, predictions)),
        "fpr": float(fp / max(fp + tn, 1)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "predicted_positive": int(predictions.sum()),
    }


def select_threshold(truth: np.ndarray, scores: np.ndarray) -> tuple[float, dict[str, object]]:
    precision, recall, thresholds = precision_recall_curve(truth, scores)
    if len(thresholds) == 0:
        threshold = float(np.max(scores) + np.finfo(float).eps)
        return threshold, prediction_metrics(truth, scores, threshold)
    f1_values = 2 * precision[:-1] * recall[:-1] / np.maximum(precision[:-1] + recall[:-1], 1e-15)
    best = float(np.nanmax(f1_values))
    candidates = np.flatnonzero(np.isclose(f1_values, best, rtol=0, atol=1e-12))
    ranked: list[tuple[float, float, float, float, dict[str, object]]] = []
    for index in candidates:
        threshold = float(thresholds[index])
        metrics = prediction_metrics(truth, scores, threshold)
        ranked.append((float(metrics["fpr"]), -float(metrics["mcc"]), -threshold, threshold, metrics))
    _, _, _, threshold, metrics = min(ranked)
    return threshold, metrics


def score_sets(bundle: dict[str, object], seed: int) -> dict[str, dict[str, np.ndarray]]:
    X = {name: np.asarray(bundle[f"X_{name}"], dtype=float) for name in SPLITS}
    y = {name: np.asarray(bundle[f"y_{name}"], dtype=int) for name in SPLITS}
    normal = y["train"] == 0
    X_normal = X["train"][normal]
    if len(X_normal) < 2:
        raise RuntimeError("Fewer than two normal training observations")
    scaler = StandardScaler().fit(X_normal)
    scaled = {name: scaler.transform(X[name]) for name in SPLITS}

    scores: dict[str, dict[str, np.ndarray]] = {method: {} for method in ALL_METHODS}
    isolation = IsolationForest(n_estimators=200, contamination="auto", random_state=seed, n_jobs=1)
    isolation.fit(X_normal)
    for name in SPLITS:
        scores["IsolationForest"][name] = -isolation.decision_function(X[name])
        scores["ZScore"][name] = np.abs(scaled[name]).max(axis=1)
        scores["IQR"][name] = iqr_scores(X_normal, X[name])
        scores["Histogram"][name] = np.asarray(bundle[f"hist_{name}"], dtype=float)

    hidden = min(32, max(4, X_normal.shape[1] // 2))
    generator = np.random.default_rng(seed)
    if len(X_normal) > 12000:
        sample_indices = generator.choice(len(X_normal), size=12000, replace=False)
        ae_fit = scaled["train"][normal][sample_indices]
    else:
        ae_fit = scaled["train"][normal]
    autoencoder = MLPRegressor(
        hidden_layer_sizes=(hidden,),
        activation="relu",
        solver="adam",
        max_iter=80,
        random_state=seed,
        early_stopping=True,
        n_iter_no_change=8,
    )
    autoencoder.fit(ae_fit, ae_fit)
    for name in SPLITS:
        reconstructed = autoencoder.predict(scaled[name])
        scores["AutoencoderMLP"][name] = ((scaled[name] - reconstructed) ** 2).mean(axis=1)

    component_names = ("IsolationForest", "ZScore", "IQR", "Histogram", "AutoencoderMLP")
    for name in SPLITS:
        calibrated = [
            empirical_percentile(scores[component]["train"][normal], scores[component][name])
            for component in component_names
        ]
        scores["EnsembleTrainCalibrated"][name] = np.mean(np.column_stack(calibrated), axis=1)
    return scores


def ledger_columns() -> list[str]:
    with LEDGER_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        return next(csv.reader(handle))


def append_ledger(
    experiment_id: str,
    dataset: str,
    seed: int,
    method: str,
    status: str,
    raw_path: Path,
    *,
    started_at: str = "",
    completed_at: str = "",
    error_path: str = "",
    notes: str = "",
) -> None:
    columns = ledger_columns()
    values = {
        "experiment_id": experiment_id,
        "phase": "3",
        "run_id": experiment_id,
        "dataset": dataset,
        "scenario": "strict_chronological_holdout",
        "seed": str(seed),
        "model": method,
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "command": f"scripts/run_strict_sequence_experiments.py --resume --dataset {dataset.lower()} --method {method} --seed {seed}",
        "config_path": rel(CONFIG_PATH),
        "raw_result_path": rel(raw_path),
        "summary_path": rel(FINAL_DATA / f"{dataset.lower()}_strict_drain3_summary.csv"),
        "figure_path": "",
        "error_path": error_path,
        "git_commit": git_commit(),
        "notes": notes,
    }
    with LEDGER_PATH.open("a", encoding="utf-8-sig", newline="") as handle:
        csv.DictWriter(handle, fieldnames=columns).writerow({column: values.get(column, "") for column in columns})


def valid_artifact(path: Path, experiment_id: str) -> bool:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return (
        payload.get("experiment_id") == experiment_id
        and payload.get("dataset") in {"HDFS", "BGL"}
        and payload.get("seed") is not None
        and isinstance(payload.get("configuration"), dict)
        and isinstance(payload.get("metrics"), dict)
    )


def planned_runs(dataset: str) -> list[tuple[str, int]]:
    return [(method, seed) for method in STOCHASTIC_METHODS for seed in SEEDS] + [
        (method, 42) for method in DETERMINISTIC_METHODS
    ]


def confidence_half_width(values: pd.Series) -> float:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if len(clean) < 2:
        return math.nan
    return float(student_t.ppf(0.975, len(clean) - 1) * clean.std(ddof=1) / math.sqrt(len(clean)))


def refresh_outputs(dataset: str) -> None:
    rows: list[dict[str, object]] = []
    for path in sorted(PHASE_DIR.glob(f"e3_strict_{dataset.lower()}_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rows.append(
            {
                "experiment_id": payload["experiment_id"],
                "run_id": payload["run_id"],
                "dataset": payload["dataset"],
                "seed": payload["seed"],
                "method": payload["method"],
                "threshold": payload["threshold"],
                "train_rows": payload["configuration"]["split_rows"]["train"],
                "validation_rows": payload["configuration"]["split_rows"]["validation"],
                "test_rows": payload["configuration"]["split_rows"]["test"],
                **payload["metrics"],
                "fit_score_time_sec": payload["fit_score_time_sec"],
                "artifact_path": rel(path),
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        return
    frame.to_csv(FINAL_DATA / f"{dataset.lower()}_strict_drain3_raw.csv", index=False, encoding="utf-8-sig")
    records: list[dict[str, object]] = []
    for method, group in frame.groupby("method"):
        records.append(
            {
                "dataset": dataset,
                "method": method,
                "n": int(len(group)),
                "seeds": ",".join(str(int(value)) for value in sorted(group["seed"].unique())),
                "f1_mean": float(group["f1"].mean()),
                "f1_std": float(group["f1"].std(ddof=1)) if len(group) > 1 else math.nan,
                "f1_median": float(group["f1"].median()),
                "f1_min": float(group["f1"].min()),
                "f1_max": float(group["f1"].max()),
                "f1_ci95_half_width": confidence_half_width(group["f1"]),
                "precision_mean": float(group["precision"].mean()),
                "recall_mean": float(group["recall"].mean()),
                "pr_auc_mean": float(group["pr_auc"].mean()),
                "mcc_mean": float(group["mcc"].mean()),
                "fpr_mean": float(group["fpr"].mean()),
                "fit_score_time_sec_mean": float(group["fit_score_time_sec"].mean()),
            }
        )
    pd.DataFrame(records).sort_values("f1_mean", ascending=False).to_csv(
        FINAL_DATA / f"{dataset.lower()}_strict_drain3_summary.csv", index=False, encoding="utf-8-sig"
    )


def run_dataset(
    dataset: str,
    config: dict[str, object],
    *,
    resume: bool,
    method_filter: str | None,
    seed_filter: int | None,
    prepare_only: bool,
) -> int:
    bundle = prepare_bundle(dataset, config)
    if prepare_only:
        print(f"PREPARED {dataset} {json.dumps(bundle['metadata']['splits'], ensure_ascii=False)}")
        return 0
    y = {name: np.asarray(bundle[f"y_{name}"], dtype=int) for name in SPLITS}
    plans = [
        (method, seed)
        for method, seed in planned_runs(dataset)
        if (method_filter is None or method == method_filter) and (seed_filter is None or seed == seed_filter)
    ]
    failures = 0
    scores_by_seed: dict[int, dict[str, dict[str, np.ndarray]]] = {}
    for method, seed in plans:
        experiment_id = f"e3_strict_{dataset.lower()}_seed{seed}_{method.lower()}"
        raw_path = PHASE_DIR / f"{experiment_id}.json"
        if valid_artifact(raw_path, experiment_id):
            print(f"SKIPPED_ALREADY_COMPLETED {experiment_id}")
            continue
        if raw_path.exists() and not resume:
            print(f"SKIPPED_EXISTING_INVALID {experiment_id}")
            continue
        started = utc_now()
        append_ledger(experiment_id, dataset, seed, method, "PLANNED", raw_path)
        append_ledger(experiment_id, dataset, seed, method, "RUNNING", raw_path, started_at=started)
        try:
            timing = time.perf_counter()
            if seed not in scores_by_seed:
                scores_by_seed[seed] = score_sets(bundle, seed)
            scores = scores_by_seed[seed][method]
            threshold, validation_metrics = select_threshold(y["validation"], scores["validation"])
            metrics = prediction_metrics(y["test"], scores["test"], threshold)
            duration = time.perf_counter() - timing
            payload = {
                "schema_version": 1,
                "experiment_id": experiment_id,
                "run_id": experiment_id,
                "phase": 3,
                "dataset": dataset,
                "scenario": "strict_chronological_holdout",
                "seed": seed,
                "method": method,
                "generated_at": utc_now(),
                "git_commit": git_commit(),
                "configuration": {
                    "protocol_path": rel(CONFIG_PATH),
                    "split_rows": {name: int(len(y[name])) for name in SPLITS},
                    "split_positive_rate": {name: float(y[name].mean()) for name in SPLITS},
                    "feature_count": int(np.asarray(bundle["X_train"]).shape[1]),
                    "feature_names": np.asarray(bundle["feature_names"]).astype(str).tolist(),
                    "drain3_state_path": bundle["metadata"]["drain3"]["state_path"],
                    "drain3_state_sha256": bundle["metadata"]["drain3"]["state_sha256"],
                    "threshold_selected_on": "validation_only",
                    "threshold_objective": "maximum_f1_then_min_fpr_then_max_mcc_then_highest_threshold",
                    "test_prevalence_used": False,
                    "test_score_distribution_used_for_threshold": False,
                },
                "threshold": threshold,
                "validation_metrics": validation_metrics,
                "metrics": metrics,
                "fit_score_time_sec": duration,
            }
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            raw_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if not valid_artifact(raw_path, experiment_id):
                raise RuntimeError("written artifact failed validation")
            append_ledger(
                experiment_id,
                dataset,
                seed,
                method,
                "COMPLETED",
                raw_path,
                started_at=started,
                completed_at=utc_now(),
            )
            refresh_outputs(dataset)
            print(f"COMPLETED {experiment_id} f1={metrics['f1']:.6f} pr_auc={metrics['pr_auc']:.6f}")
        except Exception as exc:
            failures += 1
            error_path = DOC_ROOT / "logs" / f"{experiment_id}.log"
            error_path.parent.mkdir(parents=True, exist_ok=True)
            error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
            append_ledger(
                experiment_id,
                dataset,
                seed,
                method,
                "FAILED",
                raw_path,
                started_at=started,
                completed_at=utc_now(),
                error_path=rel(error_path),
                notes=f"{type(exc).__name__}: {exc}",
            )
            print(f"FAILED {experiment_id}: {type(exc).__name__}: {exc}")
    refresh_outputs(dataset)
    return failures


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Strict HDFS/BGL Drain3 train-validation-test experiments")
    parser.add_argument("--dataset", choices=["hdfs", "bgl", "all"], default="all")
    parser.add_argument("--method", choices=list(ALL_METHODS))
    parser.add_argument("--seed", type=int, choices=list(SEEDS))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--force-prepare", action="store_true")
    args = parser.parse_args(argv)
    datasets = ("HDFS", "BGL") if args.dataset == "all" else (args.dataset.upper(),)
    if args.dry_run:
        for dataset in datasets:
            for method, seed in planned_runs(dataset):
                if args.method and args.method != method:
                    continue
                if args.seed is not None and args.seed != seed:
                    continue
                experiment_id = f"e3_strict_{dataset.lower()}_seed{seed}_{method.lower()}"
                raw_path = PHASE_DIR / f"{experiment_id}.json"
                state = "SKIPPED_ALREADY_COMPLETED" if valid_artifact(raw_path, experiment_id) else "WOULD_RUN"
                print(f"{state} {experiment_id}")
        return 0
    config = load_config()
    failures = 0
    for dataset in datasets:
        if args.force_prepare:
            for path in (
                PREPARED_DIR / f"{dataset.lower()}_feature_bundle.npz",
                PREPARED_DIR / f"{dataset.lower()}_preparation.json",
            ):
                if path.exists():
                    path.unlink()
        failures += run_dataset(
            dataset,
            config,
            resume=args.resume,
            method_filter=args.method,
            seed_filter=args.seed,
            prepare_only=args.prepare_only,
        )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
