#!/usr/bin/env python3
"""Agent 5 - sensibilité secondaire du corrélateur à la durée des incidents.

Analyse descriptive : seul l'écart moyen inter-événements varie (1, 3, 6 min),
scénario S1 (clés stables), 20 graines, fenêtre 15 min. Elle ne sert pas à choisir
un paramètre : elle montre que le rappel dépend du rapport durée/fenêtre.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import agent5_correlation_extended as base  # noqa: E402

GAPS = [1.0, 3.0, 6.0]


def main() -> int:
    run_id = "agent5_correlation_gapsens_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = base.OUT_ROOT / run_id
    out.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="agent5_gap_"))
    rows = []
    try:
        for gap in GAPS:
            for seed in base.PROTOCOL["seeds"]:
                frame, truth, meta = base.generate(seed, 0.0, gap_mean_min=gap)
                for method in ("M_keys", "B_time"):
                    pred, trunc = base.run_method(frame, base.METHOD_KEEP[method], work, f"{gap}_{seed}_{method}", base.PROTOCOL["window_minutes"])
                    rows.append({"gap_mean_min": gap, "seed": seed, "method": method, **meta, "truncated_groups": trunc, **base.pair_metrics(truth, pred)})
    finally:
        shutil.rmtree(work, ignore_errors=True)
    pd.DataFrame(rows).to_csv(out / "per_seed_metrics.csv", index=False, encoding="utf-8")
    summary = {}
    for gap in GAPS:
        for method in ("M_keys", "B_time"):
            sub = [r for r in rows if r["gap_mean_min"] == gap and r["method"] == method]
            pool = base.pooled(sub)
            summary[f"gap{gap:g}_{method}"] = {
                "pooled": pool,
                "seed_bootstrap95": {k: base.seed_bootstrap(sub, k) for k in ("precision", "recall", "f1")},
                "fragmented_true_mean": float(np.mean([r["fragmented_true"] for r in sub])),
            }
    result = {"run_id": run_id, "status": "COMPLETED", "scenario": "S1_cles_stables", "gaps_min": GAPS,
              "seeds": base.PROTOCOL["seeds"], "base_protocol": base.PROTOCOL["protocol_id"],
              "role": "analyse secondaire descriptive, non utilisée pour régler un paramètre", "summary": summary}
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    for k, v in summary.items():
        p = v["pooled"]
        print(k, p["TP"], p["FP"], p["FN"], round(p["precision"], 4), round(p["recall"], 4), round(p["f1"], 4), v["seed_bootstrap95"]["recall"])
    print(run_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
