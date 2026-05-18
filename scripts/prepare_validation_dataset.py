"""Prepare des datasets labellises pour valider les detecteurs Logminer.

Les datasets publics HDFS et BGL sont volumineux. Ce script fabrique des CSV
normalises et echantillonnes avec une colonne `label`, afin que
`src/logminer/agents/model_compare.py` puisse calculer precision, rappel et F1.

Exemples:
    python scripts/prepare_validation_dataset.py hdfs \
        --input data/raw/Datasets/Dataset_csv/hdfs.csv \
        --labels data/raw/Datasets/HDFS_1/anomaly_label.csv \
        --output data/processed/validation_hdfs.csv

    python scripts/prepare_validation_dataset.py bgl \
        --input data/raw/Datasets/BGL/BGL.log \
        --output data/processed/validation_bgl.csv
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


BLOCK_RE = re.compile(r"\bblk_-?\d+\b")
BGL_RE = re.compile(
    r"^(?P<label>[-*A-Za-z]+)\s+"
    r"(?P<event_id>\d+)\s+"
    r"(?P<date_raw>\d{4}\.\d{2}\.\d{2})\s+"
    r"(?P<node>\S+)\s+"
    r"(?P<timestamp_raw>\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d+)\s+"
    r"(?P<source>\S+)\s+RAS\s+"
    r"(?P<subsystem>\S+)\s+"
    r"(?P<severity>[A-Za-z]+)\s+"
    r"(?P<message>.*)$"
)


def _label_to_binary(value: object) -> int:
    """Convertit les conventions de labels publiques vers 0/1."""

    text = str(value).strip().lower()
    return int(text in {"1", "true", "yes", "anomaly", "abnormal", "attack", "failure", "fail", "*"})


def _bgl_label_to_binary(value: str) -> int:
    """Dans BGL, '-' signifie normal; les autres marqueurs signalent anomalie."""

    marker = value.strip()
    return 0 if marker == "-" else 1


def _bgl_timestamp_to_iso(value: str) -> str:
    return pd.to_datetime(value, format="%Y-%m-%d-%H.%M.%S.%f", errors="coerce", utc=True).isoformat()


def _can_add(label: int, counters: dict[int, int], max_normal: int, max_anomaly: int) -> bool:
    if label == 1:
        return counters[1] < max_anomaly
    return counters[0] < max_normal


def _quotas_reached(counters: dict[int, int], max_normal: int, max_anomaly: int) -> bool:
    return counters[0] >= max_normal and counters[1] >= max_anomaly


def prepare_hdfs(
    input_csv: Path,
    labels_csv: Path,
    output_csv: Path,
    max_normal: int,
    max_anomaly: int,
    chunksize: int,
) -> Path:
    """Prepare HDFS en reliant chaque ligne au label de son block id.

    HDFS est labellise par bloc (`blk_...`) dans `anomaly_label.csv`. Comme un
    bloc apparait sur plusieurs lignes, on extrait le block id depuis le message
    et on propage son label a chaque evenement normalise.
    """

    labels = pd.read_csv(labels_csv, dtype=str)
    labels.columns = [column.strip() for column in labels.columns]
    block_column = "BlockId"
    label_column = "Label"
    if block_column not in labels or label_column not in labels:
        raise ValueError("Le fichier HDFS doit contenir les colonnes BlockId et Label")

    label_map = {
        str(row[block_column]).strip(): _label_to_binary(row[label_column])
        for _, row in labels.iterrows()
    }

    counters = {0: 0, 1: 0}
    selected_chunks: list[pd.DataFrame] = []

    for chunk in pd.read_csv(input_csv, sep=";", dtype=str, chunksize=chunksize, keep_default_na=False):
        messages = chunk.get("message", pd.Series("", index=chunk.index)).astype(str)
        chunk["block_id"] = messages.str.extract(f"({BLOCK_RE.pattern})", expand=False).fillna("")
        chunk["label"] = chunk["block_id"].map(label_map).fillna(0).astype(int)

        rows = []
        for _, row in chunk.iterrows():
            label = int(row["label"])
            if _can_add(label, counters, max_normal, max_anomaly):
                rows.append(row)
                counters[label] += 1
            if _quotas_reached(counters, max_normal, max_anomaly):
                break

        if rows:
            selected_chunks.append(pd.DataFrame(rows))
        if _quotas_reached(counters, max_normal, max_anomaly):
            break

    if not selected_chunks:
        raise ValueError("Aucune ligne HDFS selectionnee")

    output = pd.concat(selected_chunks, ignore_index=True)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_csv, sep=";", index=False, encoding="utf-8-sig")
    return output_csv


def prepare_bgl(input_log: Path, output_csv: Path, max_normal: int, max_anomaly: int) -> Path:
    """Prepare BGL depuis le log brut en conservant le label de debut de ligne."""

    counters = {0: 0, 1: 0}
    rows: list[dict[str, object]] = []

    with input_log.open("r", encoding="utf-8", errors="replace") as handle:
        for lineno, line in enumerate(handle, start=1):
            match = BGL_RE.match(line.strip())
            if not match:
                continue

            label = _bgl_label_to_binary(match.group("label"))
            if not _can_add(label, counters, max_normal, max_anomaly):
                continue

            timestamp_raw = match.group("timestamp_raw")
            rows.append(
                {
                    "dataset": "bgl",
                    "filepath": str(input_log),
                    "lineno": lineno,
                    "event": match.group("event_id"),
                    "timestamp_iso": _bgl_timestamp_to_iso(timestamp_raw),
                    "source": match.group("source"),
                    "host": match.group("node"),
                    "severity": match.group("severity").upper(),
                    "category": "system",
                    "subcategory": match.group("subsystem"),
                    "message": match.group("message"),
                    "label": label,
                    "raw_label": match.group("label"),
                }
            )
            counters[label] += 1

            if _quotas_reached(counters, max_normal, max_anomaly):
                break

    if not rows:
        raise ValueError("Aucune ligne BGL selectionnee")

    output = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_csv, sep=";", index=False, encoding="utf-8-sig")
    return output_csv


def summarize(path: Path) -> None:
    data = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False)
    labels = data["label"].astype(int).value_counts().sort_index().to_dict()
    print(f"Dataset prepare: {path}")
    print(f"Lignes: {len(data)}")
    print(f"Labels: normal={labels.get(0, 0)} anomaly={labels.get(1, 0)}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare HDFS/BGL pour la validation precision/rappel/F1")
    parser.add_argument("dataset", choices=["hdfs", "bgl"], help="Dataset a preparer")
    parser.add_argument("--input", required=True, type=Path, help="Fichier source HDFS CSV ou BGL log brut")
    parser.add_argument("--labels", type=Path, help="Labels HDFS anomaly_label.csv")
    parser.add_argument("--output", required=True, type=Path, help="CSV normalise labellise a produire")
    parser.add_argument("--max-normal", type=int, default=5000, help="Nombre maximal de lignes normales")
    parser.add_argument("--max-anomaly", type=int, default=5000, help="Nombre maximal de lignes anormales")
    parser.add_argument("--chunksize", type=int, default=100000, help="Taille des blocs de lecture CSV")
    args = parser.parse_args(argv)

    if args.dataset == "hdfs":
        if not args.labels:
            raise SystemExit("--labels est requis pour HDFS")
        output = prepare_hdfs(args.input, args.labels, args.output, args.max_normal, args.max_anomaly, args.chunksize)
    else:
        output = prepare_bgl(args.input, args.output, args.max_normal, args.max_anomaly)

    summarize(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
