"""Agent routeur de modeles.

Cet agent choisit le modele d'anomalie adapte au type de journal:

- reseau: tcpdump, pcap, UNSW, DDoS/archive, flux IP/ports/protocoles;
- systeme: Windows Event, syslog, HDFS/BGL et journaux applicatifs/systeme.

Il peut seulement afficher la route choisie, ou lancer detection + correlation
avec le modele selectionne.
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

from agents.correlator import correlate_anomalies
from agents.detector import detect_anomalies
from detectors.file_detector import detect_kind


NETWORK_MODEL_DEFAULT = "models/isolation_forest_network_colab.joblib"
SYSTEM_MODEL_DEFAULT = "models/isolation_forest_colab.joblib"

NETWORK_KINDS = {"pcap", "tcpdump_text", "cef_leef", "apache"}
SYSTEM_KINDS = {"win_event", "syslog", "hdfs", "bgl", "cloudtrail", "jsonl", "praudit_text", "praudit_xml"}

NETWORK_COLUMNS = {
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "proto",
    "service",
    "state",
    "dur",
    "spkts",
    "dpkts",
    "sbytes",
    "dbytes",
    "rate",
    "sload",
    "dload",
    "attack_cat",
}
SYSTEM_COLUMNS = {
    "event",
    "source",
    "host",
    "user",
    "severity",
    "component",
    "pid",
    "tid",
    "session",
}


def _infer_sep(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:8192]
    return max([";", ",", "\t"], key=sample.count)


def _read_sample(path: Path, sep: str, nrows: int) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path).head(nrows).astype(str)

    csv_sep = _infer_sep(path) if sep.lower() == "auto" else sep
    return pd.read_csv(path, sep=csv_sep, dtype=str, keep_default_na=False, nrows=nrows)


def _score_dataframe(df: pd.DataFrame) -> tuple[int, int, list[str]]:
    columns = {str(column).lstrip("\ufeff") for column in df.columns}
    lower_columns = {column.lower() for column in columns}
    reasons: list[str] = []

    network_score = len(lower_columns & NETWORK_COLUMNS) * 8
    system_score = len(lower_columns & SYSTEM_COLUMNS) * 8

    if lower_columns & NETWORK_COLUMNS:
        reasons.append("colonnes reseau: " + ",".join(sorted(lower_columns & NETWORK_COLUMNS)[:8]))
    if lower_columns & SYSTEM_COLUMNS:
        reasons.append("colonnes systeme: " + ",".join(sorted(lower_columns & SYSTEM_COLUMNS)[:8]))

    if "dataset" in lower_columns:
        dataset_values = " ".join(df.get("dataset", pd.Series(dtype=str)).astype(str).str.lower().head(200).tolist())
        if any(token in dataset_values for token in ("pcap", "tcpdump", "unsw", "ddos", "drdos")):
            network_score += 35
            reasons.append("dataset oriente reseau")
        if any(token in dataset_values for token in ("windows", "hdfs", "bgl", "syslog")):
            system_score += 25
            reasons.append("dataset oriente systeme")

    text = " ".join(
        df[column].astype(str).str.lower().head(100).str.cat(sep=" ")
        for column in df.columns[: min(len(df.columns), 12)]
    )
    if any(token in text for token in ("microsoft-windows", "eventid", "security-auditing")):
        system_score += 30
        reasons.append("contenu Windows Event")
    if any(token in text for token in ("tcp", "udp", "icmp", "drdos", "attack_cat")):
        network_score += 20
        reasons.append("contenu/protocole reseau")

    return network_score, system_score, reasons


def route_model(
    input_path: str | Path,
    *,
    sep: str = "auto",
    sample_rows: int = 1000,
    system_model: str | Path = SYSTEM_MODEL_DEFAULT,
    network_model: str | Path = NETWORK_MODEL_DEFAULT,
) -> dict[str, object]:
    """Retourne la famille de logs et le modele a utiliser."""

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Chemin introuvable: {path}")

    if path.is_file() and path.suffix.lower() in {".csv", ".parquet"}:
        df = _read_sample(path, sep=sep, nrows=sample_rows)
        network_score, system_score, reasons = _score_dataframe(df)
        kind = path.suffix.lower().lstrip(".")
    else:
        kind = detect_kind(str(path)) if path.is_file() else "directory"
        network_score = 50 if kind in NETWORK_KINDS else 0
        system_score = 50 if kind in SYSTEM_KINDS else 0
        reasons = [f"type detecte: {kind}"]

    family = "network" if network_score > system_score else "system"
    confidence = abs(network_score - system_score)
    model = network_model if family == "network" else system_model

    return {
        "family": family,
        "model": str(model),
        "kind": kind,
        "network_score": network_score,
        "system_score": system_score,
        "confidence": confidence,
        "reasons": reasons,
    }


def _default_output(input_path: Path, suffix: str) -> Path:
    stem = input_path.stem or "dataset"
    return Path("data/processed") / f"{stem}_{suffix}.csv"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent routeur systeme/reseau pour choisir le bon modele")
    parser.add_argument("-i", "--input", required=True, help="CSV/Parquet normalise ou fichier brut a classifier")
    parser.add_argument("--sep", default="auto", help="Separateur CSV ou auto")
    parser.add_argument("--sample-rows", type=int, default=1000, help="Nombre de lignes echantillonnees")
    parser.add_argument("--system-model", default=SYSTEM_MODEL_DEFAULT, help="Modele systeme/Windows")
    parser.add_argument("--network-model", default=NETWORK_MODEL_DEFAULT, help="Modele reseau")
    parser.add_argument("--detect", action="store_true", help="Lance detection + correlation avec le modele choisi")
    parser.add_argument("-o", "--output", default="", help="CSV anomalies si --detect")
    parser.add_argument("--incidents-output", default="", help="CSV incidents si --detect")
    parser.add_argument("--window-minutes", type=int, default=15, help="Fenetre de correlation")
    args = parser.parse_args(argv)

    route = route_model(
        args.input,
        sep=args.sep,
        sample_rows=args.sample_rows,
        system_model=args.system_model,
        network_model=args.network_model,
    )

    print(f"Famille detectee: {route['family']}")
    print(f"Type/source: {route['kind']}")
    print(f"Modele choisi: {route['model']}")
    print(f"Scores: network={route['network_score']} system={route['system_score']} confidence={route['confidence']}")
    if route["reasons"]:
        print("Raisons: " + " | ".join(str(reason) for reason in route["reasons"]))

    if not args.detect:
        return 0

    model_path = Path(str(route["model"]))
    if not model_path.exists():
        raise FileNotFoundError(f"Modele choisi introuvable: {model_path}")

    input_path = Path(args.input)
    anomalies_output = Path(args.output) if args.output else _default_output(input_path, f"{route['family']}_anomalies")
    incidents_output = (
        Path(args.incidents_output)
        if args.incidents_output
        else _default_output(input_path, f"{route['family']}_incidents")
    )

    detect_anomalies(args.input, anomalies_output, sep=";" if args.sep == "auto" else args.sep, model_in=model_path)
    correlate_anomalies(anomalies_output, incidents_output, window_minutes=args.window_minutes)

    print(f"CSV anomalies: {anomalies_output}")
    print(f"CSV incidents: {incidents_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
