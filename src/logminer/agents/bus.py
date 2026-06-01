"""Bus de communication entre agents Logminer.

La V1 conserve un bus JSONL local, simple et reproductible. La V2/V3 peut
utiliser Redis Streams avec le meme format de message pour rapprocher le
prototype d'une architecture distribuee.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Protocol
from uuid import uuid4


try:
    import redis
except ImportError:  # pragma: no cover - dependance optionnelle hors V2
    redis = None


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


class MessageBus(Protocol):
    """Contrat minimal partage par les bus JSONL et Redis."""

    run_id: str

    def publish(
        self,
        source: str,
        target: str,
        message_type: str,
        payload: Dict[str, Any] | None = None,
        status: str = "ok",
    ) -> AgentMessage:
        ...

    def read(self) -> List[AgentMessage]:
        ...


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


class RedisMessageBus:
    """Bus Redis Streams pour les runs FastAPI/agents distribues."""

    def __init__(
        self,
        url: str = "redis://localhost:6379/0",
        stream: str = "logminer:events",
        run_id: str | None = None,
        maxlen: int = 10000,
    ):
        if redis is None:
            raise RuntimeError("Le paquet Python 'redis' n'est pas installe")

        self.url = url
        self.stream = stream
        self.run_id = run_id or uuid4().hex
        self.maxlen = maxlen
        self.client = redis.Redis.from_url(url, decode_responses=True)

    def ping(self) -> bool:
        return bool(self.client.ping())

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
        self.client.xadd(
            self.stream,
            {
                "run_id": message.run_id,
                "source": message.source,
                "target": message.target,
                "message_type": message.message_type,
                "payload": json.dumps(message.payload, ensure_ascii=False),
                "status": message.status,
                "timestamp": message.timestamp,
            },
            maxlen=self.maxlen,
            approximate=True,
        )
        return message

    def read(self, run_id: str | None = None, count: int = 100) -> List[AgentMessage]:
        entries = self.client.xrevrange(self.stream, count=count)
        messages: List[AgentMessage] = []
        for _, fields in reversed(entries):
            if run_id is not None and fields.get("run_id") != run_id:
                continue
            payload_raw = fields.get("payload") or "{}"
            try:
                payload = json.loads(payload_raw)
            except json.JSONDecodeError:
                payload = {"raw": payload_raw}
            messages.append(
                AgentMessage(
                    run_id=fields.get("run_id", ""),
                    source=fields.get("source", ""),
                    target=fields.get("target", ""),
                    message_type=fields.get("message_type", ""),
                    payload=payload,
                    status=fields.get("status", "ok"),
                    timestamp=fields.get("timestamp", ""),
                )
            )
        return messages


def filter_messages(messages: Iterable[AgentMessage], run_id: str | None = None) -> List[AgentMessage]:
    """Filtre les messages d'un run donne."""

    if run_id is None:
        return list(messages)
    return [message for message in messages if message.run_id == run_id]
