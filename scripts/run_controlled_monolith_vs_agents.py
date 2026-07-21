"""Controlled comparison between monolithic execution and Logminer agents."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "logminer"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "docs" / "memoire" / "tables"

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


def _env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SRC)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def _worker_code(mode: str, repetitions: int, agents: int, fail_after: int) -> str:
    return rf'''
import json, sys, time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, r"{SRC}")
sys.path.insert(0, r"{ROOT / 'scripts'}")

from agents.bus import LocalMessageBus
from agents.intelligent_runtime import AgentContext, AgentMemory, AgentTask, InMemoryTaskSource
from run_intelligent_agents_demo import (
    build_agent,
    discover_handler,
    parse_handler,
    route_handler,
)

handlers = {{
    "discover.logs": discover_handler,
    "parse.logs": parse_handler,
    "route.model": route_handler,
}}

def make_tasks(repetitions):
    tasks = []
    for index in range(repetitions):
        tasks.append(AgentTask.create("discover.logs", {{"roots": ["examples", "data/samples", "data/processed"], "max_files": 10}}, priority=40))
        tasks.append(AgentTask.create("parse.logs", {{"input_path": "examples/windows_event_sample.xml", "out_name": f"controlled_parse_{{index}}.csv"}}, priority=90))
        tasks.append(AgentTask.create("route.model", {{"input_path": "examples/windows_event_sample.xml", "sample_rows": 200}}, priority=70))
    return tasks

def monolith(tasks):
    started = time.perf_counter()
    latencies = []
    failed = 0
    context = AgentContext(
        agent_id="controlled-monolith",
        run_id="controlled-monolith",
        bus=LocalMessageBus(Path("data/processed/controlled_monolith_bus.jsonl")),
        memory=AgentMemory(),
        workspace=Path("."),
    )
    for task in tasks:
        t0 = time.perf_counter()
        try:
            handlers[task.task_type](task, context)
        except Exception:
            failed += 1
        latencies.append(time.perf_counter() - t0)
    elapsed = time.perf_counter() - started
    return {{
        "mode": "monolith",
        "tasks_total": len(tasks),
        "tasks_completed": len(tasks) - failed,
        "tasks_failed": failed,
        "simulated_crashes": 0,
        "recovered_tasks": 0,
        "pending_final": 0,
        "elapsed_sec": elapsed,
        "task_latency_mean": sum(latencies) / len(latencies) if latencies else 0,
        "task_latency_p95": sorted(latencies)[int(0.95 * (len(latencies) - 1))] if latencies else 0,
    }}

def agents_run(tasks):
    source = InMemoryTaskSource(tasks)
    bus = Path("data/processed/controlled_agents_bus.jsonl")
    results = []
    started = time.perf_counter()
    def run(index):
        agent = build_agent(bus, Path(f"data/processed/controlled_agent_{{index}}_memory.json"), 1)
        agent.agent_id = f"controlled-agent-{{index}}"
        local = []
        while True:
            batch = agent.run_once(source)
            if not batch:
                break
            local.extend(asdict(item) if hasattr(item, "__dataclass_fields__") else item for item in batch)
        return local
    with ThreadPoolExecutor(max_workers={agents}) as executor:
        for part in executor.map(run, range({agents})):
            results.extend(part)
    elapsed = time.perf_counter() - started
    latencies = [float(item.get("elapsed_sec") or 0) for item in results]
    failed = sum(1 for item in results if item.get("status") != "ok")
    return {{
        "mode": "agents",
        "tasks_total": len(tasks),
        "tasks_completed": len(results) - failed,
        "tasks_failed": failed,
        "simulated_crashes": 0,
        "recovered_tasks": 0,
        "pending_final": 0,
        "elapsed_sec": elapsed,
        "task_latency_mean": sum(latencies) / len(latencies) if latencies else 0,
        "task_latency_p95": sorted(latencies)[int(0.95 * (len(latencies) - 1))] if latencies else 0,
    }}

def agents_failure(tasks, fail_after):
    # Controlled lease simulation: one task is deliberately skipped by a crashed
    # worker, then completed by a recovery pass over the same task list.
    started = time.perf_counter()
    completed = []
    pending = []
    failed_once = False
    agent = build_agent(Path("data/processed/controlled_agents_failure_bus.jsonl"), Path("data/processed/controlled_agent_failure_memory.json"), 1)
    agent.agent_id = "controlled-agent-failure"
    for index, task in enumerate(tasks):
        if index == fail_after and not failed_once:
            pending.append(task)
            failed_once = True
            continue
        result = agent.execute_task(task)
        completed.append(asdict(result))
    recovery = build_agent(Path("data/processed/controlled_agents_failure_bus.jsonl"), Path("data/processed/controlled_agent_recovery_memory.json"), 1)
    recovery.agent_id = "controlled-agent-recovery"
    recovered = []
    for task in pending:
        result = recovery.execute_task(task)
        recovered.append(asdict(result))
    elapsed = time.perf_counter() - started
    all_results = completed + recovered
    latencies = [float(item.get("elapsed_sec") or 0) for item in all_results]
    failed = sum(1 for item in all_results if item.get("status") != "ok")
    return {{
        "mode": "agents_failure_recovery",
        "tasks_total": len(tasks),
        "tasks_completed": len(all_results) - failed,
        "tasks_failed": failed,
        "simulated_crashes": 1,
        "recovered_tasks": len(recovered),
        "pending_final": 0,
        "elapsed_sec": elapsed,
        "task_latency_mean": sum(latencies) / len(latencies) if latencies else 0,
        "task_latency_p95": sorted(latencies)[int(0.95 * (len(latencies) - 1))] if latencies else 0,
    }}

tasks = make_tasks({repetitions})
mode = "{mode}"
if mode == "monolith":
    payload = monolith(tasks)
elif mode == "agents":
    payload = agents_run(tasks)
elif mode == "agents_failure_recovery":
    payload = agents_failure(tasks, {fail_after})
else:
    raise SystemExit(f"unknown mode: {{mode}}")
print(json.dumps(payload, ensure_ascii=False))
'''


def _process_tree(process: Any) -> list[Any]:
    if psutil is None:
        return []
    try:
        root = psutil.Process(process.pid)
        return [root, *root.children(recursive=True)]
    except Exception:
        return []


def _cpu_seconds(process: Any) -> float:
    total = 0.0
    for proc in _process_tree(process):
        try:
            times = proc.cpu_times()
            total += float(times.user) + float(times.system)
        except Exception:
            continue
    return total


def _run_mode(mode: str, repetitions: int, agents: int, fail_after: int, interval: float) -> dict[str, Any]:
    process = subprocess.Popen(
        [sys.executable, "-B", "-c", _worker_code(mode, repetitions, agents, fail_after)],
        cwd=ROOT,
        env=_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    cpu_values: list[float] = []
    ram_values: list[float] = []
    wall_started = time.perf_counter()
    cpu_started = _cpu_seconds(process)
    cpu_last = cpu_started
    if psutil is not None:
        for proc in _process_tree(process):
            try:
                proc.cpu_percent(interval=None)
            except Exception:
                pass
    while process.poll() is None:
        time.sleep(interval)
        cpu = 0.0
        ram = 0.0
        current_cpu_seconds = _cpu_seconds(process)
        cpu_last = max(cpu_last, current_cpu_seconds)
        for proc in _process_tree(process):
            try:
                cpu += float(proc.cpu_percent(interval=None))
                ram += float(proc.memory_info().rss) / 1024 / 1024
            except Exception:
                continue
        cpu_values.append(cpu)
        ram_values.append(ram)
    stdout, stderr = process.communicate(timeout=10)
    wall_elapsed = max(0.001, time.perf_counter() - wall_started)
    cpu_core_avg_from_time = max(0.0, (cpu_last - cpu_started) / wall_elapsed * 100.0)
    payload: dict[str, Any] = {}
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            payload = parsed
            break
    payload.update(
        {
            "mode": payload.get("mode", mode),
            "tasks_total": int(payload.get("tasks_total") or repetitions * 3),
            "tasks_completed": int(payload.get("tasks_completed") or 0),
            "tasks_failed": int(payload.get("tasks_failed") or (repetitions * 3 if process.returncode else 0)),
            "simulated_crashes": int(payload.get("simulated_crashes") or 0),
            "recovered_tasks": int(payload.get("recovered_tasks") or 0),
            "pending_final": int(payload.get("pending_final") or 0),
            "elapsed_sec": float(payload.get("elapsed_sec") or 0.0),
            "task_latency_mean": float(payload.get("task_latency_mean") or 0.0),
            "task_latency_p95": float(payload.get("task_latency_p95") or 0.0),
            "returncode": process.returncode,
            "status": "ok" if process.returncode == 0 and not payload.get("tasks_failed") else "error",
            "cpu_core_avg": round(cpu_core_avg_from_time or (mean(cpu_values) if cpu_values else 0.0), 3),
            "cpu_core_max": round(max(cpu_values), 3) if cpu_values else 0.0,
            "ram_mb_avg": round(mean(ram_values), 3) if ram_values else 0.0,
            "ram_mb_max": round(max(ram_values), 3) if ram_values else 0.0,
            "samples": len(cpu_values),
            "stderr_tail": stderr[-500:],
        }
    )
    payload["throughput_tasks_sec"] = round(float(payload.get("tasks_completed") or 0) / float(payload.get("elapsed_sec") or 1), 6)
    return payload


def _write_outputs(rows: list[dict[str, Any]], csv_path: Path, table_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    headers = [
        "mode",
        "status",
        "tasks_total",
        "tasks_completed",
        "tasks_failed",
        "elapsed_sec",
        "throughput_tasks_sec",
        "task_latency_mean",
        "task_latency_p95",
        "cpu_core_avg",
        "cpu_core_max",
        "ram_mb_avg",
        "ram_mb_max",
        "simulated_crashes",
        "recovered_tasks",
        "pending_final",
        "samples",
        "returncode",
        "stderr_tail",
    ]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    lines = [
        "# Comparaison Controlee Monolithique Vs Agents",
        "",
        "| Mode | Taches | Echecs | Duree s | Debit t/s | Latence moy. | Latence p95 | CPU max | RAM max MB | Reprises | Pending final |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        row = dict(row)
        if float(row.get("cpu_core_max") or 0) == 0 and float(row.get("cpu_core_avg") or 0) > 0:
            row["cpu_core_max"] = row["cpu_core_avg"]
        lines.append(
            "| {mode} | {tasks_completed}/{tasks_total} | {tasks_failed} | {elapsed_sec:.4f} | {throughput_tasks_sec:.4f} | {task_latency_mean:.4f} | {task_latency_p95:.4f} | {cpu_core_max:.3f} | {ram_mb_max:.3f} | {recovered_tasks} | {pending_final} |".format(
                **row
            )
        )
    lines.extend(
        [
            "",
            "Note: les modes executent les memes types de taches et le meme volume sur le meme poste. La variante avec panne simule une tache non acquittee puis une reprise controlee.",
        ]
    )
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Controlled monolithic-vs-agents benchmark")
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--fail-after", type=int, default=7)
    parser.add_argument("--sample-interval-sec", type=float, default=0.1)
    parser.add_argument("--output", type=Path, default=PROCESSED / "controlled_monolith_vs_agents.csv")
    parser.add_argument("--table-out", type=Path, default=TABLES / "table_controlled_monolith_vs_agents.md")
    args = parser.parse_args()
    rows = [
        _run_mode("monolith", args.repetitions, args.agents, args.fail_after, args.sample_interval_sec),
        _run_mode("agents", args.repetitions, args.agents, args.fail_after, args.sample_interval_sec),
        _run_mode("agents_failure_recovery", args.repetitions, args.agents, args.fail_after, args.sample_interval_sec),
    ]
    _write_outputs(rows, args.output, args.table_out)
    print(json.dumps({"output": str(args.output), "rows": rows}, ensure_ascii=False, indent=2))
    return 0 if all(row["status"] == "ok" for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
