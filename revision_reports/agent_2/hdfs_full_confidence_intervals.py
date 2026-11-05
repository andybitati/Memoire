"""Intervalles de confiance sur les blocs de test pour agent2_hdfs_full_20261104T131314Z.

Les cinq graines donnent la même matrice de confusion : l'IC de Student entre
graines est donc de largeur nulle et ne mesure pas l'incertitude d'échantillonnage
des blocs. On calcule ici des IC exacts (Clopper-Pearson) pour précision, rappel
et FPR, et un IC bootstrap (rééchantillonnage multinomial des 115 013 blocs) pour
le F1 et le MCC, qui ne dépendent que de la matrice de confusion.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
from scipy.stats import beta

OUT = Path(__file__).resolve().parent
RUN_ID = "agent2_hdfs_full_20261104T131314Z"
N_BOOT = 20000
SEED = 20261104


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    lower = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    upper = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lower, upper


def f1_mcc(tp, fp, tn, fn):
    tp, fp, tn, fn = (np.asarray(x, dtype=np.float64) for x in (tp, fp, tn, fn))
    f1 = np.divide(2 * tp, 2 * tp + fp + fn, out=np.zeros_like(tp), where=(2 * tp + fp + fn) > 0)
    denom = np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = np.divide(tp * tn - fp * fn, denom, out=np.zeros_like(tp), where=denom > 0)
    return f1, mcc


def main() -> int:
    with (OUT / f"{RUN_ID}__seed_metrics.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    matrices = {(int(r["test_tp"]), int(r["test_fp"]), int(r["test_tn"]), int(r["test_fn"])) for r in rows}
    if len(matrices) != 1:
        raise AssertionError(f"Matrices de confusion différentes selon la graine: {matrices}")
    tp, fp, tn, fn = matrices.pop()
    n = tp + fp + tn + fn

    rng = np.random.default_rng(SEED)
    draws = rng.multinomial(n, np.array([tp, fp, tn, fn]) / n, size=N_BOOT)
    f1, mcc = f1_mcc(draws[:, 0], draws[:, 1], draws[:, 2], draws[:, 3])
    f1_point, mcc_point = (float(v) for v in f1_mcc(tp, fp, tn, fn))

    payload = {
        "run_id": RUN_ID + "__test_block_ci",
        "source_run_id": RUN_ID,
        "source": f"revision_reports/agent_2/{RUN_ID}__seed_metrics.csv",
        "confusion_matrix_all_seeds": {"tp": tp, "fp": fp, "tn": tn, "fn": fn, "n": n},
        "precision": {"value": tp / (tp + fp), "ci95_clopper_pearson": clopper_pearson(tp, tp + fp)},
        "recall": {"value": tp / (tp + fn), "ci95_clopper_pearson": clopper_pearson(tp, tp + fn)},
        "fpr": {"value": fp / (fp + tn), "ci95_clopper_pearson": clopper_pearson(fp, fp + tn)},
        "f1": {"value": f1_point, "ci95_bootstrap_percentile": [float(np.quantile(f1, 0.025)), float(np.quantile(f1, 0.975))]},
        "mcc": {"value": mcc_point, "ci95_bootstrap_percentile": [float(np.quantile(mcc, 0.025)), float(np.quantile(mcc, 0.975))]},
        "bootstrap": {"replicates": N_BOOT, "seed": SEED, "method": "multinomial resampling of test blocks from the confusion matrix"},
    }
    path = OUT / f"{RUN_ID}__test_block_ci.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
