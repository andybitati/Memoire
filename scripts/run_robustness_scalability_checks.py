"""Controle robustesse et scalabilite Logminer.

Ce script couvre les objectifs 6 et 7 du document directeur: tester des logs
varies, verifier le comportement sur entree incomplete/corrompue et produire
un rapport simple de scalabilite multi-source.
"""

from __future__ import annotations

import argparse
import csv
import sys
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from logminer.detectors.file_detector import detect_kind, iter_files
from logminer.pipeline import run_pipeline


SAMPLES: dict[str, bytes] = {
    "linux_auth.log": b"Jun  2 10:00:01 srv sshd[10]: Failed password for invalid user root from 10.0.0.5 port 51234 ssh2\n",
    "apache_access.log": b'10.0.0.8 - - [02/Jun/2026:10:01:00 +0100] "GET /admin HTTP/1.1" 403 532 "-" "curl/8"\n',
    "cloudtrail.jsonl": b'{"eventTime":"2026-06-02T09:00:00Z","eventSource":"iam.amazonaws.com","eventName":"CreateUser","userIdentity":{"userName":"admin"}}\n',
    "cef.log": b"CEF:0|Example|IDS|1.0|100|Port scan detected|8|src=10.0.0.4 dst=10.0.0.9\n",
    "corrupt_incomplete.log": b"\xff\xfe\x00broken line without known structure\n<Event><System><EventID>",
}


def write_samples(input_dir: Path) -> None:
    input_dir.mkdir(parents=True, exist_ok=True)
    for name, content in SAMPLES.items():
        (input_dir / name).write_bytes(content)


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8-sig", errors="ignore") as handle:
        return max(0, sum(1 for _ in handle) - 1)


def rows_by_filepath(paths: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for output in paths:
        path = Path(output)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", errors="ignore", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            for row in reader:
                filepath = row.get("filepath", "")
                counts[filepath] = counts.get(filepath, 0) + 1
    return counts


def run_checks(input_dir: Path, output_csv: Path, parsed_dir: Path) -> Path:
    write_samples(input_dir)
    rows: list[dict[str, Any]] = []

    discovered = list(iter_files(str(input_dir)))
    started = time.perf_counter()
    produced = run_pipeline(
        str(input_dir),
        out_dir=str(parsed_dir),
        out_name="robustness_scalability_events.csv",
        sep=";",
        debug=False,
    )
    elapsed = round(time.perf_counter() - started, 4)
    parsed_rows = sum(count_rows(Path(path)) for path in produced)
    per_file_rows = rows_by_filepath(produced)

    for path in discovered:
        item = Path(path)
        kind = detect_kind(str(item))
        normalized_rows = per_file_rows.get(str(item), 0)
        status = "ok" if normalized_rows > 0 else "no_rows"
        if item.name.startswith("corrupt") and kind == "unknown" and normalized_rows > 0:
            status = "kept_unknown"
        rows.append(
            {
                "scenario": "multi_source_or_corrupt",
                "file": item.name,
                "detected_kind": kind,
                "status": status,
                "normalized_rows": normalized_rows,
                "pipeline_elapsed_sec": elapsed,
                "total_files": len(discovered),
                "total_parsed_rows": parsed_rows,
                "produced_csv": "|".join(str(Path(p)) for p in produced),
            }
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    return output_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Controle robustesse/scalabilite Logminer")
    parser.add_argument("--input-dir", type=Path, default=Path("data/processed/robustness_scalability_inputs"))
    parser.add_argument("--parsed-dir", type=Path, default=Path("data/processed/robustness_scalability_outputs"))
    parser.add_argument("--output", type=Path, default=Path("data/processed/robustness_scalability_report.csv"))
    args = parser.parse_args()

    output = run_checks(args.input_dir, args.output, args.parsed_dir)
    print(f"Rapport ecrit: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
