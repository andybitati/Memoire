"""Worker d'agents intelligents multi-taches sur Redis Streams.

Ce script permet de lancer plusieurs agents dans des processus differents.
Ils consomment le meme stream Redis, publient heartbeat/decisions et se
repartissent les taches selon leurs capacites.
"""

from __future__ import annotations

import argparse
import json
import socket
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = REPO_ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.bus import RedisMessageBus
from agents.intelligent_runtime import (
    AgentCapability,
    AgentTask,
    MultiTaskIntelligentAgent,
    RedisTaskSource,
)
from run_intelligent_agents_demo import (
    correlate_handler,
    detect_handler,
    discover_handler,
    parse_handler,
    route_handler,
)


def build_redis_agent(
    *,
    agent_id: str,
    bus: RedisMessageBus,
    memory_path: Path,
    max_parallel_tasks: int,
) -> MultiTaskIntelligentAgent:
    capabilities = [
        AgentCapability("perception", ("discover.logs",), max_parallel=2, confidence=0.95),
        AgentCapability("parser", ("parse.logs",), max_parallel=2, confidence=0.9),
        AgentCapability("router", ("route.model",), max_parallel=4, confidence=0.95),
        AgentCapability("detector", ("detect.anomalies",), max_parallel=2, confidence=0.85),
        AgentCapability("correlator", ("correlate.incidents",), max_parallel=2, confidence=0.85),
    ]
    handlers = {
        "discover.logs": discover_handler,
        "parse.logs": parse_handler,
        "route.model": route_handler,
        "detect.anomalies": detect_handler,
        "correlate.incidents": correlate_handler,
    }
    return MultiTaskIntelligentAgent(
        agent_id=agent_id,
        capabilities=capabilities,
        handlers=handlers,
        bus=bus,
        memory_path=memory_path,
        workspace=REPO_ROOT,
        max_parallel_tasks=max_parallel_tasks,
    )


def enqueue_demo_tasks(source: RedisTaskSource, input_path: str) -> list[str]:
    tasks = [
        AgentTask.create("discover.logs", {"roots": ["examples", "data/samples", "data/processed"], "max_files": 10}, priority=40),
        AgentTask.create("parse.logs", {"input_path": input_path, "out_name": "redis_intelligent_demo_parsed.csv"}, priority=90),
        AgentTask.create("route.model", {"input_path": input_path, "sample_rows": 200}, priority=70),
    ]
    return [source.enqueue(task) for task in tasks]


def main() -> int:
    parser = argparse.ArgumentParser(description="Worker Redis d'agents intelligents multi-taches")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--event-stream", default="logminer:events")
    parser.add_argument("--task-stream", default="logminer:agent_tasks")
    parser.add_argument("--group", default="logminer-intelligent-agents")
    parser.add_argument("--consumer", default=None)
    parser.add_argument("--agent-id", default=None)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--memory", default="data/processed/intelligent_redis_agent_memory.json")
    parser.add_argument("--max-parallel-tasks", type=int, default=3)
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--block-ms", type=int, default=1000)
    parser.add_argument("--claim-idle-ms", type=int, default=0)
    parser.add_argument("--crash-after-fetch", action="store_true")
    parser.add_argument("--enqueue-demo", action="store_true")
    parser.add_argument("--demo-input", default="examples/windows_event_sample.xml")
    args = parser.parse_args()

    run_id = args.run_id or f"redis-intelligent-{socket.gethostname()}"
    bus = RedisMessageBus(url=args.redis_url, stream=args.event_stream, run_id=run_id)
    consumer = args.consumer or f"{socket.gethostname()}-{Path(sys.argv[0]).stem}"
    source = RedisTaskSource(
        bus,
        stream=args.task_stream,
        group=args.group,
        consumer=consumer,
        block_ms=args.block_ms,
        claim_idle_ms=args.claim_idle_ms,
    )
    if args.enqueue_demo:
        message_ids = enqueue_demo_tasks(source, args.demo_input)
        print(json.dumps({"enqueued": message_ids, "task_stream": args.task_stream}, ensure_ascii=False, indent=2))

    agent = build_redis_agent(
        agent_id=args.agent_id or consumer,
        bus=bus,
        memory_path=REPO_ROOT / args.memory,
        max_parallel_tasks=args.max_parallel_tasks,
    )
    if args.crash_after_fetch:
        fetched = source.fetch(agent, limit=1)
        agent.publish_state(
            "agent.simulated_crash",
            {"fetched_tasks": [asdict(task) for task in fetched], "reason": "crash_after_fetch_before_ack"},
            status="error",
        )
        print(json.dumps({"simulated_crash": True, "fetched": [asdict(task) for task in fetched]}, ensure_ascii=False, indent=2))
        return 2 if fetched else 0

    all_results = []
    for _ in range(max(1, args.cycles)):
        all_results.extend(agent.run_once(source))
    print(json.dumps([asdict(result) for result in all_results], ensure_ascii=False, indent=2))
    return 0 if all(result.status == "ok" for result in all_results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
