"""Agent collecteur Logminer.

Le collecteur decouvre les journaux disponibles dans les zones locales du
projet avant de les remettre a l'orchestrateur. Il ne supprime rien: il produit
un manifeste exploitable par l'API, le dashboard et le memoire.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional


BASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BASE_DIR.parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.bus import LocalMessageBus, MessageBus
from pipeline import detect_kind


SUPPORTED_SUFFIXES = {
    ".csv",
    ".evtx",
    ".json",
    ".jsonl",
    ".log",
    ".pcap",
    ".pcapng",
    ".tcpdump",
    ".txt",
    ".xml",
    ".parquet",
}

SKIPPED_SUFFIXES = {
    ".7z",
    ".gz",
    ".joblib",
    ".pdf",
    ".py",
    ".tar",
    ".zip",
}

DEFAULT_ROOTS = (
    "data/raw/windows_events_admin",
    "data/raw/windows_events",
    "data/raw/Datasets",
    "examples",
)


@dataclass
class LogCandidate:
    path: str
    kind: str
    size_bytes: int
    modified: str
    priority: int


def _project_path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    return path if path.is_absolute() else REPO_ROOT / path


def _iter_files(roots: Iterable[str | Path]) -> Iterable[Path]:
    for root_value in roots:
        root = _project_path(root_value)
        if root.is_file():
            yield root
            continue
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.is_file() and not path.name.startswith("."):
                yield path


def _priority(path: Path, kind: str) -> int:
    text = str(path).lower()
    score = 0
    if "windows_events_admin" in text or "windows_events" in text:
        score += 40
    if kind in {"win_event", "syslog", "cef_leef", "cloudtrail", "apache", "hdfs", "bgl"}:
        score += 25
    if path.suffix.lower() in {".csv", ".parquet"}:
        score += 35
    if "sample" in text or "examples" in text:
        score -= 10
    return score


def discover_logs(
    roots: Iterable[str | Path] = DEFAULT_ROOTS,
    max_files: int = 200,
    max_bytes: int = 100 * 1024 * 1024,
    bus: MessageBus | None = None,
) -> list[LogCandidate]:
    """Decouvre les journaux candidats et les classe par pertinence."""

    candidates: list[LogCandidate] = []
    for path in _iter_files(roots):
        suffix = path.suffix.lower()
        if suffix in SKIPPED_SUFFIXES or suffix not in SUPPORTED_SUFFIXES:
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        if stat.st_size <= 0 or stat.st_size > max_bytes:
            continue
        try:
            kind = "structured" if suffix in {".csv", ".parquet"} else detect_kind(str(path))
        except Exception:
            kind = "unknown"
        candidates.append(
            LogCandidate(
                path=str(path),
                kind=kind,
                size_bytes=stat.st_size,
                modified=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                priority=_priority(path, kind),
            )
        )

    candidates.sort(key=lambda item: (item.priority, item.modified, -item.size_bytes), reverse=True)
    limited = candidates[:max(1, max_files)]

    if bus is not None:
        bus.publish(
            source="collector",
            target="orchestrator",
            message_type="collector.discovery.completed",
            payload={
                "roots": [str(_project_path(root)) for root in roots],
                "candidates": len(limited),
                "selected": limited[0].path if limited else "",
            },
            status="ok" if limited else "warning",
        )

    return limited


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent collecteur Logminer")
    parser.add_argument("--root", action="append", dest="roots", default=[], help="Dossier ou fichier a scanner")
    parser.add_argument("--max-files", type=int, default=50, help="Nombre maximal de candidats retournes")
    parser.add_argument("--max-mb", type=int, default=100, help="Taille maximale par fichier")
    parser.add_argument("--bus", default="", help="Journal de messages JSONL")
    parser.add_argument("--run-id", default=None, help="Identifiant de run")
    args = parser.parse_args(argv)

    bus = LocalMessageBus(args.bus, run_id=args.run_id) if args.bus else None
    roots = args.roots or list(DEFAULT_ROOTS)
    candidates = discover_logs(roots=roots, max_files=args.max_files, max_bytes=args.max_mb * 1024 * 1024, bus=bus)
    for candidate in candidates:
        print(asdict(candidate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
