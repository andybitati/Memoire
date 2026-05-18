"""Dashboard Streamlit pour les agents Logminer."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


DEFAULT_EVENTS = Path("data/processed/windows_copies_pipeline.csv")
DEFAULT_ANOMALIES = Path("data/processed/anomalies.csv")
DEFAULT_INCIDENTS = Path("data/processed/incidents.csv")
DEFAULT_BUS = Path("data/processed/agent_messages.jsonl")


def load_csv(path: str | Path, sep: str = ";") -> pd.DataFrame:
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False)


def sidebar_paths() -> tuple[Path, Path, Path, Path]:
    st.sidebar.header("Sources")
    events = Path(st.sidebar.text_input("Evenements", str(DEFAULT_EVENTS)))
    anomalies = Path(st.sidebar.text_input("Anomalies", str(DEFAULT_ANOMALIES)))
    incidents = Path(st.sidebar.text_input("Incidents", str(DEFAULT_INCIDENTS)))
    bus = Path(st.sidebar.text_input("Bus", str(DEFAULT_BUS)))
    return events, anomalies, incidents, bus


def filter_frame(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    if df.empty:
        return df

    filtered = df.copy()
    for column in ("host", "severity", "category", "source"):
        if column not in filtered.columns:
            continue
        values = sorted(value for value in filtered[column].dropna().astype(str).unique() if value)
        selected = st.sidebar.multiselect(column, values, default=[], key=f"{prefix}_{column}")
        if selected:
            filtered = filtered[filtered[column].isin(selected)]
    return filtered


def metric_row(events: pd.DataFrame, anomalies: pd.DataFrame, incidents: pd.DataFrame) -> None:
    anomaly_count = 0
    if not anomalies.empty and "is_anomaly" in anomalies.columns:
        anomaly_count = int((anomalies["is_anomaly"].astype(str) == "1").sum())

    cols = st.columns(4)
    cols[0].metric("Evenements", len(events))
    cols[1].metric("Anomalies", anomaly_count)
    cols[2].metric("Incidents", len(incidents))
    cols[3].metric("Sources", events["source"].nunique() if "source" in events.columns and not events.empty else 0)


def timeline(df: pd.DataFrame, title: str) -> None:
    if df.empty or "timestamp_iso" not in df.columns:
        return

    times = pd.to_datetime(df["timestamp_iso"], errors="coerce", utc=True).dropna()
    if times.empty:
        return

    counts = times.dt.floor("h").value_counts().sort_index()
    st.subheader(title)
    st.line_chart(counts)


def show_bus(path: Path) -> None:
    st.subheader("Messages agents")
    if not path.exists():
        st.info("Aucun bus de messages trouve.")
        return

    rows = []
    with path.open("r", encoding="utf-8") as f_in:
        for line in f_in:
            line = line.strip()
            if line:
                rows.append(line)

    st.text_area("JSONL", "\n".join(rows[-30:]), height=220)


def main() -> None:
    st.set_page_config(page_title="Logminer Agents", layout="wide")
    st.title("Logminer - Surveillance multi-agents")

    events_path, anomalies_path, incidents_path, bus_path = sidebar_paths()
    events = load_csv(events_path)
    anomalies = load_csv(anomalies_path)
    incidents = load_csv(incidents_path)

    st.sidebar.subheader("Filtres evenements")
    filtered_events = filter_frame(events, "events")
    st.sidebar.subheader("Filtres anomalies")
    filtered_anomalies = filter_frame(anomalies, "anomalies")

    metric_row(filtered_events, filtered_anomalies, incidents)
    timeline(filtered_events, "Volume horaire des evenements")

    st.subheader("Incidents correles")
    if incidents.empty:
        st.info("Aucun incident disponible.")
    else:
        st.dataframe(incidents, use_container_width=True, height=260)

    st.subheader("Anomalies candidates")
    if filtered_anomalies.empty:
        st.info("Aucune anomalie disponible.")
    else:
        st.dataframe(filtered_anomalies.head(500), use_container_width=True, height=360)

    st.subheader("Evenements normalises")
    if filtered_events.empty:
        st.info("Aucun evenement disponible.")
    else:
        st.dataframe(filtered_events.head(500), use_container_width=True, height=360)

    show_bus(bus_path)


if __name__ == "__main__":
    main()
