"""Explain CICIDS2017 holdout instability by held-out scenario."""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pandas as pd


METRICS = Path("data/processed/controlled_split_cicids_metrics.csv")
OUT = Path("data/processed/cicids_holdout_instability_analysis.csv")
TABLE = Path("docs/memoire/tables/table_cicids_holdout_instability.md")


def _heldout_file(notes: str) -> str:
    match = re.search(r"heldout_file=([^;]+)", str(notes))
    return match.group(1) if match else ""


def _labels(notes: str) -> dict[str, int]:
    match = re.search(r"test_labels=(\{.*\})", str(notes))
    if not match:
        return {}
    try:
        parsed = ast.literal_eval(match.group(1))
    except Exception:
        return {}
    return {str(key): int(value) for key, value in parsed.items()}


def _attack_labels(counts: dict[str, int]) -> str:
    attacks = {key: value for key, value in counts.items() if key.upper() != "BENIGN"}
    return ", ".join(f"{key}={value}" for key, value in attacks.items()) or "aucune"


def main() -> int:
    frame = pd.read_csv(METRICS)
    holdout = frame[frame["split"].eq("file_or_scenario_holdout")].copy()
    holdout["heldout_file"] = holdout["notes"].map(_heldout_file)
    holdout["label_counts"] = holdout["notes"].map(_labels)
    holdout["attack_labels"] = holdout["label_counts"].map(_attack_labels)
    holdout["positive_total_in_file"] = holdout["label_counts"].map(
        lambda counts: sum(value for key, value in counts.items() if key.upper() != "BENIGN")
    )
    holdout["benign_total_in_file"] = holdout["label_counts"].map(lambda counts: counts.get("BENIGN", 0))
    holdout["file_positive_rate"] = holdout["positive_total_in_file"] / (
        holdout["positive_total_in_file"] + holdout["benign_total_in_file"]
    )
    holdout["positive_detected_rate"] = holdout["tp"] / (holdout["tp"] + holdout["fn"])
    columns = [
        "seed",
        "heldout_file",
        "attack_labels",
        "file_positive_rate",
        "test_rows",
        "test_positive_rate",
        "tp",
        "fn",
        "fp",
        "tn",
        "precision",
        "recall",
        "f1",
        "pr_auc",
        "mcc",
    ]
    result = holdout[columns].sort_values("seed")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(OUT, index=False, encoding="utf-8-sig")

    rows = [
        "# Instabilite Holdout CICIDS2017",
        "",
        "| Seed | Fichier tenu hors entrainement | Attaques du fichier | Taux attaque fichier | TP | FN | FP | F1 | PR-AUC | Lecture |",
        "| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for _, row in result.iterrows():
        if row["f1"] == 0:
            reading = "aucun positif detecte dans l'echantillon tenu hors entrainement"
        elif row["f1"] < 0.1:
            reading = "detection quasi nulle malgre quelques positifs retrouves"
        else:
            reading = "scenario partiellement generalise"
        rows.append(
            "| {seed:.0f} | {heldout_file} | {attack_labels} | {file_positive_rate:.4f} | {tp:.0f} | {fn:.0f} | {fp:.0f} | {f1:.6f} | {pr_auc:.6f} | {reading} |".format(
                reading=reading,
                **row,
            )
        )
    rows.extend(
        [
            "",
            "Conclusion: l'ecart-type eleve vient de l'heterogeneite des scenarios tenus hors entrainement. Le modele generalise partiellement au DDoS, presque pas au PortScan dans ce protocole, et pas aux scenarios Bot, Infiltration et WebAttacks echantillonnes.",
        ]
    )
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(result.to_string(index=False).encode("ascii", errors="replace").decode("ascii"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
