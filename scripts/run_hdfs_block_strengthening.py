"""Évalue HDFS au niveau block_id avec Drain3 ajusté sur le train uniquement."""

from __future__ import annotations

import argparse
import gzip
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence
from drain3.template_miner_config import TemplateMinerConfig

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from dataset_strengthening_common import (  # noqa: E402
    CONFIG_PATH,
    PHASE_ROOT,
    append_ledger,
    binary_metrics,
    ensure_phase_dirs,
    git_commit,
    load_config,
    relative,
    run_id,
    select_threshold,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)


BLOCK_RE = re.compile(r"blk_-?\d+")
HDFS_RE = re.compile(
    r"^(?P<date>\d{6})\s+(?P<time>\d{6})\s+(?P<pid>\d+)\s+"
    r"(?P<severity>[A-Za-z]+)\s+(?P<source>[^:]+):\s*(?P<message>.*)$"
)
SPLITS = ("train", "validation", "test")


def load_labels(path: Path) -> dict[str, int]:
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    frame.columns = [str(column).strip().lstrip("\ufeff") for column in frame.columns]
    block_column = next(column for column in frame.columns if column.lower() == "blockid")
    label_column = next(column for column in frame.columns if column.lower() == "label")
    labels = frame[label_column].astype(str).str.strip().str.lower()
    return dict(zip(frame[block_column].astype(str), labels.ne("normal").astype(int)))


def scan_block_order(raw_path: Path, labels: dict[str, int]) -> tuple[list[str], int, int]:
    seen: set[str] = set()
    ordered: list[str] = []
    line_count = 0
    multi_block_lines = 0
    with raw_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for line_count, line in enumerate(handle, start=1):
            blocks = list(dict.fromkeys(BLOCK_RE.findall(line)))
            if len(blocks) > 1:
                multi_block_lines += 1
            for block_id in blocks:
                if block_id in labels and block_id not in seen:
                    seen.add(block_id)
                    ordered.append(block_id)
    return ordered, line_count, multi_block_lines


