"""Normalise les datasets Linux/auth vers le schema Logminer.

Les fichiers `linux_auth_logs_*.csv` sont deja tabulaires, mais leurs colonnes
ne correspondent pas directement au contrat commun utilise par les agents. Ce
script les convertit en CSV `;` compatible avec le detecteur Linux et le
routeur multi-modeles.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


LOGMINER_COLUMNS = [
    "dataset",
    "subtype",
    "filepath",
    "lineno",
    "recno",
    "timestamp_iso",
    "severity",
    "event",
    "source",
    "component",
    "host",
    "pid",
    "tid",
    "session",
    "user",
    "uid",
    "gid",
    "auid",
    "euid",
    "egid",
    "exe",
    "path",
    "path_all",
    "exec_args",
    "exec_args_all",
    "exec_env_all",
    "src_ip",
    "src_port",
    "dst_ip",
    "dst_port",
    "proto",
    "length",
    "flags",
    "http_method",
    "http_url",
    "http_status",
    "bytes_sent",
    "user_agent",
    "referrer",
    "category",
    "subcategory",
    "message",
    "anomaly_label",
]


def _pick(frame: pd.DataFrame, name: str, default: str = "") -> pd.Series:
    if name in frame.columns:
        return frame[name].fillna("").astype(str)
    return pd.Series(default, index=frame.index, dtype=str)


def _severity(status: pd.Series, label: pd.Series) -> pd.Series:
    status_lower = status.astype(str).str.lower()
    label_lower = label.astype(str).str.lower()
    severity = pd.Series("INFO", index=status.index, dtype=str)
    severity[status_lower.str.contains("fail|denied|error", regex=True, na=False)] = "WARNING"
    severity[label_lower.ne("") & label_lower.ne("normal")] = "ERROR"
    return severity


def _normalise_chunk(chunk: pd.DataFrame, source_path: Path, offset: int) -> pd.DataFrame:
    chunk.columns = [str(column).strip().lstrip("\ufeff") for column in chunk.columns]

    output = pd.DataFrame("", index=chunk.index, columns=LOGMINER_COLUMNS)
    dataset_name = source_path.stem
    timestamp = pd.to_datetime(_pick(chunk, "timestamp"), errors="coerce", utc=True)
    label = _pick(chunk, "anomaly_label")
    status = _pick(chunk, "status")
    service = _pick(chunk, "service")
    attempts = _pick(chunk, "attempts")
    comment = _pick(chunk, "comment")
    user = _pick(chunk, "username")
    src_ip = _pick(chunk, "source_ip")
    port = _pick(chunk, "port")
    proto = _pick(chunk, "protocol")

    output["dataset"] = dataset_name
    output["subtype"] = "linux_auth"
    output["filepath"] = str(source_path)
    output["lineno"] = range(offset + 1, offset + len(chunk) + 1)
    output["recno"] = output["lineno"]
    output["timestamp_iso"] = timestamp.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ").fillna("")
    output["severity"] = _severity(status, label)
    output["event"] = label.where(label.ne(""), status)
    output["source"] = service
    output["component"] = service
    output["host"] = _pick(chunk, "server").where(_pick(chunk, "server").ne(""), _pick(chunk, "city"))
    output["user"] = user
    output["src_ip"] = src_ip
    output["src_port"] = port
    output["proto"] = proto
    output["category"] = "authentication"
    output["subcategory"] = label.where(label.ne(""), status)
    output["anomaly_label"] = label

    generated = (
        "linux auth "
        + status.where(status.ne(""), "event")
        + " service="
        + service
        + " user="
        + user
        + " src_ip="
        + src_ip
        + " port="
        + port
        + " proto="
        + proto
        + " attempts="
        + attempts
    )
    output["message"] = comment.where(comment.ne(""), generated)
    return output


def normalise_file(input_csv: Path, output_csv: Path, chunksize: int) -> int:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if output_csv.exists():
        output_csv.unlink()

    total = 0
    write_header = True
    chunks = pd.read_csv(input_csv, dtype=str, keep_default_na=False, chunksize=chunksize)
    for chunk in chunks:
        normalised = _normalise_chunk(chunk, input_csv, total)
        normalised.to_csv(
            output_csv,
            sep=";",
            index=False,
            encoding="utf-8-sig",
            mode="w" if write_header else "a",
            header=write_header,
        )
        write_header = False
        total += len(normalised)

    return total


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalise un CSV Linux/auth vers le schema Logminer")
    parser.add_argument("-i", "--input", required=True, type=Path, help="CSV linux_auth_logs_*.csv")
    parser.add_argument("-o", "--output", required=True, type=Path, help="CSV normalise a produire")
    parser.add_argument("--chunksize", type=int, default=100000, help="Lignes lues par bloc")
    args = parser.parse_args(argv)

    rows = normalise_file(args.input, args.output, args.chunksize)
    print(f"CSV Linux/auth normalise: {args.output}")
    print(f"Lignes: {rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
