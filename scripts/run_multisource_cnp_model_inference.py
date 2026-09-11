#!/usr/bin/env python3
"""Campagne CNP H/M avec appel réel des artefacts de modèles compatibles."""

from __future__ import annotations

import json
import sys
import warnings
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from time import perf_counter, process_time
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
for directory in (ROOT / "scripts", ROOT / "src", ROOT / "src/logminer/parsers"):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

from dataset_strengthening_common import metrics_from_prediction  # noqa: E402
from final_consolidation_common import (  # noqa: E402
    CONFIG_PATH, PHASE_ROOT, append_ledger, ensure_phase_dirs, relative,
    run_id, sha256_file, utc_now, write_csv, write_json,
)
from logminer.agents.bus import AgentMessage  # noqa: E402
from logminer.agents.contract_net import ContractNetCoordinator  # noqa: E402
from logminer.agents.correlator import correlate_anomalies  # noqa: E402
from logminer.agents.detector import align_features  # noqa: E402
from logminer.agents.intelligent_runtime import AgentCapability, AgentTask, MultiTaskIntelligentAgent  # noqa: E402
from logminer.agents.model_router import (  # noqa: E402
    _linux_auth_features, _positive_class_probability, _supervised_features, route_dataframe,
)
from logminer.features.event_features import build_feature_frame  # noqa: E402
from prepare_wazuh_dataset import _normalise_chunk  # noqa: E402
from run_multisource_cnp_e2e_strengthening import candidate_rule, load_raw_units, normalize_unit  # noqa: E402
from train_linux_auth_model import prepare_linux_auth_frame  # noqa: E402

try:
    import psutil
except ImportError:  # pragma: no cover - explicitly reported at runtime
    psutil = None

EXPERIMENT_ID = "final_p3_multisource_cnp_model_inference"
SOURCE_CONFIG = ROOT / "experiments/phase_dataset_strengthening/configs/multiformat_balanced_protocol.json"
REGISTRY_PATH = PHASE_ROOT / "configs/multisource_model_compatibility_registry.json"
TARGET = 200
RUNTIME_REGISTRY: dict[str, dict[str, Any]] = {}
MODEL_CACHE: dict[str, dict[str, Any]] = {}
MODEL_LOAD_AUDIT: dict[str, dict[str, Any]] = {}


def normalize_for_model(source_id: str, raw: Any, index: int, source_path: Path) -> dict[str, Any]:
    if source_id == "linux_auth":
        if not isinstance(raw, dict):
            raise TypeError("linux_auth_raw_unit_not_mapping")
        return prepare_linux_auth_frame(pd.DataFrame([raw])).iloc[0].to_dict()
    if source_id == "wazuh":
        if not isinstance(raw, dict):
            raise TypeError("wazuh_raw_unit_not_mapping")
        return _normalise_chunk(pd.DataFrame([raw]), source_path, index - 1).iloc[0].to_dict()
    if source_id == "network_tabular":
        if not isinstance(raw, dict):
            raise TypeError("network_raw_unit_not_mapping")
        return {str(key).strip().lstrip("\ufeff"): value for key, value in raw.items()}
    return normalize_unit(source_id, raw, index)


