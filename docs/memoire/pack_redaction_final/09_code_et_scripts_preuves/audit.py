"""Journal d'audit applicatif Logminer."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_AUDIT_PATH = REPO_ROOT / "data" / "processed" / "logminer_audit.jsonl"


@dataclass
class AuditEntry:
    action: str
    status: str
    actor: str = "system"
    target: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


def write_audit(
    action: str,
    status: str = "ok",
    actor: str = "system",
    target: str = "",
    details: dict[str, Any] | None = None,
    path: str | Path = DEFAULT_AUDIT_PATH,
) -> AuditEntry:
    audit_path = Path(path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    entry = AuditEntry(action=action, status=status, actor=actor, target=target, details=dict(details or {}))
    with audit_path.open("a", encoding="utf-8") as f_out:
        f_out.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
    return entry


def read_audit(limit: int = 100, path: str | Path = DEFAULT_AUDIT_PATH) -> list[AuditEntry]:
    audit_path = Path(path)
    if not audit_path.exists():
        return []
    lines = audit_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    entries: list[AuditEntry] = []
    for line in lines[-max(1, limit) :]:
        if not line.strip():
            continue
        try:
            entries.append(AuditEntry(**json.loads(line)))
        except Exception:
            continue
    return entries
