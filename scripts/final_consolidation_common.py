"""Utilitaires reproductibles de la consolidation scientifique finale."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PHASE_ROOT = ROOT / "experiments" / "phase_final_scientific_consolidation"
CONFIG_PATH = PHASE_ROOT / "configs" / "final_scientific_consolidation_protocol.json"
PHASE_LEDGER = PHASE_ROOT / "LEDGER.csv"
GLOBAL_LEDGER = ROOT / "state" / "EXPERIMENT_LEDGER.csv"
LEDGER_FIELDS = [
    "experiment_id", "phase", "run_id", "dataset", "protocol", "status",
    "started_at", "completed_at", "command", "config_path", "raw_result_path",
    "summary_path", "figure_path", "error_path", "git_commit", "notes",
]


def ensure_phase_dirs() -> None:
    for name in ("configs", "raw", "processed", "aggregated", "figures", "logs", "reports", "manifests"):
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


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT,
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "INFORMATION À VÉRIFIER"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )
    temporary.replace(path)


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Objet non sérialisable en JSON : {type(value).__name__}")


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    data = list(rows)
    columns = fieldnames if fieldnames is not None else (list(data[0]) if data else [])
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
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
