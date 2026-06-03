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
GENERATED_DIR = REPO_ROOT / "scripts" / "generated"


@dataclass
class PrivilegedRequest:
    supported: bool
    launched: bool
    command: str
    message: str
    launcher_path: str = ""


def _quote_ps(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _quote_cmd(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def create_windows_admin_launcher(
    days: int,
    copy_logs: Iterable[str],
    raw_directory: str,
    output_directory: str,
) -> Path:
    """Cree un lanceur interactif a executer en administrateur."""

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    launcher_path = GENERATED_DIR / "run_windows_sensitive_collection_admin.cmd"
    logs = ",".join(copy_logs)
    ps_arguments = " ".join(
        [
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            _quote_cmd(str(WINDOWS_COLLECT_SCRIPT)),
            "-Days",
            str(max(1, days)),
            "-RawDirectory",
            _quote_cmd(raw_directory),
            "-OutputDirectory",
            _quote_cmd(output_directory),
            "-CopyLogs",
            _quote_cmd(logs),
        ]
    )
    launcher_path.write_text(
        "\r\n".join(
            [
                "@echo off",
                "title Logminer - Collecte Windows privilegiee",
                f"cd /d {_quote_cmd(str(REPO_ROOT))}",
                f"powershell.exe {ps_arguments}",
                "echo.",
                "echo Collecte terminee. Vous pouvez fermer cette fenetre.",
                "pause",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return launcher_path


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

    copy_logs = list(copy_logs)
    launcher_path = create_windows_admin_launcher(days, copy_logs, raw_directory, output_directory)
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
        message = detail[:500] or "Demande d'elevation refusee ou impossible"
        return PrivilegedRequest(
            True,
            False,
            command,
            f"{message}. Lanceur administrateur prepare: {launcher_path}",
            str(launcher_path),
        )

    return PrivilegedRequest(
        True,
        True,
        command,
        "Invite administrateur lancee. Si rien ne s'affiche, executer le lanceur en administrateur.",
        str(launcher_path),
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
