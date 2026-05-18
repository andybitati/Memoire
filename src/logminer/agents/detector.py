"""Agent detecteur d'anomalies base sur Isolation Forest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

import pandas as pd
from sklearn.ensemble import IsolationForest


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from features.event_features import build_feature_frame, load_events

try:
    from agents.bus import LocalMessageBus
except ImportError:
    LocalMessageBus = None


def detect_anomalies(
    input_csv: str | Path,
    output_csv: str | Path,
    sep: str = ";",
    contamination: float = 0.05,
    random_state: int = 42,
    max_categorical_unique: int = 100,
    bus: LocalMessageBus | None = None,
) -> str:
    """Entraine Isolation Forest sur un CSV normalise et exporte les scores.

    Le modele est non supervise: il apprend la structure globale du lot donne,
    puis marque les evenements les plus atypiques comme anomalies candidates.
    """

    if bus is not None:
        bus.publish(
            source="detector",
            target="correlator",
            message_type="detection.started",
            payload={"input_csv": str(input_csv), "output_csv": str(output_csv), "contamination": contamination},
        )

    events = load_events(input_csv, sep=sep)
    if events.empty:
        raise ValueError(f"Aucun evenement a analyser dans {input_csv}")

    features = build_feature_frame(events, max_categorical_unique=max_categorical_unique)
    if features.empty:
        raise ValueError("Impossible de construire des features ML depuis le CSV fourni")

    contamination = min(max(float(contamination), 0.001), 0.5)
    if len(events) < 20:
        contamination = min(contamination, 1 / max(len(events), 1))

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
        n_jobs=1,
    )
    labels = model.fit_predict(features)
    scores = model.decision_function(features)

    result = events.copy()
    result["anomaly_score"] = scores
    result["is_anomaly"] = (labels == -1).astype(int)
    result["anomaly_rank"] = result["anomaly_score"].rank(method="first", ascending=True).astype(int)

    output_path = Path(output_csv)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    result.sort_values(["is_anomaly", "anomaly_score"], ascending=[False, True]).to_csv(
        output_path,
        sep=sep,
        index=False,
        encoding="utf-8-sig",
    )

    anomaly_count = int(result["is_anomaly"].sum())
    if bus is not None:
        bus.publish(
            source="detector",
            target="correlator",
            message_type="detection.completed",
            payload={
                "input_csv": str(input_csv),
                "output_csv": str(output_path),
                "events": int(len(result)),
                "anomalies": anomaly_count,
            },
        )

    return str(output_path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent detecteur Logminer avec Isolation Forest")
    parser.add_argument("-i", "--input", required=True, help="CSV normalise produit par Logminer")
    parser.add_argument("-o", "--output", default="data/processed/anomalies.csv", help="CSV des anomalies")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--contamination", type=float, default=0.05, help="Proportion attendue d'anomalies")
    parser.add_argument("--random-state", type=int, default=42, help="Graine aleatoire")
    parser.add_argument("--max-categorical-unique", type=int, default=100, help="Limite one-hot par colonne")
    parser.add_argument("--bus", default="", help="Journal de messages JSONL")
    parser.add_argument("--run-id", default=None, help="Identifiant de run partage entre agents")
    args = parser.parse_args(argv)

    bus = None
    if args.bus:
        if LocalMessageBus is None:
            raise RuntimeError("Bus local indisponible")
        bus = LocalMessageBus(args.bus, run_id=args.run_id)

    output = detect_anomalies(
        input_csv=args.input,
        output_csv=args.output,
        sep=args.sep,
        contamination=args.contamination,
        random_state=args.random_state,
        max_categorical_unique=args.max_categorical_unique,
        bus=bus,
    )

    anomalies = pd.read_csv(output, sep=args.sep, dtype=str, keep_default_na=False)
    count = int((anomalies.get("is_anomaly", "0").astype(str) == "1").sum())
    print(f"CSV anomalies: {output}")
    print(f"Evenements analyses: {len(anomalies)}")
    print(f"Anomalies candidates: {count}")
    if bus is not None:
        print(f"Bus: {bus.path}")
        print(f"Run ID: {bus.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
