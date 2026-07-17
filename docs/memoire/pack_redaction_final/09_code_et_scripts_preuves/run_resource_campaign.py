"""Campagne CPU/RAM multi-cycles pour Logminer.

Le script mesure plusieurs cycles de workflow via l'API locale deja lancee.
Il n'essaie pas de demarrer FastAPI: cela evite les attentes longues et rend le
protocole explicite.

Sorties:
- data/processed/resource_campaign.csv
- docs/memoire/tables/table_resource_campaign_multicycle.md
- docs/memoire/figures/fig_resource_campaign_multicycle.svg
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "docs" / "memoire" / "tables"
FIGURES = ROOT / "docs" / "memoire" / "figures"


def post_json(url: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url: str, timeout: int) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def num(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = [
        "cycle",
        "status",
        "run_id",
        "workflow_sec",
        "parse_sec",
        "route_sec",
        "detect_sec",
        "correlate_sec",
        "input_rows",
        "anomalies_rows",
        "incidents_rows",
        "agent",
        "cpu_equiv_core_percent",
        "cpu_machine_percent",
        "memory_mb",
        "logical_cpus",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, title: str, headers: list[str], rows: list[list[object]]) -> None:
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def summarize(rows: list[dict[str, Any]]) -> list[list[object]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row.get("status") != "ok" or not row.get("agent"):
            continue
        grouped.setdefault(str(row["agent"]), []).append(row)

    summary: list[list[object]] = []
    for agent, values in sorted(grouped.items()):
        workflow = [num(row["workflow_sec"]) for row in values if num(row["workflow_sec"]) > 0]
        cpu_core = [num(row["cpu_equiv_core_percent"]) for row in values]
        cpu_machine = [num(row["cpu_machine_percent"]) for row in values]
        memory = [num(row["memory_mb"]) for row in values]
        summary.append(
            [
                agent,
                len(values),
                f"{statistics.mean(workflow):.4f}" if workflow else "n/a",
                f"{max(workflow):.4f}" if workflow else "n/a",
                f"{statistics.mean(cpu_core):.2f}",
                f"{max(cpu_core):.2f}",
                f"{statistics.mean(cpu_machine):.2f}",
                f"{max(cpu_machine):.2f}",
                f"{statistics.mean(memory):.2f}",
                f"{max(memory):.2f}",
            ]
        )
    return summary


def write_svg(path: Path, rows: list[dict[str, Any]]) -> None:
    ok_rows = [row for row in rows if row.get("status") == "ok" and row.get("agent")]
    agents = sorted({str(row["agent"]) for row in ok_rows})
    width = 980
    height = 420
    left = 72
    right = 32
    top = 72
    bottom = 58
    plot_w = width - left - right
    plot_h = height - top - bottom
    colors = ["#2f6fbb", "#c23b38", "#2f8f46", "#d9822b"]
    max_cpu = max([num(row["cpu_machine_percent"]) for row in ok_rows] + [1.0])
    max_cpu = max(max_cpu, 10.0)
    cycles = sorted({int(num(row["cycle"])) for row in ok_rows})

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172026}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#5b6770}.axis{font-size:11px;fill:#5b6770}.legend{font-size:12px}</style>",
        '<text x="36" y="34" class="title">Campagne CPU/RAM multi-cycles</text>',
        '<text x="36" y="56" class="sub">CPU machine normalise par agent sur plusieurs cycles Logminer</text>',
    ]
    for tick in range(6):
        y = top + plot_h - plot_h * tick / 5
        value = max_cpu * tick / 5
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="#d9dee3"/>')
        parts.append(f'<text x="{left - 10}" y="{y + 4:.1f}" text-anchor="end" class="axis">{value:.1f}%</text>')
    for index, agent in enumerate(agents):
        points = []
        agent_rows = [row for row in ok_rows if row["agent"] == agent]
        by_cycle = {int(num(row["cycle"])): row for row in agent_rows}
        for cycle in cycles:
            row = by_cycle.get(cycle)
            if not row:
                continue
            x = left + plot_w * (cycle - min(cycles)) / max(1, max(cycles) - min(cycles))
            y = top + plot_h - plot_h * num(row["cpu_machine_percent"]) / max_cpu
            points.append((x, y))
        if points:
            color = colors[index % len(colors)]
            parts.append(
                f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in points)}" fill="none" stroke="{color}" stroke-width="3"/>'
            )
            for x, y in points:
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
            legend_y = height - 28 - index * 18
            parts.append(f'<rect x="{left + index * 230}" y="{legend_y - 10}" width="12" height="12" fill="{color}"/>')
            parts.append(f'<text x="{left + 18 + index * 230}" y="{legend_y}" class="legend">{agent}</text>')
    parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 8}" text-anchor="middle" class="sub">Cycles</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def run_campaign(api_base: str, cycles: int, interval_sec: float, max_mb: int, timeout: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    api_base = api_base.rstrip("/")
    for cycle in range(1, cycles + 1):
        status = "ok"
        error = ""
        workflow: dict[str, Any] = {}
        resources: dict[str, Any] = {}
        try:
            workflow = post_json(
                f"{api_base}/run/discovered",
                {"use_redis": False, "max_mb": max_mb, "run_id": f"resource-campaign-{int(time.time())}-{cycle}"},
                timeout=timeout,
            )
            resources = get_json(f"{api_base}/resources", timeout=timeout)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            status = "error"
            error = str(exc)

        agents = resources.get("agents") or [{}]
        for agent in agents:
            rows.append(
                {
                    "cycle": cycle,
                    "status": status,
                    "run_id": workflow.get("run_id", ""),
                    "workflow_sec": (workflow.get("timings") or {}).get("workflow_sec", ""),
                    "parse_sec": (workflow.get("timings") or {}).get("parse_sec", ""),
                    "route_sec": (workflow.get("timings") or {}).get("route_sec", ""),
                    "detect_sec": (workflow.get("timings") or {}).get("detect_sec", ""),
                    "correlate_sec": (workflow.get("timings") or {}).get("correlate_sec", ""),
                    "input_rows": workflow.get("input_rows", ""),
                    "anomalies_rows": workflow.get("anomalies_rows", ""),
                    "incidents_rows": workflow.get("incidents_rows", ""),
                    "agent": agent.get("agent", ""),
                    "cpu_equiv_core_percent": agent.get("cpu_percent", ""),
                    "cpu_machine_percent": agent.get("cpu_machine_percent", ""),
                    "memory_mb": agent.get("memory_mb", ""),
                    "logical_cpus": resources.get("logical_cpus", ""),
                    "error": error,
                }
            )
        if cycle < cycles:
            time.sleep(max(0.0, interval_sec))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne CPU/RAM multi-cycles Logminer")
    parser.add_argument("--api-base", default="http://127.0.0.1:8000")
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--interval-sec", type=float, default=2.0)
    parser.add_argument("--max-mb", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--output", type=Path, default=PROCESSED / "resource_campaign.csv")
    args = parser.parse_args()

    rows = run_campaign(args.api_base, max(1, args.cycles), args.interval_sec, args.max_mb, args.timeout)
    write_csv(args.output, rows)
    summary = summarize(rows)
    write_md(
        TABLES / "table_resource_campaign_multicycle.md",
        "Campagne Ressources Multi-Cycles",
        [
            "Agent",
            "Cycles",
            "Workflow moy. s",
            "Workflow max s",
            "CPU equiv. moy.",
            "CPU equiv. max",
            "CPU machine moy.",
            "CPU machine max",
            "RAM moy. MB",
            "RAM max MB",
        ],
        summary,
    )
    write_svg(FIGURES / "fig_resource_campaign_multicycle.svg", rows)
    print(f"Campagne ecrite: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
