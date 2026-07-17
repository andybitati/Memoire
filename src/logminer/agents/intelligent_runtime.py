"""Noyau d'agents intelligents multi-taches pour Logminer.

Ce module ajoute une couche explicite au-dessus des modules historiques:

- capacites declarees par agent;
- selection autonome des taches selon capacite, priorite et memoire;
- execution concurrente de plusieurs types de taches;
- heartbeat et traces de decision sur le bus;
- memoire locale reutilisable entre cycles.

L'objectif n'est pas de simuler une cognition generale, mais de fournir des
agents logiciels defendables: ils percoivent des taches, choisissent selon une
politique explicite, executent plusieurs competences et apprennent un minimum
de leur historique d'erreurs/succes.
"""

from __future__ import annotations

import json
import socket
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any, Callable, Iterable, Protocol
from uuid import uuid4

from agents.bus import MessageBus


TaskHandler = Callable[["AgentTask", "AgentContext"], dict[str, Any]]


@dataclass(frozen=True)
class AgentCapability:
    """Competence qu'un agent peut annoncer et utiliser."""

    name: str
    task_types: tuple[str, ...]
    max_parallel: int = 1
    cost: float = 1.0
    confidence: float = 1.0
    description: str = ""

    def supports(self, task_type: str) -> bool:
        return task_type in self.task_types or "*" in self.task_types


@dataclass
class AgentTask:
    """Tache transportable entre agents ou workers."""

    task_id: str
    task_type: str
    payload: dict[str, Any] = field(default_factory=dict)
    priority: int = 50
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    deadline_sec: float | None = None
    required_capability: str | None = None
    attempts: int = 0

    @classmethod
    def create(
        cls,
        task_type: str,
        payload: dict[str, Any] | None = None,
        *,
        priority: int = 50,
        required_capability: str | None = None,
        deadline_sec: float | None = None,
    ) -> "AgentTask":
        return cls(
            task_id=uuid4().hex,
            task_type=task_type,
            payload=dict(payload or {}),
            priority=int(priority),
            required_capability=required_capability,
            deadline_sec=deadline_sec,
        )


@dataclass
class TaskResult:
    """Resultat explicable d'une tache."""

    task_id: str
    task_type: str
    agent_id: str
    status: str
    output: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    started_at: str = ""
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    elapsed_sec: float = 0.0
    decision_score: float = 0.0
    decision_reasons: list[str] = field(default_factory=list)


@dataclass
class AgentMemory:
    """Memoire locale simple pour apprendre des executions precedentes."""

    successes_by_type: dict[str, int] = field(default_factory=dict)
    errors_by_type: dict[str, int] = field(default_factory=dict)
    last_errors: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def record(self, result: TaskResult) -> None:
        target = self.successes_by_type if result.status == "ok" else self.errors_by_type
        target[result.task_type] = int(target.get(result.task_type, 0)) + 1
        self.completed_tasks.append(result.task_id)
        self.completed_tasks = self.completed_tasks[-200:]
        if result.error:
            self.last_errors.append(result.error[:300])
            self.last_errors = self.last_errors[-20:]
        self.updated_at = datetime.now(timezone.utc).isoformat()


@dataclass
class AgentContext:
    """Contexte transmis aux handlers de taches."""

    agent_id: str
    run_id: str
    bus: MessageBus | None
    memory: AgentMemory
    workspace: Path


class TaskSource(Protocol):
    """Source abstraite de taches pour agents."""

    def fetch(self, agent: "MultiTaskIntelligentAgent", limit: int) -> list[AgentTask]:
        ...

    def acknowledge(self, task: AgentTask, result: TaskResult) -> None:
        ...


class InMemoryTaskSource:
    """Source locale utile pour tests et demonstrations reproductibles."""

    def __init__(self, tasks: Iterable[AgentTask]):
        self._tasks = list(tasks)
        self._lock = Lock()

    def fetch(self, agent: "MultiTaskIntelligentAgent", limit: int) -> list[AgentTask]:
        with self._lock:
            selected: list[AgentTask] = []
            remaining: list[AgentTask] = []
            for task in self._tasks:
                if len(selected) < limit and agent.can_handle(task):
                    selected.append(task)
                else:
                    remaining.append(task)
            self._tasks = remaining
            return selected

    def acknowledge(self, task: AgentTask, result: TaskResult) -> None:
        return None


