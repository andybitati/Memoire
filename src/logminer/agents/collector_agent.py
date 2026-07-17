"""Agent collecteur Logminer.

Le collecteur decouvre les journaux disponibles dans les zones locales du
projet avant de les remettre a l'orchestrateur. Il ne supprime rien: il produit
un manifeste exploitable par l'API, le dashboard et le memoire.
"""

from __future__ import annotations

import argparse
import os
import platform
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    ".audit",
    ".cef",
    ".csv",
    ".err",
    ".evtx",
    ".json",
    ".jsonl",
    ".leef",
    ".log",
    ".ndjson",
    ".out",
    ".pcap",
    ".pcapng",
    ".trace",
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

WINDOWS_DISCOVERY_ROOTS = (
    r"C:\Windows\System32\winevt\Logs",
    r"C:\Program Files\ossec-agent",
    r"C:\Program Files (x86)\ossec-agent",
    r"C:\ProgramData\ossec-agent",
    r"C:\ProgramData\Wazuh",
    r"C:\inetpub\logs\LogFiles",
    r"C:\ProgramData\Docker\containers",
)

LINUX_DISCOVERY_ROOTS = (
    "/var/log",
    "/var/ossec/logs",
    "/var/lib/docker/containers",
    "/opt",
    "/srv",
)

COMMON_ENV_ROOTS = (
    "LOGMINER_LOG_ROOTS",
    "LOGMINER_EXTRA_LOG_ROOTS",
)

WINDOWS_ENV_ROOTS = (
    "ProgramData",
    "ProgramFiles",
    "ProgramFiles(x86)",
    "LOCALAPPDATA",
    "APPDATA",
)

WINDOWS_APP_LOG_RELATIVE_DIRS = (
    "Logs",
    "logs",
    "LogFiles",
    "log",
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


def _split_env_roots(value: str) -> list[str]:
    separators = [";", os.pathsep]
    roots = [value]
    for separator in separators:
        if separator and separator in value:
            roots = [part for item in roots for part in item.split(separator)]
    return [root.strip().strip('"') for root in roots if root.strip()]


def _windows_application_roots() -> list[str]:
    """Retourne des dossiers applicatifs Windows susceptibles de contenir des logs."""

    roots: list[str] = []
    for env_name in WINDOWS_ENV_ROOTS:
        env_value = os.getenv(env_name, "")
        if not env_value:
            continue
        base = Path(env_value)
        for relative in WINDOWS_APP_LOG_RELATIVE_DIRS:
            roots.append(str(base / relative))

    user_profile = os.getenv("USERPROFILE", "")
    if user_profile:
        local = Path(user_profile) / "AppData" / "Local"
        roaming = Path(user_profile) / "AppData" / "Roaming"
        roots.extend(
            [
                str(local / "Logs"),
                str(local / "LogFiles"),
                str(local / "log"),
                str(roaming / "Logs"),
                str(roaming / "LogFiles"),
                str(roaming / "log"),
            ]
        )
    return roots


def deployment_roots(
    *,
    include_project: bool = True,
    include_os: bool = True,
    extra_roots: Iterable[str | Path] | None = None,
    system_name: str | None = None,
) -> list[str]:
    """Construit les racines de decouverte adaptees a l'OS cible."""

    roots: list[str] = []
    if include_project:
        roots.extend(str(root) for root in DEFAULT_ROOTS)

    detected_system = (system_name or platform.system()).lower()
    if include_os:
        if detected_system == "windows":
            roots.extend(WINDOWS_DISCOVERY_ROOTS)
            roots.extend(_windows_application_roots())
        elif detected_system == "linux":
            roots.extend(LINUX_DISCOVERY_ROOTS)

    for env_name in COMMON_ENV_ROOTS:
        env_value = os.getenv(env_name, "")
        if env_value:
            roots.extend(_split_env_roots(env_value))

    if extra_roots:
        roots.extend(str(root) for root in extra_roots)

    seen: set[str] = set()
    unique: list[str] = []
    for root in roots:
        normalized = str(root).strip()
        key = normalized.lower()
        if normalized and key not in seen:
            seen.add(key)
            unique.append(normalized)
    return unique


def _iter_files(roots: Iterable[str | Path]) -> Iterable[Path]:
    for root_value in roots:
        root = _project_path(root_value)
        if root.is_file():
            yield root
            continue
        if not root.is_dir():
            continue
        try:
            iterator = root.rglob("*")
            for path in iterator:
                try:
                    if path.is_file() and not path.name.startswith("."):
                        yield path
                except OSError:
                    continue
        except OSError:
            continue


def _iter_root_files(root_value: str | Path) -> list[Path]:
    root = _project_path(root_value)
    if root.is_file():
        return [root]
    if not root.is_dir():
        return []
    files: list[Path] = []
    try:
        for path in root.rglob("*"):
            try:
                if path.is_file() and not path.name.startswith("."):
                    files.append(path)
            except OSError:
                continue
    except OSError:
        return files
    return files


def _iter_files_parallel(roots: Iterable[str | Path], parallel_workers: int) -> list[Path]:
    root_values = list(roots)
    workers = min(max(1, int(parallel_workers)), max(1, len(root_values)))
    if workers == 1 or len(root_values) <= 1:
        return list(_iter_files(root_values))

    files_by_index: dict[int, list[Path]] = {}
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="logminer-collector") as executor:
        futures = {
            executor.submit(_iter_root_files, root_value): index
            for index, root_value in enumerate(root_values)
        }
        for future in as_completed(futures):
            files_by_index[futures[future]] = future.result()

    files: list[Path] = []
    for index in sorted(files_by_index):
        files.extend(files_by_index[index])
    return files


