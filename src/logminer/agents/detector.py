"""Agent detecteur d'anomalies base sur Isolation Forest."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import joblib
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
    model_in: str | Path = "",
    model_out: str | Path = "",
    bus: LocalMessageBus | None = None,
) -> str:
    """Entraine ou recharge Isolation Forest puis exporte les scores.

    En mode prototype, le modele peut etre entraine directement sur le CSV
    fourni. Pour les gros datasets, l'entrainement peut se faire sur le cloud:
    `model_out` enregistre alors un artefact joblib reutilisable localement avec
    `model_in`. L'artefact contient aussi les colonnes de features, afin que
    l'inference realigne les colonnes one-hot sur le schema appris.
    """

    if bus is not None:
        bus.publish(
            source="detector",
            target="correlator",
            message_type="detection.started",
            payload={
                "input_csv": str(input_csv),
                "output_csv": str(output_csv),
                "contamination": contamination,
                "model_in": str(model_in),
                "model_out": str(model_out),
            },
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

    if model_in:
        artifact = load_model_artifact(model_in)
        model = artifact["model"]
        feature_columns = artifact["feature_columns"]
        features = align_features(features, feature_columns)
    else:
        model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
            n_jobs=1,
        )
        labels = model.fit_predict(features)
        if model_out:
            save_model_artifact(
                model_out,
                model=model,
                feature_columns=list(features.columns),
                input_csv=input_csv,
                contamination=contamination,
                random_state=random_state,
                max_categorical_unique=max_categorical_unique,
                train_rows=len(events),
            )

    if model_in:
        labels = model.predict(features)
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
                "model_in": str(model_in),
                "model_out": str(model_out),
            },
        )

    return str(output_path)


def save_model_artifact(
    path: str | Path,
    *,
    model: IsolationForest,
    feature_columns: list[str],
    input_csv: str | Path,
    contamination: float,
    random_state: int,
    max_categorical_unique: int,
    train_rows: int,
) -> str:
    """Enregistre le modele et son schema de features avec joblib.

    Sauvegarder seulement le modele ne suffit pas avec des variables one-hot:
    les colonnes peuvent changer entre entrainement et inference. L'artefact
    conserve donc l'ordre exact des colonnes vues pendant l'entrainement.
    """

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    artifact = {
        "model_type": "isolation_forest",
        "model": model,
        "feature_columns": feature_columns,
        "metadata": {
            "input_csv": str(input_csv),
            "contamination": contamination,
            "random_state": random_state,
            "max_categorical_unique": max_categorical_unique,
            "train_rows": train_rows,
            "trained_at": datetime.now(timezone.utc).isoformat(),
        },
    }
    joblib.dump(artifact, output_path)
    return str(output_path)


def load_model_artifact(path: str | Path) -> dict:
    """Charge un artefact joblib produit par `save_model_artifact`."""

    artifact = joblib.load(path)
    if not isinstance(artifact, dict) or "model" not in artifact or "feature_columns" not in artifact:
        raise ValueError(f"Artefact modele invalide: {path}")
    return artifact


def align_features(features: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Realigne les features d'inference sur le schema d'entrainement."""

    return features.reindex(columns=feature_columns, fill_value=0).astype(float)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent detecteur Logminer avec Isolation Forest")
    parser.add_argument("-i", "--input", required=True, help="CSV normalise produit par Logminer")
    parser.add_argument("-o", "--output", default="data/processed/anomalies.csv", help="CSV des anomalies")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--contamination", type=float, default=0.05, help="Proportion attendue d'anomalies")
    parser.add_argument("--random-state", type=int, default=42, help="Graine aleatoire")
    parser.add_argument("--max-categorical-unique", type=int, default=100, help="Limite one-hot par colonne")
    parser.add_argument("--model-in", default="", help="Artefact joblib a charger pour scorer sans reentrainer")
    parser.add_argument("--model-out", default="", help="Chemin joblib ou sauvegarder le modele entraine")
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
        model_in=args.model_in,
        model_out=args.model_out,
        bus=bus,
    )

    anomalies = pd.read_csv(output, sep=args.sep, dtype=str, keep_default_na=False)
    count = int((anomalies.get("is_anomaly", "0").astype(str) == "1").sum())
    print(f"CSV anomalies: {output}")
    print(f"Evenements analyses: {len(anomalies)}")
    print(f"Anomalies candidates: {count}")
    if args.model_out:
        print(f"Modele sauvegarde: {args.model_out}")
    if args.model_in:
        print(f"Modele charge: {args.model_in}")
    if bus is not None:
        print(f"Bus: {bus.path}")
        print(f"Run ID: {bus.run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
