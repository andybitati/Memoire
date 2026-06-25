"""Campagne ressources pour execution parallele Logminer.

Cette campagne mesure un scenario reproductible sans serveur FastAPI:
- generation d'un CSV synthetique labelise;
- execution de `compare_models(..., parallel_workers=N)`;
- echantillonnage CPU/RAM du processus Python pendant le run;
- export CSV, tableau Markdown et figure SVG pour le memoire/articles.
"""

from __future__ import annotations

import argparse
import csv
import statistics
import sys
import threading
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "logminer"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "docs" / "memoire" / "tables"
FIGURES = ROOT / "docs" / "memoire" / "figures"

from agents.model_compare import compare_models  # noqa: E402

try:
    import psutil
except ImportError:  # pragma: no cover - dependance optionnelle
    psutil = None


def build_synthetic_dataset(path: Path, rows: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    headers = ["timestamp_iso", "severity", "event", "source", "host", "user", "message", "label"]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter=";")
        writer.writeheader()
        for index in range(1, max(2, rows) + 1):
            anomalous = index % 17 == 0 or index % 43 == 0
            writer.writerow(
                {
                    "timestamp_iso": f"2026-06-25T10:{index % 60:02d}:{index % 60:02d}Z",
                    "severity": "ERROR" if anomalous else ("WARNING" if index % 9 == 0 else "INFO"),
                    "event": "4625" if anomalous else "4624",
                    "source": "parallel-campaign",
                    "host": f"host{index % 8}",
                    "user": f"user{index % 20}",
                    "message": "failed login denied attack pattern" if anomalous else "normal login accepted",
                    "label": "1" if anomalous else "0",
                }
            )
    return path


def _monitor(stop_event: threading.Event, samples: list[dict[str, float]], interval_sec: float) -> None:
    if psutil is None:
        return
    process = psutil.Process()
    logical_cpus = psutil.cpu_count(logical=True) or 1
    process.cpu_percent(interval=None)
    while not stop_event.wait(max(0.05, interval_sec)):
        try:
            cpu_core = float(process.cpu_percent(interval=None))
            memory_mb = float(process.memory_info().rss / 1024 / 1024)
            samples.append(
                {
                    "cpu_equiv_core_percent": round(cpu_core, 4),
                    "cpu_machine_percent": round(cpu_core / logical_cpus, 4),
                    "memory_mb": round(memory_mb, 4),
                }
            )
        except Exception:
            continue


