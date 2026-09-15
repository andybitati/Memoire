"""Campagne Contract Net avec agents déjà lancés sur plusieurs VM."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import socket
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


def append_ledger(path: Path, row: dict[str, object]) -> None:
    fields = ["run_id", "started_at", "completed_at", "status", "loads", "repetitions", "workers", "raw_runs", "statistics", "sha256_manifest"]
    with path.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fields).writerow(row)


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne CNP Redis multi-VM")
    parser.add_argument("--redis-url", default="redis://192.168.56.1:6379/0")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agents", default="debian-alpha,ubuntu-beta")
    parser.add_argument("--tasks", type=int, default=60)
    parser.add_argument("--timeout-sec", type=float, default=10.0)
    parser.add_argument("--registry-timeout-sec", type=float, default=45.0)
    args = parser.parse_args()
    agent_ids = [item.strip() for item in args.agents.split(",") if item.strip()]
    if args.tasks < 1 or len(agent_ids) < 2:
        raise ValueError("La campagne exige au moins une tâche et deux agents")

    started_at = datetime.now(timezone.utc).isoformat()
    namespace = f"logminer:cnp:{args.run_id}"
    event_stream = f"logminer:events:{args.run_id}"
    raw_dir = PHASE_ROOT / "raw"
    log_dir = PHASE_ROOT / "logs"
    report_dir = PHASE_ROOT / "reports"
    manifest_dir = PHASE_ROOT / "manifests"
    for directory in (raw_dir, log_dir, report_dir, manifest_dir):
        directory.mkdir(parents=True, exist_ok=True)

    bus = RedisMessageBus(url=args.redis_url, stream=event_stream, run_id=args.run_id, maxlen=100_000)
    if not bus.ping():
        raise RuntimeError("Redis ne répond pas")
    transport = RedisContractNetTransport(bus, namespace=namespace, run_id=args.run_id)
    deadline = time.monotonic() + args.registry_timeout_sec
    registry: dict[str, object] = {}
    while time.monotonic() < deadline:
        registry = transport.registered_agents()
        if all(agent_id in registry for agent_id in agent_ids):
            break
        time.sleep(0.2)
    if not all(agent_id in registry for agent_id in agent_ids):
        raise RuntimeError(f"Registre multi-VM incomplet: {sorted(registry)}")

    coordinator = RedisContractNetCoordinator(transport, agent_ids, response_timeout_sec=args.timeout_sec)
    task_types = ("parse.synthetic", "route.synthetic", "detect.synthetic", "correlate.synthetic")
    task_rows: list[dict[str, object]] = []
    started = time.perf_counter()
    for index in range(args.tasks):
        task = AgentTask(
            task_id=f"{args.run_id}-task-{index}",
            task_type=task_types[index % len(task_types)],
            payload={"values": [index + 1, index * 3 + 7, 17, 31], "idempotency_key": f"{args.run_id}-effect-{index}"},
        )
        outcome = coordinator.negotiate(task)
        task_rows.append(
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "winner": outcome.winner,
                "status": outcome.status,
                "latency_ms": round(outcome.elapsed_sec * 1000, 6),
                "proposals": json.dumps(outcome.proposals, sort_keys=True),
                "refusals": json.dumps(outcome.refusals, sort_keys=True),
                "result_pid": outcome.result.output.get("pid", "") if outcome.result else "",
                "result_host": outcome.result.output.get("host", "") if outcome.result else "",
                "reassignments": outcome.reassignments,
            }
        )
    duration_sec = time.perf_counter() - started

    counter_key = f"{namespace}:controlled_effect_counter"
    shared_key = f"{args.run_id}-shared-idempotence"
    first = coordinator.negotiate(
        AgentTask(
            task_id=f"{args.run_id}-idempotence-first",
            task_type="parse.synthetic",
            payload={"values": [2, 3, 5, 7], "idempotency_key": shared_key, "effect_counter_key": counter_key},
        )
    )
    replay_agents = [agent_id for agent_id in agent_ids if agent_id != first.winner]
    replay = RedisContractNetCoordinator(transport, replay_agents, response_timeout_sec=args.timeout_sec).negotiate(
        AgentTask(
            task_id=f"{args.run_id}-idempotence-replay",
            task_type="parse.synthetic",
            payload={"values": [2, 3, 5, 7], "idempotency_key": shared_key, "effect_counter_key": counter_key},
        )
    )
    effect_count = int(bus.client.get(counter_key) or 0)

    events = bus.read(run_id=args.run_id, count=100_000)
    event_log = log_dir / f"{args.run_id}__agent_messages.jsonl"
    with event_log.open("w", encoding="utf-8") as handle:
        for message in events:
            handle.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
    message_counts = Counter(message.message_type for message in events)
    winners = Counter(str(row["winner"]) for row in task_rows)
    latencies = [float(row["latency_ms"]) for row in task_rows]
    completed = sum(row["status"] == "ok" for row in task_rows)
    reassignments = sum(int(row["reassignments"]) for row in task_rows)
    result_hosts = sorted({str(row["result_host"]) for row in task_rows if row["result_host"]})
    registry_hosts = sorted({str(registry[agent_id].get("host", "")) for agent_id in agent_ids})
    replayed = bool(replay.result and replay.result.output.get("_idempotency_replayed"))
    status = (
        "ok"
        if completed == args.tasks
        and len(result_hosts) >= 2
        and effect_count == 1
        and replayed
        and message_counts.get("REFUSE", 0) > 0
        and reassignments > 0
        else "partial"
    )
    summary = {
        "run_id": args.run_id,
        "namespace": namespace,
        "redis_url": args.redis_url,
        "redis_server": bus.client.info("server").get("redis_version"),
        "coordinator_host": socket.gethostname(),
        "registered_agents": {agent_id: registry[agent_id] for agent_id in agent_ids},
        "registry_hosts": registry_hosts,
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
        "reassignments": reassignments,
        "distinct_result_pids": sorted({str(row["result_pid"]) for row in task_rows if row["result_pid"]}),
        "distinct_result_hosts": result_hosts,
        "idempotence": {
            "first_agent": first.winner,
            "replay_agent": replay.winner,
            "different_agents": first.winner != replay.winner,
            "replayed": replayed,
            "persistent_effects": effect_count,
            "duplicate_effects": max(0, effect_count - 1),
            "redis_completed_keys": RedisIdempotencyStore(bus.client, f"{namespace}:idempotency").completed_count(),
        },
        "status": status,
    }

    raw_json = raw_dir / f"{args.run_id}__redis_cnp_multivm.json"
    raw_csv = raw_dir / f"{args.run_id}__redis_cnp_multivm_tasks.csv"
    report = report_dir / f"{args.run_id}__redis_cnp_multivm.md"
    manifest = manifest_dir / f"{args.run_id}__sha256.json"
    raw_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    with raw_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(task_rows[0]))
        writer.writeheader()
        writer.writerows(task_rows)
    report.write_text(
        "\n".join(
            [
                "# Campagne CNP Redis multi-VM",
                "",
                f"- Run : `{args.run_id}`",
                f"- Redis : `{summary['redis_server']}` sur l'hôte de laboratoire `{args.redis_url}`",
                f"- Hôtes agents : `{registry_hosts}`",
                f"- Tâches réussies : `{completed}/{args.tasks}`",
                f"- Débit : `{summary['throughput_tasks_sec']}` tâches/s",
                f"- Latence p95 : `{summary['latency_p95_ms']}` ms",
                f"- Répartition : `{json.dumps(dict(winners), ensure_ascii=False)}`",
                f"- Refus explicites : `{message_counts.get('REFUSE', 0)}` ; réattributions après échec : `{reassignments}`",
                f"- Replay idempotent : `{replayed}` ; effets persistants : `{effect_count}`",
                f"- Statut : `{status}`",
                "",
                "Cette expérience démontre des décisions et exécutions d'agents sur deux VM. Redis reste centralisé sur l'hôte Windows du laboratoire ; aucune haute disponibilité ni portée industrielle n'est revendiquée.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    write_manifest(
        manifest,
        args.run_id,
        [raw_json, raw_csv, event_log, report, Path(__file__), ROOT / "scripts" / "logminer_redis_cnp_agent.py", ROOT / "src" / "logminer" / "agents" / "redis_contract_net.py", ROOT / "src" / "logminer" / "agents" / "idempotency.py"],
    )
    append_ledger(
        manifest_dir / "EXPERIMENT_LEDGER.csv",
        {
            "run_id": args.run_id,
            "started_at": started_at,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "loads": json.dumps([args.tasks]),
            "repetitions": 1,
            "workers": len(agent_ids),
            "raw_runs": str(raw_json.relative_to(ROOT)).replace("\\", "/"),
            "statistics": str(raw_csv.relative_to(ROOT)).replace("\\", "/"),
            "sha256_manifest": str(manifest.relative_to(ROOT)).replace("\\", "/"),
        },
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
