"""Estimation (non mesurée) du surcoût relatif de l'orchestration en agents sur une
tâche d'inférence réelle.

Surcoût par tâche = 1/débit(agents) - 1/débit(monolithe), débits du benchmark A--D
(tableau tab:benchmark-debit, charges 100 et 5 000). Latence d'inférence = moyenne, sur
les sept sources passées par un modèle, de la latence moyenne de la condition M.

Hypothèse : le surcoût est additif et indépendant de la durée de la tâche. Si la latence
de la condition M inclut déjà une part d'orchestration, le rapport est surestimé.

Usage : python overhead_estimate.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "experiments" / "phase_final_scientific_consolidation" / "aggregated" / "multisource_cnp_model_inference_by_source.csv"
OUT = Path(__file__).resolve().parent

# Débits moyens (tâches/s) du tableau tab:benchmark-debit ; source :
# ma_20260909T160812Z_34016__statistics.csv (matrice A.2).
THROUGHPUT = {
    100: {"A_monolithe": 72657, "C_agents": 1309, "D_agents_memoire": 1249},
    5000: {"A_monolithe": 84728, "C_agents": 1201, "D_agents_memoire": 1178},
}

d = pd.read_csv(SRC)
m = d[(d.condition == "M") & (d.model_inference_count > 0)]
inference_mean_s = m.latency_mean.mean()
inference_weighted_s = (m.latency_mean * m.n).sum() / m.n.sum()

rows = []
for load, t in THROUGHPUT.items():
    for arch in ("C_agents", "D_agents_memoire"):
        overhead_s = 1 / t[arch] - 1 / t["A_monolithe"]
        rows.append({
            "load": load,
            "architecture": arch,
            "overhead_ms_per_task": overhead_s * 1000,
            "inference_mean_ms": inference_mean_s * 1000,
            "relative_overhead_pct": 100 * overhead_s / inference_mean_s,
        })
out = pd.DataFrame(rows)
out.to_csv(OUT / "overhead_estimate.csv", index=False)
print(f"sources M avec inférence : {len(m)} ; latence moyenne {inference_mean_s*1000:.2f} ms (pondérée {inference_weighted_s*1000:.2f} ms)")
print(out.round(3).to_string(index=False))
