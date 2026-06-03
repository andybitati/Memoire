"""Parseur Apache/Nginx access log."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any

from writer import emit


COMBINED = re.compile(
    r'^(?P<src_ip>\S+)\s+\S+\s+(?P<user>\S+)\s+\[(?P<dt>[^\]]+)\]\s+'
    r'"(?P<method>[A-Z]+)\s+(?P<url>[^"]*?)(?:\s+HTTP/[^"]*)?"\s+'
    r"(?P<status>\d{3})\s+(?P<bytes>\S+)"
    r'(?:\s+"(?P<referrer>[^"]*)"\s+"(?P<user_agent>[^"]*)")?'
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\r", " ").replace("\n", " ")).strip()


def _timestamp(value: str) -> str:
    for fmt in ("%d/%b/%Y:%H:%M:%S %z", "%d/%b/%Y:%H:%M:%S"):
        try:
            parsed = datetime.strptime(value, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except ValueError:
            continue
    return ""


def _severity(status: str) -> str:
    if not status.isdigit():
        return ""
    code = int(status)
    if code >= 500:
        return "ERROR"
    if code >= 400:
        return "WARN"
    return "INFO"


class Parser:
    subtype = "apache"

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
                if raw.startswith("{"):
                    try:
                        self._emit_json(writer, path, lineno, json.loads(raw), raw)
                        continue
                    except json.JSONDecodeError:
                        pass
                match = COMBINED.match(raw)
                if not match:
                    emit(writer, {"dataset": "web", "subtype": self.subtype, "filepath": path, "lineno": lineno, "message": raw})
                    continue
                groups = match.groupdict()
                emit(
                    writer,
                    {
                        "dataset": "web",
                        "subtype": self.subtype,
                        "filepath": path,
                        "lineno": lineno,
                        "timestamp_iso": _timestamp(groups.get("dt") or ""),
                        "severity": _severity(groups.get("status") or ""),
                        "event": groups.get("status", ""),
                        "source": "apache",
                        "src_ip": groups.get("src_ip", ""),
                        "user": "" if groups.get("user") == "-" else groups.get("user", ""),
                        "http_method": groups.get("method", ""),
                        "http_url": groups.get("url", ""),
                        "http_status": groups.get("status", ""),
                        "bytes_sent": "" if groups.get("bytes") == "-" else groups.get("bytes", ""),
                        "referrer": groups.get("referrer", ""),
                        "user_agent": groups.get("user_agent", ""),
                        "category": "web",
                        "subcategory": "access",
                        "message": raw,
                    },
                )

    def _emit_json(self, writer, path: str, lineno: int, row: dict[str, Any], raw: str) -> None:
        status = _clean(row.get("status") or row.get("status_code") or row.get("http_status"))
        emit(
            writer,
            {
                "dataset": "web",
                "subtype": self.subtype,
                "filepath": path,
                "lineno": lineno,
                "timestamp_iso": _clean(row.get("timestamp") or row.get("time") or row.get("@timestamp")),
                "severity": _severity(status),
                "event": status,
                "source": _clean(row.get("server") or "apache"),
                "src_ip": _clean(row.get("remote_addr") or row.get("src_ip") or row.get("ip")),
                "user": _clean(row.get("user") or row.get("remote_user")),
                "http_method": _clean(row.get("method") or row.get("request_method")),
                "http_url": _clean(row.get("uri") or row.get("url") or row.get("path")),
                "http_status": status,
                "bytes_sent": _clean(row.get("bytes") or row.get("bytes_sent")),
                "referrer": _clean(row.get("referrer")),
                "user_agent": _clean(row.get("user_agent")),
                "category": "web",
                "subcategory": "access",
                "message": _clean(row.get("message") or raw),
            },
        )
