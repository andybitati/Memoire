#!/usr/bin/env python3
"""Agent 5 - corrélation : corpus synthétique agrandi, plusieurs graines, baselines.

Réutilise sans modification ``src/logminer/agents/correlator.py::correlate_anomalies``.
Les baselines sont obtenues en appelant le même corrélateur sur une copie de
l'entrée dont certaines clés de regroupement sont vidées :

* ``B_time``      : fenêtre temporelle seule (toutes les clés vidées) ;
* ``B_host_time`` : fenêtre temporelle + hôte (autres clés vidées) ;
* ``M_keys``      : corrélateur complet (fenêtre + 7 clés), configuration du mémoire.

Le protocole (paramètres du générateur, graines, fenêtre) est écrit dans le JSON
de sortie avant l'évaluation. Aucun paramètre n'est réglé a posteriori.
Sortie : revision_reports/agent_5/correlation/<run_id>/.
"""

from __future__ import annotations

import itertools
import json
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta, t as student_t

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "logminer"))
from agents.correlator import GROUP_COLUMNS, correlate_anomalies  # noqa: E402

OUT_ROOT = ROOT / "revision_reports" / "agent_5" / "correlation"
KEY_COLUMNS = [c for c in GROUP_COLUMNS if c != "time_window"]
ORIGINAL_INPUT = ROOT / "data/processed/final_experiments_2026/phase_8/correlation_synthetic_input.csv"
ORIGINAL_TRUTH = ROOT / "data/processed/final_experiments_2026/phase_8/correlation_synthetic_truth.csv"

PROTOCOL = {
    "protocol_id": "agent5_correlation_extended_v1",
    "algorithm": "src/logminer/agents/correlator.py::correlate_anomalies (inchangé)",
    "window_minutes": 15,
    "seeds": list(range(20)),
    "scenarios": {
        "S1_cles_stables": {"p_multistage": 0.0},
        "S2_multi_etapes": {"p_multistage": 0.3},
    },
    "generator": {
        "horizon_hours": 12,
        "start": "2026-01-15T00:00:00Z",
        "n_incidents": 80,
        "events_per_incident": "1 + Poisson(3), plafonné à 10",
        "inter_event_gap_minutes": "Exponentielle(moyenne 3), arrondie à la seconde",
        "n_isolated_anomalies": 20,
        "n_noise_non_anomalous": 40,
        "incident_types": ["auth_bruteforce", "network_scan", "authz_denied", "process_spawn"],
        "multistage_chain": "LOGIN_FAILURE(auth.log) -> LOGIN_SUCCESS(auth.log) -> SPAWN(sysmon), même hôte et utilisateur",
        "host_pool_per_type": 8,
        "user_pool": 6,
        "scan_ports": [22, 80, 445, 3389],
        "db_ports": [3306, 5432],
    },
    "methods": {
        "M_keys": "corrélateur complet : floor(t,15min)+host+user+source+category+subcategory+proto+dst_port",
        "B_host_time": "même code, clés vidées sauf host : floor(t,15min)+host",
        "B_time": "même code, toutes les clés vidées : floor(t,15min) seule",
    },
    "unit_of_metric": "paires d'événements anomaux (vérité = même incident vrai)",
    "ci_methods": {
        "seed_level": "IC 95 % de Student sur la moyenne des 20 graines (graines = corpus indépendants)",
        "seed_bootstrap": "IC 95 % percentile, bootstrap des graines (B=5000, rng=12345) sur la métrique agrégée",
        "clopper_pearson_pairs": "IC exact sur paires agrégées, INDICATIF : les paires ne sont pas indépendantes",
    },
    "interpretation_ceiling": "Corpus synthétique construit par l'auteur ; ne valide pas une performance SOC réelle.",
}

