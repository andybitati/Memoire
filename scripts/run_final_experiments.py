"""Runner reprenable pour les expériences finales du mémoire Logminer.

Le registre est append-only : la dernière ligne d'un ``experiment_id`` décrit
son état courant. Chaque run écrit immédiatement un artefact JSON atomique.
Les anciens artefacts du projet ne sont jamais utilisés comme destination.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.metadata
import json
import math
import os
import platform
import subprocess
import sys
import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import psutil
from scipy.stats import t as student_t
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

from evaluate_cicids_model_candidates import _candidate_models, _score
from evaluate_supervised_strict_splits import _network_feature_columns, collect_network_sample


ROOT = Path(__file__).resolve().parents[1]
FINAL_DATA = ROOT / "data" / "processed" / "final_experiments_2026"
FINAL_DOCS = ROOT / "docs" / "memoire" / "final_experiments_2026"
STATE = FINAL_DOCS / "state"
CONFIGS = FINAL_DOCS / "configs"
TABLES = FINAL_DOCS / "tables"
FIGURES = FINAL_DOCS / "figures"
LOGS = FINAL_DOCS / "logs"
LEDGER = STATE / "EXPERIMENT_LEDGER.csv"
ARTIFACT_INDEX = STATE / "ARTIFACT_INDEX.json"
CICIDS_CONFIG = CONFIGS / "cicids_final_protocol.json"

SEEDS = (42, 43, 44, 45, 46)
SCENARIO_FILES = {
    "DDoS": "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "PortScan": "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Bot": "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Infiltration": "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "WebAttacks": "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
}
MODELS = ("RandomForest", "ExtraTrees", "HistGradientBoosting", "LogisticRegression", "SGDLogistic")
LEDGER_FIELDS = (
    "experiment_id",
    "phase",
    "run_id",
    "dataset",
    "scenario",
    "seed",
    "model",
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
)
ALLOWED_STATUSES = {"PLANNED", "RUNNING", "COMPLETED", "FAILED", "SKIPPED", "INVALIDATED"}
_RANDOM_POOL_CACHE: tuple[pd.DataFrame, pd.Series, dict[str, object]] | None = None


@dataclass(frozen=True)
class RunPlan:
    experiment_id: str
    phase: int
    experiment: str
    dataset: str
    scenario: str
    seed: int
    model: str
    split: str

    @property
    def raw_path(self) -> Path:
        return FINAL_DATA / f"phase_{self.phase}" / f"{self.experiment_id}.json"

    @property
    def summary_path(self) -> Path:
        if self.phase == 1 and self.split == "random_stratified":
            return FINAL_DATA / "cicids_random_multiseed_summary.csv"
        if self.phase == 1:
            return FINAL_DATA / "cicids_holdout_multiseed_summary.csv"
        if self.phase == 2:
            return FINAL_DATA / "cicids_model_multiseed_summary.csv"
        return FINAL_DATA / f"phase_{self.phase}_summary.csv"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, check=False, capture_output=True, text=True
    )
    return completed.stdout.strip() if completed.returncode == 0 else "INFORMATION À VÉRIFIER."


def ensure_directories() -> None:
    for path in (FINAL_DATA, STATE, CONFIGS, TABLES, FIGURES, LOGS):
        path.mkdir(parents=True, exist_ok=True)


def read_latest_ledger() -> dict[str, dict[str, str]]:
    if not LEDGER.exists() or LEDGER.stat().st_size == 0:
        return {}
    latest: dict[str, dict[str, str]] = {}
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("experiment_id"):
                latest[row["experiment_id"]] = row
    return latest


def append_ledger(plan: RunPlan, status: str, **updates: object) -> None:
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"Unsupported ledger status: {status}")
    ensure_directories()
    write_header = not LEDGER.exists() or LEDGER.stat().st_size == 0
    row: dict[str, object] = {
        "experiment_id": plan.experiment_id,
        "phase": plan.phase,
        "run_id": plan.experiment_id,
        "dataset": plan.dataset,
        "scenario": plan.scenario,
        "seed": plan.seed,
        "model": plan.model,
        "status": status,
        "started_at": "",
        "completed_at": "",
        "command": subprocess.list2cmdline(sys.argv),
        "config_path": rel(CICIDS_CONFIG),
        "raw_result_path": rel(plan.raw_path),
        "summary_path": "",
        "figure_path": "",
        "error_path": "",
        "git_commit": git_commit(),
        "notes": "",
    }
    row.update(updates)
    with LEDGER.open("a", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS)
        if write_header:
            writer.writeheader()
        writer.writerow({key: row.get(key, "") for key in LEDGER_FIELDS})


def artifact_valid(plan: RunPlan) -> tuple[bool, str]:
    path = plan.raw_path
    if not path.exists() or path.stat().st_size == 0:
        return False, "artifact missing or empty"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"unreadable JSON: {exc}"
    required = {"experiment_id", "run_id", "dataset", "scenario", "seed", "model", "configuration", "metrics"}
    missing = required.difference(payload)
    if missing:
        return False, f"missing keys: {sorted(missing)}"
    if payload["experiment_id"] != plan.experiment_id or int(payload["seed"]) != plan.seed:
        return False, "identity mismatch"
    metrics = payload.get("metrics", {})
    expected_metrics = {"accuracy", "precision", "recall", "f1", "pr_auc", "mcc", "fpr", "tn", "fp", "fn", "tp"}
    if not expected_metrics.issubset(metrics):
        return False, f"missing metrics: {sorted(expected_metrics.difference(metrics))}"
    return True, "ok"


def atomic_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def build_plans() -> list[RunPlan]:
    plans: list[RunPlan] = []
    for scenario in SCENARIO_FILES:
        slug = scenario.lower().replace(" ", "_")
        for seed in SEEDS:
            plans.append(
                RunPlan(
                    experiment_id=f"e1_holdout_{slug}_seed{seed}",
                    phase=1,
                    experiment="cicids_holdout_multiseed",
                    dataset="CICIDS2017",
                    scenario=scenario,
                    seed=seed,
                    model="RandomForest",
                    split="file_or_scenario_holdout",
                )
            )
    for seed in SEEDS:
        plans.append(
            RunPlan(
                experiment_id=f"e1_random_stratified_seed{seed}",
                phase=1,
                experiment="cicids_random_multiseed",
                dataset="CICIDS2017",
                scenario="RandomStratified",
                seed=seed,
                model="RandomForest",
                split="random_stratified",
            )
        )
    for scenario in SCENARIO_FILES:
        slug = scenario.lower().replace(" ", "_")
        for seed in SEEDS:
            for model in MODELS:
                plans.append(
                    RunPlan(
                        experiment_id=f"e2_models_{slug}_seed{seed}_{model.lower()}",
                        phase=2,
                        experiment="cicids_model_multiseed",
                        dataset="CICIDS2017",
                        scenario=scenario,
                        seed=seed,
                        model=model,
                        split="file_or_scenario_holdout",
                    )
                )
    return plans


def matching_phase1_random_forest(plan: RunPlan) -> RunPlan | None:
    if plan.phase != 2 or plan.model != "RandomForest":
        return None
    for candidate in build_plans():
        if (
            candidate.phase == 1
            and candidate.experiment == "cicids_holdout_multiseed"
            and candidate.scenario == plan.scenario
            and candidate.seed == plan.seed
            and candidate.model == "RandomForest"
        ):
            return candidate
    return None


def select_plans(args: argparse.Namespace) -> list[RunPlan]:
    plans = build_plans()
    if args.phase is not None:
        plans = [plan for plan in plans if plan.phase == args.phase]
    if args.experiment:
        plans = [plan for plan in plans if plan.experiment == args.experiment]
    if args.scenario:
        plans = [plan for plan in plans if plan.scenario.lower() == args.scenario.lower()]
    if args.model:
        plans = [plan for plan in plans if plan.model.lower() == args.model.lower()]
    if args.seed is not None:
        plans = [plan for plan in plans if plan.seed == args.seed]
    return plans


def cicids_files() -> list[Path]:
    config = json.loads(CICIDS_CONFIG.read_text(encoding="utf-8"))
    directory = ROOT / config["input_directory"]
    files = sorted(directory.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CICIDS CSV files in {directory}")
    configured = set(SCENARIO_FILES.values())
    absent = configured.difference(path.name for path in files)
    if absent:
        raise FileNotFoundError(f"Configured CICIDS scenarios missing: {sorted(absent)}")
    return files


def load_holdout(plan: RunPlan) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, dict[str, object]]:
    files = cicids_files()
    feature_columns = _network_feature_columns(files[0])
    heldout = next(path for path in files if path.name == SCENARIO_FILES[plan.scenario])
    train_files = [path for path in files if path != heldout]
    x_train, y_train, train_labels = collect_network_sample(
        train_files,
        feature_columns,
        max_negative=8000,
        max_positive=8000,
        chunksize=100000,
        max_chunks_per_file=2,
        seed=plan.seed,
    )
    x_test, y_test, test_labels = collect_network_sample(
        [heldout],
        feature_columns,
        max_negative=4000,
        max_positive=4000,
        chunksize=100000,
        max_chunks_per_file=2,
        seed=plan.seed,
    )
    details = {
        "heldout_file": rel(heldout),
        "training_files": [rel(path) for path in train_files],
        "train_source_label_counts_before_caps": train_labels,
        "test_source_label_counts_before_caps": test_labels,
    }
    return x_train, y_train, x_test, y_test, details


def load_random_control(plan: RunPlan) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, dict[str, object]]:
    global _RANDOM_POOL_CACHE
    if _RANDOM_POOL_CACHE is None:
        files = cicids_files()
        feature_columns = _network_feature_columns(files[0])
        x_parts: list[pd.DataFrame] = []
        y_parts: list[pd.Series] = []
        source_counts: dict[str, dict[str, int]] = {}
        for file_index, path in enumerate(files):
            x_part, y_part, labels = collect_network_sample(
                [path],
                feature_columns,
                max_negative=12000,
                max_positive=12000,
                chunksize=100000,
                max_chunks_per_file=2,
                seed=2026 + file_index,
            )
            x_parts.append(x_part.reset_index(drop=True))
            y_parts.append(y_part.reset_index(drop=True))
            source_counts[path.name] = labels
        x_pool = pd.concat(x_parts, ignore_index=True)
        y_pool = pd.concat(y_parts, ignore_index=True)
        negative_indices = y_pool[y_pool == 0].sample(n=12000, random_state=2026).index
        positive_indices = y_pool[y_pool == 1].sample(n=12000, random_state=2026).index
        pool_indices = negative_indices.append(positive_indices)
        x_pool = x_pool.loc[pool_indices].reset_index(drop=True)
        y_pool = y_pool.loc[pool_indices].reset_index(drop=True)
        pool_details: dict[str, object] = {
            "source_files": [rel(path) for path in files],
            "source_label_counts_before_caps": source_counts,
            "pool_seed": 2026,
            "pool_rows": int(len(y_pool)),
            "pool_positive_rate": float(y_pool.mean()),
        }
        _RANDOM_POOL_CACHE = x_pool, y_pool, pool_details
    x_pool, y_pool, cached_details = _RANDOM_POOL_CACHE
    x_train, x_test, y_train, y_test = train_test_split(
        x_pool,
        y_pool,
        train_size=16000,
        test_size=8000,
        stratify=y_pool,
        random_state=plan.seed,
    )
    details = dict(cached_details)
    return x_train, y_train, x_test, y_test, details


def compute_metrics(y_test: pd.Series, y_pred: np.ndarray, y_score: np.ndarray) -> dict[str, float | int]:
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    denominator = fp + tn
    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "pr_auc": float(average_precision_score(y_test, y_score)) if y_test.nunique() > 1 else math.nan,
        "mcc": float(matthews_corrcoef(y_test, y_pred)),
        "fpr": float(fp / denominator) if denominator else math.nan,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def execute_cicids(plan: RunPlan, data: tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series, dict[str, object]]) -> dict[str, object]:
    x_train, y_train, x_test, y_test, details = data
    models = _candidate_models(plan.seed)
    model = models[plan.model]
    train_started = time.perf_counter()
    model.fit(x_train, y_train)
    train_time = time.perf_counter() - train_started
    test_started = time.perf_counter()
    y_pred = np.asarray(model.predict(x_test), dtype=int)
    y_score = _score(model, x_test)
    test_time = time.perf_counter() - test_started
    metrics = compute_metrics(y_test, y_pred, y_score)
    metrics["train_time_sec"] = float(train_time)
    metrics["test_time_sec"] = float(test_time)
    return {
        "schema_version": 1,
        "experiment_id": plan.experiment_id,
        "run_id": plan.experiment_id,
        "phase": plan.phase,
        "experiment": plan.experiment,
        "dataset": plan.dataset,
        "scenario": plan.scenario,
        "seed": plan.seed,
        "model": plan.model,
        "split": plan.split,
        "generated_at": utc_now(),
        "git_commit": git_commit(),
        "configuration": {
            "protocol_path": rel(CICIDS_CONFIG),
            "feature_count": int(x_train.shape[1]),
            "train_rows": int(len(y_train)),
            "test_rows": int(len(y_test)),
            "train_positive_rate": float(y_train.mean()),
            "test_positive_rate": float(y_test.mean()),
            **details,
        },
        "metrics": metrics,
    }


def reuse_phase1_random_forest(plan: RunPlan, source: RunPlan) -> dict[str, object]:
    valid, reason = artifact_valid(source)
    if not valid:
        raise ValueError(f"Cannot reuse {source.experiment_id}: {reason}")
    payload = json.loads(source.raw_path.read_text(encoding="utf-8"))
    payload.update(
        {
            "experiment_id": plan.experiment_id,
            "run_id": plan.experiment_id,
            "phase": plan.phase,
            "experiment": plan.experiment,
            "generated_at": utc_now(),
            "git_commit": git_commit(),
            "execution_kind": "REUSED_IDENTICAL_PHASE1_RESULT",
            "reused_from": {
                "experiment_id": source.experiment_id,
                "artifact_path": rel(source.raw_path),
                "reason": "Same dataset, scenario, seed, representation, sampling caps and RandomForest hyperparameters.",
            },
        }
    )
    configuration = dict(payload.get("configuration", {}))
    configuration["reused_without_refit"] = True
    configuration["source_protocol_path"] = configuration.get("protocol_path", rel(CICIDS_CONFIG))
    payload["configuration"] = configuration
    return payload


def flatten_artifacts(phase: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    directory = FINAL_DATA / f"phase_{phase}"
    for path in sorted(directory.glob("*.json")) if directory.exists() else []:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        configuration = payload.get("configuration", {})
        metrics = payload.get("metrics", {})
        rows.append(
            {
                "experiment_id": payload.get("experiment_id"),
                "run_id": payload.get("run_id"),
                "dataset": payload.get("dataset"),
                "scenario": payload.get("scenario"),
                "seed": payload.get("seed"),
                "model": payload.get("model"),
                "split": payload.get("split"),
                "feature_count": configuration.get("feature_count"),
                "train_rows": configuration.get("train_rows"),
                "test_rows": configuration.get("test_rows"),
                "train_positive_rate": configuration.get("train_positive_rate"),
                "test_positive_rate": configuration.get("test_positive_rate"),
                **metrics,
                "artifact_path": rel(path),
            }
        )
    return pd.DataFrame(rows)


def confidence_half_width(values: pd.Series) -> float:
    clean = pd.to_numeric(values, errors="coerce").dropna()
    if len(clean) < 2:
        return math.nan
    return float(student_t.ppf(0.975, len(clean) - 1) * clean.std(ddof=1) / math.sqrt(len(clean)))


def aggregate(frame: pd.DataFrame, groups: list[str]) -> pd.DataFrame:
    if frame.empty:
        return frame
    records: list[dict[str, object]] = []
    for keys, group in frame.groupby(groups, dropna=False):
        key_values = keys if isinstance(keys, tuple) else (keys,)
        record = dict(zip(groups, key_values))
        record.update(
            {
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
                "fp_mean": float(group["fp"].mean()),
                "fn_mean": float(group["fn"].mean()),
                "train_time_sec_mean": float(group["train_time_sec"].mean()),
                "test_time_sec_mean": float(group["test_time_sec"].mean()),
            }
        )
        records.append(record)
    return pd.DataFrame(records)


def _write_heatmap(frame: pd.DataFrame, metric: str, title: str, output_name: str) -> Path:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    scenarios = list(SCENARIO_FILES)
    matrix = frame.pivot(index="scenario", columns="seed", values=metric).reindex(index=scenarios, columns=SEEDS)
    values = matrix.to_numpy(dtype=float)
    fig, axis = plt.subplots(figsize=(8.8, 4.8))
    image = axis.imshow(values, aspect="auto", cmap="viridis", vmin=np.nanmin(values), vmax=np.nanmax(values))
    axis.set_xticks(range(len(SEEDS)), labels=[str(seed) for seed in SEEDS])
    axis.set_yticks(range(len(scenarios)), labels=scenarios)
    axis.set_xlabel("Seed")
    axis.set_ylabel("Scénario tenu hors entraînement")
    axis.set_title(title)
    for row_index in range(values.shape[0]):
        for column_index in range(values.shape[1]):
            value = values[row_index, column_index]
            axis.text(column_index, row_index, f"{value:.3f}", ha="center", va="center", color="white" if value < np.nanmean(values) else "black", fontsize=8)
    fig.colorbar(image, ax=axis, label=metric.upper().replace("PR_AUC", "PR-AUC"))
    fig.tight_layout()
    output = FIGURES / output_name
    fig.savefig(output, dpi=180)
    plt.close(fig)
    return output


def write_phase1_assets(holdout: pd.DataFrame, random: pd.DataFrame) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    outputs: list[Path] = []
    scenarios = list(SCENARIO_FILES)
    values = [holdout.loc[holdout["scenario"] == scenario, "f1"].to_numpy() for scenario in scenarios]
    fig, axis = plt.subplots(figsize=(9.2, 5.2))
    axis.boxplot(values, tick_labels=scenarios, showmeans=True)
    axis.set_ylabel("F1")
    axis.set_xlabel("Scénario tenu hors entraînement")
    axis.set_ylim(-0.03, 1.03)
    axis.set_title("CICIDS2017 — F1 par scénario holdout\nRandomForest, 5 seeds/scénario, N=25 runs")
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output = FIGURES / "cicids_f1_par_scenario_boxplot.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    outputs.append(output)

    fig, axis = plt.subplots(figsize=(7.8, 5.2))
    comparison = [holdout["f1"].to_numpy(), random["f1"].to_numpy()]
    axis.boxplot(comparison, tick_labels=["Holdout scénario\nN=25", "Split aléatoire stratifié\nN=5"], showmeans=True)
    for position, series in enumerate(comparison, start=1):
        offsets = np.linspace(-0.08, 0.08, len(series))
        axis.scatter(np.full(len(series), position) + offsets, series, s=22, alpha=0.75)
    axis.set_ylabel("F1")
    axis.set_ylim(-0.03, 1.03)
    axis.set_title("CICIDS2017 — Split aléatoire vs scénarios tenus hors entraînement\nRandomForest, même représentation et plafonds comparables")
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output = FIGURES / "cicids_random_vs_holdout_f1.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    outputs.append(output)

    outputs.append(
        _write_heatmap(
            holdout,
            "f1",
            "CICIDS2017 — F1 scénario × seed\nRandomForest, holdout complet, N=25 runs",
            "cicids_f1_scenario_seed_heatmap.png",
        )
    )
    outputs.append(
        _write_heatmap(
            holdout,
            "pr_auc",
            "CICIDS2017 — PR-AUC scénario × seed\nRandomForest, holdout complet, N=25 runs",
            "cicids_prauc_scenario_seed_heatmap.png",
        )
    )
    outputs.append(
        _write_heatmap(
            holdout,
            "mcc",
            "CICIDS2017 — MCC scénario × seed\nRandomForest, holdout complet, N=25 runs",
            "cicids_mcc_scenario_seed_heatmap.png",
        )
    )

    holdout_summary = aggregate(holdout, ["dataset", "scenario", "model", "split"])
    random_summary = aggregate(random, ["dataset", "model", "split"])
    lines = [
        "# CICIDS2017 — PHASE 1",
        "",
        "| Protocole | Scénario | N | Seeds | F1 moyen | Écart-type | PR-AUC | MCC | FPR | Limite |",
        "| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for _, row in holdout_summary.iterrows():
        limitation = "32 positifs/run" if row["scenario"] == "Infiltration" else "Sous-échantillon plafonné fixe"
        lines.append(
            f"| Holdout fichier/scénario | {row['scenario']} | {int(row['n'])} | {row['seeds']} | {row['f1_mean']:.6f} | {row['f1_std']:.6f} | {row['pr_auc_mean']:.6f} | {row['mcc_mean']:.6f} | {row['fpr_mean']:.6f} | {limitation} |"
        )
    for _, row in random_summary.iterrows():
        lines.append(
            f"| Split aléatoire stratifié | Tous scénarios, pool fixe | {int(row['n'])} | {row['seeds']} | {row['f1_mean']:.6f} | {row['f1_std']:.6f} | {row['pr_auc_mean']:.6f} | {row['mcc_mean']:.6f} | {row['fpr_mean']:.6f} | Mélange aléatoire des captures |"
        )
    table_output = TABLES / "cicids_phase1_results.md"
    table_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    outputs.append(table_output)
    return outputs


def write_phase2_assets(frame: pd.DataFrame) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    outputs: list[Path] = []
    scenarios = list(SCENARIO_FILES)
    models = list(_candidate_models(seed=SEEDS[0]))
    scenario_summary = aggregate(frame, ["dataset", "scenario", "model", "split"])
    scenario_summary.to_csv(
        FINAL_DATA / "cicids_model_scenario_summary.csv", index=False, encoding="utf-8-sig"
    )

    def heatmap(metric: str, label: str, output_name: str) -> Path:
        matrix = (
            scenario_summary.pivot(index="model", columns="scenario", values=metric)
            .reindex(index=models, columns=scenarios)
        )
        values = matrix.to_numpy(dtype=float)
        fig, axis = plt.subplots(figsize=(10.2, 5.4))
        image = axis.imshow(values, aspect="auto", cmap="viridis", vmin=np.nanmin(values), vmax=np.nanmax(values))
        axis.set_xticks(range(len(scenarios)), labels=scenarios)
        axis.set_yticks(range(len(models)), labels=models)
        axis.set_xlabel("Scénario tenu hors entraînement")
        axis.set_ylabel("Modèle")
        axis.set_title(f"CICIDS2017 — {label} moyen par modèle et scénario\n5 seeds par cellule, N=125 résultats")
        threshold = float(np.nanmean(values))
        for row_index in range(values.shape[0]):
            for column_index in range(values.shape[1]):
                value = values[row_index, column_index]
                axis.text(
                    column_index,
                    row_index,
                    f"{value:.3f}",
                    ha="center",
                    va="center",
                    color="white" if value < threshold else "black",
                    fontsize=8,
                )
        fig.colorbar(image, ax=axis, label=label)
        fig.tight_layout()
        output = FIGURES / output_name
        fig.savefig(output, dpi=180)
        plt.close(fig)
        return output

    outputs.append(heatmap("f1_mean", "F1", "cicids_modeles_scenarios_f1.png"))
    outputs.append(heatmap("pr_auc_mean", "PR-AUC", "cicids_modeles_scenarios_prauc.png"))
    outputs.append(heatmap("mcc_mean", "MCC", "cicids_modeles_scenarios_mcc.png"))

    model_summary = aggregate(frame, ["dataset", "model", "split"]).sort_values("f1_mean", ascending=False)
    fig, axis = plt.subplots(figsize=(8.8, 5.4))
    sizes = 70 + 850 * model_summary["pr_auc_mean"].clip(lower=0)
    axis.scatter(
        model_summary["train_time_sec_mean"],
        model_summary["f1_mean"],
        s=sizes,
        c=model_summary["fpr_mean"],
        cmap="magma_r",
        edgecolor="black",
        linewidth=0.6,
    )
    for _, row in model_summary.iterrows():
        axis.annotate(
            row["model"],
            (row["train_time_sec_mean"], row["f1_mean"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )
    axis.set_xlabel("Temps moyen d'entraînement par run (s)")
    axis.set_ylabel("F1 macro moyen")
    axis.set_title("CICIDS2017 — compromis performance/coût\nTaille = PR-AUC moyenne ; couleur = FPR moyen ; N=25 résultats/modèle")
    axis.grid(alpha=0.25)
    fig.tight_layout()
    output = FIGURES / "cicids_modeles_compromis_f1_temps.png"
    fig.savefig(output, dpi=180)
    plt.close(fig)
    outputs.append(output)

    lines = [
        "# CICIDS2017 — PHASE 2",
        "",
        "Chaque cellule agrège cinq seeds. Le test de chaque scénario est tenu hors entraînement.",
        "",
        "| Scénario | Modèle | N | F1 moyen | Écart-type | Précision | Rappel | PR-AUC | MCC | FPR | Entraînement (s) | Inférence (s) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in scenario_summary.sort_values(["scenario", "f1_mean"], ascending=[True, False]).iterrows():
        lines.append(
            f"| {row['scenario']} | {row['model']} | {int(row['n'])} | {row['f1_mean']:.6f} | {row['f1_std']:.6f} | {row['precision_mean']:.6f} | {row['recall_mean']:.6f} | {row['pr_auc_mean']:.6f} | {row['mcc_mean']:.6f} | {row['fpr_mean']:.6f} | {row['train_time_sec_mean']:.6f} | {row['test_time_sec_mean']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Agrégation macro sur les cinq scénarios",
            "",
            "| Modèle | N | F1 moyen | Écart-type | PR-AUC | MCC | FPR | Entraînement (s) | Inférence (s) |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for _, row in model_summary.iterrows():
        lines.append(
            f"| {row['model']} | {int(row['n'])} | {row['f1_mean']:.6f} | {row['f1_std']:.6f} | {row['pr_auc_mean']:.6f} | {row['mcc_mean']:.6f} | {row['fpr_mean']:.6f} | {row['train_time_sec_mean']:.6f} | {row['test_time_sec_mean']:.6f} |"
        )
    lines.extend(
        [
            "",
            "Les temps sont des durées murales mesurées par `time.perf_counter()` autour de `fit` et de la prédiction/scoring dans le runner. Les 25 temps RandomForest proviennent des runs strictement identiques de phase 1 réutilisés sans refit.",
            "",
            "Le F1 macro ne suffit pas à désigner un modèle dominant : les classements PR-AUC, MCC, FPR et coût diffèrent selon le scénario.",
        ]
    )
    table_output = TABLES / "cicids_phase2_model_comparison.md"
    table_output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    outputs.append(table_output)
    return outputs


def refresh_phase_outputs(phase: int) -> None:
    frame = flatten_artifacts(phase)
    if frame.empty:
        return
    FINAL_DATA.mkdir(parents=True, exist_ok=True)
    if phase == 1:
        holdout = frame[frame["split"] == "file_or_scenario_holdout"].copy()
        random = frame[frame["split"] == "random_stratified"].copy()
        holdout.to_csv(FINAL_DATA / "cicids_holdout_multiseed_raw.csv", index=False, encoding="utf-8-sig")
        random.to_csv(FINAL_DATA / "cicids_random_multiseed_raw.csv", index=False, encoding="utf-8-sig")
        aggregate(holdout, ["dataset", "scenario", "model", "split"]).to_csv(
            FINAL_DATA / "cicids_holdout_multiseed_summary.csv", index=False, encoding="utf-8-sig"
        )
        aggregate(random, ["dataset", "model", "split"]).to_csv(
            FINAL_DATA / "cicids_random_multiseed_summary.csv", index=False, encoding="utf-8-sig"
        )
        combined = pd.concat([holdout, random], ignore_index=True)
        aggregate(combined, ["dataset", "model", "split"]).to_csv(
            FINAL_DATA / "cicids_random_vs_holdout_summary.csv", index=False, encoding="utf-8-sig"
        )
        if len(holdout) == 25 and len(random) == 5:
            write_phase1_assets(holdout, random)
    elif phase == 2:
        frame.to_csv(FINAL_DATA / "cicids_model_multiseed_raw.csv", index=False, encoding="utf-8-sig")
        summary = aggregate(frame, ["dataset", "model", "split"]).sort_values("f1_mean", ascending=False)
        summary.to_csv(FINAL_DATA / "cicids_model_multiseed_summary.csv", index=False, encoding="utf-8-sig")
        summary.sort_values(["f1_mean", "pr_auc_mean", "mcc_mean"], ascending=[False, False, False]).to_csv(
            FINAL_DATA / "cicids_model_tradeoffs.csv", index=False, encoding="utf-8-sig"
        )
        if len(frame) == len(SCENARIO_FILES) * len(SEEDS) * len(_candidate_models(seed=SEEDS[0])):
            write_phase2_assets(frame)


def run_plans(plans: list[RunPlan], *, resume: bool) -> int:
    latest = read_latest_ledger()
    grouped: dict[tuple[str, int, str], list[RunPlan]] = {}
    for plan in plans:
        grouped.setdefault((plan.split, plan.seed, plan.scenario), []).append(plan)
    failures = 0
    for _, group in grouped.items():
        runnable: list[RunPlan] = []
        for plan in group:
            previous = latest.get(plan.experiment_id)
            if previous and previous.get("status") == "COMPLETED":
                valid, reason = artifact_valid(plan)
                if valid:
                    print(f"SKIPPED_ALREADY_COMPLETED {plan.experiment_id}")
                    continue
                append_ledger(plan, "INVALIDATED", completed_at=utc_now(), notes=reason)
            elif previous and previous.get("status") == "FAILED" and not resume:
                print(f"SKIPPED_FAILED_REQUIRES_RESUME {plan.experiment_id}")
                continue
            elif plan.raw_path.exists():
                valid, reason = artifact_valid(plan)
                if valid:
                    print(f"SKIPPED_EXISTING_UNREGISTERED {plan.experiment_id}")
                else:
                    print(f"SKIPPED_EXISTING_INVALID {plan.experiment_id}: {reason}")
                continue
            runnable.append(plan)
        if not runnable:
            continue
        remaining: list[RunPlan] = []
        for plan in runnable:
            source = matching_phase1_random_forest(plan)
            if source is None:
                remaining.append(plan)
                continue
            started_at = utc_now()
            append_ledger(plan, "PLANNED")
            append_ledger(plan, "RUNNING", started_at=started_at, notes=f"reuse_source={source.experiment_id}")
            try:
                payload = reuse_phase1_random_forest(plan, source)
                atomic_json(plan.raw_path, payload)
                valid, reason = artifact_valid(plan)
                if not valid:
                    raise ValueError(f"Reused artifact validation failed: {reason}")
                refresh_phase_outputs(plan.phase)
                append_ledger(
                    plan,
                    "COMPLETED",
                    started_at=started_at,
                    completed_at=utc_now(),
                    summary_path=rel(plan.summary_path),
                    notes=f"REUSED_IDENTICAL_PHASE1_RESULT source={source.experiment_id}",
                )
                print(f"COMPLETED_REUSED {plan.experiment_id} source={source.experiment_id}")
            except Exception as exc:
                error_path = LOGS / f"{plan.experiment_id}.error.txt"
                error_path.write_text(traceback.format_exc(), encoding="utf-8")
                append_ledger(
                    plan,
                    "FAILED",
                    started_at=started_at,
                    completed_at=utc_now(),
                    error_path=rel(error_path),
                    notes=str(exc),
                )
                failures += 1
        runnable = remaining
        if not runnable:
            continue
        try:
            data = load_random_control(runnable[0]) if runnable[0].split == "random_stratified" else load_holdout(runnable[0])
        except Exception as exc:
            for plan in runnable:
                error_path = LOGS / f"{plan.experiment_id}.error.txt"
                error_path.write_text(traceback.format_exc(), encoding="utf-8")
                append_ledger(plan, "FAILED", completed_at=utc_now(), error_path=rel(error_path), notes=str(exc))
                failures += 1
            continue
        for plan in runnable:
            started_at = utc_now()
            append_ledger(plan, "PLANNED")
            append_ledger(plan, "RUNNING", started_at=started_at)
            try:
                payload = execute_cicids(plan, data)
                atomic_json(plan.raw_path, payload)
                valid, reason = artifact_valid(plan)
                if not valid:
                    raise ValueError(f"Artifact validation failed: {reason}")
                refresh_phase_outputs(plan.phase)
                append_ledger(
                    plan,
                    "COMPLETED",
                    started_at=started_at,
                    completed_at=utc_now(),
                    summary_path=rel(plan.summary_path),
                )
                print(f"COMPLETED {plan.experiment_id} f1={payload['metrics']['f1']:.6f}")
            except Exception as exc:
                error_path = LOGS / f"{plan.experiment_id}.error.txt"
                error_path.write_text(traceback.format_exc(), encoding="utf-8")
                append_ledger(
                    plan,
                    "FAILED",
                    started_at=started_at,
                    completed_at=utc_now(),
                    error_path=rel(error_path),
                    notes=str(exc),
                )
                failures += 1
    return 1 if failures else 0


def installed_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return "INFORMATION À VÉRIFIER."


def freeze_environment() -> Path:
    freeze = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"], cwd=ROOT, check=False, capture_output=True, text=True
    )
    payload = {
        "generated_at_utc": utc_now(),
        "git_commit": git_commit(),
        "os": platform.platform(),
        "os_version": platform.version(),
        "python": sys.version,
        "python_executable": sys.executable,
        "virtual_environment": sys.prefix if sys.prefix != sys.base_prefix else "none",
        "cpu": platform.processor() or "INFORMATION À VÉRIFIER.",
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_processors": psutil.cpu_count(logical=True),
        "ram_bytes": psutil.virtual_memory().total,
        "gpu": "INFORMATION À VÉRIFIER.",
        "versions": {
            "scikit-learn": installed_version("scikit-learn"),
            "pandas": installed_version("pandas"),
            "numpy": installed_version("numpy"),
            "scipy": installed_version("scipy"),
            "drain3": installed_version("drain3"),
            "redis_python_client": installed_version("redis"),
            "redis_server": "INFORMATION À VÉRIFIER.",
            "psutil": installed_version("psutil"),
            "joblib": installed_version("joblib"),
        },
        "pip_freeze_status": freeze.returncode,
        "pip_freeze": freeze.stdout.splitlines() if freeze.returncode == 0 else ["INFORMATION À VÉRIFIER."],
    }
    output = FINAL_DOCS / "environment_final_experiments.json"
    atomic_json(output, payload)
    return output


def hash_and_lines(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    lines = 0
    final_byte = b""
    with path.open("rb") as handle:
        while chunk := handle.read(8 * 1024 * 1024):
            digest.update(chunk)
            lines += chunk.count(b"\n")
            final_byte = chunk[-1:]
    if path.stat().st_size and final_byte != b"\n":
        lines += 1
    return digest.hexdigest(), lines


def csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as handle:
        return [value.strip() for value in next(csv.reader(handle))]


def csv_classes(path: Path, label_column: str) -> list[str]:
    values: set[str] = set()
    target = label_column.strip().lower()
    selector = lambda column: str(column).strip().lower() == target
    for chunk in pd.read_csv(path, usecols=selector, dtype=str, chunksize=100000, encoding_errors="ignore"):
        if len(chunk.columns) != 1:
            raise ValueError(f"Label column {label_column!r} not uniquely resolved in {path}")
        selected = chunk.columns[0]
        values.update(chunk[selected].dropna().astype(str).str.strip().unique())
    return sorted(value for value in values if value)


def dataset_manifest() -> Path:
    cicids = cicids_files()
    hdfs_log = ROOT / "data/raw/Datasets/HDFS_1/HDFS.log"
    hdfs_labels = ROOT / "data/raw/Datasets/HDFS_1/anomaly_label.csv"
    bgl_log = ROOT / "data/raw/Datasets/BGL/BGL.log"
    specifications: list[tuple[str, Path, str, str, str, str]] = []
    specifications.extend(
        ("CICIDS2017", path, "CICIDS2017", "Label", "PHASE 1; PHASE 2", "csv") for path in cicids
    )
    specifications.extend(
        [
            ("HDFS", hdfs_labels, "HDFS_1", "Label", "PHASE 3", "csv"),
            ("HDFS", hdfs_log, "HDFS_1", "BlockId linked through anomaly_label.csv", "PHASE 3", "log"),
            ("BGL", bgl_log, "BGL", "First token in each raw line", "PHASE 3", "log"),
        ]
    )
    rows: list[dict[str, object]] = []
    hdfs_label_classes: list[str] | None = None
    for dataset, path, version, label_field, usage, kind in specifications:
        if not path.exists():
            rows.append(
                {
                    "dataset": dataset,
                    "source_file": rel(path),
                    "source_directory": rel(path.parent),
                    "source_officielle": "INFORMATION À VÉRIFIER.",
                    "version": version,
                    "sha256": "INFORMATION À VÉRIFIER.",
                    "nombre_lignes": "INFORMATION À VÉRIFIER.",
                    "nombre_colonnes": "INFORMATION À VÉRIFIER.",
                    "unite_observation": "log line" if kind == "log" else "flow/label row",
                    "labels": label_field,
                    "classes": "INFORMATION À VÉRIFIER.",
                    "date_fichier": "INFORMATION À VÉRIFIER.",
                    "usage_experimental": usage,
                    "remarque": "Fichier absent lors du gel de l'environnement.",
                }
            )
            continue
        sha256, line_count = hash_and_lines(path)
        columns = csv_header(path) if kind == "csv" else []
        classes: list[str] | str = "INFORMATION À VÉRIFIER."
        if dataset == "CICIDS2017":
            matching_label = next((column for column in columns if column.lower() == "label"), "")
            classes = csv_classes(path, matching_label) if matching_label else "INFORMATION À VÉRIFIER."
        elif path == hdfs_labels:
            matching_label = next((column for column in columns if column.lower() == "label"), "")
            hdfs_label_classes = csv_classes(path, matching_label) if matching_label else None
            classes = hdfs_label_classes or "INFORMATION À VÉRIFIER."
        elif path == hdfs_log and hdfs_label_classes:
            classes = hdfs_label_classes
        rows.append(
            {
                "dataset": dataset,
                "source_file": rel(path),
                "source_directory": rel(path.parent),
                "source_officielle": "INFORMATION À VÉRIFIER.",
                "version": version,
                "sha256": sha256,
                "nombre_lignes": line_count - 1 if kind == "csv" else line_count,
                "nombre_colonnes": len(columns) if kind == "csv" else 1,
                "unite_observation": "raw log line" if kind == "log" else ("network flow" if dataset == "CICIDS2017" else "block label"),
                "labels": label_field,
                "classes": json.dumps(classes, ensure_ascii=False) if isinstance(classes, list) else classes,
                "date_fichier": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
                "usage_experimental": usage,
                "remarque": "Provenance locale gelée; URL et checksum officiels non présents dans le dépôt.",
            }
        )
    output = FINAL_DOCS / "dataset_manifest_final.csv"
    pd.DataFrame(rows).to_csv(output, index=False, encoding="utf-8-sig")
    return output


def phase_zero(*, dry_run: bool) -> int:
    environment_path = FINAL_DOCS / "environment_final_experiments.json"
    manifest_path = FINAL_DOCS / "dataset_manifest_final.csv"
    if dry_run:
        print(f"WOULD_WRITE {rel(environment_path)}")
        print(f"WOULD_HASH_AND_WRITE {rel(manifest_path)}")
        return 0
    print(f"WROTE {rel(freeze_environment())}")
    print(f"WROTE {rel(dataset_manifest())}")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run final reproducible experiments with append-only checkpoints")
    parser.add_argument("--resume", action="store_true", help="Skip valid completed runs and retry failed runs")
    parser.add_argument("--phase", type=int, choices=range(0, 13))
    parser.add_argument("--experiment")
    parser.add_argument("--scenario")
    parser.add_argument("--model")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    ensure_directories()
    if args.phase == 0:
        return phase_zero(dry_run=args.dry_run)
    plans = select_plans(args)
    if not plans:
        print("NO_MATCHING_RUNS")
        return 0
    latest = read_latest_ledger()
    if args.dry_run:
        for plan in plans:
            previous = latest.get(plan.experiment_id, {}).get("status", "PLANNED")
            valid, _ = artifact_valid(plan)
            source = matching_phase1_random_forest(plan)
            source_valid = artifact_valid(source)[0] if source is not None else False
            if previous == "COMPLETED" and valid:
                action = "SKIPPED_ALREADY_COMPLETED"
            elif source_valid:
                action = "WOULD_REUSE_PHASE1"
            else:
                action = "WOULD_RUN"
            print(f"{action} {plan.experiment_id} phase={plan.phase} scenario={plan.scenario} seed={plan.seed} model={plan.model}")
        return 0
    return run_plans(plans, resume=args.resume)


if __name__ == "__main__":
    raise SystemExit(main())
