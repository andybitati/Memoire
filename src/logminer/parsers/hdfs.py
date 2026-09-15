"""Parseur léger pour les journaux HDFS de Loghub.

Le format court utilisé par HDFS_v1 est traité explicitement. Le parseur ne
charge pas le fichier en mémoire et n'apprend aucun état : Drain3 reste réservé
aux protocoles expérimentaux qui le gèlent après l'entraînement.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone

from writer import emit


HDFS_SHORT_RE = re.compile(
    r"^(?P<date>\d{6})\s+(?P<time>\d{6})\s+(?P<pid>\d+)\s+"
    r"(?P<severity>[A-Za-z]+)\s+(?P<source>[^:]+):\s*(?P<message>.*)$"
)
BLOCK_RE = re.compile(r"blk_-?\d+")
IP_PAIR_RE = re.compile(
    r"src:\s*/?(?P<src_ip>[0-9a-fA-F:.]+):(?P<src_port>\d+)\s+"
    r"dest:\s*/?(?P<dst_ip>[0-9a-fA-F:.]+):(?P<dst_port>\d+)"
)


def _timestamp(date_value: str, time_value: str) -> str:
    parsed = datetime.strptime(date_value + time_value, "%y%m%d%H%M%S")
    return parsed.replace(tzinfo=timezone.utc).isoformat()


def _severity(value: str) -> str:
    upper = str(value or "").upper()
    return {"WARN": "WARNING", "ERR": "ERROR", "FATAL": "CRITICAL"}.get(upper, upper)


class Parser:
    subtype = "hdfs"

    def parse(
        self,
        path: str,
        writer,
        sep: str = ";",
        split_rows: int = 0,
        progress_every: int = 0,
        use_tqdm: bool = False,
        debug: bool = False,
    ) -> None:
        del sep, split_rows, progress_every, use_tqdm, debug
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for lineno, line in enumerate(handle, start=1):
                raw = line.rstrip("\r\n")
                if not raw.strip():
                    continue
                match = HDFS_SHORT_RE.match(raw)
                if match is None:
                    emit(
                        writer,
                        {
                            "dataset": "hdfs",
                            "subtype": self.subtype,
                            "filepath": path,
                            "lineno": lineno,
                            "category": "system",
                            "subcategory": "hdfs_unparsed",
                            "message": raw,
                        },
                    )
                    continue

                groups = match.groupdict()
                message = groups["message"].strip()
                block = BLOCK_RE.search(message)
                addresses = IP_PAIR_RE.search(message)
                payload = {
                    "dataset": "hdfs",
                    "subtype": self.subtype,
                    "filepath": path,
                    "lineno": lineno,
                    "timestamp_iso": _timestamp(groups["date"], groups["time"]),
                    "severity": _severity(groups["severity"]),
                    "event": block.group(0) if block else "",
                    "source": groups["source"].strip(),
                    "component": groups["source"].strip(),
                    "pid": groups["pid"],
                    "category": "system",
                    "subcategory": "hdfs",
                    "message": message,
                }
                if addresses:
                    payload.update(addresses.groupdict())
                emit(writer, payload)
