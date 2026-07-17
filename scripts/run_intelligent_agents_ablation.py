"""Ablation des modes Logminer pour le memoire.

Scenarios compares:

1. pipeline centralise;
2. agent unique multi-taches;
3. agents locaux multiples;
4. agents Redis distribues avec panne/reprise.

Chaque scenario est execute comme un processus separe. Le script mesure la
duree, le CPU cumule en equivalent coeur et la RAM maximale de l'arbre de
processus, puis produit les tableaux exploitables dans la redaction.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "docs" / "memoire" / "tables"
ARCH = ROOT / "docs" / "architecture"
LOGMINER_SRC = ROOT / "src" / "logminer"

try:
    import psutil
except ImportError:  # pragma: no cover - dependance deja dans requirements
    psutil = None


def env() -> dict[str, str]:
    current = os.environ.copy()
    current["PYTHONDONTWRITEBYTECODE"] = "1"
    current["PYTHONPATH"] = str(LOGMINER_SRC)
    return current


def scenario_commands(args: argparse.Namespace) -> list[dict[str, Any]]:
    central_code = (
        "import sys,json,time;"
        "from pathlib import Path;"
        "sys.path.insert(0,r'src\\logminer');"
        "import pipeline;"
        "from agents.model_router import route_for_file;"
        "started=time.perf_counter();"
        "out=pipeline.run_pipeline(r'examples\\windows_event_sample.xml',r'data\\processed\\ablation','central_pipeline.csv',debug=False);"
        "route=route_for_file(r'examples\\windows_event_sample.xml');"
        "print(json.dumps({'status':'ok','tasks_total':2,'tasks_failed':0,'output':out,'route_family':route.family,'elapsed_sec':round(time.perf_counter()-started,4)},ensure_ascii=False))"
    )
    return [
        {
            "scenario": "pipeline_centralise",
            "label": "Pipeline centralise",
            "claim": "Reference non distribuee: parsing + routage dans un seul processus",
            "command": [sys.executable, "-B", "-c", central_code],
        },
        {
            "scenario": "agent_unique_multitache",
            "label": "Agent unique multi-taches",
            "claim": "Un agent choisit et execute plusieurs types de taches",
            "command": [sys.executable, "-B", "scripts/run_intelligent_agents_demo.py", "--json"],
        },
        {
            "scenario": "agents_locaux_multiples",
            "label": "Agents locaux multiples",
            "claim": "Plusieurs agents partagent une file locale et se repartissent les taches",
            "command": [
                sys.executable,
                "-B",
                "scripts/run_intelligent_agents_campaign.py",
                "--agents",
                str(args.local_agents),
                "--repetitions",
                str(args.repetitions),
                "--max-parallel-tasks",
                str(args.max_parallel_tasks),
            ],
        },
        {
            "scenario": "agents_redis_panne_reprise",
            "label": "Agents Redis panne/reprise",
            "claim": "Workers Redis multi-processus avec panne avant ack et reprise pending",
            "command": [
                sys.executable,
                "-B",
                "scripts/run_intelligent_redis_campaign.py",
                "--workers",
                str(args.redis_workers),
                "--repetitions",
                str(args.repetitions),
                "--cycles",
                str(args.redis_cycles),
                "--max-parallel-tasks",
                str(args.max_parallel_tasks),
            ],
        },
    ]


def process_tree(root: Any) -> list[Any]:
    if psutil is None:
        return []
    try:
        return [root, *root.children(recursive=True)]
    except Exception:
        return [root]


def sample_resources(process: subprocess.Popen, interval_sec: float) -> dict[str, float]:
    if psutil is None:
        return {"cpu_core_avg": 0.0, "cpu_core_max": 0.0, "memory_mb_avg": 0.0, "memory_mb_max": 0.0, "samples": 0}
    root_process = psutil.Process(process.pid)
    cpu_values: list[float] = []
    memory_values: list[float] = []
    for proc in process_tree(root_process):
        try:
            proc.cpu_percent(interval=None)
        except Exception:
            pass
    while process.poll() is None:
        time.sleep(max(0.05, interval_sec))
        cpu_total = 0.0
        memory_total = 0.0
        for proc in process_tree(root_process):
            try:
                cpu_total += float(proc.cpu_percent(interval=None))
                memory_total += float(proc.memory_info().rss) / 1024 / 1024
            except Exception:
                continue
        cpu_values.append(cpu_total)
        memory_values.append(memory_total)
    return {
        "cpu_core_avg": round(mean(cpu_values), 3) if cpu_values else 0.0,
        "cpu_core_max": round(max(cpu_values), 3) if cpu_values else 0.0,
        "memory_mb_avg": round(mean(memory_values), 3) if memory_values else 0.0,
        "memory_mb_max": round(max(memory_values), 3) if memory_values else 0.0,
        "samples": len(cpu_values),
    }


def extract_json(stdout: str) -> dict[str, Any]:
    text = stdout.strip()
    if not text:
        return {}
    starts = [index for index, char in enumerate(text) if char in "[{"]
    for start in starts:
        try:
            parsed = json.loads(text[start:])
            if isinstance(parsed, list):
                return {"results": parsed}
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue
    return {"raw": text[-1000:]}


def normalize_metrics(scenario: dict[str, Any], payload: dict[str, Any], returncode: int) -> dict[str, Any]:
    summary = payload.get("summary") if isinstance(payload.get("summary"), dict) else payload
    results = payload.get("results") or summary.get("results") or []
    tasks_total = summary.get("tasks_total") or summary.get("completed") or summary.get("unique_completed")
    if tasks_total is None and isinstance(results, list):
        tasks_total = len(results)
    tasks_failed = summary.get("tasks_failed") or summary.get("failed") or summary.get("unique_failed") or 0
    if scenario["scenario"] == "pipeline_centralise":
        tasks_total = summary.get("tasks_total", 2)
        tasks_failed = summary.get("tasks_failed", 0 if returncode == 0 else 1)
    return {
        "scenario": scenario["scenario"],
        "label": scenario["label"],
        "claim": scenario["claim"],
        "returncode": returncode,
        "status": "ok" if returncode == 0 else "error",
        "tasks_total": int(tasks_total or 0),
        "tasks_failed": int(tasks_failed or 0),
        "tasks_per_sec_reported": summary.get("tasks_per_sec", ""),
        "simulated_crashes": summary.get("simulated_crashes", 0),
        "pending_after": summary.get("pending_after", ""),
        "estimated_loss": summary.get("estimated_loss", ""),
        "by_agent": json.dumps(summary.get("by_agent", {}), ensure_ascii=False),
        "by_type": json.dumps(summary.get("by_type", {}), ensure_ascii=False),
    }


def run_scenario(scenario: dict[str, Any], interval_sec: float) -> dict[str, Any]:
    started = time.perf_counter()
    process = subprocess.Popen(
        scenario["command"],
        cwd=ROOT,
        env=env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    resources = sample_resources(process, interval_sec)
    stdout, stderr = process.communicate(timeout=10)
    elapsed_sec = round(time.perf_counter() - started, 4)
    payload = extract_json(stdout)
    row = normalize_metrics(scenario, payload, process.returncode)
    row.update(
        {
            "elapsed_sec": elapsed_sec,
            "tasks_per_sec_measured": round(row["tasks_total"] / elapsed_sec, 4) if elapsed_sec > 0 else 0.0,
            **resources,
            "stdout_tail": stdout[-1200:],
            "stderr_tail": stderr[-1200:],
        }
    )
    return row


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    headers = [
        "scenario",
        "label",
        "status",
        "returncode",
        "tasks_total",
        "tasks_failed",
        "elapsed_sec",
        "tasks_per_sec_measured",
        "tasks_per_sec_reported",
        "cpu_core_avg",
        "cpu_core_max",
        "memory_mb_avg",
        "memory_mb_max",
        "samples",
        "simulated_crashes",
        "pending_after",
        "estimated_loss",
        "claim",
        "by_agent",
        "by_type",
        "stdout_tail",
        "stderr_tail",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def write_table(path: Path, title: str, headers: list[str], rows: list[list[Any]]) -> None:
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_markdown_summary(path: Path, rows: list[dict[str, Any]]) -> None:
    best = max(rows, key=lambda row: float(row.get("tasks_per_sec_measured") or 0))
    lines = [
        "# Ablation Agents Intelligents Multi-Taches",
        "",
        f"Date: {time.strftime('%Y-%m-%d')}",
        "",
        "## Lecture rapide",
        "",
        f"- Scenarios executes: `{len(rows)}`",
        f"- Meilleur debit local mesure: `{best['label']}` avec `{best['tasks_per_sec_measured']}` taches/s",
        "- Les VM/machines physiques ne sont pas testees dans cette campagne.",
        "",
        "## Resultats",
        "",
        "| Scenario | Statut | Taches | Echecs | Duree s | Taches/s | CPU max | RAM max MB | Preuve |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        proof = "panne/reprise" if int(row.get("simulated_crashes") or 0) else "execution"
        lines.append(
            f"| {row['label']} | {row['status']} | {row['tasks_total']} | {row['tasks_failed']} | "
            f"{row['elapsed_sec']} | {row['tasks_per_sec_measured']} | {row['cpu_core_max']} | "
            f"{row['memory_mb_max']} | {proof} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation scientifique",
            "",
            "L'ablation montre la progression de la contribution: le pipeline centralise "
            "sert de reference, l'agent unique rend explicite la selection autonome des "
            "taches, les agents locaux prouvent le partage d'une file, et Redis ajoute "
            "une distribution multi-processus avec reprise de tache non acquittee. "
            "Cette preuve reste locale; le deploiement sur VM ou machines distinctes "
            "est volontairement exclu de cette campagne.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ablation agents intelligents Logminer")
    parser.add_argument("--repetitions", type=int, default=4)
    parser.add_argument("--local-agents", type=int, default=3)
    parser.add_argument("--redis-workers", type=int, default=3)
    parser.add_argument("--redis-cycles", type=int, default=5)
    parser.add_argument("--max-parallel-tasks", type=int, default=2)
    parser.add_argument("--sample-interval-sec", type=float, default=0.25)
    parser.add_argument("--output", type=Path, default=PROCESSED / "intelligent_agents_ablation.csv")
    args = parser.parse_args()

    rows = [run_scenario(scenario, args.sample_interval_sec) for scenario in scenario_commands(args)]
    write_csv(args.output, rows)
    write_table(
        TABLES / "table_intelligent_agents_ablation.md",
        "Ablation Agents Intelligents",
        ["Scenario", "Statut", "Taches", "Echecs", "Duree s", "Taches/s", "Panne simulee", "Pending final", "Perte estimee"],
        [
            [
                row["label"],
                row["status"],
                row["tasks_total"],
                row["tasks_failed"],
                row["elapsed_sec"],
                row["tasks_per_sec_measured"],
                row["simulated_crashes"],
                row["pending_after"],
                row["estimated_loss"],
            ]
            for row in rows
        ],
    )
    write_table(
        TABLES / "table_intelligent_agents_resources.md",
        "Consommation Ressources Agents Intelligents",
        ["Scenario", "CPU moy. equiv. coeur", "CPU max equiv. coeur", "RAM moy. MB", "RAM max MB", "Echantillons"],
        [
            [row["label"], row["cpu_core_avg"], row["cpu_core_max"], row["memory_mb_avg"], row["memory_mb_max"], row["samples"]]
            for row in rows
        ],
    )
    write_markdown_summary(ARCH / "intelligent_agents_ablation_summary.md", rows)
    print(json.dumps({"output": str(args.output), "rows": rows}, ensure_ascii=False, indent=2))
    return 0 if all(row["status"] == "ok" and int(row["tasks_failed"]) == 0 for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
