"""Detecteur baseline explicable pour l'objectif 2.

Ce module sert de point de comparaison face aux modeles IA. Il ne cherche pas a
etre le meilleur detecteur possible; il formalise une approche simple, lisible
et reproductible basee sur des regles de securite et quelques signaux
statistiques. Dans le memoire, il joue le role de baseline "heuristique".
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from features.event_features import load_events


SEVERITY_WEIGHT = {
    "": 0.0,
    "DEBUG": 0.1,
    "VERBOSE": 0.1,
    "INFO": 0.2,
    "WARNING": 0.45,
    "ERROR": 0.8,
    "CRITICAL": 1.0,
}

SECURITY_CATEGORY_WEIGHT = {
    "AUTHENTICATION": 0.65,
    "AUTHORIZATION": 0.6,
    "INTRUSION_ATTEMPT": 0.9,
    "DOS_ATTACK": 0.9,
    "MALWARE": 1.0,
    "SYSTEM_ERROR": 0.55,
    "APPLICATION_ERROR": 0.45,
    "CONFIGURATION_CHANGE": 0.5,
}

SUSPICIOUS_MESSAGE = re.compile(
    r"failed|failure|denied|unauthorized|exception|crash|fault|malware|scan|brute|flood|bad password",
    re.I,
)


def _series(events: pd.DataFrame, column: str) -> pd.Series:
    """Retourne une colonne texte meme si elle est absente du CSV."""

    return events.get(column, pd.Series("", index=events.index)).fillna("").astype(str)


def _rarity_score(values: pd.Series) -> pd.Series:
    """Score simple: plus une valeur est rare, plus elle devient suspecte.

    Les journaux contiennent beaucoup d'evenements repetitifs. Une source ou un
    EventID tres rare n'est pas automatiquement malveillant, mais c'est un bon
    signal faible pour une baseline explicable.
    """

    counts = values.value_counts(dropna=False)
    if counts.empty:
        return pd.Series(0.0, index=values.index)
    max_count = counts.max()
    return values.map(lambda value: 1.0 - (counts.get(value, 0) / max_count)).astype(float)


def score_events(events: pd.DataFrame) -> pd.DataFrame:
    """Calcule un score baseline et une explication par evenement."""

    result = events.copy()
    severity = _series(result, "severity").str.upper()
    category = _series(result, "category").str.upper()
    message = _series(result, "message")
    http_status = pd.to_numeric(_series(result, "http_status"), errors="coerce").fillna(0)

    severity_score = severity.map(SEVERITY_WEIGHT).fillna(0.0)
    category_score = category.map(SECURITY_CATEGORY_WEIGHT).fillna(0.0)
    keyword_score = message.str.contains(SUSPICIOUS_MESSAGE).astype(float) * 0.55
    http_score = http_status.apply(lambda status: 0.7 if status >= 500 else 0.5 if status in (401, 403) else 0.0)
    event_rarity = _rarity_score(_series(result, "event")) * 0.35
    source_rarity = _rarity_score(_series(result, "source")) * 0.25

    # Pondération conservatrice: un evenement doit cumuler plusieurs signaux
    # pour arriver en haut du classement.
    result["baseline_score"] = (
        severity_score + category_score + keyword_score + http_score + event_rarity + source_rarity
    ).round(6)

    explanations = []
    for index in result.index:
        reasons: list[str] = []
        if severity_score.loc[index] >= 0.8:
            reasons.append("severity")
        if category_score.loc[index] >= 0.6:
            reasons.append("security_category")
        if keyword_score.loc[index] > 0:
            reasons.append("suspicious_message")
        if http_score.loc[index] > 0:
            reasons.append("http_status")
        if event_rarity.loc[index] > 0.25:
            reasons.append("rare_event")
        if source_rarity.loc[index] > 0.18:
            reasons.append("rare_source")
        explanations.append(",".join(reasons) or "low_signal")

    result["baseline_reason"] = explanations
    result["baseline_rank"] = result["baseline_score"].rank(method="first", ascending=False).astype(int)
    return result


def detect_baseline(
    input_csv: str | Path,
    output_csv: str | Path,
    sep: str = ";",
    contamination: float = 0.05,
) -> str:
    """Produit un CSV d'anomalies candidates avec la baseline explicable."""

    events = load_events(input_csv, sep=sep)
    if events.empty:
        raise ValueError(f"Aucun evenement a analyser dans {input_csv}")

    contamination = min(max(float(contamination), 0.001), 0.5)
    limit = max(1, int(len(events) * contamination))
    result = score_events(events)
    result["is_anomaly"] = 0
    result.loc[result["baseline_score"].nlargest(limit).index, "is_anomaly"] = 1

    output_path = Path(output_csv)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    result.sort_values(["is_anomaly", "baseline_score"], ascending=[False, False]).to_csv(
        output_path,
        sep=sep,
        index=False,
        encoding="utf-8-sig",
    )
    return str(output_path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Baseline explicable pour la detection d'anomalies")
    parser.add_argument("-i", "--input", required=True, help="CSV normalise Logminer")
    parser.add_argument("-o", "--output", default="data/processed/baseline_anomalies.csv", help="CSV de sortie")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--contamination", type=float, default=0.05, help="Proportion d'anomalies candidates")
    args = parser.parse_args(argv)

    output = detect_baseline(args.input, args.output, args.sep, args.contamination)
    rows = pd.read_csv(output, sep=args.sep, dtype=str, keep_default_na=False)
    count = int((rows["is_anomaly"].astype(str) == "1").sum())
    print(f"CSV baseline: {output}")
    print(f"Evenements analyses: {len(rows)}")
    print(f"Anomalies candidates: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
