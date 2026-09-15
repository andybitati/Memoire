#!/usr/bin/env python3
"""Évalue le routeur sur des fichiers originaux, sans pseudo-réplication en chunks."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PARSERS = SRC / "logminer" / "parsers"
SCRIPTS = ROOT / "scripts"
for directory in (SRC, PARSERS, SCRIPTS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

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
from logminer.parsers import bgl as bgl_parser  # noqa: E402
from logminer.parsers import hdfs as hdfs_parser  # noqa: E402
from logminer.parsers.windows_event import _iter_evtx_events, _parse_event_elem  # noqa: E402

CONFIG = PHASE_ROOT / "configs" / "router_independent_sources.json"
EXPERIMENT_ID = "dataset_04_router_independent"


def read_csv_sample(path: Path, limit: int) -> pd.DataFrame:
    header = path.open("r", encoding="utf-8-sig", errors="ignore").readline()
    separator = max((",", ";", "\t"), key=header.count)
    return pd.read_csv(path, sep=separator, dtype=str, keep_default_na=False, nrows=limit, encoding_errors="ignore")


def read_windows(path: Path, limit: int) -> pd.DataFrame:
    rows = []
    for index, event in enumerate(_iter_evtx_events(str(path)), start=1):
        rows.append(_parse_event_elem(event, "neutral.evtx", index))
        if len(rows) >= limit:
            break
    return pd.DataFrame(rows)


def read_hdfs(path: Path, limit: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            match = hdfs_parser.HDFS_SHORT_RE.match(line.rstrip("\r\n"))
            if not match:
                continue
            values = match.groupdict()
            message = values["message"]
            block = hdfs_parser.BLOCK_RE.search(message)
            rows.append({
                "dataset": "hdfs", "subtype": "hdfs", "lineno": lineno,
                "timestamp_iso": hdfs_parser._timestamp(values["date"], values["time"]),
                "severity": hdfs_parser._severity(values["severity"]), "event": block.group(0) if block else "",
                "source": values["source"], "component": values["source"], "message": message,
            })
            if len(rows) >= limit:
                break
    return pd.DataFrame(rows)


def read_bgl(path: Path, limit: int) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        for lineno, line in enumerate(handle, start=1):
            match = bgl_parser.BGL_RE.match(line.rstrip("\r\n"))
            if not match:
                continue
            values = match.groupdict()
            rows.append({
                "dataset": "bgl", "subtype": "bgl", "lineno": lineno,
                "timestamp_iso": bgl_parser._timestamp(values["timestamp"]),
                "severity": bgl_parser._severity(values["severity"]), "event": values["label"],
                "source": values["component"], "component": values["component"],
                "host": values["node"], "message": values["message"],
            })
            if len(rows) >= limit:
                break
    return pd.DataFrame(rows)


def load_source(item: dict[str, Any], limit: int) -> pd.DataFrame:
    path = ROOT / item["path"]
    adapter = item["adapter"]
    if adapter == "windows_evtx":
        frame = read_windows(path, limit)
    elif adapter == "hdfs_text":
        frame = read_hdfs(path, limit)
    elif adapter == "bgl_text":
        frame = read_bgl(path, limit)
    elif adapter == "linux_text":
        messages = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if line.strip():
                    messages.append(line.rstrip("\r\n"))
                if len(messages) >= limit:
                    break
        frame = pd.DataFrame({"dataset": "linux", "subtype": "syslog", "message": messages})
    elif adapter == "csv":
        frame = read_csv_sample(path, limit)
    else:
        raise ValueError(f"Adaptateur inconnu: {adapter}")
    # Le chemin local et le nom du fichier ne sont jamais offerts au routeur.
    return frame.drop(columns=[column for column in frame.columns if str(column).lower() == "filepath"], errors="ignore")


def measure(results: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in results if not row["error"]]
    y_true = [row["expected_route"] for row in valid]
    y_pred = [row["predicted_family"] for row in valid]
    known = [row for row in valid if row["true_family"] != "unknown_family"]
    unknown = [row for row in valid if row["true_family"] == "unknown_family"]
    return {
        "n_original_files": len(valid),
        "n_source_groups": len({row["source_group"] for row in valid}),
        "accuracy_all_expected_routes": float(accuracy_score(y_true, y_pred)) if valid else float("nan"),
        "macro_f1_all_expected_routes": float(f1_score(y_true, y_pred, average="macro", zero_division=0)) if valid else float("nan"),
        "known_accuracy": float(np.mean([row["correct"] for row in known])) if known else float("nan"),
        "fallback_rate": float(np.mean([row["fallback"] for row in valid])) if valid else float("nan"),
        "unknown_rejection_rate": float(np.mean([row["fallback"] for row in unknown])) if unknown else float("nan"),
        "confidence_margin_mean": float(np.mean([row["confidence_margin"] for row in valid])) if valid else float("nan"),
        "confidence_interpretation": "heuristic score margin; not a calibrated probability",
        "errors": len(results) - len(valid),
    }


def plot_confusion(results: list[dict[str, Any]], output: Path) -> None:
    valid = [row for row in results if not row["error"]]
    labels = sorted({row["expected_route"] for row in valid} | {row["predicted_family"] for row in valid})
    matrix = confusion_matrix([row["expected_route"] for row in valid], [row["predicted_family"] for row in valid], labels=labels)
    fig, ax = plt.subplots(figsize=(9.5, 8))
    image = ax.imshow(matrix, cmap="Blues")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=8)
    ax.set_xticks(range(len(labels)), labels, rotation=45, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("Famille prédite")
    ax.set_ylabel("Route attendue")
    ax.set_title("Routeur — une observation par fichier original")
    fig.colorbar(image, ax=ax, fraction=0.046)
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
    source_ids = [item["source_id"] for item in config["sources"]]
    paths = [item["path"] for item in config["sources"]]
    if len(source_ids) != len(set(source_ids)) or len(paths) != len(set(paths)):
        raise AssertionError("Chaque source_id et chaque fichier original doivent être uniques.")
    missing = [item["path"] for item in config["sources"] if not (ROOT / item["path"]).exists()]
    if missing:
        raise FileNotFoundError(f"Sources absentes: {missing}")
    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", "n_files": len(paths), "n_groups": len({item['source_group'] for item in config['sources']})}, ensure_ascii=False))
        return 0

    current_run = run_id("router_independent")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(experiment_id=EXPERIMENT_ID, phase="4/7", run_id=current_run, dataset="multi-source router corpus", protocol="one_original_file_no_path_signal", status="RUNNING", started_at=started_at, command="python scripts/run_router_independent_strengthening.py", error_path=relative(error_path))
    try:
        results: list[dict[str, Any]] = []
        manifest_sources = []
        neutral_dir = PHASE_ROOT / "processed" / current_run
        neutral_dir.mkdir(parents=True, exist_ok=True)
        for index, item in enumerate(config["sources"], start=1):
            path = ROOT / item["path"]
            frame = load_source(item, int(config["sample_rows"]))
            neutral_path = neutral_dir / f"source_{index:03d}.csv"
            frame.to_csv(neutral_path, index=False, encoding="utf-8-sig")
            started = perf_counter()
            try:
                route = route_dataframe(frame)
                predicted = str(route["family"])
                error = ""
            except Exception as exc:
                route = {"family": "", "model": "", "confidence": 0, "scores": {}, "reasons": []}
                predicted = ""
                error = f"{type(exc).__name__}: {exc}"
            expected = "fallback" if item["true_family"] == "unknown_family" else item["true_family"]
            results.append({
                **item,
                "run_id": current_run,
                "expected_route": expected,
                "predicted_family": predicted,
                "correct": predicted == expected,
                "fallback": predicted == "fallback",
                "confidence_margin": route["confidence"],
                "confidence_is_calibrated_probability": False,
                "model": route["model"],
                "scores_json": json.dumps(route["scores"], sort_keys=True),
                "reasons": " | ".join(str(value) for value in route["reasons"]),
                "sample_rows": len(frame),
                "neutral_artifact": relative(neutral_path),
                "latency_sec": perf_counter() - started,
                "error": error,
            })
            manifest_sources.append({"source_id": item["source_id"], "source_group": item["source_group"], "path": item["path"], "sha256": sha256_file(path), "neutral_path": relative(neutral_path), "neutral_sha256": sha256_file(neutral_path)})
        raw_path = PHASE_ROOT / "raw" / f"{current_run}_routes.csv"
        summary_path = PHASE_ROOT / "aggregated" / "router_independent_summary.json"
        confusion_path = PHASE_ROOT / "aggregated" / "router_independent_confusion.csv"
        figure_path = PHASE_ROOT / "figures" / "dataset_06_router_independent_confusion.png"
        write_csv(raw_path, results)
        summary = measure(results)
        write_json(summary_path, summary)
        valid = [row for row in results if not row["error"]]
        labels = sorted({row["expected_route"] for row in valid} | {row["predicted_family"] for row in valid})
        matrix = confusion_matrix([row["expected_route"] for row in valid], [row["predicted_family"] for row in valid], labels=labels)
        write_csv(confusion_path, [{"expected_route": a, "predicted_family": b, "count": int(matrix[i, j])} for i, a in enumerate(labels) for j, b in enumerate(labels)])
        plot_confusion(results, figure_path)
        write_json(PHASE_ROOT / "manifests" / f"{current_run}_manifest.json", {"run_id": current_run, "config_sha256": sha256_file(CONFIG), "path_signal": "disabled", "sources": manifest_sources})
        append_ledger(experiment_id=EXPERIMENT_ID, phase="4/7", run_id=current_run, dataset="multi-source router corpus", protocol="one_original_file_no_path_signal", status="COMPLETED", started_at=started_at, completed_at=utc_now(), command="python scripts/run_router_independent_strengthening.py", raw_result_path=relative(raw_path), summary_path=relative(summary_path), figure_path=relative(figure_path), error_path=relative(error_path), notes=f"N files={summary['n_original_files']}; source groups={summary['n_source_groups']}; confidence non calibrée")
        print(f"COMPLETED {current_run} accuracy={summary['accuracy_all_expected_routes']:.6f}")
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(experiment_id=EXPERIMENT_ID, phase="4/7", run_id=current_run, dataset="multi-source router corpus", protocol="one_original_file_no_path_signal", status="FAILED", started_at=started_at, completed_at=utc_now(), command="python scripts/run_router_independent_strengthening.py", error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
