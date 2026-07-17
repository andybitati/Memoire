"""Agent superviseur autonome Logminer.

Le superviseur ajoute une boucle perception -> etat -> decision -> action au
prototype. Il n'est pas un agent cognitif generaliste, mais il prend de vraies
decisions operationnelles: choisir une source, ajuster les parametres de
routage/correlation selon la charge et lancer le workflow adapte.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter
from typing import Any


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.audit import write_audit
from agents.bus import LocalMessageBus, MessageBus
from agents.collector_agent import DEFAULT_ROOTS, LogCandidate, deployment_roots, discover_logs
from agents.model_router import route_model, run_routed_detection
from agents.resource_monitor import snapshot as resource_snapshot
from pipeline import run_pipeline


@dataclass
class SupervisorPerception:
    """Donnees observees avant decision."""

    candidates: list[dict[str, Any]]
    resources: dict[str, Any]
    run_id: str
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class SupervisorState:
    """Etat interne minimal conserve par cycle."""

    selected_path: str = ""
    selected_kind: str = ""
    cpu_machine_percent: float = 0.0
    memory_mb: float = 0.0
    previous_errors: int = 0
    processed_paths: list[str] = field(default_factory=list)
    recent_families: list[str] = field(default_factory=list)
    analyst_rejections: int = 0


@dataclass
class SupervisorDecision:
    """Decision explicable prise par l'agent."""

    action: str
    selected_path: str
    parse_if_needed: bool
    sample_rows: int
    window_minutes: int
    max_mb: int
    reasons: list[str]


@dataclass
class SupervisorCycleResult:
    """Resultat complet d'un cycle autonome."""

    run_id: str
    perception: SupervisorPerception
    state: SupervisorState
    decision: SupervisorDecision
    workflow: dict[str, Any]
    status: str
    elapsed_sec: float


@dataclass
class SupervisorMemory:
    """Memoire persistante entre cycles autonomes."""

    cycles: int = 0
    successes: int = 0
    errors: int = 0
    processed_paths: list[str] = field(default_factory=list)
    recent_families: list[str] = field(default_factory=list)
    last_decision: dict[str, Any] = field(default_factory=dict)
    last_error: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def _project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def _resource_state(resources: dict[str, Any]) -> tuple[float, float]:
    cpu = float(resources.get("cpu_logminer_machine_percent") or 0.0)
    memory = 0.0
    for agent in resources.get("agents") or []:
        try:
            memory += float(agent.get("memory_mb") or 0.0)
        except (TypeError, ValueError):
            continue
    return round(cpu, 2), round(memory, 2)


def load_memory(path: str | Path = "data/processed/supervisor_state.json") -> SupervisorMemory:
    """Charge la memoire persistante du superviseur."""

    memory_path = _project_path(path)
    if not memory_path.exists():
        return SupervisorMemory()
    try:
        data = json.loads(memory_path.read_text(encoding="utf-8"))
        return SupervisorMemory(**data)
    except Exception:
        return SupervisorMemory(last_error=f"memoire illisible: {memory_path}")


def save_memory(memory: SupervisorMemory, path: str | Path = "data/processed/supervisor_state.json") -> None:
    """Sauvegarde l'etat interne entre deux cycles."""

    memory.updated_at = datetime.now(timezone.utc).isoformat()
    memory_path = _project_path(path)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(asdict(memory), ensure_ascii=False, indent=2), encoding="utf-8")


def _score_candidate(candidate: dict[str, Any], memory: SupervisorMemory) -> tuple[int, list[str]]:
    """Score une source candidate a partir de la perception et de la memoire."""

    path = str(candidate.get("path") or "")
    kind = str(candidate.get("kind") or "")
    priority = int(candidate.get("priority") or 0)
    score = priority
    reasons = [f"priorite collecteur={priority}"]
    if path in memory.processed_paths[-10:]:
        score -= 35
        reasons.append("deja traite recemment")
    if kind in {"hdfs", "bgl"}:
        score += 15
        reasons.append("famille sequentielle a surveiller")
    if kind == "unknown":
        score -= 10
        reasons.append("source inconnue: prudence")
    if any(token in path.lower() for token in ("cef", "cloudtrail", "apache")):
        score += 5
        reasons.append("format robuste utile pour validation")
    return score, reasons


