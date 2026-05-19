"""Cree un dataset de logs simules avec anomalies injectees.

Le script part d'un CSV normalise Logminer, copie les lignes, puis modifie un
pourcentage d'evenements pour simuler des erreurs ou attaques simples:
authentification echouee, acces refuse, malware, panne service, trafic suspect.

La sortie contient une colonne `label`:

- 0: evenement conserve comme normal;
- 1: anomalie injectee.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


ATTACK_MESSAGES = [
    "SIMULATED_ATTACK brute force authentication failure user=root source=10.10.10.10",
    "SIMULATED_ERROR service crash exception stacktrace generated for validation",
    "SIMULATED_MALWARE suspicious executable blocked by endpoint protection",
    "SIMULATED_DENIED repeated access denied on protected resource",
    "SIMULATED_NETWORK_SCAN multiple connection attempts detected from 192.0.2.55",
]


def inject_anomalies(
    input_csv: Path,
    output_csv: Path,
    sep: str = ";",
    anomaly_fraction: float = 0.05,
    max_rows: int = 10000,
    random_state: int = 42,
) -> Path:
    data = pd.read_csv(input_csv, sep=sep, dtype=str, keep_default_na=False)
    if max_rows > 0 and len(data) > max_rows:
        data = data.sample(max_rows, random_state=random_state).sort_index().reset_index(drop=True)

    if data.empty:
        raise ValueError(f"Aucune ligne dans {input_csv}")

    rng = np.random.default_rng(random_state)
    data = data.copy()
    data["label"] = 0
    anomaly_count = max(1, int(len(data) * min(max(anomaly_fraction, 0.001), 0.5)))
    anomaly_indices = rng.choice(data.index.to_numpy(), size=anomaly_count, replace=False)

    for position, index in enumerate(anomaly_indices):
        attack_message = ATTACK_MESSAGES[position % len(ATTACK_MESSAGES)]
        data.loc[index, "label"] = 1

        if "severity" in data.columns:
            data.loc[index, "severity"] = "CRITICAL" if position % 2 == 0 else "ERROR"
        if "category" in data.columns:
            data.loc[index, "category"] = "AUTHENTICATION" if "authentication" in attack_message else "SYSTEM_ERROR"
        if "subcategory" in data.columns:
            data.loc[index, "subcategory"] = "SIMULATED_INJECTION"
        if "event" in data.columns:
            data.loc[index, "event"] = f"SIM-{1000 + (position % 20)}"
        if "source" in data.columns:
            data.loc[index, "source"] = "simulated.attack.generator"
        if "src_ip" in data.columns:
            data.loc[index, "src_ip"] = f"203.0.113.{1 + (position % 200)}"
        if "http_status" in data.columns:
            data.loc[index, "http_status"] = "500" if position % 2 == 0 else "403"
        if "message" in data.columns:
            original = str(data.loc[index, "message"])
            data.loc[index, "message"] = f"{attack_message} | original={original[:160]}"

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_csv, sep=sep, index=False, encoding="utf-8-sig")
    print(f"Dataset simule: {output_csv}")
    print(f"Lignes: {len(data)}")
    print(f"Anomalies injectees: {anomaly_count}")
    return output_csv


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Injecte des anomalies simulees dans un CSV Logminer")
    parser.add_argument("-i", "--input", required=True, type=Path, help="CSV source normalise")
    parser.add_argument("-o", "--output", required=True, type=Path, help="CSV simule labellise")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--anomaly-fraction", type=float, default=0.05, help="Proportion d'anomalies injectees")
    parser.add_argument("--max-rows", type=int, default=10000, help="0 = toutes les lignes")
    parser.add_argument("--random-state", type=int, default=42, help="Graine aleatoire")
    args = parser.parse_args(argv)

    inject_anomalies(
        input_csv=args.input,
        output_csv=args.output,
        sep=args.sep,
        anomaly_fraction=args.anomaly_fraction,
        max_rows=args.max_rows,
        random_state=args.random_state,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
