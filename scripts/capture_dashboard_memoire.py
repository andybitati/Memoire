"""Capture Ariel Logminer dashboard views for the memoire.

Run the dashboard first, for example:
    npm --prefix web/dashboard run dev
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS_CAPTURE_DIR = ROOT / "docs" / "memoire" / "captures"
LATEX_CAPTURE_DIR = ROOT / "memoire_logminer_latex_overleaf" / "captures"
PACK_CAPTURE_DIR = ROOT / "docs" / "memoire" / "pack_redaction_final" / "05_captures_dashboard"
PACK_LATEX_CAPTURE_DIR = ROOT / "docs" / "memoire" / "pack_redaction_final" / "10_latex_overleaf" / "captures"


CAPTURES = [
    ("dashboard_vue_ensemble.png", "http://127.0.0.1:5173/?view=overview", "1600,1100"),
    ("dashboard_resultats_detail_incident.png", "http://127.0.0.1:5173/?view=results", "1600,1200"),
    ("dashboard_ressources_audit.png", "http://127.0.0.1:5173/?view=technical", "1600,1300"),
    ("dashboard_longue_vue.png", "http://127.0.0.1:5173/?view=overview", "1600,1800"),
]


def find_browser() -> Path | None:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\EdgeCore\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def capture(browser: Path, filename: str, url: str, window_size: str) -> Path:
    DOCS_CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DOCS_CAPTURE_DIR / filename
    user_data_dir = ROOT / "data" / "processed" / "_edge_dashboard_capture"
    user_data_dir.mkdir(parents=True, exist_ok=True)
    command = [
        str(browser),
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--disable-crash-reporter",
        "--disable-features=RendererCodeIntegrity",
        f"--user-data-dir={user_data_dir.resolve()}",
        f"--window-size={window_size}",
        "--virtual-time-budget=7000",
        f"--screenshot={output_path.resolve()}",
        url,
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=35)
    if not output_path.exists() or output_path.stat().st_size < 50_000:
        raise RuntimeError(f"Capture suspecte ou vide: {output_path}")
    return output_path


def mirror_capture(path: Path) -> None:
    for target_dir in [LATEX_CAPTURE_DIR, PACK_CAPTURE_DIR, PACK_LATEX_CAPTURE_DIR]:
        if target_dir.exists():
            target = target_dir / path.name
            shutil.copyfile(path, target)


def main() -> int:
    browser = find_browser()
    if browser is None:
        print("Chrome/Edge introuvable; impossible de produire les captures PNG.", file=sys.stderr)
        return 1

    outputs = []
    for filename, url, window_size in CAPTURES:
        output = capture(browser, filename, url, window_size)
        mirror_capture(output)
        outputs.append(output)

    shutil.rmtree(ROOT / "data" / "processed" / "_edge_dashboard_capture", ignore_errors=True)
    for output in outputs:
        print(f"{output}: {output.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
