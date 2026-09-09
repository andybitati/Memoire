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
from agents.intelligent_runtime import AgentCapability, AgentMemory, AgentTask, MultiTaskIntelligentAgent
from agents.redis_contract_net import RedisContractNetCoordinator


def ok_handler(task, context):
    return {"task_id": task.task_id, "agent_id": context.agent_id}


class TrueMultiAgentTests(unittest.TestCase):
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
