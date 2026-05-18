"""Agent correlateur d'anomalies.

Le correlateur regroupe les anomalies candidates en incidents lisibles. Pour le
prototype, la correlation est volontairement explicable: fenetre temporelle,
machine, utilisateur, source et categorie.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.bus import LocalMessageBus


GROUP_COLUMNS = ["time_window", "host", "user", "source", "category", "subcategory"]
SEVERITY_RANK = {"": 0, "DEBUG": 1, "VERBOSE": 1, "INFO": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}


def _severity_max(values: pd.Series) -> str:
    ranked = [(SEVERITY_RANK.get(str(value).upper(), 0), str(value).upper()) for value in values]
    if not ranked:
        return ""
    return max(ranked, key=lambda item: item[0])[1]


def _first_non_empty(values: pd.Series) -> str:
    for value in values.astype(str):
        if value.strip():
            return value.strip()
    return ""


def _value_or_unknown(values: pd.Series) -> str:
    return _first_non_empty(values) or "UNKNOWN"


def _summary(group: pd.DataFrame) -> str:
    category = _value_or_unknown(group.get("category", pd.Series(dtype=str)))
    source = _value_or_unknown(group.get("source", pd.Series(dtype=str)))
    host = _value_or_unknown(group.get("host", pd.Series(dtype=str)))
    count = len(group)
    return f"{count} anomalie(s) {category} sur {host} via {source}"


def correlate_anomalies(
    input_csv: str | Path,
    output_csv: str | Path,
    sep: str = ";",
    window_minutes: int = 15,
    bus: LocalMessageBus | None = None,
) -> str:
    """Regroupe les anomalies candidates en incidents."""

    if bus is not None:
        bus.publish(
            source="correlator",
            target="visualizer",
            message_type="correlation.started",
            payload={"input_csv": str(input_csv), "output_csv": str(output_csv), "window_minutes": window_minutes},
        )

    events = pd.read_csv(input_csv, sep=sep, dtype=str, keep_default_na=False)
    if events.empty:
        raise ValueError(f"Aucune anomalie a correler dans {input_csv}")

    if "is_anomaly" in events.columns:
        anomalies = events[events["is_anomaly"].astype(str) == "1"].copy()
    else:
        anomalies = events.copy()

    output_path = Path(output_csv)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    if anomalies.empty:
        incidents = pd.DataFrame(
            columns=[
                "incident_id",
                "start_time",
                "end_time",
                "host",
                "user",
                "source",
                "category",
                "subcategory",
                "severity",
                "event_count",
                "min_anomaly_score",
                "max_anomaly_rank",
                "events",
                "summary",
            ]
        )
        incidents.to_csv(output_path, sep=sep, index=False, encoding="utf-8-sig")
        return str(output_path)

    timestamps = pd.to_datetime(anomalies.get("timestamp_iso", ""), errors="coerce", utc=True)
    anomalies["timestamp_dt"] = timestamps
    anomalies["time_window"] = timestamps.dt.floor(f"{max(window_minutes, 1)}min").astype(str).fillna("unknown")

    for column in GROUP_COLUMNS:
        if column not in anomalies.columns:
            anomalies[column] = ""
        anomalies[column] = anomalies[column].fillna("").astype(str)

    rows = []
    for incident_no, (_, group) in enumerate(anomalies.groupby(GROUP_COLUMNS, dropna=False), start=1):
        valid_times = group["timestamp_dt"].dropna()
        event_ids = sorted(set(value for value in group.get("event", pd.Series(dtype=str)).astype(str) if value))
        anomaly_scores = pd.to_numeric(group.get("anomaly_score", pd.Series(dtype=str)), errors="coerce")
        anomaly_ranks = pd.to_numeric(group.get("anomaly_rank", pd.Series(dtype=str)), errors="coerce")

        rows.append(
            {
                "incident_id": f"INC-{incident_no:06d}",
                "start_time": valid_times.min().isoformat() if not valid_times.empty else "",
                "end_time": valid_times.max().isoformat() if not valid_times.empty else "",
                "host": _value_or_unknown(group["host"]),
                "user": _first_non_empty(group["user"]),
                "source": _value_or_unknown(group["source"]),
                "category": _value_or_unknown(group["category"]),
                "subcategory": _value_or_unknown(group["subcategory"]),
                "severity": _severity_max(group.get("severity", pd.Series(dtype=str))),
                "event_count": len(group),
                "min_anomaly_score": anomaly_scores.min() if not anomaly_scores.dropna().empty else "",
                "max_anomaly_rank": int(anomaly_ranks.max()) if not anomaly_ranks.dropna().empty else "",
                "events": ",".join(event_ids[:20]),
                "summary": _summary(group),
            }
        )

    incidents = pd.DataFrame(rows)
    incidents = incidents.sort_values(["event_count", "severity", "start_time"], ascending=[False, False, True])
    incidents.to_csv(output_path, sep=sep, index=False, encoding="utf-8-sig")

    if bus is not None:
        bus.publish(
            source="correlator",
            target="visualizer",
            message_type="correlation.completed",
            payload={"input_csv": str(input_csv), "output_csv": str(output_path), "incidents": int(len(incidents))},
        )

    return str(output_path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent correlateur Logminer")
    parser.add_argument("-i", "--input", required=True, help="CSV d'anomalies produit par detector.py")
    parser.add_argument("-o", "--output", default="data/processed/incidents.csv", help="CSV des incidents correles")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--window-minutes", type=int, default=15, help="Fenetre temporelle de correlation")
    parser.add_argument("--bus", default="", help="Journal de messages JSONL")
    parser.add_argument("--run-id", default=None, help="Identifiant de run partage entre agents")
    args = parser.parse_args(argv)

    bus = LocalMessageBus(args.bus, run_id=args.run_id) if args.bus else None
    output = correlate_anomalies(args.input, args.output, args.sep, args.window_minutes, bus=bus)
    incidents = pd.read_csv(output, sep=args.sep, dtype=str, keep_default_na=False)
    print(f"CSV incidents: {output}")
    print(f"Incidents correles: {len(incidents)}")
    if bus is not None:
        print(f"Bus: {bus.path}")
        print(f"Run ID: {bus.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