def validate_registry(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required = {
        "source_family", "recommended_model", "artifact_exists", "feature_schema",
        "expected_input", "output_type", "compatible", "reason_if_incompatible",
    }
    output: list[dict[str, Any]] = []
    for entry in entries:
        missing = required - set(entry)
        if missing:
            raise ValueError(f"Registre incomplet pour {entry.get('source_family')}: {sorted(missing)}")
        path = ROOT / str(entry["recommended_model"])
        observed_exists = path.exists() and path.stat().st_size > 0
        if bool(entry["artifact_exists"]) != observed_exists:
            raise AssertionError(f"artifact_exists incorrect pour {entry['source_family']}")
        row = dict(entry)
        row["observed_artifact_exists"] = observed_exists
        row["artifact_sha256"] = sha256_file(path) if observed_exists else ""
        output.append(row)
    return output


def load_artifact(entry: dict[str, Any]) -> tuple[dict[str, Any], float]:
    path_text = str(entry["recommended_model"])
    if path_text in MODEL_CACHE:
        return MODEL_CACHE[path_text], 0.0
    path = ROOT / path_text
    started = perf_counter()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        artifact = joblib.load(path)
    elapsed = perf_counter() - started
    if not isinstance(artifact, dict) or "model" not in artifact or "feature_columns" not in artifact:
        raise ValueError(f"Artefact incomplet: {path}")
    MODEL_CACHE[path_text] = artifact
    MODEL_LOAD_AUDIT[path_text] = {
        "artifact": path_text,
        "artifact_sha256": entry["artifact_sha256"],
        "model_type": artifact.get("model_type", type(artifact["model"]).__name__),
        "feature_count": len(artifact["feature_columns"]),
        "load_time_sec": elapsed,
        "warnings": [str(item.message) for item in captured],
    }
    return artifact, elapsed


def infer_one(row: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    artifact, load_time = load_artifact(entry)
    model = artifact["model"]
    model_type = str(artifact.get("model_type", type(model).__name__))
    frame = pd.DataFrame([row])
    started = perf_counter()
    if model_type == "random_forest_linux_auth":
        features = _linux_auth_features(frame, list(artifact["feature_columns"]))
        labels = np.asarray(model.predict(features), dtype=int)
        scores = _positive_class_probability(model, features, labels)
        prediction_type = "binary_label_and_positive_class_probability"
        prediction = int(labels[0] == 1)
        score = float(scores[0])
    elif model_type.startswith("random_forest"):
        features = _supervised_features(frame, list(artifact["feature_columns"]))
        labels = np.asarray(model.predict(features), dtype=int)
        scores = _positive_class_probability(model, features, labels)
        prediction_type = "binary_label_and_positive_class_probability"
        prediction = int(labels[0] == 1)
        score = float(scores[0])
    elif model_type == "isolation_forest":
        max_unique = int(artifact.get("metadata", {}).get("max_categorical_unique", 100))
        features = align_features(build_feature_frame(frame, max_categorical_unique=max_unique), list(artifact["feature_columns"]))
        label = int(np.asarray(model.predict(features), dtype=int)[0])
        decision = float(np.asarray(model.decision_function(features), dtype=float)[0])
        prediction_type = "isolation_label_and_negative_decision_score"
        prediction = int(label == -1)
        score = -decision
    else:
        raise ValueError(f"Type de modèle non pris en charge: {model_type}")
    elapsed = perf_counter() - started
    return {
        "model_loaded": str(entry["recommended_model"]),
        "model_type": model_type,
        "artifact_sha256": entry["artifact_sha256"],
        "model_load_time_sec": load_time,
        "inference_time_sec": elapsed,
        "inference_executed": True,
        "prediction_type": prediction_type,
        "is_anomaly": prediction,
        "score": score,
        "fallback_used": False,
        "support_status": "SUPPORTED_MODEL_INFERENCE",
    }


def compatible_truth(source_id: str, row: dict[str, Any]) -> int | None:
    lower = {str(key).lower(): str(value).strip() for key, value in row.items()}
    if source_id == "linux_auth" and "anomaly_label" in lower:
        return int(lower["anomaly_label"].lower() not in {"normal", "0", "false", "benign", "-", ""})
    if source_id == "network_tabular" and "label" in lower:
        return int(lower["label"].upper() != "BENIGN")
    if source_id == "bgl" and "event" in lower:
        return int(lower["event"] not in {"", "-"})
    return None


def common_candidate_fields(row: dict[str, Any]) -> dict[str, Any]:
    lower = {str(key).lower(): value for key, value in row.items()}
    return {
        "timestamp_iso": lower.get("timestamp_iso", lower.get("timestamp", "")),
        "host": lower.get("host", lower.get("server", "")),
        "user": lower.get("user", lower.get("username", "")),
        "source": lower.get("source", lower.get("service", "")),
        "category": lower.get("category", ""),
        "subcategory": lower.get("subcategory", ""),
        "proto": lower.get("proto", lower.get("protocol", "")),
        "dst_port": lower.get("dst_port", lower.get("destination port", lower.get("port", ""))),
        "severity": lower.get("severity", ""),
        "event": lower.get("event", ""),
        "message": lower.get("message", lower.get("comment", "")),
    }


def handler(task: AgentTask, context: Any) -> dict[str, Any]:
    source_id = str(task.payload["source_id"])
    condition = str(task.payload["condition"])
    source_path = ROOT / str(task.payload["source_path"])
    normalized = normalize_for_model(source_id, task.payload["raw_unit"], int(task.payload["unit_index"]), source_path)
    route_frame = pd.DataFrame([normalized]).drop(columns=["filepath"], errors="ignore")
    route = route_dataframe(route_frame)
    entry = RUNTIME_REGISTRY[source_id]
    operation_started = perf_counter()
    if condition == "H":
        is_anomaly, score, rule = candidate_rule(normalized)
        inference = {
            "model_loaded": "",
            "model_type": "e2e_lightweight_candidate_rule_v1",
            "artifact_sha256": "",
            "model_load_time_sec": 0.0,
            "inference_time_sec": perf_counter() - operation_started,
            "inference_executed": False,
            "prediction_type": "heuristic_candidate",
            "is_anomaly": int(is_anomaly),
            "score": float(score),
            "fallback_used": True,
            "support_status": "LIGHTWEIGHT_HEURISTIC_FALLBACK",
            "heuristic_rule": rule,
        }
    elif bool(entry["compatible"]):
        if Path(str(route["model"])).as_posix().lower() != Path(str(entry["recommended_model"])).as_posix().lower():
            raise ValueError(f"Route incompatible avec le registre pour {source_id}: {route['model']}")
        inference = infer_one(normalized, entry)
        inference["heuristic_rule"] = ""
    else:
        is_anomaly, score, rule = candidate_rule(normalized)
        inference = {
            "model_loaded": "", "model_type": "e2e_lightweight_candidate_rule_v1",
            "artifact_sha256": "", "model_load_time_sec": 0.0,
            "inference_time_sec": perf_counter() - operation_started,
            "inference_executed": False, "prediction_type": "heuristic_candidate",
            "is_anomaly": int(is_anomaly), "score": float(score), "fallback_used": True,
            "support_status": "LIGHTWEIGHT_HEURISTIC_FALLBACK", "heuristic_rule": rule,
        }
    return {
        "end_to_end_run_id": task.payload["end_to_end_run_id"],
        "source_id": source_id, "condition": condition, "unit_index": task.payload["unit_index"],
        "agent_id": context.agent_id, "parsed": True, "normalized": True, "routed": True,
        "route_family": route["family"], "model_recommended": route["model"],
        "ground_truth": compatible_truth(source_id, normalized),
        "normalized_fields": common_candidate_fields(normalized),
        **inference,
    }


def build_agents(current_run: str, condition: str) -> list[MultiTaskIntelligentAgent]:
    profiles = {
        "agent-system": {"windows_event": 0.94, "syslog": 0.91, "hdfs": 0.98, "bgl": 0.97},
        "agent-security": {"windows_event": 0.89, "linux_auth": 0.98, "wazuh": 0.99},
        "agent-network": {"apache": 0.90, "network_tabular": 0.99},
    }
    agents: list[MultiTaskIntelligentAgent] = []
    for agent_id, sources in profiles.items():
        supported = {f"pipeline.{source_id}.{condition}": confidence for source_id, confidence in sources.items()}
        capabilities = [
            AgentCapability(name=f"{agent_id}:{task_type}", task_types=(task_type,), max_parallel=4, confidence=confidence, cost=0.2)
            for task_type, confidence in supported.items()
        ]
        agent = MultiTaskIntelligentAgent(
            agent_id=agent_id, capabilities=capabilities,
            handlers={task_type: handler for task_type in supported},
            max_parallel_tasks=4, memory_enabled=True,
        )
        agent.run_id = current_run
        agents.append(agent)
    return agents


def condition_resource_snapshot() -> dict[str, float | str]:
    if psutil is None:
        return {"rss_bytes": "INFORMATION À VÉRIFIER", "cpu_user_sec": "INFORMATION À VÉRIFIER", "cpu_system_sec": "INFORMATION À VÉRIFIER"}
    process = psutil.Process()
    cpu = process.cpu_times()
    return {"rss_bytes": float(process.memory_info().rss), "cpu_user_sec": float(cpu.user), "cpu_system_sec": float(cpu.system)}


def make_tasks(current_run: str, condition: str, units: dict[str, list[Any]], source_paths: dict[str, str]) -> list[AgentTask]:
    tasks: list[AgentTask] = []
    for source_id, rows in units.items():
        for index, raw in enumerate(rows, start=1):
            tasks.append(AgentTask.create(
                f"pipeline.{source_id}.{condition}",
                {
                    "end_to_end_run_id": current_run, "condition": condition,
                    "source_id": source_id, "source_path": source_paths[source_id],
                    "unit_index": index, "raw_unit": raw,
                    "idempotency_key": f"{current_run}:{condition}:{source_id}:{index}",
                }, priority=50,
            ))
    return tasks


def trace_outcomes(current_run: str, condition: str, outcomes: list[Any]) -> list[dict[str, Any]]:
    traces: list[dict[str, Any]] = []
    for outcome in outcomes:
        result = outcome.result
        output = result.output if result is not None else {}
        traces.append({
            "end_to_end_run_id": current_run, "condition": condition,
            "source_id": output.get("source_id", ""), "unit_index": output.get("unit_index", ""),
            "task_id": outcome.task_id, "contract_id": outcome.contract_id, "agent_id": outcome.winner or "",
            "status": result.status if result is not None else "error",
            "latency_sec": outcome.elapsed_sec, "parsed": bool(output.get("parsed", False)),
            "normalized": bool(output.get("normalized", False)), "routed": bool(output.get("routed", False)),
            "route_family": output.get("route_family", ""),
            "model_recommended": output.get("model_recommended", ""), "model_loaded": output.get("model_loaded", ""),
            "model_type": output.get("model_type", ""), "inference_executed": bool(output.get("inference_executed", False)),
            "artifact_sha256": output.get("artifact_sha256", ""), "prediction_type": output.get("prediction_type", ""),
            "is_anomaly": int(output.get("is_anomaly", 0)), "score": output.get("score", ""),
            "ground_truth": output.get("ground_truth", ""), "fallback_used": bool(output.get("fallback_used", False)),
            "support_status": output.get("support_status", "UNSUPPORTED"),
            "model_load_time_sec": float(output.get("model_load_time_sec", 0.0)),
            "inference_time_sec": float(output.get("inference_time_sec", 0.0)),
            "heuristic_rule": output.get("heuristic_rule", ""),
            "proposals": len(outcome.proposals), "refusals": len(outcome.refusals),
            "reassignments": outcome.reassignments, "error": result.error if result is not None else "no_result",
            "normalized_fields_json": json.dumps(output.get("normalized_fields", {}), ensure_ascii=False, sort_keys=True),
        })
    return traces


def condition_summary(condition: str, traces: list[dict[str, Any]], incidents: int, resources: dict[str, Any]) -> dict[str, Any]:
    frame = pd.DataFrame(traces)
    latencies = frame["latency_sec"].astype(float).to_numpy()
    return {
        "condition": condition, "input_count": len(traces),
        "model_inference_count": int(frame["inference_executed"].sum()),
        "heuristic_fallback_count": int(frame["fallback_used"].sum()),
        "unsupported_count": int((frame["support_status"] == "UNSUPPORTED").sum()),
        "errors": int((frame["status"] != "ok").sum()),
        "refusals": int(frame["refusals"].sum()), "reassignments": int(frame["reassignments"].sum()),
        "candidate_anomalies": int(frame["is_anomaly"].sum()), "candidate_incidents": int(incidents),
        "latency_mean": float(latencies.mean()), "latency_p95": float(np.percentile(latencies, 95)),
        "model_load_time": float(frame["model_load_time_sec"].sum()),
        "inference_time": float(frame["inference_time_sec"].sum()),
        "coverage": float((frame["support_status"] != "UNSUPPORTED").mean()),
        "model_inference_coverage": float(frame["inference_executed"].mean()),
        **resources,
    }


def per_source_summary(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(traces)
    rows: list[dict[str, Any]] = []
    for (condition, source), group in frame.groupby(["condition", "source_id"], sort=True):
        rows.append({
            "condition": condition, "source": source,
            "recommended_model": " | ".join(sorted(set(group["model_recommended"].astype(str)))),
            "model_actually_executed": " | ".join(sorted(value for value in set(group["model_loaded"].astype(str)) if value)) or "NONE",
            "n": len(group), "fallback": int(group["fallback_used"].sum()),
            "error": int((group["status"] != "ok").sum()),
            "model_inference_count": int(group["inference_executed"].sum()),
            "latency_mean": float(group["latency_sec"].astype(float).mean()),
            "latency_p95": float(np.percentile(group["latency_sec"].astype(float), 95)),
        })
    return rows


def predictive_metrics(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(traces)
    usable = frame.loc[(frame["condition"] == "M") & frame["inference_executed"] & frame["ground_truth"].isin([0, 1])]
    rows: list[dict[str, Any]] = []
    for source, group in usable.groupby("source_id", sort=True):
        truth = group["ground_truth"].astype(int).to_numpy()
        prediction = group["is_anomaly"].astype(int).to_numpy()
        scores = group["score"].astype(float).to_numpy()
        if len(np.unique(truth)) < 2:
            rows.append({
                "condition": "M", "source": source, "n": len(group),
                "status": "NON ÉVALUÉ", "reason": "one ground-truth class in selected units",
            })
            continue
        rows.append({
            "condition": "M", "source": source, "n": len(group), "status": "DESCRIPTIVE_ONLY",
            "reason": "prediction unit and label compatible; source may overlap historical model training data",
            **metrics_from_prediction(truth, prediction, scores),
        })
    return rows


def make_figures(source_rows: list[dict[str, Any]], figure_coverage: Path, figure_latency: Path) -> None:
    frame = pd.DataFrame(source_rows)
    model = frame.loc[frame["condition"] == "M"].copy()
    model["real_model"] = model["model_inference_count"]
    model["heuristic"] = model["fallback"]
    model["unsupported"] = model["n"] - model["real_model"] - model["heuristic"]
    ax = model.set_index("source")[["real_model", "heuristic", "unsupported"]].plot(
        kind="bar", stacked=True, figsize=(10.5, 5.8), color=["#2a7185", "#e2a03f", "#b04a5a"],
    )
    ax.set_ylabel("Unités")
    ax.set_title("CNP condition M — couverture d’inférence réelle")
    ax.tick_params(axis="x", rotation=25)
    ax.figure.tight_layout()
    ax.figure.savefig(figure_coverage, dpi=180)
    plt.close(ax.figure)

    pivot_mean = frame.pivot(index="source", columns="condition", values="latency_mean")
    ax = pivot_mean.plot(kind="bar", figsize=(10.5, 5.8), color=["#888888", "#2a7185"])
    ax.set_ylabel("Latence moyenne CNP par tâche (s)")
    ax.set_title("CNP — latence condition H contre condition M")
    ax.tick_params(axis="x", rotation=25)
    ax.figure.tight_layout()
    ax.figure.savefig(figure_latency, dpi=180)
    plt.close(ax.figure)


def main() -> int:
    global RUNTIME_REGISTRY
    ensure_phase_dirs()
    if len(AgentMessage.__dataclass_fields__) != 7:
        raise AssertionError("AgentMessage ne contient plus exactement sept champs.")
    source_config = json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))
    registry_config = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    registry_rows = validate_registry(registry_config["entries"])
    RUNTIME_REGISTRY = {row["source_family"]: row for row in registry_rows}
    if set(RUNTIME_REGISTRY) != {item["id"] for item in source_config["formats"]}:
        raise AssertionError("Le registre de compatibilité ne couvre pas exactement les huit sources.")

    current_run = run_id("multisource_cnp_model_inference")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID, phase="P3", run_id=current_run, dataset="8 real local sources",
        protocol="CNP_condition_H_vs_M_real_artifact_inference", status="RUNNING", started_at=started_at,
        command="python scripts/run_multisource_cnp_model_inference.py", error_path=relative(error_path),
    )
    try:
        units: dict[str, list[Any]] = {}
        source_paths: dict[str, str] = {}
        source_hashes: list[dict[str, Any]] = []
        for item in source_config["formats"]:
            selected = load_raw_units(item, TARGET)
            units[item["id"]] = selected
            source_paths[item["id"]] = item["source"]
            source_hashes.append({
                "source_id": item["id"], "path": item["source"],
                "sha256": sha256_file(ROOT / item["source"]), "selected_units": len(selected),
            })

        all_traces: list[dict[str, Any]] = []
        transcripts: list[dict[str, Any]] = []
        condition_resources: dict[str, dict[str, Any]] = {}
        for condition in ("H", "M"):
            tasks = make_tasks(current_run, condition, units, source_paths)
            coordinator = ContractNetCoordinator(build_agents(current_run, condition), run_id=current_run)
            before = condition_resource_snapshot()
            cpu_before = process_time()
            wall_started = perf_counter()
            outcomes = coordinator.run_tasks(tasks, max_workers=1)
            wall_elapsed = perf_counter() - wall_started
            cpu_elapsed = process_time() - cpu_before
            after = condition_resource_snapshot()
            condition_resources[condition] = {
                "condition_wall_time_sec": wall_elapsed,
                "condition_process_time_sec": cpu_elapsed,
                "rss_before_bytes": before["rss_bytes"], "rss_after_bytes": after["rss_bytes"],
                "cpu_user_before_sec": before["cpu_user_sec"], "cpu_user_after_sec": after["cpu_user_sec"],
                "cpu_system_before_sec": before["cpu_system_sec"], "cpu_system_after_sec": after["cpu_system_sec"],
            }
            all_traces.extend(trace_outcomes(current_run, condition, outcomes))
            transcripts.extend(asdict(message) for message in coordinator.transcript)

        trace_path = PHASE_ROOT / "raw" / f"{current_run}_unit_trace.csv"
        messages_path = PHASE_ROOT / "raw" / f"{current_run}_cnp_messages.jsonl"
        registry_output = PHASE_ROOT / "processed" / "multisource_model_compatibility_registry_observed.csv"
        model_load_path = PHASE_ROOT / "raw" / f"{current_run}_model_load_audit.json"
        write_csv(trace_path, all_traces)
        write_csv(registry_output, registry_rows)
        write_json(model_load_path, list(MODEL_LOAD_AUDIT.values()))
        with messages_path.open("w", encoding="utf-8") as handle:
            for message in transcripts:
                handle.write(json.dumps(message, ensure_ascii=False) + "\n")

        candidate_rows: list[dict[str, Any]] = []
        for row in all_traces:
            if row["condition"] != "M" or not row["is_anomaly"]:
                continue
            fields = json.loads(row["normalized_fields_json"])
            fields.update({
                "end_to_end_run_id": current_run, "source_id": row["source_id"],
                "task_id": row["task_id"], "contract_id": row["contract_id"],
                "agent_id": row["agent_id"], "model": row["model_loaded"] or row["model_type"],
                "is_anomaly": 1, "anomaly_score": row["score"], "anomaly_rank": len(candidate_rows) + 1,
            })
            candidate_rows.append(fields)
        candidate_path = PHASE_ROOT / "processed" / f"{current_run}_candidate_anomalies.csv"
        incident_path = PHASE_ROOT / "processed" / f"{current_run}_candidate_incidents.csv"
        write_csv(candidate_path, candidate_rows, fieldnames=list(candidate_rows[0]) if candidate_rows else ["end_to_end_run_id", "source_id", "is_anomaly"])
        if candidate_rows:
            correlate_anomalies(candidate_path, incident_path, sep=",", window_minutes=15)
            incident_count = len(pd.read_csv(incident_path))
        else:
            write_csv(incident_path, [], fieldnames=["incident_id", "event_count"])
            incident_count = 0

        summaries = [
            condition_summary(condition, [row for row in all_traces if row["condition"] == condition], incident_count if condition == "M" else 0, condition_resources[condition])
            for condition in ("H", "M")
        ]
        source_rows = per_source_summary(all_traces)
        predictive_rows = predictive_metrics(all_traces)
        source_path = PHASE_ROOT / "aggregated" / "multisource_cnp_model_inference_by_source.csv"
        predictive_path = PHASE_ROOT / "aggregated" / "multisource_cnp_model_predictive_metrics.csv"
        summary_path = PHASE_ROOT / "aggregated" / "multisource_cnp_model_inference_summary.json"
        snapshot_path = PHASE_ROOT / "aggregated" / "multisource_cnp_model_api_dashboard_snapshot.json"
        report_path = PHASE_ROOT / "reports" / "MULTISOURCE_CNP_REAL_MODEL_INFERENCE.md"
        figure_coverage = PHASE_ROOT / "figures" / "dataset_17_e2e_real_model_coverage.png"
        figure_latency = PHASE_ROOT / "figures" / "dataset_18_e2e_real_model_latency.png"
        write_csv(source_path, source_rows)
        write_csv(predictive_path, predictive_rows)
        make_figures(source_rows, figure_coverage, figure_latency)
        summary = {
            "run_id": current_run, "conditions": summaries, "per_source": source_rows,
            "predictive_metrics": predictive_rows,
            "condition_H_predictive_metrics": "NON ÉVALUÉ",
            "condition_H_predictive_reason": "the historical heuristic directly uses available source labels for labeled inputs",
            "ground_truth_policy": "per-source only when prediction unit and label are compatible; no global predictive metric",
            "agent_message_fields": list(AgentMessage.__dataclass_fields__),
            "model_load_audit": list(MODEL_LOAD_AUDIT.values()),
        }
        write_json(summary_path, summary)
        write_json(snapshot_path, {
            "generated_at": utc_now(), "endpoint_semantics": "offline API/dashboard evidence snapshot",
            "summary": summaries, "sources": source_rows,
        })

        m = next(row for row in summaries if row["condition"] == "M")
        h = next(row for row in summaries if row["condition"] == "H")
        report_lines = [
            "# CNP multi-source avec inférence réelle des modèles routés", "",
            f"Run : `{current_run}`. Les conditions H et M traitent chacune `{h['input_count']}` unités via de vrais agents et le protocole Contract Net.", "",
            "## Registre de compatibilité", "",
            "Le registre a été figé avant l’exécution. Un artefact n’est appelé que lorsque son schéma et l’unité d’entrée sont compatibles. Apache reste un fallback heuristique explicite, car la fixture d’une ligne n’expose pas les champs HTTP structurés nécessaires.", "",
            "## Résultats", "",
            "| Condition | Inférences modèle | Fallbacks heuristiques | Unsupported | Erreurs | Refus | Réattributions | Anomalies candidates | Incidents candidats | Latence moyenne (s) | P95 (s) |", "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            f"| H | {h['model_inference_count']} | {h['heuristic_fallback_count']} | {h['unsupported_count']} | {h['errors']} | {h['refusals']} | {h['reassignments']} | {h['candidate_anomalies']} | {h['candidate_incidents']} | {h['latency_mean']:.6f} | {h['latency_p95']:.6f} |",
            f"| M | {m['model_inference_count']} | {m['heuristic_fallback_count']} | {m['unsupported_count']} | {m['errors']} | {m['refusals']} | {m['reassignments']} | {m['candidate_anomalies']} | {m['candidate_incidents']} | {m['latency_mean']:.6f} | {m['latency_p95']:.6f} |", "",
            "## Vérité terrain", "",
            "Aucune accuracy globale n’est calculée. Les métriques prédictives de M sont séparées par source lorsque l’unité et le label sont compatibles. Pour H, elles sont `NON ÉVALUÉ` car la règle historique utilise directement les labels disponibles sur les entrées labellisées ; les présenter comme prédictions serait circulaire.", "",
            "Les sorties sans vérité terrain restent des anomalies et incidents candidats. Elles ne constituent pas une accuracy.", "",
            "## Limites", "",
            "Cette campagne démontre le chargement et l’appel des artefacts compatibles dans une chaîne CNP locale. Elle ne démontre ni un gain prédictif global du routage, ni une validité industrielle, ni l’indépendance des sources par rapport aux données historiques d’apprentissage des artefacts.",
        ]
        report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        artifacts = [trace_path, messages_path, registry_output, model_load_path, candidate_path, incident_path, source_path, predictive_path, summary_path, snapshot_path, report_path, figure_coverage, figure_latency]
        manifest_path = PHASE_ROOT / "manifests" / f"{current_run}_manifest.json"
        write_json(manifest_path, {
            "run_id": current_run, "status": "COMPLETED",
            "config": {"path": relative(CONFIG_PATH), "sha256": sha256_file(CONFIG_PATH)},
            "registry": {"path": relative(REGISTRY_PATH), "sha256": sha256_file(REGISTRY_PATH)},
            "sources": source_hashes,
            "models": [{"path": row["recommended_model"], "sha256": row["artifact_sha256"], "compatible": row["compatible"]} for row in registry_rows],
            "artifacts": [{"path": relative(path), "sha256": sha256_file(path)} for path in artifacts],
        })
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P3", run_id=current_run, dataset="8 real local sources",
            protocol="CNP_condition_H_vs_M_real_artifact_inference", status="COMPLETED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/run_multisource_cnp_model_inference.py",
            raw_result_path=relative(trace_path), summary_path=relative(summary_path),
            figure_path=f"{relative(figure_coverage)} | {relative(figure_latency)}", error_path=relative(error_path),
            notes=f"M real inference={m['model_inference_count']}; fallback={m['heuristic_fallback_count']}; errors={m['errors']}.",
        )
        print(json.dumps({"status": "COMPLETED", "run_id": current_run, "H": h, "M": m}, ensure_ascii=False))
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P3", run_id=current_run, dataset="8 real local sources",
            protocol="CNP_condition_H_vs_M_real_artifact_inference", status="FAILED",
            started_at=started_at, completed_at=utc_now(), command="python scripts/run_multisource_cnp_model_inference.py",
            error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
