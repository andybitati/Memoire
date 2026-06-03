"""Parseur syslog RFC3164/RFC5424 heuristique."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from writer import emit


RFC3164 = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s+(?P<time>\d\d:\d\d:\d\d)\s+"
    r"(?P<host>\S+)\s+(?P<proc>[^:\[]+)(?:\[(?P<pid>\d+)\])?:\s*(?P<msg>.*)$"
)
RFC5424 = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})?)\s+"
    r"(?P<host>\S+)\s+(?P<app>\S+)\s+(?P<msg>.*)$"
)
MONTHS = {name: index for index, name in enumerate(("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"), start=1)}


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\r", " ").replace("\n", " ")).strip()


def _severity(message: str) -> str:
    low = message.lower()
    if any(token in low for token in ("critical", "panic", "fatal")):
        return "CRITICAL"
    if any(token in low for token in ("error", "failed", "failure", "denied")):
        return "ERROR"
    if any(token in low for token in ("warn", "invalid", "refused")):
        return "WARN"
    return "INFO"


def _timestamp_3164(mon: str, day: str, hhmmss: str) -> str:
    now = datetime.now(timezone.utc)
    month = MONTHS.get(mon)
    if not month:
        return ""
    try:
        return datetime(now.year, month, int(day), *[int(part) for part in hhmmss.split(":")], tzinfo=timezone.utc).isoformat()
    except ValueError:
        return ""


class Parser:
    subtype = "syslog"

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
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            for lineno, line in enumerate(handle, start=1):
                raw = line.strip()
                if not raw:
                    continue
                match = RFC3164.match(raw)
                if match:
                    groups = match.groupdict()
                    message = _clean(groups.get("msg"))
                    emit(
                        writer,
                        {
                            "dataset": "syslog",
                            "subtype": self.subtype,
                            "filepath": path,
                            "lineno": lineno,
                            "timestamp_iso": _timestamp_3164(groups["mon"], groups["day"], groups["time"]),
                            "severity": _severity(message),
                            "source": _clean(groups.get("proc")),
                            "component": _clean(groups.get("proc")),
                            "host": _clean(groups.get("host")),
                            "pid": _clean(groups.get("pid")),
                            "category": "system",
                            "subcategory": "syslog",
                            "message": message,
                        },
                    )
                    continue

                match = RFC5424.match(raw)
                if match:
                    groups = match.groupdict()
                    message = _clean(groups.get("msg"))
                    emit(
                        writer,
                        {
                            "dataset": "syslog",
                            "subtype": self.subtype,
                            "filepath": path,
                            "lineno": lineno,
                            "timestamp_iso": _clean(groups.get("ts")).replace("Z", "+00:00"),
                            "severity": _severity(message),
                            "source": _clean(groups.get("app")),
                            "component": _clean(groups.get("app")),
                            "host": _clean(groups.get("host")),
                            "category": "system",
                            "subcategory": "syslog",
                            "message": message,
                        },
                    )
                    continue

                emit(
                    writer,
                    {
                        "dataset": "syslog",
                        "subtype": self.subtype,
                        "filepath": path,
                        "lineno": lineno,
                        "category": "system",
                        "subcategory": "syslog_unknown",
                        "message": raw,
                    },
                )
