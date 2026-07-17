"""Campagne locale multi-agents pour mesurer la repartition des taches.

Cette campagne utilise plusieurs agents dans un meme runtime Python. Elle ne
remplace pas la preuve Redis multi-processus, mais elle produit une preuve
rapide que plusieurs agents autonomes peuvent partager une file de taches et
executer des competences differentes en parallele.
"""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from pathlib import Path
from time import perf_counter


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = REPO_ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))
if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from agents.bus import LocalMessageBus
from agents.intelligent_runtime import AgentTask, InMemoryTaskSource
from run_intelligent_agents_demo import build_agent


def _project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def build_tasks(input_path: str, repetitions: int) -> list[AgentTask]:
    tasks: list[AgentTask] = []
    for index in range(max(1, repetitions)):
        tasks.extend(
            [
                AgentTask.create(
                    "discover.logs",
                    {"roots": ["examples", "data/samples", "data/processed"], "max_files": 10},
                    priority=35 + index,
                ),
                AgentTask.create(
                    "parse.logs",
                    {
                        "input_path": input_path,
                        "out_name": f"campaign_{index}_parsed.csv",
                        "out_dir": "data/processed/intelligent_campaign",
                    },
                    priority=90,
                ),
                AgentTask.create("route.model", {"input_path": input_path, "sample_rows": 200}, priority=70),
            ]
        )
    return tasks


def run_agent(agent_index: int, source: InMemoryTaskSource, bus_path: Path, max_parallel_tasks: int) -> list[dict]:
    memory_path = _project_path(f"data/processed/intelligent_campaign_agent_{agent_index}_memory.json")
    agent = build_agent(bus_path, memory_path, max_parallel_tasks)
    agent.agent_id = f"ariel-multitask-agent-{agent_index}"
    results = []
    while True:
        batch = agent.run_once(source)
        if not batch:
            break
        results.extend(asdict(result) for result in batch)
    return results


def summarize(results: list[dict], elapsed_sec: float, agent_count: int) -> dict:
    by_agent: dict[str, int] = {}
    by_type: dict[str, int] = {}
    failures = 0
    for result in results:
        by_agent[result["agent_id"]] = by_agent.get(result["agent_id"], 0) + 1
        by_type[result["task_type"]] = by_type.get(result["task_type"], 0) + 1
        failures += 1 if result["status"] != "ok" else 0
    return {
        "agent_count": agent_count,
        "tasks_total": len(results),
        "tasks_failed": failures,
        "elapsed_sec": round(elapsed_sec, 4),
        "tasks_per_sec": round(len(results) / elapsed_sec, 4) if elapsed_sec else 0,
        "by_agent": by_agent,
        "by_type": by_type,
    }


def write_markdown(path: Path, summary: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Campagne Agents Intelligents Multi-Taches",
        "",
        f"- Agents: {summary['agent_count']}",
        f"- Taches traitees: {summary['tasks_total']}",
        f"- Echecs: {summary['tasks_failed']}",
        f"- Duree: {summary['elapsed_sec']} s",
        f"- Debit: {summary['tasks_per_sec']} taches/s",
        "",
        "## Repartition Par Agent",
        "",
        "| Agent | Taches |",
        "| --- | ---: |",
    ]
    for agent, count in sorted(summary["by_agent"].items()):
        lines.append(f"| {agent} | {count} |")
    lines.extend(["", "## Repartition Par Type", "", "| Type | Taches |", "| --- | ---: |"])
    for task_type, count in sorted(summary["by_type"].items()):
        lines.append(f"| {task_type} | {count} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne locale multi-agents intelligents")
    parser.add_argument("--input", default="examples/windows_event_sample.xml")
    parser.add_argument("--agents", type=int, default=3)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument("--max-parallel-tasks", type=int, default=2)
    parser.add_argument("--bus", default="data/processed/intelligent_campaign_messages.jsonl")
    parser.add_argument("--summary", default="data/processed/intelligent_agents_campaign_summary.json")
    parser.add_argument("--markdown", default="docs/architecture/intelligent_agents_campaign_summary.md")
    args = parser.parse_args()

    started = perf_counter()
    source = InMemoryTaskSource(build_tasks(args.input, args.repetitions))
    bus_path = _project_path(args.bus)
    bus_path.parent.mkdir(parents=True, exist_ok=True)
    LocalMessageBus(bus_path).publish(
        source="campaign",
        target="agents",
        message_type="campaign.started",
        payload={"agents": args.agents, "repetitions": args.repetitions, "input": args.input},
    )
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=max(1, args.agents), thread_name_prefix="intelligent-agent") as executor:
        futures = [
            executor.submit(run_agent, index, source, bus_path, args.max_parallel_tasks)
            for index in range(1, max(1, args.agents) + 1)
        ]
        for future in as_completed(futures):
            results.extend(future.result())
    summary = summarize(results, perf_counter() - started, max(1, args.agents))
    payload = {"summary": summary, "results": results}
    summary_path = _project_path(args.summary)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(_project_path(args.markdown), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["tasks_failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
