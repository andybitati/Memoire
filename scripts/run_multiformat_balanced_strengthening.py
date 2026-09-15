#!/usr/bin/env python3
"""Validation multiformat équilibrée, isolée des anciennes preuves de phase 5."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SRC = ROOT / "src"
for directory in (SCRIPTS, SRC):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

import run_multiformat_validation as legacy  # noqa: E402
from dataset_strengthening_common import (  # noqa: E402
    PHASE_ROOT,
    append_ledger,
    ensure_phase_dirs,
    relative,
    run_id,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)
from logminer.agents.model_router import route_dataframe  # noqa: E402

CONFIG = PHASE_ROOT / "configs" / "multiformat_balanced_protocol.json"
EXPERIMENT_ID = "dataset_05_multiformat_balanced"


def read_normalized(path: Path) -> pd.DataFrame:
    header = path.open("r", encoding="utf-8-sig", errors="ignore").readline()
    separator = max((",", ";", "\t"), key=header.count)
    return pd.read_csv(path, sep=separator, dtype=str, keep_default_na=False, encoding_errors="ignore")


def normalized_path(root: Path, item: dict[str, Any]) -> Path:
    names = {
        "linux_auth": "linux_auth.csv",
        "wazuh": "wazuh.csv",
        "network_tabular": "network_tabular.csv",
    }
    return root / "normalized" / names.get(item["id"], f"{item['id']}.csv")


def make_figure(rows: list[dict[str, Any]], output: Path) -> None:
    labels = [row["source_id"] for row in rows]
    x = np.arange(len(rows))
    width = 0.25
    fig, ax = plt.subplots(figsize=(11, 6))
    for offset, key, label, color in ((-1, "parsing_coverage", "Parsing", "#4C78A8"), (0, "normalization_coverage", "Normalisation", "#54A24B"), (1, "loss_rate", "Perte", "#E45756")):
        ax.bar(x + offset * width, [float(row[key]) for row in rows], width, label=label, color=color)
    for index, row in enumerate(rows):
        ax.text(index, 1.02, f"N={row['read']}", ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x, labels, rotation=25, ha="right")
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Proportion")
    ax.set_title("Couverture multiformat par source — sans duplication")
    ax.legend(ncol=3)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    ensure_phase_dirs()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    missing = [item["source"] for item in config["formats"] if not (ROOT / item["source"]).exists()]
    if missing:
        raise FileNotFoundError(f"Sources absentes: {missing}")
    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", "sources": len(config["formats"]), "target": config["target_events_per_source"]}, ensure_ascii=False))
        return 0

    current_run = run_id("multiformat_balanced")
    started_at = utc_now()
    run_root = PHASE_ROOT / "processed" / current_run
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    legacy.PHASE_ROOT = run_root
    append_ledger(experiment_id=EXPERIMENT_ID, phase="5/7", run_id=current_run, dataset="8 sources", protocol="balanced_max_1000_no_duplication", status="RUNNING", started_at=started_at, command="python scripts/run_multiformat_balanced_strengthening.py", error_path=relative(error_path))
    try:
        summaries: list[dict[str, Any]] = []
        all_details: list[dict[str, Any]] = []
        all_fields: list[dict[str, Any]] = []
        manifest_sources: list[dict[str, Any]] = []
        for item in config["formats"]:
            summary, details, fields = legacy.analyse_item(item)
            indices = [int(row["event_index"]) for row in details]
            if len(indices) != len(set(indices)):
                raise AssertionError(f"Réutilisation d'unités détectée pour {item['id']}")
            normalized_file = normalized_path(run_root, item)
            fallback = 0
            routed_family = ""
            route_error = ""
            if normalized_file.exists() and summary["n_normalise"]:
                try:
                    normalized = read_normalized(normalized_file).drop(columns=["filepath"], errors="ignore")
                    route = route_dataframe(normalized.head(200))
                    routed_family = str(route["family"])
                    fallback = int(summary["n_normalise"]) if routed_family == "fallback" else 0
                except Exception as exc:
                    route_error = f"{type(exc).__name__}: {exc}"
            read_count = int(summary["n_lu"])
            parsed_count = int(summary["n_parse"])
            normalized_count = int(summary["n_normalise"])
            row = {
                "run_id": current_run,
                "source_id": item["id"],
                "display_name": item["display_name"],
                "source_path": item["source"],
                "source_status": item["source_status"],
                "raw_unit": item["raw_unit"],
                "target": int(item["limit"]),
                "read": read_count,
                "parsed": parsed_count,
                "normalized": normalized_count,
                "failed": int(summary["n_erreur"]),
                "lost": int(summary["n_perdu"]),
                "fallback": fallback,
                "fallback_measurement": "batch_route_applied_to_all_normalized_units",
                "routed_family": routed_family,
                "parsing_coverage": parsed_count / read_count if read_count else 0.0,
                "normalization_coverage": normalized_count / read_count if read_count else 0.0,
                "loss_rate": (read_count - normalized_count) / read_count if read_count else 0.0,
                "selection_duplicates": 0,
                "execution_error": summary["execution_error"],
                "route_error": route_error,
            }
            summaries.append(row)
            for detail in details:
                detail.update({"run_id": current_run, "source_id": item["id"]})
            for field in fields:
                field.update({"run_id": current_run, "source_id": item["id"]})
            all_details.extend(details)
            all_fields.extend(fields)
            manifest_sources.append({"source_id": item["id"], "path": item["source"], "sha256": sha256_file(ROOT / item["source"]), "normalized_path": relative(normalized_file) if normalized_file.exists() else "", "normalized_sha256": sha256_file(normalized_file) if normalized_file.exists() else ""})
        summary_path = PHASE_ROOT / "aggregated" / "multiformat_balanced_summary.csv"
        detail_path = PHASE_ROOT / "raw" / f"{current_run}_units.csv"
        fields_path = PHASE_ROOT / "aggregated" / "multiformat_mandatory_field_completeness.csv"
        failures_path = PHASE_ROOT / "raw" / f"{current_run}_failures.csv"
        figure_path = PHASE_ROOT / "figures" / "dataset_07_multiformat_coverage.png"
        write_csv(summary_path, summaries)
        write_csv(detail_path, all_details)
        write_csv(fields_path, all_fields)
        write_csv(failures_path, [row for row in all_details if str(row["parsed"]).lower() not in {"true", "1"}], fieldnames=list(all_details[0]) if all_details else ["run_id", "source_id", "parse_error"])
        make_figure(summaries, figure_path)
        write_json(PHASE_ROOT / "manifests" / f"{current_run}_manifest.json", {"run_id": current_run, "config_sha256": sha256_file(CONFIG), "selection_duplicates": 0, "sources": manifest_sources})
        append_ledger(experiment_id=EXPERIMENT_ID, phase="5/7", run_id=current_run, dataset="8 sources", protocol="balanced_max_1000_no_duplication", status="COMPLETED", started_at=started_at, completed_at=utc_now(), command="python scripts/run_multiformat_balanced_strengthening.py", raw_result_path=relative(detail_path), summary_path=relative(summary_path), figure_path=relative(figure_path), error_path=relative(error_path), notes=f"read={sum(row['read'] for row in summaries)} normalized={sum(row['normalized'] for row in summaries)}; Apache N réel conservé")
        print(f"COMPLETED {current_run} normalized={sum(row['normalized'] for row in summaries)}/{sum(row['read'] for row in summaries)}")
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(experiment_id=EXPERIMENT_ID, phase="5/7", run_id=current_run, dataset="8 sources", protocol="balanced_max_1000_no_duplication", status="FAILED", started_at=started_at, completed_at=utc_now(), command="python scripts/run_multiformat_balanced_strengthening.py", error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
