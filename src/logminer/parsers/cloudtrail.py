"""Parseur AWS CloudTrail JSON ou JSONL."""

from __future__ import annotations

import gzip
import json
import re
from pathlib import Path
from typing import Any, Iterable

from writer import emit


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\r", " ").replace("\n", " ")).strip()


def _open_text(path: str):
    if path.lower().endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8", errors="ignore")
    return open(path, "r", encoding="utf-8", errors="ignore")


def _records_from_json(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict) and isinstance(value.get("Records"), list):
        for record in value["Records"]:
            if isinstance(record, dict):
                yield record
    elif isinstance(value, dict):
        yield value
    elif isinstance(value, list):
        for record in value:
            if isinstance(record, dict):
                yield record


def _user(record: dict[str, Any]) -> str:
    identity = record.get("userIdentity") if isinstance(record.get("userIdentity"), dict) else {}
    return _clean(identity.get("userName") or identity.get("principalId") or identity.get("arn") or "")


class Parser:
    subtype = "cloudtrail"

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
        recno = 0
        text = Path(path).read_text(encoding="utf-8", errors="ignore") if not path.lower().endswith(".gz") else ""
        if text.strip().startswith("{") and '"Records"' in text[:2048]:
            try:
                values = json.loads(text)
                for record in _records_from_json(values):
                    recno += 1
                    self._emit_record(writer, path, recno, record)
                return
            except json.JSONDecodeError:
                pass

        with _open_text(path) as handle:
            for lineno, line in enumerate(handle, start=1):
                raw = line.strip()
                if not raw:
                    continue
                try:
                    value = json.loads(raw)
                except json.JSONDecodeError:
                    emit(writer, {"dataset": "cloudtrail", "subtype": self.subtype, "filepath": path, "lineno": lineno, "message": raw})
                    continue
                for record in _records_from_json(value):
                    recno += 1
                    self._emit_record(writer, path, recno, record, lineno)

    def _emit_record(self, writer, path: str, recno: int, record: dict[str, Any], lineno: int = 0) -> None:
        emit(
            writer,
            {
                "dataset": "cloudtrail",
                "subtype": self.subtype,
                "filepath": path,
                "lineno": lineno,
                "recno": recno,
                "timestamp_iso": _clean(record.get("eventTime")),
                "severity": "INFO",
                "event": _clean(record.get("eventName")),
                "source": _clean(record.get("eventSource")),
                "component": _clean(record.get("awsRegion")),
                "user": _user(record),
                "src_ip": _clean(record.get("sourceIPAddress")),
                "user_agent": _clean(record.get("userAgent")),
                "category": "cloud",
                "subcategory": "aws_cloudtrail",
                "message": _clean(record.get("errorMessage") or record.get("eventName") or json.dumps(record, ensure_ascii=False)),
            },
        )
