"""Agent 4 -- CSE-CIC-IDS2018 : prevalence realiste, raccourci Dst Port, echec du Random Forest.

Partie 1 (reglage publie) : relit les pools figes du run external_csecicids2018_20260910T230136Z,
reproduit l'echantillonnage equilibre (seed_sample) et les deux modeles (memes hyperparametres),
verifie la reproduction des F1 publies, puis ajoute : ablation sans Dst Port, Dst Port seul,
importances RF, rappel par famille d'attaque (Dst Port 21 = SlowHTTPTest, 80 = Hulk dans le
fichier du 16 fevrier ; correspondance verifiee sur le fichier complet) et regles sans
apprentissage sur Dst Port.

Partie 2 (prevalence observee) : echantillon de Bernoulli uniforme, independant du label, de
chaque journee complete (taux 0,15, graine fixe). Train a prevalence naturelle (class_weight
balanced comme le protocole publie), test a prevalence naturelle de la journee de test.
Directions : 15->16 (principale), 16->15 (inverse), intra-15 et intra-16 (split aleatoire 50/50).
Jeux de variables : ALL (78), NO_DST_PORT (77), DST_PORT_ONLY (1). Seuil fixe 0,5. Graines 42-46.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, matthews_corrcoef
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "revision_reports" / "agent_4" / "artifacts" / "csecic"
OUT.mkdir(parents=True, exist_ok=True)
RAW_DIR = ROOT / "data" / "raw" / "external" / "CSE-CIC-IDS2018"
DAYS = {"2018-02-15": RAW_DIR / "Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv",
        "2018-02-16": RAW_DIR / "Friday-16-02-2018_TrafficForML_CICFlowMeter.csv"}
PUB_RUN = "external_csecicids2018_20260910T230136Z"
PUB_DIR = ROOT / "experiments" / "phase_dataset_strengthening"
SEEDS = (42, 43, 44, 45, 46)
META = {"target", "__source_row", "__priority"}
RUN_ID = "agent4_csecic_shortcut_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BERNOULLI_RATE = 0.15
TRAIN_ROWS = 50000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def models(seed: int) -> dict:
    return {
        "RandomForest": RandomForestClassifier(n_estimators=120, max_depth=28, min_samples_leaf=2,
                                               class_weight="balanced", random_state=seed, n_jobs=2),
        "LogisticRegression": Pipeline([("scale", StandardScaler()),
                                        ("model", LogisticRegression(max_iter=1000, class_weight="balanced",
                                                                     solver="lbfgs", random_state=seed))]),
    }


def metrics(y: np.ndarray, pred: np.ndarray, score: np.ndarray | None) -> dict:
    tp = int(((y == 1) & (pred == 1)).sum()); fp = int(((y == 0) & (pred == 1)).sum())
    fn = int(((y == 1) & (pred == 0)).sum()); tn = int(((y == 0) & (pred == 0)).sum())
    p = tp / (tp + fp) if tp + fp else 0.0; r = tp / (tp + fn) if tp + fn else 0.0
    return {"n": int(len(y)), "prevalence": float(y.mean()), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0,
            "fpr": fp / (fp + tn) if fp + tn else 0.0,
            "mcc": float(matthews_corrcoef(y, pred)) if len(np.unique(pred)) > 1 or True else 0.0,
            "pr_auc": float(average_precision_score(y, score)) if score is not None and len(np.unique(y)) > 1 else None}


def seed_sample(pool: pd.DataFrame, per_class: int, seed: int) -> pd.DataFrame:
    # identique a scripts/run_external_csecicids2018_strengthening.py::seed_sample
    parts = [pool.loc[pool["target"] == t].sample(n=min(per_class, int((pool["target"] == t).sum())),
                                                   replace=False, random_state=seed + t) for t in (0, 1)]
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


def feature_sets(columns: list[str]) -> dict[str, list[str]]:
    return {"ALL": columns, "NO_DST_PORT": [c for c in columns if c != "Dst Port"], "DST_PORT_ONLY": ["Dst Port"]}


def fit_eval(name: str, model, xtr, ytr, xte, yte, extra: dict) -> tuple[dict, object]:
    t = time.perf_counter()
    model.fit(xtr, ytr)
    score = model.predict_proba(xte)[:, 1]
    pred = (score >= 0.5).astype(int)
    row = {"model": name, **extra, **metrics(yte, pred, score), "fit_predict_sec": time.perf_counter() - t}
    return row, (model, pred, score)


def part1() -> dict:
    train_pool = pd.read_csv(PUB_DIR / "processed" / f"{PUB_RUN}_train_pool.csv.gz")
    test_pool = pd.read_csv(PUB_DIR / "processed" / f"{PUB_RUN}_test_pool.csv.gz")
    columns = [c for c in train_pool.columns if c not in META]
    published = pd.read_csv(PUB_DIR / "raw" / f"{PUB_RUN}_metrics.csv")
    rows, importances, family_rows = [], [], []
    for seed in SEEDS:
        tr = seed_sample(train_pool, 10000, seed); te = seed_sample(test_pool, 10000, seed)
        ytr = tr["target"].to_numpy(); yte = te["target"].to_numpy()
        port = te["Dst Port"].to_numpy()
        for fs_name, cols in feature_sets(columns).items():
            for mname, model in models(seed).items():
                row, (fitted, pred, score) = fit_eval(mname, model, tr[cols], ytr, te[cols], yte,
                                                      {"seed": seed, "feature_set": fs_name, "n_features": len(cols)})
                if fs_name == "ALL":
                    pub = published[(published.model == mname) & (published.seed == seed)]["f1"].iloc[0]
                    row["published_f1"] = float(pub); row["reproduces_published"] = bool(abs(pub - row["f1"]) < 1e-9)
                rows.append(row)
                for fam, mask in (("Hulk_port80", (yte == 1) & (port == 80)), ("SlowHTTPTest_port21", (yte == 1) & (port == 21)),
                                  ("Benign", yte == 0)):
                    family_rows.append({"seed": seed, "model": mname, "feature_set": fs_name, "family": fam,
                                        "n": int(mask.sum()), "predicted_attack_rate": float(pred[mask].mean()) if mask.any() else None})
                if fs_name == "ALL" and mname == "RandomForest":
                    for c, v in zip(cols, fitted.feature_importances_):
                        importances.append({"seed": seed, "model": mname, "kind": "impurity", "feature": c, "importance": float(v)})
                if fs_name == "ALL" and seed == 42:
                    sub = te.sample(n=4000, random_state=0)
                    pi = permutation_importance(fitted, sub[cols], sub["target"].to_numpy(), scoring="f1",
                                                n_repeats=3, random_state=0, n_jobs=1)
                    for c, v in zip(cols, pi.importances_mean):
                        importances.append({"seed": seed, "model": mname, "kind": "permutation_f1_test_balanced_4000",
                                            "feature": c, "importance": float(v)})
                if fs_name == "ALL" and seed == 42 and mname == "LogisticRegression":
                    pass
        # regles sans apprentissage (seuil fixe a priori, non appris sur le test)
        for rule, pred in (("rule_dst_port_lt_1024", (port < 1024).astype(int)),
                           ("rule_dst_port_in_train_attack_ports", np.isin(port, np.unique(tr.loc[tr.target == 1, "Dst Port"])).astype(int))):
            rows.append({"model": rule, "seed": seed, "feature_set": "DST_PORT_RULE", "n_features": 1, **metrics(yte, pred, None)})
        # descriptif du shift sur Dst Port dans les pools equilibres
    port_desc = {}
    for nm, pool in (("train_2018-02-15", train_pool), ("test_2018-02-16", test_pool)):
        for t in (0, 1):
            p = pool.loc[pool.target == t, "Dst Port"]
            port_desc[f"{nm}|target={t}"] = {"n": int(len(p)), "share_lt_1024": float((p < 1024).mean()),
                                             "top_ports": {str(int(k)): int(v) for k, v in p.value_counts().head(6).items()}}
    return {"rows": rows, "importances": importances, "families": family_rows, "dst_port_pool_description": port_desc}


def bernoulli_day(path: Path, seed: int) -> tuple[pd.DataFrame, dict]:
    rng = np.random.default_rng(seed)
    kept, labels_all, scanned, headers = [], {}, 0, 0
    for chunk in pd.read_csv(path, chunksize=20000, low_memory=False):
        chunk.columns = [str(c).strip() for c in chunk.columns]
        lab = chunk["Label"].astype(str).str.strip()
        hdr = lab.eq("Label"); headers += int(hdr.sum())
        chunk = chunk.loc[~hdr]; lab = lab.loc[~hdr]
        scanned += len(chunk)
        for k, v in lab.value_counts().items():
            labels_all[k] = labels_all.get(k, 0) + int(v)
        mask = rng.random(len(chunk)) < BERNOULLI_RATE
        sub = chunk.loc[mask].drop(columns=[c for c in ("Timestamp", "Flow ID", "Src IP", "Dst IP", "Source IP", "Destination IP") if c in chunk.columns])
        lab_sub = sub.pop("Label").astype(str).str.strip()
        num = sub.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0).clip(-1e12, 1e12).astype("float32")
        num["label_name"] = lab_sub.to_numpy()
        num["target"] = (lab_sub.str.upper() != "BENIGN").astype(np.int8).to_numpy()
        kept.append(num)
    frame = pd.concat(kept, ignore_index=True)
    return frame, {"rows_scanned": scanned, "repeated_header_rows": headers, "label_counts_full_file": labels_all,
                   "sample_rows": int(len(frame)), "sample_prevalence": float(frame.target.mean()),
                   "full_file_prevalence": float(1 - labels_all.get("Benign", 0) / scanned)}


def part2() -> dict:
    days, audit = {}, {}
    for i, (day, path) in enumerate(DAYS.items()):
        days[day], audit[day] = bernoulli_day(path, 7000 + i)
    columns = [c for c in days["2018-02-15"].columns if c not in ("label_name", "target")]
    assert columns == [c for c in days["2018-02-16"].columns if c not in ("label_name", "target")]
    rows, fam_rows = [], []
    directions = {"15_to_16": ("2018-02-15", "2018-02-16"), "16_to_15": ("2018-02-16", "2018-02-15"),
                  "intra_15": ("2018-02-15", "2018-02-15"), "intra_16": ("2018-02-16", "2018-02-16")}
    for direction, (dtr, dte) in directions.items():
        for seed in SEEDS:
            if dtr == dte:
                perm = np.random.default_rng(seed).permutation(len(days[dtr]))
                half = len(perm) // 2
                tr_pool, te = days[dtr].iloc[perm[:half]], days[dtr].iloc[perm[half:]]
            else:
                tr_pool, te = days[dtr], days[dte]
            tr = tr_pool.sample(n=min(TRAIN_ROWS, len(tr_pool)), random_state=seed, replace=False)
            ytr, yte = tr["target"].to_numpy(), te["target"].to_numpy()
            port = te["Dst Port"].to_numpy()
            for fs_name, cols in feature_sets(columns).items():
                for mname, model in models(seed).items():
                    if direction != "15_to_16" and fs_name == "DST_PORT_ONLY" and mname == "RandomForest":
                        continue
                    row, (_, pred, _) = fit_eval(mname, model, tr[cols], ytr, te[cols], yte,
                                                 {"direction": direction, "seed": seed, "feature_set": fs_name,
                                                  "n_features": len(cols), "train_rows": len(tr),
                                                  "train_prevalence": float(ytr.mean())})
                    rows.append(row)
                    for fam in sorted(te["label_name"].unique()):
                        m = te["label_name"].to_numpy() == fam
                        fam_rows.append({"direction": direction, "seed": seed, "model": mname, "feature_set": fs_name,
                                         "family": fam, "n": int(m.sum()), "predicted_attack_rate": float(pred[m].mean())})
            for rule, pred in (("rule_dst_port_lt_1024", (port < 1024).astype(int)),):
                rows.append({"model": rule, "direction": direction, "seed": seed, "feature_set": "DST_PORT_RULE",
                             "n_features": 1, "train_rows": 0, **metrics(yte, pred, None)})
            print("part2", direction, seed, flush=True)
    port_desc = {}
    for day, fr in days.items():
        for fam, g in fr.groupby("label_name"):
            port_desc[f"{day}|{fam}"] = {"n_sample": int(len(g)), "share_dst_port_lt_1024": float((g["Dst Port"] < 1024).mean()),
                                        "top_ports": {str(int(k)): int(v) for k, v in g["Dst Port"].value_counts().head(6).items()}}
    return {"rows": rows, "families": fam_rows, "audit": audit, "dst_port_by_family_sample": port_desc}


def summarise(rows: list[dict], keys: list[str]) -> list[dict]:
    fr = pd.DataFrame(rows)
    out = []
    for k, g in fr.groupby(keys, sort=False):
        d = dict(zip(keys, k if isinstance(k, tuple) else (k,)))
        for m in ("f1", "precision", "recall", "fpr", "mcc", "pr_auc", "prevalence"):
            vals = pd.to_numeric(g[m], errors="coerce").dropna()
            d[f"{m}_mean"] = float(vals.mean()) if len(vals) else None
            d[f"{m}_min"] = float(vals.min()) if len(vals) else None
            d[f"{m}_max"] = float(vals.max()) if len(vals) else None
        d["n_seeds"] = int(len(g))
        out.append(d)
    return out


def main() -> None:
    t0 = time.perf_counter()
    p1 = part1()
    print("part1 done", time.perf_counter() - t0, flush=True)
    p2 = part2()
    files = {}
    for name, rows in (("part1_published_setting_rows", p1["rows"]), ("part1_importances", p1["importances"]),
                       ("part1_family_rates", p1["families"]), ("part2_observed_prevalence_rows", p2["rows"]),
                       ("part2_family_rates", p2["families"])):
        path = OUT / f"{RUN_ID}__{name}.csv"
        pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8")
        files[name] = str(path.relative_to(ROOT)).replace("\\", "/")
    s1 = summarise(p1["rows"], ["model", "feature_set"])
    s2 = summarise(p2["rows"], ["direction", "model", "feature_set"])
    imp = pd.DataFrame(p1["importances"]).groupby(["model", "kind", "feature"])["importance"].mean().reset_index()
    top_imp = {f"{m}|{k}": g.sort_values("importance", ascending=False).head(10)[["feature", "importance"]].to_dict("records")
               for (m, k), g in imp.groupby(["model", "kind"])}
    fam1 = pd.DataFrame(p1["families"]).groupby(["model", "feature_set", "family"])["predicted_attack_rate"].agg(["mean", "min", "max"]).reset_index().to_dict("records")
    fam2 = pd.DataFrame(p2["families"]).groupby(["direction", "model", "feature_set", "family"])["predicted_attack_rate"].agg(["mean", "min", "max"]).reset_index().to_dict("records")
    summary = {
        "run_id": RUN_ID, "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "inputs": {
            "raw_files": {d: {"path": str(p.relative_to(ROOT)).replace("\\", "/"), "bytes": p.stat().st_size, "sha256": sha256(p)} for d, p in DAYS.items()},
            "published_pools": {k: {"path": f"experiments/phase_dataset_strengthening/processed/{PUB_RUN}_{k}_pool.csv.gz",
                                    "sha256": sha256(PUB_DIR / "processed" / f"{PUB_RUN}_{k}_pool.csv.gz")} for k in ("train", "test")},
            "published_metrics": f"experiments/phase_dataset_strengthening/raw/{PUB_RUN}_metrics.csv",
        },
        "protocol": {"part1": "pools publies, 10 000/classe/graine, seed_sample identique, seuil 0,5",
                     "part2": f"Bernoulli uniforme taux {BERNOULLI_RATE} par journee (graines 7000/7001), train {TRAIN_ROWS} lignes a prevalence naturelle, test = echantillon complet de la journee de test a prevalence naturelle ; intra-jour : split aleatoire 50/50 par graine",
                     "models": "RF(120 arbres, max_depth 28, min_samples_leaf 2, class_weight balanced) ; LR(StandardScaler + lbfgs, class_weight balanced, max_iter 1000)",
                     "seeds": list(SEEDS), "threshold": 0.5, "selection_on_test": False},
        "part1_summary": s1, "part1_top_importances": top_imp, "part1_family_predicted_attack_rate": fam1,
        "part1_dst_port_pools": p1["dst_port_pool_description"],
        "part2_audit": p2["audit"], "part2_summary": s2, "part2_family_predicted_attack_rate": fam2,
        "part2_dst_port_by_family_sample": p2["dst_port_by_family_sample"],
        "artifacts": files, "elapsed_sec": time.perf_counter() - t0,
    }
    out = OUT / f"{RUN_ID}__result.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
