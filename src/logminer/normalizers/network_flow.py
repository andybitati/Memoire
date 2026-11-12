"""Normalisation des flux réseau tabulaires (CICFlowMeter) vers le schéma commun.

Projette les colonnes présentes dans les exports CICFlowMeter (CICIDS2017,
CSE-CIC-IDS2018) vers les champs réseau du schéma (``schema.columns.COLUMNS``).
Une colonne absente des données reste vide : aucune valeur n'est fabriquée.
L'étiquette de vérité terrain (``Label``) n'est jamais projetée.
"""

from __future__ import annotations

import pandas as pd

try:
    from ..schema.columns import COLUMNS
except ImportError:  # exécution avec src/logminer sur le chemin
    from schema.columns import COLUMNS

# Champ du schéma -> noms possibles de la colonne source, comparés après nettoyage.
ALIASES: dict[str, tuple[str, ...]] = {
    "dst_port": ("destination port", "dst port"),
    "src_port": ("source port", "src port"),
    "src_ip": ("source ip", "src ip"),
    "dst_ip": ("destination ip", "dst ip"),
    "proto": ("protocol",),
    "bytes_sent": ("total length of fwd packets", "totlen fwd pkts"),
}
TIMESTAMP_ALIASES = ("timestamp",)


def _clean(name: str) -> str:
    return str(name).strip().lstrip("﻿").lower()


def _timestamp_iso(values: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(values, errors="coerce", dayfirst=True, format="mixed")
    return parsed.dt.strftime("%Y-%m-%dT%H:%M:%S").fillna("")


def normalize_flows(raw: pd.DataFrame, *, dataset: str, filepath: str) -> pd.DataFrame:
    """Retourne un DataFrame aux colonnes ``COLUMNS``, une ligne par flux."""

    by_clean = {_clean(column): column for column in raw.columns}
    out = pd.DataFrame("", index=raw.index, columns=COLUMNS)
    out["dataset"] = dataset
    out["subtype"] = "network_flow"
    out["filepath"] = filepath
    out["recno"] = [str(index + 1) for index in range(len(raw))]
    for field, aliases in ALIASES.items():
        source = next((by_clean[a] for a in aliases if a in by_clean), None)
        if source is not None:
            out[field] = raw[source].astype(str).str.strip().values
    ts = next((by_clean[a] for a in TIMESTAMP_ALIASES if a in by_clean), None)
    if ts is not None:
        out["timestamp_iso"] = _timestamp_iso(raw[ts].astype(str)).values
    return out.reset_index(drop=True)