class RedisTaskSource:
    """Source de taches basee sur Redis Streams.

    Les taches sont stockees dans un stream dedie. Les champs attendus sont:
    `task_type`, `payload`, `priority`, `required_capability` et `deadline_sec`.
    """

    def __init__(
        self,
        bus: Any,
        *,
        stream: str = "logminer:agent_tasks",
        group: str = "logminer-intelligent-agents",
        consumer: str | None = None,
        block_ms: int = 1000,
        claim_idle_ms: int = 0,
    ):
        self.bus = bus
        self.stream = stream
        self.group = group
        self.consumer = consumer or f"{socket.gethostname()}-agent"
        self.block_ms = int(block_ms)
        self.claim_idle_ms = int(claim_idle_ms)
        self._message_ids: dict[str, str] = {}

    def enqueue(self, task: AgentTask) -> str:
        return str(
            self.bus.client.xadd(
                self.stream,
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "payload": json.dumps(task.payload, ensure_ascii=False),
                    "priority": str(task.priority),
                    "required_capability": task.required_capability or "",
                    "deadline_sec": "" if task.deadline_sec is None else str(task.deadline_sec),
                    "attempts": str(task.attempts),
                    "created_at": task.created_at,
                },
                maxlen=getattr(self.bus, "maxlen", 10000),
                approximate=True,
            )
        )

    def _entries_to_tasks(self, agent: "MultiTaskIntelligentAgent", entries: Iterable[tuple[str, dict[str, str]]]) -> list[AgentTask]:
        tasks: list[AgentTask] = []
        for message_id, fields in entries:
            payload_raw = fields.get("payload") or "{}"
            try:
                payload = json.loads(payload_raw)
            except json.JSONDecodeError:
                payload = {"raw": payload_raw}
            deadline_raw = fields.get("deadline_sec") or ""
            task = AgentTask(
                task_id=fields.get("task_id") or uuid4().hex,
                task_type=fields.get("task_type") or "",
                payload=payload,
                priority=int(fields.get("priority") or 50),
                created_at=fields.get("created_at") or datetime.now(timezone.utc).isoformat(),
                deadline_sec=float(deadline_raw) if deadline_raw else None,
                required_capability=fields.get("required_capability") or None,
                attempts=int(fields.get("attempts") or 0),
            )
            self._message_ids[task.task_id] = message_id
            if agent.can_handle(task):
                tasks.append(task)
        return tasks

    def _claim_stale(self, agent: "MultiTaskIntelligentAgent", limit: int) -> list[AgentTask]:
        if self.claim_idle_ms <= 0:
            return []
        try:
            response = self.bus.client.xautoclaim(
                self.stream,
                self.group,
                self.consumer,
                min_idle_time=max(1, self.claim_idle_ms),
                start_id="0-0",
                count=max(1, limit),
            )
        except Exception:
            return []
        entries = response[1] if isinstance(response, (list, tuple)) and len(response) > 1 else []
        return self._entries_to_tasks(agent, entries)

    def fetch(self, agent: "MultiTaskIntelligentAgent", limit: int) -> list[AgentTask]:
        self.bus.ensure_group(self.group, stream=self.stream, start_id="0")
        claimed = self._claim_stale(agent, limit)
        if claimed:
            return claimed[:limit]

        responses = self.bus.client.xreadgroup(
            groupname=self.group,
            consumername=self.consumer,
            streams={self.stream: ">"},
            count=max(1, limit),
            block=max(0, self.block_ms),
        )
        tasks: list[AgentTask] = []
        for _, entries in responses:
            tasks.extend(self._entries_to_tasks(agent, entries))
        return tasks

    def acknowledge(self, task: AgentTask, result: TaskResult) -> None:
        message_id = self._message_ids.get(task.task_id)
        if message_id:
            self.bus.client.xack(self.stream, self.group, message_id)


