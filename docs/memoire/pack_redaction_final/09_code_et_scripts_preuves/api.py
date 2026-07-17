"""API FastAPI V2 pour piloter les agents Logminer.

La V2 expose la logique stable de la V1 CLI sans la remplacer. Les endpoints
acceptent des chemins locaux du projet, puis appellent les fonctions deja
utilisees par les commandes CLI: parsing, routage, detection et correlation.
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from datetime import datetime, timezone
import os
from time import perf_counter
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.model_router import MODEL_DEFAULTS, route_model, run_routed_detection
from agents.correlator import correlate_anomalies
from agents.bus import MqttMessageBus, RedisMessageBus
from agents.audit import read_audit, write_audit
from agents.collector_agent import DEFAULT_ROOTS, discover_logs
from agents.privilege_agent import request_windows_sensitive_collection
from agents.resource_monitor import snapshot as resource_snapshot
from agents.runtime_agent import ensure_runtime, runtime_status
from agents.supervisor_agent import run_supervisor_campaign, run_supervisor_cycle
from pipeline import run_pipeline


app = FastAPI(
    title="Ariel Logminer API",
    description="API V2 locale pour router, detecter et correler des journaux heterogenes.",
    version="0.1.0",
)


class RouteRequest(BaseModel):
    input_path: str = Field(..., description="Chemin local vers un CSV, Parquet ou log brut")
    sep: str = "auto"
    sample_rows: int = 1000


class ParseRequest(BaseModel):
    input_path: str
    out_dir: str = "data/processed"
    out_name: str = "api_parsed.csv"
    sep: str = ";"
    debug: bool = False


class DetectRequest(BaseModel):
    input_path: str
    sep: str = "auto"
    sample_rows: int = 1000
    output: str | None = None
    incidents_output: str | None = None
    window_minutes: int = 15
    run_id: str | None = None
    use_redis: bool = False


class CorrelateRequest(BaseModel):
    input_path: str = Field(..., description="CSV d'anomalies produit par la detection")
    output: str = "data/processed/api_incidents.csv"
    sep: str = "auto"
    window_minutes: int = 15
    run_id: str | None = None
    use_redis: bool = False


class RunRequest(BaseModel):
    input_path: str
    parse_if_needed: bool = True
    out_dir: str = "data/processed"
    sep: str = "auto"
    sample_rows: int = 1000
    window_minutes: int = 15
    run_id: str | None = None
    use_redis: bool = False


class DiscoverRequest(BaseModel):
    roots: list[str] = Field(default_factory=lambda: list(DEFAULT_ROOTS))
    max_files: int = 50
    max_mb: int = 100
    run_id: str | None = None
    use_redis: bool = False


class RunDiscoveredRequest(BaseModel):
    roots: list[str] = Field(default_factory=lambda: list(DEFAULT_ROOTS))
    out_dir: str = "data/processed"
    sep: str = "auto"
    sample_rows: int = 1000
    window_minutes: int = 15
    run_id: str | None = None
    use_redis: bool = True
    max_mb: int = 100


class QueueRunRequest(RunRequest):
    job_stream: str | None = None
    job_type: str = "workflow.run"


class SupervisorCycleRequest(BaseModel):
    roots: list[str] = Field(default_factory=lambda: list(DEFAULT_ROOTS))
    max_files: int = 20
    max_mb: int = 100
    out_dir: str = "data/processed"
    bus_path: str = "data/processed/supervisor_messages.jsonl"
    memory_path: str = "data/processed/supervisor_state.json"
    run_id: str | None = None


class SupervisorCampaignRequest(SupervisorCycleRequest):
    cycles: int = 3


class RuntimePrepareRequest(BaseModel):
    compose_file: str = "docker-compose.redis.yml"
    start_desktop: bool = True
    wait_seconds: int = 45
    run_id: str | None = None


class PrivilegedWindowsCollectRequest(BaseModel):
    days: int = 2
    copy_logs: list[str] = Field(default_factory=lambda: ["Application", "System", "Security"])
    raw_directory: str = "data\\raw\\windows_events_admin"
    output_directory: str = "data\\processed"
    run_id: str | None = None
    use_redis: bool = True


class EventsRequest(BaseModel):
    run_id: str | None = None
    count: int = 100


class MqttPublishRequest(BaseModel):
    source: str = "api"
    target: str = "mqtt"
    message_type: str = "mqtt.test"
    payload: dict[str, Any] = Field(default_factory=dict)
    status: str = "ok"
    run_id: str | None = None


class AlertDecisionRequest(BaseModel):
    alert_id: str = Field(..., description="Identifiant d'alerte, incident ou ligne analysee")
    decision: str = Field(..., description="accept, reject ou reclassify")
    analyst: str = "dashboard"
    severity: str | None = None
    category: str | None = None
    reason: str = ""
    run_id: str | None = None


def _path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _existing_path(value: str | Path) -> Path:
    path = _path(value)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Chemin introuvable: {path}")
    return path


def _infer_sep(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:8192]
    return max([";", ",", "\t"], key=sample.count)


def _count_rows(path: str | Path, sep: str = "auto") -> int | None:
    file_path = _path(path)
    try:
        if file_path.suffix.lower() == ".csv":
            return max(sum(1 for _ in file_path.open("r", encoding="utf-8-sig", errors="ignore")) - 1, 0)
        if file_path.suffix.lower() == ".parquet":
            return int(len(pd.read_parquet(file_path, columns=[])))
    except Exception:
        return None
    return None


def _model_summary(family: str, artifact: str) -> dict[str, Any]:
    path = _path(artifact)
    return {
        "family": family,
        "artifact": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def _model_paths() -> dict[str, Path]:
    return {family: _path(artifact) for family, artifact in MODEL_DEFAULTS.items()}


def _redis_settings() -> dict[str, Any]:
    return {
        "url": os.getenv("LOGMINER_REDIS_URL", "redis://localhost:6379/0"),
        "stream": os.getenv("LOGMINER_REDIS_STREAM", "logminer:events"),
        "job_stream": os.getenv("LOGMINER_REDIS_JOB_STREAM", "logminer:jobs"),
        "job_group": os.getenv("LOGMINER_REDIS_JOB_GROUP", "logminer-workers"),
    }


def _mqtt_settings() -> dict[str, Any]:
    return {
        "host": os.getenv("LOGMINER_MQTT_HOST", "localhost"),
        "port": int(os.getenv("LOGMINER_MQTT_PORT", "1883")),
        "topic_prefix": os.getenv("LOGMINER_MQTT_TOPIC_PREFIX", "logminer/events"),
        "qos": int(os.getenv("LOGMINER_MQTT_QOS", "1")),
        "username": os.getenv("LOGMINER_MQTT_USERNAME") or None,
        "password": os.getenv("LOGMINER_MQTT_PASSWORD") or None,
    }


def _redis_bus(run_id: str | None = None) -> RedisMessageBus:
    settings = _redis_settings()
    try:
        bus = RedisMessageBus(url=settings["url"], stream=settings["stream"], run_id=run_id)
        bus.ping()
        return bus
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Redis indisponible: {exc}") from exc


def _mqtt_bus(run_id: str | None = None) -> MqttMessageBus:
    settings = _mqtt_settings()
    try:
        bus = MqttMessageBus(run_id=run_id, **settings)
        bus.ping()
        return bus
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"MQTT indisponible: {exc}") from exc


def _publish(
    bus: Any | None,
    source: str,
    target: str,
    message_type: str,
    payload: dict[str, Any] | None = None,
    status: str = "ok",
) -> None:
    if bus is not None:
        bus.publish(source=source, target=target, message_type=message_type, payload=payload, status=status)


def _audit(action: str, status: str = "ok", target: str = "", details: dict[str, Any] | None = None) -> None:
    try:
        write_audit(action=action, status=status, actor="api", target=target, details=details)
    except Exception:
        pass


def _run_workflow(request: RunRequest, input_path: Path, run_id: str, bus: RedisMessageBus | None) -> dict[str, Any]:
    workflow_started = perf_counter()
    timings: dict[str, float] = {}
    out_dir = _path(request.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    _publish(
        bus,
        source="api",
        target="orchestrator",
        message_type="workflow.started",
        payload={"input_path": str(input_path), "out_dir": str(out_dir), "parse_if_needed": request.parse_if_needed},
    )

    source_for_detection = input_path
    parsed_csv = ""
    if request.parse_if_needed and input_path.suffix.lower() not in {".csv", ".parquet"}:
        parse_started = perf_counter()
        parsed_name = f"api_{run_id}_parsed.csv"
        parse_sep = ";" if request.sep == "auto" else request.sep
        _publish(bus, "orchestrator", "parser", "parsing.started", {"input_path": str(input_path)})
        produced = run_pipeline(str(input_path), str(out_dir), parsed_name, sep=parse_sep)
        if not produced:
            _publish(bus, "parser", "orchestrator", "parsing.failed", {"reason": "no parsed csv produced"}, status="error")
            raise HTTPException(status_code=400, detail="Aucun CSV produit par le parsing")
        source_for_detection = _path(produced[0])
        parsed_csv = str(source_for_detection)
        timings["parse_sec"] = round(perf_counter() - parse_started, 4)
        _publish(bus, "parser", "orchestrator", "parsing.completed", {"parsed_csv": parsed_csv})

    anomalies_csv = out_dir / f"api_{run_id}_anomalies.csv"
    incidents_csv = out_dir / f"api_{run_id}_incidents.csv"
    _publish(bus, "orchestrator", "detector", "detection.started", {"input_path": str(source_for_detection)})
    try:
        detection_started = perf_counter()
        result = run_routed_detection(
            source_for_detection,
            sep=request.sep,
            sample_rows=request.sample_rows,
            output=anomalies_csv,
            incidents_output=incidents_csv,
            window_minutes=request.window_minutes,
            models=_model_paths(),
        )
        routed_timings = result.get("timings") if isinstance(result.get("timings"), dict) else {}
        timings.update({str(key): float(value) for key, value in routed_timings.items()})
        timings["detect_and_correlate_sec"] = round(perf_counter() - detection_started, 4)
    except Exception as exc:
        _publish(bus, "detector", "orchestrator", "workflow.failed", {"error": str(exc)}, status="error")
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    response = {
        "run_id": run_id,
        "input_path": str(input_path),
        "parsed_csv": parsed_csv,
        **result,
        "input_rows": _count_rows(source_for_detection, request.sep),
        "anomalies_rows": _count_rows(result["anomalies_csv"], _infer_sep(_path(result["anomalies_csv"]))),
        "incidents_rows": _count_rows(result["incidents_csv"], _infer_sep(_path(result["incidents_csv"]))),
        "timings": {**timings, "workflow_sec": round(perf_counter() - workflow_started, 4)},
    }
    _publish(bus, "orchestrator", "api", "workflow.completed", response)
    return response


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "v2-fastapi",
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/redis/health")
def redis_health() -> dict[str, Any]:
    settings = _redis_settings()
    bus = _redis_bus()
    return {
        "status": "ok",
        "url": settings["url"],
        "stream": settings["stream"],
        "job_stream": settings["job_stream"],
        "ping": bus.ping(),
        "events": bus.stream_info(settings["stream"]),
        "jobs": bus.stream_info(settings["job_stream"]),
    }


@app.get("/redis/pending")
def redis_pending() -> dict[str, Any]:
    settings = _redis_settings()
    bus = _redis_bus()
    return {
        "job_stream": settings["job_stream"],
        "job_group": settings["job_group"],
        "pending": bus.pending_jobs(stream=settings["job_stream"], group=settings["job_group"]),
    }


@app.get("/mqtt/health")
def mqtt_health() -> dict[str, Any]:
    settings = _mqtt_settings()
    bus = _mqtt_bus()
    try:
        ping = bus.ping()
    finally:
        bus.close()
    return {
        "status": "ok",
        "host": settings["host"],
        "port": settings["port"],
        "topic_prefix": settings["topic_prefix"],
        "qos": settings["qos"],
        "ping_publish": ping,
    }


@app.post("/mqtt/publish")
def mqtt_publish(request: MqttPublishRequest) -> dict[str, Any]:
    bus = _mqtt_bus(request.run_id)
    try:
        message = bus.publish(
            source=request.source,
            target=request.target,
            message_type=request.message_type,
            payload=request.payload,
            status=request.status,
        )
    finally:
        bus.close()
    return {"published": True, "message": asdict(message)}


@app.get("/events")
def events(run_id: str | None = None, count: int = 100) -> dict[str, Any]:
    bus = _redis_bus(run_id=run_id)
    messages = bus.read(run_id=run_id, count=max(1, min(count, 1000)))
    return {
        "stream": bus.stream,
        "run_id": run_id,
        "count": len(messages),
        "events": [asdict(message) for message in messages],
    }


@app.get("/models")
def models() -> dict[str, Any]:
    return {"models": [_model_summary(family, artifact) for family, artifact in MODEL_DEFAULTS.items()]}


@app.get("/audit")
def audit(limit: int = 100) -> dict[str, Any]:
    entries = read_audit(limit=max(1, min(limit, 1000)))
    return {"count": len(entries), "events": [asdict(entry) for entry in entries]}


@app.post("/alerts/decision")
def alert_decision(request: AlertDecisionRequest) -> dict[str, Any]:
    allowed = {"accept", "reject", "reclassify"}
    decision = request.decision.strip().lower()
    if decision not in allowed:
        raise HTTPException(status_code=400, detail=f"Decision invalide: {request.decision}")
    entry = write_audit(
        action=f"alert.{decision}",
        status="ok",
        actor=request.analyst or "dashboard",
        target=request.alert_id,
        details={
            "run_id": request.run_id,
            "severity": request.severity,
            "category": request.category,
            "reason": request.reason,
        },
    )
    return {"decision": decision, "audit": asdict(entry)}


@app.get("/resources")
def resources() -> dict[str, Any]:
    return resource_snapshot()


@app.get("/runtime/status")
def get_runtime_status() -> dict[str, Any]:
    return asdict(runtime_status())


@app.post("/runtime/prepare")
def prepare_runtime(request: RuntimePrepareRequest) -> dict[str, Any]:
    bus = None
    try:
        bus = _redis_bus(request.run_id)
    except HTTPException:
        bus = None

    _publish(
        bus,
        source="api",
        target="runtime",
        message_type="runtime.prepare.started",
        payload={"compose_file": request.compose_file, "start_desktop": request.start_desktop},
    )
    status = ensure_runtime(
        compose_file=request.compose_file,
        start_desktop=request.start_desktop,
        wait_seconds=request.wait_seconds,
    )
    _publish(
        bus,
        source="runtime",
        target="api",
        message_type="runtime.prepare.completed",
        payload=asdict(status),
        status="ok" if status.services_started or status.docker_engine else "warning",
    )
    _audit(
        "runtime.prepare",
        status="ok" if status.services_started or status.docker_engine else "warning",
        target="docker",
        details=asdict(status),
    )
    return asdict(status)


@app.post("/collect/discover")
def collect_discover(request: DiscoverRequest) -> dict[str, Any]:
    bus = _redis_bus(request.run_id) if request.use_redis else None
    _publish(
        bus,
        source="api",
        target="collector",
        message_type="collector.discovery.started",
        payload={"roots": request.roots, "max_mb": request.max_mb},
    )
    candidates = discover_logs(
        roots=request.roots,
        max_files=request.max_files,
        max_bytes=max(1, request.max_mb) * 1024 * 1024,
        bus=bus,
    )
    _audit(
        "collector.discover",
        status="ok" if candidates else "warning",
        target="local_logs",
        details={"count": len(candidates), "selected": candidates[0].path if candidates else "", "roots": request.roots},
    )
    return {
        "run_id": bus.run_id if bus is not None else request.run_id,
        "count": len(candidates),
        "selected": asdict(candidates[0]) if candidates else None,
        "candidates": [asdict(candidate) for candidate in candidates],
    }


@app.post("/collect/windows/privileged")
def collect_windows_privileged(request: PrivilegedWindowsCollectRequest) -> dict[str, Any]:
    bus = _redis_bus(request.run_id) if request.use_redis else None
    _publish(
        bus,
        source="api",
        target="privilege",
        message_type="privilege.request.started",
        payload={"days": request.days, "copy_logs": request.copy_logs},
    )
    result = request_windows_sensitive_collection(
        days=request.days,
        copy_logs=request.copy_logs,
        raw_directory=request.raw_directory,
        output_directory=request.output_directory,
    )
    _publish(
        bus,
        source="privilege",
        target="collector",
        message_type="privilege.request.completed",
        payload=asdict(result),
        status="ok" if result.launched else "warning",
    )
    _audit(
        "privilege.request",
        status="ok" if result.launched else "warning",
        target="windows_sensitive_logs",
        details=asdict(result),
    )
    return {"run_id": bus.run_id if bus is not None else request.run_id, **asdict(result)}


@app.post("/route")
def route(request: RouteRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    try:
        return route_model(input_path, sep=request.sep, sample_rows=request.sample_rows, models=_model_paths())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/parse")
def parse(request: ParseRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    try:
        produced = run_pipeline(
            input_path,
            request.out_dir,
            request.out_name,
            sep=request.sep,
            debug=request.debug,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"produced": produced, "count": len(produced)}


@app.post("/detect")
def detect(request: DetectRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    bus = _redis_bus(request.run_id) if request.use_redis else None
    _publish(
        bus,
        source="api",
        target="detector",
        message_type="detection.started",
        payload={"input_path": str(input_path), "sep": request.sep},
    )
    try:
        result = run_routed_detection(
            input_path,
            sep=request.sep,
            sample_rows=request.sample_rows,
            output=request.output,
            incidents_output=request.incidents_output,
            window_minutes=request.window_minutes,
            models=_model_paths(),
        )
    except Exception as exc:
        _publish(bus, "detector", "api", "detection.failed", {"error": str(exc)}, status="error")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    response = {
        **result,
        "run_id": bus.run_id if bus is not None else request.run_id,
        "input_rows": _count_rows(input_path, request.sep),
        "anomalies_rows": _count_rows(result["anomalies_csv"], _infer_sep(_path(result["anomalies_csv"]))),
        "incidents_rows": _count_rows(result["incidents_csv"], _infer_sep(_path(result["incidents_csv"]))),
    }
    _publish(bus, "detector", "api", "detection.completed", response)
    return response


@app.post("/correlate")
def correlate(request: CorrelateRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    output_path = _path(request.output)
    sep = _infer_sep(input_path) if request.sep == "auto" else request.sep
    bus = _redis_bus(request.run_id) if request.use_redis else None
    _publish(
        bus,
        source="api",
        target="correlator",
        message_type="correlation.started",
        payload={"input_path": str(input_path), "output": str(output_path)},
    )
    try:
        incidents_csv = correlate_anomalies(
            input_path,
            output_path,
            sep=sep,
            window_minutes=request.window_minutes,
        )
    except Exception as exc:
        _publish(bus, "correlator", "api", "correlation.failed", {"error": str(exc)}, status="error")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    response = {
        "run_id": bus.run_id if bus is not None else request.run_id,
        "input_path": str(input_path),
        "incidents_csv": incidents_csv,
        "incidents_rows": _count_rows(incidents_csv, sep),
    }
    _publish(bus, "correlator", "api", "correlation.completed", response)
    return response


@app.post("/run")
def run(request: RunRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    run_id = request.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bus = _redis_bus(run_id) if request.use_redis else None
    response = _run_workflow(request, input_path, run_id, bus)
    _audit("workflow.run", target=str(input_path), details=response)
    return response


@app.post("/run/queued")
def run_queued(request: QueueRunRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    settings = _redis_settings()
    run_id = request.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    bus = _redis_bus(run_id)
    job_stream = request.job_stream or settings["job_stream"]
    payload = {
        "input_path": str(input_path),
        "parse_if_needed": request.parse_if_needed,
        "out_dir": request.out_dir,
        "sep": request.sep,
        "sample_rows": request.sample_rows,
        "window_minutes": request.window_minutes,
        "run_id": run_id,
    }
    job_id = bus.enqueue_job(payload, stream=job_stream, job_type=request.job_type)
    _publish(
        bus,
        source="api",
        target="worker",
        message_type="workflow.queued",
        payload={"job_id": job_id, "job_stream": job_stream, **payload},
    )
    _audit("workflow.queued", target=str(input_path), details={"job_id": job_id, "job_stream": job_stream, **payload})
    return {
        "status": "queued",
        "run_id": run_id,
        "job_id": job_id,
        "job_stream": job_stream,
        "worker_command": "python scripts\\logminer_redis_worker.py --once",
    }


@app.post("/run/discovered")
def run_discovered(request: RunDiscoveredRequest) -> dict[str, Any]:
    run_id = request.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bus = _redis_bus(run_id) if request.use_redis else None
    _publish(
        bus,
        source="orchestrator",
        target="collector",
        message_type="collector.discovery.started",
        payload={"roots": request.roots, "max_mb": request.max_mb},
    )
    candidates = discover_logs(
        roots=request.roots,
        max_files=1,
        max_bytes=max(1, request.max_mb) * 1024 * 1024,
        bus=bus,
    )
    if not candidates:
        _publish(bus, "collector", "orchestrator", "workflow.failed", {"reason": "no log candidate found"}, status="error")
        raise HTTPException(status_code=404, detail="Aucun journal candidat trouve")

    selected = _existing_path(candidates[0].path)
    workflow = RunRequest(
        input_path=str(selected),
        parse_if_needed=selected.suffix.lower() not in {".csv", ".parquet"},
        out_dir=request.out_dir,
        sep=request.sep,
        sample_rows=request.sample_rows,
        window_minutes=request.window_minutes,
        run_id=run_id,
        use_redis=request.use_redis,
    )
    response = _run_workflow(workflow, selected, run_id, bus)
    full_response = {"selected": asdict(candidates[0]), **response}
    _audit("workflow.run_discovered", target=str(selected), details=full_response)
    return full_response


@app.post("/supervisor/cycle")
def supervisor_cycle(request: SupervisorCycleRequest) -> dict[str, Any]:
    """Execute un cycle autonome perception-etat-decision-action."""

    result = run_supervisor_cycle(
        roots=request.roots,
        max_files=request.max_files,
        max_mb=request.max_mb,
        out_dir=request.out_dir,
        bus_path=request.bus_path,
        memory_path=request.memory_path,
        run_id=request.run_id,
    )
    return asdict(result)


@app.post("/supervisor/campaign")
def supervisor_campaign(request: SupervisorCampaignRequest) -> dict[str, Any]:
    """Execute plusieurs cycles autonomes avec memoire persistante."""

    results = run_supervisor_campaign(
        cycles=max(1, request.cycles),
        roots=request.roots,
        max_files=request.max_files,
        max_mb=request.max_mb,
        out_dir=request.out_dir,
        bus_path=request.bus_path,
        memory_path=request.memory_path,
    )
    return {"cycles": len(results), "results": [asdict(result) for result in results]}
