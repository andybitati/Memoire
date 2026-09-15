"""Protocole Contract Net léger pour l'allocation autonome des tâches Logminer.

Le coordinateur tient le registre, diffuse les appels, compare les utilités et
assure l'audit. Chaque utilité et chaque refus sont calculés localement par les
agents. Les informations du protocole sont transportées dans ``payload`` afin
de préserver strictement le contrat métier ``AgentMessage``.
"""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Iterable
from uuid import uuid4

try:
    from .bus import AgentMessage, MessageBus
    from .intelligent_runtime import AgentTask, BidEvaluation, MultiTaskIntelligentAgent, TaskResult
except ImportError:  # pragma: no cover - exécution directe historique
    from agents.bus import AgentMessage, MessageBus
    from agents.intelligent_runtime import AgentTask, BidEvaluation, MultiTaskIntelligentAgent, TaskResult


CNP_MESSAGE_TYPES = (
    "CFP",
    "PROPOSE",
    "REFUSE",
    "AWARD",
    "REJECT",
    "ACCEPT",
    "RESULT",
    "FAIL",
    "FEEDBACK",
)


@dataclass
class NegotiationResult:
    """Trace structurée d'une négociation et de son exécution."""

    contract_id: str
    task_id: str
    status: str
    winner: str = ""
    proposals: dict[str, float] = field(default_factory=dict)
    refusals: dict[str, str] = field(default_factory=dict)
    result: TaskResult | None = None
    message_counts: dict[str, int] = field(default_factory=dict)
    reassignments: int = 0
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str = ""
    elapsed_sec: float = 0.0


