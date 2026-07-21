"""Agent de fenetrage glissant pour HDFS/BGL.

Il enrichit un CSV Logminer avec des colonnes `seq_*` afin de tester une
remediation concrete au modele ligne par ligne sur journaux sequentiels.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from features.event_features import load_events
from features.sequence_windows import add_sequence_window_features


def enrich_sequence_windows(
    input_csv: str | Path,
    output_csv: str | Path,
    *,
    sep: str = ";",
    family: str = "auto",
    window_minutes: int = 30,
    template_method: str = "drain3",
    drain_similarity: float = 0.5,
    allow_template_fallback: bool = True,
) -> str:
    """Lit un CSV normalise, ajoute les features sequentielles et l'ecrit."""

    events = load_events(input_csv, sep=sep)
    if events.empty:
        raise ValueError(f"Aucun evenement a enrichir dans {input_csv}")

    enriched = add_sequence_window_features(
        events,
        family=family,
        window_minutes=window_minutes,
        template_method=template_method,
        drain_similarity=drain_similarity,
        allow_template_fallback=allow_template_fallback,
    )

    output_path = Path(output_csv)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_csv(output_path, sep=sep, index=False, encoding="utf-8-sig")
    return str(output_path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent de fenetrage glissant HDFS/BGL")
    parser.add_argument("-i", "--input", required=True, help="CSV normalise Logminer")
    parser.add_argument("-o", "--output", required=True, help="CSV enrichi avec colonnes seq_*")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--family", default="auto", choices=["auto", "hdfs", "bgl", "sequence"], help="Famille de logs")
    parser.add_argument("--window-minutes", type=int, default=30, help="Taille de la fenetre glissante")
    parser.add_argument(
        "--template-method",
        default="drain3",
        choices=["drain3", "drain_like", "simple"],
        help="Templateur utilise",
    )
    parser.add_argument("--drain-similarity", type=float, default=0.5, help="Seuil de similarite Drain-like")
    parser.add_argument(
        "--strict-template-library",
        action="store_true",
        help="Echoue si --template-method drain3 est demande mais que drain3 n'est pas installe",
    )
    args = parser.parse_args(argv)

    output = enrich_sequence_windows(
        args.input,
        args.output,
        sep=args.sep,
        family=args.family,
        window_minutes=args.window_minutes,
        template_method=args.template_method,
        drain_similarity=args.drain_similarity,
        allow_template_fallback=not args.strict_template_library,
    )

    enriched = pd.read_csv(output, sep=args.sep, dtype=str, keep_default_na=False, nrows=5)
    seq_columns = [column for column in enriched.columns if str(column).startswith("seq_")]
    print(f"CSV enrichi: {output}")
    print(f"Colonnes sequentielles ajoutees: {len(seq_columns)}")
    if seq_columns:
        print("Apercu colonnes: " + ", ".join(seq_columns[:12]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
