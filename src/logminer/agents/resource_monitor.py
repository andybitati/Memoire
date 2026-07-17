"""Mesure de consommation des ressources Logminer."""

from __future__ import annotations

import os
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]

try:
    import psutil
except ImportError:  # pragma: no cover - dependance optionnelle
    psutil = None


@dataclass
class AgentResource:
    agent: str
    role: str
    pids: str
    cpu_percent: float
    cpu_machine_percent: float
    memory_mb: float
    status: str
    command: str


def _safe_cmdline(process: Any) -> list[str]:
    try:
        return [str(part) for part in process.cmdline()]
    except Exception:
        return []


def _classify_process(process: Any, current_pid: int) -> tuple[str, str] | None:
    try:
        name = str(process.name()).lower()
        cwd = Path(process.cwd()).resolve()
    except Exception:
        cwd = Path("")

    cmdline = _safe_cmdline(process)
    command = " ".join(cmdline).lower()
    in_repo = False
    try:
        in_repo = cwd == REPO_ROOT or REPO_ROOT in cwd.parents
    except Exception:
        in_repo = str(REPO_ROOT).lower() in command

    if process.pid == current_pid or "src.logminer.api:app" in command or "uvicorn" in command:
        return ("API / Orchestrateur", "parse, route, detecte, correle et expose les agents")
    if "server.mjs" in command and "web" in command:
        return ("Dashboard Web", "visualisation, decisions analyste et proxy API")
    if "redis-server" in name or "redis-server" in command:
        return ("Bus Redis", "messages evenementiels inter-agents")
    if "logminer_intelligent_agent_worker.py" in command:
        return ("Agents intelligents Redis", "workers multi-taches distribues et reprise des taches pending")
    if not in_repo:
        return None
    if "collect_windows_events.ps1" in command or "collector_agent" in command:
        return ("Collecteur", "decouverte et collecte des journaux")
    if "detector.py" in command or "model_router.py" in command:
        return ("Detecteur IA", "routage modele et scoring")
    if "correlator.py" in command:
        return ("Correlateur", "regroupement des anomalies en incidents")
    if "dashboard.py" in command or "streamlit" in command:
        return ("Dashboard Streamlit", "visualisation prototype")
    if "python" in name or "node" in name:
        return ("Processus Logminer", "processus auxiliaire du prototype")
    return None


def snapshot() -> dict[str, Any]:
    if psutil is None:
        return {
            "available": False,
            "agents": [],
            "timestamp": time.time(),
            "message": "psutil non installe; executer pip install -r requirements.txt",
        }

    current_pid = os.getpid()
    logical_cpus = psutil.cpu_count(logical=True) or 1
    grouped: dict[str, dict[str, Any]] = {}
    seen: set[int] = set()
    for process in psutil.process_iter(["pid", "name", "status"]):
        if process.pid in seen:
            continue
        classification = _classify_process(process, current_pid)
        if classification is None:
            continue
        seen.add(process.pid)
        try:
            memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
        except Exception:
            memory_mb = 0.0
        try:
            cpu_percent = round(process.cpu_percent(interval=0.0), 2)
        except Exception:
            cpu_percent = 0.0
        try:
            status = str(process.status())
        except Exception:
            status = "unknown"
        cmdline = _safe_cmdline(process)
        command = " ".join(cmdline)[:220] if cmdline else str(process.name())
        agent_name, role = classification
        group = grouped.setdefault(
            agent_name,
            {
                "role": role,
                "pids": [],
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "statuses": set(),
                "commands": [],
            },
        )
        group["pids"].append(str(process.pid))
        group["cpu_percent"] += cpu_percent
        group["memory_mb"] += memory_mb
        group["statuses"].add(status)
        if len(group["commands"]) < 2:
            group["commands"].append(command)

    agents = [
        AgentResource(
            agent=agent,
            role=str(values["role"]),
            pids=",".join(values["pids"]),
            cpu_percent=round(float(values["cpu_percent"]), 2),
            cpu_machine_percent=round(float(values["cpu_percent"]) / logical_cpus, 2),
            memory_mb=round(float(values["memory_mb"]), 2),
            status="/".join(sorted(values["statuses"])) if values["statuses"] else "unknown",
            command=" | ".join(values["commands"]),
        )
        for agent, values in grouped.items()
    ]
    agents.sort(key=lambda item: item.agent)
    total_cpu_core_percent = round(sum(agent.cpu_percent for agent in agents), 2)
    total_cpu_machine_percent = round(total_cpu_core_percent / logical_cpus, 2)
    return {
        "available": True,
        "agents": [asdict(agent) for agent in agents],
        "agent_count": len(agents),
        "logical_cpus": logical_cpus,
        "cpu_logminer_core_percent": total_cpu_core_percent,
        "cpu_logminer_machine_percent": total_cpu_machine_percent,
        "timestamp": time.time(),
        "message": "Mesure par agent Logminer; CPU equiv. coeur et CPU machine normalise",
    }
