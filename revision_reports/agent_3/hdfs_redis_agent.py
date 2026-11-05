from __future__ import annotations

import argparse
import json
import os
import platform
import socket
import sys
import time
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus
from agents.idempotency import RedisIdempotencyStore
from agents.intelligent_runtime import AgentCapability, AgentTask, MultiTaskIntelligentAgent
from agents.redis_contract_net import RedisContractNetTransport


def evaluate_block(task, context):
    score = float(task.payload["mean_score"])
    threshold = float(task.payload["threshold"])
    return {
        "block_id": str(task.payload["block_id"]),
        "label": int(task.payload["label"]),
        "prediction": int(score >= threshold),
        "mean_score": score,
        "agent_id": context.agent_id,
        "pid": os.getpid(),
        "host": socket.gethostname(),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis-url", required=True)
    parser.add_argument("--event-stream", required=True)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--idle-timeout-sec", type=float, default=900.0)
    args = parser.parse_args()

    bus = RedisMessageBus(url=args.redis_url, stream=args.event_stream, run_id=args.run_id, maxlen=250000)
    if not bus.ping():
        raise RuntimeError("Redis ne répond pas")
    transport = RedisContractNetTransport(bus, namespace=args.namespace, run_id=args.run_id)
    agent = MultiTaskIntelligentAgent(
        agent_id=args.agent_id,
        capabilities=[AgentCapability("hdfs-block", ("hdfs.block.evaluate",), confidence=0.9)],
        handlers={"hdfs.block.evaluate": evaluate_block},
        bus=bus,
        max_parallel_tasks=1,
        memory_enabled=False,
        idempotency_store=RedisIdempotencyStore(bus.client, namespace=args.namespace + ":idempotency"),
    )
    transport.register(
        args.agent_id,
        {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "os": platform.platform(),
            "python": sys.version,
            "profile": "hdfs-equal-confidence",
            "perception": asdict(agent.perceive()),
        },
    )
    agent.heartbeat()
    inbox = transport.inbox(args.agent_id)
    cursor = transport.latest_id(inbox)
    pending = {}
    completed = 0
    last_activity = time.monotonic()
    while time.monotonic() - last_activity < args.idle_timeout_sec:
        cursor, messages = transport.read(inbox, cursor, block_ms=500, count=100)
        if not messages:
            continue
        last_activity = time.monotonic()
        for message in messages:
            contract_id = str(message.payload.get("contract_id") or "")
            if message.message_type == "CFP":
                task = AgentTask(**message.payload["task"])
                evaluation = agent.propose(task)
                pending[contract_id] = (task, evaluation)
                transport.send_response(
                    source=args.agent_id,
                    target=message.source,
                    message_type="PROPOSE" if evaluation.accepted else "REFUSE",
                    payload={
                        "contract_id": contract_id,
                        "task_id": task.task_id,
                        "utility": evaluation.utility,
                        "components": evaluation.components,
                        "reasons": list(evaluation.reasons),
                        "refusal_reason": evaluation.refusal_reason,
                        "pid": os.getpid(),
                        "host": socket.gethostname(),
                    },
                    status="ok" if evaluation.accepted else "refused",
                )
            elif message.message_type == "AWARD":
                item = pending.get(contract_id)
                if item is None:
                    continue
                task, evaluation = item
                if not agent.accept(task):
                    transport.send_response(
                        source=args.agent_id,
                        target=message.source,
                        message_type="REFUSE",
                        payload={"contract_id": contract_id, "task_id": task.task_id, "refusal_reason": "agent_overloaded"},
                        status="refused",
                    )
                    continue
                transport.send_response(
                    source=args.agent_id,
                    target=message.source,
                    message_type="ACCEPT",
                    payload={"contract_id": contract_id, "task_id": task.task_id, "pid": os.getpid()},
                )
                result = agent.execute_task(task, evaluation.utility, list(evaluation.reasons))
                transport.send_response(
                    source=args.agent_id,
                    target=message.source,
                    message_type="RESULT" if result.status == "ok" else "FAIL",
                    payload={"contract_id": contract_id, "result": asdict(result), "pid": os.getpid()},
                    status=result.status,
                )
                completed += int(result.status == "ok")
            elif message.message_type in {"REJECT", "FEEDBACK"}:
                pending.pop(contract_id, None)
    print(json.dumps({"run_id": args.run_id, "agent_id": args.agent_id, "completed": completed, "status": "ok"}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
