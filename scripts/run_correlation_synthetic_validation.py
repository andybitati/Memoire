"""Validation contrôlée du corrélateur sur une vérité terrain synthétique figée."""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "logminer"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agents.correlator import correlate_anomalies


DOC_ROOT = ROOT / "docs" / "memoire" / "final_experiments_2026"
DATA_ROOT = ROOT / "data" / "processed" / "final_experiments_2026"
PHASE_ROOT = DATA_ROOT / "phase_8"
CONFIG_PATH = DOC_ROOT / "configs" / "correlation_synthetic_protocol.json"
LEDGER_PATH = DOC_ROOT / "state" / "EXPERIMENT_LEDGER.csv"
INPUT_PATH = PHASE_ROOT / "correlation_synthetic_input.csv"
TRUTH_PATH = PHASE_ROOT / "correlation_synthetic_truth.csv"
INCIDENTS_PATH = PHASE_ROOT / "correlation_synthetic_incidents.csv"
PAIRS_PATH = PHASE_ROOT / "correlation_synthetic_pairs.csv"
SUMMARY_PATH = DATA_ROOT / "correlation_synthetic_summary.json"
TABLE_PATH = DOC_ROOT / "tables" / "correlation_synthetic_metrics.md"
FIGURE_PATH = DOC_ROOT / "figures" / "correlation_synthetic_metrics.png"
REPORT_PATH = DOC_ROOT / "experiment_correlation_synthetic_summary.md"
EXPERIMENT_ID = "e8_correlation_synthetic_controlled"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def current_git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def append_ledger(status: str, started_at: str, completed_at: str = "", notes: str = "") -> None:
    row = {
        "experiment_id": EXPERIMENT_ID,
        "phase": "8",
        "run_id": EXPERIMENT_ID,
        "dataset": "synthetic controlled incidents",
        "scenario": "fixed-window correlation edge cases",
        "seed": "",
        "model": "agents.correlator.correlate_anomalies",
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "command": "scripts/run_correlation_synthetic_validation.py --resume",
        "config_path": str(CONFIG_PATH.relative_to(ROOT)).replace("\\", "/"),
        "raw_result_path": str(PAIRS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "summary_path": str(SUMMARY_PATH.relative_to(ROOT)).replace("\\", "/"),
        "figure_path": str(FIGURE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "error_path": "",
        "git_commit": current_git_commit(),
        "notes": notes,
    }
    with LEDGER_PATH.open("r", encoding="utf-8", newline="") as handle:
        fields = next(csv.reader(handle))
    with LEDGER_PATH.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writerow(row)


def valid_completed_artifact() -> bool:
    if not SUMMARY_PATH.exists() or SUMMARY_PATH.stat().st_size == 0:
        return False
    try:
        summary = json.loads(SUMMARY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return summary.get("experiment_id") == EXPERIMENT_ID and summary.get("status") == "COMPLETED"


def build_data(config: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    events: list[dict[str, object]] = []
    truth: list[dict[str, str]] = []
    event_no = 1
    for incident in config["true_incidents"]:
        for timestamp in incident["timestamps"]:
            event_id = f"EVT-{event_no:03d}"
            row = {
                "timestamp_iso": timestamp,
                "is_anomaly": "1",
                "event": event_id,
                **incident["keys"],
                "severity": "WARNING",
                "anomaly_score": "-0.10",
                "anomaly_rank": str(event_no),
            }
            events.append(row)
            truth.append({"event": event_id, "true_incident": incident["id"]})
            event_no += 1
    for noise in config["noise_events"]:
        event_id = f"NOISE-{event_no:03d}"
        events.append(
            {
                **noise,
                "is_anomaly": "0",
                "event": event_id,
                "severity": "INFO",
                "anomaly_score": "0.10",
                "anomaly_rank": str(event_no),
            }
        )
        event_no += 1
    return pd.DataFrame(events), pd.DataFrame(truth)


def evaluate(truth: pd.DataFrame, incidents: pd.DataFrame, noise_ids: set[str]) -> tuple[dict, pd.DataFrame]:
    true_map = dict(zip(truth["event"], truth["true_incident"]))
    pred_map: dict[str, str] = {}
    for row in incidents.itertuples(index=False):
        for event_id in str(row.events).split(","):
            if event_id:
                pred_map[event_id] = str(row.incident_id)
    if set(pred_map) != set(true_map):
        raise ValueError("La sortie ne couvre pas exactement tous les événements anomaux")

    pair_rows = []
    tp = fp = fn = tn = 0
    for left, right in itertools.combinations(sorted(true_map), 2):
        true_same = true_map[left] == true_map[right]
        pred_same = pred_map[left] == pred_map[right]
        outcome = "TP" if true_same and pred_same else "FP" if pred_same else "FN" if true_same else "TN"
        tp += outcome == "TP"
        fp += outcome == "FP"
        fn += outcome == "FN"
        tn += outcome == "TN"
        pair_rows.append({"event_left": left, "event_right": right, "true_same": int(true_same), "predicted_same": int(pred_same), "outcome": outcome})

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    true_to_pred: dict[str, set[str]] = {}
    pred_to_true: dict[str, set[str]] = {}
    for event_id, true_id in true_map.items():
        pred_id = pred_map[event_id]
        true_to_pred.setdefault(true_id, set()).add(pred_id)
        pred_to_true.setdefault(pred_id, set()).add(true_id)
    output_event_ids = {value for cell in incidents["events"].astype(str) for value in cell.split(",") if value}
    metrics = {
        "pairwise_tp": tp,
        "pairwise_fp": fp,
        "pairwise_fn": fn,
        "pairwise_tn": tn,
        "pairwise_precision": precision,
        "pairwise_recall": recall,
        "pairwise_f1": f1,
        "true_incidents": len(true_to_pred),
        "predicted_incidents": len(pred_to_true),
        "fragmented_true_incidents": sum(len(ids) > 1 for ids in true_to_pred.values()),
        "incorrectly_fused_predicted_incidents": sum(len(ids) > 1 for ids in pred_to_true.values()),
        "noise_events": len(noise_ids),
        "noise_excluded": len(noise_ids - output_event_ids),
    }
    return metrics, pd.DataFrame(pair_rows)


def write_outputs(config: dict, input_events: pd.DataFrame, truth: pd.DataFrame, metrics: dict) -> None:
    table = [
        "| Métrique | Valeur |",
        "| --- | ---: |",
        f"| Événements d'entrée | {len(input_events)} |",
        f"| Événements anomaux évalués | {len(truth)} |",
        f"| Incidents vrais | {metrics['true_incidents']} |",
        f"| Incidents produits | {metrics['predicted_incidents']} |",
        f"| Précision pairwise | {metrics['pairwise_precision']:.6f} |",
        f"| Rappel pairwise | {metrics['pairwise_recall']:.6f} |",
        f"| F1 pairwise | {metrics['pairwise_f1']:.6f} |",
        f"| Incidents vrais fragmentés | {metrics['fragmented_true_incidents']} |",
        f"| Incidents prédits fusionnant plusieurs vérités | {metrics['incorrectly_fused_predicted_incidents']} |",
        f"| Bruits exclus | {metrics['noise_excluded']}/{metrics['noise_events']} |",
    ]
    TABLE_PATH.write_text("\n".join(table) + "\n", encoding="utf-8")

    labels = ["Précision\npairwise", "Rappel\npairwise", "F1\npairwise"]
    values = [metrics["pairwise_precision"], metrics["pairwise_recall"], metrics["pairwise_f1"]]
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    bars = ax.bar(labels, values, color=["#4472C4", "#70AD47", "#ED7D31"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Corrélation synthétique contrôlée — fenêtre fixe 15 min (N=16 anomalies)")
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.02, f"{value:.3f}", ha="center")
    ax.text(0.5, -0.18, f"Fragmentations: {metrics['fragmented_true_incidents']} | Fusions incorrectes: {metrics['incorrectly_fused_predicted_incidents']}", transform=ax.transAxes, ha="center")
    fig.tight_layout()
    fig.savefig(FIGURE_PATH, dpi=180)
    plt.close(fig)

    report = f"""# Corrélation d'incidents — validation synthétique contrôlée

## Objectif

Évaluer l'implémentation réelle `correlate_anomalies` sur une vérité terrain synthétique figée avant exécution, sans revendiquer une validation SOC réelle.

## Protocole

- Fenêtre fixe: {config['window_minutes']} minutes, arrondie par plancher temporel.
- Clés: `host`, `user`, `source`, `category`, `subcategory`, `proto`, `dst_port`.
- Vérité terrain séparée de l'entrée du corrélateur.
- 19 événements: 16 anomalies dans 6 incidents vrais et 3 bruits non anomaux.
- Cas contrôlés: deux incidents stables, un incident traversant une frontière de fenêtre, deux incidents distincts aux clés identiques dans la même fenêtre, un incident stable supplémentaire et trois bruits.
- Mesure pairwise sur les 120 paires d'événements anomaux.

## Résultats

- Incidents produits: {metrics['predicted_incidents']} pour {metrics['true_incidents']} incidents vrais.
- Précision pairwise: `{metrics['pairwise_precision']:.6f}`.
- Rappel pairwise: `{metrics['pairwise_recall']:.6f}`.
- F1 pairwise: `{metrics['pairwise_f1']:.6f}`.
- Comptages pairwise: TP={metrics['pairwise_tp']}, FP={metrics['pairwise_fp']}, FN={metrics['pairwise_fn']}, TN={metrics['pairwise_tn']}.
- Incidents vrais fragmentés: {metrics['fragmented_true_incidents']}.
- Incidents prédits fusionnant plusieurs incidents vrais: {metrics['incorrectly_fused_predicted_incidents']}.
- Bruits exclus: {metrics['noise_excluded']}/{metrics['noise_events']}.

## Interprétation

Le corrélateur fonctionne conformément à ses règles explicites sur les cas stables et filtre le bruit marqué non anomal. La fenêtre fixe peut fragmenter un incident traversant sa frontière. Des incidents indépendants indiscernables par les clés disponibles sont fusionnés. Cette expérience teste la logique déterministe sur scénarios construits; elle ne mesure ni une généralisation à des incidents réels ni une performance SOC.

## Artefacts

- `configs/correlation_synthetic_protocol.json`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_input.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_truth.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_incidents.csv`.
- `data/processed/final_experiments_2026/phase_8/correlation_synthetic_pairs.csv`.
- `data/processed/final_experiments_2026/correlation_synthetic_summary.json`.
- `tables/correlation_synthetic_metrics.md`.
- `figures/correlation_synthetic_metrics.png`.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps({"experiment_id": EXPERIMENT_ID, "status": "PLANNED", **config["expected_counts_before_run"]}, indent=2))
        return 0
    if args.resume and valid_completed_artifact():
        print("SKIPPED_ALREADY_COMPLETED")
        return 0

    started_at = now_iso()
    append_ledger("RUNNING", started_at)
    PHASE_ROOT.mkdir(parents=True, exist_ok=True)
    TABLE_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    input_events, truth = build_data(config)
    expected = config["expected_counts_before_run"]
    assert len(input_events) == expected["input_events"]
    assert len(truth) == expected["anomalous_events"]
    input_events.to_csv(INPUT_PATH, sep=config["separator"], index=False, encoding="utf-8-sig")
    truth.to_csv(TRUTH_PATH, sep=config["separator"], index=False, encoding="utf-8-sig")
    correlate_anomalies(INPUT_PATH, INCIDENTS_PATH, sep=config["separator"], window_minutes=config["window_minutes"], parallel_workers=config["parallel_workers"])
    incidents = pd.read_csv(INCIDENTS_PATH, sep=config["separator"], dtype=str, keep_default_na=False)
    noise_ids = set(input_events.loc[input_events["is_anomaly"] == "0", "event"])
    metrics, pairs = evaluate(truth, incidents, noise_ids)
    pairs.to_csv(PAIRS_PATH, index=False, encoding="utf-8-sig")
    completed_at = now_iso()
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": EXPERIMENT_ID,
        "status": "COMPLETED",
        "started_at": started_at,
        "completed_at": completed_at,
        "git_commit": current_git_commit(),
        "config_path": str(CONFIG_PATH.relative_to(ROOT)).replace("\\", "/"),
        "dataset": "synthetic controlled incidents",
        "protocol_id": config["protocol_id"],
        "window_minutes": config["window_minutes"],
        "input_events": len(input_events),
        "anomalous_events": len(truth),
        **metrics,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_outputs(config, input_events, truth, metrics)
    append_ledger("COMPLETED", started_at, completed_at, f"pairwise_f1={metrics['pairwise_f1']:.6f} fragmentation={metrics['fragmented_true_incidents']} fusion={metrics['incorrectly_fused_predicted_incidents']}")
    print(json.dumps(summary, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
