"""Bus de communication local entre agents Logminer.

Le bus est volontairement simple pour le prototype: chaque agent publie un
message JSON dans un fichier `.jsonl`. Cela donne une trace exploitable dans le
memoire sans imposer tout de suite Redis, MQTT ou FastAPI.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List
from uuid import uuid4


@dataclass
class AgentMessage:
    """Message standard echange entre agents."""

    run_id: str
    source: str
    target: str
    message_type: str
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "ok"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class LocalMessageBus:
    """Bus append-only stocke dans un fichier JSONL."""

    def __init__(self, path: str | Path = "data/processed/agent_messages.jsonl", run_id: str | None = None):
        self.path = Path(path)
        self.run_id = run_id or uuid4().hex
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def publish(
        self,
        source: str,
        target: str,
        message_type: str,
        payload: Dict[str, Any] | None = None,
        status: str = "ok",
    ) -> AgentMessage:
        message = AgentMessage(
            run_id=self.run_id,
            source=source,
            target=target,
            message_type=message_type,
            payload=dict(payload or {}),
            status=status,
        )

        with self.path.open("a", encoding="utf-8") as f_out:
            f_out.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")

        return message

    def read(self) -> List[AgentMessage]:
        if not self.path.exists():
            return []

        messages: List[AgentMessage] = []
        with self.path.open("r", encoding="utf-8") as f_in:
            for line in f_in:
                line = line.strip()
                if not line:
                    continue
                messages.append(AgentMessage(**json.loads(line)))
        return messages


def filter_messages(messages: Iterable[AgentMessage], run_id: str | None = None) -> List[AgentMessage]:
    """Filtre les messages d'un run donne."""

    if run_id is None:
        return list(messages)
    return [message for message in messages if message.run_id == run_id]
