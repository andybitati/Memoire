from __future__ import annotations

import argparse
import csv
import json
import socket
import sys
import time
from collections import Counter
from pathlib import Path
from statistics import fmean, median

ROOT = Path(__file__).resolve().parents[2]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus
from agents.intelligent_runtime import AgentTask
from agents.redis_contract_net import RedisContractNetCoordinator, RedisContractNetTransport


def percentile(values, quantile):
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * quantile
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--redis-url", default="redis://127.0.0.1:6379/0")
    parser.add_argument("--agents", default="debian-alpha,ubuntu-beta")
    parser.add_argument("--input", default="experiments/phase_final_scientific_consolidation/processed/hdfs_test_block_frozen_mean_scores.csv")
    parser.add_argument("--threshold", type=float, default=1.2729429339548877)
    parser.add_argument("--registry-timeout-sec", type=float, default=120.0)
    args = parser.parse_args()

    output_dir = ROOT / "revision_reports" / "agent_3"
    summary_path = output_dir / (args.run_id + "__hdfs_multivm_summary.json")
    tasks_path = output_dir / (args.run_id + "__hdfs_multivm_tasks.csv")
    if summary_path.exists() or tasks_path.exists():
        raise FileExistsError("run_id déjà utilisé")

    agents = [item.strip() for item in args.agents.split(",") if item.strip()]
    namespace = "logminer:cnp:" + args.run_id
    event_stream = "logminer:events:" + args.run_id
    bus = RedisMessageBus(url=args.redis_url, stream=event_stream, run_id=args.run_id, maxlen=250000)
    transport = RedisContractNetTransport(bus, namespace=namespace, run_id=args.run_id)
    deadline = time.monotonic() + args.registry_timeout_sec
    registry = {}
    while time.monotonic() < deadline:
        registry = transport.registered_agents()
        if all(agent in registry for agent in agents):
            break
        time.sleep(0.25)
    if not all(agent in registry for agent in agents):
        raise RuntimeError("registre incomplet: " + repr(sorted(registry)))
    hosts = {str(registry[agent].get("host", "")) for agent in agents}
    if len(hosts) < 2:
        raise RuntimeError("deux hôtes distincts requis: " + repr(sorted(hosts)))

    with (ROOT / args.input).open("r", encoding="utf-8-sig", newline="") as handle:
        blocks = list(csv.DictReader(handle))
    coordinator = RedisContractNetCoordinator(transport, agents, response_timeout_sec=5.0)
    rows = []
    latencies = []
    by_agent = Counter()
    started = time.perf_counter()
    for index, block in enumerate(blocks):
        outcome = coordinator.negotiate(
            AgentTask(
                task_id="{}-block-{:07d}".format(args.run_id, index),
                task_type="hdfs.block.evaluate",
                payload={
                    "block_id": block["block_id"],
                    "label": int(block["label"]),
                    "mean_score": float(block["mean_score"]),
                    "threshold": args.threshold,
                    "idempotency_key": "{}-block-{}".format(args.run_id, block["block_id"]),
                },
            )
        )
        result = outcome.result.output if outcome.result else {}
        latency_ms = outcome.elapsed_sec * 1000.0
        latencies.append(latency_ms)
        by_agent[str(result.get("agent_id") or outcome.winner)] += int(outcome.status == "ok")
        rows.append({
            "run_id": args.run_id,
            "task_id": outcome.task_id,
            "block_id": block["block_id"],
            "label": int(block["label"]),
            "mean_score": float(block["mean_score"]),
            "prediction": result.get("prediction", ""),
            "winner": outcome.winner or "",
            "result_agent": result.get("agent_id", ""),
            "result_host": result.get("host", ""),
            "status": outcome.status,
            "latency_ms": round(latency_ms, 6),
            "reassignments": outcome.reassignments,
            "proposals_json": json.dumps(outcome.proposals, sort_keys=True),
        })
    elapsed = time.perf_counter() - started
    with tasks_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    valid = [row for row in rows if row["status"] == "ok" and row["prediction"] != ""]
    tp = sum(row["label"] == 1 and int(row["prediction"]) == 1 for row in valid)
    fp = sum(row["label"] == 0 and int(row["prediction"]) == 1 for row in valid)
    tn = sum(row["label"] == 0 and int(row["prediction"]) == 0 for row in valid)
    fn = sum(row["label"] == 1 and int(row["prediction"]) == 0 for row in valid)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    summary = {
        "run_id": args.run_id,
        "status": "COMPLETED" if len(valid) == len(blocks) else "FAILED",
        "source_run_id": "ds_hdfs_block_20260910T081756Z",
        "input": args.input,
        "coordinator_host": socket.gethostname(),
        "redis_url": args.redis_url,
        "agents": {agent: registry[agent] for agent in agents},
        "distinct_agent_hosts": sorted(hosts),
        "blocks": len(blocks),
        "successful_blocks": len(valid),
        "duration_sec": round(elapsed, 6),
        "throughput_blocks_sec": round(len(valid) / elapsed, 6),
        "latency_mean_ms": round(fmean(latencies), 6),
        "latency_median_ms": round(median(latencies), 6),
        "latency_p95_ms": round(percentile(latencies, 0.95), 6),
        "latency_p99_ms": round(percentile(latencies, 0.99), 6),
        "tasks_by_agent": dict(by_agent),
        "threshold": args.threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "scope": "transport et décision distribués sur des scores HDFS figés; calcul des scores non rejoué dans les VM",
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0 if summary["status"] == "COMPLETED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
