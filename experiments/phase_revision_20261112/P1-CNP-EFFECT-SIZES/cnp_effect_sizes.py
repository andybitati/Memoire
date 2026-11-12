"""Analyse secondaire (non préenregistrée) des campagnes Contract Net.

Pour chaque scénario et chaque contraste apparié par graine (C - static, C - least_loaded),
calcule : différence moyenne du taux d'échec à la première exécution, IC à 95 % (t de
Student), taille d'effet dz = moyenne / écart-type des différences, rapport de débit C /
comparateur avec IC, et différence minimale détectable (puissance 80 %, alpha 5 %,
bilatéral) avec n graines. Le contraste C - static est disponible dans deux jeux de
graines indépendants (E-CNP-STATIC-ASSIGNMENT : 20261105..., E-CNP-LEAST-LOADED :
20261205...), ce qui permet d'évaluer la réplication et une estimation poolée (60 graines).

Ne modifie aucune décision préenregistrée.
Usage : python cnp_effect_sizes.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "phase_revision_20261105"
OUT = Path(__file__).resolve().parent


def paired(df, arm, ref):
    a = df[df.arm == arm].set_index(["scenario", "seed"])
    b = df[df.arm == ref].set_index(["scenario", "seed"])
    j = a.join(b, lsuffix="_a", rsuffix="_b", how="inner")
    j["d_fail"] = j.first_execution_failure_rate_a - j.first_execution_failure_rate_b
    j["ratio_tp"] = j.throughput_tasks_sec_a / j.throughput_tasks_sec_b
    return j.reset_index()


def summarize(j, label):
    rows = []
    for sc, g in j.groupby("scenario"):
        n = len(g)
        d = g.d_fail
        m, sd = d.mean(), d.std(ddof=1)
        tcrit = stats.t.ppf(0.975, n - 1)
        se = sd / np.sqrt(n) if n > 1 else np.nan
        r = g.ratio_tp
        rse = r.std(ddof=1) / np.sqrt(n)
        # dz minimal détectable, puissance 0,8 (approximation normale + correction t)
        dz_mde = (stats.t.ppf(0.975, n - 1) + stats.t.ppf(0.80, n - 1)) / np.sqrt(n)
        rows.append({
            "contrast": label, "scenario": sc, "n": n,
            "fail_delta_mean": m,
            "fail_delta_ci_low": m - tcrit * se if sd > 0 else m,
            "fail_delta_ci_high": m + tcrit * se if sd > 0 else m,
            "fail_delta_sd": sd,
            "dz": m / sd if sd > 0 else np.nan,
            "dz_min_detectable_80pct": dz_mde,
            "fail_delta_min_detectable": dz_mde * sd,
            "throughput_ratio_mean": r.mean(),
            "throughput_ratio_ci_low": r.mean() - tcrit * rse,
            "throughput_ratio_ci_high": r.mean() + tcrit * rse,
        })
    return rows


static_runs = pd.read_csv(BASE / "E-CNP-STATIC-ASSIGNMENT" / "runs.csv")
ll_runs = pd.read_csv(BASE / "E-CNP-LEAST-LOADED" / "runs.csv")

j1 = paired(static_runs, "C", "static")
j2 = paired(ll_runs, "C", "static")
j3 = paired(ll_runs, "C", "least_loaded")
pooled = pd.concat([j1, j2])

rows = []
rows += summarize(j1, "C-static, graines 20261105+ (E-CNP-STATIC-ASSIGNMENT)")
rows += summarize(j2, "C-static, graines 20261205+ (E-CNP-LEAST-LOADED)")
rows += summarize(pooled, "C-static, 60 graines poolées")
rows += summarize(j3, "C-least_loaded, graines 20261205+")
out = pd.DataFrame(rows)
out.to_csv(OUT / "cnp_effect_sizes.csv", index=False)
pd.set_option("display.width", 250)
print(out[["contrast", "scenario", "n", "fail_delta_mean", "fail_delta_ci_low", "fail_delta_ci_high",
           "dz", "fail_delta_min_detectable", "throughput_ratio_mean", "throughput_ratio_ci_low",
           "throughput_ratio_ci_high"]].round(4).to_string(index=False))
