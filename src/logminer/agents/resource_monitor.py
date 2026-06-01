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
class ResourceSnapshot:
    available: bool
    cpu_percent: float | None
    memory_percent: float | None
    memory_used_mb: float | None
    memory_total_mb: float | None
    disk_percent: float | None
    disk_free_gb: float | None
    process_memory_mb: float | None
    process_cpu_percent: float | None
    process_count: int | None
    timestamp: float
    message: str


def snapshot() -> dict[str, Any]:
    if psutil is None:
        return asdict(
            ResourceSnapshot(
                available=False,
                cpu_percent=None,
                memory_percent=None,
                memory_used_mb=None,
                memory_total_mb=None,
                disk_percent=None,
                disk_free_gb=None,
                process_memory_mb=None,
                process_cpu_percent=None,
                process_count=None,
                timestamp=time.time(),
                message="psutil non installe; executer pip install -r requirements.txt",
            )
        )

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(str(REPO_ROOT.anchor or REPO_ROOT))
    process = psutil.Process(os.getpid())
    children = process.children(recursive=True)
    rss = process.memory_info().rss + sum(child.memory_info().rss for child in children if child.is_running())

    return asdict(
        ResourceSnapshot(
            available=True,
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_used_mb=round(memory.used / 1024 / 1024, 2),
            memory_total_mb=round(memory.total / 1024 / 1024, 2),
            disk_percent=disk.percent,
            disk_free_gb=round(disk.free / 1024 / 1024 / 1024, 2),
            process_memory_mb=round(rss / 1024 / 1024, 2),
            process_cpu_percent=process.cpu_percent(interval=0.0),
            process_count=1 + len(children),
            timestamp=time.time(),
            message="ok",
        )
    )
