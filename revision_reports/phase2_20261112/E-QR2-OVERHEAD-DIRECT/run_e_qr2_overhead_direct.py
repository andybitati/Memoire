"""E-QR2-OVERHEAD-DIRECT : surcoût d'orchestration mesuré à l'intérieur de chaque tâche.

Pour chaque tâche, surcoût = durée totale vue par l'architecture − durée du handler
(effet métier, mesurée autour de l'appel). La variabilité de l'inférence, commune aux deux
termes, s'annule ; seul le coût de l'organisation (négociation, messages, attribution,
journalisation) reste. Réutilise sans modification le benchmark A-D
(scripts/run_true_multi_agent_experiments.py) et l'effet réel d'E-QR2-REAL-INFERENCE.

Plan : tâche {micro, reelle} x architecture {A, C, D} x 1 worker x 10 graines
(20261501 à 20261510), 200 tâches par exécution.

Protocole : revision_reports/phase2_20261112/E-QR2-OVERHEAD-DIRECT/PROTOCOLE.md.
Usage : python run_e_qr2_overhead_direct.py [--smoke]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import sklearn

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "phase2_20261112" / "E-QR2-REAL-INFERENCE"))
import run_e_qr2_real_inference as previous  # noqa: E402  (charge aussi le modèle et le benchmark)

bench = previous.bench
EXPERIMENT = "E-QR2-OVERHEAD-DIRECT"
OUT = ROOT / "experiments" / "phase_revision_20261112" / EXPERIMENT
SEEDS = tuple(20_261_501 + index for index in range(10))
LOAD = 200
ARCHS = ("A", "C", "D")
KINDS = ("micro", "reelle")
ADDITIVITY_MARGIN_MS = 0.25
T95_9 = 2.2621571627409915
_HANDLER_MS: dict[str, float] = {}


def timed(effect):
    def wrapper(task, context):
        started = time.perf_counter()
        try:
            return effect(task, context)
        finally:
            _HANDLER_MS[task.task_id] = (time.perf_counter() - started) * 1000.0
    return wrapper


def run(kind, arch, seed, rep):
    _HANDLER_MS.clear()
    effect = previous.real_effect if kind == "reelle" else previous._ORIGINAL_EFFECT
    bench.synthetic_effect = timed(effect)
    try:
        workload = bench.generate_workload(LOAD, seed)
        run_id = f"{EXPERIMENT}-{kind}-{arch}-{seed}"
        row, tasks, _ = bench.run_one_architecture(
            arch, workload, run_id=run_id, load=LOAD, repetition=rep, seed=seed, workers=1)
    finally:
        bench.synthetic_effect = previous._ORIGINAL_EFFECT
    if row["status"] != "ok" or len(tasks) != LOAD:
        raise AssertionError(f"{run_id}: exécution incomplète ({row['error']})")
    handler = [_HANDLER_MS[t["task_id"]] for t in tasks]
    overhead = [t["latency_ms"] - _HANDLER_MS[t["task_id"]] for t in tasks]
    return {"kind": kind, "architecture": arch, "seed": seed,
            "handler_median_ms": statistics.median(handler),
            "total_median_ms": statistics.median(t["latency_ms"] for t in tasks),
            "overhead_median_ms": statistics.median(overhead),
            "overhead_mean_ms": statistics.fmean(overhead),
            "overhead_p95_ms": bench.percentile(overhead, 0.95),
            "throughput_tasks_sec": row["throughput_tasks_sec"]}


def ci(values):
    m = statistics.fmean(values)
    half = T95_9 * statistics.stdev(values) / math.sqrt(len(values))
    return {"n": len(values), "mean": m, "ci95_lower": m - half, "ci95_upper": m + half}


def analyse(rows):
    by = {(r["kind"], r["architecture"], r["seed"]): r for r in rows}
    seeds = sorted({r["seed"] for r in rows})
    res, decision = {}, {}
    for arch in ARCHS:
        for kind in KINDS:
            res[f"{kind}_{arch}_overhead_median_ms"] = ci([by[(kind, arch, s)]["overhead_median_ms"] for s in seeds])
            res[f"{kind}_{arch}_handler_median_ms"] = ci([by[(kind, arch, s)]["handler_median_ms"] for s in seeds])
        diff = [by[("reelle", arch, s)]["overhead_median_ms"] - by[("micro", arch, s)]["overhead_median_ms"] for s in seeds]
        rel = [by[("reelle", arch, s)]["overhead_median_ms"] / by[("reelle", arch, s)]["handler_median_ms"] for s in seeds]
        res[f"{arch}_real_minus_micro_overhead_ms"] = ci(diff)
        res[f"{arch}_relative_overhead_real"] = ci(rel)
        if arch == "A":
            continue
        d = res[f"{arch}_real_minus_micro_overhead_ms"]
        if d["ci95_upper"] <= ADDITIVITY_MARGIN_MS:
            verdict = "surcout_additif_confirme"
        elif d["ci95_lower"] > ADDITIVITY_MARGIN_MS:
            verdict = "surcout_non_additif"
        else:
            verdict = "indetermine"
        decision[arch] = verdict
    verdicts = set(decision.values())
    decision["conclusion"] = verdicts.pop() if len(verdicts) == 1 else "mixte"
    return res, decision


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    global LOAD
    seeds = (1, 2) if args.smoke else SEEDS
    if args.smoke:
        LOAD = 20
    started = datetime.now(timezone.utc)
    rows = []
    for position, seed in enumerate(seeds):
        order = ARCHS[position % 3:] + ARCHS[: position % 3]
        for kind in KINDS:
            for arch in order:
                rows.append(run(kind, arch, seed, position))
    if args.smoke:
        print(f"essai technique conforme : {len(rows)} exécutions")
        return 0
    res, decision = analyse(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    runs = OUT / "runs.csv"
    with runs.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = OUT / "summary.json"
    summary.write_text(json.dumps({
        "experiment_id": EXPERIMENT, "started_at_utc": started.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(), "load": LOAD, "seeds": list(seeds),
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "scikit_learn": sklearn.__version__, "numpy": np.__version__},
        "results": res, "decision": decision}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sources = [Path(__file__).resolve(), Path(previous.__file__).resolve(),
               ROOT / "scripts" / "run_true_multi_agent_experiments.py",
               ROOT / "src" / "logminer" / "agents" / "contract_net.py", previous.MODEL_PATH]
    with (OUT / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["role", "path", "bytes", "sha256"])
        for role, p in [("artifact", runs), ("artifact", summary)] + [("source", p) for p in sources]:
            w.writerow([role, p.relative_to(ROOT).as_posix(), p.stat().st_size, sha256(p)])
    print("terminé :", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
