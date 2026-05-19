"""Construit un CSV d'entrainement cloud depuis plusieurs datasets traites.

Le dossier `cloud_upload/logminer_cloud_data/train` contient plusieurs CSV deja
normalises ou structures. `detector.py` attend un seul CSV en entree; ce script
fusionne donc les fichiers utiles en conservant l'union des colonnes.

Exemple Colab:
    python scripts/build_cloud_training_dataset.py \
      --input-dir /content/drive/MyDrive/logminer_cloud_data/train \
      --output data/processed/cloud_training_dataset.csv \
      --max-rows-per-file 50000
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


def _csv_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.glob("*.csv") if path.is_file())


def collect_columns(files: list[Path], sep: str) -> list[str]:
    """Collecte l'union stable des colonnes sans charger les datasets entiers."""

    columns: list[str] = []
    seen: set[str] = set()
    for path in files:
        header = pd.read_csv(path, sep=sep, nrows=0).columns
        for column in header:
            cleaned = str(column).lstrip("\ufeff")
            if cleaned not in seen:
                seen.add(cleaned)
                columns.append(cleaned)

    if "dataset" not in seen:
        columns.insert(0, "dataset")
    return columns


def append_file(
    path: Path,
    output: Path,
    columns: list[str],
    sep: str,
    chunksize: int,
    max_rows_per_file: int,
    write_header: bool,
) -> tuple[bool, int]:
    """Ajoute un fichier au CSV final en limitant optionnellement le volume."""

    written = 0
    for chunk in pd.read_csv(path, sep=sep, dtype=str, keep_default_na=False, chunksize=chunksize):
        chunk.columns = [str(column).lstrip("\ufeff") for column in chunk.columns]
        if "dataset" not in chunk.columns:
            chunk.insert(0, "dataset", path.stem)

        if max_rows_per_file > 0:
            remaining = max_rows_per_file - written
            if remaining <= 0:
                break
            chunk = chunk.head(remaining)

        chunk = chunk.reindex(columns=columns, fill_value="")
        chunk.to_csv(output, sep=sep, index=False, encoding="utf-8-sig", mode="a", header=write_header)
        write_header = False
        written += len(chunk)

        if max_rows_per_file > 0 and written >= max_rows_per_file:
            break

    return write_header, written


def build_dataset(
    input_dir: Path,
    output: Path,
    sep: str = ";",
    chunksize: int = 100000,
    max_rows_per_file: int = 0,
) -> Path:
    files = _csv_files(input_dir)
    if not files:
        raise ValueError(f"Aucun CSV trouve dans {input_dir}")

    columns = collect_columns(files, sep)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    write_header = True
    total = 0
    for path in files:
        write_header, written = append_file(path, output, columns, sep, chunksize, max_rows_per_file, write_header)
        total += written
        print(f"{path.name}: {written} lignes ajoutees")

    print(f"CSV entrainement cloud: {output}")
    print(f"Lignes totales: {total}")
    print(f"Colonnes: {len(columns)}")
    return output


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fusionne plusieurs CSV traites pour entrainement cloud")
    parser.add_argument("--input-dir", required=True, type=Path, help="Dossier contenant les CSV train")
    parser.add_argument("--output", required=True, type=Path, help="CSV fusionne a produire")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--chunksize", type=int, default=100000, help="Lignes lues par bloc")
    parser.add_argument(
        "--max-rows-per-file",
        type=int,
        default=0,
        help="0 = toutes les lignes; sinon limite par fichier pour un entrainement plus leger",
    )
    args = parser.parse_args(argv)

    build_dataset(args.input_dir, args.output, args.sep, args.chunksize, args.max_rows_per_file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
