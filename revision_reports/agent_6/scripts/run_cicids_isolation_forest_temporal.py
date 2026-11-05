#!/usr/bin/env python3
"""Agent 6 -- Isolation Forest non supervise sur CICIDS2017, protocole temporel.

Reutilise les pools figes du run ``cicids_temporal_20260910T083015Z``
(lundi--jeudi pour l'apprentissage, vendredi pour le test) sans relire les CSV
bruts. Le test de chaque graine est tire avec la meme fonction et la meme graine
que la campagne LR/RF (``seed_sample``, 10 000 par classe), ce qui rend les
tests identiques a ceux de la campagne supervisee.

Protocole :
- ajustement : 10 000 flux BENIGN de lundi--jeudi uniquement (aucun label
  d'attaque n'est vu pendant l'ajustement) ;
- validation (lundi--jeudi, disjointe de l'ajustement) : 5 000 BENIGN +
  5 000 attaques ;
- deux regles de seuil, toutes deux fixees sur validation, jamais sur test :
  (a) ``benign_q99`` : quantile 99 % des scores des BENIGN de validation
      (ne requiert que des donnees normales ; FPR cible ~1 %) ;
  (b) ``val_maxf1`` : seuil maximisant le F1 de validation (calibration
      semi-supervisee utilisant les attaques de lundi--jeudi) ;
- graines 42 a 46.

Calculs bornes : n_jobs=2, ~120 000 lignes en memoire.
"""

from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from dataset_strengthening_common import (  # noqa: E402
    binary_metrics,
    descriptive,
    select_threshold,
    sha256_file,
)

SOURCE_RUN = "cicids_temporal_20260910T083015Z"
PROCESSED = ROOT / "experiments/phase_dataset_strengthening/processed"
TRAIN_POOL = PROCESSED / f"{SOURCE_RUN}_train_pool.csv.gz"
TEST_POOL = PROCESSED / f"{SOURCE_RUN}_test_pool.csv.gz"
SUP_METRICS = ROOT / f"experiments/phase_dataset_strengthening/raw/{SOURCE_RUN}_metrics.csv"
OUT = ROOT / "revision_reports/agent_6/artifacts"
META = {"target", "__source_file", "__source_row", "__priority"}
SEEDS = [42, 43, 44, 45, 46]


def seed_sample(pool: pd.DataFrame, *, per_class: int, seed: int) -> pd.DataFrame:
    """Copie conforme de scripts/run_cicids_temporal_strengthening.py::seed_sample."""
    parts = []
    for target in (0, 1):
        group = pool.loc[pool["target"] == target]
        parts.append(group.sample(n=min(per_class, len(group)), replace=False, random_state=seed + target))
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