def perceive(
    *,
    roots: list[str] | None = None,
    max_files: int = 20,
    max_mb: int = 100,
    bus: MessageBus | None = None,
    collector_parallel_workers: int = 1,
    use_deployment_roots: bool = False,
) -> SupervisorPerception:
    """Observe les sources disponibles et la charge locale."""

    selected_roots = (
        deployment_roots(include_project=True, extra_roots=roots)
        if use_deployment_roots
        else roots or list(DEFAULT_ROOTS)
    )
    candidates = discover_logs(
        roots=selected_roots,
        max_files=max_files,
        max_bytes=max(1, max_mb) * 1024 * 1024,
        bus=bus,
        parallel_workers=collector_parallel_workers,
    )
    resources = resource_snapshot()
    run_id = bus.run_id if bus is not None else datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return SupervisorPerception(
        candidates=[asdict(candidate) for candidate in candidates],
        resources=resources,
        run_id=run_id,
    )


def select_candidate(perception: SupervisorPerception, memory: SupervisorMemory) -> tuple[dict[str, Any], list[str]]:
    """Choisit une source selon perception + memoire."""

    if not perception.candidates:
        return {}, ["aucun candidat"]
    unprocessed = [candidate for candidate in perception.candidates if str(candidate.get("path") or "") not in memory.processed_paths]
    candidate_pool = unprocessed or perception.candidates
    scored = []
    for candidate in candidate_pool:
        score, reasons = _score_candidate(candidate, memory)
        if unprocessed:
            reasons.append("exploration source non traitee")
        scored.append((score, candidate, reasons))
    scored.sort(key=lambda item: (item[0], str(item[1].get("modified") or "")), reverse=True)
    score, candidate, reasons = scored[0]
    return candidate, [f"score selection={score}", *reasons]


def update_state(perception: SupervisorPerception, memory: SupervisorMemory | None = None) -> SupervisorState:
    """Transforme les observations en etat interne exploitable."""

    agent_memory = memory or SupervisorMemory()
    selected, _ = select_candidate(perception, agent_memory)
    cpu, memory_mb = _resource_state(perception.resources)
    return SupervisorState(
        selected_path=str(selected.get("path") or ""),
        selected_kind=str(selected.get("kind") or ""),
        cpu_machine_percent=cpu,
        memory_mb=memory_mb,
        previous_errors=agent_memory.errors,
        processed_paths=list(agent_memory.processed_paths[-10:]),
        recent_families=list(agent_memory.recent_families[-10:]),
    )


