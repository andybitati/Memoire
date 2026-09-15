#!/usr/bin/env python3
"""Replay multi-source réel au travers des agents légers et du protocole CNP."""

from __future__ import annotations

import argparse
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Evtx.Evtx import Evtx
from Evtx.Views import evtx_record_xml_view

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PARSERS = SRC / "logminer" / "parsers"
SCRIPTS = ROOT / "scripts"
for directory in (SRC, PARSERS, SCRIPTS):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from dataset_strengthening_common import (  # noqa: E402
    PHASE_ROOT,
    append_ledger,
    ensure_phase_dirs,
    relative,
    run_id,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)
from logminer.agents.bus import AgentMessage  # noqa: E402
from logminer.agents.contract_net import ContractNetCoordinator  # noqa: E402
from logminer.agents.correlator import correlate_anomalies  # noqa: E402
from logminer.agents.intelligent_runtime import AgentCapability, AgentTask, MultiTaskIntelligentAgent  # noqa: E402
from logminer.agents.model_router import route_dataframe  # noqa: E402
from logminer.parsers import bgl as bgl_parser  # noqa: E402
from logminer.parsers import hdfs as hdfs_parser  # noqa: E402
from logminer.parsers.windows_event import _parse_event_elem  # noqa: E402

CONFIG = PHASE_ROOT / "configs" / "multiformat_balanced_protocol.json"
EXPERIMENT_ID = "dataset_06_multisource_cnp_e2e"
TARGET = 200


def load_raw_units(item: dict[str, Any], limit: int) -> list[Any]:
    path = ROOT / item["source"]
    adapter = item["adapter"]
    if adapter == "pipeline_evtx_sample":
        values = []
        with Evtx(str(path)) as log:
            for record in log.records():
                values.append(evtx_record_xml_view(record))
                if len(values) >= limit:
                    break
        return values
    if adapter in {"pipeline_text_sample"}:
        values = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                if line.strip():
                    values.append(line.rstrip("\r\n"))
                if len(values) >= limit:
                    break
        return values
    header = path.open("r", encoding="utf-8-sig", errors="ignore").readline()
    separator = max((",", ";", "\t"), key=header.count)
    return pd.read_csv(path, sep=separator, dtype=str, keep_default_na=False, nrows=limit, encoding_errors="ignore").to_dict(orient="records")


def normalize_unit(source_id: str, raw: Any, unit_index: int) -> dict[str, Any]:
    if source_id == "windows_event":
        return _parse_event_elem(ET.fromstring(str(raw)), "neutral.evtx", unit_index)
    if source_id == "hdfs":
        match = hdfs_parser.HDFS_SHORT_RE.match(str(raw))
        if not match:
            raise ValueError("hdfs_unparsed")
        values = match.groupdict()
        block = hdfs_parser.BLOCK_RE.search(values["message"])
        return {"dataset": "hdfs", "subtype": "hdfs", "timestamp_iso": hdfs_parser._timestamp(values["date"], values["time"]), "severity": hdfs_parser._severity(values["severity"]), "event": block.group(0) if block else "", "source": values["source"], "component": values["source"], "category": "system", "subcategory": "hdfs", "message": values["message"]}
    if source_id == "bgl":
        match = bgl_parser.BGL_RE.match(str(raw))
        if not match:
            raise ValueError("bgl_unparsed")
        values = match.groupdict()
        return {"dataset": "bgl", "subtype": "bgl", "timestamp_iso": bgl_parser._timestamp(values["timestamp"]), "severity": bgl_parser._severity(values["severity"]), "event": values["label"], "source": values["component"], "component": values["component"], "host": values["node"], "category": "system", "subcategory": "bgl", "message": values["message"]}
    if source_id == "syslog":
        return {"dataset": "linux", "subtype": "syslog", "source": "syslog", "category": "system", "message": str(raw)}
    if source_id == "apache":
        return {"dataset": "unknown", "subtype": "apache", "source": "apache", "category": "network", "message": str(raw)}
    if not isinstance(raw, dict):
        raise TypeError("csv_unit_not_mapping")
    return {str(key).strip().lstrip("\ufeff"): value for key, value in raw.items()}


