"""Validation du Contract Net Logminer entre processus distincts via Redis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean, median


ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus
from agents.idempotency import RedisIdempotencyStore
from agents.intelligent_runtime import AgentTask
from agents.redis_contract_net import RedisContractNetCoordinator, RedisContractNetTransport


PHASE_ROOT = ROOT / "experiments" / "phase_multi_agent"


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(len(ordered) - 1, lower + 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def append_ledger(path: Path, row: dict[str, object]) -> None:
    fields = ["run_id", "started_at", "completed_at", "status", "loads", "repetitions", "workers", "raw_runs", "statistics", "sha256_manifest"]
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writerow(row)


def write_manifest(path: Path, run_id: str, files: list[Path]) -> None:
    records = []
    for file_path in sorted(set(files)):
        if not file_path.is_file():
            continue
        data = file_path.read_bytes()
        records.append(
            {
                "path": str(file_path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        )
    path.write_text(json.dumps({"run_id": run_id, "files": records}, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne CNP Redis entre processus")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--tasks", type=int, default=60)
    parser.add_argument("--timeout-sec", type=float, default=10.0)
    args = parser.parse_args()
    if args.tasks < 1:
        raise ValueError("--tasks doit être positif")

    started_at = datetime.now(timezone.utc).isoformat()
    run_id = datetime.now(timezone.utc).strftime("redis_cnp_%Y%m%dT%H%M%SZ") + f"_{os.getpid()}"
    namespace = f"logminer:cnp:{run_id}"
    event_stream = f"logminer:events:{run_id}"
    raw_dir = PHASE_ROOT / "raw"
    log_dir = PHASE_ROOT / "logs"
    report_dir = PHASE_ROOT / "reports"
    manifest_dir = PHASE_ROOT / "manifests"
    for directory in (raw_dir, log_dir, report_dir, manifest_dir):
        directory.mkdir(parents=True, exist_ok=True)

    bus = RedisMessageBus(url=args.redis_url, stream=event_stream, run_id=run_id, maxlen=100_000)
    if not bus.ping():
        raise RuntimeError("Redis ne répond pas")
    transport = RedisContractNetTransport(bus, namespace=namespace, run_id=run_id)
    profiles = (("redis-alpha", "alpha"), ("redis-beta", "beta"), ("redis-gamma", "gamma"))
    processes = []
    log_handles = []
    worker_logs = []
    for agent_id, profile in profiles:
        log_path = log_dir / f"{run_id}__{agent_id}.log"
        handle = log_path.open("w", encoding="utf-8")
        command = [
            sys.executable,
            "-B",
            "scripts/logminer_redis_cnp_agent.py",
            "--redis-url",
            args.redis_url,
            "--event-stream",
            event_stream,
            "--namespace",
            namespace,
            "--run-id",
            run_id,
            "--agent-id",
            agent_id,
            "--profile",
            profile,
            "--memory",
            "on",
            "--idle-timeout-sec",
            "8",
        ]
        process = subprocess.Popen(command, cwd=ROOT, stdout=handle, stderr=subprocess.STDOUT, text=True)
        processes.append((agent_id, process))
        log_handles.append(handle)
        worker_logs.append(log_path)

    registry_deadline = time.monotonic() + 20
    registry = {}
    while time.monotonic() < registry_deadline:
        registry = transport.registered_agents()
        if all(agent_id in registry for agent_id, _ in profiles):
            break
        if any(process.poll() not in {None, 0} for _, process in processes):
            break
        time.sleep(0.1)
    agent_ids = [agent_id for agent_id, _ in profiles if agent_id in registry]
    if len(agent_ids) != len(profiles):
        for _, process in processes:
            if process.poll() is None:
                process.terminate()
        for handle in log_handles:
            handle.close()
        raise RuntimeError(f"Registre incomplet: {sorted(registry)}")

    coordinator = RedisContractNetCoordinator(
        transport,
        agent_ids,
        response_timeout_sec=args.timeout_sec,
    )
    outcomes = []
    task_rows = []
    started = time.perf_counter()
    task_types = ("parse.synthetic", "route.synthetic", "detect.synthetic", "correlate.synthetic")
    for index in range(args.tasks):
        task = AgentTask(
            task_id=f"{run_id}-task-{index}",
            task_type=task_types[index % len(task_types)],
            payload={
                "values": [index + 1, index * 3 + 7, 17, 31],
                "idempotency_key": f"{run_id}-effect-{index}",
            },
        )
        outcome = coordinator.negotiate(task)
        outcomes.append(outcome)
        task_rows.append(
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "winner": outcome.winner,
                "status": outcome.status,
                "latency_ms": round(outcome.elapsed_sec * 1000, 6),
                "proposals": json.dumps(outcome.proposals, sort_keys=True),
                "refusals": json.dumps(outcome.refusals, sort_keys=True),
                "result_pid": (outcome.result.output.get("pid") if outcome.result else ""),
                "result_host": (outcome.result.output.get("host") if outcome.result else ""),
            }
        )
    duration_sec = time.perf_counter() - started

    counter_key = f"{namespace}:controlled_effect_counter"
    first_task = AgentTask(
        task_id=f"{run_id}-idempotence-first",
        task_type="parse.synthetic",
        payload={
            "values": [2, 3, 5, 7],
            "idempotency_key": f"{run_id}-shared-idempotence",
            "effect_counter_key": counter_key,
        },
    )
    first_effect = coordinator.negotiate(first_task)
    remaining_agents = [agent_id for agent_id in agent_ids if agent_id != first_effect.winner]
    replay_coordinator = RedisContractNetCoordinator(
        transport,
        remaining_agents,
        response_timeout_sec=args.timeout_sec,
    )
    replay_task = AgentTask(
        task_id=f"{run_id}-idempotence-replay",
        task_type="parse.synthetic",
        payload={
            "values": [2, 3, 5, 7],
            "idempotency_key": f"{run_id}-shared-idempotence",
            "effect_counter_key": counter_key,
        },
    )
    replay_effect = replay_coordinator.negotiate(replay_task)
    effect_count = int(bus.client.get(counter_key) or 0)

    for _, process in processes:
        try:
            process.wait(timeout=12)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)
    for handle in log_handles:
        handle.close()

    worker_status = {
        agent_id: {"pid": process.pid, "returncode": process.returncode}
        for agent_id, process in processes
    }
    latencies = [float(row["latency_ms"]) for row in task_rows]
    winners = Counter(row["winner"] for row in task_rows)
    events = bus.read(run_id=run_id, count=100_000)
    event_log = log_dir / f"{run_id}__agent_messages.jsonl"
    with event_log.open("w", encoding="utf-8") as handle:
        for message in events:
            handle.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
    message_counts = Counter(message.message_type for message in events)
    completed = sum(row["status"] == "ok" for row in task_rows)
    summary = {
        "run_id": run_id,
        "namespace": namespace,
        "redis_url": args.redis_url,
        "redis_server": bus.client.info("server").get("redis_version"),
        "host": socket.gethostname(),
        "registered_agents": registry,
        "worker_status": worker_status,
        "tasks": args.tasks,
        "successful_tasks": completed,
        "failed_tasks": args.tasks - completed,
        "duration_sec": round(duration_sec, 6),
        "throughput_tasks_sec": round(completed / duration_sec, 6),
        "latency_mean_ms": round(fmean(latencies), 6),
        "latency_median_ms": round(median(latencies), 6),
        "latency_p95_ms": round(percentile(latencies, 0.95), 6),
        "latency_p99_ms": round(percentile(latencies, 0.99), 6),
        "tasks_by_agent": dict(winners),
        "message_counts": dict(message_counts),
        "distinct_result_pids": sorted({str(row["result_pid"]) for row in task_rows if row["result_pid"]}),
        "distinct_result_hosts": sorted({str(row["result_host"]) for row in task_rows if row["result_host"]}),
        "idempotence": {
            "first_agent": first_effect.winner,
            "replay_agent": replay_effect.winner,
            "different_process_agents": first_effect.winner != replay_effect.winner,
            "first_status": first_effect.status,
            "replay_status": replay_effect.status,
            "replayed": bool(replay_effect.result and replay_effect.result.output.get("_idempotency_replayed")),
            "persistent_effects": effect_count,
            "duplicate_effects": max(0, effect_count - 1),
            "redis_completed_keys": RedisIdempotencyStore(bus.client, f"{namespace}:idempotency").completed_count(),
        },
        "status": "ok"
        if completed == args.tasks
        and len({process.pid for _, process in processes}) == 3
        and effect_count == 1
        and bool(replay_effect.result and replay_effect.result.output.get("_idempotency_replayed"))
        else "partial",
    }

    raw_json = raw_dir / f"{run_id}__redis_cnp.json"
    raw_csv = raw_dir / f"{run_id}__redis_cnp_tasks.csv"
    raw_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with raw_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(task_rows[0]))
        writer.writeheader()
        writer.writerows(task_rows)
    report = report_dir / f"{run_id}__redis_cnp.md"
    report.write_text(
        "\n".join(
            [
                "# Campagne CNP Redis inter-processus",
                "",
                f"- Run : `{run_id}`",
                f"- Redis : `{summary['redis_server']}`",
                f"- Agents enregistrés : `{len(registry)}`",
                f"- PID distincts : `{summary['distinct_result_pids']}`",
                f"- Tâches réussies : `{completed}/{args.tasks}`",
                f"- Débit : `{summary['throughput_tasks_sec']}` tâches/s",
                f"- Latence p95 : `{summary['latency_p95_ms']}` ms",
                f"- Répartition : `{json.dumps(dict(winners), ensure_ascii=False)}`",
                f"- Effets persistants du replay : `{effect_count}`",
                f"- Replay idempotent détecté : `{summary['idempotence']['replayed']}`",
                "",
                "Les processus sont distincts mais s'exécutent sur le même hôte Windows. Cette campagne n'est pas une preuve multi-VM.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    manifest = manifest_dir / f"{run_id}__sha256.json"
    write_manifest(
        manifest,
        run_id,
        [
            raw_json,
            raw_csv,
            event_log,
            report,
            *worker_logs,
            ROOT / "scripts" / "logminer_redis_cnp_agent.py",
            ROOT / "scripts" / "run_redis_cnp_process_campaign.py",
            ROOT / "src" / "logminer" / "agents" / "redis_contract_net.py",
            ROOT / "src" / "logminer" / "agents" / "idempotency.py",
        ],
    )
    append_ledger(
        manifest_dir / "EXPERIMENT_LEDGER.csv",
        {
            "run_id": run_id,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": summary["status"],
            "loads": json.dumps([args.tasks]),
            "repetitions": 1,
            "workers": len(agent_ids),
            "raw_runs": str(raw_json.relative_to(ROOT)).replace("\\", "/"),
            "statistics": str(raw_csv.relative_to(ROOT)).replace("\\", "/"),
            "sha256_manifest": str(manifest.relative_to(ROOT)).replace("\\", "/"),
        },
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
