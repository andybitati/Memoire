"""Parseur CEF et LEEF tolerant."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from writer import emit


CEF_HEADER = re.compile(
    r"^CEF:(?P<version>\d+)\|(?P<vendor>[^|]*)\|(?P<product>[^|]*)\|(?P<device_version>[^|]*)\|"
    r"(?P<signature>[^|]*)\|(?P<name>[^|]*)\|(?P<severity>[^|]*)(?:\|(?P<ext>.*))?$"
)
LEEF_HEADER = re.compile(
    r"^LEEF:(?P<version>\d+)\|(?P<vendor>[^|]*)\|(?P<product>[^|]*)\|(?P<device_version>[^|]*)\|"
    r"(?P<signature>[^\t|]*)(?:\t(?P<ext>.*))?$"
)


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\r", " ").replace("\n", " ")).strip()


def _severity(value: str) -> str:
    value = _clean(value).upper()
    if value.isdigit():
        level = int(value)
        if level >= 8:
            return "CRITICAL"
        if level >= 6:
            return "ERROR"
        if level >= 4:
            return "WARN"
        return "INFO"
    return {"WARNING": "WARN", "ERR": "ERROR", "CRIT": "CRITICAL"}.get(value, value)


def _parse_ext(ext: str, delimiter: str) -> dict[str, str]:
    values: dict[str, str] = {}
    if not ext:
        return values
    parts = ext.split(delimiter) if delimiter == "\t" else re.split(r"\s+(?=\w+=)", ext)
    for part in parts:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        values[key.strip()] = value.strip().replace(r"\=", "=").replace(r"\|", "|")
    return values


def _pick_timestamp(values: dict[str, str]) -> str:
    for key in ("rt", "end", "start"):
        raw = values.get(key, "").strip()
        if not raw.isdigit():
            continue
        try:
            epoch = int(raw)
            if epoch > 10_000_000_000:
                epoch = epoch / 1000
            return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
        except (OSError, ValueError, OverflowError):
            continue
    for key in ("devTime", "deviceTime", "endTime", "startTime"):
        raw = values.get(key, "").strip()
        if not raw:
            continue
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc).isoformat()
        except ValueError:
            continue
    return ""


class Parser:
    subtype = "cef_leef"

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
                match = CEF_HEADER.match(raw)
                delimiter = " "
                if not match:
                    match = LEEF_HEADER.match(raw)
                    delimiter = "\t"
                if not match:
                    emit(writer, {"dataset": "siem", "subtype": self.subtype, "filepath": path, "lineno": lineno, "message": raw})
                    continue
                groups = match.groupdict()
                ext = _parse_ext(groups.get("ext") or "", delimiter)
                emit(
                    writer,
                    {
                        "dataset": "siem",
                        "subtype": self.subtype,
                        "filepath": path,
                        "lineno": lineno,
                        "timestamp_iso": _pick_timestamp(ext),
                        "severity": _severity(groups.get("severity") or ext.get("sev", "")),
                        "event": groups.get("signature", ""),
                        "source": groups.get("product", ""),
                        "component": groups.get("vendor", ""),
                        "host": ext.get("dhost") or ext.get("dvchost") or "",
                        "user": ext.get("suser") or ext.get("duser") or "",
                        "src_ip": ext.get("src", ""),
                        "src_port": ext.get("spt", ""),
                        "dst_ip": ext.get("dst", ""),
                        "dst_port": ext.get("dpt", ""),
                        "proto": ext.get("proto", ""),
                        "category": "security",
                        "subcategory": "siem",
                        "message": _clean(groups.get("name") or raw),
                    },
                )
