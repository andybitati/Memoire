"""Memoire de feedback analyste appliquee aux anomalies candidates."""

from __future__ import annotations

import hashlib
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.audit import read_audit


TOKEN_RE = re.compile(r"[a-zA-Z0-9_./:-]+")


@dataclass(frozen=True)
class FeedbackProfile:
    decisions: int
    rejects: Counter[str]
    accepts: Counter[str]
    reclassifies: Counter[str]


def _norm(value: object) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text


def _row_value(row: pd.Series, *columns: str) -> str:
    lower = {str(column).lower(): column for column in row.index}
    for column in columns:
        original = lower.get(column.lower())
        if original is not None:
            value = _norm(row.get(original, ""))
            if value:
                return value
    return ""


def feedback_key_from_values(*, category: str = "", severity: str = "", event: str = "", source: str = "", message: str = "") -> str:
    """Construit une cle stable de similarite pour un signal analyste."""

    message_tokens = TOKEN_RE.findall(_norm(message))[:10]
    raw = "|".join(
        [
            _norm(category) or "unknown",
            _norm(severity) or "unknown",
            _norm(event) or "unknown",
            _norm(source) or "unknown",
            " ".join(message_tokens),
        ]
    )
    return hashlib.sha1(raw.encode("utf-8", errors="ignore")).hexdigest()[:16]


def feedback_key_from_row(row: pd.Series) -> str:
    return feedback_key_from_values(
        category=_row_value(row, "category", "wazuh_groups", "_source.rule.groups"),
        severity=_row_value(row, "severity", "wazuh_rule_level", "_source.rule.level"),
        event=_row_value(row, "event", "subcategory", "wazuh_rule_id", "_source.rule.id"),
        source=_row_value(row, "source", "component", "wazuh_decoder", "_source.decoder.name"),
        message=_row_value(row, "message", "wazuh_rule_description", "_source.rule.description", "_source.full_log"),
    )


def load_feedback_profile(limit: int = 1000) -> FeedbackProfile:
    """Charge les decisions analyste auditees et les agrège par motif."""

    rejects: Counter[str] = Counter()
    accepts: Counter[str] = Counter()
    reclassifies: Counter[str] = Counter()
    decisions = 0
    for entry in read_audit(limit=limit):
        if not entry.action.startswith("alert."):
            continue
        details: dict[str, Any] = entry.details or {}
        key = feedback_key_from_values(
            category=str(details.get("category") or ""),
            severity=str(details.get("severity") or ""),
            event=str(details.get("event") or entry.target or ""),
            source=str(details.get("source") or ""),
            message=str(details.get("reason") or ""),
        )
        decision = entry.action.replace("alert.", "", 1)
        decisions += 1
        if decision == "reject":
            rejects[key] += 1
        elif decision == "accept":
            accepts[key] += 1
        elif decision == "reclassify":
            reclassifies[key] += 1
    return FeedbackProfile(decisions=decisions, rejects=rejects, accepts=accepts, reclassifies=reclassifies)


def apply_feedback_memory(
    anomalies: pd.DataFrame,
    *,
    profile: FeedbackProfile | None = None,
    reject_penalty: int = 18,
    accept_bonus: int = 12,
    reclassify_penalty: int = 8,
) -> pd.DataFrame:
    """Ajoute des colonnes memoire et ajuste la priorite des anomalies.

    La fonction ne supprime aucune ligne. Elle rend l'effet du feedback visible
    par des colonnes dediees afin que l'audit reste possible.
    """

    if anomalies.empty:
        result = anomalies.copy()
        result["memory_feedback_key"] = ""
        result["memory_reject_count"] = 0
        result["memory_accept_count"] = 0
        result["memory_reclassify_count"] = 0
        result["memory_priority_delta"] = 0
        result["memory_priority_score"] = 0
        result["memory_action_hint"] = "no_feedback"
        return result

    feedback = profile or load_feedback_profile()
    result = anomalies.copy()
    keys = result.apply(feedback_key_from_row, axis=1)
    reject_counts = keys.map(lambda key: int(feedback.rejects.get(key, 0)))
    accept_counts = keys.map(lambda key: int(feedback.accepts.get(key, 0)))
    reclassify_counts = keys.map(lambda key: int(feedback.reclassifies.get(key, 0)))

    score = pd.to_numeric(result.get("anomaly_score", pd.Series(0, index=result.index)), errors="coerce").fillna(0)
    is_anomaly = pd.to_numeric(result.get("is_anomaly", pd.Series(0, index=result.index)), errors="coerce").fillna(0)
    severity = result.get("severity", pd.Series("", index=result.index)).astype(str).str.upper()
    severity_score = severity.map({"CRITICAL": 90, "ERROR": 70, "WARNING": 45, "INFO": 25}).fillna(20)
    anomaly_depth = (-score).clip(lower=0, upper=1) * 25
    base_priority = severity_score + anomaly_depth + is_anomaly.clip(lower=0, upper=1) * 10
    delta = accept_counts * accept_bonus - reject_counts * reject_penalty - reclassify_counts * reclassify_penalty
    adjusted = (base_priority + delta).clip(lower=0, upper=100).round(2)

    result["memory_feedback_key"] = keys
    result["memory_reject_count"] = reject_counts
    result["memory_accept_count"] = accept_counts
    result["memory_reclassify_count"] = reclassify_counts
    result["memory_priority_delta"] = delta
    result["memory_priority_score"] = adjusted
    result["memory_action_hint"] = "no_feedback"
    result.loc[reject_counts > 0, "memory_action_hint"] = "downrank_repeated_rejection"
    result.loc[reclassify_counts > 0, "memory_action_hint"] = "review_reclassified_pattern"
    result.loc[accept_counts > reject_counts, "memory_action_hint"] = "promote_confirmed_pattern"
    return result


def apply_feedback_memory_to_csv(input_csv: str | Path, output_csv: str | Path | None = None, *, sep: str = ";") -> str:
    input_path = Path(input_csv)
    output_path = Path(output_csv) if output_csv else input_path
    frame = pd.read_csv(input_path, sep=sep, dtype=str, keep_default_na=False)
    enriched = apply_feedback_memory(frame)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(output_path, sep=sep, index=False, encoding="utf-8-sig")
    return str(output_path)
