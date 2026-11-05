"""Agent 4 -- BGL, protocole diagnostique F : anomalies recurrentes a template connu.

Les protocoles R0, B, C, D, E (bgl_second_protocol.py) laissent <= 7 positifs de test sur un
template connu : les familles d'anomalies BGL apparaissent par rafales et la rafale du test R0
(ciod: Error reading message prefix on CioStream socket ...) n'existe pas avant le test.
F choisit donc, APRES inspection de la position des familles d'anomalies dans le journal, un
segment initial ou les memes familles (ciod: failed to read message prefix, rts panic, machine
check interrupt) reviennent : train = lignes 1..200 000, validation = 700 001..800 000,
test = 800 001..950 000. Decoupage chronologique, Drain3 ajuste sur train seul (sans label),
statistiques Histogram sur train normal, seuil sur validation. La fenetre etant choisie au vu
des labels, F est un diagnostic de mecanisme, non une estimation de performance.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bgl_second_protocol as bsp  # noqa: E402

PROTO = sys.argv[1] if len(sys.argv) > 1 else "F"
RUN_ID = ("agent4_bgl_known_template_diag_" if PROTO == "F" else "agent4_bgl_contiguous_horizon_") + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
bsp.RUN_ID = RUN_ID


def main() -> None:
    if PROTO == "F":
        ranges = {"train": [(1, 200000)], "validation": [(700001, 800000)], "test": [(800001, 950000)]}
        name, desc, uses_labels = "F_recurrent_anomaly_segment", "Diagnostic post hoc : train 1-200000, validation 700001-800000, test 800001-950000.", True
    else:
        # G : regle sans label ; test R0, validation = 20 000 lignes precedentes, train = 80 000 lignes contigues precedentes
        ranges = {"train": [(4163167, 4243166)], "validation": [(4243167, 4263166)], "test": [(4263167, 4283166)]}
        name, desc, uses_labels = "G_contiguous_short_horizon", "Test R0 ; validation 4243167-4263166 ; train contigu 4163167-4243166 (80 000 lignes).", False
    frames = bsp.read_ranges(ranges)
    res = bsp.evaluate(name, frames, ["train"], desc)
    csv_path = bsp.OUT / f"{RUN_ID}__group_metrics.csv"
    pd.DataFrame(res["group_rows"]).to_csv(csv_path, index=False, encoding="utf-8")
    summary = {
        "run_id": RUN_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=bsp.ROOT, text=True).strip(),
        "inputs": {"raw_log": "data/raw/Datasets/BGL/BGL.log", "raw_log_sha256": bsp.sha256(bsp.RAW)},
        "ranges_one_based_inclusive": {k: [list(x) for x in v] for k, v in ranges.items()},
        "selection_uses_labels": uses_labels,
        "selection_note": ("fenetre choisie apres inspection de la position des familles d'anomalies ; diagnostic, pas estimation" if uses_labels else "plages fixees par regle positionnelle relative au test R0, sans label"),
        "observation_unit": "raw log event",
        "results": [res],
        "artifacts": [str(csv_path.relative_to(bsp.ROOT)).replace("\\", "/")],
    }
    out = bsp.OUT / f"{RUN_ID}__result.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    m, c = res["test_metrics_histogram"], res["coverage"]
    print(json.dumps({"f1": m["f1"], "tp": m["tp"], "fp": m["fp"], "fn": m["fn"], "tn": m["tn"], **c,
                      "eq_sev": res["histogram_decision_decomposition"]["hist_pred_equals_severity_novelty"]}, indent=1))
    for row in res["group_rows"]:
        print(row["model"], row["group"], row["n"], row["positives"], "f1=%.6f" % row["f1"], "rec=%.4f" % row["recall"])
    print(out)


if __name__ == "__main__":
    main()