def main() -> int:
    run_id = "agent6_cicids_iforest_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    train_pool = pd.read_csv(TRAIN_POOL)
    test_pool = pd.read_csv(TEST_POOL)
    features = [c for c in train_pool.columns if c not in META]
    assert len(features) == 78, len(features)
    sup = pd.read_csv(SUP_METRICS, encoding="utf-8-sig")

    rows: list[dict] = []
    per_source: list[dict] = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        benign = train_pool.loc[train_pool["target"] == 0].reset_index(drop=True)
        attacks = train_pool.loc[train_pool["target"] == 1].reset_index(drop=True)
        perm = rng.permutation(len(benign))
        fit_df = benign.iloc[perm[:10_000]]
        val_benign = benign.iloc[perm[10_000:15_000]]
        val_attack = attacks.iloc[rng.permutation(len(attacks))[:5_000]]
        val_df = pd.concat([val_benign, val_attack], ignore_index=True)
        assert set(fit_df["__source_file"] + ":" + fit_df["__source_row"].astype(str)).isdisjoint(
            set(val_df["__source_file"] + ":" + val_df["__source_row"].astype(str))
        )
        test_df = seed_sample(test_pool, per_class=10_000, seed=seed)

        model = IsolationForest(n_estimators=200, max_samples=256, contamination="auto", random_state=seed, n_jobs=2)
        t0 = perf_counter()
        model.fit(fit_df[features].to_numpy(dtype=np.float64))
        fit_time = perf_counter() - t0
        val_scores = -model.score_samples(val_df[features].to_numpy(dtype=np.float64))
        t0 = perf_counter()
        test_scores = -model.score_samples(test_df[features].to_numpy(dtype=np.float64))
        test_time = perf_counter() - t0
        y_val = val_df["target"].to_numpy(dtype=np.int8)
        y_test = test_df["target"].to_numpy(dtype=np.int8)

        thresholds = {
            "benign_q99": float(np.quantile(val_scores[y_val == 0], 0.99)),
            "val_maxf1": float(select_threshold(y_val, val_scores)[0]),
        }
        for rule, thr in thresholds.items():
            val_m = binary_metrics(y_val, val_scores, thr)
            test_m = binary_metrics(y_test, test_scores, thr)
            rows.append(
                {
                    "run_id": run_id,
                    "dataset": "CICIDS2017",
                    "protocol": "temporal_holdout_MonThu_fit_benign_only__Fri_test",
                    "model": "IsolationForest",
                    "threshold_rule": rule,
                    "seed": seed,
                    "fit_rows_benign": len(fit_df),
                    "val_rows": len(val_df),
                    "test_rows": len(test_df),
                    "val_f1": val_m["f1"],
                    "val_fpr": val_m["fpr"],
                    **{f"test_{k}": v for k, v in test_m.items()},
                    "test_roc_auc": float(roc_auc_score(y_test, test_scores)),
                    "fit_time_sec": fit_time,
                    "test_time_sec": test_time,
                }
            )
            pred = test_scores >= thr
            for src, grp in test_df.assign(pred=pred).groupby("__source_file"):
                pos = grp["target"] == 1
                neg = ~pos
                per_source.append(
                    {
                        "run_id": run_id, "seed": seed, "threshold_rule": rule, "source_file": src,
                        "n_attack": int(pos.sum()), "attack_recall": float(grp.loc[pos, "pred"].mean()) if pos.any() else float("nan"),
                        "n_benign": int(neg.sum()), "benign_fpr": float(grp.loc[neg, "pred"].mean()) if neg.any() else float("nan"),
                    }
                )
        print(f"seed {seed} done: roc_auc={rows[-1]['test_roc_auc']:.4f}", flush=True)

    frame = pd.DataFrame(rows)
    summary = []
    for rule, grp in frame.groupby("threshold_rule"):
        rec = {"run_id": run_id, "model": "IsolationForest", "threshold_rule": rule, "seeds": ",".join(map(str, SEEDS))}
        for m in ("test_precision", "test_recall", "test_f1", "test_pr_auc", "test_roc_auc", "test_mcc", "test_fpr", "val_f1", "val_fpr"):
            for k, v in descriptive(grp[m]).items():
                rec[f"{m}_{k}"] = v
        summary.append(rec)
    # Reference supervisee, meme test (meme seed_sample), lue depuis l'artefact existant.
    for model, grp in sup.groupby("model"):
        rec = {"run_id": SOURCE_RUN, "model": model, "threshold_rule": "predict_default(supervised)", "seeds": ",".join(map(str, sorted(grp["seed"])))}
        for src, dst in (("precision", "test_precision"), ("recall", "test_recall"), ("f1", "test_f1"), ("pr_auc", "test_pr_auc"), ("mcc", "test_mcc"), ("fpr", "test_fpr")):
            for k, v in descriptive(grp[src]).items():
                rec[f"{dst}_{k}"] = v
        summary.append(rec)

    frame.to_csv(OUT / f"{run_id}_metrics.csv", index=False, encoding="utf-8")
    pd.DataFrame(summary).to_csv(OUT / f"{run_id}_summary.csv", index=False, encoding="utf-8")
    ps = pd.DataFrame(per_source)
    ps.to_csv(OUT / f"{run_id}_per_source.csv", index=False, encoding="utf-8")
    manifest = {
        "run_id": run_id,
        "started_at": started,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "script": "revision_reports/agent_6/scripts/run_cicids_isolation_forest_temporal.py",
        "source_run": SOURCE_RUN,
        "inputs": {
            str(p.relative_to(ROOT).as_posix()): sha256_file(p) for p in (TRAIN_POOL, TEST_POOL, SUP_METRICS)
        },
        "protocol": {
            "fit": "10000 BENIGN flows Mon-Thu, no attack label used",
            "validation": "5000 BENIGN + 5000 attacks Mon-Thu, disjoint from fit",
            "test": "Friday, seed_sample(per_class=10000, seed) identical to supervised LR/RF run",
            "threshold_rules": {"benign_q99": "99th percentile of validation BENIGN scores", "val_maxf1": "argmax F1 on validation (tie-break lower FPR)"},
            "model": "IsolationForest(n_estimators=200, max_samples=256, n_jobs=2), score=-score_samples",
            "features": 78,
            "seeds": SEEDS,
        },
        "environment": {"python": platform.python_version(), "sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__},
        "caveat": "Test balanced 50/50 (prevalence non realiste pour la detection d'anomalies); attaques du vendredi (DDoS, PortScan, Bot) absentes de lundi-jeudi.",
    }
    (OUT / f"{run_id}_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"COMPLETED {run_id}")
    print(pd.DataFrame(summary)[["model", "threshold_rule", "test_f1_mean", "test_f1_sample_std", "test_recall_mean", "test_fpr_mean", "test_pr_auc_mean"]].to_string())
    print(ps.groupby(["threshold_rule", "source_file"])[["attack_recall", "benign_fpr"]].mean().to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
