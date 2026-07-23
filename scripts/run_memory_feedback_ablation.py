"""Ablation de la memoire de feedback analyste sur les anomalies Logminer.

Le script mesure l'effet de la memoire sur la priorisation, pas une amelioration
de generalisation du modele. Il peut utiliser l'audit reel ou un scenario
controle qui simule le rejet des motifs les plus repetitifs.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "logminer"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agents.feedback_memory import FeedbackProfile, apply_feedback_memory, feedback_key_from_row, load_feedback_profile


DEFAULT_INPUT = ROOT / "data" / "processed" / "wazuh_months_anomalies.csv"
DEFAULT_OUT = ROOT / "data" / "processed" / "memory_feedback_ablation.csv"
DEFAULT_TABLE = ROOT / "docs" / "memoire" / "tables" / "table_memory_feedback_ablation.md"


def _count_priority(frame: pd.DataFrame, threshold: float) -> int:
    if "memory_priority_score" not in frame.columns:
        return 0
    values = pd.to_numeric(frame["memory_priority_score"], errors="coerce").fillna(0)
    return int((values >= threshold).sum())


def _simulated_profile(frame: pd.DataFrame, top_n: int, reject_count: int) -> FeedbackProfile:
    keys = frame.apply(feedback_key_from_row, axis=1)
    most_common = Counter(keys).most_common(max(1, top_n))
    rejects = Counter({key: int(reject_count) for key, _ in most_common})
    return FeedbackProfile(decisions=sum(rejects.values()), rejects=rejects, accepts=Counter(), reclassifies=Counter())


def run_ablation(
    input_csv: Path,
    *,
    sep: str = ";",
    output_csv: Path = DEFAULT_OUT,
    table_out: Path = DEFAULT_TABLE,
    simulate_top_n: int = 5,
    simulated_reject_count: int = 3,
) -> pd.DataFrame:
    frame = pd.read_csv(input_csv, sep=sep, dtype=str, keep_default_na=False)
    actual_profile = load_feedback_profile()
    actual = apply_feedback_memory(frame, profile=actual_profile)
    simulated_profile = _simulated_profile(frame, simulate_top_n, simulated_reject_count)
    simulated = apply_feedback_memory(frame, profile=simulated_profile)

    baseline_candidates = int((pd.to_numeric(frame.get("is_anomaly", pd.Series(1, index=frame.index)), errors="coerce").fillna(1) == 1).sum())
    actual_downranked = int((pd.to_numeric(actual["memory_priority_delta"], errors="coerce").fillna(0) < 0).sum())
    simulated_downranked = int((pd.to_numeric(simulated["memory_priority_delta"], errors="coerce").fillna(0) < 0).sum())

    rows = [
        {
            "scenario": "audit_reel",
            "feedback_decisions": actual_profile.decisions,
            "candidate_rows": len(frame),
            "anomaly_candidates": baseline_candidates,
            "downranked_rows": actual_downranked,
            "priority_ge_70": _count_priority(actual, 70),
            "priority_ge_50": _count_priority(actual, 50),
            "reading": "effet mesure a partir des decisions analyste auditees",
        },
        {
            "scenario": f"controle_top_{simulate_top_n}_motifs_rejetes",
            "feedback_decisions": simulated_profile.decisions,
            "candidate_rows": len(frame),
            "anomaly_candidates": baseline_candidates,
            "downranked_rows": simulated_downranked,
            "priority_ge_70": _count_priority(simulated, 70),
            "priority_ge_50": _count_priority(simulated, 50),
            "reading": "test de sensibilite: motifs repetitifs abaisses par feedback simule",
        },
    ]
    result = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_csv, sep=sep, index=False, encoding="utf-8-sig")

    table_out.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Ablation Memoire Feedback",
        "",
        "| Scenario | Decisions feedback | Lignes | Anomalies candidates | Lignes abaissees | Priorite >= 70 | Priorite >= 50 | Lecture |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['feedback_decisions']} | {row['candidate_rows']} | "
            f"{row['anomaly_candidates']} | {row['downranked_rows']} | {row['priority_ge_70']} | "
            f"{row['priority_ge_50']} | {row['reading']} |"
        )
    lines.extend(
        [
            "",
            "Note: cette ablation mesure l'effet de la memoire sur la priorisation des alertes. "
            "Elle ne prouve pas a elle seule une amelioration de la generalisation du modele.",
        ]
    )
    table_out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Evalue l'effet de la memoire feedback sur la priorisation.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--sep", default=";")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--table-out", type=Path, default=DEFAULT_TABLE)
    parser.add_argument("--simulate-top-n", type=int, default=5)
    parser.add_argument("--simulated-reject-count", type=int, default=3)
    args = parser.parse_args()
    result = run_ablation(
        args.input,
        sep=args.sep,
        output_csv=args.output,
        table_out=args.table_out,
        simulate_top_n=args.simulate_top_n,
        simulated_reject_count=args.simulated_reject_count,
    )
    print(result.to_string(index=False))
    print(f"CSV: {args.output}")
    print(f"Table: {args.table_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
