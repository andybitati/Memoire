"""Réévaluation HDFS Histogram sur validation/test complets, cinq échantillons train.

Tous les artefacts sont écrits à côté de ce script. Le protocole reprend la
partition 60/20/20 par première occurrence déjà matérialisée par le run source
``ds_hdfs_block_20260910T081756Z``. Pour chaque graine, 6 000 blocs du train
sont échantillonnés de façon stratifiée; Drain3 est ajusté sur ces seuls blocs,
persisté puis rechargé. Validation et test utilisent uniquement ``match``.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
import sys
import time
from array import array
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence
from drain3.template_miner_config import TemplateMinerConfig
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dataset_strengthening_common import binary_metrics, select_threshold  # noqa: E402
from run_hdfs_block_strengthening import (  # noqa: E402
    BLOCK_RE,
    HDFS_RE,
    drain_config,
    load_labels,
    stratified_block_sample,
)


RAW = ROOT / "data/raw/Datasets/HDFS_1/HDFS.log"
LABELS = ROOT / "data/raw/Datasets/HDFS_1/anomaly_label.csv"
SOURCE_PARTITIONS = (
    ROOT
    / "experiments/phase_dataset_strengthening/processed/"
    / "ds_hdfs_block_20260910T081756Z__hdfs_full_block_partitions.txt.gz"
)
SOURCE_RUN = (
    ROOT
    / "experiments/phase_dataset_strengthening/raw/"
    / "ds_hdfs_block_20260910T081756Z__hdfs_block_result.json"
)
SEEDS = (42, 43, 44, 45, 46)
TRAIN_SAMPLE_SIZE = 6000
SPLITS = ("train", "validation", "test")
AGGREGATORS = ("maximum", "mean", "abnormal_ratio")


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_partitions() -> dict[str, list[str]]:
    partitions = {name: [] for name in SPLITS}
    with gzip.open(SOURCE_PARTITIONS, "rt", encoding="utf-8") as handle:
        for line in handle:
            split, block_id, _label = line.rstrip("\n").split("\t")
            partitions[split].append(block_id)
    return partitions


def configured_miner() -> TemplateMiner:
    protocol = {"drain3": {"sim_th": 0.4, "depth": 4, "max_children": 100}}
    return TemplateMiner(config=drain_config(protocol))


def event_score(
    template_id: int,
    source: str,
    severity: str,
    normal_count: int,
    template_counts: Counter[int],
    source_counts: Counter[str],
    severity_counts: Counter[str],
) -> float:
    probabilities = (
        max(template_counts.get(template_id, 0), 1) / max(normal_count, 1),
        max(source_counts.get(source, 0), 1) / max(normal_count, 1),
        max(severity_counts.get(severity, 0), 1) / max(normal_count, 1),
    )
    return float(sum(-math.log(value) for value in probabilities) / 3.0)


def parse_selected(line: str, selected: set[str]) -> tuple[list[str], str, str, str] | None:
    blocks = list(dict.fromkeys(block for block in BLOCK_RE.findall(line) if block in selected))
    if not blocks:
        return None
    match = HDFS_RE.match(line.rstrip("\r\n"))
    if match is None:
        return None
    groups = match.groupdict()
    return blocks, groups["source"].strip(), groups["severity"].upper(), groups["message"].strip()


def fit_miners(
    sample_sets: dict[int, set[str]],
) -> tuple[dict[int, TemplateMiner], dict[int, dict[str, Any]]]:
    miners = {seed: configured_miner() for seed in SEEDS}
    membership: dict[str, list[int]] = {}
    for seed, blocks in sample_sets.items():
        for block in blocks:
            membership.setdefault(block, []).append(seed)
    selected = set(membership)
    calls = Counter()
    with RAW.open("r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            parsed = parse_selected(line, selected)
            if parsed is None:
                continue
            blocks, _source, _severity, message = parsed
            for block in blocks:
                for seed in membership[block]:
                    miners[seed].add_log_message(message)
                    calls[seed] += 1
            if lineno % 2_000_000 == 0:
                print(f"fit: ligne {lineno}", flush=True)

    frozen: dict[int, TemplateMiner] = {}
    audit: dict[int, dict[str, Any]] = {}
    for seed, miner in miners.items():
        state_path = OUT / f"hdfs_seed{seed}_drain3_state.bin"
        miner.persistence_handler = FilePersistence(str(state_path))
        miner.save_state("train_complete")
        before = sha256_file(state_path)
        reloaded = TemplateMiner(
            persistence_handler=FilePersistence(str(state_path)),
            config=drain_config({"drain3": {"sim_th": 0.4, "depth": 4, "max_children": 100}}),
        )
        frozen[seed] = reloaded
        audit[seed] = {
            "state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
            "state_sha256_before_inference": before,
            "fit_events": int(calls[seed]),
            "cluster_count": len(reloaded.drain.clusters),
            "fit_partition": "sampled_train_only",
            "inference_method": "match_only",
            "inference_updates": 0,
        }
    return frozen, audit


def count_normal_train_events(
    miners: dict[int, TemplateMiner],
    sample_sets: dict[int, set[str]],
    labels: dict[str, int],
) -> dict[int, dict[str, Any]]:
    membership: dict[str, list[int]] = {}
    for seed, blocks in sample_sets.items():
        for block in blocks:
            if labels[block] == 0:
                membership.setdefault(block, []).append(seed)
    selected = set(membership)
    stats = {
        seed: {
            "normal_count": 0,
            "template": Counter(),
            "source": Counter(),
            "severity": Counter(),
        }
        for seed in SEEDS
    }
    with RAW.open("r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            parsed = parse_selected(line, selected)
            if parsed is None:
                continue
            blocks, source, severity, message = parsed
            for block in blocks:
                for seed in membership[block]:
                    cluster = miners[seed].match(message, full_search_strategy="always")
                    template_id = 0 if cluster is None else int(cluster.cluster_id)
                    seed_stats = stats[seed]
                    seed_stats["normal_count"] += 1
                    seed_stats["template"][template_id] += 1
                    seed_stats["source"][source] += 1
                    seed_stats["severity"][severity] += 1
            if lineno % 2_000_000 == 0:
                print(f"fréquences: ligne {lineno}", flush=True)
    return stats


def score_full_validation_test(
    miners: dict[int, TemplateMiner],
    stats: dict[int, dict[str, Any]],
    partitions: dict[str, list[str]],
    labels: dict[str, int],
) -> dict[str, Any]:
    block_index = {
        split: {block: index for index, block in enumerate(partitions[split])}
        for split in ("validation", "test")
    }
    selected_to_split = {
        block: split for split in ("validation", "test") for block in partitions[split]
    }
    selected = set(selected_to_split)
    counts = {
        split: np.zeros(len(partitions[split]), dtype=np.int64)
        for split in ("validation", "test")
    }
    sums = {
        seed: {
            split: np.zeros(len(partitions[split]), dtype=np.float64)
            for split in ("validation", "test")
        }
        for seed in SEEDS
    }
    maxima = {
        seed: {
            split: np.full(len(partitions[split]), -np.inf, dtype=np.float64)
            for split in ("validation", "test")
        }
        for seed in SEEDS
    }
    event_indices = {split: array("i") for split in ("validation", "test")}
    event_scores = {
        seed: {split: array("d") for split in ("validation", "test")}
        for seed in SEEDS
    }
    unparsed_selected = 0
    multi_selected = 0
    started = time.monotonic()
    with RAW.open("r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            raw_blocks = list(dict.fromkeys(block for block in BLOCK_RE.findall(line) if block in selected))
            if not raw_blocks:
                continue
            match = HDFS_RE.match(line.rstrip("\r\n"))
            if match is None:
                unparsed_selected += 1
                continue
            if len(raw_blocks) > 1:
                multi_selected += 1
            groups = match.groupdict()
            source = groups["source"].strip()
            severity = groups["severity"].upper()
            message = groups["message"].strip()
            seed_values: dict[int, float] = {}
            for seed in SEEDS:
                cluster = miners[seed].match(message, full_search_strategy="always")
                template_id = 0 if cluster is None else int(cluster.cluster_id)
                seed_stats = stats[seed]
                seed_values[seed] = event_score(
                    template_id,
                    source,
                    severity,
                    int(seed_stats["normal_count"]),
                    seed_stats["template"],
                    seed_stats["source"],
                    seed_stats["severity"],
                )
            for block in raw_blocks:
                split = selected_to_split[block]
                index = block_index[split][block]
                counts[split][index] += 1
                event_indices[split].append(index)
                for seed, value in seed_values.items():
                    sums[seed][split][index] += value
                    if value > maxima[seed][split][index]:
                        maxima[seed][split][index] = value
                    event_scores[seed][split].append(value)
            if lineno % 1_000_000 == 0:
                elapsed = time.monotonic() - started
                print(f"score: ligne {lineno}, {elapsed:.1f} s", flush=True)

    missing = {split: int(np.sum(counts[split] == 0)) for split in counts}
    if any(missing.values()):
        raise RuntimeError(f"Blocs sans événement dans l'évaluation complète: {missing}")
    return {
        "counts": counts,
        "sums": sums,
        "maxima": maxima,
        "event_indices": event_indices,
        "event_scores": event_scores,
        "diagnostics": {
            "unparsed_selected_lines": unparsed_selected,
            "multi_selected_block_lines": multi_selected,
            "missing_blocks": missing,
        },
    }


def evaluate_seed(
    seed: int,
    scored: dict[str, Any],
    partitions: dict[str, list[str]],
    labels: dict[str, int],
) -> dict[str, Any]:
    truth = {
        split: np.asarray([labels[block] for block in partitions[split]], dtype=np.int8)
        for split in ("validation", "test")
    }
    indices = {
        split: np.frombuffer(scored["event_indices"][split], dtype=np.int32)
        for split in ("validation", "test")
    }
    scores = {
        split: np.frombuffer(scored["event_scores"][seed][split], dtype=np.float64)
        for split in ("validation", "test")
    }
    event_truth_validation = truth["validation"][indices["validation"]]
    event_threshold, event_validation = select_threshold(event_truth_validation, scores["validation"])
    event_test = binary_metrics(
        truth["test"][indices["test"]], scores["test"], event_threshold
    )

    aggregates: dict[str, dict[str, np.ndarray]] = {
        split: {
            "maximum": scored["maxima"][seed][split],
            "mean": scored["sums"][seed][split] / scored["counts"][split],
            "abnormal_ratio": np.bincount(
                indices[split],
                weights=(scores[split] >= event_threshold).astype(np.float64),
                minlength=len(partitions[split]),
            )
            / scored["counts"][split],
        }
        for split in ("validation", "test")
    }
    candidates: list[tuple[float, float, float, float, str, dict[str, Any]]] = []
    aggregator_rows: list[dict[str, Any]] = []
    for aggregator in AGGREGATORS:
        threshold, validation = select_threshold(truth["validation"], aggregates["validation"][aggregator])
        test = binary_metrics(truth["test"], aggregates["test"][aggregator], threshold)
        row = {
            "aggregator": aggregator,
            "threshold": threshold,
            "validation": validation,
            "test": test,
        }
        aggregator_rows.append(row)
        candidates.append(
            (-float(validation["f1"]), float(validation["fpr"]), -float(validation["mcc"]), -threshold, aggregator, row)
        )
    winner = min(candidates)[-1]
    return {
        "seed": seed,
        "event_threshold": event_threshold,
        "event_validation": event_validation,
        "event_test": event_test,
        "aggregators": aggregator_rows,
        "selected_aggregator": winner["aggregator"],
        "selected_block_threshold": winner["threshold"],
        "validation": winner["validation"],
        "test": winner["test"],
    }


def confidence_interval(values: list[float]) -> dict[str, float]:
    array_values = np.asarray(values, dtype=float)
    mean = float(array_values.mean())
    standard_deviation = float(array_values.std(ddof=1))
    half = float(student_t.ppf(0.975, len(array_values) - 1) * standard_deviation / math.sqrt(len(array_values)))
    return {
        "n_seeds": len(values),
        "mean": mean,
        "standard_deviation": standard_deviation,
        "ci95_student_lower": mean - half,
        "ci95_student_upper": mean + half,
        "minimum": float(array_values.min()),
        "maximum": float(array_values.max()),
        "interval_definition": "IC bilatéral de Student à 95 % sur les cinq graines d'échantillonnage train",
    }


def write_csv_artifacts(results: list[dict[str, Any]], prevalence: list[dict[str, Any]], run_id: str) -> None:
    metrics_path = OUT / f"{run_id}__seed_metrics.csv"
    with metrics_path.open("w", encoding="utf-8", newline="") as handle:
        fieldnames = [
            "run_id", "seed", "aggregator", "event_threshold", "block_threshold",
            "validation_n", "validation_prevalence", "validation_f1",
            "test_n", "test_prevalence", "test_precision", "test_recall", "test_f1",
            "test_pr_auc", "test_mcc", "test_fpr", "test_tp", "test_fp", "test_tn", "test_fn",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            test = result["test"]
            validation = result["validation"]
            writer.writerow({
                "run_id": run_id,
                "seed": result["seed"],
                "aggregator": result["selected_aggregator"],
                "event_threshold": result["event_threshold"],
                "block_threshold": result["selected_block_threshold"],
                "validation_n": validation["n"],
                "validation_prevalence": validation["prevalence"],
                "validation_f1": validation["f1"],
                "test_n": test["n"],
                "test_prevalence": test["prevalence"],
                "test_precision": test["precision"],
                "test_recall": test["recall"],
                "test_f1": test["f1"],
                "test_pr_auc": test["pr_auc"],
                "test_mcc": test["mcc"],
                "test_fpr": test["fpr"],
                "test_tp": test["tp"],
                "test_fp": test["fp"],
                "test_tn": test["tn"],
                "test_fn": test["fn"],
            })

    prevalence_path = OUT / f"{run_id}__partition_prevalence.csv"
    with prevalence_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["run_id", "partition", "seed", "n_blocks", "positive_blocks", "prevalence"])
        writer.writeheader()
        for row in prevalence:
            writer.writerow({"run_id": run_id, **row})


def main() -> int:
    started_at = now_utc()
    run_id = "agent2_hdfs_full_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    labels = load_labels(LABELS)
    partitions = load_partitions()
    source_result = json.loads(SOURCE_RUN.read_text(encoding="utf-8"))
    expected = source_result["full_partition_counts"]
    observed = {split: len(partitions[split]) for split in SPLITS}
    if observed != expected:
        raise AssertionError(f"Partition source incohérente: {observed} != {expected}")

    samples = {
        seed: stratified_block_sample(partitions["train"], labels, TRAIN_SAMPLE_SIZE, seed)
        for seed in SEEDS
    }
    sample_sets = {seed: set(blocks) for seed, blocks in samples.items()}
    miners, drain_audit = fit_miners(sample_sets)
    stats = count_normal_train_events(miners, sample_sets, labels)
    scored = score_full_validation_test(miners, stats, partitions, labels)
    results = [evaluate_seed(seed, scored, partitions, labels) for seed in SEEDS]

    for seed, miner in miners.items():
        state_path = ROOT / drain_audit[seed]["state_path"]
        drain_audit[seed]["state_sha256_after_inference"] = sha256_file(state_path)
        drain_audit[seed]["state_unchanged"] = (
            drain_audit[seed]["state_sha256_before_inference"]
            == drain_audit[seed]["state_sha256_after_inference"]
        )
        drain_audit[seed]["cluster_count_after_inference"] = len(miner.drain.clusters)
        if not drain_audit[seed]["state_unchanged"]:
            raise AssertionError(f"État Drain3 modifié pendant l'inférence, seed={seed}")

    prevalence: list[dict[str, Any]] = []
    for split in SPLITS:
        values = [labels[block] for block in partitions[split]]
        prevalence.append({
            "partition": f"full_{split}", "seed": "",
            "n_blocks": len(values), "positive_blocks": int(sum(values)),
            "prevalence": float(np.mean(values)),
        })
    for seed, blocks in samples.items():
        values = [labels[block] for block in blocks]
        prevalence.append({
            "partition": "sampled_train", "seed": seed,
            "n_blocks": len(values), "positive_blocks": int(sum(values)),
            "prevalence": float(np.mean(values)),
        })

    intervals = {
        metric: confidence_interval([float(result["test"][metric]) for result in results])
        for metric in ("precision", "recall", "f1", "pr_auc", "mcc", "fpr")
    }
    write_csv_artifacts(results, prevalence, run_id)
    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "started_at": started_at,
        "completed_at": now_utc(),
        "protocol": {
            "source_partition_run_id": source_result["run_id"],
            "partition_unit": "block_id ordered by first raw-log occurrence",
            "split_ratios": [0.6, 0.2, 0.2],
            "train_sample_blocks_per_seed": TRAIN_SAMPLE_SIZE,
            "train_sample_seeds": list(SEEDS),
            "validation_blocks": "full 20% partition",
            "test_blocks": "full 20% partition",
            "drain3_fit": "sampled train only, one miner per seed",
            "drain3_inference": "persisted/reloaded state; match_only on validation/test",
            "threshold_selection": "validation only; maximize F1, then lower FPR, higher MCC, higher threshold",
            "block_aggregator_selection": "validation only among maximum, mean, abnormal_ratio",
            "test_use": "single final evaluation per seed after all choices",
        },
        "inputs": {
            "raw_path": str(RAW.relative_to(ROOT)).replace("\\", "/"),
            "raw_sha256": source_result["inputs"]["raw_sha256"],
            "raw_sha256_source": str(SOURCE_RUN.relative_to(ROOT)).replace("\\", "/"),
            "labels_path": str(LABELS.relative_to(ROOT)).replace("\\", "/"),
            "labels_sha256": sha256_file(LABELS),
            "partition_path": str(SOURCE_PARTITIONS.relative_to(ROOT)).replace("\\", "/"),
            "partition_sha256": sha256_file(SOURCE_PARTITIONS),
        },
        "partition_counts": observed,
        "prevalence": prevalence,
        "drain3": {str(seed): drain_audit[seed] for seed in SEEDS},
        "normal_train_event_counts": {str(seed): int(stats[seed]["normal_count"]) for seed in SEEDS},
        "diagnostics": scored["diagnostics"],
        "per_seed": results,
        "across_seed_intervals": intervals,
        "artifacts": [
            f"revision_reports/agent_2/{run_id}__seed_metrics.csv",
            f"revision_reports/agent_2/{run_id}__partition_prevalence.csv",
            f"revision_reports/agent_2/{run_id}__result.json",
        ],
    }
    output = OUT / f"{run_id}__result.json"
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    (OUT / "LATEST_RUN.txt").write_text(run_id + "\n", encoding="utf-8")
    print(json.dumps({"run_id": run_id, "result": str(output), "f1": intervals["f1"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