TYPES = {
    "auth_bruteforce": {"source": "auth.log", "category": "AUTHENTICATION", "subcategory": "LOGIN_FAILURE", "proto": "", "port": None, "user": True},
    "network_scan": {"source": "netflow", "category": "NETWORK", "subcategory": "SCAN", "proto": "TCP", "port": "scan", "user": False},
    "authz_denied": {"source": "audit", "category": "AUTHORIZATION", "subcategory": "DENIED", "proto": "TCP", "port": "db", "user": True},
    "process_spawn": {"source": "sysmon", "category": "PROCESS", "subcategory": "SPAWN", "proto": "", "port": None, "user": True},
}
CHAIN = [("auth.log", "AUTHENTICATION", "LOGIN_FAILURE"), ("auth.log", "AUTHENTICATION", "LOGIN_SUCCESS"), ("sysmon", "PROCESS", "SPAWN")]


def iso(ts: datetime) -> str:
    return ts.strftime("%Y-%m-%dT%H:%M:%SZ")


def generate(seed: int, p_multistage: float, gap_mean_min: float = 3.0) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    g = PROTOCOL["generator"]
    rng = np.random.default_rng(seed)
    start = datetime(2026, 1, 15, tzinfo=timezone.utc)
    horizon = g["horizon_hours"] * 3600
    users = [f"user{i}" for i in range(g["user_pool"])]
    events: list[dict] = []
    truth: list[dict] = []
    n_multistage = 0

    def add(row: dict, incident: str, anomalous: bool) -> None:
        eid = f"E{len(events) + 1:05d}"
        events.append({
            "timestamp_iso": row["timestamp_iso"], "is_anomaly": "1" if anomalous else "0", "event": eid,
            "host": row["host"], "user": row["user"], "source": row["source"], "category": row["category"],
            "subcategory": row["subcategory"], "proto": row["proto"], "dst_port": row["dst_port"],
            "severity": "WARNING" if anomalous else "INFO", "anomaly_score": "-0.10" if anomalous else "0.10",
            "anomaly_rank": str(len(events) + 1),
        })
        if anomalous:
            truth.append({"event": eid, "true_incident": incident})

    type_names = list(TYPES)
    for k in range(g["n_incidents"]):
        inc = f"GT-{k:03d}"
        t0 = start + timedelta(seconds=int(rng.integers(0, horizon)))
        n_ev = int(min(1 + rng.poisson(3), 10))
        multistage = rng.random() < p_multistage
        if multistage:
            n_multistage += 1
            host = f"host-ms-{int(rng.integers(0, g['host_pool_per_type']))}"
            user = users[int(rng.integers(0, len(users)))]
            n_ev = max(n_ev, 3)
            stages = sorted(rng.integers(0, 3, size=n_ev).tolist())
            stages[0], stages[-1] = 0, 2
            stages = sorted(stages)
            ts = t0
            for stage in stages:
                src, cat, sub = CHAIN[stage]
                add({"timestamp_iso": iso(ts), "host": host, "user": user, "source": src, "category": cat,
                     "subcategory": sub, "proto": "", "dst_port": ""}, inc, True)
                ts += timedelta(seconds=int(round(rng.exponential(gap_mean_min) * 60)))
            continue
        tname = type_names[int(rng.integers(0, len(type_names)))]
        spec = TYPES[tname]
        host = f"host-{tname[:4]}-{int(rng.integers(0, g['host_pool_per_type']))}"
        user = users[int(rng.integers(0, len(users)))] if spec["user"] else ""
        if spec["port"] == "scan":
            port = str(g["scan_ports"][int(rng.integers(0, len(g["scan_ports"])))])
        elif spec["port"] == "db":
            port = str(g["db_ports"][int(rng.integers(0, len(g["db_ports"])))])
        else:
            port = ""
        ts = t0
        for _ in range(n_ev):
            add({"timestamp_iso": iso(ts), "host": host, "user": user, "source": spec["source"], "category": spec["category"],
                 "subcategory": spec["subcategory"], "proto": spec["proto"], "dst_port": port}, inc, True)
            ts += timedelta(seconds=int(round(rng.exponential(gap_mean_min) * 60)))

    def random_keys() -> dict:
        tname = type_names[int(rng.integers(0, len(type_names)))]
        spec = TYPES[tname]
        return {"host": f"host-{tname[:4]}-{int(rng.integers(0, g['host_pool_per_type']))}",
                "user": users[int(rng.integers(0, len(users)))] if spec["user"] else "",
                "source": spec["source"], "category": spec["category"], "subcategory": spec["subcategory"],
                "proto": spec["proto"], "dst_port": str(g["scan_ports"][0]) if spec["port"] == "scan" else ("5432" if spec["port"] == "db" else "")}

    for k in range(g["n_isolated_anomalies"]):
        row = random_keys()
        row["timestamp_iso"] = iso(start + timedelta(seconds=int(rng.integers(0, horizon))))
        add(row, f"ISO-{k:03d}", True)
    for _ in range(g["n_noise_non_anomalous"]):
        row = random_keys()
        row["subcategory"] = "BENIGN"
        row["timestamp_iso"] = iso(start + timedelta(seconds=int(rng.integers(0, horizon))))
        add(row, "", False)

    frame = pd.DataFrame(events).sort_values("timestamp_iso", kind="stable").reset_index(drop=True)
    meta = {"n_events": len(frame), "n_anomalous": len(truth), "n_multistage_incidents": n_multistage}
    return frame, pd.DataFrame(truth), meta


