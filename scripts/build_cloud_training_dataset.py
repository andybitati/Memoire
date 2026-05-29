"""Construit un CSV d'entrainement cloud depuis plusieurs datasets traites.

Le dossier `cloud_upload/logminer_cloud_data/train` contient plusieurs CSV deja
normalises ou structures. `detector.py` attend un seul CSV en entree; ce script
fusionne donc les fichiers utiles en conservant l'union des colonnes.

Exemple Colab:
    python scripts/build_cloud_training_dataset.py \
      --input-dir /content/drive/MyDrive/logminer_cloud_data/train \
      --output data/processed/cloud_training_dataset.csv \
      --max-rows-per-file 50000

Role dans le projet:
    Le detecteur IA attend un seul CSV. Or les experiences reseau combinent
    plusieurs sources: UNSWNB15, tcpdump converti, Parquet UNSW, petits CSV
    systeme/reseau. Ce script fabrique donc un dataset commun en gardant l'union
    des colonnes et en limitant optionnellement le nombre de lignes par fichier.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from typing import Iterable

import pandas as pd

SUPPORTED_EXTENSIONS = {".csv", ".parquet"}


def _data_files(input_dir: Path, recursive: bool = False) -> list[Path]:
    """Liste les fichiers d'entree supportes.

    `recursive=True` est utile apres extraction d'archives ZIP dans Colab, car
    certains datasets placent les CSV dans des sous-dossiers.
    """

    pattern = "**/*" if recursive else "*"
    return sorted(
        path
        for path in input_dir.glob(pattern)
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def _file_key(path: Path, mode: str) -> tuple[object, ...]:
    """Construit une cle de deduplication pour un fichier.

    Modes:
        - none: pas de deduplication logique, on garde le chemin;
        - name-size: rapide, suffisant quand les ZIP contiennent les memes noms;
        - hash: strict, mais couteux sur des fichiers de plusieurs Go.
    """

    if mode == "none":
        return (str(path.resolve()).lower(),)

    stat = path.stat()
    if mode == "name-size":
        return (path.name.lower(), stat.st_size)

    digest = hashlib.sha256()
    with path.open("rb") as f_in:
        # Lecture par blocs pour eviter de charger des fichiers geants en RAM.
        for chunk in iter(lambda: f_in.read(1024 * 1024), b""):
            digest.update(chunk)
    return (digest.hexdigest(),)


def _deduplicate_files(files: list[Path], mode: str) -> list[Path]:
    """Garde une seule copie des fichiers declares identiques."""

    if mode == "none":
        return files

    kept: list[Path] = []
    seen: dict[tuple[object, ...], Path] = {}
    for path in files:
        key = _file_key(path, mode)
        if key in seen:
            print(f"Doublon ignore ({mode}): {path} == {seen[key]}")
            continue
        seen[key] = path
        kept.append(path)
    return kept


def _infer_csv_sep(path: Path, sep: str) -> str:
    """Detecte le separateur CSV a partir d'un petit extrait."""

    if sep.lower() != "auto":
        return sep

    # On se limite a l'en-tete. Les messages de logs contiennent souvent des
    # virgules, ce qui peut faire croire a tort qu'un CSV `;` est separe par `,`.
    with path.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f_in:
        sample = f_in.readline()
    candidates = [";", ",", "\t"]
    return max(candidates, key=sample.count)


def _read_header(path: Path, sep: str) -> list[str]:
    """Lit l'en-tete sans parcourir tout le fichier.

    Sur les gros CSV reseau, `pandas.read_csv(..., nrows=0)` peut encore etre
    lent. Lire seulement la premiere ligne est plus previsible localement et en
    Colab.
    """

    if path.suffix.lower() == ".parquet":
        return [str(column).lstrip("\ufeff") for column in pd.read_parquet(path).head(0).columns]

    file_sep = _infer_csv_sep(path, sep)
    with path.open("r", encoding="utf-8-sig", errors="ignore", newline="") as f_in:
        first_line = f_in.readline()
    return [str(column).lstrip("\ufeff") for column in next(csv.reader([first_line], delimiter=file_sep), [])]


