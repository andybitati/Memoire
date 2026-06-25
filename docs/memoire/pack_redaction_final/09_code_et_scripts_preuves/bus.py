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

try:
    import paho.mqtt.client as mqtt
except ImportError:  # pragma: no cover - dependance optionnelle hors V2/V3
    mqtt = None


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

    def stream_info(self, stream: str | None = None) -> Dict[str, Any]:
        """Retourne un etat leger du Stream Redis."""

        stream_name = stream or self.stream
        try:
            return dict(self.client.xinfo_stream(stream_name))
        except Exception:
            return {"name": stream_name, "exists": False, "length": 0}

    def ensure_group(self, group: str, stream: str | None = None, start_id: str = "0") -> None:
        """Cree un consumer group Redis Streams si necessaire."""

        stream_name = stream or self.stream
        try:
            self.client.xgroup_create(stream_name, group, id=start_id, mkstream=True)
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

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

    def enqueue_job(
        self,
        payload: Dict[str, Any],
        *,
        stream: str = "logminer:jobs",
        job_type: str = "workflow.run",
    ) -> str:
        """Publie un job persistant pour un worker separe."""

        job_payload = dict(payload)
        job_payload.setdefault("run_id", self.run_id)
        job_payload.setdefault("job_type", job_type)
        job_payload.setdefault("status", "queued")
        job_payload.setdefault("created_at", datetime.now(timezone.utc).isoformat())
        return str(
            self.client.xadd(
                stream,
                {
                    "run_id": str(job_payload.get("run_id", "")),
                    "job_type": str(job_payload.get("job_type", job_type)),
                    "payload": json.dumps(job_payload, ensure_ascii=False),
                    "status": "queued",
                    "created_at": str(job_payload.get("created_at", "")),
                },
                maxlen=self.maxlen,
                approximate=True,
            )
        )

    def read_group_jobs(
        self,
        *,
        stream: str = "logminer:jobs",
        group: str = "logminer-workers",
        consumer: str = "worker-1",
        count: int = 1,
        block_ms: int = 5000,
    ) -> List[Dict[str, Any]]:
        """Lit des jobs via consumer group pour repartir le travail entre workers."""

        self.ensure_group(group, stream=stream, start_id="0")
        responses = self.client.xreadgroup(
            groupname=group,
            consumername=consumer,
            streams={stream: ">"},
            count=max(1, count),
            block=max(0, block_ms),
        )
        jobs: List[Dict[str, Any]] = []
        for stream_name, entries in responses:
            for message_id, fields in entries:
                payload_raw = fields.get("payload") or "{}"
                try:
                    payload = json.loads(payload_raw)
                except json.JSONDecodeError:
                    payload = {"raw": payload_raw}
                jobs.append(
                    {
                        "stream": stream_name,
                        "id": message_id,
                        "run_id": fields.get("run_id") or payload.get("run_id"),
                        "job_type": fields.get("job_type") or payload.get("job_type"),
                        "status": fields.get("status", "queued"),
                        "payload": payload,
                    }
                )
        return jobs

    def claim_stale_jobs(
        self,
        *,
        stream: str = "logminer:jobs",
        group: str = "logminer-workers",
        consumer: str = "worker-1",
        min_idle_ms: int = 300000,
        count: int = 1,
    ) -> List[Dict[str, Any]]:
        """Reclame des jobs pending restes trop longtemps sans ack."""

        self.ensure_group(group, stream=stream, start_id="0")
        try:
            response = self.client.xautoclaim(
                stream,
                group,
                consumer,
                min_idle_time=max(1, min_idle_ms),
                start_id="0-0",
                count=max(1, count),
            )
        except Exception:
            return []

        entries = response[1] if isinstance(response, (list, tuple)) and len(response) > 1 else []
        jobs: List[Dict[str, Any]] = []
        for message_id, fields in entries:
            payload_raw = fields.get("payload") or "{}"
            try:
                payload = json.loads(payload_raw)
            except json.JSONDecodeError:
                payload = {"raw": payload_raw}
            jobs.append(
                {
                    "stream": stream,
                    "id": message_id,
                    "run_id": fields.get("run_id") or payload.get("run_id"),
                    "job_type": fields.get("job_type") or payload.get("job_type"),
                    "status": fields.get("status", "queued"),
                    "payload": payload,
                    "claimed": True,
                }
            )
        return jobs

    def ack_job(self, message_id: str, *, stream: str = "logminer:jobs", group: str = "logminer-workers") -> int:
        """Accuse reception d'un job traite."""

        return int(self.client.xack(stream, group, message_id))

    def pending_jobs(self, *, stream: str = "logminer:jobs", group: str = "logminer-workers") -> Dict[str, Any]:
        """Expose un resume des jobs non acquittes."""

        self.ensure_group(group, stream=stream, start_id="0")
        try:
            summary = self.client.xpending(stream, group)
            return dict(summary)
        except Exception as exc:
            return {"error": str(exc)}


def filter_messages(messages: Iterable[AgentMessage], run_id: str | None = None) -> List[AgentMessage]:
    """Filtre les messages d'un run donne."""

    if run_id is None:
        return list(messages)
    return [message for message in messages if message.run_id == run_id]


class MqttMessageBus:
    """Bus MQTT leger pour collecteurs et traces temps reel non persistantes."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        topic_prefix: str = "logminer/events",
        run_id: str | None = None,
        client_id: str | None = None,
        keepalive: int = 30,
        qos: int = 1,
        username: str | None = None,
        password: str | None = None,
    ):
        if mqtt is None:
            raise RuntimeError("Le paquet Python 'paho-mqtt' n'est pas installe")

        self.host = host
        self.port = int(port)
        self.topic_prefix = topic_prefix.strip("/")
        self.run_id = run_id or uuid4().hex
        self.keepalive = int(keepalive)
        self.qos = max(0, min(int(qos), 2))
        self.client_id = client_id or f"logminer-{self.run_id}"
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=self.client_id)
        if username:
            self.client.username_pw_set(username, password=password)
        self.client.connect(self.host, self.port, keepalive=self.keepalive)
        self.client.loop_start()

    def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    def ping(self) -> bool:
        info = self.client.publish(
            f"{self.topic_prefix}/health",
            json.dumps({"run_id": self.run_id, "status": "ping"}, ensure_ascii=False),
            qos=self.qos,
        )
        info.wait_for_publish(timeout=5)
        return bool(info.is_published())

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
        topic = f"{self.topic_prefix}/{message.target}/{message.message_type}".replace(" ", "_")
        info = self.client.publish(topic, json.dumps(asdict(message), ensure_ascii=False), qos=self.qos)
        info.wait_for_publish(timeout=5)
        if not info.is_published():
            raise RuntimeError(f"Publication MQTT non confirmee sur {topic}")
        return message

    def read(self) -> List[AgentMessage]:
        """MQTT est pub/sub; l'historique n'est pas relu comme JSONL/Redis."""

        return []
