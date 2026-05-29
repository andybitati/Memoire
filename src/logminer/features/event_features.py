"""Conversion des evenements normalises en variables utilisables par le ML.

Le projet manipule deux types de donnees:
    - le schema Logminer normalise (`src_port`, `dst_port`, `severity`, etc.);
    - des datasets reseau deja structures comme UNSW/CIC-DDoS, avec des
      colonnes numeriques riches (`Flow Duration`, `Total Fwd Packets`, etc.).

Le constructeur de features doit donc rester compatible avec le schema commun,
mais aussi recuperer les colonnes numeriques utiles des datasets reseau.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


NUMERIC_COLUMNS = ["src_port", "dst_port", "http_status", "bytes_sent", "length", "pid", "tid"]
CATEGORICAL_COLUMNS = ["dataset", "subtype", "severity", "category", "subcategory"]
OPTIONAL_CATEGORICAL_COLUMNS = ["event", "source", "host", "proto", "protocol", "service", "state"]

# Colonnes a ne pas injecter comme variables ML generiques. Les labels doivent
# rester reserves a l'evaluation; les identifiants/timestamps risquent surtout
# d'apprendre la provenance ou l'ordre des lignes au lieu du comportement.
EXCLUDED_GENERIC_COLUMNS = {
    "label",
    "attack_cat",
    "class",
    "target",
    "is_anomaly",
    "anomaly_score",
    "anomaly_rank",
    "timestamp_iso",
    "timestamp",
    "timecreated",
    "date_raw",
    "timestamp_raw",
    "filepath",
    "file",
    "flow id",
    "source ip",
    "destination ip",
    "src_ip",
    "dst_ip",
    "message",
    "content",
    "eventtemplate",
}

SEVERITY_SCORE = {
    "": 0,
    "DEBUG": 1,
    "VERBOSE": 1,
    "INFO": 2,
    "WARNING": 3,
    "ERROR": 4,
    "CRITICAL": 5,
}


def load_events(csv_path: str | Path, sep: str = ";") -> pd.DataFrame:
    """Charge un CSV Logminer en conservant les champs texte."""

    return pd.read_csv(csv_path, sep=sep, dtype=str, keep_default_na=False)


def _to_numeric(series: pd.Series) -> pd.Series:
    # Certains datasets reseau utilisent des virgules ou des valeurs Infinity.
    cleaned = series.astype(str).str.replace(",", ".", regex=False)
    cleaned = cleaned.replace({"Infinity": "", "inf": "", "-inf": ""})
    return pd.to_numeric(cleaned, errors="coerce").fillna(0)


def _safe_feature_name(column: str) -> str:
    return "num_" + "".join(ch.lower() if ch.isalnum() else "_" for ch in str(column)).strip("_")


def _generic_numeric_features(events: pd.DataFrame, existing: set[str]) -> pd.DataFrame:
    """Recupere les colonnes numeriques utiles hors schema Logminer.

    C'est indispensable pour UNSWNB15/CIC-DDoS: leurs variables reseau sont
    deja calculees mais ne portent pas les noms normalises de Logminer.
    """

    features = pd.DataFrame(index=events.index)
    for column in events.columns:
        normalized = str(column).strip().lower().lstrip("\ufeff")
        if normalized in existing or normalized in EXCLUDED_GENERIC_COLUMNS:
            continue

        values = _to_numeric(events[column])
        # On garde une colonne seulement si elle contient assez de valeurs
        # numeriques non nulles et si elle varie. Cela evite d'ajouter du bruit.
        raw_numeric = pd.to_numeric(events[column].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        if raw_numeric.notna().mean() < 0.8:
            continue
        if values.nunique(dropna=False) <= 1:
            continue

        feature_name = _safe_feature_name(column)
        if feature_name not in features.columns:
            features[feature_name] = values

    return features


def _message_features(events: pd.DataFrame) -> pd.DataFrame:
    message = events.get("message", pd.Series("", index=events.index)).astype(str)
    return pd.DataFrame(
        {
            "message_len": message.str.len(),
            "message_words": message.str.split().str.len(),
            "message_has_error": message.str.contains("error|failed|denied|exception", case=False, regex=True).astype(int),
            "message_has_ip": message.str.contains(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", regex=True).astype(int),
        },
        index=events.index,
    )


def _time_features(events: pd.DataFrame) -> pd.DataFrame:
    raw_timestamps = events.get("timestamp_iso", pd.Series("", index=events.index))
    timestamps = pd.to_datetime(raw_timestamps, errors="coerce", utc=True)
    return pd.DataFrame(
        {
            "hour": timestamps.dt.hour.fillna(0).astype(int),
            "weekday": timestamps.dt.weekday.fillna(0).astype(int),
            "has_timestamp": timestamps.notna().astype(int),
        },
        index=events.index,
    )


def _categorical_features(events: pd.DataFrame, max_unique: int) -> pd.DataFrame:
    columns: list[str] = []

    for column in CATEGORICAL_COLUMNS:
        if column in events.columns:
            columns.append(column)

    for column in OPTIONAL_CATEGORICAL_COLUMNS:
        if column in events.columns and events[column].nunique(dropna=False) <= max_unique:
            columns.append(column)

    if not columns:
        return pd.DataFrame(index=events.index)

    values = events[columns].fillna("").astype(str)
    return pd.get_dummies(values, prefix=columns, dummy_na=False)


def build_feature_frame(
    events: pd.DataFrame,
    max_categorical_unique: int = 100,
    include_columns: Iterable[str] | None = None,
) -> pd.DataFrame:
    """Construit une matrice de features numeriques pour la detection.

    Args:
        events: DataFrame conforme au schema Logminer.
        max_categorical_unique: limite les colonnes one-hot trop cardinales.
        include_columns: colonnes numeriques additionnelles a inclure.
    """

    features = pd.DataFrame(index=events.index)
    used_numeric_columns: set[str] = set()

    for column in NUMERIC_COLUMNS:
        if column in events.columns:
            features[column] = _to_numeric(events[column])
            used_numeric_columns.add(column.lower())

    for column in include_columns or []:
        if column in events.columns and column not in features.columns:
            features[column] = _to_numeric(events[column])
            used_numeric_columns.add(column.lower())

    severity = events.get("severity", pd.Series("", index=events.index)).astype(str).str.upper()
    features["severity_score"] = severity.map(SEVERITY_SCORE).fillna(0).astype(int)

    parts = [
        features,
        _generic_numeric_features(events, used_numeric_columns),
        _message_features(events),
        _time_features(events),
        _categorical_features(events, max_categorical_unique),
    ]

    matrix = pd.concat(parts, axis=1)
    matrix = matrix.apply(pd.to_numeric, errors="coerce").fillna(0)
    return matrix.astype(float)
