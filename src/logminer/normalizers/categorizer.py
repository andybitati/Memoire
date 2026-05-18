"""Categorisation explicable des evenements de securite."""

from __future__ import annotations

import re
from typing import Any, Dict, Tuple

try:
    from .base import BaseNormalizer
except ImportError:
    from base import BaseNormalizer


SYSTEM_ERROR = "SYSTEM_ERROR"
AUTHENTICATION = "AUTHENTICATION"
AUTHORIZATION = "AUTHORIZATION"
CONFIGURATION_CHANGE = "CONFIGURATION_CHANGE"
NETWORK_ACTIVITY = "NETWORK_ACTIVITY"
APPLICATION_ERROR = "APPLICATION_ERROR"
INTRUSION_ATTEMPT = "INTRUSION_ATTEMPT"
DOS_ATTACK = "DOS_ATTACK"
MALWARE = "MALWARE"
INFORMATIONAL = "INFORMATIONAL"

_RE_FAILED_PWD = re.compile(r"\bfailed password\b|\bauthentication failure\b|bad password|logon failed", re.I)
_RE_ACCEPTED_PWD = re.compile(r"\baccepted password\b|\bsession opened\b|logon successful", re.I)
_RE_INVALID_USER = re.compile(r"\binvalid user\b|unknown user", re.I)
_RE_SUDO = re.compile(r"\bsudo\b|\bCOMMAND=", re.I)
_RE_PERM_DENIED = re.compile(r"permission denied|access denied|not authorized|unauthorized", re.I)
_RE_SCAN = re.compile(r"\b(nmap|masscan|port ?scan|scan detected|recon)\b", re.I)
_RE_BRUTE = re.compile(r"\b(bruteforce|brute force|too many authentication failures)\b", re.I)
_RE_DOS = re.compile(r"\b(ddos|dos|syn flood|syn flooding|flood detected)\b", re.I)
_RE_MALWARE = re.compile(r"\b(malware|trojan|ransomware|backdoor|virus)\b", re.I)
_RE_KERNEL = re.compile(r"\b(kernel|panic|oops|bugcheck)\b", re.I)
_RE_CRASH = re.compile(r"segfault|core dumped|stack trace|application error|faulting application", re.I)
_RE_CONFIG = re.compile(r"service (started|stopped)|configuration|policy|installed|updated", re.I)

WINDOWS_AUTH_FAILURE = {"4625", "4771", "4776"}
WINDOWS_AUTH_SUCCESS = {"4624", "4648"}
WINDOWS_AUTHZ = {"4670", "4672", "4673", "4674"}
WINDOWS_CHANGE = {"4697", "4702", "4719", "4720", "4722", "4726", "4732", "4738", "7045"}


def _safe_int(value: Any) -> int:
    try:
        return int(str(value).strip())
    except Exception:
        return -1


def categorize(event: Dict[str, Any] | None) -> Tuple[str, str]:
    """Retourne `(category, subcategory)` pour un evenement normalise."""

    event = event or {}
    text = " ".join(
        str(event.get(key) or "")
        for key in ("message", "event", "source", "component", "severity", "http_status")
    )
    event_id = str(event.get("event") or "").strip()
    severity = str(event.get("severity") or "").strip().upper()
    subtype = str(event.get("subtype") or event.get("dataset") or "").lower()
    http_status = _safe_int(event.get("http_status"))

    if event_id in WINDOWS_AUTH_FAILURE or _RE_FAILED_PWD.search(text) or _RE_INVALID_USER.search(text):
        return AUTHENTICATION, "failure"
    if event_id in WINDOWS_AUTH_SUCCESS or _RE_ACCEPTED_PWD.search(text):
        return AUTHENTICATION, "success"
    if event_id in WINDOWS_AUTHZ or _RE_SUDO.search(text) or _RE_PERM_DENIED.search(text):
        return AUTHORIZATION, "privilege_or_access"
    if event_id in WINDOWS_CHANGE or _RE_CONFIG.search(text):
        return CONFIGURATION_CHANGE, "system_or_policy"
    if _RE_BRUTE.search(text):
        return INTRUSION_ATTEMPT, "bruteforce"
    if _RE_SCAN.search(text):
        return INTRUSION_ATTEMPT, "reconnaissance"
    if _RE_DOS.search(text):
        return DOS_ATTACK, "flood"
    if _RE_MALWARE.search(text):
        return MALWARE, "malicious_code"
    if http_status >= 500 or _RE_CRASH.search(text):
        return APPLICATION_ERROR, "runtime_failure"
    if http_status in (401, 403):
        return AUTHORIZATION, "http_access_denied"
    if http_status == 404:
        return APPLICATION_ERROR, "http_not_found"
    if _RE_KERNEL.search(text):
        return SYSTEM_ERROR, "kernel"
    if severity in {"ERROR", "CRITICAL"}:
        return SYSTEM_ERROR, severity.lower()
    if subtype in {"pcap", "tcpdump_text", "apache", "cef_leef"}:
        return NETWORK_ACTIVITY, subtype

    return INFORMATIONAL, "generic"


class CategorizerNormalizer(BaseNormalizer):
    """Ajoute `category` et `subcategory` si le parseur ne les a pas fournis."""

    name = "categorizer"

    def normalize(self, event: Dict[str, Any] | None) -> Dict[str, Any]:
        normalized = dict(event or {})
        if normalized.get("category") and normalized.get("subcategory"):
            return normalized

        category, subcategory = categorize(normalized)
        if not normalized.get("category"):
            normalized["category"] = category
        if not normalized.get("subcategory"):
            normalized["subcategory"] = subcategory
        return normalized
