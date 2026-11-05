"""Panne contrôlée appariée sur les architectures A, B, C et D.

Point de panne commun : le worker exécute l'effet durable, persiste son résultat
(si un magasin d'idempotence existe), puis disparaît avant d'émettre RESULT.
Politique commune : la tâche non confirmée est rejouée une fois sur un worker
vivant (redémarrage du processus pour A). Le délai de détection de la panne est
un paramètre commun non simulé ; la latence de reprise mesurée commence à la
panne et s'arrête à la confirmation du résultat rejoué.

* A  : monolithe séquentiel, sans magasin d'idempotence (comme le benchmark) ;
* B  : workers centralisés en tourniquet, sans magasin d'idempotence ;
* C  : Contract Net, mémoire désactivée, magasin SQLite partagé ;
* D  : Contract Net, mémoire activée, magasin SQLite partagé ;
* A+I, B+I : ablation, A et B dotés du même magasin SQLite.

Toutes les sorties sont écrites dans revision_reports/agent_3/.
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
import tempfile
import time
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
for path in (ROOT / "src" / "logminer", ROOT / "scripts"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_true_multi_agent_experiments as bench  # noqa: E402
from agents.contract_net import ContractNetCoordinator  # noqa: E402
from agents.idempotency import SQLiteIdempotencyStore  # noqa: E402
from agents.intelligent_runtime import AgentTask, TaskResult  # noqa: E402

SEEDS = tuple(range(42, 52))
LOAD = 40
CRASH_INDEX = 9
ARCHITECTURES = ("A", "B", "C", "D", "A+I", "B+I")
WORKERS = 3


class EffectLedger:
    """Compteur d'effets durables par clé d'idempotence."""

    def __init__(self) -> None:
        self.effects: Counter[str] = Counter()
        self.committed: set[str] = set()

    def handler(self, task: AgentTask, context: Any) -> dict[str, Any]:
        key = str(task.payload["idempotency_key"])
        self.effects[key] += 1
        values = [int(value) for value in task.payload.get("values", [])]
        checksum = sum((index + 17) * value * value for index, value in enumerate(values)) % 1_000_003
        return {"checksum": checksum, "effect_number": self.effects[key], "agent_id": context.agent_id}


class PlainWorker:
    """Worker sans agent : exécute le handler, avec ou sans magasin d'idempotence."""

    def __init__(self, worker_id: str, ledger: EffectLedger, store: SQLiteIdempotencyStore | None) -> None:
        self.worker_id = worker_id
        self.ledger = ledger
        self.store = store

    def execute(self, task: AgentTask) -> dict[str, Any]:
        key = str(task.payload["idempotency_key"])
        if self.store is not None:
            reservation, previous = self.store.reserve(key, owner=self.worker_id, task_id=task.task_id)
            if reservation == "completed" and previous is not None:
                return {**previous.result, "_idempotency_replayed": True}
        output = self.ledger.handler(task, SimpleNamespace(agent_id=self.worker_id))
        if self.store is not None:
            self.store.complete(key, owner=self.worker_id, task_id=task.task_id, result=output)
        return output


def workload(seed: int) -> list[AgentTask]:
    return [bench.agent_task(specification) for specification in bench.generate_workload(LOAD, seed)]


def run_plain(tasks: list[AgentTask], *, workers: int, store: SQLiteIdempotencyStore | None, ledger: EffectLedger) -> dict[str, Any]:
    pool = [PlainWorker(f"w{index + 1}", ledger, store) for index in range(workers)]
    alive = list(pool)
    crash_at = recovered_at = None
    replayed = False
    for index, task in enumerate(tasks):
        worker = alive[index % len(alive)]
        worker.execute(task)
        if index == CRASH_INDEX:
            # Panne : effet durable effectué, résultat non confirmé.
            crash_at = time.perf_counter()
            if workers > 1:
                alive.remove(worker)
                retry_worker = alive[index % len(alive)]
            else:
                retry_worker = PlainWorker(worker.worker_id + "-restarted", ledger, store)
                alive = [retry_worker]
            output = retry_worker.execute(task)
            replayed = bool(output.get("_idempotency_replayed"))
            recovered_at = time.perf_counter()
        ledger.committed.add(str(task.payload["idempotency_key"]))
    return {"crash_at": crash_at, "recovered_at": recovered_at, "idempotency_replayed": replayed, "reassignments": 1}