def make_full_splits(ordered: list[str], ratios: list[float]) -> dict[str, list[str]]:
    if len(ratios) != 3 or not math.isclose(sum(ratios), 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError("HDFS split ratios must contain three values summing to one")
    first = int(len(ordered) * ratios[0])
    second = int(len(ordered) * (ratios[0] + ratios[1]))
    splits = {
        "train": ordered[:first],
        "validation": ordered[first:second],
        "test": ordered[second:],
    }
    assert set(splits["train"]).isdisjoint(splits["validation"])
    assert set(splits["train"]).isdisjoint(splits["test"])
    assert set(splits["validation"]).isdisjoint(splits["test"])
    return splits


def stratified_block_sample(
    block_ids: list[str], labels: dict[str, int], target: int, seed: int
) -> list[str]:
    rng = np.random.default_rng(seed)
    by_label = {0: [block for block in block_ids if labels[block] == 0], 1: [block for block in block_ids if labels[block] == 1]}
    if target <= 0 or target >= len(block_ids):
        return list(block_ids)
    positive_target = int(round(target * len(by_label[1]) / max(len(block_ids), 1)))
    positive_target = min(len(by_label[1]), max(1 if by_label[1] else 0, positive_target))
    negative_target = min(len(by_label[0]), target - positive_target)
    if negative_target + positive_target < target:
        positive_target = min(len(by_label[1]), target - negative_target)
    selected = []
    for label, count in ((0, negative_target), (1, positive_target)):
        candidates = np.asarray(by_label[label], dtype=object)
        if count >= len(candidates):
            selected.extend(candidates.tolist())
        elif count:
            selected.extend(rng.choice(candidates, size=count, replace=False).tolist())
    position = {block_id: index for index, block_id in enumerate(block_ids)}
    return sorted(selected, key=position.__getitem__)


def collect_selected_events(
    raw_path: Path,
    labels: dict[str, int],
    selected_to_split: dict[str, str],
) -> tuple[dict[str, pd.DataFrame], dict[str, int]]:
    rows: dict[str, list[dict[str, Any]]] = {name: [] for name in SPLITS}
    diagnostics = {"cross_split_lines_skipped": 0, "multi_selected_block_lines": 0, "unparsed_selected_lines": 0}
    with raw_path.open("r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            selected = list(dict.fromkeys(block for block in BLOCK_RE.findall(line) if block in selected_to_split))
            if not selected:
                continue
            if len(selected) > 1:
                diagnostics["multi_selected_block_lines"] += 1
                partitions = {selected_to_split[block] for block in selected}
                if len(partitions) > 1:
                    diagnostics["cross_split_lines_skipped"] += 1
                    continue
            match = HDFS_RE.match(line.rstrip("\r\n"))
            if match is None:
                diagnostics["unparsed_selected_lines"] += 1
                continue
            groups = match.groupdict()
            for block_id in selected:
                split = selected_to_split[block_id]
                rows[split].append(
                    {
                        "source_lineno": lineno,
                        "block_id": block_id,
                        "label": labels[block_id],
                        "source": groups["source"].strip(),
                        "severity": groups["severity"].upper(),
                        "message": groups["message"].strip(),
                    }
                )
    frames = {name: pd.DataFrame(rows[name]) for name in SPLITS}
    for name, frame in frames.items():
        if frame.empty:
            raise RuntimeError(f"No HDFS events collected for {name}")
    return frames, diagnostics


def drain_config(protocol: dict[str, Any]) -> TemplateMinerConfig:
    values = protocol["drain3"]
    config = TemplateMinerConfig()
    config.profiling_enabled = False
    config.snapshot_interval_minutes = 0
    config.drain_sim_th = float(values["sim_th"])
    config.drain_depth = int(values["depth"])
    config.drain_max_children = int(values["max_children"])
    config.drain_max_clusters = None
    config.parametrize_numeric_tokens = True
    config.snapshot_compress_state = True
    return config


def fit_frozen_drain(
    train_messages: pd.Series, protocol: dict[str, Any], state_path: Path
) -> tuple[TemplateMiner, dict[str, Any]]:
    miner = TemplateMiner(config=drain_config(protocol))
    add_calls = 0
    for message in train_messages.fillna("").astype(str):
        miner.add_log_message(message)
        add_calls += 1
    state_path.parent.mkdir(parents=True, exist_ok=True)
    miner.persistence_handler = FilePersistence(str(state_path))
    miner.save_state("train_complete")
    state_hash = sha256_file(state_path)
    frozen = TemplateMiner(persistence_handler=FilePersistence(str(state_path)), config=drain_config(protocol))
    return frozen, {
        "add_log_message_calls": add_calls,
        "fit_partition": "train_only",
        "inference_method": "match_only",
        "state_sha256_before_inference": state_hash,
        "cluster_count_before_inference": len(frozen.drain.clusters),
    }


def assign_templates(miner: TemplateMiner, frame: pd.DataFrame) -> np.ndarray:
    identifiers: list[int] = []
    for message in frame["message"].fillna("").astype(str):
        cluster = miner.match(message, full_search_strategy="always")
        identifiers.append(0 if cluster is None else int(cluster.cluster_id))
    return np.asarray(identifiers, dtype=np.int32)


def histogram_scores(frames: dict[str, pd.DataFrame], template_ids: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    normal_mask = frames["train"]["label"].astype(int).to_numpy() == 0
    normal_count = max(int(normal_mask.sum()), 1)
    template_counts = Counter(template_ids["train"][normal_mask].tolist())
    source_counts = Counter(frames["train"].loc[normal_mask, "source"].astype(str))
    severity_counts = Counter(frames["train"].loc[normal_mask, "severity"].astype(str))
    output: dict[str, np.ndarray] = {}
    for split in SPLITS:
        values = []
        for template_id, source, severity in zip(
            template_ids[split], frames[split]["source"].astype(str), frames[split]["severity"].astype(str)
        ):
            probabilities = (
                max(template_counts.get(int(template_id), 0), 1) / normal_count,
                max(source_counts.get(source, 0), 1) / normal_count,
                max(severity_counts.get(severity, 0), 1) / normal_count,
            )
            values.append(float(sum(-math.log(value) for value in probabilities) / 3.0))
        output[split] = np.asarray(values, dtype=np.float64)
    return output


def aggregate_blocks(frame: pd.DataFrame, scores: np.ndarray, event_threshold: float) -> pd.DataFrame:
    work = frame[["block_id", "label"]].copy()
    work["event_score"] = scores
    work["event_abnormal"] = scores >= event_threshold
    grouped = work.groupby("block_id", sort=False)
    result = grouped.agg(
        label=("label", "first"),
        event_count=("event_score", "size"),
        maximum=("event_score", "max"),
        mean=("event_score", "mean"),
        abnormal_ratio=("event_abnormal", "mean"),
        label_variants=("label", "nunique"),
    ).reset_index()
    if int(result["label_variants"].max()) != 1:
        raise AssertionError("A block_id has inconsistent labels")
    return result.drop(columns="label_variants")


def evaluate_aggregators(blocks: dict[str, pd.DataFrame]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    candidates: list[tuple[float, float, float, float, str, dict[str, Any]]] = []
    for aggregator in ("maximum", "mean", "abnormal_ratio"):
        threshold, validation = select_threshold(
            blocks["validation"]["label"].to_numpy(), blocks["validation"][aggregator].to_numpy()
        )
        test = binary_metrics(blocks["test"]["label"].to_numpy(), blocks["test"][aggregator].to_numpy(), threshold)
        row = {
            "aggregator": aggregator,
            "threshold": threshold,
            **{f"validation_{key}": value for key, value in validation.items()},
            **{f"test_{key}": value for key, value in test.items()},
        }
        rows.append(row)
        candidates.append((-validation["f1"], validation["fpr"], -validation["mcc"], -threshold, aggregator, row))
    winner = min(candidates)[-1]
    return rows, winner


def make_figures(comparison: list[dict[str, Any]], aggregators: list[dict[str, Any]]) -> list[Path]:
    import matplotlib.pyplot as plt

    first = PHASE_ROOT / "figures" / "dataset_01_hdfs_event_vs_block.png"
    fig, axis = plt.subplots(figsize=(8.5, 5.2))
    labels = [row["evaluation"] for row in comparison]
    values = [float(row["f1"]) for row in comparison]
    bars = axis.bar(labels, values, color=["#4C78A8", "#F58518"])
    for bar, value in zip(bars, values):
        axis.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.4f}", ha="center")
    axis.set_ylim(0, min(1.08, max(values + [0.1]) + 0.15))
    axis.set_ylabel("F1 sur le test gelé")
    axis.set_title("HDFS — même split, unité événement vs unité block_id")
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(first, dpi=180)
    plt.close(fig)

    second = PHASE_ROOT / "figures" / "dataset_02_hdfs_block_aggregators.png"
    fig, axis = plt.subplots(figsize=(9, 5.2))
    names = [row["aggregator"] for row in aggregators]
    val = [float(row["validation_f1"]) for row in aggregators]
    test = [float(row["test_f1"]) for row in aggregators]
    x = np.arange(len(names))
    axis.bar(x - 0.18, val, width=0.36, label="Validation", color="#4C78A8")
    axis.bar(x + 0.18, test, width=0.36, label="Test gelé", color="#F58518")
    axis.set_xticks(x, names)
    axis.set_ylabel("F1")
    axis.set_title("HDFS — agrégateurs de scores événementiels au niveau bloc")
    axis.legend()
    axis.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(second, dpi=180)
    plt.close(fig)
    return [first, second]


def execute() -> dict[str, Any]:
    ensure_phase_dirs()
    config = load_config()
    protocol = config["hdfs_block"]
    identifier = run_id("ds_hdfs_block")
    experiment_id = "dataset_strengthening_hdfs_block"
    started = utc_now()
    raw_path = ROOT / protocol["raw"]
    labels_path = ROOT / protocol["labels"]
    append_ledger(
        experiment_id=experiment_id,
        phase=1,
        run_id=identifier,
        dataset="HDFS",
        protocol="block_level_first_occurrence_60_20_20",
        status="RUNNING",
        started_at=started,
        command="scripts/run_hdfs_block_strengthening.py",
    )
    try:
        labels = load_labels(labels_path)
        ordered, line_count, multi_block_lines = scan_block_order(raw_path, labels)
        full_splits = make_full_splits(ordered, list(protocol["split_ratios"]))
        selected = {
            split: stratified_block_sample(
                full_splits[split], labels, int(protocol["sample_blocks"][split]), int(protocol["sample_seed"]) + index
            )
            for index, split in enumerate(SPLITS)
        }
        selected_sets = {name: set(values) for name, values in selected.items()}
        assert selected_sets["train"].isdisjoint(selected_sets["validation"])
        assert selected_sets["train"].isdisjoint(selected_sets["test"])
        assert selected_sets["validation"].isdisjoint(selected_sets["test"])
        selected_to_split = {block: split for split in SPLITS for block in selected[split]}

        partition_path = PHASE_ROOT / "processed" / f"{identifier}__hdfs_full_block_partitions.txt.gz"
        with gzip.open(partition_path, "wt", encoding="utf-8", newline="\n") as handle:
            for split in SPLITS:
                for block_id in full_splits[split]:
                    handle.write(f"{split}\t{block_id}\t{labels[block_id]}\n")
        selected_rows = [
            {"block_id": block, "partition": split, "label": labels[block], "selection_seed": int(protocol["sample_seed"]) + index}
            for index, split in enumerate(SPLITS)
            for block in selected[split]
        ]
        selected_path = PHASE_ROOT / "processed" / f"{identifier}__hdfs_selected_blocks.csv"
        write_csv(selected_path, selected_rows)

        frames, diagnostics = collect_selected_events(raw_path, labels, selected_to_split)
        events_path = PHASE_ROOT / "raw" / f"{identifier}__hdfs_selected_events.csv.gz"
        pd.concat([frame.assign(partition=split) for split, frame in frames.items()], ignore_index=True).to_csv(
            events_path, index=False, encoding="utf-8", compression="gzip"
        )

        state_path = PHASE_ROOT / "processed" / f"{identifier}__hdfs_drain3_train_state.bin"
        miner, drain_audit = fit_frozen_drain(frames["train"]["message"], protocol, state_path)
        template_ids = {split: assign_templates(miner, frames[split]) for split in SPLITS}
        drain_audit.update(
            {
                "state_sha256_after_inference": sha256_file(state_path),
                "cluster_count_after_inference": len(miner.drain.clusters),
                "inference_updates": 0,
            }
        )
        if drain_audit["state_sha256_before_inference"] != drain_audit["state_sha256_after_inference"]:
            raise AssertionError("Drain3 persisted state changed during match-only inference")

        event_scores = histogram_scores(frames, template_ids)
        event_threshold, event_validation = select_threshold(frames["validation"]["label"].to_numpy(), event_scores["validation"])
        event_test = binary_metrics(frames["test"]["label"].to_numpy(), event_scores["test"], event_threshold)
        block_frames = {split: aggregate_blocks(frames[split], event_scores[split], event_threshold) for split in SPLITS}
        aggregator_rows, winner = evaluate_aggregators(block_frames)
        aggregate_path = PHASE_ROOT / "aggregated" / f"{identifier}__hdfs_block_aggregators.csv"
        write_csv(aggregate_path, aggregator_rows)
        comparison = [
            {"evaluation": "event_level_same_split", "unit": "event", **event_test},
            {
                "evaluation": f"block_level_{winner['aggregator']}",
                "unit": "block_id",
                **{key.removeprefix("test_"): value for key, value in winner.items() if key.startswith("test_")},
            },
        ]
        comparison_path = PHASE_ROOT / "aggregated" / f"{identifier}__hdfs_event_block_comparison.csv"
        write_csv(comparison_path, comparison)
        figures = make_figures(comparison, aggregator_rows)

        summary = {
            "schema_version": 1,
            "run_id": identifier,
            "generated_at": utc_now(),
            "git_commit": git_commit(),
            "protocol": protocol,
            "inputs": {
                "raw": relative(raw_path),
                "raw_sha256": sha256_file(raw_path),
                "labels": relative(labels_path),
                "labels_sha256": sha256_file(labels_path),
                "raw_lines": line_count,
                "labels_count": len(labels),
                "blocks_found": len(ordered),
                "labels_without_observed_block": len(set(labels) - set(ordered)),
            },
            "full_partition_counts": {split: len(full_splits[split]) for split in SPLITS},
            "selected_block_counts": {split: len(selected[split]) for split in SPLITS},
            "selected_event_counts": {split: len(frames[split]) for split in SPLITS},
            "selected_positive_blocks": {split: int(sum(labels[block] for block in selected[split])) for split in SPLITS},
            "assertions": {
                "train_val_disjoint": True,
                "train_test_disjoint": True,
                "val_test_disjoint": True,
                "selection_uses_test_for_threshold": False,
                "selection_uses_test_for_aggregator": False,
                "drain3_train_only": True,
            },
            "diagnostics": {**diagnostics, "multi_block_lines_in_full_source": multi_block_lines},
            "drain3": drain_audit,
            "event_level": {"threshold": event_threshold, "validation": event_validation, "test": event_test},
            "block_selection": {
                "selected_aggregator": winner["aggregator"],
                "selected_threshold": winner["threshold"],
                "validation_f1": winner["validation_f1"],
                "test_f1": winner["test_f1"],
            },
            "historical_reference": {
                "protocol": "strict_event_level_2026_phase_3",
                "f1": 0.269307,
                "equivalent_benchmark": False,
            },
            "artifacts": [relative(path) for path in [partition_path, selected_path, events_path, state_path, aggregate_path, comparison_path, *figures]],
        }
        raw_result = PHASE_ROOT / "raw" / f"{identifier}__hdfs_block_result.json"
        write_json(raw_result, summary)
        report_path = PHASE_ROOT / "reports" / "HDFS_BLOCK_LEVEL_ANALYSIS.md"
        report_path.write_text(
            "\n".join(
                [
                    "# HDFS — évaluation au niveau block_id",
                    "",
                    f"- Run : `{identifier}`",
                    f"- Blocs observés : `{len(ordered)}` ; partitions 60/20/20 : `{summary['full_partition_counts']}`.",
                    f"- Blocs sélectionnés : `{summary['selected_block_counts']}`.",
                    f"- Événements sélectionnés : `{summary['selected_event_counts']}`.",
                    "- Intersections train/validation/test : vides.",
                    f"- Drain3 : `{drain_audit['add_log_message_calls']}` appels train, `0` mise à jour validation/test.",
                    f"- Seuil événementiel choisi sur validation : `{event_threshold:.9f}`.",
                    f"- F1 événementiel sur ce test : `{event_test['f1']:.6f}`.",
                    f"- Agrégateur bloc retenu sur validation : `{winner['aggregator']}` ; seuil `{winner['threshold']:.9f}`.",
                    f"- F1 bloc sur test gelé : `{winner['test_f1']:.6f}`.",
                    "",
                    "L’ancien F1 événementiel `0,269307` reste un résultat d’un autre protocole. Il n’est pas traité comme un benchmark équivalent.",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        summary["artifacts"].append(relative(report_path))
        completed = utc_now()
        append_ledger(
            experiment_id=experiment_id,
            phase=1,
            run_id=identifier,
            dataset="HDFS",
            protocol="block_level_first_occurrence_60_20_20",
            status="COMPLETED",
            started_at=started,
            completed_at=completed,
            command="scripts/run_hdfs_block_strengthening.py",
            raw_result_path=relative(raw_result),
            summary_path=relative(report_path),
            figure_path=";".join(relative(path) for path in figures),
            notes=f"aggregator={winner['aggregator']}; test_f1={winner['test_f1']:.6f}",
        )
        return summary
    except Exception as exc:
        error_path = PHASE_ROOT / "logs" / f"{identifier}__hdfs_block_error.txt"
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=experiment_id,
            phase=1,
            run_id=identifier,
            dataset="HDFS",
            protocol="block_level_first_occurrence_60_20_20",
            status="FAILED",
            started_at=started,
            completed_at=utc_now(),
            command="scripts/run_hdfs_block_strengthening.py",
            error_path=relative(error_path),
            notes=f"{type(exc).__name__}: {exc}",
        )
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = load_config()["hdfs_block"]
    if args.dry_run:
        payload = {
            "status": "DRY_RUN",
            "raw_exists": (ROOT / config["raw"]).exists(),
            "labels_exists": (ROOT / config["labels"]).exists(),
            "config": relative(CONFIG_PATH),
        }
    else:
        payload = execute()
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