def blank(frame: pd.DataFrame, keep: list[str]) -> pd.DataFrame:
    out = frame.copy()
    for col in KEY_COLUMNS:
        if col not in keep:
            out[col] = ""
    return out


METHOD_KEEP = {"M_keys": KEY_COLUMNS, "B_host_time": ["host"], "B_time": []}


def run_method(frame: pd.DataFrame, keep: list[str], workdir: Path, tag: str, window: int) -> tuple[dict[str, str], int]:
    inp = workdir / f"{tag}_in.csv"
    out = workdir / f"{tag}_inc.csv"
    blank(frame, keep).to_csv(inp, sep=";", index=False, encoding="utf-8-sig")
    correlate_anomalies(inp, out, sep=";", window_minutes=window, parallel_workers=1)
    inc = pd.read_csv(out, sep=";", dtype=str, keep_default_na=False)
    pred: dict[str, str] = {}
    truncated = 0
    by_key: dict[tuple, str] = {}
    for row in inc.itertuples(index=False):
        ids = [v for v in str(row.events).split(",") if v]
        if int(row.event_count) != len(ids):
            truncated += 1
        for eid in ids:
            pred[eid] = str(row.incident_id)
        window_start = pd.Timestamp(row.start_time).floor(f"{window}min")
        by_key[(window_start, row.host, row.user, row.source, row.category, row.subcategory, row.proto, row.dst_port)] = str(row.incident_id)
    if truncated:
        # La sortie du corrélateur tronque la liste d'événements à 20 ; on retrouve
        # l'appartenance des événements manquants via la clé de groupe publiée.
        anomalies = frame[frame["is_anomaly"] == "1"]
        blanked = blank(anomalies, keep)
        for r in blanked.itertuples(index=False):
            if r.event in pred:
                continue
            key = (pd.Timestamp(r.timestamp_iso).floor(f"{window}min"), r.host or "UNKNOWN", r.user, r.source or "UNKNOWN",
                   r.category or "UNKNOWN", r.subcategory or "UNKNOWN", r.proto, r.dst_port)
            pred[r.event] = by_key[key]
    return pred, truncated


