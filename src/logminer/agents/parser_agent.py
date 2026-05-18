"""Agent parseur/normaliseur.

Cet agent encapsule `pipeline.run_pipeline` et publie ses etats sur le bus
local. Il represente les agents 1-2 cote Python: detection de format, parsing
et normalisation CSV.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.bus import LocalMessageBus
from pipeline import run_pipeline


def parse_logs(
    input_path: str | Path,
    out_dir: str | Path = "data/processed",
    out_name: str = "dataset.csv",
    sep: str = ";",
    bus: LocalMessageBus | None = None,
    debug: bool = False,
) -> list[str]:
    """Parse un fichier/dossier et publie les messages de cycle de vie."""

    bus = bus or LocalMessageBus()
    input_path = str(input_path)
    out_dir = str(out_dir)

    bus.publish(
        source="parser",
        target="detector",
        message_type="parse.started",
        payload={"input_path": input_path, "out_dir": out_dir, "out_name": out_name},
    )

    produced = run_pipeline(
        input_path=input_path,
        out_dir=out_dir,
        out_name=out_name,
        sep=sep,
        debug=debug,
    )

    bus.publish(
        source="parser",
        target="detector",
        message_type="parse.completed",
        payload={"produced_csv": produced, "primary_csv": produced[0] if produced else ""},
    )
    return produced


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent parseur Logminer")
    parser.add_argument("-i", "--input", required=True, help="Fichier ou dossier de logs bruts")
    parser.add_argument("--out-dir", default="data/processed", help="Dossier de sortie")
    parser.add_argument("--name", default="dataset.csv", help="Nom du CSV produit")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--bus", default="data/processed/agent_messages.jsonl", help="Journal de messages JSONL")
    parser.add_argument("--run-id", default=None, help="Identifiant de run partage entre agents")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    args = parser.parse_args(argv)

    bus = LocalMessageBus(args.bus, run_id=args.run_id)
    produced = parse_logs(args.input, args.out_dir, args.name, args.sep, bus=bus, debug=args.debug)
    print("\n".join(produced))
    print(f"Bus: {bus.path}")
    print(f"Run ID: {bus.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
