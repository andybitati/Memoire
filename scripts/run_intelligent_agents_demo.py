"""Demo locale des agents intelligents multi-taches Logminer.

La demo ne depend pas de Redis. Elle prouve trois proprietes:

1. un meme agent choisit entre plusieurs taches selon capacites/priorite;
2. il execute plusieurs types de taches en parallele;
3. il conserve une memoire et publie heartbeat/decisions dans un bus JSONL.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = REPO_ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import LocalMessageBus
from agents.collector_agent import discover_logs
from agents.intelligent_runtime import (
    AgentCapability,
    AgentContext,
    AgentTask,
    InMemoryTaskSource,
    MultiTaskIntelligentAgent,
)
from agents.model_router import route_model, run_routed_detection
from agents.correlator import correlate_anomalies
from pipeline import run_pipeline


def _project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def discover_handler(task: AgentTask, context: AgentContext) -> dict[str, Any]:
    roots = task.payload.get("roots") or ["examples", "data/samples", "data/processed"]
    candidates = discover_logs(
        roots=roots,
        max_files=int(task.payload.get("max_files", 10)),
        max_bytes=int(task.payload.get("max_mb", 10)) * 1024 * 1024,
        bus=context.bus,
        parallel_workers=int(task.payload.get("parallel_workers", 2)),
    )
    return {
        "count": len(candidates),
        "selected": asdict(candidates[0]) if candidates else None,
        "candidates": [asdict(candidate) for candidate in candidates[:5]],
    }


def parse_handler(task: AgentTask, context: AgentContext) -> dict[str, Any]:
    input_path = _project_path(task.payload["input_path"])
    out_dir = _project_path(task.payload.get("out_dir", "data/processed/intelligent_demo"))
    out_name = task.payload.get("out_name", f"{task.task_id}_parsed.csv")
    produced = run_pipeline(
        str(input_path),
        str(out_dir),
        out_name,
        sep=task.payload.get("sep", ";"),
        parallel_workers=int(task.payload.get("parallel_workers", 2)),
    )
    return {"produced": produced, "count": len(produced)}


def route_handler(task: AgentTask, context: AgentContext) -> dict[str, Any]:
    input_path = _project_path(task.payload["input_path"])
    return route_model(
        input_path,
        sep=task.payload.get("sep", "auto"),
        sample_rows=int(task.payload.get("sample_rows", 500)),
    )


def detect_handler(task: AgentTask, context: AgentContext) -> dict[str, Any]:
    input_path = _project_path(task.payload["input_path"])
    out_dir = _project_path(task.payload.get("out_dir", "data/processed/intelligent_demo"))
    out_dir.mkdir(parents=True, exist_ok=True)
    result = run_routed_detection(
        input_path,
        sep=task.payload.get("sep", "auto"),
        sample_rows=int(task.payload.get("sample_rows", 500)),
        output=out_dir / f"{task.task_id}_anomalies.csv",
        incidents_output=out_dir / f"{task.task_id}_incidents.csv",
        window_minutes=int(task.payload.get("window_minutes", 15)),
        chunk_workers=int(task.payload.get("chunk_workers", 2)),
        correlator_parallel_workers=int(task.payload.get("correlator_parallel_workers", 2)),
    )
    return result


def correlate_handler(task: AgentTask, context: AgentContext) -> dict[str, Any]:
    input_path = _project_path(task.payload["input_path"])
    output = _project_path(task.payload.get("output", f"data/processed/intelligent_demo/{task.task_id}_incidents.csv"))
    incidents = correlate_anomalies(
        input_path,
        output,
        sep=task.payload.get("sep", "auto"),
        window_minutes=int(task.payload.get("window_minutes", 15)),
        parallel_workers=int(task.payload.get("parallel_workers", 2)),
    )
    return {"incidents_csv": incidents}


def build_agent(bus_path: Path, memory_path: Path, max_parallel_tasks: int) -> MultiTaskIntelligentAgent:
    bus = LocalMessageBus(bus_path)
    capabilities = [
        AgentCapability("perception", ("discover.logs",), max_parallel=2, confidence=0.95, description="Decouverte de sources"),
        AgentCapability("parser", ("parse.logs",), max_parallel=2, confidence=0.9, description="Parsing multi-format"),
        AgentCapability("router", ("route.model",), max_parallel=4, confidence=0.95, description="Routage par famille"),
        AgentCapability("detector", ("detect.anomalies",), max_parallel=2, confidence=0.85, description="Detection routee"),
        AgentCapability("correlator", ("correlate.incidents",), max_parallel=2, confidence=0.85, description="Correlation incidents"),
    ]
    handlers = {
        "discover.logs": discover_handler,
        "parse.logs": parse_handler,
        "route.model": route_handler,
        "detect.anomalies": detect_handler,
        "correlate.incidents": correlate_handler,
    }
    return MultiTaskIntelligentAgent(
        agent_id="ariel-multitask-agent-1",
        capabilities=capabilities,
        handlers=handlers,
        bus=bus,
        memory_path=memory_path,
        workspace=REPO_ROOT,
        max_parallel_tasks=max_parallel_tasks,
    )


def default_tasks(input_path: str) -> list[AgentTask]:
    return [
        AgentTask.create("discover.logs", {"roots": ["examples", "data/samples", "data/processed"], "max_files": 10}, priority=40),
        AgentTask.create("parse.logs", {"input_path": input_path, "out_name": "intelligent_demo_parsed.csv"}, priority=90),
        AgentTask.create("route.model", {"input_path": input_path, "sample_rows": 200}, priority=70),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo locale des agents intelligents multi-taches")
    parser.add_argument("--input", default="examples/windows_event_sample.xml")
    parser.add_argument("--bus", default="data/processed/intelligent_agent_messages.jsonl")
    parser.add_argument("--memory", default="data/processed/intelligent_agent_memory.json")
    parser.add_argument("--max-parallel-tasks", type=int, default=3)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    agent = build_agent(_project_path(args.bus), _project_path(args.memory), args.max_parallel_tasks)
    source = InMemoryTaskSource(default_tasks(args.input))
    results = agent.run_once(source)
    payload = {
        "branch_goal": "agents intelligents multi-taches",
        "agent": agent.agent_id,
        "capabilities": [asdict(capability) for capability in agent.capabilities],
        "results": [asdict(result) for result in results],
        "bus": str(_project_path(args.bus)),
        "memory": str(_project_path(args.memory)),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"Agent: {payload['agent']}")
        print(f"Taches executees: {len(results)}")
        for result in results:
            print(f"- {result.task_type}: {result.status} ({result.elapsed_sec}s)")
        print(f"Bus: {payload['bus']}")
        print(f"Memoire: {payload['memory']}")
    return 0 if all(result.status == "ok" for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
