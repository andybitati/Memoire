"""Traite les journaux Windows recents depuis C:\\Windows\\System32\\winevt\\Logs.

Usage:
    python scripts/process_recent_windows_events.py
    python scripts/process_recent_windows_events.py --days 2

Le script filtre les fichiers `.evtx` par date de modification du fichier
(`LastWriteTime`) et produit:

- `data/processed/windows_recent_events.csv`
- `data/processed/windows_recent_manifest.csv`
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = Path(r"C:\Windows\System32\winevt\Logs")
LOGMINER_DIR = ROOT / "src" / "logminer"
OUTPUT_DIR = ROOT / "data" / "processed"


def configure_imports() -> None:
    """Rend les modules Logminer importables depuis ce script."""

    sys.path.insert(0, str(LOGMINER_DIR))
    sys.path.insert(0, str(LOGMINER_DIR / "io"))


def recent_evtx_files(days: int) -> list[Path]:
    """Retourne les fichiers EVTX modifies dans les `days` derniers jours."""

    cutoff = datetime.now() - timedelta(days=days)
    files = []

    for path in LOG_DIR.glob("*.evtx"):
        try:
            modified = datetime.fromtimestamp(path.stat().st_mtime)
        except OSError:
            continue
        if modified >= cutoff:
            files.append(path)

    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)


def write_manifest(files: list[Path], manifest_path: Path) -> None:
    """Ecrit la liste des fichiers utilises pour la verification."""

    with manifest_path.open("w", newline="", encoding="utf-8-sig") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["path", "size_bytes", "last_write_time"])
        writer.writeheader()
        for path in files:
            stat = path.stat()
            writer.writerow(
                {
                    "path": str(path),
                    "size_bytes": stat.st_size,
                    "last_write_time": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                }
            )


def main() -> int:
    parser = argparse.ArgumentParser(description="Traite les fichiers EVTX Windows recents.")
    parser.add_argument("--days", type=int, default=2, help="Nombre de jours a remonter")
    parser.add_argument("--limit", type=int, default=0, help="Limiter le nombre de fichiers traites (0 = aucun limite)")
    args = parser.parse_args()

    configure_imports()

    from csv_writer import open_writer
    from parsers.windows_event import Parser

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    files = recent_evtx_files(args.days)
    if args.limit > 0:
        files = files[: args.limit]

    manifest_path = OUTPUT_DIR / "windows_recent_manifest.csv"
    output_path = OUTPUT_DIR / "windows_recent_events.csv"
    write_manifest(files, manifest_path)

    f_out, writer, csv_path = open_writer(str(output_path), part=0, sep=";")
    parser_instance = Parser()
    ok = 0
    failed = 0

    try:
        for path in files:
            try:
                parser_instance.parse(
                    path=str(path),
                    writer=writer,
                    sep=";",
                    split_rows=0,
                    progress_every=0,
                    use_tqdm=False,
                    debug=False,
                )
                ok += 1
                print(f"OK {path}")
            except Exception as exc:
                failed += 1
                print(f"FAIL {path}: {exc}", file=sys.stderr)
    finally:
        f_out.close()

    print(f"Fichiers selectionnes: {len(files)}")
    print(f"Fichiers traites: {ok}")
    print(f"Fichiers en echec: {failed}")
    print(f"Manifest: {manifest_path}")
    print(f"CSV: {csv_path}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
