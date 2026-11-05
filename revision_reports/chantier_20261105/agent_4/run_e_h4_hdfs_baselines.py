"""E-H4: baselines simples au niveau bloc sur le test HDFS gelé.

Ce programme réutilise les cinq états Drain3 déjà ajustés par le protocole
HDFS principal. Il n'ajuste aucun parseur et ne choisit les seuils que sur la
validation complète. Les sorties sont limitées au dossier C13 de l'expérience.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence


ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments/phase_revision_20261105/E-H4-HDFS-BLOCK-BASELINES"
PROTOCOL = ROOT / "revision_reports/chantier_20261105/agent_4/protocoles/E-H4-HDFS-BLOCK-BASELINES.md"
SCRIPT = Path(__file__).resolve()
RAW = ROOT / "data/raw/Datasets/HDFS_1/HDFS.log"
LABELS = ROOT / "data/raw/Datasets/HDFS_1/anomaly_label.csv"
PARTITIONS = ROOT / "experiments/phase_dataset_strengthening/processed/ds_hdfs_block_20260910T081756Z__hdfs_full_block_partitions.txt.gz"
SOURCE_RESULT = ROOT / "experiments/phase_revision_20261104/agent_2_hdfs/agent2_hdfs_full_20261104T134240Z__result.json"
SEEDS = (42, 43, 44, 45, 46)
BLOCK_RE = re.compile(r"blk_-?\d+")
HDFS_RE = re.compile(
    r"^(?P<date>\d{6})\s+(?P<time>\d{6})\s+(?P<pid>\d+)\s+"
    r"(?P<severity>[A-Za-z]+)\s+(?P<source>[^:]+):\s*(?P<message>.*)$"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_labels() -> dict[str, int]:
    frame = pd.read_csv(LABELS, dtype=str, keep_default_na=False)
    frame.columns = [str(column).strip().lstrip("\ufeff") for column in frame.columns]
    block_col = next(column for column in frame.columns if column.lower() == "blockid")
    label_col = next(column for column in frame.columns if column.lower() == "label")
    return dict(
        zip(
            frame[block_col].astype(str),
            frame[label_col].astype(str).str.strip().str.lower().ne("normal").astype(int),
        )
    )


def load_partitions() -> dict[str, list[str]]:
    result = {"train": [], "validation": [], "test": []}
    with gzip.open(PARTITIONS, "rt", encoding="utf-8") as handle:
        for line in handle:
            split, block_id, _label = line.rstrip("\n").split("\t")
            result[split].append(block_id)
    return result


def stratified_sample(blocks: list[str], labels: dict[str, int], target: int, seed: int) -> list[str]:
    rng = np.random.default_rng(seed)
    by_label = {value: [block for block in blocks if labels[block] == value] for value in (0, 1)}
    positive_target = int(round(target * len(by_label[1]) / len(blocks)))
    negative_target = target - positive_target
    chosen = []
    for value, count in ((0, negative_target), (1, positive_target)):
        chosen.extend(rng.choice(np.asarray(by_label[value], dtype=object), size=count, replace=False).tolist())
    order = {block: index for index, block in enumerate(blocks)}
    return sorted(chosen, key=order.__getitem__)


def configured_miner(state_path: Path) -> TemplateMiner:
    scripts = ROOT / "scripts"
    import sys

    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from run_hdfs_block_strengthening import drain_config

    protocol = {"drain3": {"sim_th": 0.4, "depth": 4, "max_children": 100}}
    return TemplateMiner(persistence_handler=FilePersistence(str(state_path)), config=drain_config(protocol))


def binary_metrics(truth: np.ndarray, prediction: np.ndarray) -> dict[str, float | int]:
    truth = truth.astype(int)
    prediction = prediction.astype(int)
    tp = int(np.sum((truth == 1) & (prediction == 1)))
    fp = int(np.sum((truth == 0) & (prediction == 1)))
    tn = int(np.sum((truth == 0) & (prediction == 0)))
    fn = int(np.sum((truth == 1) & (prediction == 0)))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "n": int(len(truth)), "precision": precision, "recall": recall, "f1": f1,
        "fpr": fpr, "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


def select_threshold(truth: np.ndarray, scores: np.ndarray) -> tuple[float, dict[str, float | int]]:
    candidates = np.unique(scores)
    best: tuple[float, float, float, dict[str, float | int]] | None = None
    for threshold in candidates:
        metrics = binary_metrics(truth, scores >= threshold)
        key = (float(metrics["f1"]), -float(metrics["fpr"]), float(threshold), metrics)
        if best is None or key[:3] > best[:3]:
            best = key
    assert best is not None
    return float(best[2]), best[3]


def main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    labels = load_labels()
    partitions = load_partitions()
    source = json.loads(SOURCE_RESULT.read_text(encoding="utf-8"))
    source_by_seed = {int(result["seed"]): result for result in source["per_seed"]}
    if set(source_by_seed) != set(SEEDS):
        raise AssertionError(f"Graines source inattendues: {sorted(source_by_seed)}")
    if any("test" not in result or "selected_block_threshold" not in result for result in source_by_seed.values()):
        raise AssertionError("Résultats HDFS source incomplets")
    expected = source["partition_counts"]
    observed = {name: len(values) for name, values in partitions.items()}
    if observed != expected:
        raise AssertionError(f"Partition inattendue: {observed} != {expected}")

    samples = {seed: set(stratified_sample(partitions["train"], labels, 6000, seed)) for seed in SEEDS}
    miners: dict[int, TemplateMiner] = {}
    state_hashes: dict[int, str] = {}
    for seed in SEEDS:
        state_path = ROOT / source["drain3"][str(seed)]["state_path"]
        observed_hash = sha256(state_path)
        expected_hash = source["drain3"][str(seed)]["state_sha256_after_inference"]
        if observed_hash != expected_hash:
            raise AssertionError(f"État Drain3 seed {seed} modifié")
        miners[seed] = configured_miner(state_path)
        state_hashes[seed] = observed_hash

    membership: dict[str, list[int]] = {}
    for seed, blocks in samples.items():
        for block in blocks:
            if labels[block] == 0:
                membership.setdefault(block, []).append(seed)
    train_selected = set(membership)
    template_counts = {seed: Counter() for seed in SEEDS}
    normal_event_counts = Counter()
    with RAW.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_number, line in enumerate(handle, start=1):
            blocks = [block for block in dict.fromkeys(BLOCK_RE.findall(line)) if block in train_selected]
            if not blocks:
                continue
            match = HDFS_RE.match(line.rstrip("\r\n"))
            if match is None:
                continue
            message = match.group("message").strip()
            for block in blocks:
                for seed in membership[block]:
                    cluster = miners[seed].match(message, full_search_strategy="always")
                    template_id = 0 if cluster is None else int(cluster.cluster_id)
                    template_counts[seed][template_id] += 1
                    normal_event_counts[seed] += 1
            if line_number % 2_000_000 == 0:
                print(f"train frequencies: line {line_number}", flush=True)

    block_index = {
        split: {block: index for index, block in enumerate(partitions[split])}
        for split in ("validation", "test")
    }
    selected_to_split = {
        block: split for split in ("validation", "test") for block in partitions[split]
    }
    selected = set(selected_to_split)
    counts = {split: np.zeros(len(partitions[split]), dtype=np.int64) for split in ("validation", "test")}
    unknown = {
        seed: {split: np.zeros(len(partitions[split]), dtype=np.int64) for split in ("validation", "test")}
        for seed in SEEDS
    }
    rarity_sum = {
        seed: {split: np.zeros(len(partitions[split]), dtype=np.float64) for split in ("validation", "test")}
        for seed in SEEDS
    }
    with RAW.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_number, line in enumerate(handle, start=1):
            blocks = [block for block in dict.fromkeys(BLOCK_RE.findall(line)) if block in selected]
            if not blocks:
                continue
            match = HDFS_RE.match(line.rstrip("\r\n"))
            if match is None:
                continue
            message = match.group("message").strip()
            values: dict[int, tuple[int, float]] = {}
            for seed in SEEDS:
                cluster = miners[seed].match(message, full_search_strategy="always")
                template_id = 0 if cluster is None else int(cluster.cluster_id)
                is_unknown = int(cluster is None)
                frequency = max(template_counts[seed].get(template_id, 0), 1)
                rarity = -math.log(frequency / max(normal_event_counts[seed], 1))
                values[seed] = (is_unknown, rarity)
            for block in blocks:
                split = selected_to_split[block]
                index = block_index[split][block]
                counts[split][index] += 1
                for seed, (is_unknown, rarity) in values.items():
                    unknown[seed][split][index] += is_unknown
                    rarity_sum[seed][split][index] += rarity
            if line_number % 1_000_000 == 0:
                print(f"validation/test: line {line_number}", flush=True)

    if any(np.any(values == 0) for values in counts.values()):
        raise AssertionError("Au moins un bloc d'évaluation n'a aucun événement")
    truth = {
        split: np.asarray([labels[block] for block in partitions[split]], dtype=np.int8)
        for split in ("validation", "test")
    }

    rows: list[dict[str, object]] = []
    for seed in SEEDS:
        fixed_all = binary_metrics(truth["test"], np.ones_like(truth["test"]))
        rows.append({"seed": seed, "baseline": "all_positive", "threshold": "fixed", **fixed_all})

        unknown_test = unknown[seed]["test"] > 0
        fixed_unknown = binary_metrics(truth["test"], unknown_test)
        rows.append({"seed": seed, "baseline": "any_unseen_template", "threshold": 1, **fixed_unknown})

        validation_score = rarity_sum[seed]["validation"] / counts["validation"]
        test_score = rarity_sum[seed]["test"] / counts["test"]
        threshold, validation_metrics = select_threshold(truth["validation"], validation_score)
        test_metrics = binary_metrics(truth["test"], test_score >= threshold)
        rows.append({
            "seed": seed,
            "baseline": "template_only_mean_surprisal",
            "threshold": threshold,
            "validation_f1": validation_metrics["f1"],
            **test_metrics,
        })

        source_seed = source_by_seed[seed]
        source_test = source_seed["test"]
        rows.append({
            "seed": seed,
            "baseline": "histogram_source_result",
            "threshold": source_seed["selected_block_threshold"],
            **{key: source_test[key] for key in ("n", "precision", "recall", "f1", "fpr", "tp", "fp", "tn", "fn")},
        })

    metrics_path = OUT / "metrics_by_seed.csv"
    frame = pd.DataFrame(rows)
    frame.to_csv(metrics_path, index=False, encoding="utf-8")
    means = frame.groupby("baseline")["f1"].mean().to_dict()
    best_simple_name = max((name for name in means if name != "histogram_source_result"), key=means.get)
    margin = float(means["histogram_source_result"] - means[best_simple_name])
    decision = margin >= 0.01
    summary = {
        "experiment_id": "E-H4-HDFS-BLOCK-BASELINES",
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "partition_counts": observed,
        "test_positive_blocks": int(truth["test"].sum()),
        "seeds": list(SEEDS),
        "mean_f1": means,
        "best_simple_baseline": best_simple_name,
        "histogram_minus_best_simple_f1": margin,
        "criterion_margin": 0.01,
        "criterion_met": decision,
        "interpretation_rule": "Histogram dépasse la meilleure baseline simple si la marge moyenne de F1 est au moins 0,01.",
        "state_sha256": state_hashes,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest_rows = []
    for role, path in [
        ("protocol", PROTOCOL), ("runner", SCRIPT), ("raw_hdfs", RAW), ("labels", LABELS),
        ("partitions", PARTITIONS), ("source_result", SOURCE_RESULT),
        ("artifact", metrics_path), ("artifact", summary_path),
    ]:
        manifest_rows.append({"role": role, "path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size})
    manifest_path = OUT / "MANIFEST_SHA256.csv"
    with manifest_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "path", "sha256", "bytes"])
        writer.writeheader()
        writer.writerows(manifest_rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
