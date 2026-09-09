"""Transport Contract Net inter-processus fondé sur Redis Streams."""

from __future__ import annotations

import json
import time
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

try:
    from .bus import AgentMessage, RedisMessageBus
    from .contract_net import CNP_MESSAGE_TYPES, NegotiationResult
    from .intelligent_runtime import AgentTask, TaskResult
except ImportError:  # pragma: no cover
    from agents.bus import AgentMessage, RedisMessageBus
    from agents.contract_net import CNP_MESSAGE_TYPES, NegotiationResult
    from agents.intelligent_runtime import AgentTask, TaskResult


def _message_fields(message: AgentMessage) -> dict[str, str]:
    return {
        "run_id": message.run_id,
        "source": message.source,
        "target": message.target,
        "message_type": message.message_type,
        "payload": json.dumps(message.payload, ensure_ascii=False),
        "status": message.status,
        "timestamp": message.timestamp,
    }


def _decode_message(fields: dict[str, Any]) -> AgentMessage:
    payload_raw = fields.get("payload") or "{}"
    if isinstance(payload_raw, bytes):
        payload_raw = payload_raw.decode("utf-8")
    return AgentMessage(
        run_id=str(fields.get("run_id", "")),
        source=str(fields.get("source", "")),
        target=str(fields.get("target", "")),
        message_type=str(fields.get("message_type", "")),
        payload=json.loads(payload_raw),
        status=str(fields.get("status", "ok")),
        timestamp=str(fields.get("timestamp", "")),
    )


class RedisContractNetTransport:
    """Boîtes dédiées par agent et flux de réponses partagé par run."""

    def __init__(self, bus: RedisMessageBus, *, namespace: str, run_id: str):
        self.bus = bus
        self.client = bus.client
        self.namespace = namespace.rstrip(":")
        self.run_id = run_id
        self.response_stream = f"{self.namespace}:responses"
        self.registry_key = f"{self.namespace}:registry"

    def inbox(self, agent_id: str) -> str:
        return f"{self.namespace}:inbox:{agent_id}"

    def _send(self, stream: str, *, source: str, target: str, message_type: str, payload: dict[str, Any], status: str) -> AgentMessage:
        message = AgentMessage(
            run_id=self.run_id,
            source=source,
            target=target,
            message_type=message_type,
            payload=dict(payload),
            status=status,
        )
        self.client.xadd(stream, _message_fields(message))
        self.bus.publish(source, target, message_type, payload, status)
        return message

    def send_to_agent(
        self,
        agent_id: str,
        *,
        source: str,
        message_type: str,
        payload: dict[str, Any],
        status: str = "ok",
    ) -> AgentMessage:
        return self._send(
            self.inbox(agent_id),
            source=source,
            target=agent_id,
            message_type=message_type,
            payload=payload,
            status=status,
        )

    def send_response(
        self,
        *,
        source: str,
        target: str,
        message_type: str,
        payload: dict[str, Any],
        status: str = "ok",
    ) -> AgentMessage:
        return self._send(
            self.response_stream,
            source=source,
            target=target,
            message_type=message_type,
            payload=payload,
            status=status,
        )

    def read(self, stream: str, cursor: str, *, block_ms: int = 1000, count: int = 100) -> tuple[str, list[AgentMessage]]:
        responses = self.client.xread({stream: cursor}, count=max(1, count), block=max(0, block_ms))
        messages: list[AgentMessage] = []
        latest = cursor
        for _, entries in responses:
            for message_id, fields in entries:
                latest = str(message_id)
                message = _decode_message(fields)
                if message.run_id == self.run_id:
                    messages.append(message)
        return latest, messages

    def latest_id(self, stream: str) -> str:
        entries = self.client.xrevrange(stream, count=1)
        return str(entries[0][0]) if entries else "0-0"

    def register(self, agent_id: str, payload: dict[str, Any]) -> None:
        record = {"agent_id": agent_id, "run_id": self.run_id, "updated_at": datetime.now(timezone.utc).isoformat(), **payload}
        self.client.hset(self.registry_key, agent_id, json.dumps(record, ensure_ascii=False))

    def registered_agents(self) -> dict[str, dict[str, Any]]:
        records = {}
        for agent_id, raw in self.client.hgetall(self.registry_key).items():
            records[str(agent_id)] = json.loads(raw)
        return records


