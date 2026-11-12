"""E-QR2-REAL-INFERENCE : coût de l'organisation en agents sur une tâche d'inférence réelle.

Réutilise le benchmark A-D (scripts/run_true_multi_agent_experiments.py) sans le
modifier : seul l'effet exécuté par tâche est remplacé, par monkeypatching de
``synthetic_effect``, soit par l'effet synthétique d'origine (microtâche), soit par un
appel réel au modèle Isolation Forest HDFS du prototype
(``models/isolation_forest_hdfs_colab.joblib``, ``decision_function`` sur un vecteur de
21 variables dérivé de la tâche).

Plan : tâche {micro, reelle} x architecture {A, B, C, D} x workers {1, 3} x 10 répétitions,
200 tâches par exécution, graines 20261401 à 20261410, ordre des architectures alterné.

Protocole : revision_reports/phase2_20261112/E-QR2-REAL-INFERENCE/PROTOCOLE.md.
Usage : python run_e_qr2_real_inference.py [--smoke]
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
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import run_true_multi_agent_experiments as bench  # noqa: E402

EXPERIMENT = "E-QR2-REAL-INFERENCE"
OUT = ROOT / "experiments" / "phase_revision_20261112" / EXPERIMENT
MODEL_PATH = ROOT / "models" / "isolation_forest_hdfs_colab.joblib"
SEEDS = tuple(20_261_401 + index for index in range(10))
LOAD = 200
ARCHS = ("A", "B", "C", "D")
WORKERS = (1, 3)
KINDS = ("micro", "reelle")
ADDITIVITY_FACTOR = 2.0
T95 = {9: 2.2621571627409915, 1: 12.706204736432095}

warnings.filterwarnings("ignore", message="X does not have valid feature names")
_ORIGINAL_EFFECT = bench.synthetic_effect
# Désérialisation joblib : fichier produit par ce projet et versionné avec le prototype
# (même modèle que la condition M), jamais une source externe ; son empreinte SHA-256
# est inscrite au manifeste.
_MODEL = joblib.load(MODEL_PATH)
_MODEL = _MODEL.get("model", _MODEL) if isinstance(_MODEL, dict) else _MODEL
_N_FEATURES = int(_MODEL.n_features_in_)


def real_effect(task, context):
    output = _ORIGINAL_EFFECT(task, context)
    values = [float(v) for v in task.payload.get("values", [])]
    vector = np.zeros((1, _N_FEATURES))
    vector[0, : min(len(values), _N_FEATURES)] = np.asarray(values[:_N_FEATURES]) / 10_000.0
    output["anomaly_score"] = float(_MODEL.decision_function(vector)[0])
    return output


def run(kind, arch, workers, seed, rep):
    bench.synthetic_effect = real_effect if kind == "reelle" else _ORIGINAL_EFFECT
    try:
        workload = bench.generate_workload(LOAD, seed)
        run_id = f"{EXPERIMENT}-{kind}-{arch}-w{workers}-{seed}"
        row, _tasks, _coord = bench.run_one_architecture(
            arch, workload, run_id=run_id, load=LOAD, repetition=rep, seed=seed, workers=workers)
    finally:
        bench.synthetic_effect = _ORIGINAL_EFFECT
    if row["status"] != "ok" or row["successful_tasks"] != LOAD:
        raise AssertionError(f"{run_id}: exécution incomplète ({row['error']})")
    return {"kind": kind, "architecture": arch, "workers": workers, "seed": seed,
            "duration_sec": row["duration_sec"], "throughput_tasks_sec": row["throughput_tasks_sec"],
            "latency_median_ms": row["latency_median_ms"], "latency_p95_ms": row["latency_p95_ms"],
            "messages_per_task": row["messages_per_task"]}


def ci(values):
    n = len(values)
    m = statistics.fmean(values)
    if n < 2:
        return {"n": n, "mean": m, "ci95_lower": m, "ci95_upper": m}
    half = T95[n - 1] * statistics.stdev(values) / math.sqrt(n)
    return {"n": n, "mean": m, "ci95_lower": m - half, "ci95_upper": m + half}


def analyse(rows):
    by = {(r["kind"], r["architecture"], r["workers"], r["seed"]): r for r in rows}
    seeds = sorted({r["seed"] for r in rows})
    res = {}
    for kind in KINDS:
        for workers in WORKERS:
            a = [by[(kind, "A", workers, s)] for s in seeds]
            res[f"{kind}_w{workers}_A_service_ms"] = ci([1000.0 / r["throughput_tasks_sec"] for r in a])
            for arch in ("B", "C", "D"):
                x = [by[(kind, arch, workers, s)] for s in seeds]
                over = [1000.0 / xr["throughput_tasks_sec"] - 1000.0 / ar["throughput_tasks_sec"] for xr, ar in zip(x, a)]
                rel = [(1.0 / xr["throughput_tasks_sec"] - 1.0 / ar["throughput_tasks_sec"]) / (1.0 / ar["throughput_tasks_sec"]) for xr, ar in zip(x, a)]
                ratio = [xr["throughput_tasks_sec"] / ar["throughput_tasks_sec"] for xr, ar in zip(x, a)]
                res[f"{kind}_w{workers}_{arch}_minus_A_overhead_ms"] = ci(over)
                res[f"{kind}_w{workers}_{arch}_relative_overhead"] = ci(rel)
                res[f"{kind}_w{workers}_{arch}_over_A_throughput_ratio"] = ci(ratio)
    decision = {}
    for arch in ("C", "D"):
        micro = res[f"micro_w1_{arch}_minus_A_overhead_ms"]["mean"]
        real = res[f"reelle_w1_{arch}_minus_A_overhead_ms"]
        bound = ADDITIVITY_FACTOR * micro
        if real["ci95_upper"] <= bound:
            verdict = "surcout_additif_confirme"
        elif real["ci95_lower"] > bound:
            verdict = "surcout_non_additif"
        else:
            verdict = "indetermine"
        decision[arch] = {"micro_overhead_ms": micro, "bound_ms": bound,
                          "real_overhead_ci95_upper_ms": real["ci95_upper"], "verdict": verdict}
    verdicts = {v["verdict"] for v in decision.values()}
    decision["conclusion"] = verdicts.pop() if len(verdicts) == 1 else "mixte"
    return res, decision


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="graines réservées 1 et 2, 20 tâches, rien n'est écrit ni affiché")
    args = parser.parse_args()
    global LOAD
    seeds = (1, 2) if args.smoke else SEEDS
    if args.smoke:
        LOAD = 20
    started = datetime.now(timezone.utc)
    rows = []
    plan = [(k, w) for k in KINDS for w in WORKERS]
    for position, seed in enumerate(seeds):
        order = ARCHS[position % 4:] + ARCHS[: position % 4]
        for kind, workers in plan:
            for arch in order:
                rows.append(run(kind, arch, workers, seed, position))
    res, decision = analyse(rows)
    if args.smoke:
        print(f"essai technique conforme : {len(rows)} exécutions")
        return 0
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
        "model": str(MODEL_PATH.relative_to(ROOT).as_posix()), "n_features": _N_FEATURES,
        "environment": {"python": platform.python_version(), "platform": platform.platform(),
                        "scikit_learn": sklearn.__version__, "numpy": np.__version__},
        "results": res, "decision": decision}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sources = [Path(__file__).resolve(), ROOT / "scripts" / "run_true_multi_agent_experiments.py",
               ROOT / "src" / "logminer" / "agents" / "contract_net.py",
               ROOT / "src" / "logminer" / "agents" / "intelligent_runtime.py", MODEL_PATH]
    with (OUT / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["role", "path", "bytes", "sha256"])
        for role, p in [("artifact", runs), ("artifact", summary)] + [("source", p) for p in sources]:
            w.writerow([role, p.relative_to(ROOT).as_posix(), p.stat().st_size, sha256(p)])
    print("terminé :", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
