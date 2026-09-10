"""Parseur léger pour le journal Blue Gene/L publié dans Loghub."""

from __future__ import annotations

import re
from datetime import datetime, timezone

from writer import emit


BGL_RE = re.compile(
    r"^(?P<label>\S+)\s+(?P<epoch>\d+)\s+(?P<date>\d{4}\.\d{2}\.\d{2})\s+"
    r"(?P<location>\S+)\s+(?P<timestamp>\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d+)\s+"
    r"(?P<node>\S+)\s+RAS\s+(?P<component>\S+)\s+(?P<severity>\S+)\s*(?P<message>.*)$"
)


def _timestamp(value: str) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d-%H.%M.%S.%f").replace(tzinfo=timezone.utc).isoformat()
    except ValueError:
        return ""


def _severity(value: str) -> str:
    upper = str(value or "").upper()
    return {"WARN": "WARNING", "ERR": "ERROR", "FATAL": "CRITICAL"}.get(upper, upper)


class Parser:
    subtype = "bgl"

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
                match = BGL_RE.match(raw)
                if match is None:
                    emit(
                        writer,
                        {
                            "dataset": "bgl",
                            "subtype": self.subtype,
                            "filepath": path,
                            "lineno": lineno,
                            "category": "system",
                            "subcategory": "bgl_unparsed",
                            "message": raw,
                        },
                    )
                    continue

                groups = match.groupdict()
                emit(
                    writer,
                    {
                        "dataset": "bgl",
                        "subtype": self.subtype,
                        "filepath": path,
                        "lineno": lineno,
                        "timestamp_iso": _timestamp(groups["timestamp"]),
                        "severity": _severity(groups["severity"]),
                        "event": groups["label"],
                        "source": groups["component"],
                        "component": groups["component"],
                        "host": groups["node"],
                        "category": "system",
                        "subcategory": "bgl",
                        "message": groups["message"].strip(),
                    },
                )
