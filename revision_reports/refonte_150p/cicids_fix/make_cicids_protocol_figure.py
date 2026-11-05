"""Régénère fig_cicids_protocol_comparison.png à partir des artefacts retenus.

- séparation aléatoire et protocole temporel : cicids_protocol_comparison.csv
  (lignes « Random stratifié » et « Holdout temporel ») ;
- holdout par scénario : E-CICIDS-HOLDOUT-FIX (RandomForest et tout positif),
  qui remplace la ligne « Holdout scénario (historique) », issue d'un
  échantillonnage par premières lignes.

Aucune valeur n'est écrite en dur : tout est lu dans les CSV.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "ARIEL_LOGMINER_MEMOIRE_FINAL/figures/final/fig_cicids_protocol_comparison.png"
PROTO = ROOT / "experiments/phase_dataset_strengthening/aggregated/cicids_protocol_comparison.csv"
FIX = ROOT / "experiments/phase_revision_20261105/E-CICIDS-HOLDOUT-FIX/summary.csv"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 15, "axes.titlesize": 18,
                     "axes.labelsize": 16, "xtick.labelsize": 13, "ytick.labelsize": 13,
                     "savefig.dpi": 360})

proto = pd.read_csv(PROTO, encoding="utf-8-sig")
fix = pd.read_csv(FIX, encoding="utf-8").set_index("model")

random_rf = proto[proto.protocol.str.startswith("Random")].iloc[0]
temporal = proto[proto.protocol.str.startswith("Holdout temporel")].set_index("model")

bars = [
    ("Séparation aléatoire\nRandom Forest", float(random_rf.f1), "#2563eb"),
    ("Holdout par scénario\nRandom Forest", float(fix.loc["RandomForest", "f1_mean"]), "#dc2626"),
    ("Holdout par scénario\nTout positif", float(fix.loc["AllPositive", "f1_mean"]), "#9ca3af"),
    ("Temporel\nRégression logistique", float(temporal.loc["LogisticRegression", "f1"]), "#d97706"),
    ("Temporel\nRandom Forest", float(temporal.loc["RandomForest", "f1"]), "#16a34a"),
]

fig, ax = plt.subplots(figsize=(12, 6.5))
x = np.arange(len(bars))
rects = ax.bar(x, [b[1] for b in bars], color=[b[2] for b in bars])
for r in rects:
    ax.annotate(f"{r.get_height():.4f}".replace(".", ","), (r.get_x() + r.get_width() / 2, r.get_height()),
                xytext=(0, 5), textcoords="offset points", ha="center", va="bottom", fontsize=12)
ax.set_xticks(x, [b[0] for b in bars], rotation=12, ha="right")
ax.set_ylabel("F1 de la classe attaque (moyenne)")
ax.set_ylim(0, 1.08)
ax.set_title("CICIDS2017 : sensibilité du F1 au protocole de séparation")
ax.grid(axis="y", alpha=.25)
fig.savefig(OUT, dpi=360, bbox_inches="tight", facecolor="white")
print(OUT)
for label, value, _ in bars:
    print(label.replace("\n", " / "), round(value, 6))