class MultiTaskIntelligentAgent:
    """Agent logiciel multi-taches avec politique de decision explicite."""

    def __init__(
        self,
        *,
        agent_id: str,
        capabilities: Iterable[AgentCapability],
        handlers: dict[str, TaskHandler],
        bus: MessageBus | None = None,
        memory_path: str | Path | None = None,
        workspace: str | Path = ".",
        max_parallel_tasks: int | None = None,
    ):
        self.agent_id = agent_id
        self.capabilities = list(capabilities)
        self.handlers = dict(handlers)
        self.bus = bus
        self.workspace = Path(workspace)
        self.memory_path = Path(memory_path) if memory_path else None
        self.memory = self._load_memory()
        self.max_parallel_tasks = max_parallel_tasks or max((cap.max_parallel for cap in self.capabilities), default=1)
        self.run_id = bus.run_id if bus is not None else uuid4().hex

    def _load_memory(self) -> AgentMemory:
        if self.memory_path is None or not self.memory_path.exists():
            return AgentMemory()
        try:
            return AgentMemory(**json.loads(self.memory_path.read_text(encoding="utf-8")))
        except Exception as exc:
            return AgentMemory(last_errors=[f"memory load failed: {exc}"])

    def save_memory(self) -> None:
        if self.memory_path is None:
            return
        self.memory_path.parent.mkdir(parents=True, exist_ok=True)
        self.memory_path.write_text(json.dumps(asdict(self.memory), ensure_ascii=False, indent=2), encoding="utf-8")

    def publish_state(self, message_type: str, payload: dict[str, Any] | None = None, status: str = "ok") -> None:
        if self.bus is None:
            return
        self.bus.publish(
            source=self.agent_id,
            target="supervisor",
            message_type=message_type,
            payload={
                "agent_id": self.agent_id,
                "capabilities": [asdict(capability) for capability in self.capabilities],
                **dict(payload or {}),
            },
            status=status,
        )

    def heartbeat(self) -> None:
        self.publish_state(
            "agent.heartbeat",
            {
                "memory": asdict(self.memory),
                "max_parallel_tasks": self.max_parallel_tasks,
            },
        )

    def can_handle(self, task: AgentTask) -> bool:
        if task.required_capability:
            return any(capability.name == task.required_capability for capability in self.capabilities)
        return any(capability.supports(task.task_type) for capability in self.capabilities)

    def score_task(self, task: AgentTask) -> tuple[float, list[str]]:
        score = float(task.priority)
        reasons = [f"priority={task.priority}"]
        if task.task_id in self.memory.completed_tasks:
            score -= 100.0
            reasons.append("already completed")
        matching = [capability for capability in self.capabilities if capability.supports(task.task_type)]
        if task.required_capability:
            matching = [capability for capability in matching if capability.name == task.required_capability]
        if not matching:
            return -9999.0, ["unsupported task"]
        best = max(matching, key=lambda capability: capability.confidence - capability.cost * 0.05)
        score += best.confidence * 20.0
        score -= best.cost
        reasons.append(f"capability={best.name}")
        reasons.append(f"confidence={best.confidence}")
        errors = self.memory.errors_by_type.get(task.task_type, 0)
        successes = self.memory.successes_by_type.get(task.task_type, 0)
        score += min(successes, 10) * 0.5
        score -= min(errors, 10) * 2.0
        if errors:
            reasons.append(f"historical_errors={errors}")
        if successes:
            reasons.append(f"historical_successes={successes}")
        if task.deadline_sec is not None and task.deadline_sec < 5:
            score += 10.0
            reasons.append("short deadline")
        return score, reasons

    def choose_tasks(self, tasks: Iterable[AgentTask], limit: int | None = None) -> list[tuple[AgentTask, float, list[str]]]:
        scored = [(task, *self.score_task(task)) for task in tasks if self.can_handle(task)]
        scored = [item for item in scored if item[1] > -999]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[: max(1, limit or self.max_parallel_tasks)]

    def execute_task(self, task: AgentTask, score: float = 0.0, reasons: list[str] | None = None) -> TaskResult:
        started = datetime.now(timezone.utc).isoformat()
        timer = perf_counter()
        context = AgentContext(
            agent_id=self.agent_id,
            run_id=self.run_id,
            bus=self.bus,
            memory=self.memory,
            workspace=self.workspace,
        )
        self.publish_state(
            "agent.task.started",
            {"task": asdict(task), "decision_score": score, "decision_reasons": reasons or []},
        )
        try:
            handler = self.handlers[task.task_type]
            output = handler(task, context)
            result = TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                agent_id=self.agent_id,
                status="ok",
                output=output,
                started_at=started,
                elapsed_sec=round(perf_counter() - timer, 4),
                decision_score=score,
                decision_reasons=list(reasons or []),
            )
        except Exception as exc:
            result = TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                agent_id=self.agent_id,
                status="error",
                error=str(exc),
                started_at=started,
                elapsed_sec=round(perf_counter() - timer, 4),
                decision_score=score,
                decision_reasons=list(reasons or []),
            )
        self.memory.record(result)
        self.save_memory()
        self.publish_state(
            "agent.task.completed" if result.status == "ok" else "agent.task.failed",
            {"result": asdict(result)},
            status=result.status,
        )
        return result

    def run_once(self, source: TaskSource, *, fetch_limit: int | None = None) -> list[TaskResult]:
        self.heartbeat()
        tasks = source.fetch(self, limit=fetch_limit or self.max_parallel_tasks)
        selected = self.choose_tasks(tasks, limit=self.max_parallel_tasks)
        if not selected:
            self.publish_state("agent.idle", {"fetched": len(tasks)})
            return []
        results: list[TaskResult] = []
        with ThreadPoolExecutor(max_workers=max(1, self.max_parallel_tasks), thread_name_prefix=self.agent_id) as executor:
            futures = {
                executor.submit(self.execute_task, task, score, reasons): task
                for task, score, reasons in selected
            }
            for future in as_completed(futures):
                task = futures[future]
                result = future.result()
                source.acknowledge(task, result)
                results.append(result)
        return results
