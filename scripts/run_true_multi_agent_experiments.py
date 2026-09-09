"""Campagne reproductible du noyau multi-agents autonome léger.

La campagne compare quatre architectures sur des workloads appariés :

* A : monolithe séquentiel;
* B : workers centralisés;
* C : Contract Net autonome, mémoire désactivée;
* D : Contract Net autonome, mémoire activée.

Elle ajoute une expérience d'adaptation, une reprise post-traitement/pré-ACK
et un pipeline Logminer bout en bout. Aucun résultat historique n'est modifié :
chaque exécution écrit des fichiers portant son identifiant de run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import statistics
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = ROOT / "src" / "logminer"
SCRIPTS_DIR = ROOT / "scripts"
for import_path in (LOGMINER_SRC, SCRIPTS_DIR):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from agents.bus import LocalMessageBus
from agents.contract_net import CNP_MESSAGE_TYPES, ContractNetCoordinator
from agents.feedback_memory import apply_feedback_memory_to_csv
from agents.idempotency import SQLiteIdempotencyStore
from agents.intelligent_runtime import AgentCapability, AgentPolicyWeights, AgentTask, MultiTaskIntelligentAgent

try:
    import psutil
except ImportError:  # pragma: no cover - dépendance déclarée dans requirements.txt
    psutil = None


PHASE_ROOT = ROOT / "experiments" / "phase_multi_agent"
ARCHITECTURES = {
    "A": "monolith",
    "B": "centralized_workers",
    "C": "autonomous_memory_off",
    "D": "autonomous_memory_on",
}
TASK_TYPES = ("parse.synthetic", "route.synthetic", "detect.synthetic", "correlate.synthetic")
RUN_FIELDS = [
    "run_id",
    "architecture",
    "architecture_label",
    "load",
    "repetition",
    "seed",
    "status",
    "successful_tasks",
    "failed_tasks",
    "duration_sec",
    "throughput_tasks_sec",
    "latency_mean_ms",
    "latency_median_ms",
    "latency_p95_ms",
    "latency_p99_ms",
    "cpu_time_sec",
    "cpu_core_equivalent_percent",
    "cpu_machine_normalized_percent",
    "rss_start_mb",
    "rss_end_mb",
    "rss_peak_mb",
    "cfp",
    "propose",
    "refuse",
    "award",
    "reject",
    "accept",
    "result",
    "fail",
    "feedback",
    "cnp_messages_total",
    "messages_per_task",
    "reassignments",
    "jain_fairness",
    "recovered_tasks",
    "duplicate_effects",
    "pending_final",
    "lag_final",
    "error",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def percentile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    return ordered[lower] * (upper - position) + ordered[upper] * (position - lower)


def jain_index(values: Iterable[int | float]) -> float:
    normalized = [float(value) for value in values]
    if not normalized or sum(value * value for value in normalized) == 0:
        return 0.0
    return (sum(normalized) ** 2) / (len(normalized) * sum(value * value for value in normalized))


class ResourceSampler:
    """Mesure documentée : temps CPU du processus et pic RSS échantillonné."""

    def __init__(self, interval_sec: float = 0.005):
        self.interval_sec = interval_sec
        self.process = psutil.Process(os.getpid()) if psutil is not None else None
        self.stop_event = threading.Event()
        self.samples: list[float] = []
        self.thread: threading.Thread | None = None
        self.cpu_start = 0.0
        self.rss_start = 0.0

    def start(self) -> None:
        if self.process is None:
            return
        cpu = self.process.cpu_times()
        self.cpu_start = float(cpu.user + cpu.system)
        self.rss_start = float(self.process.memory_info().rss) / 1024 / 1024
        self.samples = [self.rss_start]

        def sample() -> None:
            while not self.stop_event.wait(self.interval_sec):
                try:
                    self.samples.append(float(self.process.memory_info().rss) / 1024 / 1024)
                except Exception:
                    return

        self.thread = threading.Thread(target=sample, name="resource-sampler", daemon=True)
        self.thread.start()

    def stop(self, wall_sec: float) -> dict[str, float]:
        if self.process is None:
            return {
                "cpu_time_sec": 0.0,
                "cpu_core_equivalent_percent": 0.0,
                "cpu_machine_normalized_percent": 0.0,
                "rss_start_mb": 0.0,
                "rss_end_mb": 0.0,
                "rss_peak_mb": 0.0,
            }
        self.stop_event.set()
        if self.thread is not None:
            self.thread.join(timeout=2)
        cpu = self.process.cpu_times()
        cpu_elapsed = max(0.0, float(cpu.user + cpu.system) - self.cpu_start)
        rss_end = float(self.process.memory_info().rss) / 1024 / 1024
        self.samples.append(rss_end)
        core_equivalent = cpu_elapsed / wall_sec * 100.0 if wall_sec > 0 else 0.0
        logical = psutil.cpu_count(logical=True) or 1
        return {
            "cpu_time_sec": round(cpu_elapsed, 6),
            "cpu_core_equivalent_percent": round(core_equivalent, 6),
            "cpu_machine_normalized_percent": round(core_equivalent / logical, 6),
            "rss_start_mb": round(self.rss_start, 6),
            "rss_end_mb": round(rss_end, 6),
            "rss_peak_mb": round(max(self.samples), 6),
        }


def load_policy() -> tuple[AgentPolicyWeights, float]:
    path = PHASE_ROOT / "configs" / "agent_policy.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    return AgentPolicyWeights.from_mapping(payload["weights"]), float(payload.get("minimum_utility", 0.0))


def generate_workload(load: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    workload = []
    for index in range(load):
        task_type = TASK_TYPES[index % len(TASK_TYPES)]
        values = [rng.randint(1, 10_000) for _ in range(12)]
        workload.append(
            {
                "task_id": f"paired-{seed}-{load}-{index}",
                "task_type": task_type,
                "payload": {
                    "values": values,
                    "idempotency_key": f"paired-{seed}-{load}-{index}",
                },
            }
        )
    return workload


def synthetic_effect(task: AgentTask, context: Any) -> dict[str, Any]:
    values = [int(value) for value in task.payload.get("values", [])]
    checksum = 0
    for index, value in enumerate(values):
        checksum = (checksum + (index + 17) * value * value) % 1_000_003
    preferred = str(task.payload.get("preferred_agent") or "")
    if preferred and preferred != context.agent_id:
        raise RuntimeError(f"specialization_mismatch:{context.agent_id}:{preferred}")
    return {"checksum": checksum, "agent_id": context.agent_id}


def build_agents(*, memory_enabled: bool, run_id: str) -> list[MultiTaskIntelligentAgent]:
    weights, minimum_utility = load_policy()
    profiles = {
        "agent-alpha": {
            "parse.synthetic": 0.95,
            "route.synthetic": 0.82,
            "detect.synthetic": 0.70,
            "correlate.synthetic": 0.72,
        },
        "agent-beta": {
            "parse.synthetic": 0.78,
            "route.synthetic": 0.96,
            "detect.synthetic": 0.88,
            "correlate.synthetic": 0.82,
        },
        "agent-gamma": {
            "parse.synthetic": 0.70,
            "route.synthetic": 0.76,
            "detect.synthetic": 0.97,
            "correlate.synthetic": 0.96,
        },
    }
    agents = []
    for agent_id, task_confidences in profiles.items():
        capabilities = [
            AgentCapability(
                name=f"{agent_id}-{task_type}",
                task_types=(task_type,),
                max_parallel=2,
                confidence=confidence,
            )
            for task_type, confidence in task_confidences.items()
        ]
        agent = MultiTaskIntelligentAgent(
            agent_id=agent_id,
            capabilities=capabilities,
            handlers={task_type: synthetic_effect for task_type in TASK_TYPES},
            max_parallel_tasks=2,
            memory_enabled=memory_enabled,
            policy_weights=weights,
            minimum_utility=minimum_utility,
        )
        agent.run_id = run_id
        agents.append(agent)
    return agents


def agent_task(specification: dict[str, Any]) -> AgentTask:
    return AgentTask(
        task_id=str(specification["task_id"]),
        task_type=str(specification["task_type"]),
        payload=dict(specification["payload"]),
    )


def measured_call(task: AgentTask, agent_id: str) -> tuple[str, str, float, str]:
    started = time.perf_counter()
    status = "ok"
    error = ""
    try:
        synthetic_effect(task, SimpleNamespace(agent_id=agent_id))
    except Exception as exc:  # pragma: no cover - benchmark nominal
        status = "error"
        error = str(exc)
    return task.task_id, status, (time.perf_counter() - started) * 1000.0, error


def run_monolith(workload: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], Counter[str], dict[str, int], int]:
    rows = []
    for specification in workload:
        task_id, status, latency_ms, error = measured_call(agent_task(specification), "monolith")
        rows.append({"task_id": task_id, "agent_id": "monolith", "status": status, "latency_ms": latency_ms, "error": error})
    return rows, Counter(), {"monolith": len(rows)}, 0


def run_centralized(workload: list[dict[str, Any]], workers: int) -> tuple[list[dict[str, Any]], Counter[str], dict[str, int], int]:
    worker_ids = [f"central-worker-{index + 1}" for index in range(workers)]
    rows = []
    counts = Counter()
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="central") as executor:
        futures = {}
        for index, specification in enumerate(workload):
            task = agent_task(specification)
            worker_id = worker_ids[index % workers]
            future = executor.submit(measured_call, task, worker_id)
            futures[future] = worker_id
        for future in as_completed(futures):
            task_id, status, latency_ms, error = future.result()
            worker_id = futures[future]
            counts[worker_id] += 1
            rows.append({"task_id": task_id, "agent_id": worker_id, "status": status, "latency_ms": latency_ms, "error": error})
    return rows, Counter(), dict(counts), 0


def run_autonomous(
    workload: list[dict[str, Any]],
    *,
    memory_enabled: bool,
    workers: int,
    run_id: str,
) -> tuple[list[dict[str, Any]], Counter[str], dict[str, int], int, ContractNetCoordinator]:
    agents = build_agents(memory_enabled=memory_enabled, run_id=run_id)
    coordinator = ContractNetCoordinator(agents, run_id=run_id)
    outcomes = coordinator.run_tasks((agent_task(specification) for specification in workload), max_workers=workers)
    rows = []
    counts = Counter()
    reassignments = 0
    for outcome in outcomes:
        result = outcome.result
        agent_id = outcome.winner or "unassigned"
        status = result.status if result is not None else "error"
        latency_ms = outcome.elapsed_sec * 1000.0
        error = result.error if result is not None else "no_result"
        rows.append({"task_id": outcome.task_id, "agent_id": agent_id, "status": status, "latency_ms": latency_ms, "error": error})
        if outcome.winner:
            counts[outcome.winner] += 1
        reassignments += int(outcome.reassignments)
    return rows, Counter(coordinator.message_counts()), dict(counts), reassignments, coordinator


def summarize_run(
    *,
    run_id: str,
    architecture: str,
    load: int,
    repetition: int,
    seed: int,
    duration_sec: float,
    resources: dict[str, float],
    task_rows: list[dict[str, Any]],
    messages: Counter[str],
    tasks_by_agent: dict[str, int],
    reassignments: int,
    workers: int,
    error: str = "",
) -> dict[str, Any]:
    latencies = [float(row["latency_ms"]) for row in task_rows]
    successful = sum(row["status"] == "ok" for row in task_rows)
    failed = len(task_rows) - successful
    fairness_values = list(tasks_by_agent.values())
    if architecture in {"B", "C", "D"}:
        fairness_values += [0] * max(0, workers - len(fairness_values))
    total_messages = sum(int(messages.get(message_type, 0)) for message_type in CNP_MESSAGE_TYPES)
    row = {
        "run_id": run_id,
        "architecture": architecture,
        "architecture_label": ARCHITECTURES[architecture],
        "load": load,
        "repetition": repetition,
        "seed": seed,
        "status": "ok" if not error and failed == 0 else "error",
        "successful_tasks": successful,
        "failed_tasks": failed,
        "duration_sec": round(duration_sec, 6),
        "throughput_tasks_sec": round(successful / duration_sec, 6) if duration_sec > 0 else 0.0,
        "latency_mean_ms": round(statistics.fmean(latencies), 6) if latencies else 0.0,
        "latency_median_ms": round(statistics.median(latencies), 6) if latencies else 0.0,
        "latency_p95_ms": round(percentile(latencies, 0.95), 6),
        "latency_p99_ms": round(percentile(latencies, 0.99), 6),
        **resources,
        **{message_type.lower(): int(messages.get(message_type, 0)) for message_type in CNP_MESSAGE_TYPES},
        "cnp_messages_total": total_messages,
        "messages_per_task": round(total_messages / len(task_rows), 6) if task_rows else 0.0,
        "reassignments": reassignments,
        "jain_fairness": round(jain_index(fairness_values), 6),
        "recovered_tasks": 0,
        "duplicate_effects": 0,
        "pending_final": 0,
        "lag_final": 0,
        "error": error,
    }
    return row


def run_one_architecture(
    architecture: str,
    workload: list[dict[str, Any]],
    *,
    run_id: str,
    load: int,
    repetition: int,
    seed: int,
    workers: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], ContractNetCoordinator | None]:
    sampler = ResourceSampler()
    sampler.start()
    started = time.perf_counter()
    coordinator = None
    error = ""
    try:
        if architecture == "A":
            task_rows, messages, tasks_by_agent, reassignments = run_monolith(workload)
        elif architecture == "B":
            task_rows, messages, tasks_by_agent, reassignments = run_centralized(workload, workers)
        else:
            task_rows, messages, tasks_by_agent, reassignments, coordinator = run_autonomous(
                workload,
                memory_enabled=architecture == "D",
                workers=workers,
                run_id=run_id,
            )
    except Exception as exc:  # une erreur reste dans les artefacts au lieu d'être masquée
        task_rows, messages, tasks_by_agent, reassignments = [], Counter(), {}, 0
        error = f"{type(exc).__name__}: {exc}"
    duration_sec = time.perf_counter() - started
    resources = sampler.stop(duration_sec)
    run_row = summarize_run(
        run_id=run_id,
        architecture=architecture,
        load=load,
        repetition=repetition,
        seed=seed,
        duration_sec=duration_sec,
        resources=resources,
        task_rows=task_rows,
        messages=messages,
        tasks_by_agent=tasks_by_agent,
        reassignments=reassignments,
        workers=workers,
        error=error,
    )
    for row in task_rows:
        row.update(
            {
                "run_id": run_id,
                "architecture": architecture,
                "load": load,
                "repetition": repetition,
                "seed": seed,
            }
        )
    return run_row, task_rows, coordinator


def aggregate_runs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = [
        "duration_sec",
        "throughput_tasks_sec",
        "latency_mean_ms",
        "latency_median_ms",
        "latency_p95_ms",
        "latency_p99_ms",
        "cpu_time_sec",
        "cpu_core_equivalent_percent",
        "cpu_machine_normalized_percent",
        "rss_peak_mb",
        "messages_per_task",
        "reassignments",
        "jain_fairness",
        "successful_tasks",
        "failed_tasks",
    ]
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row["architecture"]), int(row["load"])), []).append(row)
    aggregated = []
    for (architecture, load), group in sorted(grouped.items()):
        for metric in metrics:
            values = [float(row[metric]) for row in group]
            count = len(values)
            average = statistics.fmean(values)
            deviation = statistics.stdev(values) if count > 1 else 0.0
            margin = 1.96 * deviation / math.sqrt(count) if count > 1 else 0.0
            aggregated.append(
                {
                    "architecture": architecture,
                    "architecture_label": ARCHITECTURES[architecture],
                    "load": load,
                    "metric": metric,
                    "n": count,
                    "mean": round(average, 6),
                    "std": round(deviation, 6),
                    "median": round(statistics.median(values), 6),
                    "min": round(min(values), 6),
                    "max": round(max(values), 6),
                    "ci95_low": round(average - margin, 6),
                    "ci95_high": round(average + margin, 6),
                    "ci_method": "normal_approximation_1.96",
                }
            )
    return aggregated


def adaptation_experiment(run_id: str, raw_dir: Path) -> list[dict[str, Any]]:
    weights, minimum = load_policy()
    agent_ids = ("agent-alpha", "agent-beta", "agent-gamma")

    def build_adaptive_agent(agent_id: str) -> MultiTaskIntelligentAgent:
        return MultiTaskIntelligentAgent(
            agent_id=agent_id,
            capabilities=[AgentCapability("adaptive", ("adaptive",), max_parallel=1, confidence=0.9)],
            handlers={"adaptive": synthetic_effect},
            max_parallel_tasks=1,
            memory_enabled=True,
            policy_weights=weights,
            minimum_utility=minimum,
        )

    coordinator = ContractNetCoordinator([build_adaptive_agent(agent_id) for agent_id in agent_ids], run_id=run_id)
    rows = []
    for index in range(120):
        phase = 1 if index < 60 else 2
        preferred = "agent-alpha" if phase == 1 else "agent-gamma"
        task = AgentTask(
            task_id=f"adapt-{run_id}-{index}",
            task_type="adaptive",
            payload={"values": [index, phase, 17], "preferred_agent": preferred},
        )
        outcome = coordinator.negotiate(task)
        row = {
            "run_id": run_id,
            "index": index,
            "phase": phase,
            "preferred_agent": preferred,
            "winner": outcome.winner,
            "status": outcome.status,
            "reassignments": outcome.reassignments,
        }
        for agent_id in agent_ids:
            row[f"utility_{agent_id}"] = outcome.proposals.get(agent_id, "")
        rows.append(row)
    write_csv(raw_dir / f"{run_id}__adaptation.csv", rows)
    return rows


def recovery_experiment(run_id: str, raw_dir: Path) -> dict[str, Any]:
    store = SQLiteIdempotencyStore(raw_dir / f"{run_id}__recovery_idempotency.sqlite3")
    effects = {"count": 0}
    pending: dict[str, str] = {}

    def persistent_effect(task: AgentTask, context: Any) -> dict[str, Any]:
        effects["count"] += 1
        return {"effect_number": effects["count"], "producer": context.agent_id}

    capability = [AgentCapability("persistent-effect", ("persistent.effect",))]
    agent_a = MultiTaskIntelligentAgent(
        agent_id="recovery-agent-a",
        capabilities=capability,
        handlers={"persistent.effect": persistent_effect},
        idempotency_store=store,
    )
    agent_b = MultiTaskIntelligentAgent(
        agent_id="recovery-agent-b",
        capabilities=capability,
        handlers={"persistent.effect": persistent_effect},
        idempotency_store=store,
    )
    task = AgentTask(
        task_id=f"recovery-{run_id}",
        task_type="persistent.effect",
        payload={"idempotency_key": f"recovery-effect-{run_id}"},
    )
    pending[task.task_id] = agent_a.agent_id
    first = agent_a.execute_task(task)
    crash_at = time.perf_counter()
    # Crash contrôlé : le résultat est durable, mais l'entrée demeure pending faute d'ACK.
    pending[task.task_id] = agent_b.agent_id
    recovered = agent_b.execute_task(task)
    pending.pop(task.task_id, None)
    recovery_latency = time.perf_counter() - crash_at
    metrics = {
        "run_id": run_id,
        "transport": "controlled_pending_queue",
        "crash_point": "after_persistent_result_before_ack",
        "first_agent": agent_a.agent_id,
        "recovery_agent": agent_b.agent_id,
        "first_status": first.status,
        "recovery_status": recovered.status,
        "idempotency_replayed": bool(recovered.output.get("_idempotency_replayed")),
        "persistent_effects": effects["count"],
        "duplicate_effects": max(0, effects["count"] - 1),
        "recovered_tasks": int(recovered.status == "ok"),
        "recovery_latency_sec": round(recovery_latency, 6),
        "pending_final": len(pending),
        "lag_final": len(pending),
    }
    (raw_dir / f"{run_id}__recovery.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metrics


def end_to_end_experiment(run_id: str, raw_dir: Path, logs_dir: Path) -> dict[str, Any]:
    from run_intelligent_agents_demo import (
        correlate_handler,
        detect_handler,
        discover_handler,
        parse_handler,
        route_handler,
    )

    end_to_end_run_id = f"e2e-{run_id}"
    output_dir = raw_dir / f"{run_id}__end_to_end_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    bus = LocalMessageBus(logs_dir / f"{run_id}__end_to_end_messages.jsonl", run_id=end_to_end_run_id)
    store = SQLiteIdempotencyStore(raw_dir / f"{run_id}__end_to_end_idempotency.sqlite3")

    def feedback_handler(task: AgentTask, context: Any) -> dict[str, Any]:
        output = apply_feedback_memory_to_csv(task.payload["input_path"], sep=task.payload.get("sep", ";"))
        return {"feedback_csv": output, "agent_id": context.agent_id}

    handlers: dict[str, Callable[..., dict[str, Any]]] = {
        "discover.logs": discover_handler,
        "parse.logs": parse_handler,
        "route.model": route_handler,
        "detect.anomalies": detect_handler,
        "correlate.incidents": correlate_handler,
        "feedback.apply": feedback_handler,
    }
    task_types = tuple(handlers)
    agents = []
    for index, agent_id in enumerate(("e2e-alpha", "e2e-beta", "e2e-gamma")):
        capabilities = [
            AgentCapability(
                name=f"{agent_id}-{task_type}",
                task_types=(task_type,),
                max_parallel=2,
                confidence=max(0.65, 0.96 - abs((position % 3) - index) * 0.12),
            )
            for position, task_type in enumerate(task_types)
        ]
        agents.append(
            MultiTaskIntelligentAgent(
                agent_id=agent_id,
                capabilities=capabilities,
                handlers=handlers,
                bus=bus,
                max_parallel_tasks=2,
                memory_enabled=True,
                idempotency_store=store,
            )
        )
    coordinator = ContractNetCoordinator(agents, bus=bus, run_id=end_to_end_run_id)
    stage_records = []
    parsed_path = ""
    anomalies_path = ""
    common = {"end_to_end_run_id": end_to_end_run_id}
    stage_specs: list[tuple[str, dict[str, Any]]] = [
        ("discover.logs", {**common, "roots": ["examples"], "max_files": 10}),
        (
            "parse.logs",
            {
                **common,
                "input_path": "examples/windows_event_sample.xml",
                "out_dir": str(output_dir),
                "out_name": "e2e_parsed.csv",
                "parallel_workers": 1,
            },
        ),
    ]
    for task_type, payload in stage_specs:
        payload["idempotency_key"] = f"{end_to_end_run_id}-{task_type}"
        outcome = coordinator.negotiate(AgentTask.create(task_type, payload))
        stage_records.append(asdict(outcome))
        if outcome.status != "ok" or outcome.result is None:
            break
        if task_type == "parse.logs":
            produced = outcome.result.output.get("produced", [])
            parsed_path = str(produced[0] if isinstance(produced, list) and produced else produced)

    if parsed_path and all(record["status"] == "ok" for record in stage_records):
        remaining = [
            ("route.model", {**common, "input_path": parsed_path, "sample_rows": 200}),
            (
                "detect.anomalies",
                {
                    **common,
                    "input_path": parsed_path,
                    "out_dir": str(output_dir),
                    "sample_rows": 200,
                    "chunk_workers": 1,
                    "correlator_parallel_workers": 1,
                },
            ),
        ]
        for task_type, payload in remaining:
            payload["idempotency_key"] = f"{end_to_end_run_id}-{task_type}"
            outcome = coordinator.negotiate(AgentTask.create(task_type, payload))
            stage_records.append(asdict(outcome))
            if outcome.status != "ok" or outcome.result is None:
                break
            if task_type == "detect.anomalies":
                anomalies_path = str(outcome.result.output.get("anomalies_csv", ""))

    if anomalies_path and all(record["status"] == "ok" for record in stage_records):
        for task_type, payload in (
            (
                "correlate.incidents",
                {
                    **common,
                    "input_path": anomalies_path,
                    "output": str(output_dir / "e2e_incidents_explicit.csv"),
                    "parallel_workers": 1,
                    "sep": ";",
                },
            ),
            ("feedback.apply", {**common, "input_path": anomalies_path, "sep": ";"}),
        ):
            payload["idempotency_key"] = f"{end_to_end_run_id}-{task_type}"
            outcome = coordinator.negotiate(AgentTask.create(task_type, payload))
            stage_records.append(asdict(outcome))
            if outcome.status != "ok":
                break

    result = {
        "run_id": run_id,
        "end_to_end_run_id": end_to_end_run_id,
        "expected_stages": 6,
        "executed_stages": len(stage_records),
        "successful_stages": sum(record["status"] == "ok" for record in stage_records),
        "status": "ok" if len(stage_records) == 6 and all(record["status"] == "ok" for record in stage_records) else "error",
        "parsed_path": parsed_path,
        "anomalies_path": anomalies_path,
        "message_counts": coordinator.message_counts(),
        "stages": stage_records,
    }
    (raw_dir / f"{run_id}__end_to_end.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return result


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    selected_fields = fields or sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=selected_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def append_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    """Ajoute un bloc de résultats bruts sans le conserver en mémoire."""

    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writerows(rows)


def write_representative_messages(path: Path, coordinator: ContractNetCoordinator) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for message in coordinator.transcript:
            handle.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")


def create_figures(
    run_id: str,
    figure_dir: Path,
    run_rows: list[dict[str, Any]],
    adaptation_rows: list[dict[str, Any]],
    recovery: dict[str, Any],
    end_to_end: dict[str, Any],
) -> list[Path]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure_dir.mkdir(parents=True, exist_ok=True)
    created = []

    def line_figure(filename: str, metric: str, ylabel: str) -> None:
        fig, axis = plt.subplots(figsize=(8, 5))
        for architecture in ARCHITECTURES:
            points = []
            for load in sorted({int(row["load"]) for row in run_rows}):
                values = [float(row[metric]) for row in run_rows if row["architecture"] == architecture and int(row["load"]) == load]
                if values:
                    points.append((load, statistics.fmean(values)))
            if points:
                axis.plot([point[0] for point in points], [point[1] for point in points], marker="o", label=architecture)
        axis.set_xlabel("Nombre de tâches")
        axis.set_ylabel(ylabel)
        axis.grid(True, alpha=0.3)
        axis.legend(title="Architecture")
        fig.tight_layout()
        target = figure_dir / filename
        fig.savefig(target, dpi=180)
        plt.close(fig)
        created.append(target)

    line_figure("01_throughput_vs_load.png", "throughput_tasks_sec", "Débit (tâches/s)")
    line_figure("02_p95_latency_vs_load.png", "latency_p95_ms", "Latence p95 (ms)")
    line_figure("03_cpu_vs_load.png", "cpu_machine_normalized_percent", "CPU machine normalisé (%)")
    line_figure("04_rss_vs_load.png", "rss_peak_mb", "RSS maximale (MiB)")
    line_figure("05_messages_per_task.png", "messages_per_task", "Messages CNP par tâche")
    line_figure("06_jain_fairness.png", "jain_fairness", "Indice d'équité de Jain")

    fig, axis = plt.subplots(figsize=(7, 5))
    labels = ["Mémoire OFF", "Mémoire ON"]
    codes = ["C", "D"]
    latency = [statistics.fmean(float(row["latency_p95_ms"]) for row in run_rows if row["architecture"] == code) for code in codes]
    axis.bar(labels, latency)
    axis.set_ylabel("Latence p95 moyenne (ms)")
    axis.set_title("Ablation de la mémoire décisionnelle")
    fig.tight_layout()
    target = figure_dir / "07_memory_ablation.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    created.append(target)

    fig, axis = plt.subplots(figsize=(7, 5))
    recovery_labels = ["Effets dupliqués", "Tâches récupérées", "Pending final", "Lag final"]
    recovery_values = [recovery[key] for key in ("duplicate_effects", "recovered_tasks", "pending_final", "lag_final")]
    axis.bar(recovery_labels, recovery_values)
    axis.tick_params(axis="x", rotation=20)
    axis.set_ylabel("Nombre")
    fig.tight_layout()
    target = figure_dir / "08_recovery_idempotency.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    created.append(target)

    fig, axis = plt.subplots(figsize=(9, 5))
    for agent_id in ("agent-alpha", "agent-beta", "agent-gamma"):
        values = [float(row[f"utility_{agent_id}"]) for row in adaptation_rows if row[f"utility_{agent_id}"] != ""]
        indices = [int(row["index"]) for row in adaptation_rows if row[f"utility_{agent_id}"] != ""]
        axis.plot(indices, values, label=agent_id)
    axis.axvline(59.5, color="black", linestyle="--", linewidth=1, label="changement de phase")
    axis.set_xlabel("Tâche")
    axis.set_ylabel("Utilité proposée")
    axis.legend()
    axis.grid(True, alpha=0.3)
    fig.tight_layout()
    target = figure_dir / "09_agent_utility_over_time.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    created.append(target)

    fig, axis = plt.subplots(figsize=(9, 4))
    stage_names = [record["result"]["task_type"] if record.get("result") else "échec" for record in end_to_end.get("stages", [])]
    colors = ["#2e8b57" if record.get("status") == "ok" else "#b22222" for record in end_to_end.get("stages", [])]
    axis.bar(stage_names, [1] * len(stage_names), color=colors)
    axis.set_ylim(0, 1.2)
    axis.set_yticks([0, 1], ["", "exécutée"])
    axis.tick_params(axis="x", rotation=25)
    axis.set_title(f"Pipeline bout en bout — {end_to_end.get('status', 'unknown')}")
    fig.tight_layout()
    target = figure_dir / "10_end_to_end_pipeline.png"
    fig.savefig(target, dpi=180)
    plt.close(fig)
    created.append(target)
    return created


def write_report(
    path: Path,
    *,
    run_id: str,
    loads: list[int],
    repetitions: int,
    run_rows: list[dict[str, Any]],
    recovery: dict[str, Any],
    end_to_end: dict[str, Any],
) -> None:
    failures = [row for row in run_rows if row["status"] != "ok"]
    lines = [
        "# Rapport d'exécution multi-agents",
        "",
        f"- Run : `{run_id}`",
        f"- Charges : `{loads}`",
        f"- Répétitions par charge et architecture : `{repetitions}`",
        f"- Exécutions principales : `{len(run_rows)}`",
        f"- Exécutions principales en erreur : `{len(failures)}`",
        f"- Reprise : `{json.dumps(recovery, ensure_ascii=False)}`",
        f"- Pipeline bout en bout : `{end_to_end.get('status')}` ({end_to_end.get('successful_stages')}/{end_to_end.get('expected_stages')})",
        "",
        "## Unités de mesure",
        "",
        "- `duration_sec` : temps mural mesuré avec `time.perf_counter()`.",
        "- `throughput_tasks_sec` : tâches réussies divisées par le temps mural.",
        "- latences : millisecondes par tâche; pour C/D, elles incluent négociation et exécution.",
        "- `cpu_time_sec` : somme utilisateur+système du processus Python.",
        "- `cpu_core_equivalent_percent` : temps CPU / temps mural × 100; 100 % correspond à un cœur occupé.",
        "- `cpu_machine_normalized_percent` : valeur précédente divisée par le nombre de processeurs logiques.",
        "- RSS : MiB du processus, échantillonnée toutes les 5 ms; ce n'est pas la mémoire de toute la machine.",
        "- IC à 95 % : approximation normale `moyenne ± 1,96 × erreur standard`.",
        "",
        "## Portée",
        "",
        "Ces résultats décrivent uniquement cette implémentation et cette machine locale. Ils ne constituent pas une validation industrielle ni une preuve multi-VM autonome.",
        "",
    ]
    if failures:
        lines.extend(["## Erreurs observées", ""])
        lines.extend(f"- {row['architecture']} N={row['load']} rép. {row['repetition']} : {row['error'] or row['failed_tasks']}" for row in failures)
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def append_ledger(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row))
        if not exists:
            writer.writeheader()
        writer.writerow(row)


def sha256_manifest(path: Path, run_id: str, files: list[Path]) -> None:
    records = []
    for file_path in sorted(set(files)):
        if not file_path.exists() or not file_path.is_file():
            continue
        content = file_path.read_bytes()
        records.append(
            {
                "path": str(file_path.relative_to(ROOT)).replace("\\", "/"),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"run_id": run_id, "created_at": utc_now(), "files": records}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def environment_manifest(path: Path, run_id: str, args: argparse.Namespace) -> None:
    payload = {
        "run_id": run_id,
        "created_at": utc_now(),
        "python": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "logical_processors": psutil.cpu_count(logical=True) if psutil is not None else None,
        "physical_cores": psutil.cpu_count(logical=False) if psutil is not None else None,
        "ram_bytes": psutil.virtual_memory().total if psutil is not None else None,
        "arguments": vars(args),
        "agent_message_fields": ["run_id", "source", "target", "message_type", "payload", "status", "timestamp"],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne Logminer réellement multi-agents")
    parser.add_argument("--loads", default="100,500,1000,5000")
    parser.add_argument("--repetitions", type=int, default=10)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--base-seed", type=int, default=731_941)
    parser.add_argument("--skip-end-to-end", action="store_true")
    args = parser.parse_args()

    loads = [int(value.strip()) for value in args.loads.split(",") if value.strip()]
    if not loads or any(value <= 0 for value in loads):
        raise ValueError("Les charges doivent être des entiers strictement positifs")
    if args.repetitions < 1 or args.workers < 1:
        raise ValueError("Les répétitions et workers doivent être strictement positifs")

    started_at = utc_now()
    run_id = datetime.now(timezone.utc).strftime("ma_%Y%m%dT%H%M%SZ") + f"_{os.getpid()}"
    raw_dir = PHASE_ROOT / "raw"
    aggregated_dir = PHASE_ROOT / "aggregated"
    logs_dir = PHASE_ROOT / "logs"
    reports_dir = PHASE_ROOT / "reports"
    manifests_dir = PHASE_ROOT / "manifests"
    figure_dir = PHASE_ROOT / "figures" / run_id
    for directory in (raw_dir, aggregated_dir, logs_dir, reports_dir, manifests_dir, figure_dir):
        directory.mkdir(parents=True, exist_ok=True)

    run_rows: list[dict[str, Any]] = []
    raw_runs_path = raw_dir / f"{run_id}__runs.csv"
    raw_tasks_path = raw_dir / f"{run_id}__task_latencies.csv"
    task_fields = ["run_id", "architecture", "load", "repetition", "seed", "task_id", "agent_id", "status", "latency_ms", "error"]
    write_csv(raw_tasks_path, [], task_fields)
    representative_log = logs_dir / f"{run_id}__representative_cnp_messages.jsonl"
    for load in loads:
        for repetition in range(args.repetitions):
            seed = args.base_seed + load * 100 + repetition
            workload = generate_workload(load, seed)
            architecture_order = list(ARCHITECTURES)
            rotation = repetition % len(architecture_order)
            architecture_order = architecture_order[rotation:] + architecture_order[:rotation]
            for architecture in architecture_order:
                run_row, task_rows, coordinator = run_one_architecture(
                    architecture,
                    workload,
                    run_id=run_id,
                    load=load,
                    repetition=repetition,
                    seed=seed,
                    workers=args.workers,
                )
                run_rows.append(run_row)
                append_csv(raw_tasks_path, task_rows, task_fields)
                if load == min(loads) and repetition == 0 and coordinator is not None:
                    write_representative_messages(representative_log, coordinator)
                print(
                    json.dumps(
                        {
                            "architecture": architecture,
                            "load": load,
                            "repetition": repetition,
                            "status": run_row["status"],
                            "throughput": run_row["throughput_tasks_sec"],
                        },
                        ensure_ascii=False,
                    ),
                    flush=True,
                )

    run_rows.sort(key=lambda row: (int(row["load"]), int(row["repetition"]), str(row["architecture"])))
    aggregated = aggregate_runs(run_rows)
    aggregated_path = aggregated_dir / f"{run_id}__statistics.csv"
    write_csv(raw_runs_path, run_rows, RUN_FIELDS)
    write_csv(aggregated_path, aggregated)

    adaptation_rows = adaptation_experiment(run_id, raw_dir)
    recovery = recovery_experiment(run_id, raw_dir)
    if args.skip_end_to_end:
        end_to_end = {"status": "skipped", "expected_stages": 6, "successful_stages": 0, "stages": []}
        end_to_end_path = raw_dir / f"{run_id}__end_to_end.json"
        end_to_end_path.write_text(json.dumps(end_to_end, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        end_to_end = end_to_end_experiment(run_id, raw_dir, logs_dir)
        end_to_end_path = raw_dir / f"{run_id}__end_to_end.json"

    figure_paths = create_figures(run_id, figure_dir, run_rows, adaptation_rows, recovery, end_to_end)
    report_path = reports_dir / f"{run_id}__summary.md"
    write_report(
        report_path,
        run_id=run_id,
        loads=loads,
        repetitions=args.repetitions,
        run_rows=run_rows,
        recovery=recovery,
        end_to_end=end_to_end,
    )
    environment_path = manifests_dir / f"{run_id}__environment.json"
    environment_manifest(environment_path, run_id, args)
    generated_files = [
        raw_runs_path,
        raw_tasks_path,
        aggregated_path,
        raw_dir / f"{run_id}__adaptation.csv",
        raw_dir / f"{run_id}__recovery.json",
        raw_dir / f"{run_id}__recovery_idempotency.sqlite3",
        end_to_end_path,
        raw_dir / f"{run_id}__end_to_end_idempotency.sqlite3",
        representative_log,
        logs_dir / f"{run_id}__end_to_end_messages.jsonl",
        report_path,
        environment_path,
        *figure_paths,
    ]
    generated_files.extend(path for path in (raw_dir / f"{run_id}__end_to_end_outputs").glob("**/*") if path.is_file())
    manifest_path = manifests_dir / f"{run_id}__sha256.json"
    sha256_manifest(manifest_path, run_id, generated_files)
    completed_at = utc_now()
    status = (
        "ok"
        if all(row["status"] == "ok" for row in run_rows)
        and recovery["duplicate_effects"] == 0
        and end_to_end.get("status") == "ok"
        else "partial"
    )
    append_ledger(
        manifests_dir / "EXPERIMENT_LEDGER.csv",
        {
            "run_id": run_id,
            "started_at": started_at,
            "completed_at": completed_at,
            "status": status,
            "loads": json.dumps(loads),
            "repetitions": args.repetitions,
            "workers": args.workers,
            "raw_runs": str(raw_runs_path.relative_to(ROOT)).replace("\\", "/"),
            "statistics": str(aggregated_path.relative_to(ROOT)).replace("\\", "/"),
            "sha256_manifest": str(manifest_path.relative_to(ROOT)).replace("\\", "/"),
        },
    )
    print(
        json.dumps(
            {
                "run_id": run_id,
                "status": status,
                "main_runs": len(run_rows),
                "raw_runs": str(raw_runs_path),
                "statistics": str(aggregated_path),
                "report": str(report_path),
                "figures": [str(path) for path in figure_paths],
                "recovery": recovery,
                "end_to_end_status": end_to_end.get("status"),
                "manifest": str(manifest_path),
         