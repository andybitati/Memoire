"""Orchestrateur local des agents Logminer.

Il fournit la premiere forme de communication entre agents:
parseur/normaliseur -> detecteur -> futurs correlateur/dashboard.
Chaque transition est publiee dans un bus JSONL local.
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
from agents.correlator import correlate_anomalies
from agents.detector import detect_anomalies
from agents.parser_agent import parse_logs


def run_local_pipeline(
    input_path: str | Path,
    out_dir: str | Path = "data/processed",
    parsed_name: str = "dataset.csv",
    anomalies_name: str = "anomalies.csv",
    incidents_name: str = "incidents.csv",
    sep: str = ";",
    contamination: float = 0.05,
    window_minutes: int = 15,
    bus_path: str | Path = "data/processed/agent_messages.jsonl",
    run_id: str | None = None,
    debug: bool = False,
    parser_parallel_workers: int = 1,
) -> dict[str, str]:
    """Execute parseur puis detecteur en partageant le meme bus."""

    bus = LocalMessageBus(bus_path, run_id=run_id)
    bus.publish(
        source="orchestrator",
        target="parser",
        message_type="workflow.started",
        payload={"input_path": str(input_path), "out_dir": str(out_dir)},
    )

    produced = parse_logs(
        input_path=input_path,
        out_dir=out_dir,
        out_name=parsed_name,
        sep=sep,
        bus=bus,
        debug=debug,
        parallel_workers=parser_parallel_workers,
    )
    if not produced:
        bus.publish(
            source="orchestrator",
            target="user",
            message_type="workflow.failed",
            payload={"reason": "no parsed csv produced"},
            status="error",
        )
        raise RuntimeError("Aucun CSV produit par l'agent parseur")

    parsed_csv = produced[0]
    anomalies_csv = str(Path(out_dir) / anomalies_name)
    incidents_csv = str(Path(out_dir) / incidents_name)
    detect_anomalies(
        input_csv=parsed_csv,
        output_csv=anomalies_csv,
        sep=sep,
        contamination=contamination,
        bus=bus,
    )
    correlate_anomalies(
        input_csv=anomalies_csv,
        output_csv=incidents_csv,
        sep=sep,
        window_minutes=window_minutes,
        bus=bus,
    )

    bus.publish(
        source="orchestrator",
        target="user",
        message_type="workflow.completed",
        payload={"parsed_csv": parsed_csv, "anomalies_csv": anomalies_csv, "incidents_csv": incidents_csv, "bus": str(bus.path)},
    )

    return {
        "run_id": bus.run_id,
        "bus": str(bus.path),
        "parsed_csv": parsed_csv,
        "anomalies_csv": anomalies_csv,
        "incidents_csv": incidents_csv,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Orchestrateur local des agents Logminer")
    parser.add_argument("-i", "--input", required=True, help="Fichier ou dossier de logs bruts")
    parser.add_argument("--out-dir", default="data/processed", help="Dossier de sortie")
    parser.add_argument("--parsed-name", default="dataset.csv", help="Nom du CSV parse")
    parser.add_argument("--anomalies-name", default="anomalies.csv", help="Nom du CSV anomalies")
    parser.add_argument("--incidents-name", default="incidents.csv", help="Nom du CSV incidents")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--contamination", type=float, default=0.05, help="Proportion attendue d'anomalies")
    parser.add_argument("--window-minutes", type=int, default=15, help="Fenetre de correlation")
    parser.add_argument("--bus", default="data/processed/agent_messages.jsonl", help="Journal de messages JSONL")
    parser.add_argument("--run-id", default=None, help="Identifiant de run partage")
    parser.add_argument("--debug", action="store_true", help="Mode debug")
    parser.add_argument("--parser-parallel-workers", type=int, default=1, help="Nombre de fichiers parses en parallele")
    args = parser.parse_args(argv)

    result = run_local_pipeline(
        input_path=args.input,
        out_dir=args.out_dir,
        parsed_name=args.parsed_name,
        anomalies_name=args.anomalies_name,
        incidents_name=args.incidents_name,
        sep=args.sep,
        contamination=args.contamination,
        window_minutes=args.window_minutes,
        bus_path=args.bus,
        run_id=args.run_id,
        debug=args.debug,
        parser_parallel_workers=args.parser_parallel_workers,
    )

    print(f"Run ID: {result['run_id']}")
    print(f"Bus: {result['bus']}")
    print(f"CSV parse: {result['parsed_csv']}")
    print(f"CSV anomalies: {result['anomalies_csv']}")
    print(f"CSV incidents: {result['incidents_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