def decide(
    state: SupervisorState,
    *,
    default_max_mb: int = 100,
    selection_reasons: list[str] | None = None,
) -> SupervisorDecision:
    """Choisit une action et des parametres de workflow."""

    reasons: list[str] = list(selection_reasons or [])
    if not state.selected_path:
        return SupervisorDecision(
            action="skip",
            selected_path="",
            parse_if_needed=False,
            sample_rows=0,
            window_minutes=15,
            max_mb=default_max_mb,
            reasons=["aucune source candidate detectee"],
        )

    sample_rows = 1000
    window_minutes = 15
    max_mb = default_max_mb

    if state.cpu_machine_percent >= 70:
        sample_rows = 300
        max_mb = min(max_mb, 5)
        reasons.append("charge CPU elevee: reduction echantillon et volume")
    elif state.cpu_machine_percent >= 35:
        sample_rows = 600
        max_mb = min(max_mb, 20)
        reasons.append("charge CPU moderee: profil prudent")
    else:
        reasons.append("charge locale acceptable")

    if state.previous_errors >= 2:
        sample_rows = min(sample_rows, 300)
        max_mb = min(max_mb, 5)
        reasons.append("erreurs recentes: profil conservateur")

    if state.selected_kind in {"hdfs", "bgl"} or any(token in state.selected_path.lower() for token in ("hdfs", "bgl")):
        window_minutes = 30
        reasons.append("logs systemes sequentiels: fenetre de correlation elargie")

    if state.selected_kind == "unknown":
        sample_rows = min(sample_rows, 300)
        reasons.append("source inconnue: routage prudent vers degradation controlee")

    if state.recent_families.count("fallback") >= 3:
        window_minutes = max(window_minutes, 20)
        reasons.append("fallback frequent: correlation plus large pour analyse humaine")

    suffix = Path(state.selected_path).suffix.lower()
    parse_if_needed = suffix not in {".csv", ".parquet"}
    return SupervisorDecision(
        action="run_workflow",
        selected_path=state.selected_path,
        parse_if_needed=parse_if_needed,
        sample_rows=sample_rows,
        window_minutes=window_minutes,
        max_mb=max_mb,
        reasons=reasons,
    )


def act(
    decision: SupervisorDecision,
    *,
    out_dir: str | Path = "data/processed",
    bus: MessageBus | None = None,
    parser_parallel_workers: int = 1,
    chunk_workers: int = 1,
    correlator_parallel_workers: int = 1,
) -> dict[str, Any]:
    """Execute l'action decidee par le superviseur."""

    if decision.action == "skip":
        return {"action": "skip", "reason": "; ".join(decision.reasons)}

    input_path = _project_path(decision.selected_path)
    output_dir = _project_path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    run_id = bus.run_id if bus is not None else datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if bus is not None:
        bus.publish(
            source="supervisor",
            target="orchestrator",
            message_type="supervisor.action.started",
            payload=asdict(decision),
        )

    source_for_detection = input_path
    parsed_csv = ""
    timings: dict[str, float] = {}
    if decision.parse_if_needed:
        parse_started = perf_counter()
        parsed_name = f"supervisor_{run_id}_parsed.csv"
        produced = run_pipeline(
            str(input_path),
            str(output_dir),
            parsed_name,
            sep=";",
            parallel_workers=parser_parallel_workers,
        )
        if not produced:
            raise RuntimeError(f"Parsing sans sortie pour {input_path}")
        source_for_detection = _project_path(produced[0])
        parsed_csv = str(source_for_detection)
        timings["parse_sec"] = round(perf_counter() - parse_started, 4)

    route_preview = route_model(source_for_detection, sample_rows=decision.sample_rows)
    anomalies_csv = output_dir / f"supervisor_{run_id}_anomalies.csv"
    incidents_csv = output_dir / f"supervisor_{run_id}_incidents.csv"
    result = run_routed_detection(
        source_for_detection,
        sample_rows=decision.sample_rows,
        output=anomalies_csv,
        incidents_output=incidents_csv,
        window_minutes=decision.window_minutes,
        chunk_workers=chunk_workers,
        correlator_parallel_workers=correlator_parallel_workers,
    )
    timings.update(result.get("timings") or {})
    workflow = {
        "action": decision.action,
        "input_path": str(input_path),
        "parsed_csv": parsed_csv,
        "route_preview": route_preview,
        **result,
        "timings": timings,
    }

    if bus is not None:
        bus.publish(
            source="supervisor",
            target="audit",
            message_type="supervisor.action.completed",
            payload={
                "selected_path": decision.selected_path,
                "family": (result.get("route") or {}).get("family"),
                "anomalies_csv": result.get("anomalies_csv"),
                "incidents_csv": result.get("incidents_csv"),
            },
        )
    return workflow


