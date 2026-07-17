"""Campagne Redis pour agents intelligents multi-taches.

La campagne valide trois points defendables pour le memoire:

- plusieurs workers/processus consomment un meme stream de taches;
- une panne avant acquittement laisse une tache pending;
- un autre worker recupere la tache pending via Redis Streams `XAUTOCLAIM`.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import quantiles


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = REPO_ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus
from agents.intelligent_runtime import AgentTask, RedisTaskSource


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 4)
    index = 94 if percent == 95 else 98
    return round(quantiles(values, n=100, method="inclusive")[index], 4)


def campaign_tasks(repetitions: int, input_path: str) -> list[AgentTask]:
    tasks: list[AgentTask] = []
    for index in range(max(1, repetitions)):
        tasks.extend(
            [
                AgentTask.create(
                    "parse.logs",
                    {"input_path": input_path, "out_name": f"redis_campaign_{index + 1}_parsed.csv"},
                    priority=90,
                ),
                AgentTask.create("route.model", {"input_path": input_path, "sample_rows": 200}, priority=75),
                AgentTask.create(
                    "discover.logs",
                    {"roots": ["examples", "data/samples", "data/processed"], "max_files": 15},
                    priority=45,
                ),
            ]
        )
    return tasks


def run_worker(
    args: argparse.Namespace,
    run_id: str,
    group: str,
    task_stream: str,
    consumer: str,
    agent_id: str,
    cycles: int,
    claim_idle_ms: int,
) -> subprocess.Popen:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(LOGMINER_SRC)
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "logminer_intelligent_agent_worker.py"),
        "--redis-url",
        args.redis_url,
        "--event-stream",
        args.event_stream,
        "--task-stream",
        task_stream,
        "--group",
        group,
        "--consumer",
        consumer,
        "--agent-id",
        agent_id,
        "--run-id",
        run_id,
        "--memory",
        f"data/processed/{agent_id}_memory.json",
        "--max-parallel-tasks",
        str(args.max_parallel_tasks),
        "--cycles",
        str(cycles),
        "--block-ms",
        str(args.block_ms),
        "--claim-idle-ms",
        str(claim_idle_ms),
    ]
    return subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_crash_worker(args: argparse.Namespace, run_id: str, group: str, task_stream: str) -> dict[str, str | int]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(LOGMINER_SRC)
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "logminer_intelligent_agent_worker.py"),
        "--redis-url",
        args.redis_url,
        "--event-stream",
        args.event_stream,
        "--task-stream",
        task_stream,
        "--group",
        group,
        "--consumer",
        "crash-worker",
        "--agent-id",
        "redis-crash-agent",
        "--run-id",
        run_id,
        "--memory",
        "data/processed/redis_crash_agent_memory.json",
        "--crash-after-fetch",
        "--block-ms",
        str(args.block_ms),
    ]
    completed = subprocess.run(command, cwd=REPO_ROOT, env=env, capture_output=True, text=True, check=False)
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def summarize_messages(bus: RedisMessageBus, run_id: str, count: int) -> dict[str, object]:
    messages = bus.read(run_id=run_id, count=count)
    completed = [message for message in messages if message.message_type == "agent.task.completed"]
    failed = [message for message in messages if message.message_type == "agent.task.failed"]
    crashed = [message for message in messages if message.message_type == "agent.simulated_crash"]
    unique_completed = {message.payload.get("result", {}).get("task_id", "") for message in completed}
    unique_failed = {message.payload.get("result", {}).get("task_id", "") for message in failed}
    elapsed = [
        float(message.payload.get("result", {}).get("elapsed_sec") or 0)
        for message in completed
    ]
    return {
        "messages": len(messages),
        "completed": len(completed),
        "unique_completed": len([task_id for task_id in unique_completed if task_id]),
        "failed": len(failed),
        "unique_failed": len([task_id for task_id in unique_failed if task_id]),
        "simulated_crashes": len(crashed),
        "by_agent": dict(Counter(message.source for message in completed)),
        "by_type": dict(Counter(message.payload.get("result", {}).get("task_type", "") for message in completed)),
        "elapsed_p95_sec": percentile(elapsed, 95),
        "elapsed_p99_sec": percentile(elapsed, 99),
    }


def write_markdown(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Campagne Redis Agents Intelligents",
        "",
        f"Date: {summary['timestamp']}",
        "",
        "## Resultat",
        "",
        f"- Run: `{summary['run_id']}`",
        f"- Workers: `{summary['workers']}`",
        f"- Taches enfilees: `{summary['tasks_enqueued']}`",
        f"- Taches terminees: `{summary['completed']}`",
        f"- Taches terminees uniques: `{summary['unique_completed']}`",
        f"- Taches echouees: `{summary['failed']}`",
        f"- Pannes simulees avant ack: `{summary['simulated_crashes']}`",
        f"- Pending apres campagne: `{summary['pending_after']}`",
        f"- Perte estimee: `{summary['estimated_loss']}`",
        f"- Debit: `{summary['tasks_per_sec']}` taches/s",
        f"- Latence p95/p99: `{summary['elapsed_p95_sec']}` / `{summary['elapsed_p99_sec']}` s",
        "",
        "## Repartition",
        "",
        "Par agent:",
        "",
        "```json",
        json.dumps(summary["by_agent"], ensure_ascii=False, indent=2),
        "```",
        "",
        "Par type de tache:",
        "",
        "```json",
        json.dumps(summary["by_type"], ensure_ascii=False, indent=2),
        "```",
        "",
        "## Interpretation",
        "",
        "Cette campagne apporte une preuve executable que les agents Logminer peuvent "
        "fonctionner comme workers distribues: ils partagent un stream Redis, publient "
        "leurs decisions et recuperent une tache abandonnee avant acquittement.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne Redis distribuee des agents intelligents")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--event-stream", default="logminer:events")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--repetitions", type=int, default=4)
    parser.add_argument("--max-parallel-tasks", type=int, default=2)
    parser.add_argument("--cycles", type=int, default=4)
    parser.add_argument("--block-ms", type=int, default=1000)
    parser.add_argument("--claim-idle-ms", type=int, default=1)
    parser.add_argument("--normal-claim-idle-ms", type=int, default=30000)
    parser.add_argument("--input", default="examples/windows_event_sample.xml")
    args = parser.parse_args()

    started = time.perf_counter()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    run_id = f"redis-campaign-{timestamp}"
    group = f"logminer-campaign-{timestamp}"
    task_stream = f"logminer:agent_tasks:campaign:{timestamp}"
    bus = RedisMessageBus(url=args.redis_url, stream=args.event_stream, run_id=run_id)
    bus.ping()
    source = RedisTaskSource(bus, stream=task_stream, group=group, consumer="campaign-enqueuer")
    task_ids = [source.enqueue(task) for task in campaign_tasks(args.repetitions, args.input)]

    crash = run_crash_worker(args, run_id, group, task_stream)
    time.sleep(max(0.05, args.claim_idle_ms / 1000))

    recovery = run_worker(
        args,
        run_id,
        group,
        task_stream,
        "recovery-worker",
        "redis-recovery-agent",
        1,
        args.claim_idle_ms,
    )
    recovery_stdout, recovery_stderr = recovery.communicate(timeout=120)

    workers = [
        run_worker(
            args,
            run_id,
            group,
            task_stream,
            f"worker-{index + 1}",
            f"redis-agent-{index + 1}",
            args.cycles,
            args.normal_claim_idle_ms,
        )
        for index in range(max(1, args.workers))
    ]
    worker_outputs = []
    for process in workers:
        stdout, stderr = process.communicate(timeout=120)
        worker_outputs.append({"returncode": process.returncode, "stdout": stdout, "stderr": stderr})

    elapsed = round(time.perf_counter() - started, 4)
    message_summary = summarize_messages(bus, run_id, count=5000)
    pending = bus.client.xpending(task_stream, group)
    pending_after = int(pending.get("pending", 0)) if isinstance(pending, dict) else 0
    completed = int(message_summary["completed"])
    unique_completed = int(message_summary["unique_completed"])
    failed = int(message_summary["failed"])
    unique_failed = int(message_summary["unique_failed"])
    summary: dict[str, object] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "task_stream": task_stream,
        "group": group,
        "workers": args.workers,
        "tasks_enqueued": len(task_ids),
        "completed": completed,
        "unique_completed": unique_completed,
        "failed": failed,
        "unique_failed": unique_failed,
        "simulated_crashes": message_summary["simulated_crashes"],
        "pending_after": pending_after,
        "estimated_loss": max(0, len(task_ids) - unique_completed - unique_failed - pending_after),
        "elapsed_sec": elapsed,
        "tasks_per_sec": round(completed / elapsed, 3) if elapsed > 0 else 0,
        "elapsed_p95_sec": message_summary["elapsed_p95_sec"],
        "elapsed_p99_sec": message_summary["elapsed_p99_sec"],
        "by_agent": message_summary["by_agent"],
        "by_type": message_summary["by_type"],
        "crash_worker": crash,
        "recovery_worker": {"returncode": recovery.returncode, "stdout": recovery_stdout, "stderr": recovery_stderr},
        "worker_outputs": worker_outputs,
    }

    output_json = REPO_ROOT / "data" / "processed" / "intelligent_redis_campaign_summary.json"
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(REPO_ROOT / "docs" / "architecture" / "intelligent_agents_redis_campaign_summary.md", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["estimated_loss"] == 0 and failed == 0 and unique_completed == len(task_ids) else 1


if __name__ == "__main__":
    raise SystemExit(main())
