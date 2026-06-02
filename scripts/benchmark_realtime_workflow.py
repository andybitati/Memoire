"""Benchmark quasi temps reel du workflow Logminer.

Le script appelle l'API FastAPI locale plusieurs fois et enregistre les
latences par cycle. Il sert les objectifs 4 et 7 du document directeur:
detection quasi temps reel, latence et charge par workflow.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def post_json(url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def run_benchmark(api_base: str, cycles: int, interval_sec: float, output: Path, max_mb: int) -> Path:
    rows: list[dict[str, Any]] = []
    endpoint = f"{api_base.rstrip('/')}/run/discovered"
    for index in range(1, cycles + 1):
        started = time.perf_counter()
        status = "ok"
        error = ""
        result: dict[str, Any] = {}
        try:
            result = post_json(endpoint, {"use_redis": False, "max_mb": max_mb, "run_id": f"bench-{int(time.time())}-{index}"}, timeout=120)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            status = "error"
            error = str(exc)
        elapsed = round(time.perf_counter() - started, 4)
        timings = result.get("timings") or {}
        rows.append(
            {
                "cycle": index,
                "status": status,
                "elapsed_sec": elapsed,
                "workflow_sec": timings.get("workflow_sec", ""),
                "parse_sec": timings.get("parse_sec", ""),
                "detect_and_correlate_sec": timings.get("detect_and_correlate_sec", ""),
                "input_rows": result.get("input_rows", ""),
                "anomalies_rows": result.get("anomalies_rows", ""),
                "incidents_rows": result.get("incidents_rows", ""),
                "run_id": result.get("run_id", ""),
                "error": error,
            }
        )
        if index < cycles:
            time.sleep(max(0.0, interval_sec))

    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark quasi temps reel Logminer")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000")
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--interval-sec", type=float, default=5.0)
    parser.add_argument("--max-mb", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("data/processed/realtime_workflow_benchmark.csv"))
    args = parser.parse_args()

    output = run_benchmark(args.api_base, max(1, args.cycles), args.interval_sec, args.output, args.max_mb)
    print(f"Benchmark ecrit: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