def run_supervisor_cycle(
    *,
    roots: list[str] | None = None,
    max_files: int = 20,
    max_mb: int = 100,
    out_dir: str | Path = "data/processed",
    bus_path: str | Path = "data/processed/supervisor_messages.jsonl",
    memory_path: str | Path = "data/processed/supervisor_state.json",
    run_id: str | None = None,
    parser_parallel_workers: int = 1,
    chunk_workers: int = 1,
    correlator_parallel_workers: int = 1,
    collector_parallel_workers: int = 1,
    use_deployment_roots: bool = False,
) -> SupervisorCycleResult:
    """Execute un cycle autonome complet."""

    started = perf_counter()
    bus = LocalMessageBus(bus_path, run_id=run_id)
    memory = load_memory(memory_path)
    perception = perceive(
        roots=roots,
        max_files=max_files,
        max_mb=max_mb,
        bus=bus,
        collector_parallel_workers=collector_parallel_workers,
        use_deployment_roots=use_deployment_roots,
    )
    selected, selection_reasons = select_candidate(perception, memory)
    state = update_state(perception, memory)
    if selected:
        state.selected_path = str(selected.get("path") or state.selected_path)
        state.selected_kind = str(selected.get("kind") or state.selected_kind)
    decision = decide(state, default_max_mb=max_mb, selection_reasons=selection_reasons)
    status = "ok"
    try:
        workflow = act(
            decision,
            out_dir=out_dir,
            bus=bus,
            parser_parallel_workers=parser_parallel_workers,
            chunk_workers=chunk_workers,
            correlator_parallel_workers=correlator_parallel_workers,
        )
    except Exception as exc:
        status = "error"
        workflow = {"error": str(exc)}
        bus.publish("supervisor", "audit", "supervisor.action.failed", {"error": str(exc)}, status="error")

    result = SupervisorCycleResult(
        run_id=bus.run_id,
        perception=perception,
        state=state,
        decision=decision,
        workflow=workflow,
        status=status,
        elapsed_sec=round(perf_counter() - started, 4),
    )
    memory.cycles += 1
    memory.last_decision = asdict(decision)
    if status == "ok":
        memory.successes += 1
        memory.last_error = ""
        if decision.selected_path:
            memory.processed_paths.append(decision.selected_path)
            memory.processed_paths = memory.processed_paths[-50:]
        family = str((workflow.get("route") or {}).get("family") or "")
        if family:
            memory.recent_families.append(family)
            memory.recent_families = memory.recent_families[-50:]
    else:
        memory.errors += 1
        memory.last_error = str(workflow.get("error") or "unknown")
    save_memory(memory, memory_path)
    write_audit(
        action="supervisor.cycle",
        status=status,
        actor="supervisor",
        target=decision.selected_path,
        details={
            "decision": asdict(decision),
            "workflow": workflow,
            "elapsed_sec": result.elapsed_sec,
        },
    )
    return result


