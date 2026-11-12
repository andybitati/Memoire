"""Analyse secondaire (non préenregistrée) de E-CICIDS-HOLDOUT-FIX.

Agrège PR-AUC et MCC, déjà présents dans metrics.csv, par scénario tenu à l'écart et par
modèle, et les compare à la prévalence du test (PR-AUC d'un classement aléatoire) et au
MCC de la prédiction systématiquement positive (0). Ne modifie pas la décision
préenregistrée, fondée sur le F1.

Usage : python aggregate_cicids_holdout.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "experiments" / "phase_revision_20261105" / "E-CICIDS-HOLDOUT-FIX" / "metrics.csv"
OUT = Path(__file__).resolve().parent

d = pd.read_csv(SRC)
models = d[d.model != "AllPositive"]

by_scenario = (
    models.groupby(["scenario", "model"])
    .agg(
        seeds=("seed", "nunique"),
        prevalence=("test_positive_rate", "mean"),
        pr_auc=("pr_auc", "mean"),
        mcc=("mcc", "mean"),
        f1=("f1", "mean"),
    )
    .reset_index()
)
by_scenario["pr_auc_over_prevalence"] = by_scenario.pr_auc / by_scenario.prevalence
by_scenario.to_csv(OUT / "cicids_holdout_secondary_by_scenario.csv", index=False)

by_model = (
    models.groupby("model")
    .agg(pr_auc=("pr_auc", "mean"), mcc=("mcc", "mean"), f1=("f1", "mean"))
    .reset_index()
)
counts = by_scenario.assign(
    mcc_positive=by_scenario.mcc > 0,
    pr_auc_above_prevalence=by_scenario.pr_auc > by_scenario.prevalence,
).groupby("model")[["mcc_positive", "pr_auc_above_prevalence"]].sum().reset_index()
by_model = by_model.merge(counts, on="model")
by_model.to_csv(OUT / "cicids_holdout_secondary_by_model.csv", index=False)

print(by_scenario.round(4).to_string(index=False))
print()
print(by_model.round(4).to_string(index=False))