class RedisContractNetCoordinator:
    """Coordinateur CNP utilisant uniquement des réponses émises par les processus agents."""

    def __init__(
        self,
        transport: RedisContractNetTransport,
        agent_ids: Iterable[str],
        *,
        coordinator_id: str = "redis-cnp-coordinator",
        response_timeout_sec: float = 10.0,
    ):
        self.transport = transport
        self.agent_ids = sorted(set(agent_ids))
        self.coordinator_id = coordinator_id
        self.response_timeout_sec = response_timeout_sec
        self.response_cursor = transport.latest_id(transport.response_stream)
        self.counts: Counter[str] = Counter()

    def _send(self, agent_id: str, message_type: str, payload: dict[str, Any], status: str = "ok") -> None:
        self.transport.send_to_agent(
            agent_id,
            source=self.coordinator_id,
            message_type=message_type,
            payload=payload,
            status=status,
        )
        self.counts[message_type] += 1

    def _collect(
        self,
        contract_id: str,
        expected_sources: set[str],
        terminal_types: set[str],
        *,
        required_any_type: set[str] | None = None,
    ) -> list[AgentMessage]:
        deadline = time.monotonic() + self.response_timeout_sec
        collected: list[AgentMessage] = []
        seen: set[tuple[str, str]] = set()
        while time.monotonic() < deadline:
            remaining_ms = max(1, int((deadline - time.monotonic()) * 1000))
            self.response_cursor, messages = self.transport.read(
                self.transport.response_stream,
                self.response_cursor,
                block_ms=min(1000, remaining_ms),
            )
            for message in messages:
                if message.payload.get("contract_id") != contract_id or message.message_type not in terminal_types:
                    continue
                key = (message.source, message.message_type)
                if key in seen:
                    continue
                seen.add(key)
                collected.append(message)
                self.counts[message.message_type] += 1
            sources_complete = expected_sources.issubset({message.source for message in collected})
            terminal_complete = not required_any_type or any(
                message.message_type in required_any_type for message in collected
            )
            if sources_complete and terminal_complete:
                break
        return collected

    def negotiate(self, task: AgentTask) -> NegotiationResult:
        started = time.perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()
        contract_id = uuid4().hex
        cfp_payload = {"contract_id": contract_id, "task": asdict(task)}
        for agent_id in self.agent_ids:
            self._send(agent_id, "CFP", cfp_payload)

        responses = self._collect(contract_id, set(self.agent_ids), {"PROPOSE", "REFUSE"})
        proposals = {
            message.source: float(message.payload.get("utility", 0.0))
            for message in responses
            if message.message_type == "PROPOSE"
        }
        refusals = {
            message.source: str(message.payload.get("refusal_reason", ""))
            for message in responses
            if message.message_type == "REFUSE"
        }
        if not proposals:
            return NegotiationResult(
                contract_id=contract_id,
                task_id=task.task_id,
                status="error",
                refusals=refusals,
                message_counts={name: int(self.counts.get(name, 0)) for name in CNP_MESSAGE_TYPES},
                started_at=started_at,
                completed_at=datetime.now(timezone.utc).isoformat(),
                elapsed_sec=round(time.perf_counter() - started, 6),
            )

        ranking = sorted(proposals, key=lambda agent_id: (-proposals[agent_id], agent_id))
        winner = ""
        result = None
        reassignments = 0
        attempted: list[str] = []
        for candidate in ranking:
            winner = candidate
            attempted.append(candidate)
            self._send(candidate, "AWARD", {"contract_id": contract_id, "task_id": task.task_id, "utility": proposals[candidate]})
            terminal = self._collect(
                contract_id,
                {candidate},
                {"ACCEPT", "RESULT", "FAIL"},
                required_any_type={"RESULT", "FAIL"},
            )
            result_messages = [message for message in terminal if message.message_type in {"RESULT", "FAIL"}]
            candidate_result = None
            if result_messages:
                result_payload = result_messages[-1].payload.get("result") or {}
                candidate_result = TaskResult(**result_payload)
            if candidate_result is not None and candidate_result.status == "ok":
                result = candidate_result
                break
            self._send(
                candidate,
                "FEEDBACK",
                {"contract_id": contract_id, "task_id": task.task_id, "outcome": "error"},
                "error",
            )
            if candidate != ranking[-1]:
                reassignments += 1

        status = "ok" if result is not None else "error"
        for agent_id in ranking:
            if agent_id not in attempted:
                self._send(
                    agent_id,
                    "REJECT",
                    {"contract_id": contract_id, "task_id": task.task_id, "winner": winner},
                    "rejected",
                )
        if status == "ok":
            self._send(
                winner,
                "FEEDBACK",
                {"contract_id": contract_id, "task_id": task.task_id, "outcome": status},
                status,
            )
        return NegotiationResult(
            contract_id=contract_id,
            task_id=task.task_id,
            status=status,
            winner=winner,
            proposals=proposals,
            refusals=refusals,
            result=result,
            reassignments=reassignments,
            message_counts={name: int(self.counts.get(name, 0)) for name in CNP_MESSAGE_TYPES},
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            elapsed_sec=round(time.perf_counter() - started, 6),
        )