class ContractNetCoordinator:
    """Registre et arbitre minimal; les agents restent auteurs de leurs offres."""

    def __init__(
        self,
        agents: Iterable[MultiTaskIntelligentAgent],
        *,
        bus: MessageBus | None = None,
        coordinator_id: str = "contract-net-coordinator",
        run_id: str | None = None,
    ):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.bus = bus
        self.coordinator_id = coordinator_id
        self.run_id = run_id or (bus.run_id if bus is not None else uuid4().hex)
        self.transcript: list[AgentMessage] = []
        self.registry: dict[str, dict[str, Any]] = {}
        self.refresh_registry()

    def register(self, agent: MultiTaskIntelligentAgent) -> None:
        self.agents[agent.agent_id] = agent
        self.registry[agent.agent_id] = asdict(agent.perceive())

    def unregister(self, agent_id: str) -> None:
        self.agents.pop(agent_id, None)
        self.registry.pop(agent_id, None)

    def refresh_registry(self) -> dict[str, dict[str, Any]]:
        self.registry = {agent_id: asdict(agent.perceive()) for agent_id, agent in self.agents.items()}
        return dict(self.registry)

    def _publish(
        self,
        *,
        source: str,
        target: str,
        message_type: str,
        payload: dict[str, Any],
        status: str = "ok",
    ) -> AgentMessage:
        if message_type not in CNP_MESSAGE_TYPES:
            raise ValueError(f"Type de message CNP inconnu: {message_type}")
        if self.bus is not None:
            message = self.bus.publish(source, target, message_type, payload, status)
        else:
            message = AgentMessage(
                run_id=self.run_id,
                source=source,
                target=target,
                message_type=message_type,
                payload=dict(payload),
                status=status,
            )
        self.transcript.append(message)
        return message

    @staticmethod
    def _evaluation_payload(contract_id: str, task: AgentTask, evaluation: BidEvaluation) -> dict[str, Any]:
        return {
            "contract_id": contract_id,
            "task_id": task.task_id,
            "task_type": task.task_type,
            "idempotency_key": task.payload.get("idempotency_key", ""),
            "utility": evaluation.utility,
            "components": evaluation.components,
            "reasons": list(evaluation.reasons),
            "refusal_reason": evaluation.refusal_reason,
        }

    def negotiate(self, task: AgentTask, *, allow_reassignment: bool = True) -> NegotiationResult:
        """Négocie, attribue et exécute une tâche selon un cycle CNP observable."""

        timer = perf_counter()
        started_at = datetime.now(timezone.utc).isoformat()
        contract_id = uuid4().hex
        transcript_start = len(self.transcript)
        common_payload = {
            "contract_id": contract_id,
            "task": asdict(task),
            "idempotency_key": task.payload.get("idempotency_key", ""),
            "end_to_end_run_id": task.payload.get("end_to_end_run_id", ""),
        }
        self._publish(
            source=self.coordinator_id,
            target="*",
            message_type="CFP",
            payload=common_payload,
        )

        proposals: list[tuple[MultiTaskIntelligentAgent, BidEvaluation]] = []
        refusals: dict[str, str] = {}
        for agent_id in sorted(self.agents):
            agent = self.agents[agent_id]
            evaluation = agent.propose(task)
            payload = self._evaluation_payload(contract_id, task, evaluation)
            if evaluation.accepted:
                proposals.append((agent, evaluation))
                self._publish(
                    source=agent.agent_id,
                    target=self.coordinator_id,
                    message_type="PROPOSE",
                    payload=payload,
                )
            else:
                refusals[agent.agent_id] = evaluation.refusal_reason
                self._publish(
                    source=agent.agent_id,
                    target=self.coordinator_id,
                    message_type="REFUSE",
                    payload=payload,
                    status="refused",
                )

        ranked = sorted(proposals, key=lambda item: (-item[1].utility, item[0].agent_id))
        result: TaskResult | None = None
        winner = ""
        reassignments = 0
        attempted: set[str] = set()
        for index, (agent, evaluation) in enumerate(ranked):
            if index > 0:
                reassignments += 1
            attempted.add(agent.agent_id)
            self._publish(
                source=self.coordinator_id,
                target=agent.agent_id,
                message_type="AWARD",
                payload=self._evaluation_payload(contract_id, task, evaluation),
            )
            if not agent.accept(task):
                refusals[agent.agent_id] = "agent_overloaded"
                self._publish(
                    source=agent.agent_id,
                    target=self.coordinator_id,
                    message_type="REFUSE",
                    payload={
                        "contract_id": contract_id,
                        "task_id": task.task_id,
                        "refusal_reason": "agent_overloaded",
                        "stage": "award_acceptance",
                    },
                    status="refused",
                )
                if allow_reassignment:
                    continue
                break
            winner = agent.agent_id
            self._publish(
                source=agent.agent_id,
                target=self.coordinator_id,
                message_type="ACCEPT",
                payload={"contract_id": contract_id, "task_id": task.task_id},
            )
            result = agent.execute_task(task, evaluation.utility, list(evaluation.reasons))
            terminal_type = "RESULT" if result.status == "ok" else "FAIL"
            self._publish(
                source=agent.agent_id,
                target=self.coordinator_id,
                message_type=terminal_type,
                payload={"contract_id": contract_id, "result": asdict(result)},
                status=result.status,
            )
            self._publish(
                source=self.coordinator_id,
                target=agent.agent_id,
                message_type="FEEDBACK",
                payload={
                    "contract_id": contract_id,
                    "task_id": task.task_id,
                    "outcome": result.status,
                    "observed_utility": evaluation.utility,
                    "elapsed_sec": result.elapsed_sec,
                },
                status=result.status,
            )
            if result.status == "ok" or not allow_reassignment:
                break

        for agent, evaluation in ranked:
            if agent.agent_id == winner or agent.agent_id in attempted:
                continue
            self._publish(
                source=self.coordinator_id,
                target=agent.agent_id,
                message_type="REJECT",
                payload={
                    "contract_id": contract_id,
                    "task_id": task.task_id,
                    "utility": evaluation.utility,
                    "winner": winner,
                },
                status="rejected",
            )

        if not ranked:
            self._publish(
                source=self.coordinator_id,
                target="supervisor",
                message_type="FAIL",
                payload={
                    "contract_id": contract_id,
                    "task_id": task.task_id,
                    "reason": "no_proposal",
                    "refusals": refusals,
                },
                status="error",
            )

        messages = self.transcript[transcript_start:]
        counts = Counter(message.message_type for message in messages)
        status = "ok" if result is not None and result.status == "ok" else "error"
        self.refresh_registry()
        return NegotiationResult(
            contract_id=contract_id,
            task_id=task.task_id,
            status=status,
            winner=winner,
            proposals={agent.agent_id: evaluation.utility for agent, evaluation in proposals},
            refusals=refusals,
            result=result,
            message_counts={message_type: int(counts.get(message_type, 0)) for message_type in CNP_MESSAGE_TYPES},
            reassignments=reassignments,
            started_at=started_at,
            completed_at=datetime.now(timezone.utc).isoformat(),
            elapsed_sec=round(perf_counter() - timer, 6),
        )

    def run_tasks(self, tasks: Iterable[AgentTask], *, max_workers: int = 1) -> list[NegotiationResult]:
        """Exécute plusieurs négociations, éventuellement en parallèle."""

        task_list = list(tasks)
        if max_workers <= 1:
            return [self.negotiate(task) for task in task_list]
        results: list[NegotiationResult] = []
        with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="cnp") as executor:
            futures = [executor.submit(self.negotiate, task) for task in task_list]
            for future in as_completed(futures):
                results.append(future.result())
        return results

    def message_counts(self) -> dict[str, int]:
        counts = Counter(message.message_type for message in self.transcript)
        return {message_type: int(counts.get(message_type, 0)) for message_type in CNP_MESSAGE_TYPES}
