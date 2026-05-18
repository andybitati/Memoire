"""Normalisation generique des champs communs Logminer."""

from __future__ import annotations

from typing import Any, Dict

try:
    from .base import BaseNormalizer
except ImportError:
    from base import BaseNormalizer


SEVERITY_MAP = {
    "0": "",
    "1": "CRITICAL",
    "2": "ERROR",
    "3": "WARNING",
    "4": "INFO",
    "5": "VERBOSE",
    "TRACE": "DEBUG",
    "DBG": "DEBUG",
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "INFORMATION": "INFO",
    "INFORMATIONAL": "INFO",
    "NOTICE": "INFO",
    "WARN": "WARNING",
    "WARNING": "WARNING",
    "ERR": "ERROR",
    "ERROR": "ERROR",
    "CRIT": "CRITICAL",
    "CRITICAL": "CRITICAL",
    "ALERT": "CRITICAL",
    "EMERG": "CRITICAL",
    "EMERGENCY": "CRITICAL",
    "FATAL": "CRITICAL",
    "VERBOSE": "VERBOSE",
}


class DefaultNormalizer(BaseNormalizer):
    """Harmonise les valeurs communes sans connaitre le format d'origine."""

    name = "default"

    def normalize(self, event: Dict[str, Any] | None) -> Dict[str, Any]:
        normalized = dict(event or {})

        severity = str(normalized.get("severity") or "").strip()
        if severity:
            normalized["severity"] = SEVERITY_MAP.get(severity.upper(), severity.upper())

        for key in ("dataset", "subtype", "source", "component", "host", "user"):
            if key in normalized and normalized[key] is not None:
                normalized[key] = str(normalized[key]).strip()

        for key in ("src_port", "dst_port", "http_status", "pid", "tid", "length"):
            if key in normalized and normalized[key] is not None:
                normalized[key] = str(normalized[key]).strip()

        return normalized