def collect_columns(files: list[Path], sep: str) -> list[str]:
    """Collecte l'union stable des colonnes sans charger les datasets entiers."""

    columns: list[str] = []
    seen: set[str] = set()
    for path in files:
        for column in _read_header(path, sep):
            if column not in seen:
                seen.add(column)
                columns.append(column)

    if "dataset" not in seen:
        # La colonne dataset permet de garder la provenance de chaque ligne,
        # meme quand le CSV original ne l'avait pas.
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
    # Meme quand `--sep auto` sert a lire des fichiers differents, le CSV final
    # reste en `;`, convention retenue dans Logminer et pratique avec Excel FR.
    output_sep = ";" if sep.lower() == "auto" else sep

    if path.suffix.lower() == ".parquet":
        # Les Parquet UNSW sont relativement petits dans ce projet; on les lit
        # directement puis on tronque si `max_rows_per_file` est defini.
        chunks = [pd.read_parquet(path).astype(str)]
    else:
        file_sep = _infer_csv_sep(path, sep)
        if max_rows_per_file > 0:
            # Pour les tests et entrainements echantillonnes, lire directement
            # N lignes evite d'ouvrir de gros iterateurs pandas sur des CSV de Go.
            chunks = [pd.read_csv(path, sep=file_sep, dtype=str, keep_default_na=False, nrows=max_rows_per_file)]
        else:
            # En mode complet, lecture par chunks pour reduire la pression RAM.
            chunks = pd.read_csv(path, sep=file_sep, dtype=str, keep_default_na=False, chunksize=chunksize)

    for chunk in chunks:
        chunk.columns = [str(column).lstrip("\ufeff") for column in chunk.columns]
        if "dataset" not in chunk.columns:
            # Si la source ne donne pas son nom, on utilise le nom du fichier.
            # Cela aide ensuite le routeur et l'analyse des resultats.
            chunk.insert(0, "dataset", path.stem)

        if max_rows_per_file > 0:
            remaining = max_rows_per_file - written
            if remaining <= 0:
                break
            chunk = chunk.head(remaining)

        # Chaque source est realignee sur l'union des colonnes. Les champs
        # absents deviennent vides, ce qui permet de melanger UNSW et tcpdump.
        chunk = chunk.reindex(columns=columns, fill_value="")
        chunk.to_csv(output, sep=output_sep, index=False, encoding="utf-8-sig", mode="a", header=write_header)
        write_header = False
        written += len(chunk)

        if max_rows_per_file > 0 and written >= max_rows_per_file:
            break

    return write_header, written


def build_dataset(
    input_dir: Path | list[Path] | None,
    output: Path,
    sep: str = ";",
    chunksize: int = 100000,
    max_rows_per_file: int = 0,
    recursive: bool = False,
    input_files: list[Path] | None = None,
    dedupe: str = "name-size",
) -> Path:
    """Construit le CSV final a partir de dossiers et fichiers explicites."""

    files: list[Path] = []
    input_dirs: list[Path] = []
    if isinstance(input_dir, list):
        input_dirs = input_dir
    elif input_dir is not None:
        input_dirs = [input_dir]

    for directory in input_dirs:
        files.extend(_data_files(directory, recursive=recursive))
    for path in input_files or []:
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            files.append(path)

    # `dict.fromkeys` retire les chemins strictement identiques tout en gardant
    # l'ordre trie. La deduplication suivante retire les doublons de contenu.
    files = sorted(dict.fromkeys(files))
    files = _deduplicate_files(files, dedupe)
    if not files:
        raise ValueError("Aucun fichier CSV/Parquet trouve")

    # La premiere passe collecte le schema global; la seconde ecrit les donnees.
    columns = collect_columns(files, sep)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    write_header = True
    total = 0
    for path in files:
        # Un message par source donne une trace claire dans Colab.
        write_header, written = append_file(path, output, columns, sep, chunksize, max_rows_per_file, write_header)
        total += written
        print(f"{path.name}: {written} lignes ajoutees")

    print(f"CSV entrainement cloud: {output}")
    print(f"Lignes totales: {total}")
    print(f"Colonnes: {len(columns)}")
    return output


def main(argv: Iterable[str] | None = None) -> int:
    """Point d'entree CLI utilise localement et dans les notebooks Colab."""

    parser = argparse.ArgumentParser(description="Fusionne plusieurs CSV traites pour entrainement cloud")
    parser.add_argument("--input-dir", action="append", default=[], type=Path, help="Dossier contenant les CSV/Parquet train")
    parser.add_argument("--input-file", action="append", default=[], type=Path, help="Fichier CSV/Parquet a ajouter")
    parser.add_argument("--output", required=True, type=Path, help="CSV fusionne a produire")
    parser.add_argument("--sep", default=";", help="Separateur CSV, ou 'auto' pour detecter ; , tab")
    parser.add_argument("--chunksize", type=int, default=100000, help="Lignes lues par bloc")
    parser.add_argument("--recursive", action="store_true", help="Cherche les fichiers dans les sous-dossiers")
    parser.add_argument(
        "--dedupe",
        choices=["name-size", "hash", "none"],
        default="name-size",
        help="Ignore les doublons. name-size est rapide; hash est plus strict mais lit les fichiers entiers.",
    )
    parser.add_argument(
        "--max-rows-per-file",
        type=int,
        default=0,
        help="0 = toutes les lignes; sinon limite par fichier pour un entrainement plus leger",
    )
    args = parser.parse_args(argv)

    if not args.input_dir and not args.input_file:
        # On force au moins une source pour eviter de creer un CSV vide par
        # erreur de chemin dans Colab.
        parser.error("--input-dir ou au moins un --input-file est requis")

    build_dataset(
        args.input_dir,
        args.output,
        args.sep,
        args.chunksize,
        args.max_rows_per_file,
        recursive=args.recursive,
        input_files=args.input_file,
        dedupe=args.dedupe,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