def _priority(path: Path, kind: str) -> int:
    text = str(path).lower()
    score = 0
    if "windows_events_admin" in text or "windows_events" in text:
        score += 40
    if "programdata" in text or "program files" in text or "appdata" in text or "inetpub" in text:
        score += 20
    if any(token in text for token in ("\\logs\\", "/logs/", "\\logfiles\\", "/logfiles/", "\\log\\", "/log/")):
        score += 15
    if kind in {"win_event", "syslog", "cef_leef", "cloudtrail", "apache", "hdfs", "bgl"}:
        score += 25
    if path.suffix.lower() in {".csv", ".parquet"}:
        score += 35
    if "sample" in text or "examples" in text:
        score -= 10
    return score


def _candidate_from_path(path: Path, max_bytes: int) -> LogCandidate | None:
    suffix = path.suffix.lower()
    if suffix in SKIPPED_SUFFIXES or suffix not in SUPPORTED_SUFFIXES:
        return None
    try:
        stat = path.stat()
    except OSError:
        return None
    if stat.st_size <= 0 or stat.st_size > max_bytes:
        return None
    try:
        kind = "structured" if suffix in {".csv", ".parquet"} else detect_kind(str(path))
    except Exception:
        kind = "unknown"
    return LogCandidate(
        path=str(path),
        kind=kind,
        size_bytes=stat.st_size,
        modified=datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
        priority=_priority(path, kind),
    )


def discover_logs(
    roots: Iterable[str | Path] = DEFAULT_ROOTS,
    max_files: int = 200,
    max_bytes: int = 100 * 1024 * 1024,
    bus: MessageBus | None = None,
    parallel_workers: int = 1,
) -> list[LogCandidate]:
    """Decouvre les journaux candidats et les classe par pertinence."""

    candidates: list[LogCandidate] = []
    paths = _iter_files_parallel(roots, parallel_workers)
    workers = min(max(1, int(parallel_workers)), max(1, len(paths)))
    if workers > 1 and len(paths) > 1:
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="logminer-candidate") as executor:
            futures = [executor.submit(_candidate_from_path, path, max_bytes) for path in paths]
            for future in as_completed(futures):
                candidate = future.result()
                if candidate is not None:
                    candidates.append(candidate)
    else:
        for path in paths:
            candidate = _candidate_from_path(path, max_bytes)
            if candidate is not None:
                candidates.append(candidate)

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
    parser.add_argument("--deployment-roots", action="store_true", help="Ajoute les chemins de logs standards de l'OS courant")
    parser.add_argument("--no-project-roots", action="store_true", help="N'ajoute pas les dossiers de test du projet")
    parser.add_argument("--max-files", type=int, default=50, help="Nombre maximal de candidats retournes")
    parser.add_argument("--max-mb", type=int, default=100, help="Taille maximale par fichier")
    parser.add_argument("--bus", default="", help="Journal de messages JSONL")
    parser.add_argument("--run-id", default=None, help="Identifiant de run")
    parser.add_argument("--parallel-workers", type=int, default=1, help="Nombre de racines/fichiers scannes en parallele")
    args = parser.parse_args(argv)

    bus = LocalMessageBus(args.bus, run_id=args.run_id) if args.bus else None
    if args.deployment_roots:
        roots = deployment_roots(include_project=not args.no_project_roots, extra_roots=args.roots)
    else:
        roots = args.roots or list(DEFAULT_ROOTS)
    candidates = discover_logs(
        roots=roots,
        max_files=args.max_files,
        max_bytes=args.max_mb * 1024 * 1024,
        bus=bus,
        parallel_workers=args.parallel_workers,
    )
    for candidate in candidates:
        print(asdict(candidate))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
