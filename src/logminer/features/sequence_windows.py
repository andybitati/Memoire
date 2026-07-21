"""Features de fenetrage glissant pour journaux sequentiels HDFS/BGL.

Les logs HDFS et BGL portent une partie importante du signal dans l'ordre des
evenements: repetition d'un template, alternance des composants, rafales
d'erreurs, delai depuis l'evenement precedent. Ce module ajoute ce contexte au
CSV normalise sans imposer un parseur lourd ni un backend deep learning.
"""

from __future__ import annotations

import re
from collections import Counter, deque
from dataclasses import dataclass, field
from typing import Iterable

import pandas as pd

from features.drain_templates import build_templates


TEMPLATE_NUMBER_RE = re.compile(r"\b(?:0x[0-9a-fA-F]+|\d+(?:\.\d+)*)\b")
TEMPLATE_BLOCK_RE = re.compile(r"\bblk_-?\d+\b", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")
BLOCK_RE = re.compile(r"\bblk_-?\d+\b", re.IGNORECASE)
SEVERITY_RANK = {"": 0, "DEBUG": 1, "VERBOSE": 1, "INFO": 2, "WARNING": 3, "ERROR": 4, "CRITICAL": 5}


@dataclass
class _WindowState:
    rows: deque[tuple[pd.Timestamp, str, str, int]] = field(default_factory=deque)
    templates: Counter[str] = field(default_factory=Counter)
    sources: Counter[str] = field(default_factory=Counter)
    error_count: int = 0
    warning_count: int = 0
    previous_time: pd.Timestamp | None = None
    previous_source: str = ""


def message_template(message: str) -> str:
    """Retourne un template textuel leger, Drain-like mais deterministe."""

    text = str(message or "").strip().lower()
    text = TEMPLATE_BLOCK_RE.sub("blk_<*>", text)
    text = TEMPLATE_NUMBER_RE.sub("<*>", text)
    return WHITESPACE_RE.sub(" ", text)


def _first_existing(events: pd.DataFrame, names: Iterable[str]) -> pd.Series:
    lower_to_original = {str(column).lower(): column for column in events.columns}
    for name in names:
        column = lower_to_original.get(name.lower())
        if column is not None:
            return events[column].fillna("").astype(str)
    return pd.Series("", index=events.index, dtype=str)


def _seconds_between(current: pd.Timestamp, previous: pd.Timestamp | None) -> float:
    if previous is None or pd.isna(current) or pd.isna(previous):
        return 0.0
    return max(float((current - previous).total_seconds()), 0.0)


def _severity_level(value: str) -> int:
    return SEVERITY_RANK.get(str(value or "").strip().upper(), 0)


def _prune_state(state: _WindowState, current_time: pd.Timestamp, window: pd.Timedelta) -> None:
    while state.rows and current_time - state.rows[0][0] > window:
        _, template, source, severity = state.rows.popleft()
        state.templates[template] -= 1
        if state.templates[template] <= 0:
            del state.templates[template]
        state.sources[source] -= 1
        if state.sources[source] <= 0:
            del state.sources[source]
        if severity >= SEVERITY_RANK["ERROR"]:
            state.error_count -= 1
        elif severity >= SEVERITY_RANK["WARNING"]:
            state.warning_count -= 1


def _context_key(family: str, host: str, source: str, component: str, block_id: str) -> tuple[str, ...]:
    if family == "hdfs":
        return (host or "UNKNOWN", block_id or source or component or "HDFS")
    if family == "bgl":
        return (host or source or "UNKNOWN", component or source or "BGL")
    return (host or "UNKNOWN", source or component or block_id or "SEQUENCE")


def add_sequence_window_features(
    events: pd.DataFrame,
    *,
    family: str = "auto",
    window_minutes: int = 30,
    template_method: str = "drain3",
    drain_similarity: float = 0.5,
    allow_template_fallback: bool = True,
) -> pd.DataFrame:
    """Ajoute des colonnes `seq_*` a un DataFrame Logminer.

    La fonction preserve les lignes originales et leur ordre final. Les calculs
    sont faits dans l'ordre chronologique quand `timestamp_iso` est disponible.
    """

    if events.empty:
        return events.copy()

    result = events.copy()
    family_values = _first_existing(result, ["dataset", "subtype"]).str.lower()
    detected_family = str(family or "auto").lower()
    if detected_family == "auto":
        text = " ".join(family_values.head(200).astype(str))
        if "hdfs" in text:
            detected_family = "hdfs"
        elif "bgl" in text:
            detected_family = "bgl"
        else:
            detected_family = "sequence"

    raw_time = _first_existing(result, ["timestamp_iso", "timestamp", "timecreated"])
    timestamps = pd.to_datetime(raw_time, errors="coerce", utc=True)
    fallback_time = pd.Timestamp("1970-01-01T00:00:00Z") + pd.to_timedelta(range(len(result)), unit="s")
    sort_time = timestamps.fillna(pd.Series(fallback_time, index=result.index))

    messages = _first_existing(result, ["message", "content"])
    if str(template_method).lower() in {"drain3", "drain", "drain_like"}:
        drain_frame = build_templates(
            messages,
            method=template_method,
            similarity_threshold=drain_similarity,
            allow_fallback=allow_template_fallback,
        )
        templates = drain_frame["drain_template"].astype(str)
        drain_event_ids = drain_frame["drain_event_id"].astype(int)
        template_method_used = drain_frame["drain_template_method"].astype(str)
    else:
        templates = messages.map(message_template)
        drain_event_ids = pd.Series(0, index=result.index, dtype=int)
        template_method_used = pd.Series("simple", index=result.index, dtype=str)
    template_totals = templates.value_counts(dropna=False)
    sources = _first_existing(result, ["source", "component", "event"])
    components = _first_existing(result, ["component", "source"])
    hosts = _first_existing(result, ["host"])
    severities = _first_existing(result, ["severity"]).map(_severity_level)
    block_ids = messages.str.extract(f"({BLOCK_RE.pattern})", flags=re.IGNORECASE, expand=False).fillna("")

    order = pd.DataFrame({"_idx": result.index, "_time": sort_time}).sort_values(["_time", "_idx"])
    states: dict[tuple[str, ...], _WindowState] = {}
    global_state = _WindowState()
    window = pd.Timedelta(minutes=max(int(window_minutes), 1))
    rows: dict[object, dict[str, float]] = {}

    for position, original_index in enumerate(order["_idx"], start=1):
        current_time = sort_time.loc[original_index]
        template = templates.loc[original_index]
        source = sources.loc[original_index]
        component = components.loc[original_index]
        host = hosts.loc[original_index]
        block_id = block_ids.loc[original_index]
        severity = int(severities.loc[original_index])
        key = _context_key(detected_family, host, source, component, block_id)

        context_state = states.setdefault(key, _WindowState())
        _prune_state(global_state, current_time, window)
        _prune_state(context_state, current_time, window)

        global_gap = _seconds_between(current_time, global_state.previous_time)
        context_gap = _seconds_between(current_time, context_state.previous_time)
        context_switch = int(bool(context_state.previous_source and context_state.previous_source != source))

        global_state.rows.append((current_time, template, source, severity))
        global_state.templates[template] += 1
        global_state.sources[source] += 1
        if severity >= SEVERITY_RANK["ERROR"]:
            global_state.error_count += 1
        elif severity >= SEVERITY_RANK["WARNING"]:
            global_state.warning_count += 1
        global_state.previous_time = current_time
        global_state.previous_source = source

        context_state.rows.append((current_time, template, source, severity))
        context_state.templates[template] += 1
        context_state.sources[source] += 1
        if severity >= SEVERITY_RANK["ERROR"]:
            context_state.error_count += 1
        elif severity >= SEVERITY_RANK["WARNING"]:
            context_state.warning_count += 1
        context_state.previous_time = current_time
        context_state.previous_source = source

        context_count = len(context_state.rows)
        template_frequency = int(template_totals.get(template, 0))
        rows[original_index] = {
            "seq_position": float(position),
            "seq_window_minutes": float(max(int(window_minutes), 1)),
            "seq_global_window_event_count": float(len(global_state.rows)),
            "seq_global_window_error_count": float(global_state.error_count),
            "seq_global_window_warning_count": float(global_state.warning_count),
            "seq_global_unique_templates": float(len(global_state.templates)),
            "seq_context_window_event_count": float(context_count),
            "seq_context_window_error_count": float(context_state.error_count),
            "seq_context_window_warning_count": float(context_state.warning_count),
            "seq_context_unique_sources": float(len(context_state.sources)),
            "seq_context_unique_templates": float(len(context_state.templates)),
            "seq_same_template_in_context": float(context_state.templates.get(template, 0)),
            "seq_template_frequency": float(template_frequency),
            "seq_template_ratio": float(template_frequency / max(len(result), 1)),
            "seq_template_is_rare": float(template_frequency <= 2),
            "seq_seconds_since_previous_global": float(global_gap),
            "seq_seconds_since_previous_context": float(context_gap),
            "seq_context_source_switch": float(context_switch),
            "seq_has_block_id": float(bool(block_id)),
            "seq_drain_event_id": float(drain_event_ids.loc[original_index]),
        }

    sequence_features = pd.DataFrame.from_dict(rows, orient="index").reindex(result.index).fillna(0.0)
    for column in sequence_features.columns:
        result[column] = sequence_features[column].astype(float)

    result["seq_family"] = detected_family
    result["seq_template"] = templates
    result["seq_template_method"] = template_method_used
    if str(template_method).lower() in {"drain3", "drain", "drain_like"}:
        result["seq_drain_template"] = templates
    return result
