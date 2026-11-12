"""Analyse et décision préenregistrées d'E-MULTIVM-SATURATION-DIAG.

Lit les résumés des trois bras (both, debian, ubuntu), calcule la capacité de chaque bras
(médiane sur les répétitions du débit atteint au débit offert le plus élevé) et la part de
tâches d'Ubuntu dans le bras both, applique la règle du protocole et écrit summary.json et
le manifeste.

Usage : python analyse_diag.py RUN_ID_BOTH RUN_ID_DEBIAN RUN_ID_UBUNTU
"""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "experiments" / "phase_revision_20261112" / "E-MULTIVM-SATURATION-DIAG"
TOP_RATE = 32.0
LOW_RATES = (2.0, 4.0, 8.0)


def load(run_id):
    return json.loads((OUT / f"{run_id}__saturation_summary.json").read_text(encoding="utf-8"))


def capacity(summary):
    values = [lv["completed_tasks_sec"] for lv in summary["levels"] if float(lv["offered_tasks_sec"]) == TOP_RATE]
    return statistics.median(values), values


def ubuntu_share(summary, rates):
    ok = sub = 0
    for lv in summary["levels"]:
        if float(lv["offered_tasks_sec"]) in rates:
            by = lv["tasks_by_agent"]
            ok += by.get("ubuntu-beta", 0)
            sub += sum(by.values())
    return ok / sub if sub else float("nan")


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    run_both, run_deb, run_ubu = sys.argv[1:4]
    both, deb, ubu = load(run_both), load(run_deb), load(run_ubu)
    c_both, v_both = capacity(both)
    c_deb, v_deb = capacity(deb)
    c_ubu, v_ubu = capacity(ubu)
    ratio = c_both / c_deb
    share_low = ubuntu_share(both, LOW_RATES)
    share_all = ubuntu_share(both, (2.0, 4.0, 8.0, 16.0, 32.0))
    if ratio <= 1.2 and share_low <= 0.10:
        verdict = "goulot_agent_serie_confirme"
    elif ratio >= 1.5:
        verdict = "goulot_agent_serie_refute"
    else:
        verdict = "indetermine"
    failures = {name: sum(lv["failed"] for lv in s["levels"]) for name, s in (("both", both), ("debian", deb), ("ubuntu", ubu))}
    summary = {
        "experiment_id": "E-MULTIVM-SATURATION-DIAG",
        "analysed_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_ids": {"both": run_both, "debian": run_deb, "ubuntu": run_ubu},
        "capacity_tasks_sec_at_rate32": {"both": {"median": c_both, "values": v_both},
                                         "debian": {"median": c_deb, "values": v_deb},
                                         "ubuntu": {"median": c_ubu, "values": v_ubu}},
        "ratio_both_over_debian": ratio,
        "ratio_ubuntu_over_debian": c_ubu / c_deb,
        "ubuntu_share_in_both": {"rates_2_4_8": share_low, "all_rates": share_all},
        "failed_tasks": failures,
        "agents": {name: s["agents"] for name, s in (("both", both), ("debian", deb), ("ubuntu", ubu))},
        "decision": verdict,
    }
    path = OUT / "summary.json"
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    files = sorted(OUT.glob("*__saturation_*")) + [path]
    sources = [ROOT / "revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG" / n
               for n in ("run_saturation_arm.py", "start_agents.ps1", "run_diag.ps1", "analyse_diag.py")]
    sources += [ROOT / "revision_reports/agent_3/hdfs_redis_agent.py", ROOT / "src/logminer/agents/redis_contract_net.py"]
    with (OUT / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["role", "path", "bytes", "sha256"])
        for role, p in [("artifact", f) for f in files] + [("source", s) for s in sources]:
            w.writerow([role, p.relative_to(ROOT).as_posix(), p.stat().st_size, sha256(p)])
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
