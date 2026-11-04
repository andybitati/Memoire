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

try:
    from .bus import MessageBus
    from .idempotency import SQLiteIdempotencyStore
except ImportError:  # pragma: no cover - compatibility with direct script execution
    from agents.bus import MessageBus
    from agents.idempotency import SQLiteIdempotencyStore


TaskHandler = Callable[["AgentTask", "AgentContext"], Any]


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


@dataclass(frozen=True)
class AgentPolicyWeights:
    """Poids configurables du score d'utilité local, sans prétention d'optimalité."""

    capability: float = 0.30
    history: float = 0.20
    model: float = 0.20
    availability: float = 0.15
    load: float = 0.10
    latency: float = 0.05

    def __post_init__(self) -> None:
        values = asdict(self)
        if any(float(value) < 0.0 for value in values.values()):
            raise ValueError("Les poids de politique doivent être positifs ou nuls")
        if abs(sum(float(value) for value in values.values()) - 1.0) > 1e-9:
            raise ValueError("La somme des poids de politique doit être égale à 1")

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "AgentPolicyWeights":
        if not values:
            return cls()
        return cls(**{field_name: float(values[field_name]) for field_name in asdict(cls()) if field_name in values})


@dataclass(frozen=True)
class AgentPerception:
    """Instantané local utilisé pour évaluer un appel à propositions."""

    agent_id: str
    healthy: bool
    active_tasks: int
    max_parallel_tasks: int
    load_ratio: float
    available_models: tuple[str, ...]
    available_dependencies: tuple[str, ...]
    memory_enabled: bool
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True)
class BidEvaluation:
    """Décision locale normalisée produite pour une tâche."""

    task_id: str
    agent_id: str
    accepted: bool
    utility: float
    components: dict[str, float]
    reasons: tuple[str, ...]
    refusal_reason: str = ""


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
class ActionOutcome:
    """Résultat d'un handler pouvant orienter la suite d'un objectif.

    Les handlers historiques peuvent continuer à retourner un dictionnaire.
    Ce contrat enrichi est réservé aux handlers qui souhaitent produire des
    sous-tâches ou terminer explicitement l'objectif courant.
    """

    output: dict[str, Any] = field(default_factory=dict)
    next_tasks: list[AgentTask] = field(default_factory=list)
    goal_completed: bool = False
    retry_current_task: bool = False
    notes: list[str] = field(default_factory=list)

    def control_payload(self) -> dict[str, Any]:
        return {
            "next_tasks": [asdict(task) for task in self.next_tasks],
            "goal_completed": bool(self.goal_completed),
            "retry_current_task": bool(self.retry_current_task),
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class AutonomyLimits:
    """Garde-fous d'une boucle autonome locale."""

    max_actions: int = 20
    max_depth: int = 5
    max_attempts_per_task: int = 2
    max_pending_tasks: int = 100

    def __post_init__(self) -> None:
        if min(
            self.max_actions,
            self.max_attempts_per_task,
            self.max_pending_tasks,
        ) < 1:
            raise ValueError("Les budgets d'autonomie doivent être supérieurs ou égaux à 1")
        if self.max_depth < 0:
            raise ValueError("La profondeur autonome doit être positive ou nulle")


@dataclass
class GoalState:
    """État persistant et borné d'un objectif poursuivi par un agent."""

    goal_id: str
    objective: str
    status: str = "pending"
    actions_executed: int = 0
    max_actions: int = 20
    max_depth: int = 5
    max_attempts_per_task: int = 2
    max_pending_tasks: int = 100
    pending_tasks: list[dict[str, Any]] = field(default_factory=list)
    completed_task_ids: list[str] = field(default_factory=list)
    failed_task_ids: list[str] = field(default_factory=list)
    delegated_task_ids: list[str] = field(default_factory=list)
    task_results: list[dict[str, Any]] = field(default_factory=list)
    last_error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @classmethod
    def create(
        cls,
        objective: str,
        tasks: Iterable[AgentTask],
        *,
        limits: AutonomyLimits | None = None,
        goal_id: str | None = None,
    ) -> "GoalState":
        bounds = limits or AutonomyLimits()
        return cls(
            goal_id=goal_id or uuid4().hex,
            objective=str(objective),
            max_actions=bounds.max_actions,
            max_depth=bounds.max_depth,
            max_attempts_per_task=bounds.max_attempts_per_task,
            max_pending_tasks=bounds.max_pending_tasks,
            pending_tasks=[asdict(task) for task in tasks],
        )

    @classmethod
    def from_mapping(cls, values: dict[str, Any]) -> "GoalState":
        return cls(**dict(values))

    @property
    def terminal(self) -> bool:
        return self.status in {"completed", "failed", "blocked", "budget_exhausted"}


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
    control: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMemory:
    """Memoire locale simple pour apprendre des executions precedentes."""

    successes_by_type: dict[str, int] = field(default_factory=dict)
    errors_by_type: dict[str, int] = field(default_factory=dict)
    durations_by_type: dict[str, list[float]] = field(default_factory=dict)
    last_errors: list[str] = field(default_factory=list)
    completed_tasks: list[str] = field(default_factory=list)
    recent_task_types: list[str] = field(default_factory=list)
    last_decisions: list[dict[str, Any]] = field(default_factory=list)
    goals: dict[str, dict[str, Any]] = field(default_factory=dict)
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def record(self, result: TaskResult) -> None:
        target = self.successes_by_type if result.status == "ok" else self.errors_by_type
        target[result.task_type] = int(target.get(result.task_type, 0)) + 1
        durations = self.durations_by_type.setdefault(result.task_type, [])
        durations.append(float(result.elapsed_sec))
        self.durations_by_type[result.task_type] = durations[-50:]
        self.completed_tasks.append(result.task_id)
        self.completed_tasks = self.completed_tasks[-200:]
        self.recent_task_types.append(result.task_type)
        self.recent_task_types = self.recent_task_types[-50:]
        self.last_decisions.append(
            {
                "task_id": result.task_id,
                "task_type": result.task_type,
                "status": result.status,
                "score": result.decision_score,
                "reasons": result.decision_reasons,
                "elapsed_sec": result.elapsed_sec,
                "completed_at": result.completed_at,
            }
        )
        self.last_decisions = self.last_decisions[-50:]
        if result.error:
            self.last_errors.append(result.error[:300])
            self.last_errors = self.last_errors[-20:]
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def reliability(self, task_type: str) -> float:
        successes = float(self.successes_by_type.get(task_type, 0))
        errors = float(self.errors_by_type.get(task_type, 0))
        return (successes + 1.0) / (successes + errors + 2.0)

    def average_duration(self, task_type: str) -> float | None:
        durations = self.durations_by_type.get(task_type) or []
        if not durations:
            return None
        return sum(durations) / len(durations)


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
            if hasattr(self.bus.client, "xautoclaim"):
                response = self.bus.client.xautoclaim(
                    self.stream,
                    self.group,
                    self.consumer,
                    min_idle_time=max(1, self.claim_idle_ms),
                    start_id="0-0",
                    count=max(1, limit),
                )
                entries = response[1] if isinstance(response, (list, tuple)) and len(response) > 1 else []
                return self._entries_to_tasks(agent, entries)
            pending = self.bus.client.xpending_range(
                self.stream,
                self.group,
                min="-",
                max="+",
                count=max(1, limit),
            )
            message_ids = [item["message_id"] for item in pending if int(item.get("time_since_delivered", 0)) >= self.claim_idle_ms]
            if not message_ids:
                return []
            entries = self.bus.client.xclaim(
                self.stream,
                self.group,
                self.consumer,
                min_idle_time=max(1, self.claim_idle_ms),
                message_ids=message_ids[:limit],
            )
        except Exception:
            return []
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
        policy_weights: AgentPolicyWeights | dict[str, Any] | None = None,
        minimum_utility: float = 0.0,
        memory_enabled: bool = True,
        healthy: bool = True,
        available_models: Iterable[str] | None = None,
        available_dependencies: Iterable[str] | None = None,
        idempotency_store: SQLiteIdempotencyStore | None = None,
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
        self.policy_weights = (
            policy_weights
            if isinstance(policy_weights, AgentPolicyWeights)
            else AgentPolicyWeights.from_mapping(policy_weights)
        )
        self.minimum_utility = max(0.0, min(float(minimum_utility), 1.0))
        self.memory_enabled = bool(memory_enabled)
        self.healthy = bool(healthy)
        self.available_models = set(available_models or {"*"})
        self.available_dependencies = set(available_dependencies or {"*"})
        self.idempotency_store = idempotency_store
        self._state_lock = Lock()
        self._active_task_ids: set[str] = set()

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
                "policy_snapshot": self.policy_snapshot(),
                "max_parallel_tasks": self.max_parallel_tasks,
                "operational_state": asdict(self.perceive()),
            },
        )

    def policy_snapshot(self) -> dict[str, Any]:
        task_types = set(self.memory.successes_by_type) | set(self.memory.errors_by_type) | set(self.memory.durations_by_type)
        return {
            task_type: {
                "reliability": round(self.memory.reliability(task_type), 4),
                "successes": self.memory.successes_by_type.get(task_type, 0),
                "errors": self.memory.errors_by_type.get(task_type, 0),
                "average_duration_sec": (
                    round(avg_duration, 4)
                    if (avg_duration := self.memory.average_duration(task_type)) is not None
                    else None
                ),
            }
            for task_type in sorted(task_types)
        }

    def can_handle(self, task: AgentTask) -> bool:
        if task.required_capability:
            return any(capability.name == task.required_capability for capability in self.capabilities)
        return any(capability.supports(task.task_type) for capability in self.capabilities)

    @staticmethod
    def _required_values(payload: dict[str, Any], key: str) -> set[str]:
        raw = payload.get(key, [])
        if isinstance(raw, str):
            return {raw} if raw else set()
        return {str(value) for value in raw if str(value)} if isinstance(raw, (list, tuple, set)) else set()

    @staticmethod
    def _available(required: set[str], available: set[str]) -> bool:
        return not required or "*" in available or required.issubset(available)

    def perceive(self, task: AgentTask | None = None) -> AgentPerception:
        """Observe l'état local; la tâche est acceptée pour une API perception-action stable."""

        del task
        with self._state_lock:
            active_tasks = len(self._active_task_ids)
        maximum = max(1, int(self.max_parallel_tasks))
        return AgentPerception(
            agent_id=self.agent_id,
            healthy=self.healthy,
            active_tasks=active_tasks,
            max_parallel_tasks=maximum,
            load_ratio=min(1.0, active_tasks / maximum),
            available_models=tuple(sorted(self.available_models)),
            available_dependencies=tuple(sorted(self.available_dependencies)),
            memory_enabled=self.memory_enabled,
        )

    def evaluate(self, task: AgentTask) -> BidEvaluation:
        """Évalue localement un CFP et retourne une proposition ou un refus motivé."""

        perception = self.perceive(task)
        if not self.can_handle(task):
            return BidEvaluation(task.task_id, self.agent_id, False, 0.0, {}, (), "capability_missing")
        required_models = self._required_values(task.payload, "required_models")
        if not self._available(required_models, self.available_models):
            return BidEvaluation(task.task_id, self.agent_id, False, 0.0, {}, (), "model_missing")
        required_dependencies = self._required_values(task.payload, "required_dependencies")
        if not self._available(required_dependencies, self.available_dependencies):
            return BidEvaluation(task.task_id, self.agent_id, False, 0.0, {}, (), "dependency_unavailable")
        if not perception.healthy:
            return BidEvaluation(task.task_id, self.agent_id, False, 0.0, {}, (), "agent_unhealthy")
        if perception.active_tasks >= perception.max_parallel_tasks:
            return BidEvaluation(task.task_id, self.agent_id, False, 0.0, {}, (), "agent_overloaded")

        matching = [capability for capability in self.capabilities if capability.supports(task.task_type)]
        if task.required_capability:
            matching = [capability for capability in matching if capability.name == task.required_capability]
        best = max(matching, key=lambda capability: capability.confidence)
        average_duration = self.memory.average_duration(task.task_type) if self.memory_enabled else None
        components = {
            "capability": max(0.0, min(float(best.confidence), 1.0)),
            "history": self.memory.reliability(task.task_type) if self.memory_enabled else 0.5,
            "model": 1.0,
            "availability": max(0.0, 1.0 - perception.load_ratio),
            "load": max(0.0, 1.0 - perception.load_ratio),
            "latency": 0.5 if average_duration is None else 1.0 / (1.0 + max(0.0, average_duration)),
        }
        utility = sum(
            float(getattr(self.policy_weights, component)) * value
            for component, value in components.items()
        )
        utility = max(0.0, min(utility, 1.0))
        reasons = tuple(f"{name}={value:.6f}" for name, value in components.items())
        if utility < self.minimum_utility:
            return BidEvaluation(
                task.task_id,
                self.agent_id,
                False,
                round(utility, 6),
                components,
                reasons,
                "low_expected_utility",
            )
        return BidEvaluation(task.task_id, self.agent_id, True, round(utility, 6), components, reasons)

    def compute_bid(self, task: AgentTask) -> float:
        """Retourne l'utilité locale d'une tâche, dans l'intervalle [0, 1]."""

        return self.evaluate(task).utility

    def propose(self, task: AgentTask) -> BidEvaluation:
        return self.evaluate(task)

    def refuse(self, task: AgentTask) -> str:
        evaluation = self.evaluate(task)
        return evaluation.refusal_reason

    def accept(self, task: AgentTask) -> bool:
        """Réserve localement une place après attribution du contrat."""

        with self._state_lock:
            if not self.healthy or len(self._active_task_ids) >= max(1, self.max_parallel_tasks):
                return False
            self._active_task_ids.add(task.task_id)
        return True

    def _start_task(self, task: AgentTask) -> bool:
        with self._state_lock:
            already_reserved = task.task_id in self._active_task_ids
            if not already_reserved:
                self._active_task_ids.add(task.task_id)
        return already_reserved

    def _finish_task(self, task: AgentTask) -> None:
        with self._state_lock:
            self._active_task_ids.discard(task.task_id)

    def learn(self, result: TaskResult) -> None:
        """Met à jour la mémoire seulement lorsque le mode mémoire est actif."""

        if not self.memory_enabled:
            return
        self.memory.record(result)
        self.save_memory()

    def score_task(self, task: AgentTask) -> tuple[float, list[str]]:
        """Classe une tâche à partir de la même utilité que le Contract Net."""

        evaluation = self.evaluate(task)
        if not evaluation.accepted:
            return -9999.0, [f"refusal={evaluation.refusal_reason}"]
        score = float(task.priority) + evaluation.utility * 20.0
        reasons = [
            f"priority={task.priority}",
            f"utility={evaluation.utility:.6f}",
            *evaluation.reasons,
        ]
        if task.task_id in self.memory.completed_tasks:
            score -= 100.0
            reasons.append("already completed")
        recent_same_type = sum(1 for task_type in self.memory.recent_task_types[-8:] if task_type == task.task_type)
        if recent_same_type >= 4:
            score -= recent_same_type * 1.5
            reasons.append(f"diversity_penalty={recent_same_type}")
        if task.deadline_sec is not None and task.deadline_sec < 5:
            score += 10.0 + max(0.0, 5.0 - task.deadline_sec)
            reasons.append("short deadline")
        if task.attempts:
            score -= min(task.attempts, 5) * 2.0
            reasons.append(f"attempts={task.attempts}")
        return score, reasons

    def choose_tasks(self, tasks: Iterable[AgentTask], limit: int | None = None) -> list[tuple[AgentTask, float, list[str]]]:
        scored = [(task, *self.score_task(task)) for task in tasks if self.can_handle(task)]
        scored = [item for item in scored if item[1] > -999]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[: max(1, limit or self.max_parallel_tasks)]

    def execute_task(self, task: AgentTask, score: float = 0.0, reasons: list[str] | None = None) -> TaskResult:
        self._start_task(task)
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
        idempotency_key = str(task.payload.get("idempotency_key") or "")
        key_reserved = False
        try:
            replayed_output: dict[str, Any] | None = None
            if self.idempotency_store is not None and idempotency_key:
                reservation, previous = self.idempotency_store.reserve(
                    idempotency_key,
                    owner=self.agent_id,
                    task_id=task.task_id,
                )
                if reservation == "completed" and previous is not None:
                    replayed_output = {**previous.result, "_idempotency_replayed": True}
                elif reservation == "in_progress":
                    raise RuntimeError("idempotency_key_in_progress")
                else:
                    key_reserved = True

            control: dict[str, Any] = {}
            if replayed_output is None:
                handler = self.handlers[task.task_type]
                raw_output = handler(task, context)
                if isinstance(raw_output, ActionOutcome):
                    output = dict(raw_output.output)
                    control = raw_output.control_payload()
                    persisted_output = {
                        "_agent_output": output,
                        "_agent_control": control,
                    }
                else:
                    output = dict(raw_output)
                    persisted_output = output
                if self.idempotency_store is not None and idempotency_key:
                    self.idempotency_store.complete(
                        idempotency_key,
                        owner=self.agent_id,
                        task_id=task.task_id,
                        result=persisted_output,
                    )
            else:
                if "_agent_output" in replayed_output and "_agent_control" in replayed_output:
                    output = dict(replayed_output["_agent_output"])
                    output["_idempotency_replayed"] = True
                    control = dict(replayed_output["_agent_control"])
                else:
                    output = replayed_output
            result = TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                agent_id=self.agent_id,
                status="ok",
                output=output,
                started_at=started,
                elapsed_sec=round(perf_counter() - timer, 6),
                decision_score=score,
                decision_reasons=list(reasons or []),
                control=control,
            )
        except Exception as exc:
            if key_reserved and self.idempotency_store is not None and idempotency_key:
                self.idempotency_store.release_failed(idempotency_key, owner=self.agent_id)
            result = TaskResult(
                task_id=task.task_id,
                task_type=task.task_type,
                agent_id=self.agent_id,
                status="error",
                error=str(exc),
                started_at=started,
                elapsed_sec=round(perf_counter() - timer, 6),
                decision_score=score,
                decision_reasons=list(reasons or []),
            )
        finally:
            self._finish_task(task)
        self.learn(result)
        self.publish_state(
            "agent.task.completed" if result.status == "ok" else "agent.task.failed",
            {"result": asdict(result)},
            status=result.status,
        )
        return result

    @staticmethod
    def _goal_task(task: AgentTask, *, goal_id: str, parent_task_id: str = "", depth: int = 0) -> AgentTask:
        cloned = AgentTask(**asdict(task))
        cloned.payload = {
            **cloned.payload,
            "_goal_id": goal_id,
            "_parent_task_id": parent_task_id,
            "_goal_depth": int(depth),
        }
        return cloned

    def _save_goal(self, goal: GoalState) -> None:
        goal.updated_at = datetime.now(timezone.utc).isoformat()
        self.memory.goals[goal.goal_id] = asdict(goal)
        self.save_memory()
        self.publish_state(
            "agent.goal.updated",
            {
                "goal_id": goal.goal_id,
                "objective": goal.objective,
                "goal_status": goal.status,
                "actions_executed": goal.actions_executed,
                "pending_tasks": len(goal.pending_tasks),
            },
            status="ok" if goal.status not in {"failed", "blocked", "budget_exhausted"} else "error",
        )

    def start_goal(
        self,
        objective: str,
        tasks: Iterable[AgentTask],
        *,
        limits: AutonomyLimits | None = None,
        goal_id: str | None = None,
    ) -> GoalState:
        """Crée et persiste un objectif sans encore exécuter ses tâches."""

        goal = GoalState.create(objective, tasks, limits=limits, goal_id=goal_id)
        if len(goal.pending_tasks) > goal.max_pending_tasks:
            raise ValueError("Le nombre initial de tâches dépasse le budget de l'objectif")
        prepared: list[dict[str, Any]] = []
        for raw_task in goal.pending_tasks:
            task = self._goal_task(AgentTask(**raw_task), goal_id=goal.goal_id)
            prepared.append(asdict(task))
        goal.pending_tasks = prepared
        if not goal.pending_tasks:
            goal.status = "completed"
        self._save_goal(goal)
        return goal

    def get_goal(self, goal_id: str) -> GoalState | None:
        raw = self.memory.goals.get(goal_id)
        return GoalState.from_mapping(raw) if raw is not None else None

    def pursue_goal(
        self,
        objective: str,
        tasks: Iterable[AgentTask],
        *,
        limits: AutonomyLimits | None = None,
        goal_id: str | None = None,
        delegate: Callable[[AgentTask], Any] | None = None,
    ) -> GoalState:
        """Poursuit un objectif jusqu'à sa terminaison ou un garde-fou.

        ``delegate`` reste facultatif et peut s'appuyer sur le Contract Net:
        il reçoit une tâche non exécutable localement et retourne soit un
        ``TaskResult``, soit un objet possédant un attribut ``result``.
        """

        goal = self.start_goal(objective, tasks, limits=limits, goal_id=goal_id)
        return self._advance_goal(goal, delegate=delegate)

    def resume_goal(
        self,
        goal_id: str,
        *,
        delegate: Callable[[AgentTask], Any] | None = None,
        additional_actions: int = 0,
    ) -> GoalState:
        """Reprend un objectif persistant encore exécutable."""

        goal = self.get_goal(goal_id)
        if goal is None:
            raise KeyError(f"Objectif inconnu: {goal_id}")
        if goal.status in {"completed", "failed"}:
            return goal
        if goal.status == "budget_exhausted":
            if additional_actions < 1:
                return goal
            goal.max_actions += int(additional_actions)
        if goal.status in {"blocked", "budget_exhausted"}:
            goal.status = "running"
            goal.last_error = ""
        return self._advance_goal(goal, delegate=delegate)

    def _advance_goal(
        self,
        goal: GoalState,
        *,
        delegate: Callable[[AgentTask], Any] | None,
    ) -> GoalState:
        if goal.status == "completed":
            return goal
        goal.status = "running"
        self._save_goal(goal)

        while goal.pending_tasks and goal.actions_executed < goal.max_actions:
            pending = [AgentTask(**raw_task) for raw_task in goal.pending_tasks]
            selected = self.choose_tasks(pending, limit=1)
            delegated = False
            if selected:
                task, score, reasons = selected[0]
                result = self.execute_task(task, score, reasons)
            else:
                task = pending[0]
                if delegate is None:
                    goal.status = "blocked"
                    goal.last_error = f"Aucun handler local ou proposition acceptable pour {task.task_type}"
                    self._save_goal(goal)
                    return goal
                delegated = True
                try:
                    delegated_result = delegate(task)
                except Exception as exc:
                    delegated_result = TaskResult(
                        task_id=task.task_id,
                        task_type=task.task_type,
                        agent_id=self.agent_id,
                        status="error",
                        error=f"delegation_failed: {exc}",
                    )
                result = getattr(delegated_result, "result", delegated_result)
                if result is None or not isinstance(result, TaskResult):
                    result = TaskResult(
                        task_id=task.task_id,
                        task_type=task.task_type,
                        agent_id=self.agent_id,
                        status="error",
                        error="delegation_failed",
                    )

            goal.pending_tasks = [
                raw_task for raw_task in goal.pending_tasks if raw_task.get("task_id") != task.task_id
            ]
            goal.actions_executed += 1
            if delegated:
                goal.delegated_task_ids.append(task.task_id)
            goal.task_results.append(
                {
                    "task_id": result.task_id,
                    "task_type": result.task_type,
                    "agent_id": result.agent_id,
                    "status": result.status,
                    "error": result.error,
                    "completed_at": result.completed_at,
                }
            )
            goal.task_results = goal.task_results[-50:]

            retry_requested = bool(result.control.get("retry_current_task"))
            if result.status != "ok" or retry_requested:
                next_attempt = int(task.attempts) + 1
                if next_attempt < goal.max_attempts_per_task:
                    task.attempts = next_attempt
                    goal.pending_tasks.append(asdict(task))
                    self._save_goal(goal)
                    continue
                goal.failed_task_ids.append(task.task_id)
                goal.status = "failed"
                goal.last_error = result.error or "Nombre maximal de tentatives atteint"
                self._save_goal(goal)
                return goal

            goal.completed_task_ids.append(task.task_id)
            if bool(result.control.get("goal_completed")):
                goal.pending_tasks.clear()
                goal.status = "completed"
                self._save_goal(goal)
                return goal

            parent_depth = int(task.payload.get("_goal_depth", 0))
            for raw_follow_up in result.control.get("next_tasks", []):
                depth = parent_depth + 1
                if depth > goal.max_depth:
                    goal.status = "failed"
                    goal.last_error = "Profondeur maximale de l'objectif dépassée"
                    self._save_goal(goal)
                    return goal
                follow_up = self._goal_task(
                    AgentTask(**raw_follow_up),
                    goal_id=goal.goal_id,
                    parent_task_id=task.task_id,
                    depth=depth,
                )
                goal.pending_tasks.append(asdict(follow_up))
                if len(goal.pending_tasks) > goal.max_pending_tasks:
                    goal.status = "failed"
                    goal.last_error = "Nombre maximal de tâches en attente dépassé"
                    self._save_goal(goal)
                    return goal
            self._save_goal(goal)

        if goal.pending_tasks:
            goal.status = "budget_exhausted"
            goal.last_error = "Budget maximal d'actions atteint"
        else:
            goal.status = "completed"
        self._save_goal(goal)
        return goal

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
