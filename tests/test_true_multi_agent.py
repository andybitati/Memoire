from __future__ import annotations

import sys
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import AgentMessage, LocalMessageBus
from agents.contract_net import ContractNetCoordinator
from agents.idempotency import SQLiteIdempotencyStore
from agents.intelligent_runtime import (
    ActionOutcome,
    AgentCapability,
    AgentMemory,
    AgentTask,
    AutonomyLimits,
    MultiTaskIntelligentAgent,
)
from agents.redis_contract_net import RedisContractNetCoordinator


def ok_handler(task, context):
    return {"task_id": task.task_id, "agent_id": context.agent_id}


class TrueMultiAgentTests(unittest.TestCase):
    def test_agent_pursues_and_persists_a_bounded_multistep_goal(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / "agent-memory.json"

            def discover(task, context):
                return ActionOutcome(
                    output={"discovered": True},
                    next_tasks=[AgentTask.create("parse")],
                )

            def parse(task, context):
                return ActionOutcome(output={"parsed": True}, goal_completed=True)

            agent = MultiTaskIntelligentAgent(
                agent_id="autonomous-agent",
                capabilities=[
                    AgentCapability("discover", ("discover",)),
                    AgentCapability("parse", ("parse",)),
                ],
                handlers={"discover": discover, "parse": parse},
                memory_path=memory_path,
            )
            goal = agent.pursue_goal(
                "Découvrir puis parser les journaux",
                [AgentTask.create("discover")],
                limits=AutonomyLimits(max_actions=4, max_depth=2),
            )

            self.assertEqual(goal.status, "completed")
            self.assertEqual(goal.actions_executed, 2)
            self.assertEqual(len(goal.completed_task_ids), 2)
            self.assertFalse(goal.pending_tasks)

            reloaded = MultiTaskIntelligentAgent(
                agent_id="autonomous-agent",
                capabilities=[AgentCapability("discover", ("discover",))],
                handlers={"discover": discover},
                memory_path=memory_path,
            )
            persisted = reloaded.get_goal(goal.goal_id)
            self.assertIsNotNone(persisted)
            self.assertEqual(persisted.status, "completed")
            self.assertEqual(persisted.actions_executed, 2)

    def test_goal_delegates_an_unsupported_follow_up(self):
        def plan(task, context):
            return ActionOutcome(next_tasks=[AgentTask.create("remote.detect")])

        agent = MultiTaskIntelligentAgent(
            agent_id="planner",
            capabilities=[AgentCapability("plan", ("plan",))],
            handlers={"plan": plan},
        )
        remote = MultiTaskIntelligentAgent(
            agent_id="remote-worker",
            capabilities=[AgentCapability("detect", ("remote.detect",))],
            handlers={"remote.detect": ok_handler},
        )
        coordinator = ContractNetCoordinator([remote])

        goal = agent.pursue_goal(
            "Planifier et déléguer",
            [AgentTask.create("plan")],
            delegate=coordinator.negotiate,
        )

        self.assertEqual(goal.status, "completed")
        self.assertEqual(goal.actions_executed, 2)
        self.assertEqual(len(goal.delegated_task_ids), 1)
        self.assertEqual(goal.task_results[-1]["agent_id"], "remote-worker")

    def test_goal_stops_when_the_action_budget_is_exhausted(self):
        def repeat(task, context):
            return ActionOutcome(next_tasks=[AgentTask.create("repeat")])

        agent = MultiTaskIntelligentAgent(
            agent_id="bounded-agent",
            capabilities=[AgentCapability("repeat", ("repeat",))],
            handlers={"repeat": repeat},
        )
        goal = agent.pursue_goal(
            "Répéter de façon bornée",
            [AgentTask.create("repeat")],
            limits=AutonomyLimits(max_actions=2, max_depth=5),
        )

        self.assertEqual(goal.status, "budget_exhausted")
        self.assertEqual(goal.actions_executed, 2)
        self.assertEqual(len(goal.pending_tasks), 1)

        unchanged = agent.resume_goal(goal.goal_id)
        self.assertEqual(unchanged.status, "budget_exhausted")
        agent.handlers["repeat"] = lambda task, context: ActionOutcome(goal_completed=True)
        resumed = agent.resume_goal(goal.goal_id, additional_actions=1)
        self.assertEqual(resumed.status, "completed")
        self.assertEqual(resumed.actions_executed, 3)

    def test_redis_contract_net_reassigns_after_failed_award(self):
        class FakeTransport:
            response_stream = "responses"

            def __init__(self):
                self.messages = []

            def latest_id(self, stream):
                return "0-0"

            def send_to_agent(self, agent_id, *, source, message_type, payload, status="ok"):
                contract_id = payload["contract_id"]
                if message_type == "CFP":
                    utility = 0.9 if agent_id == "agent-a" else 0.8
                    self.messages.append(
                        AgentMessage("run", agent_id, source, "PROPOSE", {"contract_id": contract_id, "utility": utility})
                    )
                elif message_type == "AWARD":
                    self.messages.append(AgentMessage("run", agent_id, source, "ACCEPT", {"contract_id": contract_id}))
                    result_status = "error" if agent_id == "agent-a" else "ok"
                    self.messages.append(
                        AgentMessage(
                            "run",
                            agent_id,
                            source,
                            "FAIL" if result_status == "error" else "RESULT",
                            {
                                "contract_id": contract_id,
                                "result": {
                                    "task_id": payload["task_id"],
                                    "task_type": "detect",
                                    "agent_id": agent_id,
                                    "status": result_status,
                                },
                            },
                            result_status,
                        )
                    )

            def read(self, stream, cursor, **kwargs):
                messages, self.messages = self.messages, []
                return "1-0", messages

        outcome = RedisContractNetCoordinator(FakeTransport(), ["agent-a", "agent-b"]).negotiate(
            AgentTask.create("detect")
        )
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.winner, "agent-b")
        self.assertEqual(outcome.reassignments, 1)

    def _dynamic_redis_transport(self, *, loads=None, utilities=None):
        class FakeTransport:
            response_stream = "responses"

            def __init__(self):
                self.messages = []
                self.loads = dict(loads or {})
                self.utilities = dict(utilities or {"agent-a": 0.9, "agent-b": 0.8})
                self.claimed = []
                self.released = []

            def latest_id(self, stream):
                return "0-0"

            def send_to_agent(self, agent_id, *, source, message_type, payload, status="ok"):
                contract_id = payload["contract_id"]
                if message_type == "CFP":
                    utility = self.utilities[agent_id]
                    self.messages.append(
                        AgentMessage(
                            "run",
                            agent_id,
                            source,
                            "PROPOSE",
                            {
                                "contract_id": contract_id,
                                "utility": utility,
                                "perception": {"max_parallel_tasks": 1},
                            },
                        )
                    )
                elif message_type == "AWARD":
                    self.messages.append(AgentMessage("run", agent_id, source, "ACCEPT", {"contract_id": contract_id}))
                    self.messages.append(
                        AgentMessage(
                            "run",
                            agent_id,
                            source,
                            "RESULT",
                            {
                                "contract_id": contract_id,
                                "result": {
                                    "task_id": payload["task_id"],
                                    "task_type": "detect",
                                    "agent_id": agent_id,
                                    "status": "ok",
                                },
                            },
                        )
                    )

            def claim_least_loaded(self, agent_ids, capacities):
                del capacities
                ordered = list(agent_ids)
                winner = min(ordered, key=lambda agent_id: (self.loads.get(agent_id, 0), ordered.index(agent_id)))
                self.loads[winner] = self.loads.get(winner, 0) + 1
                self.claimed.append((tuple(ordered), winner))
                return winner

            def release_allocation(self, agent_id):
                self.loads[agent_id] -= 1
                self.released.append(agent_id)

            def read(self, stream, cursor, **kwargs):
                messages, self.messages = self.messages, []
                return "1-0", messages

        return FakeTransport()

    def test_redis_historical_policy_keeps_utility_then_agent_id(self):
        transport = self._dynamic_redis_transport(
            loads={"agent-a": 10, "agent-b": 0},
            utilities={"agent-a": 0.9, "agent-b": 0.9},
        )
        outcome = RedisContractNetCoordinator(transport, ["agent-a", "agent-b"]).negotiate(
            AgentTask.create("detect")
        )
        self.assertEqual(outcome.winner, "agent-a")
        self.assertEqual(transport.claimed, [])

    def test_redis_utility_load_uses_load_only_between_equal_utilities(self):
        transport = self._dynamic_redis_transport(
            loads={"agent-a": 10, "agent-b": 0},
            utilities={"agent-a": 0.9, "agent-b": 0.9},
        )
        outcome = RedisContractNetCoordinator(
            transport,
            ["agent-a", "agent-b"],
            selection_policy="utility_load",
        ).negotiate(AgentTask.create("detect"))
        self.assertEqual(outcome.winner, "agent-b")
        self.assertEqual(transport.claimed, [(('agent-a', 'agent-b'), 'agent-b')])
        self.assertEqual(transport.released, ["agent-b"])

    def test_redis_least_loaded_can_choose_lower_utility(self):
        transport = self._dynamic_redis_transport(loads={"agent-a": 1, "agent-b": 0})
        outcome = RedisContractNetCoordinator(
            transport,
            ["agent-a", "agent-b"],
            selection_policy="least_loaded",
        ).negotiate(AgentTask.create("detect"))
        self.assertEqual(outcome.winner, "agent-b")
        self.assertEqual(transport.claimed, [(('agent-a', 'agent-b'), 'agent-b')])
        self.assertEqual(transport.released, ["agent-b"])

    def test_agent_message_contract_stays_at_seven_fields(self):
        self.assertEqual(
            [item.name for item in fields(AgentMessage)],
            ["run_id", "source", "target", "message_type", "payload", "status", "timestamp"],
        )

    def test_reliability_uses_laplace_smoothing(self):
        memory = AgentMemory(successes_by_type={"detect": 3}, errors_by_type={"detect": 1})
        self.assertAlmostEqual(memory.reliability("detect"), 4 / 6)
        self.assertEqual(memory.reliability("unknown"), 0.5)

    def test_contract_net_emits_proposal_refusal_award_and_result(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            bus = LocalMessageBus(Path(temp_dir) / "messages.jsonl", run_id="test-cnp")
            agent_a = MultiTaskIntelligentAgent(
                agent_id="agent-a",
                capabilities=[AgentCapability("detect", ("detect",), confidence=0.95)],
                handlers={"detect": ok_handler},
                bus=bus,
                memory_enabled=False,
            )
            agent_b = MultiTaskIntelligentAgent(
                agent_id="agent-b",
                capabilities=[AgentCapability("detect", ("detect",), confidence=0.70)],
                handlers={"detect": ok_handler},
                bus=bus,
                memory_enabled=False,
            )
            agent_c = MultiTaskIntelligentAgent(
                agent_id="agent-c",
                capabilities=[AgentCapability("parse", ("parse",), confidence=1.0)],
                handlers={"parse": ok_handler},
                bus=bus,
                memory_enabled=False,
            )
            coordinator = ContractNetCoordinator([agent_a, agent_b, agent_c], bus=bus)
            outcome = coordinator.negotiate(AgentTask.create("detect"))

            self.assertEqual(outcome.status, "ok")
            self.assertEqual(outcome.winner, "agent-a")
            self.assertEqual(outcome.refusals["agent-c"], "capability_missing")
            emitted = {message.message_type for message in coordinator.transcript}
            self.assertTrue(
                {"CFP", "PROPOSE", "REFUSE", "AWARD", "REJECT", "ACCEPT", "RESULT", "FEEDBACK"}.issubset(emitted)
            )

    def _busy_fallback_agents(self):
        """agent-a échoue ; agent-b est occupé au moment du CFP, puis se libère."""

        agent_b = MultiTaskIntelligentAgent(
            agent_id="agent-b",
            capabilities=[AgentCapability("detect", ("detect",), confidence=0.70)],
            handlers={"detect": ok_handler},
            memory_enabled=False,
            max_parallel_tasks=1,
        )
        agent_b._active_task_ids.add("other-task")

        def failing_handler(task, context):
            agent_b._active_task_ids.discard("other-task")
            raise RuntimeError("injected_failure")

        agent_a = MultiTaskIntelligentAgent(
            agent_id="agent-a",
            capabilities=[AgentCapability("detect", ("detect",), confidence=0.95)],
            handlers={"detect": failing_handler},
            memory_enabled=False,
        )
        return agent_a, agent_b

    def test_failed_award_solicits_agents_busy_at_cfp_time(self):
        agent_a, agent_b = self._busy_fallback_agents()
        coordinator = ContractNetCoordinator([agent_a, agent_b])
        outcome = coordinator.negotiate(AgentTask.create("detect"))
        self.assertEqual(outcome.status, "ok")
        self.assertEqual(outcome.winner, "agent-b")
        self.assertEqual(outcome.reassignments, 1)
        self.assertEqual(outcome.message_counts["CFP"], 2)

    def test_frozen_fallback_policy_keeps_historical_behaviour(self):
        agent_a, agent_b = self._busy_fallback_agents()
        coordinator = ContractNetCoordinator([agent_a, agent_b], fallback_policy="frozen")
        outcome = coordinator.negotiate(AgentTask.create("detect"))
        self.assertEqual(outcome.status, "error")
        self.assertEqual(outcome.refusals["agent-b"], "agent_overloaded")
        self.assertEqual(outcome.message_counts["CFP"], 1)

    def test_fallback_does_not_retry_an_agent_twice(self):
        attempts = []

        def always_fails(task, context):
            attempts.append(context.agent_id)
            raise RuntimeError("injected_failure")

        agents = [
            MultiTaskIntelligentAgent(
                agent_id=f"agent-{name}",
                capabilities=[AgentCapability("detect", ("detect",), confidence=conf)],
                handlers={"detect": always_fails},
                memory_enabled=False,
            )
            for name, conf in (("a", 0.9), ("b", 0.8), ("c", 0.7))
        ]
        outcome = ContractNetCoordinator(agents).negotiate(AgentTask.create("detect"))
        self.assertEqual(outcome.status, "error")
        self.assertEqual(sorted(attempts), ["agent-a", "agent-b", "agent-c"])
        self.assertEqual(outcome.reassignments, 2)

    def test_fail_message_is_emitted_when_no_agent_proposes(self):
        agent = MultiTaskIntelligentAgent(
            agent_id="parser",
            capabilities=[AgentCapability("parse", ("parse",))],
            handlers={"parse": ok_handler},
        )
        coordinator = ContractNetCoordinator([agent])
        outcome = coordinator.negotiate(AgentTask.create("detect"))
        self.assertEqual(outcome.status, "error")
        self.assertEqual(outcome.message_counts["FAIL"], 1)

    def test_all_standard_refusal_reasons_are_reachable(self):
        base_task = AgentTask.create("detect")
        missing_capability = MultiTaskIntelligentAgent(
            agent_id="missing-capability",
            capabilities=[AgentCapability("parse", ("parse",))],
            handlers={"parse": ok_handler},
        )
        self.assertEqual(missing_capability.refuse(base_task), "capability_missing")

        missing_model = MultiTaskIntelligentAgent(
            agent_id="missing-model",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            available_models={"isolation-forest"},
        )
        self.assertEqual(
            missing_model.refuse(AgentTask.create("detect", {"required_models": ["lstm"]})),
            "model_missing",
        )

        missing_dependency = MultiTaskIntelligentAgent(
            agent_id="missing-dependency",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            available_dependencies={"numpy"},
        )
        self.assertEqual(
            missing_dependency.refuse(AgentTask.create("detect", {"required_dependencies": ["redis"]})),
            "dependency_unavailable",
        )

        unhealthy = MultiTaskIntelligentAgent(
            agent_id="unhealthy",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            healthy=False,
        )
        self.assertEqual(unhealthy.refuse(base_task), "agent_unhealthy")

        overloaded = MultiTaskIntelligentAgent(
            agent_id="overloaded",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            max_parallel_tasks=1,
        )
        self.assertTrue(overloaded.accept(AgentTask.create("detect")))
        self.assertEqual(overloaded.refuse(base_task), "agent_overloaded")

        low_utility = MultiTaskIntelligentAgent(
            agent_id="low-utility",
            capabilities=[AgentCapability("detect", ("detect",), confidence=0.0)],
            handlers={"detect": ok_handler},
            minimum_utility=0.99,
        )
        self.assertEqual(low_utility.refuse(base_task), "low_expected_utility")

    def test_memory_switch_changes_or_neutralizes_historical_component(self):
        successful_memory = AgentMemory(successes_by_type={"detect": 9}, errors_by_type={"detect": 1})
        failing_memory = AgentMemory(successes_by_type={"detect": 1}, errors_by_type={"detect": 9})
        task = AgentTask.create("detect")

        enabled_good = MultiTaskIntelligentAgent(
            agent_id="enabled-good",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            memory_enabled=True,
        )
        enabled_bad = MultiTaskIntelligentAgent(
            agent_id="enabled-bad",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            memory_enabled=True,
        )
        enabled_good.memory = successful_memory
        enabled_bad.memory = failing_memory
        self.assertGreater(enabled_good.compute_bid(task), enabled_bad.compute_bid(task))

        disabled_good = MultiTaskIntelligentAgent(
            agent_id="disabled-good",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            memory_enabled=False,
        )
        disabled_bad = MultiTaskIntelligentAgent(
            agent_id="disabled-bad",
            capabilities=[AgentCapability("detect", ("detect",))],
            handlers={"detect": ok_handler},
            memory_enabled=False,
        )
        disabled_good.memory = successful_memory
        disabled_bad.memory = failing_memory
        self.assertEqual(disabled_good.compute_bid(task), disabled_bad.compute_bid(task))

    def test_post_processing_pre_ack_recovery_does_not_repeat_effect(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = SQLiteIdempotencyStore(Path(temp_dir) / "idempotency.sqlite3")
            effects = {"count": 0}

            def effect_handler(task, context):
                effects["count"] += 1
                return {"effect_number": effects["count"], "producer": context.agent_id}

            capability = [AgentCapability("persist", ("persist",))]
            agent_a = MultiTaskIntelligentAgent(
                agent_id="agent-a",
                capabilities=capability,
                handlers={"persist": effect_handler},
                idempotency_store=store,
            )
            agent_b = MultiTaskIntelligentAgent(
                agent_id="agent-b",
                capabilities=capability,
                handlers={"persist": effect_handler},
                idempotency_store=store,
            )
            task = AgentTask.create("persist", {"idempotency_key": "effect-001"})

            first = agent_a.execute_task(task)
            # Crash contrôlé après résultat durable : aucun ACK de transport n'est effectué.
            recovered = agent_b.execute_task(task)

            self.assertEqual(first.status, "ok")
            self.assertEqual(recovered.status, "ok")
            self.assertEqual(effects["count"], 1)
            self.assertTrue(recovered.output["_idempotency_replayed"])
            self.assertEqual(store.completed_count(), 1)


if __name__ == "__main__":
    unittest.main()
