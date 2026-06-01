"""Agent d'autorisation privilegiee.

Cet agent demande a l'administrateur d'autoriser une collecte sensible via les
mecanismes natifs du systeme. Il ne lit pas, ne stocke pas et ne transmet pas de
mot de passe administrateur.
"""

from __future__ import annotations

import argparse
import platform
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional


REPO_ROOT = Path(__file__).resolve().parents[3]
WINDOWS_COLLECT_SCRIPT = REPO_ROOT / "scripts" / "collect_windows_events.ps1"


@dataclass
class PrivilegedRequest:
    supported: bool
    launched: bool
    command: str
    message: str


def _quote_ps(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def request_windows_sensitive_collection(
    days: int = 2,
    copy_logs: Iterable[str] = ("Application", "System", "Security"),
    raw_directory: str = "data\\raw\\windows_events_admin",
    output_directory: str = "data\\processed",
) -> PrivilegedRequest:
    """Ouvre une invite UAC pour exporter les journaux Windows sensibles."""

    if platform.system().lower() != "windows":
        return PrivilegedRequest(False, False, "", "Elevation interactive disponible uniquement sur Windows")

    if not WINDOWS_COLLECT_SCRIPT.exists():
        return PrivilegedRequest(False, False, "", f"Script introuvable: {WINDOWS_COLLECT_SCRIPT}")

    logs = ",".join(copy_logs)
    argument_list = " ".join(
        [
            "-NoProfile",
            "-ExecutionPolicy Bypass",
            "-File",
            _quote_ps(str(WINDOWS_COLLECT_SCRIPT)),
            "-Days",
            str(max(1, days)),
            "-RawDirectory",
            _quote_ps(raw_directory),
            "-OutputDirectory",
            _quote_ps(output_directory),
            "-CopyLogs",
            _quote_ps(logs),
        ]
    )

    command = (
        "Start-Process -FilePath powershell "
        f"-ArgumentList {_quote_ps(argument_list)} "
        f"-WorkingDirectory {_quote_ps(str(REPO_ROOT))} "
        "-Verb RunAs"
    )

    result = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=20,
        check=False,
    )

    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return PrivilegedRequest(True, False, command, detail[:500] or "Demande d'elevation refusee ou impossible")

    return PrivilegedRequest(
        True,
        True,
        command,
        "Invite administrateur lancee. L'administrateur doit valider la fenetre UAC.",
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent d'autorisation privilegiee Logminer")
    parser.add_argument("--days", type=int, default=2, help="Fenetre de collecte Windows")
    parser.add_argument("--copy-log", action="append", dest="copy_logs", default=[], help="Journal Windows a exporter")
    args = parser.parse_args(argv)

    result = request_windows_sensitive_collection(days=args.days, copy_logs=args.copy_logs or ["Application", "System", "Security"])
    print(asdict(result))
    return 0 if result.launched else 1


if __name__ == "__main__":
    raise SystemExit(main())