def candidate_rule(row: dict[str, Any]) -> tuple[int, float, str]:
    lower = {str(key).lower(): str(value) for key, value in row.items()}
    labels = " ".join(lower.get(key, "") for key in ("label", "anomaly_label", "class", "attack_cat")).strip().lower()
    severity = lower.get("severity", "").upper()
    if labels:
        anomaly = labels not in {"benign", "normal", "0", "false", "-"}
        return int(anomaly), 1.0 if anomaly else 0.0, "available_source_label_used_as_candidate_signal"
    if lower.get("dataset") == "bgl" and lower.get("event", "") not in {"", "-"}:
        return 1, 0.8, "bgl_non_dash_label_candidate"
    if severity in {"WARNING", "ERROR", "CRITICAL", "FATAL", "SEVERE"}:
        return 1, 0.65, "severity_candidate_rule"
    wazuh_level = lower.get("_source.rule.level", lower.get("wazuh_rule_level", ""))
    try:
        if float(wazuh_level) >= 7:
            return 1, min(1.0, float(wazuh_level) / 15.0), "wazuh_level_candidate_rule"
    except ValueError:
        pass
    return 0, 0.0, "no_candidate_signal"


def real_handler(task: AgentTask, context: Any) -> dict[str, Any]:
    source_id = str(task.payload["source_id"])
    normalized = normalize_unit(source_id, task.payload["raw_unit"], int(task.payload["unit_index"]))
    route_frame = pd.DataFrame([normalized]).drop(columns=["filepath"], errors="ignore")
    route = route_dataframe(route_frame)
    is_anomaly, score, rule = candidate_rule(normalized)
    standard = {key: normalized.get(key, "") for key in ("timestamp_iso", "host", "user", "source", "category", "subcategory", "proto", "dst_port", "severity", "event", "message")}
    return {
        "end_to_end_run_id": task.payload["end_to_end_run_id"],
        "source_id": source_id,
        "unit_index": task.payload["unit_index"],
        "agent_id": context.agent_id,
        "parsed": True,
        "normalized": True,
        "routed": True,
        "detected": True,
        "route_family": route["family"],
        "routed_model": route["model"],
        "model": "e2e_lightweight_candidate_rule_v1",
        "fallback": route["family"] == "fallback",
        "is_anomaly": is_anomaly,
        "anomaly_score": score,
        "candidate_rule": rule,
        "normalized_fields": standard,
    }


def build_agents(current_run: str) -> list[MultiTaskIntelligentAgent]:
    profiles = {
        "agent-system": {"pipeline.windows_event": 0.94, "pipeline.syslog": 0.91, "pipeline.hdfs": 0.98, "pipeline.bgl": 0.97},
        "agent-security": {"pipeline.windows_event": 0.89, "pipeline.linux_auth": 0.98, "pipeline.wazuh": 0.99},
        "agent-network": {"pipeline.apache": 0.90, "pipeline.network_tabular": 0.99},
    }
    agents = []
    for agent_id, supported in profiles.items():
        capabilities = [AgentCapability(name=f"{agent_id}:{task_type}", task_types=(task_type,), max_parallel=4, confidence=confidence, cost=0.2) for task_type, confidence in supported.items()]
        agent = MultiTaskIntelligentAgent(agent_id=agent_id, capabilities=capabilities, handlers={task_type: real_handler for task_type in supported}, max_parallel_tasks=4, memory_enabled=True)
        agent.run_id = current_run
        agents.append(agent)
    return agents


def make_agent_figure(rows: list[dict[str, Any]], output: Path) -> None:
    frame = pd.DataFrame(rows)
    table = pd.crosstab(frame["source_id"], frame["agent_id"])
    ax = table.plot(kind="bar", stacked=True, figsize=(11, 6), color=["#4C78A8", "#F58518", "#54A24B"])
    ax.set_ylabel("Tâches attribuées")
    ax.set_title("Distribution des décisions CNP par source et agent")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    ax.figure.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    ax.figure.savefig(output, dpi=180)
    plt.close(ax.figure)


