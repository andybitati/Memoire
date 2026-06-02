"""Parseur JSON Lines generique."""

from __future__ import annotations

import json
import re
from typing import Any

from writer import emit


def _clean(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return re.sub(r"\s+", " ", str(value or "").replace("\r", " ").replace("\n", " ")).strip()


def _pick(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        if key in row and row[key] not in (None, ""):
            return _clean(row[key])
    return ""


class Parser:
    subtype = "jsonl"

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
                try:
                    row = json.loads(raw)
                except json.JSONDecodeError:
                    emit(writer, {"dataset": "jsonl", "subtype": self.subtype, "filepath": path, "lineno": lineno, "message": raw})
                    continue
                if not isinstance(row, dict):
                    emit(writer, {"dataset": "jsonl", "subtype": self.subtype, "filepath": path, "lineno": lineno, "message": _clean(row)})
                    continue
                emit(
                    writer,
                    {
                        "dataset": _pick(row, "dataset") or "jsonl",
                        "subtype": self.subtype,
                        "filepath": path,
                        "lineno": lineno,
                        "recno": _pick(row, "recno", "id"),
                        "timestamp_iso": _pick(row, "timestamp_iso", "timestamp", "@timestamp", "time"),
                        "severity": _pick(row, "severity", "level"),
                        "event": _pick(row, "event", "eventName", "type"),
                        "source": _pick(row, "source", "service", "provider"),
                        "component": _pick(row, "component", "app"),
                        "host": _pick(row, "host", "hostname"),
                        "user": _pick(row, "user", "username"),
                        "src_ip": _pick(row, "src_ip", "source_ip", "remote_addr"),
                        "dst_ip": _pick(row, "dst_ip", "destination_ip"),
                        "http_method": _pick(row, "http_method", "method"),
                        "http_url": _pick(row, "http_url", "url", "path"),
                        "http_status": _pick(row, "http_status", "status"),
                        "category": _pick(row, "category") or "application",
                        "subcategory": _pick(row, "subcategory") or "jsonl",
                        "message": _pick(row, "message", "msg", "description") or raw,
                    },
                )
