"""Agent runtime Logminer.

Cet agent prepare les services locaux necessaires au fonctionnement distribue
du prototype. Il verifie Docker, tente de demarrer Docker Desktop lorsque c'est
possible, puis lance les services declares par Docker Compose.
"""

from __future__ import annotations

import argparse
import platform
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_COMPOSE_FILE = REPO_ROOT / "docker-compose.redis.yml"
DOCKER_DESKTOP = Path(r"C:\Program Files\Docker\Docker\Docker Desktop.exe")


@dataclass
class RuntimeStatus:
    docker_cli: bool
    docker_engine: bool
    compose_file: str
    services_started: bool
    message: str


def _run(command: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def docker_cli_available() -> bool:
    return shutil.which("docker") is not None


def docker_engine_available() -> bool:
    if not docker_cli_available():
        return False
    result = _run(["docker", "version"], timeout=15)
    return result.returncode == 0


def start_docker_desktop(wait_seconds: int = 45) -> bool:
    """Tente de lancer Docker Desktop sur Windows, puis attend le moteur."""

    if platform.system().lower() != "windows" or not DOCKER_DESKTOP.exists():
        return False

    subprocess.Popen(
        [str(DOCKER_DESKTOP)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    deadline = time.time() + max(1, wait_seconds)
    while time.time() < deadline:
        if docker_engine_available():
            return True
        time.sleep(3)
    return docker_engine_available()


def ensure_runtime(
    compose_file: str | Path = DEFAULT_COMPOSE_FILE,
    start_desktop: bool = True,
    wait_seconds: int = 45,
) -> RuntimeStatus:
    """Prepare Docker et lance les services Logminer si possible."""

    compose_path = Path(compose_file)
    if not compose_path.is_absolute():
        compose_path = REPO_ROOT / compose_path

    if not docker_cli_available():
        return RuntimeStatus(False, False, str(compose_path), False, "Docker CLI introuvable")

    engine_ready = docker_engine_available()
    if not engine_ready and start_desktop:
        engine_ready = start_docker_desktop(wait_seconds=wait_seconds)

    if not engine_ready:
        return RuntimeStatus(True, False, str(compose_path), False, "Moteur Docker indisponible")

    if not compose_path.exists():
        return RuntimeStatus(True, True, str(compose_path), False, "Fichier Docker Compose introuvable")

    result = _run(["docker", "compose", "-f", str(compose_path), "up", "-d"], timeout=120)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        return RuntimeStatus(True, True, str(compose_path), False, detail[:500] or "docker compose a echoue")

    return RuntimeStatus(True, True, str(compose_path), True, "Services Logminer demarres")


def runtime_status(compose_file: str | Path = DEFAULT_COMPOSE_FILE) -> RuntimeStatus:
    compose_path = Path(compose_file)
    if not compose_path.is_absolute():
        compose_path = REPO_ROOT / compose_path
    return RuntimeStatus(
        docker_cli=docker_cli_available(),
        docker_engine=docker_engine_available(),
        compose_file=str(compose_path),
        services_started=False,
        message="Etat runtime lu sans action",
    )


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent runtime Logminer")
    parser.add_argument("--compose-file", default=str(DEFAULT_COMPOSE_FILE), help="Fichier Docker Compose a lancer")
    parser.add_argument("--status-only", action="store_true", help="Ne lance aucun service")
    parser.add_argument("--no-start-desktop", action="store_true", help="Ne tente pas de lancer Docker Desktop")
    args = parser.parse_args(argv)

    status = (
        runtime_status(args.compose_file)
        if args.status_only
        else ensure_runtime(args.compose_file, start_desktop=not args.no_start_desktop)
    )
    print(asdict(status))
    return 0 if status.docker_engine or args.status_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