def run_supervisor_campaign(
    *,
    cycles: int,
    roots: list[str] | None = None,
    max_files: int = 20,
    max_mb: int = 100,
    out_dir: str | Path = "data/processed",
    bus_path: str | Path = "data/processed/supervisor_messages.jsonl",
    memory_path: str | Path = "data/processed/supervisor_state.json",
    parallel_workers: int = 1,
    parser_parallel_workers: int = 1,
    chunk_workers: int = 1,
    correlator_parallel_workers: int = 1,
    collector_parallel_workers: int = 1,
    use_deployment_roots: bool = False,
) -> list[SupervisorCycleResult]:
    """Execute plusieurs cycles autonomes en conservant la memoire."""

    results: list[SupervisorCycleResult] = []
    workers = min(max(1, int(parallel_workers)), max(1, cycles))
    if workers > 1:
        bus_base = Path(bus_path)
        memory_base = Path(memory_path)
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="logminer-supervisor") as executor:
            futures = {
                executor.submit(
                    run_supervisor_cycle,
                    roots=roots,
                    max_files=max_files,
                    max_mb=max_mb,
                    out_dir=out_dir,
                    bus_path=bus_base.with_name(f"{bus_base.stem}_{index}{bus_base.suffix}"),
                    memory_path=memory_base.with_name(f"{memory_base.stem}_{index}{memory_base.suffix}"),
                    run_id=f"supervisor-campaign-parallel-{index}",
                    parser_parallel_workers=parser_parallel_workers,
                    chunk_workers=chunk_workers,
                    correlator_parallel_workers=correlator_parallel_workers,
                    collector_parallel_workers=collector_parallel_workers,
                    use_deployment_roots=use_deployment_roots,
                ): index
                for index in range(1, max(1, cycles) + 1)
            }
            ordered: dict[int, SupervisorCycleResult] = {}
            for future in as_completed(futures):
                ordered[futures[future]] = future.result()
        return [ordered[index] for index in sorted(ordered)]

    for index in range(1, max(1, cycles) + 1):
        result = run_supervisor_cycle(
            roots=roots,
            max_files=max_files,
            max_mb=max_mb,
            out_dir=out_dir,
            bus_path=bus_path,
            memory_path=memory_path,
            run_id=f"supervisor-campaign-{index}",
            parser_parallel_workers=parser_parallel_workers,
            chunk_workers=chunk_workers,
            correlator_parallel_workers=correlator_parallel_workers,
            collector_parallel_workers=collector_parallel_workers,
            use_deployment_roots=use_deployment_roots,
        )
        results.append(result)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent superviseur autonome Logminer")
    parser.add_argument("--root", action="append", dest="roots", default=[], help="Racine a observer")
    parser.add_argument("--max-files", type=int, default=20)
    parser.add_argument("--max-mb", type=int, default=100)
    parser.add_argument("--out-dir", default="data/processed")
    parser.add_argument("--bus", default="data/processed/supervisor_messages.jsonl")
    parser.add_argument("--memory", default="data/processed/supervisor_state.json")
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--parallel-workers", type=int, default=1, help="Nombre de cycles superviseur executes en parallele")
    parser.add_argument("--parser-parallel-workers", type=int, default=1, help="Nombre de fichiers parses en parallele par cycle")
    parser.add_argument("--chunk-workers", type=int, default=1, help="Nombre de chunks d'inference en parallele par cycle")
    parser.add_argument("--correlator-parallel-workers", type=int, default=1, help="Nombre de groupes correles en parallele par cycle")
    parser.add_argument("--collector-parallel-workers", type=int, default=1, help="Nombre de racines/fichiers decouverts en parallele")
    parser.add_argument("--deployment-roots", action="store_true", help="Ajoute les chemins de logs standards de l'OS courant")
    args = parser.parse_args()

    if args.cycles > 1:
        results = run_supervisor_campaign(
            cycles=args.cycles,
            roots=args.roots or None,
            max_files=args.max_files,
            max_mb=args.max_mb,
            out_dir=args.out_dir,
            bus_path=args.bus,
            memory_path=args.memory,
            parallel_workers=args.parallel_workers,
            parser_parallel_workers=args.parser_parallel_workers,
            chunk_workers=args.chunk_workers,
            correlator_parallel_workers=args.correlator_parallel_workers,
            collector_parallel_workers=args.collector_parallel_workers,
            use_deployment_roots=args.deployment_roots,
        )
        print(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2))
        return 0 if all(result.status == "ok" for result in results) else 1

    result = run_supervisor_cycle(
        roots=args.roots or None,
        max_files=args.max_files,
        max_mb=args.max_mb,
        out_dir=args.out_dir,
        bus_path=args.bus,
        memory_path=args.memory,
        run_id=args.run_id,
        parser_parallel_workers=args.parser_parallel_workers,
        chunk_workers=args.chunk_workers,
        correlator_parallel_workers=args.correlator_parallel_workers,
        collector_parallel_workers=args.collector_parallel_workers,
        use_deployment_roots=args.deployment_roots,
    )
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0 if result.status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
