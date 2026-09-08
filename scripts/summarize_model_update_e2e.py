#!/usr/bin/env python3
"""Generate the phase-4 evidence table and figure from verified JSON artifacts."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
PHASE_DIR = ROOT / "data" / "processed" / "final_experiments_2026" / "phase_4"
DOC_DIR = ROOT / "docs" / "memoire" / "final_experiments_2026"
TABLE_DIR = DOC_DIR / "tables"
FIGURE_DIR = DOC_DIR / "figures"

CASE_LABELS = {
    "promotion": "Promotion",
    "rejection": "Rejet (candidat inférieur)",
    "positive_but_insufficient": "Rejet (gain < seuil)",
}


def main() -> int:
    integrity_path = PHASE_DIR / "model_update_integrity_report.json"
    payload = json.loads(integrity_path.read_text(encoding="utf-8"))
    if not payload.get("all_integrity_checks_passed"):
        raise RuntimeError("Integrity report is not fully validated")

    rows = []
    for case_key, case in payload["cases"].items():
        rows.append(
            {
                "case": case_key,
                "case_label": CASE_LABELS[case_key],
                "dataset": "CICIDS2017 local — DDoS holdout seed 42",
                "protocol": "functional end-to-end branch test",
                "metric": case["metric"],
                "current_score": case["current_score"],
                "candidate_score": case["candidate_score"],
                "delta": case["delta"],
                "min_delta": case["min_delta"],
                "decision": case["decision"],
                "promoted": case["promoted"],
                "integrity_verified": case["integrity_verified"],
                "current_hash_before": case["current_hash_before"],
                "candidate_hash": case["candidate_hash"],
                "backup_hash": case["backup_hash"] or "",
                "current_hash_after": case["current_hash_after"],
            }
        )

    csv_path = PHASE_DIR / "model_update_decisions.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    TABLE_DIR.mkdir(parents=True, exist_ok=True)
    table_path = TABLE_DIR / "model_update_end_to_end.md"
    lines = [
        "# Mise à jour contrôlée des modèles — test fonctionnel end-to-end",
        "",
        "Dataset local : CICIDS2017, holdout DDoS, seed 42. Métrique de décision : F1. Seuil minimal de gain : 0,02. N = 3 comparaisons fonctionnelles préspécifiées.",
        "",
        "| Cas | F1 courant | F1 candidat | Delta | Seuil | Décision | Intégrité |",
        "| --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        decision = "promu" if row["promoted"] else "courant conservé"
        integrity = "vérifiée" if row["integrity_verified"] else "non vérifiée"
        lines.append(
            f"| {row['case_label']} | {row['current_score']:.6f} | "
            f"{row['candidate_score']:.6f} | {row['delta']:+.6f} | "
            f"{row['min_delta']:.6f} | {decision} | {integrity} |"
        )
    lines.extend(
        [
            "",
            "Statut scientifique : validation fonctionnelle de la procédure contrôlée. Ces trois cas ne constituent ni une nouvelle évaluation indépendante de généralisation, ni une preuve d'apprentissage continu autonome.",
        ]
    )
    table_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    labels = [row["case_label"] for row in rows]
    current = [row["current_score"] for row in rows]
    candidate = [row["candidate_score"] for row in rows]
    x = list(range(len(rows)))
    width = 0.36
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    ax.bar([value - width / 2 for value in x], current, width, label="Modèle courant", color="#4C78A8")
    ax.bar([value + width / 2 for value in x], candidate, width, label="Candidat", color="#F58518")
    for index, row in enumerate(rows):
        marker = "PROMU" if row["promoted"] else "NON PROMU"
        ax.text(index, max(current[index], candidate[index]) + 0.025, f"Δ={row['delta']:+.6f}\n{marker}", ha="center", va="bottom", fontsize=9)
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 0.92)
    ax.set_ylabel("F1 sur l'évaluation gelée")
    ax.set_title("CICIDS2017 local — mise à jour contrôlée end-to-end\nHoldout DDoS, seed 42, N = 3 comparaisons, seuil Δ = 0,02")
    ax.legend(loc="lower left")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    figure_path = FIGURE_DIR / "model_update_promotion_rejet.png"
    fig.savefig(figure_path, dpi=180)
    plt.close(fig)

    print(
        json.dumps(
            {
                "csv": str(csv_path),
                "table": str(table_path),
                "figure": str(figure_path),
                "rows": len(rows),
            },
            ensure_ascii=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
