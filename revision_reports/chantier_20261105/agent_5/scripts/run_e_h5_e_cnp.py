"""E-H5 (mémoire C contre D) et E-CNP (Contract Net contre table statique).

Le programme réutilise sans modification les agents, profils, poids et charges
de ``scripts/run_true_multi_agent_experiments.py``. Seuls les handlers sont
enveloppés pour injecter une durée de service et des échecs déterminés à
l'avance. Hors mode ``--smoke``, il refuse de s'exécuter si le protocole n'est
pas commité et inscrit au registre avec l'empreinte de son contenu.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "scripts"))

import run_true_multi_agent_experiments as bench  # noqa: E402
from agents.contract_net import ContractNetCoordinator  # noqa: E402
from agents.intelligent_runtime import AgentTask, MultiTaskIntelligentAgent  # noqa: E402

CHANTIER = ROOT / "revision_reports/chantier_20261105"
REGISTRY = CHANTIER / "PROTOCOLES_PREENREGISTRES.md"
SOURCES = (
    ROOT / "scripts/run_true_multi_agent_experiments.py",
    ROOT / "src/logminer/agents/contract_net.py",
    ROOT / "src/logminer/agents/intelligent_runtime.py",
    ROOT / "experiments/phase_multi_agent/configs/agent_policy.json",
)
EXPERIMENTS = {
    "E-H5": "E-H5-MEMORY-RELIABILITY",
    "E-CNP": "E-CNP-STATIC-ASSIGNMENT",
}
LOAD = 1000
WORKERS = 3
BASE_SEED = 20_261_105
SEEDS = tuple(BASE_SEED + index for index in range(30))
SENSITIVITY_SEEDS = SEEDS[:10]
SERVICE_SEC = 0.002
SLOW_SERVICE_SEC = 0.010
SILENT_FAILURE_START = 300
FAILURE_DEGRADATION_TOLERANCE = 0.01
THROUGHPUT_FLOOR = 0.95
THROUGHPUT_GAIN = 1.05
T_CRITICAL_95 = {1: 12.706204736432095, 9: 2.2621571627409915, 29: 2.045229642132703}
RUN_FIELDS = [
    "experiment", "scenario", "arm", "workers", "seed", "load", "successful_tasks",
    "final_failures", "executions", "first_execution_failures", "first_execution_failure_rate",
    "executions_per_task", "reassignments", "duration_sec", "throughput_tasks_sec",
    "latency_mean_ms", "latency_median_ms", "latency_p95_ms", "jain_executions",
    "messages_per_task", "executions_by_agent",
]


@dataclass(frozen=True)
class Scenario:
    """Conditions d'injection, identiques pour tous les bras d'une même graine."""

    name: str
    failure_probability: float = 0.0
    silent_agent: str = ""
    service_by_agent: dict[str, float] = field(default_factory=dict)
    default_service: float = SERVICE_SEC


E_H5_SCENARIOS = tuple(
    Scenario(name=f"best_declared_failure_p{int(level * 100):02d}", failure_probability=level)
    for level in (0.3, 0.6, 0.9)
)
E_CNP_SCENARIOS = (
    Scenario(name="s0_cost_no_service", default_service=0.0),
    Scenario(name="s1_nominal"),
    Scenario(name="s2_best_declared_failure_p30", failure_probability=0.3),
    Scenario(name="s3_silent_gamma_failure", silent_agent="agent-gamma"),
    Scenario(name="s4_slow_gamma", service_by_agent={"agent-gamma": SLOW_SERVICE_SEC}),
)
E_CNP_DECISION_SCENARIOS = tuple(item.name for item in E_CNP_SCENARIOS if item.name != "s0_cost_no_service")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def unit_draw(seed: int, task_id: str, agent_id: str) -> float:
    """Tirage uniforme reproductible, indépendant de l'ordre d'exécution et du bras."""

    material = f"{seed}|{task_id}|{agent_id}".encode("utf-8")
    return int.from_bytes(hashlib.blake2b(material, digest_size=8).digest(), "big") / 2**64


def task_index(task_id: str) -> int:
    return int(task_id.rsplit("-", 1)[1])


def declared_order(agents: list[MultiTaskIntelligentAgent]) -> dict[str, list[MultiTaskIntelligentAgent]]:
    """Ordre décroissant de confiance déclarée, identifiant en départage."""

    table: dict[str, list[MultiTaskIntelligentAgent]] = {}
    for task_type in bench.TASK_TYPES:
        def confidence(agent: MultiTaskIntelligentAgent) -> float:
            return max(cap.confidence for cap in agent.capabilities if cap.supports(task_type))

        table[task_type] = sorted(agents, key=lambda agent: (-confidence(agent), agent.agent_id))
    return table


class Instrumentation:
    """Journal des exécutions réelles, tentative par tentative."""

    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.attempts: dict[str, list[tuple[str, bool]]] = {}

    def record(self, task_id: str, agent_id: str, ok: bool) -> None:
        with self.lock:
            self.attempts.setdefault(task_id, []).append((agent_id, ok))


def instrument(
    agents: list[MultiTaskIntelligentAgent], scenario: Scenario, seed: int, journal: Instrumentation
) -> None:
    best = {task_type: order[0].agent_id for task_type, order in declared_order(agents).items()}

    def make_handler(agent_id: str):
        service = scenario.service_by_agent.get(agent_id, scenario.default_service)

        def handler(task: AgentTask, context: Any) -> dict[str, Any]:
            output = bench.synthetic_effect(task, context)
            if service > 0:
                time.sleep(service)
            fails = False
            if scenario.failure_probability > 0 and best[task.task_type] == agent_id:
                fails = unit_draw(seed, task.task_id, agent_id) < scenario.failure_probability
            if agent_id == scenario.silent_agent and task_index(task.task_id) >= SILENT_FAILURE_START:
                fails = True
            journal.record(task.task_id, agent_id, not fails)
            if fails:
                raise RuntimeError("injected_failure")
            return output

        return handler

    for agent in agents:
        handler = make_handler(agent.agent_id)
        agent.handlers = {task_type: handler for task_type in bench.TASK_TYPES}


def run_static(
    agents: list[MultiTaskIntelligentAgent], tasks: list[AgentTask], workers: int
) -> tuple[list[tuple[str, bool, float, int]], int]:
    """Table type de tâche -> agents ordonnés, avec le même repli que le Contract Net."""

    table = declared_order(agents)

    def run_one(task: AgentTask) -> tuple[str, bool, float, int]:
        started = time.perf_counter()
        reassignments = 0
        success = False
        for index, agent in enumerate(table[task.task_type]):
            if index > 0:
                reassignments += 1
            if not agent.accept(task):
                continue
            result = agent.execute_task(task, 0.0, [])
            if result.status == "ok":
                success = True
                break
        return task.task_id, success, time.perf_counter() - started, reassignments

    if workers <= 1:
        return [run_one(task) for task in tasks], 0
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="static") as executor:
        futures = [executor.submit(run_one, task) for task in tasks]
        return [future.result() for future in as_completed(futures)], 0


def run_contract_net(
    agents: list[MultiTaskIntelligentAgent], tasks: list[AgentTask], workers: int, run_id: str
) -> tuple[list[tuple[str, bool, float, int]], int]:
    coordinator = ContractNetCoordinator(agents, run_id=run_id)
    outcomes = coordinator.run_tasks(tasks, max_workers=workers)
    rows = [
        (item.task_id, item.status == "ok", item.elapsed_sec, int(item.reassignments)) for item in outcomes
    ]
    return rows, sum(coordinator.message_counts().values())


def execute_run(experiment: str, scenario: Scenario, arm: str, seed: int, workers: int, load: int) -> dict[str, Any]:
    run_id = f"{experiment}-{scenario.name}-{arm}-{seed}-{workers}"
    agents = bench.build_agents(memory_enabled=arm == "D", run_id=run_id)
    journal = Instrumentation()
    instrument(agents, scenario, seed, journal)
    tasks = [bench.agent_task(item) for item in bench.generate_workload(load, seed)]
    started = time.perf_counter()
    if arm == "static":
        rows, messages = run_static(agents, tasks, workers)
    else:
        rows, messages = run_contract_net(agents, tasks, workers, run_id)
    duration = time.perf_counter() - started

    if len(rows) != load or len({row[0] for row in rows}) != load:
        raise AssertionError(f"{run_id}: tâches perdues ou dupliquées")
    if arm != "D" and any(agent.memory.completed_tasks for agent in agents):
        raise AssertionError(f"{run_id}: mémoire écrite dans un bras sans mémoire")
    executed = journal.attempts
    if set(executed) != {row[0] for row in rows}:
        raise AssertionError(f"{run_id}: tâche sans exécution journalisée")
    first_failures = sum(1 for attempts in executed.values() if not attempts[0][1])
    by_agent = Counter(agent_id for attempts in executed.values() for agent_id, _ok in attempts)
    executions = sum(by_agent.values())
    latencies = [row[2] * 1000.0 for row in rows]
    successes = sum(1 for row in rows if row[1])
    return {
        "experiment": experiment,
        "scenario": scenario.name,
        "arm": arm,
        "workers": workers,
        "seed": seed,
        "load": load,
        "successful_tasks": successes,
        "final_failures": load - successes,
        "executions": executions,
        "first_execution_failures": first_failures,
        "first_execution_failure_rate": first_failures / load,
        "executions_per_task": executions / load,
        "reassignments": sum(row[3] for row in rows),
        "duration_sec": duration,
        "throughput_tasks_sec": load / duration,
        "latency_mean_ms": statistics.fmean(latencies),
        "latency_median_ms": statistics.median(latencies),
        "latency_p95_ms": bench.percentile(latencies, 0.95),
        "jain_executions": bench.jain_index([by_agent.get(agent.agent_id, 0) for agent in agents]),
        "messages_per_task": messages / load,
        "executions_by_agent": json.dumps(dict(sorted(by_agent.items())), sort_keys=True),
    }


def interval(values: list[float]) -> dict[str, float]:
    count = len(values)
    mean = statistics.fmean(values)
    sd = statistics.stdev(values)
    half = T_CRITICAL_95[count - 1] * sd / count**0.5
    return {"n": count, "mean": mean, "sd": sd, "ci95_lower": mean - half, "ci95_upper": mean + half}


def contrast(rows: list[dict[str, Any]], scenario: str, arm: str, reference: str, workers: int) -> dict[str, Any]:
    subset = [row for row in rows if row["scenario"] == scenario and row["workers"] == workers]
    by_arm = {
        name: {row["seed"]: row for row in subset if row["arm"] == name} for name in (arm, reference)
    }
    seeds = sorted(set(by_arm[arm]) & set(by_arm[reference]))
    if not seeds or len(seeds) != len(by_arm[arm]) or len(seeds) != len(by_arm[reference]):
        raise AssertionError(f"Appariement incomplet: {scenario}, {arm}, {reference}")

    def differences(metric: str) -> list[float]:
        return [float(by_arm[arm][seed][metric]) - float(by_arm[reference][seed][metric]) for seed in seeds]

    ratios = [
        float(by_arm[arm][seed]["throughput_tasks_sec"]) / float(by_arm[reference][seed]["throughput_tasks_sec"])
        for seed in seeds
    ]
    return {
        "scenario": scenario,
        "contrast": f"{arm}_minus_{reference}",
        "workers": workers,
        "first_execution_failure_rate_delta": interval(differences("first_execution_failure_rate")),
        "executions_per_task_delta": interval(differences("executions_per_task")),
        "final_failures_delta": interval(differences("final_failures")),
        "latency_p95_ms_delta": interval(differences("latency_p95_ms")),
        "jain_executions_delta": interval(differences("jain_executions")),
        "throughput_ratio": interval(ratios),
        "mean_first_execution_failure_rate": {
            name: statistics.fmean(float(by_arm[name][seed]["first_execution_failure_rate"]) for seed in seeds)
            for name in (arm, reference)
        },
        "mean_throughput_tasks_sec": {
            name: statistics.fmean(float(by_arm[name][seed]["throughput_tasks_sec"]) for seed in seeds)
            for name in (arm, reference)
        },
        "mean_messages_per_task": {
            name: statistics.fmean(float(by_arm[name][seed]["messages_per_task"]) for seed in seeds)
            for name in (arm, reference)
        },
    }


def decide_memory_level(item: dict[str, Any]) -> bool:
    return bool(
        item["first_execution_failure_rate_delta"]["ci95_upper"] < 0
        and item["throughput_ratio"]["ci95_lower"] >= THROUGHPUT_FLOOR
    )


def decide_contract_net(item: dict[str, Any]) -> str:
    failure = item["first_execution_failure_rate_delta"]
    ratio = item["throughput_ratio"]
    fewer_failures = failure["ci95_upper"] < 0 and ratio["ci95_lower"] >= THROUGHPUT_FLOOR
    faster = ratio["ci95_lower"] > THROUGHPUT_GAIN and failure["ci95_upper"] <= FAILURE_DEGRADATION_TOLERANCE
    if fewer_failures or faster:
        return "favorable"
    if failure["ci95_lower"] > 0 or (ratio["ci95_upper"] < THROUGHPUT_FLOOR and failure["ci95_upper"] >= 0):
        return "defavorable"
    return "indetermine"


def global_memory(levels: dict[str, bool]) -> str:
    if all(levels.values()):
        return "gain_general"
    return "gain_conditionnel" if any(levels.values()) else "aucun_gain"


def global_contract_net(decisions: dict[str, str]) -> str:
    favorable = [name for name in E_CNP_DECISION_SCENARIOS if decisions[name] == "favorable"]
    if len(favorable) == len(E_CNP_DECISION_SCENARIOS):
        return "avantage_general"
    return "avantage_conditionnel" if favorable else "aucun_avantage"


def require_preregistered(experiment_id: str, protocol: Path) -> None:
    protocol_rel = relative(protocol)
    digest = sha256(protocol)
    if digest not in REGISTRY.read_text(encoding="utf-8"):
        raise SystemExit(f"Protocole absent du registre: {digest}")
    committed = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"HEAD:{protocol_rel}"], capture_output=True, check=False
    )
    if committed.returncode != 0:
        raise SystemExit(f"Protocole non commité: {protocol_rel}")
    # La copie de travail peut différer du commit par ses fins de ligne seulement.
    if committed.stdout.replace(b"\r\n", b"\n") != protocol.read_bytes().replace(b"\r\n", b"\n"):
        raise SystemExit("La copie de travail du protocole diffère du commit")
    log = subprocess.run(
        ["git", "-C", str(ROOT), "log", "-1", "--format=%s", "--", protocol_rel],
        capture_output=True, text=True, check=True,
    ).stdout
    if experiment_id not in log:
        raise SystemExit(f"Commit de protocole inattendu: {log.strip()}")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RUN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def plan_rows(key: str, seeds: tuple[int, ...], sensitivity: tuple[int, ...]) -> list[tuple[Scenario, str, int, int]]:
    plan: list[tuple[Scenario, str, int, int]] = []
    if key == "E-H5":
        arms = ("C", "D")
        scenarios = E_H5_SCENARIOS
    else:
        arms = ("static", "C", "D")
        scenarios = E_CNP_SCENARIOS
    for scenario in scenarios:
        for position, seed in enumerate(seeds):
            rotation = position % len(arms)
            for arm in arms[rotation:] + arms[:rotation]:
                plan.append((scenario, arm, seed, WORKERS))
    if key == "E-H5":
        for scenario in scenarios:
            for position, seed in enumerate(sensitivity):
                rotation = position % len(arms)
                for arm in arms[rotation:] + arms[:rotation]:
                    plan.append((scenario, arm, seed, 1))
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("experiment", choices=sorted(EXPERIMENTS))
    parser.add_argument("--smoke", type=Path, help="Essai technique sur graines réservées, hors artefacts")
    args = parser.parse_args()

    experiment_id = EXPERIMENTS[args.experiment]
    protocol = CHANTIER / "agent_5/protocoles" / f"{experiment_id}.md"
    if args.smoke is not None:
        seeds, sensitivity, load = (1, 2), (1, 2), 40
        out = args.smoke
    else:
        require_preregistered(experiment_id, protocol)
        seeds, sensitivity, load = SEEDS, SENSITIVITY_SEEDS, LOAD
        out = ROOT / "experiments/phase_revision_20261105" / experiment_id
        if (out / "summary.json").exists():
            raise SystemExit(f"Artefacts déjà présents, refus d'écraser: {out}")
    out.mkdir(parents=True, exist_ok=True)

    started = datetime.now(timezone.utc).isoformat()
    plan = plan_rows(args.experiment, seeds, sensitivity)
    rows: list[dict[str, Any]] = []
    for index, (scenario, arm, seed, workers) in enumerate(plan, start=1):
        rows.append(execute_run(experiment_id, scenario, arm, seed, workers, load))
        if index % 30 == 0:
            print(f"{index}/{len(plan)} exécutions", flush=True)

    runs_path = out / "runs.csv"
    write_csv(runs_path, rows)

    if args.smoke is not None:
        if args.experiment == "E-H5":
            for scenario in E_H5_SCENARIOS:
                contrast(rows, scenario.name, "D", "C", WORKERS)
        else:
            for scenario in E_CNP_SCENARIOS:
                contrast(rows, scenario.name, "C", "static", WORKERS)
                contrast(rows, scenario.name, "D", "static", WORKERS)
        print(f"essai technique conforme : {len(rows)} exécutions, invariants vérifiés")
        return 0

    summary: dict[str, Any] = {
        "experiment_id": experiment_id,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "load": load,
        "workers_primary": WORKERS,
        "seeds": list(seeds),
        "service_sec": SERVICE_SEC,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "processor_count": __import__("os").cpu_count(),
        },
    }
    if args.experiment == "E-H5":
        primary = {s.name: contrast(rows, s.name, "D", "C", WORKERS) for s in E_H5_SCENARIOS}
        sensitivity_results = {s.name: contrast(rows, s.name, "D", "C", 1) for s in E_H5_SCENARIOS}
        levels = {name: decide_memory_level(item) for name, item in primary.items()}
        summary.update(
            contrasts=primary,
            sensitivity_sequential=sensitivity_results,
            level_gain=levels,
            global_decision=global_memory(levels),
        )
    else:
        by_contrast: dict[str, Any] = {}
        for arm in ("C", "D"):
            contrasts = {s.name: contrast(rows, s.name, arm, "static", WORKERS) for s in E_CNP_SCENARIOS}
            decisions = {name: decide_contract_net(contrasts[name]) for name in E_CNP_DECISION_SCENARIOS}
            by_contrast[f"{arm}_minus_static"] = {
                "contrasts": contrasts,
                "decisions": decisions,
                "global_decision": global_contract_net(decisions),
            }
        summary["results"] = by_contrast
        summary["global_decision_primary"] = by_contrast["C_minus_static"]["global_decision"]

    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    manifest = out / "MANIFEST_SHA256.csv"
    entries = [("protocol", protocol), ("runner", Path(__file__).resolve())]
    entries += [("source", path) for path in SOURCES]
    entries += [("artifact", runs_path), ("artifact", summary_path)]
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "path", "sha256", "bytes"])
        writer.writeheader()
        for role, path in entries:
            writer.writerow(
                {"role": role, "path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size}
            )
    print(f"terminé : {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
