"""Resume les fichiers de validation produits par model_compare.py.

Le script aide a exploiter les resultats dans le memoire: il rassemble les CSV
de metriques, trie les modeles par F1-score et produit une synthese compacte.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


def summarize_file(path: Path) -> pd.DataFrame:
    data = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False)
    dataset = path.stem.replace("validation_", "").replace("_metrics", "")
    data.insert(0, "dataset", dataset)

    for column in [
        "precision",
        "recall",
        "f1",
        "accuracy",
        "specificity",
        "duration_sec",
        "memory_peak_mb",
        "adaptability_score",
        "selection_score",
    ]:
        if column in data.columns:
            data[column] = pd.to_numeric(data[column], errors="coerce").fillna(0)

    return data


def summarize(paths: Iterable[Path], output: Path, top_n: int, sort_by: str) -> Path:
    frames = [summarize_file(path) for path in paths]
    if not frames:
        raise ValueError("Aucun fichier de metriques fourni")

    data = pd.concat(frames, ignore_index=True)
    if sort_by not in data.columns:
        raise ValueError(f"Colonne de tri absente: {sort_by}")

    ranked = (
        data.sort_values(["dataset", sort_by, "f1", "precision", "recall"], ascending=[True, False, False, False, False])
        .groupby("dataset", as_index=False)
        .head(top_n)
    )

    columns = [
        "dataset",
        "model",
        "events",
        "anomalies",
        "precision",
        "recall",
        "f1",
        "accuracy",
        "specificity",
        "duration_sec",
        "memory_peak_mb",
        "adaptability_score",
        "selection_score",
        "tp",
        "fp",
        "fn",
        "tn",
        "notes",
    ]
    existing_columns = [column for column in columns if column in ranked.columns]
    output.parent.mkdir(parents=True, exist_ok=True)
    ranked[existing_columns].to_csv(output, sep=";", index=False, encoding="utf-8-sig")
    return output


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synthese des validations precision/rappel/F1")
    parser.add_argument("inputs", nargs="+", type=Path, help="CSV de metriques model_compare.py")
    parser.add_argument("-o", "--output", type=Path, default=Path("data/processed/validation_summary.csv"))
    parser.add_argument("--top-n", type=int, default=3, help="Nombre de modeles a garder par dataset")
    parser.add_argument("--sort-by", default="f1", help="Colonne de tri: f1 ou selection_score")
    args = parser.parse_args(argv)

    output = summarize(args.inputs, args.output, args.top_n, args.sort_by)
    print(f"Synthese validation: {output}")
    print(pd.read_csv(output, sep=";").to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