def num(value: object) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def run_campaign(
    *,
    cycles: int,
    rows: int,
    parallel_workers: int,
    sample_interval_sec: float,
    output: Path,
) -> list[dict[str, Any]]:
    input_csv = build_synthetic_dataset(PROCESSED / "parallel_resource_campaign_input.csv", rows)
    campaign_rows: list[dict[str, Any]] = []

    for cycle in range(1, max(1, cycles) + 1):
        samples: list[dict[str, float]] = []
        stop_event = threading.Event()
        monitor = threading.Thread(target=_monitor, args=(stop_event, samples, sample_interval_sec), daemon=True)
        started = time.perf_counter()
        status = "ok"
        error = ""
        output_csv = PROCESSED / f"parallel_model_comparison_cycle_{cycle}.csv"
        monitor.start()
        try:
            compare_models(
                input_csv=input_csv,
                output_csv=output_csv,
                sep=";",
                contamination="auto",
                parallel_workers=parallel_workers,
            )
        except Exception as exc:
            status = "error"
            error = str(exc)
        finally:
            stop_event.set()
            monitor.join(timeout=2)

        elapsed = round(time.perf_counter() - started, 4)
        cpu_core_values = [sample["cpu_equiv_core_percent"] for sample in samples]
        cpu_machine_values = [sample["cpu_machine_percent"] for sample in samples]
        memory_values = [sample["memory_mb"] for sample in samples]
        campaign_rows.append(
            {
                "cycle": cycle,
                "status": status,
                "scenario": "model_compare_parallel",
                "events": rows,
                "parallel_workers": parallel_workers,
                "workflow_sec": elapsed,
                "samples": len(samples),
                "cpu_equiv_core_mean": round(statistics.mean(cpu_core_values), 4) if cpu_core_values else 0.0,
                "cpu_equiv_core_max": round(max(cpu_core_values), 4) if cpu_core_values else 0.0,
                "cpu_machine_mean": round(statistics.mean(cpu_machine_values), 4) if cpu_machine_values else 0.0,
                "cpu_machine_max": round(max(cpu_machine_values), 4) if cpu_machine_values else 0.0,
                "memory_mb_mean": round(statistics.mean(memory_values), 4) if memory_values else 0.0,
                "memory_mb_max": round(max(memory_values), 4) if memory_values else 0.0,
                "output_csv": str(output_csv),
                "error": error,
            }
        )

    write_csv(output, campaign_rows)
    return campaign_rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = [
        "cycle",
        "status",
        "scenario",
        "events",
        "parallel_workers",
        "workflow_sec",
        "samples",
        "cpu_equiv_core_mean",
        "cpu_equiv_core_max",
        "cpu_machine_mean",
        "cpu_machine_max",
        "memory_mb_mean",
        "memory_mb_max",
        "output_csv",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def write_table(path: Path, rows: list[dict[str, Any]]) -> None:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    workflow = [num(row["workflow_sec"]) for row in ok_rows]
    cpu = [num(row["cpu_machine_max"]) for row in ok_rows]
    memory = [num(row["memory_mb_max"]) for row in ok_rows]
    summary = [
        ["Cycles OK", len(ok_rows)],
        ["Evenements par cycle", ok_rows[0]["events"] if ok_rows else ""],
        ["Workers paralleles", ok_rows[0]["parallel_workers"] if ok_rows else ""],
        ["Duree moyenne workflow", f"{statistics.mean(workflow):.4f} s" if workflow else "n/a"],
        ["Duree maximale workflow", f"{max(workflow):.4f} s" if workflow else "n/a"],
        ["CPU machine max moyen", f"{statistics.mean(cpu):.4f} %" if cpu else "n/a"],
        ["RAM max moyenne", f"{statistics.mean(memory):.2f} MB" if memory else "n/a"],
    ]
    lines = [
        "# Campagne Ressources Parallele",
        "",
        "| Indicateur | Valeur |",
        "| --- | --- |",
    ]
    lines.extend(f"| {key} | {value} |" for key, value in summary)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    ok_rows = [row for row in rows if row.get("status") == "ok"]
    width, height = 980, 430
    left, right, top, bottom = 76, 42, 78, 66
    plot_w, plot_h = width - left - right, height - top - bottom
    max_value = max([num(row["cpu_machine_max"]) for row in ok_rows] + [1.0])
    max_value = max(max_value * 1.2, 5.0)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172026}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#5b6770}.axis{font-size:11px;fill:#5b6770}.label{font-size:12px}</style>",
        '<text x="36" y="34" class="title">Campagne parallele CPU/RAM</text>',
        '<text x="36" y="56" class="sub">Execution parallele de model_compare; pic CPU machine et RAM par cycle</text>',
    ]
    for tick in range(6):
        value = max_value * tick / 5
        y = top + plot_h - plot_h * tick / 5
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="#d9dee3"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" class="axis">{value:.1f}%</text>')
    points = []
    for index, row in enumerate(ok_rows):
        x = left + plot_w * index / max(1, len(ok_rows) - 1)
        y = top + plot_h - plot_h * num(row["cpu_machine_max"]) / max_value
        points.append((x, y))
    if points:
        parts.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="none" stroke="#2f6fbb" stroke-width="3"/>')
    for index, ((x, y), row) in enumerate(zip(points, ok_rows), start=1):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#d9822b"/>')
        parts.append(f'<text x="{x:.1f}" y="{height - 35}" text-anchor="middle" class="axis">{index}</text>')
        parts.append(f'<text x="{x:.1f}" y="{y - 11:.1f}" text-anchor="middle" class="label">{num(row["cpu_machine_max"]):.2f}%</text>')
    parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 10}" text-anchor="middle" class="sub">Cycles</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne ressources parallele Logminer")
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--rows", type=int, default=500)
    parser.add_argument("--parallel-workers", type=int, default=3)
    parser.add_argument("--sample-interval-sec", type=float, default=0.2)
    parser.add_argument("--output", type=Path, default=PROCESSED / "parallel_resource_campaign.csv")
    args = parser.parse_args()

    rows = run_campaign(
        cycles=args.cycles,
        rows=args.rows,
        parallel_workers=args.parallel_workers,
        sample_interval_sec=args.sample_interval_sec,
        output=args.output,
    )
    write_table(TABLES / "table_parallel_resource_campaign.md", rows)
    write_svg(FIGURES / "fig_parallel_resource_campaign.svg", rows)
    print(f"Campagne parallele ecrite: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
