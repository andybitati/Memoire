"""Analyse secondaire (non préenregistrée) de E-H4-HDFS-BLOCK-BASELINES.

Calcule le MCC de chaque référence et d'Histogram à partir des matrices de confusion
enregistrées (tp, fp, tn, fn), par graine, puis en moyenne. Ne modifie pas la décision
préenregistrée, fondée sur le F1.

Usage : python hdfs_block_mcc.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "experiments" / "phase_revision_20261105" / "E-H4-HDFS-BLOCK-BASELINES" / "metrics_by_seed.csv"
OUT = Path(__file__).resolve().parent

d = pd.read_csv(SRC)
tp, fp, tn, fn = (d[c].astype(float) for c in ("tp", "fp", "tn", "fn"))
den = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
d["mcc"] = np.where(den > 0, (tp * tn - fp * fn) / den.where(den > 0, 1.0), np.nan)
d.to_csv(OUT / "hdfs_block_mcc_by_seed.csv", index=False)

summary = d.groupby("baseline")[["f1", "mcc", "precision", "recall"]].mean().reset_index()
summary.to_csv(OUT / "hdfs_block_mcc_summary.csv", index=False)
print(summary.round(6).to_string(index=False))