def pair_metrics(truth: pd.DataFrame, pred: dict[str, str]) -> dict:
    true_map = dict(zip(truth["event"], truth["true_incident"]))
    missing = set(true_map) - set(pred)
    if missing:
        raise RuntimeError(f"{len(missing)} événements anomaux absents de la sortie (troncature events[:20] ?)")
    ids = sorted(true_map)
    tv = np.array([true_map[i] for i in ids])
    pv = np.array([pred[i] for i in ids])
    # Comptage vectorisé par paires via tables de contingence.
    tp = 0
    ct = pd.crosstab(tv, pv)
    tp = int((ct.values * (ct.values - 1) // 2).sum())
    true_same = int(sum(c * (c - 1) // 2 for c in pd.Series(tv).value_counts().values))
    pred_same = int(sum(c * (c - 1) // 2 for c in pd.Series(pv).value_counts().values))
    n = len(ids)
    total = n * (n - 1) // 2
    fp = pred_same - tp
    fn = true_same - tp
    tn = total - tp - fp - fn
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn) if tp + fn else float("nan")
    f1 = 2 * p * r / (p + r) if (tp + fp) and (tp + fn) and (p + r) else float("nan")
    t2p: dict[str, set] = {}
    p2t: dict[str, set] = {}
    for a, b in zip(tv, pv):
        t2p.setdefault(a, set()).add(b)
        p2t.setdefault(b, set()).add(a)
    return {"pairs_total": total, "TP": tp, "FP": fp, "FN": fn, "TN": tn, "precision": p, "recall": r, "f1": f1,
            "true_incidents": len(t2p), "pred_incidents": len(p2t),
            "fragmented_true": sum(len(s) > 1 for s in t2p.values()),
            "fused_pred": sum(len(s) > 1 for s in p2t.values())}


def cp(k: int, n: int, alpha: float = 0.05) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [lo, hi]


def t_ci(values: np.ndarray) -> list[float]:
    values = values[~np.isnan(values)]
    m, s, n = values.mean(), values.std(ddof=1), len(values)
    h = float(student_t.ppf(0.975, n - 1)) * s / np.sqrt(n)
    return [float(m - h), float(m + h)]


def pooled(rows: list[dict]) -> dict:
    tp = sum(r["TP"] for r in rows); fp = sum(r["FP"] for r in rows); fn = sum(r["FN"] for r in rows)
    p = tp / (tp + fp) if tp + fp else float("nan"); r = tp / (tp + fn) if tp + fn else float("nan")
    return {"TP": tp, "FP": fp, "FN": fn, "precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else float("nan")}


def seed_bootstrap(rows: list[dict], key: str, b: int = 5000) -> list[float]:
    rng = np.random.default_rng(12345)
    vals = []
    for _ in range(b):
        sample = [rows[i] for i in rng.integers(0, len(rows), len(rows))]
        vals.append(pooled(sample)[key])
    return [float(np.nanpercentile(vals, 2.5)), float(np.nanpercentile(vals, 97.5))]


def main() -> int:
    run_id = "agent5_correlation_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = OUT_ROOT / run_id
    out.mkdir(parents=True, exist_ok=True)
    (out / "protocol.json").write_text(json.dumps({"run_id": run_id, **PROTOCOL}, ensure_ascii=False, indent=2), encoding="utf-8")
    window = PROTOCOL["window_minutes"]
    work = Path(tempfile.mkdtemp(prefix="agent5_corr_"))
    rows: list[dict] = []
    total_truncated = 0
    try:
        # 1) Corpus d'origine (19 événements) : M_keys reproduit, baselines ajoutées.
        orig = pd.read_csv(ORIGINAL_INPUT, sep=";", dtype=str, keep_default_na=False)
        orig_truth = pd.read_csv(ORIGINAL_TRUTH, sep=";", dtype=str, keep_default_na=False)
        original_results = {}
        for method, keep in METHOD_KEEP.items():
            pred, trunc = run_method(orig, keep, work, f"orig_{method}", window)
            m = pair_metrics(orig_truth, pred)
            m["precision_cp95_indicatif"] = cp(m["TP"], m["TP"] + m["FP"])
            m["recall_cp95_indicatif"] = cp(m["TP"], m["TP"] + m["FN"])
            original_results[method] = m
        # 2) Corpus agrandi.
        for scen, sp in PROTOCOL["scenarios"].items():
            for seed in PROTOCOL["seeds"]:
                frame, truth, meta = generate(seed, sp["p_multistage"])
                if seed == 0:
                    frame.to_csv(out / f"example_input_{scen}_seed0.csv", sep=";", index=False, encoding="utf-8-sig")
                    truth.to_csv(out / f"example_truth_{scen}_seed0.csv", sep=";", index=False, encoding="utf-8-sig")
                for method, keep in METHOD_KEEP.items():
                    pred, trunc = run_method(frame, keep, work, f"{scen}_{seed}_{method}", window)
                    total_truncated += trunc
                    rows.append({"scenario": scen, "seed": seed, "method": method, **meta, "truncated_groups": trunc, "status": "OK", **pair_metrics(truth, pred)})
    finally:
        shutil.rmtree(work, ignore_errors=True)

    per_seed = pd.DataFrame(rows)
    per_seed.to_csv(out / "per_seed_metrics.csv", index=False, encoding="utf-8")
    aggregate: dict = {}
    for scen in PROTOCOL["scenarios"]:
        aggregate[scen] = {}
        for method in METHOD_KEEP:
            sub = [r for r in rows if r["scenario"] == scen and r["method"] == method and r["status"] == "OK"]
            if not sub:
                aggregate[scen][method] = {"status": "NO_VALID_SEED"}
                continue
            pool = pooled(sub)
            entry = {
                "n_seeds_ok": len(sub),
                "pooled": pool,
                "pooled_precision_cp95_indicatif": cp(pool["TP"], pool["TP"] + pool["FP"]),
                "pooled_recall_cp95_indicatif": cp(pool["TP"], pool["TP"] + pool["FN"]),
                "seed_bootstrap95": {k: seed_bootstrap(sub, k) for k in ("precision", "recall", "f1")},
            }
            for k in ("precision", "recall", "f1", "fragmented_true", "fused_pred", "true_incidents", "pred_incidents"):
                v = np.array([r[k] for r in sub], dtype=float)
                entry[f"{k}_mean"] = float(np.nanmean(v))
                entry[f"{k}_sd"] = float(np.nanstd(v, ddof=1))
                entry[f"{k}_min"] = float(np.nanmin(v))
                entry[f"{k}_max"] = float(np.nanmax(v))
                if k in ("precision", "recall", "f1"):
                    entry[f"{k}_t95_mean"] = t_ci(v)
            aggregate[scen][method] = entry
        # Différence appariée F1 (M_keys - baseline) par graine.
        for base in ("B_time", "B_host_time"):
            a = {r["seed"]: r["f1"] for r in rows if r["scenario"] == scen and r["method"] == "M_keys" and r["status"] == "OK"}
            b = {r["seed"]: r["f1"] for r in rows if r["scenario"] == scen and r["method"] == base and r["status"] == "OK"}
            common = sorted(set(a) & set(b))
            d = np.array([a[s] - b[s] for s in common])
            aggregate[scen][f"paired_f1_diff_M_keys_minus_{base}"] = {
                "n": len(common), "mean": float(d.mean()), "t95": t_ci(d),
                "n_seeds_M_keys_better": int((d > 0).sum()), "n_ties": int((d == 0).sum()), "n_seeds_baseline_better": int((d < 0).sum()),
            }
    result = {
        "run_id": run_id, "status": "COMPLETED", "completed_at": datetime.now(timezone.utc).isoformat(),
        "protocol_path": str((out / "protocol.json").relative_to(ROOT)).replace("\\", "/"),
        "inputs": {"original_input": str(ORIGINAL_INPUT.relative_to(ROOT)).replace("\\", "/"),
                   "original_truth": str(ORIGINAL_TRUTH.relative_to(ROOT)).replace("\\", "/"),
                   "original_reference_run": "e8_correlation_synthetic_controlled (data/processed/final_experiments_2026/correlation_synthetic_summary.json)"},
        "observation_code": "correlator._incident_row tronque la colonne events à 20 identifiants ; groupes tronqués détectés = " + str(total_truncated),
        "original_corpus": original_results,
        "extended_corpus": aggregate,
        "per_seed_csv": str((out / "per_seed_metrics.csv").relative_to(ROOT)).replace("\\", "/"),
    }
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"run_id": run_id, "truncated": total_truncated}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
