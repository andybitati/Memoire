#!/usr/bin/env python3
"""Agent 6 -- agregation (lecture seule) des runs stricts e3 HDFS/BGL existants.

Lit data/processed/final_experiments_2026/phase_3/e3_strict_*.json (aucun calcul
de modele), calcule moyenne/ecart-type par (dataset, methode) et la reference
triviale « tout positif » F1 = 2p/(1+p) a la prevalence de test.
"""
from __future__ import annotations

import glob
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "revision_reports/agent_6/artifacts"
run_id = "agent6_strict_e3_aggregate_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
rows = []
for f in sorted(glob.glob(str(ROOT / "data/processed/final_experiments_2026/phase_3/e3_strict_*.json"))):
    d = json.loads(Path(f).read_text(encoding="utf-8"))
    m, v = d["metrics"], d["validation_metrics"]
    rows.append({
        "source_run_id": d["run_id"], "dataset": d["dataset"], "method": d["method"], "seed": d["seed"],
        "test_prevalence": d["configuration"]["split_positive_rate"]["test"],
        "train_prevalence": d["configuration"]["split_positive_rate"]["train"],
        "val_f1": v["f1"], "val_fpr": v["fpr"],
        "test_f1": m["f1"], "test_precision": m["precision"], "test_recall": m["recall"],
        "test_fpr": m["fpr"], "test_pr_auc": m["pr_auc"], "test_mcc": m["mcc"],
    })
df = pd.DataFrame(rows)
agg = df.groupby(["dataset", "method"]).agg(
    n_seeds=("seed", "nunique"), test_prevalence=("test_prevalence", "first"),
    val_f1_mean=("val_f1", "mean"), test_f1_mean=("test_f1", "mean"), test_f1_std=("test_f1", "std"),
    test_fpr_mean=("test_fpr", "mean"), test_pr_auc_mean=("test_pr_auc", "mean"), test_mcc_mean=("test_mcc", "mean"),
).reset_index()
agg["all_positive_f1"] = 2 * agg["test_prevalence"] / (1 + agg["test_prevalence"])
agg.insert(0, "run_id", run_id)
df.insert(0, "run_id", run_id)
df.to_csv(OUT / f"{run_id}_per_run.csv", index=False)
agg.to_csv(OUT / f"{run_id}_summary.csv", index=False)
pd.set_option("display.width", 220)
print(run_id)
print(agg.to_string())
