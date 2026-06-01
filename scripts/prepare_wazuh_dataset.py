"""Normalise des exports Wazuh/Elastic CSV vers le schema Logminer.

Les fichiers dates `*-January.csv`, `*-October*.csv`, `*-December*.csv`
contiennent des colonnes Wazuh (`_source.rule.*`, `_source.decoder.*`,
`_source.syscheck.*`, `_source.data.audit.*`). Ce script les convertit en un
CSV commun utilisable par le detecteur et le routeur multi-modeles.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


BASE_COLUMNS = [
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
    "wazuh_rule_level",
    "wazuh_rule_id",
    "wazuh_decoder",
    "wazuh_groups",
    "wazuh_rule_description",
]


def _pick(frame: pd.DataFrame, *names: str) -> pd.Series:
    for name in names:
        if name in frame.columns:
            return frame[name].fillna("").astype(str)
    return pd.Series("", index=frame.index, dtype=str)


def _severity(level: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(level, errors="coerce").fillna(0)
    severity = pd.Series("INFO", index=level.index, dtype=str)
    severity[numeric >= 5] = "WARNING"
    severity[numeric >= 10] = "ERROR"
    severity[numeric >= 14] = "CRITICAL"
    return severity


def _category(decoder: pd.Series, groups: pd.Series) -> pd.Series:
    text = (decoder + " " + groups).str.lower()
    category = pd.Series("wazuh", index=decoder.index, dtype=str)
    category[text.str.contains("web|accesslog|sql|xss|shellshock", regex=True, na=False)] = "web_attack"
    category[text.str.contains("syscheck|fim|integrity", regex=True, na=False)] = "file_integrity"
    category[text.str.contains("audit", regex=True, na=False)] = "linux_audit"
    category[text.str.contains("pam|sshd|sudo|authentication", regex=True, na=False)] = "authentication"
    category[text.str.contains("sca", regex=True, na=False)] = "security_configuration"
    category[text.str.contains("dpkg", regex=True, na=False)] = "package"
    return category


def _normalise_chunk(chunk: pd.DataFrame, source_path: Path, offset: int) -> pd.DataFrame:
    chunk.columns = [str(column).strip().lstrip("\ufeff") for column in chunk.columns]
    output = pd.DataFrame("", index=chunk.index, columns=BASE_COLUMNS)

    timestamp = pd.to_datetime(_pick(chunk, "_source.@timestamp", "_source.timestamp"), errors="coerce", utc=True)
    level = _pick(chunk, "_source.rule.level")
    decoder = _pick(chunk, "_source.decoder.name")
    groups = _pick(chunk, "_source.rule.groups")
    description = _pick(chunk, "_source.rule.description")
    full_log = _pick(chunk, "_source.full_log")
    command = _pick(chunk, "_source.data.audit.command", "_source.data.command")

    output["dataset"] = source_path.stem
    output["subtype"] = "wazuh"
    output["filepath"] = str(source_path)
    output["lineno"] = range(offset + 1, offset + len(chunk) + 1)
    output["recno"] = output["lineno"]
    output["timestamp_iso"] = timestamp.dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ").fillna("")
    output["severity"] = _severity(level)
    output["event"] = _pick(chunk, "_source.rule.id", "_source.syscheck.event", "_source.data.audit.type")
    output["source"] = decoder
    output["component"] = _pick(chunk, "_source.predecoder.program_name", "_source.data.audit.type").where(
        _pick(chunk, "_source.predecoder.program_name", "_source.data.audit.type").ne(""), decoder
    )
    output["host"] = _pick(chunk, "_source.agent.name", "_source.predecoder.hostname")
    output["pid"] = _pick(chunk, "_source.data.audit.pid")
    output["session"] = _pick(chunk, "_source.data.audit.session")
    output["user"] = _pick(chunk, "_source.data.srcuser", "_source.data.dstuser", "_source.data.audit.uid")
    output["uid"] = _pick(chunk, "_source.data.uid", "_source.data.audit.uid")
    output["gid"] = _pick(chunk, "_source.data.audit.gid")
    output["auid"] = _pick(chunk, "_source.data.audit.auid")
    output["euid"] = _pick(chunk, "_source.data.audit.euid")
    output["egid"] = _pick(chunk, "_source.data.audit.egid")
    output["exe"] = _pick(chunk, "_source.data.audit.exe")
    output["path"] = _pick(chunk, "_source.syscheck.path", "_source.data.audit.file.name")
    output["exec_args"] = command
    output["src_ip"] = _pick(chunk, "_source.data.srcip", "_source.agent.ip")
    output["src_port"] = _pick(chunk, "_source.data.srcport")
    output["proto"] = _pick(chunk, "_source.data.protocol")
    output["http_url"] = _pick(chunk, "_source.data.url")
    output["category"] = _category(decoder, groups)
    output["subcategory"] = decoder
    output["message"] = full_log.where(full_log.ne(""), description)
    output["wazuh_rule_level"] = level
    output["wazuh_rule_id"] = _pick(chunk, "_source.rule.id")
    output["wazuh_decoder"] = decoder
    output["wazuh_groups"] = groups
    output["wazuh_rule_description"] = description
    return output


def normalise_files(input_files: list[Path], output_csv: Path, chunksize: int) -> int:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    if output_csv.exists():
        output_csv.unlink()

    total = 0
    write_header = True
    for path in input_files:
        for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunksize, encoding_errors="ignore"):
            normalised = _normalise_chunk(chunk, path, total)
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
        print(f"{path.name}: ajoute")
    return total


def _default_month_files(input_dir: Path) -> list[Path]:
    month_tokens = ("january", "october", "december")
    return sorted(path for path in input_dir.glob("*.csv") if any(token in path.name.lower() for token in month_tokens))


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalise des CSV Wazuh dates vers Logminer")
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/Datasets"), help="Dossier contenant les CSV dates")
    parser.add_argument("--input-file", action="append", default=[], type=Path, help="CSV explicite a ajouter")
    parser.add_argument("-o", "--output", required=True, type=Path, help="CSV normalise a produire")
    parser.add_argument("--chunksize", default=50000, type=int)
    args = parser.parse_args(argv)

    files = args.input_file or _default_month_files(args.input_dir)
    if not files:
        raise ValueError("Aucun fichier Wazuh trouve")
    rows = normalise_files(files, args.output, args.chunksize)
    print(f"CSV Wazuh normalise: {args.output}")
    print(f"Lignes: {rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