def make_funnel_figure(summary: dict[str, Any], output: Path) -> None:
    keys = ("input_count", "parsed_count", "normalized_count", "routed_count", "detected_count", "candidate_anomalies", "candidate_incidents")
    values = [summary[key] for key in keys]
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    bars = ax.bar(range(len(keys)), values, color=["#4C78A8", "#5C8DC1", "#69A3D2", "#54A24B", "#72B56A", "#F58518", "#E45756"])
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value, str(value), ha="center", va="bottom")
    ax.set_xticks(range(len(keys)), [key.replace("_count", "").replace("_", "\n") for key in keys])
    ax.set_ylabel("Nombre d'unités")
    ax.set_title("Pipeline multi-source CNP — entonnoir observé")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    ensure_phase_dirs()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if len(AgentMessage.__dataclass_fields__) != 7:
        raise AssertionError("AgentMessage ne contient plus exactement sept champs.")
    plan = [{"source_id": item["id"], "path": item["source"], "units": min(TARGET, int(item["limit"]))} for item in config["formats"]]
    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", "sources": plan, "agent_message_fields": list(AgentMessage.__dataclass_fields__)}, ensure_ascii=False))
        return 0

    current_run = run_id("multisource_cnp")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(experiment_id=EXPERIMENT_ID, phase="6/7", run_id=current_run, dataset="8 real local sources", protocol="per_unit_local_CNP_real_agents", status="RUNNING", started_at=started_at, command="python scripts/run_multisource_cnp_e2e_strengthening.py", error_path=relative(error_path))
    try:
        tasks: list[AgentTask] = []
        source_hashes = []
        for item in config["formats"]:
            units = load_raw_units(item, TARGET)
            source_hashes.append({"source_id": item["id"], "path": item["source"], "sha256": sha256_file(ROOT / item["source"]), "selected_units": len(units)})
            for index, unit in enumerate(units, start=1):
                tasks.append(AgentTask.create(f"pipeline.{item['id']}", {"end_to_end_run_id": current_run, "source_id": item["id"], "unit_index": index, "raw_unit": unit, "idempotency_key": f"{current_run}:{item['id']}:{index}"}, priority=50))
        coordinator = ContractNetCoordinator(build_agents(current_run), run_id=current_run)
        outcomes = coordinator.run_tasks(tasks, max_workers=max(1, args.workers))
        traces: list[dict[str, Any]] = []
        candidate_rows: list[dict[str, Any]] = []
        for outcome in outcomes:
            result = outcome.result
            output = result.output if result is not None else {}
            trace = {
                "end_to_end_run_id": current_run,
                "source_id": output.get("source_id", ""),
                "unit_index": output.get("unit_index", ""),
                "task_id": outcome.task_id,
                "contract_id": outcome.contract_id,
                "agent_id": outcome.winner or "",
                "model": output.get("model", ""),
                "routed_model": output.get("routed_model", ""),
                "route_family": output.get("route_family", ""),
                "status": result.status if result is not None else "error",
                "latency_sec": outcome.elapsed_sec,
                "parsed": bool(output.get("parsed", False)),
                "normalized": bool(output.get("normalized", False)),
                "routed": bool(output.get("routed", False)),
                "detected": bool(output.get("detected", False)),
                "is_anomaly": int(output.get("is_anomaly", 0)),
                "fallback": bool(output.get("fallback", False)),
                "proposals": len(outcome.proposals),
                "proposal_utilities_json": json.dumps(outcome.proposals, sort_keys=True),
                "refusals": len(outcome.refusals),
                "refusal_reasons_json": json.dumps(outcome.refusals, sort_keys=True),
                "reassignments": outcome.reassignments,
                "error": result.error if result is not None else "no_result",
            }
            traces.append(trace)
            if output.get("is_anomaly"):
                fields = dict(output.get("normalized_fields", {}))
                fields.update({"end_to_end_run_id": current_run, "source_id": output.get("source_id", ""), "task_id": outcome.task_id, "contract_id": outcome.contract_id, "agent_id": outcome.winner, "model": output.get("model", ""), "is_anomaly": 1, "anomaly_score": output.get("anomaly_score", 0.0), "anomaly_rank": len(candidate_rows) + 1})
                candidate_rows.append(fields)
        trace_path = PHASE_ROOT / "raw" / f"{current_run}_unit_trace.csv"
        messages_path = PHASE_ROOT / "raw" / f"{current_run}_cnp_messages.jsonl"
        candidate_path = PHASE_ROOT / "processed" / f"{current_run}_candidate_anomalies.csv"
        incidents_path = PHASE_ROOT / "processed" / f"{current_run}_candidate_incidents.csv"
        write_csv(trace_path, traces)
        write_csv(candidate_path, candidate_rows, fieldnames=list(candidate_rows[0]) if candidate_rows else ["end_to_end_run_id", "source_id", "is_anomaly"])
        with messages_path.open("w", encoding="utf-8") as handle:
            for message in coordinator.transcript:
                handle.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
        if candidate_rows:
            correlate_anomalies(candidate_path, incidents_path, sep=",", window_minutes=15)
            incidents = pd.read_csv(incidents_path, dtype=str, keep_default_na=False)
            incident_count = len(incidents)
        else:
            write_csv(incidents_path, [], fieldnames=["incident_id", "event_count"])
            incident_count = 0
        latencies = np.asarray([float(row["latency_sec"]) for row in traces], dtype=float)
        summary = {
            "run_id": current_run,
            "input_count": len(tasks),
            "parsed_count": sum(int(row["parsed"]) for row in traces),
            "normalized_count": sum(int(row["normalized"]) for row in traces),
            "routed_count": sum(int(row["routed"]) for row in traces),
            "detected_count": sum(int(row["detected"]) for row in traces),
            "candidate_anomalies": len(candidate_rows),
            "candidate_incidents": incident_count,
            "fallback_count": sum(int(row["fallback"]) for row in traces),
            "error_count": sum(row["status"] != "ok" for row in traces),
            "reassignments": sum(int(row["reassignments"]) for row in traces),
            "mean_latency_sec": float(latencies.mean()) if len(latencies) else float("nan"),
            "p95_latency_sec": float(np.percentile(latencies, 95)) if len(latencies) else float("nan"),
            "message_counts": coordinator.message_counts(),
            "agent_message_fields": list(AgentMessage.__dataclass_fields__),
            "ground_truth": "not fabricated; anomaly outputs are candidates only",
        }
        per_source = []
        frame = pd.DataFrame(traces)
        for source_id, group in frame.groupby("source_id", sort=True):
            winners = Counter(group["agent_id"])
            per_source.append({"source_id": source_id, "selected_agent": winners.most_common(1)[0][0] if winners else "", "tasks": len(group), "proposals": int(group["proposals"].sum()), "refusals": int(group["refusals"].sum()), "routed_models": "|".join(sorted(set(group["routed_model"]))), "success": int((group["status"] == "ok").sum()), "fallback": int(group["fallback"].sum()), "errors": int((group["status"] != "ok").sum()), "mean_latency_sec": float(group["latency_sec"].astype(float).mean()), "p95_latency_sec": float(np.percentile(group["latency_sec"].astype(float), 95))})
        summary_path = PHASE_ROOT / "aggregated" / "multisource_cnp_e2e_summary.json"
        source_path = PHASE_ROOT / "aggregated" / "multisource_cnp_by_source.csv"
        figure_agents = PHASE_ROOT / "figures" / "dataset_08_multisource_agent_distribution.png"
        figure_funnel = PHASE_ROOT / "figures" / "dataset_09_multisource_pipeline_funnel.png"
        snapshot_path = PHASE_ROOT / "aggregated" / "multisource_api_dashboard_snapshot.json"
        write_json(summary_path, summary)
        write_csv(source_path, per_source)
        write_json(snapshot_path, {"generated_at": utc_now(), "endpoint_semantics": "offline API/dashboard evidence snapshot", "summary": summary, "sources": per_source})
        make_agent_figure(traces, figure_agents)
        make_funnel_figure(summary, figure_funnel)
        write_json(PHASE_ROOT / "manifests" / f"{current_run}_manifest.json", {"run_id": current_run, "config_sha256": sha256_file(CONFIG), "sources": source_hashes, "artifacts": [{"path": relative(path), "sha256": sha256_file(path)} for path in (trace_path, messages_path, candidate_path, incidents_path, summary_path, source_path, snapshot_path, figure_agents, figure_funnel)]})
        append_ledger(experiment_id=EXPERIMENT_ID, phase="6/7", run_id=current_run, dataset="8 real local sources", protocol="per_unit_local_CNP_real_agents", status="COMPLETED", started_at=started_at, completed_at=utc_now(), command="python scripts/run_multisource_cnp_e2e_strengthening.py", raw_result_path=relative(trace_path), summary_path=relative(summary_path), figure_path=f"{relative(figure_agents)}|{relative(figure_funnel)}", error_path=relative(error_path), notes=f"input={len(tasks)} success={len(tasks)-summary['error_count']} candidates only; no fabricated truth")
        print(f"COMPLETED {current_run} input={len(tasks)} errors={summary['error_count']}")
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(experiment_id=EXPERIMENT_ID, phase="6/7", run_id=current_run, dataset="8 real local sources", protocol="per_unit_local_CNP_real_agents", status="FAILED", started_at=started_at, completed_at=utc_now(), command="python scripts/run_multisource_cnp_e2e_strengthening.py", error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
