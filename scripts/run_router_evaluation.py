#!/usr/bin/env python3
"""Evaluate the real Logminer file router on a frozen, source-labelled corpus."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from logminer.agents.model_router import MODEL_DEFAULTS, route_model  # noqa: E402


DOC_ROOT = ROOT / "docs" / "memoire" / "final_experiments_2026"
DATA_ROOT = ROOT / "data" / "processed" / "final_experiments_2026"
PHASE_ROOT = DATA_ROOT / "phase_6"
DEFAULT_CONFIG = DOC_ROOT / "configs" / "router_evaluation_protocol.json"
LEDGER = DOC_ROOT / "state" / "EXPERIMENT_LEDGER.csv"
EXPERIMENT_ID = "e6_router_real_primary"


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str:
    process = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    return process.stdout.strip() if process.returncode == 0 else ""


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        if not names:
            return
        writer = csv.DictWriter(handle, fieldnames=names, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def ledger_latest() -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            latest[row["experiment_id"]] = row
    return latest


def append_ledger(status: str, *, started_at: str = "", completed_at: str = "", notes: str = "") -> None:
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as handle:
        fieldnames = next(csv.reader(handle))
    row = {
        "experiment_id": EXPERIMENT_ID,
        "phase": 6,
        "run_id": EXPERIMENT_ID,
        "dataset": "router source-labelled derived corpus",
        "scenario": "neutral_filename_chunks",
        "seed": "",
        "model": "agents.model_router.route_model",
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "command": "scripts/run_router_evaluation.py --resume",
        "config_path": str(DEFAULT_CONFIG.relative_to(ROOT)).replace("\\", "/"),
        "raw_result_path": "data/processed/final_experiments_2026/router_evaluation_raw.csv",
        "summary_path": "data/processed/final_experiments_2026/router_evaluation_summary.json",
        "figure_path": "docs/memoire/final_experiments_2026/figures/router_confusion_matrix.png",
        "git_commit": git_commit(),
        "notes": notes,
    }
    with LEDGER.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writerow({name: row.get(name, "") for name in fieldnames})


def load_source(item: dict[str, Any]) -> pd.DataFrame:
    path = ROOT / item["source"]
    actual_hash = sha256_file(path)
    if actual_hash != item["source_sha256"]:
        raise RuntimeError(f"Source hash mismatch for {item['id']}: {actual_hash}")
    if item["sep"] == "parquet":
        return pd.read_parquet(path).head(int(item["max_rows"])).astype(str)
    return pd.read_csv(
        path,
        sep=item["sep"],
        dtype=str,
        keep_default_na=False,
        nrows=int(item["max_rows"]),
        encoding_errors="ignore",
    )


def build_corpus(config: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    chunk_rows = int(config["chunk_rows"])
    max_chunks = int(config["max_chunks_per_source"])
    for item in config["sources"]:
        frame = load_source(item)
        source_dir = PHASE_ROOT / "corpus" / item["id"]
        source_dir.mkdir(parents=True, exist_ok=True)
        for index, start in enumerate(range(0, len(frame), chunk_rows)):
            if index >= max_chunks:
                break
            chunk = frame.iloc[start : start + chunk_rows].copy()
            if chunk.empty:
                continue
            path = source_dir / f"chunk_{index:03d}.csv"
            chunk.to_csv(path, index=False, encoding="utf-8-sig")
            rows.append(
                {
                    "source_id": item["id"],
                    "true_family": item["true_family"],
                    "source_path": item["source"],
                    "chunk_path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "chunk_rows": len(chunk),
                    "chunk_sha256": sha256_file(path),
                }
            )
    return rows


def route_corpus(corpus: list[dict[str, Any]], sample_rows: int) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    known_families = set(MODEL_DEFAULTS)
    for item in corpus:
        path = ROOT / item["chunk_path"]
        started = perf_counter()
        try:
            route = route_model(path, sep="auto", sample_rows=sample_rows)
            predicted = str(route["family"])
            model_path = Path(str(route["model"]))
            resolved_model = model_path if model_path.is_absolute() else ROOT / model_path
            error = ""
            model_exists = resolved_model.exists()
            confidence = int(route["confidence"])
            reasons = " | ".join(str(reason) for reason in route["reasons"])
            scores = json.dumps(route["scores"], sort_keys=True, ensure_ascii=True)
            kind = str(route["kind"])
        except Exception as exc:
            predicted = ""
            error = f"{type(exc).__name__}: {exc}"
            model_exists = False
            confidence = 0
            reasons = ""
            scores = "{}"
            kind = ""
        results.append(
            {
                **item,
                "predicted_family": predicted,
                "correct": predicted == item["true_family"],
                "confidence_margin": confidence,
                "rule_used": reasons,
                "scores_json": scores,
                "kind": kind,
                "fallback": predicted == "fallback",
                "unknown": bool(predicted and predicted not in known_families),
                "model_exists": model_exists,
                "error": error,
                "route_duration_sec": round(perf_counter() - started, 6),
            }
        )
    return results


def metrics(results: list[dict[str, Any]]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    successful = [row for row in results if not row["error"]]
    labels = sorted({str(row["true_family"]) for row in successful} | {str(row["predicted_family"]) for row in successful})
    y_true = [str(row["true_family"]) for row in successful]
    y_pred = [str(row["predicted_family"]) for row in successful]
    precision, recall, f1, support = precision_recall_fscore_support(y_true, y_pred, labels=labels, zero_division=0)
    family_rows = [
        {
            "family": label,
            "precision": round(float(precision[index]), 6),
            "recall": round(float(recall[index]), 6),
            "f1": round(float(f1[index]), 6),
            "support": int(support[index]),
        }
        for index, label in enumerate(labels)
    ]
    matrix = confusion_matrix(y_true, y_pred, labels=labels)
    confusion_rows = [
        {"true_family": true_label, "predicted_family": predicted_label, "count": int(matrix[i, j])}
        for i, true_label in enumerate(labels)
        for j, predicted_label in enumerate(labels)
    ]
    summary = {
        "schema_version": 1,
        "generated_at": utcnow(),
        "experiment_id": EXPERIMENT_ID,
        "files_total": len(results),
        "files_routed": len(successful),
        "files_correct": sum(bool(row["correct"]) for row in successful),
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 6) if successful else 0.0,
        "macro_precision": round(float(np.mean(precision)), 6) if len(precision) else 0.0,
        "macro_recall": round(float(np.mean(recall)), 6) if len(recall) else 0.0,
        "macro_f1": round(float(np.mean(f1)), 6) if len(f1) else 0.0,
        "fallback_rate": round(sum(bool(row["fallback"]) for row in successful) / len(successful), 6) if successful else 0.0,
        "unknown_rate": round(sum(bool(row["unknown"]) for row in successful) / len(successful), 6) if successful else 0.0,
        "error_rate": round((len(results) - len(successful)) / len(results), 6) if results else 0.0,
        "all_selected_models_exist": all(bool(row["model_exists"]) for row in successful),
        "confidence_is_calibrated_probability": False,
        "unit": "derived CSV file",
    }
    return summary, family_rows, confusion_rows, labels


def make_outputs(config: dict[str, Any], results: list[dict[str, Any]]) -> dict[str, Any]:
    summary, family_rows, confusion_rows, labels = metrics(results)
    raw_path = DATA_ROOT / "router_evaluation_raw.csv"
    family_path = DATA_ROOT / "router_metrics_by_family.csv"
    confusion_path = DATA_ROOT / "router_confusion_matrix.csv"
    summary_path = DATA_ROOT / "router_evaluation_summary.json"
    write_csv(raw_path, results)
    write_csv(family_path, family_rows)
    write_csv(confusion_path, confusion_rows)
    summary["config"] = str(DEFAULT_CONFIG.relative_to(ROOT)).replace("\\", "/")
    summary["source_count"] = len(config["sources"])
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    matrix = np.array([[next(row["count"] for row in confusion_rows if row["true_family"] == true and row["predicted_family"] == pred) for pred in labels] for true in labels])
    fig, ax = plt.subplots(figsize=(9.0, 7.4))
    image = ax.imshow(matrix, cmap="Blues")
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, str(matrix[i, j]), ha="center", va="center", color="white" if matrix[i, j] > matrix.max() / 2 else "black")
    ax.set_xticks(range(len(labels)), labels, rotation=35, ha="right")
    ax.set_yticks(range(len(labels)), labels)
    ax.set_xlabel("Famille prédite")
    ax.set_ylabel("Vraie famille issue de la source")
    ax.set_title(f"Routeur réel — matrice de confusion\nFichiers à nom neutre, N={len(results)}, chunks de 100 événements")
    fig.colorbar(image, ax=ax, label="Nombre de fichiers")
    fig.tight_layout()
    figure_path = DOC_ROOT / "figures" / "router_confusion_matrix.png"
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    table_path = DOC_ROOT / "tables" / "router_metrics_by_family.md"
    lines = [
        "# Évaluation du routeur réel par famille",
        "",
        f"N = {summary['files_total']} fichiers dérivés à noms neutres ; unité = fichier ; exactitude = {summary['accuracy']:.6f} ; F1 macro = {summary['macro_f1']:.6f}.",
        "",
        "| Famille | Support | Précision | Rappel | F1 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in family_rows:
        lines.append(f"| {row['family']} | {row['support']} | {row['precision']:.6f} | {row['recall']:.6f} | {row['f1']:.6f} |")
    lines.extend(["", "La confiance est une marge de scores heuristiques, pas une probabilité calibrée. Les chunks d'une même source ne sont pas des réplications indépendantes."])
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--register-plan", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    expected_files = sum(min(int(config["max_chunks_per_source"]), (int(item["max_rows"]) + int(config["chunk_rows"]) - 1) // int(config["chunk_rows"])) for item in config["sources"])
    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", "sources": len(config["sources"]), "expected_files": expected_files}, ensure_ascii=True))
        return 0
    if args.register_plan:
        if EXPERIMENT_ID not in ledger_latest():
            append_ledger("PLANNED", notes=f"registered before routing; expected_files={expected_files}")
        print(json.dumps({"status": "PLAN_REGISTERED", "expected_files": expected_files}, ensure_ascii=True))
        return 0

    required = [
        DATA_ROOT / "router_evaluation_raw.csv",
        DATA_ROOT / "router_metrics_by_family.csv",
        DATA_ROOT / "router_confusion_matrix.csv",
        DATA_ROOT / "router_evaluation_summary.json",
    ]
    if args.resume and ledger_latest().get(EXPERIMENT_ID, {}).get("status") == "COMPLETED" and all(path.exists() and path.stat().st_size > 0 for path in required):
        print(f"SKIPPED_ALREADY_COMPLETED {EXPERIMENT_ID}")
        return 0

    started = utcnow()
    append_ledger("RUNNING", started_at=started)
    corpus = build_corpus(config)
    results = route_corpus(corpus, int(config["sample_rows"]))
    summary = make_outputs(config, results)
    append_ledger(
        "COMPLETED",
        started_at=started,
        completed_at=utcnow(),
        notes=f"files={summary['files_total']} correct={summary['files_correct']} accuracy={summary['accuracy']}",
    )
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
