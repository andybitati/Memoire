"""Test de saturation en boucle ouverte du Contract Net Redis sur deux VM.

Le producteur planifie des tâches ``hdfs.block.evaluate`` à un débit offert
constant pendant une fenêtre fixe, indépendamment des réponses (boucle ouverte).
Chaque négociation est exécutée par un coordinateur propre à son thread ; tous
partagent le même flux de réponses, filtré par ``contract_id``. La latence est
mesurée depuis l'instant planifié : elle inclut donc l'attente côté coordinateur.
"""

from __future__ import annotations

import argparse
import csv
import json
import socket
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus  # noqa: E402
from agents.intelligent_runtime import AgentTask  # noqa: E402
from agents.redis_contract_net import RedisContractNetCoordinator, RedisContractNetTransport  # noqa: E402

OUT = Path(__file__).resolve().parent


def percentile(values, quantile):
    ordered = sorted(values)
    if not ordered:
        return None
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--redis-url", default="redis://127.0.0.1:6379/0")
    parser.add_argument("--agents", default="debian-alpha,ubuntu-beta")
    parser.add_argument("--rates", default="1,2,4,8,16,32,64")
    parser.add_argument("--window-sec", type=float, default=30.0)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--threads", type=int, default=32)
    parser.add_argument("--threshold", type=float, default=1.2729429339548877)
    parser.add_argument("--input", default="experiments/phase_final_scientific_consolidation/processed/hdfs_test_block_frozen_mean_scores.csv")
    args = parser.parse_args()

    agents = [item.strip() for item in args.agents.split(",") if item.strip()]
    bus = RedisMessageBus(url=args.redis_url, stream="logminer:events:" + args.run_id, run_id=args.run_id, maxlen=500000)
    transport = RedisContractNetTransport(bus, namespace="logminer:cnp:" + args.run_id, run_id=args.run_id)
    deadline = time.monotonic() + 120
    registry = {}
    while time.monotonic() < deadline:
        registry = transport.registered_agents()
        if all(agent in registry for agent in agents):
            break
        time.sleep(0.25)
    if not all(agent in registry for agent in agents):
        raise RuntimeError("registre incomplet: " + repr(sorted(registry)))
    hosts = sorted({str(registry[agent].get("host", "")) for agent in agents})
    if len(hosts) < 2:
        raise RuntimeError("deux hôtes distincts requis")

    with (ROOT / args.input).open(encoding="utf-8-sig", newline="") as handle:
        blocks = list(csv.DictReader(handle))

    local = threading.local()

    def coordinator() -> RedisContractNetCoordinator:
        if not hasattr(local, "coordinator"):
            local.coordinator = RedisContractNetCoordinator(
                transport, agents, coordinator_id="sat-coord-" + threading.current_thread().name, response_timeout_sec=5.0
            )
        return local.coordinator

    rows = []
    rows_lock = threading.Lock()
    counter = {"index": 0}

    def negotiate(level_key: str, scheduled: float, block: dict[str, str]) -> None:
        with rows_lock:
            index = counter["index"]
            counter["index"] += 1
        task = AgentTask(
            task_id="{}-{:07d}".format(args.run_id, index),
            task_type="hdfs.block.evaluate",
            payload={
                "block_id": block["block_id"],
                "label": int(block["label"]),
                "mean_score": float(block["mean_score"]),
                "threshold": args.threshold,
                "idempotency_key": "{}-{:07d}".format(args.run_id, index),
            },
        )
        started = time.perf_counter()
        try:
            outcome = coordinator().negotiate(task)
            status, winner = outcome.status, outcome.winner or ""
        except Exception as exc:  # noqa: BLE001 - consigné comme échec
            status, winner = "exception:" + type(exc).__name__, ""
        finished = time.perf_counter()
        with rows_lock:
            rows.append({
                "level": level_key,
                "task_id": task.task_id,
                "status": status,
                "winner": winner,
                "scheduled_rel_sec": round(scheduled, 6),
                "queue_delay_ms": round((started - scheduled_abs[level_key] - scheduled) * 1000.0, 6),
                "latency_ms": round((finished - scheduled_abs[level_key] - scheduled) * 1000.0, 6),
                "finished_rel_sec": round(finished - scheduled_abs[level_key], 6),
            })

    scheduled_abs: dict[str, float] = {}
    levels = []
    block_index = 0
    with ThreadPoolExecutor(max_workers=args.threads, thread_name_prefix="sat") as executor:
        for repetition in range(1, args.repetitions + 1):
            for rate in [float(value) for value in args.rates.split(",")]:
                key = f"r{repetition}_rate{rate:g}"
                count = max(1, int(round(rate * args.window_sec)))
                futures = []
                origin = time.perf_counter()
                scheduled_abs[key] = origin
                for number in range(count):
                    target = number / rate
                    delay = origin + target - time.perf_counter()
                    if delay > 0:
                        time.sleep(delay)
                    futures.append(executor.submit(negotiate, key, target, blocks[block_index % len(blocks)]))
                    block_index += 1
                for future in futures:
                    future.result()
                levels.append({"key": key, "repetition": repetition, "offered_tasks_sec": rate, "submitted": count})
                time.sleep(2.0)

    with (OUT / f"{args.run_id}__saturation_tasks.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda row: row["task_id"]))

    summary_levels = []
    for level in levels:
        subset = [row for row in rows if row["level"] == level["key"]]
        ok = [row for row in subset if row["status"] == "ok"]
        latencies = [row["latency_ms"] for row in ok]
        last_finish = max((row["finished_rel_sec"] for row in ok), default=0.0)
        summary_levels.append({
            **level,
            "completed_ok": len(ok),
            "failed": len(subset) - len(ok),
            "completed_tasks_sec": round(len(ok) / last_finish, 6) if last_finish else 0.0,
            "drain_after_window_sec": round(max(0.0, last_finish - args.window_sec), 6),
            "latency_p50_ms": percentile(latencies, 0.50),
            "latency_p95_ms": percentile(latencies, 0.95),
            "latency_p99_ms": percentile(latencies, 0.99),
            "queue_delay_p95_ms": percentile([row["queue_delay_ms"] for row in ok], 0.95),
            "tasks_by_agent": dict(Counter(row["winner"] for row in ok)),
        })
    payload = {
        "run_id": args.run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "coordinator_host": socket.gethostname(),
        "agents": {agent: {key: registry[agent].get(key) for key in ("host", "os", "python", "profile")} for agent in agents},
        "protocol": {
            "producer": "open_loop, constant rate per window",
            "window_sec": args.window_sec,
            "repetitions": args.repetitions,
            "coordinator_threads": args.threads,
            "task": "hdfs.block.evaluate on frozen HDFS scores (ds_hdfs_block_20260910T081756Z)",
            "latency_origin": "scheduled submission time (includes coordinator-side queueing)",
            "response_timeout_sec_per_phase": 5.0,
            "deviation_from_PROTOCOL_CONFIG": "3 repetitions and rates 1-64 instead of 10 repetitions and 0.5-32, to bound duration",
        },
        "levels": summary_levels,
        "artifacts": [f"revision_reports/agent_3/{args.run_id}__saturation_tasks.csv", f"revision_reports/agent_3/{args.run_id}__saturation_summary.json"],
    }
    (OUT / f"{args.run_id}__saturation_summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["levels"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
