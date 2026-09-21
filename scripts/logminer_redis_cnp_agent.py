"""Processus agent autonome répondant aux contrats via Redis Streams."""

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


TASK_TYPES = ("parse.synthetic", "route.synthetic", "detect.synthetic", "correlate.synthetic")
PROFILES = {
    "alpha": (0.95, 0.82, 0.70, 0.72),
    "beta": (0.78, 0.96, 0.88, 0.82),
    "gamma": (0.70, 0.76, 0.97, 0.96),
}


def synthetic_effect(task: AgentTask, context) -> dict[str, object]:
    checksum = 0
    for index, value in enumerate(task.payload.get("values", [])):
        checksum = (checksum + (index + 17) * int(value) * int(value)) % 1_000_003
    output: dict[str, object] = {
        "checksum": checksum,
        "agent_id": context.agent_id,
        "pid": os.getpid(),
        "host": socket.gethostname(),
    }
    counter_key = str(task.payload.get("effect_counter_key") or "")
    if counter_key and context.bus is not None:
        output["effect_number"] = int(context.bus.client.incr(counter_key))
    return output


def build_agent(args: argparse.Namespace, bus: RedisMessageBus) -> MultiTaskIntelligentAgent:
    confidences = PROFILES[args.profile]
    disabled = {item.strip() for item in args.disable_task_types.split(",") if item.strip()}
    fail_once = {item.strip() for item in args.fail_once_task_types.split(",") if item.strip()}
    failed_once: set[str] = set()

    def controlled_handler(task: AgentTask, context) -> dict[str, object]:
        if task.task_type in fail_once and task.task_type not in failed_once:
            failed_once.add(task.task_type)
            raise RuntimeError(f"controlled_failure_once:{task.task_type}")
        return synthetic_effect(task, context)

    capabilities = [
        AgentCapability(
            name=f"{args.agent_id}-{task_type}",
            task_types=(task_type,),
            max_parallel=1,
            confidence=confidence,
        )
        for task_type, confidence in zip(TASK_TYPES, confidences)
        if task_type not in disabled
    ]
    store = RedisIdempotencyStore(bus.client, namespace=f"{args.namespace}:idempotency")
    return MultiTaskIntelligentAgent(
        agent_id=args.agent_id,
        capabilities=capabilities,
        handlers={task_type: controlled_handler for task_type in TASK_TYPES if task_type not in disabled},
        bus=bus,
        max_parallel_tasks=1,
        memory_enabled=args.memory == "on",
        idempotency_store=store,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent Logminer CNP inter-processus sur Redis")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--event-stream", default="logminer:events")
    parser.add_argument("--event-stream-maxlen", type=int, default=250_000)
    parser.add_argument("--namespace", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--profile", choices=sorted(PROFILES), required=True)
    parser.add_argument("--memory", choices=("on", "off"), default="on")
    parser.add_argument("--disable-task-types", default="")
    parser.add_argument("--fail-once-task-types", default="")
    parser.add_argument(
        "--crash-after-persisted-result-once",
        action="store_true",
        help=(
            "Interrompt volontairement le processus une fois, apres persistance "
            "du resultat idempotent et avant emission du message RESULT, lorsque "
            "le payload porte crash_after_persisted_result=true."
        ),
    )
    parser.add_argument("--idle-timeout-sec", type=float, default=15.0)
    args = parser.parse_args()

    bus = RedisMessageBus(
        url=args.redis_url,
        stream=args.event_stream,
        run_id=args.run_id,
        maxlen=args.event_stream_maxlen,
    )
    if not bus.ping():
        raise RuntimeError("Redis ne répond pas")
    transport = RedisContractNetTransport(bus, namespace=args.namespace, run_id=args.run_id)
    agent = build_agent(args, bus)
    transport.register(
        args.agent_id,
        {
            "pid": os.getpid(),
            "host": socket.gethostname(),
            "os": platform.platform(),
            "python": sys.version,
            "profile": args.profile,
            "perception": asdict(agent.perceive()),
        },
    )
    agent.heartbeat()
    inbox = transport.inbox(args.agent_id)
    cursor = transport.latest_id(inbox)
    pending: dict[str, tuple[AgentTask, object]] = {}
    completed = 0
    crash_injected = False
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
                if (
                    args.crash_after_persisted_result_once
                    and not crash_injected
                    and result.status == "ok"
                    and bool(task.payload.get("crash_after_persisted_result"))
                ):
                    crash_injected = True
                    print(
                        json.dumps(
                            {
                                "event": "controlled_crash_after_persisted_result",
                                "run_id": args.run_id,
                                "agent_id": args.agent_id,
                                "task_id": task.task_id,
                                "pid": os.getpid(),
                            },
                            ensure_ascii=False,
                        ),
                        flush=True,
                    )
                    os._exit(91)
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

    summary = {
        "run_id": args.run_id,
        "agent_id": args.agent_id,
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "completed": completed,
        "memory": args.memory,
        "status": "ok",
    }
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
