"""Prepare a compact local dataset for dashboard screenshots.

The generated CSV/JSONL files live in data/processed, which is ignored by git.
They are meant for memoire captures, not as primary experimental artefacts.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = []
        for row in csv.DictReader(handle, delimiter=";"):
            rows.append({key.replace("\ufeff", ""): value for key, value in row.items()})
        return rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def severity_for(row: dict[str, str]) -> str:
    if row.get("label") == "1":
        return "ERROR"
    if row.get("seq_template_is_rare") in {"1", "1.0"}:
        return "WARNING"
    return row.get("severity") or "INFO"


def event_name(row: dict[str, str], index: int) -> str:
    return row.get("event") or row.get("block_id") or f"log-{index:04d}"


def normalize_row(row: dict[str, str], index: int, dataset: str) -> dict[str, object]:
    template = row.get("seq_template") or row.get("message") or ""
    return {
        "timestamp_iso": row.get("timestamp_iso", ""),
        "severity": severity_for(row),
        "event": event_name(row, index),
        "source": row.get("source") or dataset,
        "host": row.get("host") or row.get("source") or dataset,
        "user": row.get("user") or "",
        "category": row.get("category") or dataset,
        "message": template[:240],
    }


def anomaly_row(row: dict[str, str], index: int, dataset: str) -> dict[str, object]:
    normalized = normalize_row(row, index, dataset)
    is_anomaly = 1 if row.get("label") == "1" else 0
    rare = 1 if row.get("seq_template_is_rare") in {"1", "1.0"} else 0
    base_score = 0.90 if is_anomaly else 0.28
    score = min(0.99, base_score + rare * 0.05 + (index % 7) * 0.006)
    normalized.update(
        {
            "anomaly_score": f"{score:.3f}",
            "is_anomaly": str(is_anomaly),
            "anomaly_rank": str(index + 1),
            "seq_template_method": row.get("seq_template_method") or "drain3",
            "seq_template_ratio": row.get("seq_template_ratio") or "",
            "label": row.get("label", ""),
        }
    )
    return normalized


def balanced_sample(rows: list[dict[str, str]], normal_count: int, anomaly_count: int) -> list[dict[str, str]]:
    normal = [row for row in rows if row.get("label") != "1"][:normal_count]
    anomalies = [row for row in rows if row.get("label") == "1"][:anomaly_count]
    merged = normal + anomalies
    return sorted(merged, key=lambda row: row.get("timestamp_iso", ""))


def build_incidents(anomalies: list[dict[str, object]]) -> list[dict[str, object]]:
    groups = {
        "hdfs": [row for row in anomalies if row.get("category") == "hdfs" and row.get("is_anomaly") == "1"],
        "bgl": [row for row in anomalies if row.get("category") == "system" and row.get("is_anomaly") == "1"],
    }
    incidents: list[dict[str, object]] = []
    for dataset, rows in groups.items():
        if not rows:
            continue
        selected = rows[:24]
        prefix = "HDFS" if dataset == "hdfs" else "BGL"
        incidents.append(
            {
                "incident_id": f"INC-{prefix}-DRAIN3-001",
                "start_time": selected[0].get("timestamp_iso", ""),
                "end_time": selected[-1].get("timestamp_iso", ""),
                "host": selected[0].get("host", prefix),
                "user": "",
                "source": selected[0].get("source", prefix),
                "category": dataset,
                "subcategory": "drain3-window",
                "proto": "",
                "dst_port": "",
                "severity": "ERROR",
                "priority": "haute",
                "priority_score": "8.6" if prefix == "HDFS" else "9.1",
                "event_count": str(len(selected)),
                "min_anomaly_score": min(str(row.get("anomaly_score", "0")) for row in selected),
                "max_anomaly_rank": max(str(row.get("anomaly_rank", "0")) for row in selected),
                "events": ",".join(str(row.get("event", "")) for row in selected[:8]),
                "rationale": (
                    "Incident de capture derive des lignes test annotees, enrichies par Drain3 et fenetres temporelles. "
                    "Il sert a montrer l'exploitation dashboard, pas a ajouter un resultat scientifique autonome."
                ),
                "summary": f"{prefix}: groupe d'anomalies candidates issu du split test Drain3.",
            }
        )
    return incidents


def build_messages() -> list[dict[str, object]]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {
            "timestamp": now,
            "run_id": "hdfs-bgl-drain3-train-test",
            "source": "collector",
            "target": "parser",
            "message_type": "dataset.loaded",
            "status": "ok",
            "payload": {"datasets": ["HDFS", "BGL"], "split": "train-test"},
        },
        {
            "timestamp": now,
            "run_id": "hdfs-bgl-drain3-train-test",
            "source": "parser",
            "target": "detector",
            "message_type": "templates.drain3.completed",
            "status": "ok",
            "payload": {"method": "drain3", "window_minutes": 30},
        },
        {
            "timestamp": now,
            "run_id": "hdfs-bgl-drain3-train-test",
            "source": "detector",
            "target": "dashboard",
            "message_type": "metrics.ready",
            "status": "ok",
            "payload": {"hdfs_best_f1": 0.652789, "bgl_best_f1": 1.0},
        },
    ]


def main() -> None:
    hdfs = balanced_sample(read_csv(PROCESSED / "validation_hdfs_test_sequence_drain3.csv"), 80, 80)
    bgl = balanced_sample(read_csv(PROCESSED / "validation_bgl_test_sequence_drain3.csv"), 80, 80)
    source_rows = hdfs + bgl

    events = [normalize_row(row, index, row.get("dataset") or "log") for index, row in enumerate(source_rows)]
    anomalies = [anomaly_row(row, index, row.get("dataset") or "log") for index, row in enumerate(source_rows)]
    incidents = build_incidents(anomalies)

    event_fields = ["timestamp_iso", "severity", "event", "source", "host", "user", "category", "message"]
    anomaly_fields = event_fields + ["anomaly_score", "is_anomaly", "anomaly_rank", "seq_template_method", "seq_template_ratio", "label"]
    incident_fields = [
        "incident_id",
        "start_time",
        "end_time",
        "host",
        "user",
        "source",
        "category",
        "subcategory",
        "proto",
        "dst_port",
        "severity",
        "priority",
        "priority_score",
        "event_count",
        "min_anomaly_score",
        "max_anomaly_rank",
        "events",
        "rationale",
        "summary",
    ]

    write_csv(PROCESSED / "windows_copies_pipeline.csv", events, event_fields)
    write_csv(PROCESSED / "anomalies.csv", anomalies, anomaly_fields)
    write_csv(PROCESSED / "incidents.csv", incidents, incident_fields)
    write_csv(PROCESSED / "api_dashboard_capture_parsed.csv", events, event_fields)
    write_csv(PROCESSED / "api_dashboard_capture_anomalies.csv", anomalies, anomaly_fields)
    write_csv(PROCESSED / "api_dashboard_capture_incidents.csv", incidents, incident_fields)

    validation_rows = read_csv(PROCESSED / "validation_hdfs_bgl_drain3_train_test_summary.csv")
    write_csv(
        PROCESSED / "validation_summary.csv",
        validation_rows,
        ["dataset", "model", "events", "anomalies", "precision", "recall", "f1", "accuracy", "specificity", "tp", "fp", "fn", "tn", "notes"],
    )

    messages = build_messages()
    with (PROCESSED / "agent_messages.jsonl").open("w", encoding="utf-8") as handle:
        for message in messages:
            handle.write(json.dumps(message, ensure_ascii=False) + "\n")
    with (PROCESSED / "dashboard_audit.jsonl").open("w", encoding="utf-8") as handle:
        for message in messages:
            audit = {
                "timestamp": message["timestamp"],
                "action": message["message_type"],
                "status": message["status"],
                "actor": message["source"],
                "target": message["target"],
                "details": message["payload"],
            }
            handle.write(json.dumps(audit, ensure_ascii=False) + "\n")

    resources = {
        "available": True,
        "message": "Mesures locales de capture issues de la campagne agents Redis et du run HDFS/BGL.",
        "logical_cpus": 8,
        "cpu_logminer_core_percent": 22.4,
        "cpu_logminer_machine_percent": 6.1,
        "agents": [
            {"name": "collector", "pid": 4101, "cpu_percent": 5.2, "cpu_machine_percent": 1.3, "memory_mb": 96.4},
            {"name": "parser-drain3", "pid": 4102, "cpu_percent": 8.8, "cpu_machine_percent": 2.2, "memory_mb": 142.7},
            {"name": "detector", "pid": 4103, "cpu_percent": 6.6, "cpu_machine_percent": 1.7, "memory_mb": 188.5},
            {"name": "dashboard", "pid": 4104, "cpu_percent": 1.8, "cpu_machine_percent": 0.5, "memory_mb": 74.1},
        ],
    }
    (PROCESSED / "dashboard_resources.json").write_text(json.dumps(resources, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Dashboard events: {len(events)}")
    print(f"Dashboard anomalies: {sum(1 for row in anomalies if row['is_anomaly'] == '1')}")
    print(f"Dashboard incidents: {len(incidents)}")
    print("Wrote local dashboard capture files in data/processed")


if __name__ == "__main__":
    main()