def run_cnp(tasks: list[AgentTask], *, memory_enabled: bool, store: SQLiteIdempotencyStore, ledger: EffectLedger, run_id: str) -> dict[str, Any]:
    agents = bench.build_agents(memory_enabled=memory_enabled, run_id=run_id)
    for agent in agents:
        agent.idempotency_store = store
        agent.handlers = {task_type: ledger.handler for task_type in bench.TASK_TYPES}
    coordinator = ContractNetCoordinator(agents, run_id=run_id)
    crash: dict[str, Any] = {}

    def crash_once(agent, original: Callable[..., TaskResult]) -> Callable[..., TaskResult]:
        def wrapped(task: AgentTask, score: float = 0.0, reasons: list[str] | None = None) -> TaskResult:
            result = original(task, score, reasons)
            if task.task_id == crash.get("task_id") and "crash_at" not in crash:
                crash["crash_at"] = time.perf_counter()
                crash["agent"] = agent.agent_id
                coordinator.unregister(agent.agent_id)
                return replace(result, status="error", error="worker_crash_before_result", output={})
            return result
        return wrapped

    for agent in agents:
        agent.execute_task = crash_once(agent, agent.execute_task)

    reassignments = 0
    replayed = False
    recovered_at = None
    for index, task in enumerate(tasks):
        if index == CRASH_INDEX:
            crash["task_id"] = task.task_id
        outcome = coordinator.negotiate(task)
        if index == CRASH_INDEX:
            recovered_at = time.perf_counter()
            reassignments = outcome.reassignments
            replayed = bool(outcome.result and outcome.result.output.get("_idempotency_replayed"))
        if outcome.status == "ok":
            ledger.committed.add(str(task.payload["idempotency_key"]))
    return {
        "crash_at": crash.get("crash_at"),
        "recovered_at": recovered_at,
        "idempotency_replayed": replayed,
        "reassignments": reassignments,
        "crashed_agent": crash.get("agent", ""),
    }


def run_one(architecture: str, seed: int, run_id: str, scratch: Path) -> dict[str, Any]:
    tasks = workload(seed)
    ledger = EffectLedger()
    uses_store = architecture in {"C", "D", "A+I", "B+I"}
    store = SQLiteIdempotencyStore(scratch / f"{architecture.replace('+', '_')}_{seed}.sqlite3") if uses_store else None
    if architecture in {"A", "A+I"}:
        info = run_plain(tasks, workers=1, store=store, ledger=ledger)
    elif architecture in {"B", "B+I"}:
        info = run_plain(tasks, workers=WORKERS, store=store, ledger=ledger)
    else:
        info = run_cnp(tasks, memory_enabled=architecture == "D", store=store, ledger=ledger, run_id=run_id)
    keys = [str(task.payload["idempotency_key"]) for task in tasks]
    lost = sum(key not in ledger.committed for key in keys)
    duplicates = sum(max(0, ledger.effects[key] - 1) for key in keys)
    crashed_key = keys[CRASH_INDEX]
    return {
        "run_id": run_id,
        "architecture": architecture,
        "seed": seed,
        "tasks": len(tasks),
        "crash_index": CRASH_INDEX,
        "idempotency_store": uses_store,
        "lost_tasks": lost,
        "duplicate_effects": duplicates,
        "crashed_task_effects": ledger.effects[crashed_key],
        "recovered_tasks": int(crashed_key in ledger.committed),
        "idempotency_replayed": info["idempotency_replayed"],
        "reassignments": info["reassignments"],
        "recovery_latency_ms": round((info["recovered_at"] - info["crash_at"]) * 1000.0, 6),
        "pending_final": lost,
    }


def main() -> int:
    run_id = "agent3_paired_failure_abcd_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows = []
    with tempfile.TemporaryDirectory(prefix="paired_failure_") as tmp:
        for seed in SEEDS:
            for architecture in ARCHITECTURES:
                rows.append(run_one(architecture, seed, run_id, Path(tmp)))
    with (OUT / f"{run_id}__runs.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {}
    for architecture in ARCHITECTURES:
        subset = [row for row in rows if row["architecture"] == architecture]
        latencies = [row["recovery_latency_ms"] for row in subset]
        summary[architecture] = {
            "repetitions": len(subset),
            "lost_tasks_total": sum(row["lost_tasks"] for row in subset),
            "duplicate_effects_total": sum(row["duplicate_effects"] for row in subset),
            "recovered_tasks_total": sum(row["recovered_tasks"] for row in subset),
            "idempotency_replays": sum(bool(row["idempotency_replayed"]) for row in subset),
            "recovery_latency_median_ms": round(statistics.median(latencies), 6),
            "recovery_latency_max_ms": round(max(latencies), 6),
        }
    payload = {
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "protocol": {
            "failure_point": "after_durable_effect_and_persistence_before_RESULT",
            "retry_policy": "one replay on a live worker (process restart for A); identical for all architectures",
            "detection_timeout": "common parameter, not simulated; excluded from recovery latency",
            "workload": f"scripts/run_true_multi_agent_experiments.py:generate_workload(load={LOAD}, seed)",
            "seeds": list(SEEDS),
            "crash_index": CRASH_INDEX,
            "workers_B": WORKERS,
            "agents_C_D": "scripts/run_true_multi_agent_experiments.py:build_agents (alpha, beta, gamma)",
            "reference_run_id": "ma_20260909T160812Z_34016",
            "transport": "in-process (LocalMessageBus / direct calls), not Redis",
        },
        "summary": summary,
        "artifacts": [f"revision_reports/agent_3/{run_id}__runs.csv", f"revision_reports/agent_3/{run_id}__summary.json"],
    }
    (OUT / f"{run_id}__summary.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
