"""E-R3-GOVERNANCE-CYCLE : cycle complet de promotion et de rejet (exigence R3).

Pour chaque graine : un pool CICIDS2017 hors fichier DDoS est partage en
entrainement / validation figee / test independant i.i.d. ; le fichier DDoS fournit
un second test independant (scenario nouveau). Partant d'un modele actif initial,
cinq candidats fixes sont proposes successivement. Chaque decision passe par le code
reel `run_plan` de `scripts/monthly_model_retraining.py` (--promote), qui ne voit que
la validation figee. Les tests ne sont lus qu'apres chaque decision.

Usage :
  python run_e_r3_governance_cycle.py            # execution enregistree (graines du protocole)
  python run_e_r3_governance_cycle.py --trial    # essai technique, graines reservees, sortie scratch, aucune metrique affichee
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace

import joblib
import numpy as np
import pandas as pd
from scipy.stats import t as student_t
from sklearn.metrics import f1_score, matthews_corrcoef
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for extra in (ROOT / "scripts", ROOT / "src" / "logminer"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from monthly_model_retraining import _score_artifact, run_plan  # noqa: E402
from run_final_experiments import load_holdout  # noqa: E402
from train_candidate import train as train_candidate  # noqa: E402

EXPERIMENT_ID = "E-R3-GOVERNANCE-CYCLE"
SEEDS = (20261701, 20261702, 20261703, 20261704, 20261705)
TRIAL_SEEDS = (1,)
INITIAL_MODEL = "LogisticRegression"
CYCLE = ("Stump", "RandomForest", "RandomForest_small", "ExtraTrees", "HistGradientBoosting")
METRIC = "f1"
MIN_DELTA = 0.02
SPLIT = (0.6, 0.2, 0.2)  # entrainement, validation figee, test i.i.d.
OUT_DIR = ROOT / "experiments" / "phase_revision_20261112" / EXPERIMENT_ID
TOL = 1e-9


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


def write_split_csv(x: pd.DataFrame, y: pd.Series, path: Path) -> None:
    frame = x.reset_index(drop=True).copy()
    frame["label"] = y.reset_index(drop=True).to_numpy(dtype=int)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, encoding="utf-8-sig")


def score_on_csv(artifact: Path, csv_path: Path) -> dict[str, float]:
    """Evaluation independante de `evaluate_model` : meme fonction de scoring, metrique recalculee."""
    events = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    truth = events["label"].astype(int).to_numpy()
    labels, _ = _score_artifact(artifact, events.drop(columns=["label"]))
    pred = labels.to_numpy(dtype=int)
    return {
        "f1": float(f1_score(truth, pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(truth, pred)),
    }


def mean_ci(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    n = len(arr)
    mean = float(arr.mean())
    if n < 2:
        return {"n": n, "mean": mean, "low": float("nan"), "high": float("nan")}
    half = float(student_t.ppf(0.975, n - 1) * arr.std(ddof=1) / math.sqrt(n))
    return {"n": n, "mean": mean, "low": mean - half, "high": mean + half}


def run_seed(seed: int, work: Path, audit_path: Path, python_exe: str) -> list[dict[str, object]]:
    seed_dir = work / f"seed_{seed}"
    if seed_dir.exists():
        shutil.rmtree(seed_dir)
    seed_dir.mkdir(parents=True)

    x_pool, y_pool, x_ddos, y_ddos, details = load_holdout(SimpleNamespace(scenario="DDoS", seed=seed))
    x_train, x_rest, y_train, y_rest = train_test_split(
        x_pool, y_pool, train_size=SPLIT[0], stratify=y_pool, random_state=seed
    )
    x_val, x_test, y_val, y_test = train_test_split(
        x_rest, y_rest, test_size=SPLIT[2] / (SPLIT[1] + SPLIT[2]), stratify=y_rest, random_state=seed
    )

    bundle = seed_dir / "train_bundle.npz"
    np.savez_compressed(
        bundle,
        X_train=x_train.to_numpy(dtype=float),
        y_train=y_train.to_numpy(dtype=int),
        feature_columns=np.asarray(list(x_train.columns)),
    )
    val_csv = seed_dir / "frozen_validation.csv"
    test_iid_csv = seed_dir / "test_iid.csv"
    test_ddos_csv = seed_dir / "test_ddos_file.csv"
    write_split_csv(x_val, y_val, val_csv)
    write_split_csv(x_test, y_test, test_iid_csv)
    write_split_csv(x_ddos, y_ddos, test_ddos_csv)
    val_hash_frozen = sha256_file(val_csv)
    split_info = {
        "seed": seed,
        "heldout_file": details["heldout_file"],
        "rows": {"train": len(y_train), "validation": len(y_val), "test_iid": len(y_test), "test_ddos_file": len(y_ddos)},
        "positive_rate": {
            "train": float(y_train.mean()), "validation": float(y_val.mean()),
            "test_iid": float(y_test.mean()), "test_ddos_file": float(y_ddos.mean()),
        },
        "sha256": {
            "train_bundle": sha256_file(bundle), "validation": val_hash_frozen,
            "test_iid": sha256_file(test_iid_csv), "test_ddos_file": sha256_file(test_ddos_csv),
        },
    }
    (seed_dir / "split.json").write_text(json.dumps(split_info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    active = seed_dir / "active" / "model.joblib"
    train_candidate(bundle, INITIAL_MODEL, seed, active)
    active_name = INITIAL_MODEL
    initial_test = {"iid": score_on_csv(active, test_iid_csv), "ddos": score_on_csv(active, test_ddos_csv)}

    rows: list[dict[str, object]] = []
    rows.append({
        "seed": seed, "cycle": 0, "candidate": INITIAL_MODEL, "active_before": "", "decision": "initial",
        "active_after": INITIAL_MODEL,
        "active_after_test_iid_f1": initial_test["iid"]["f1"], "active_after_test_iid_mcc": initial_test["iid"]["mcc"],
        "active_after_test_ddos_f1": initial_test["ddos"]["f1"], "active_after_test_ddos_mcc": initial_test["ddos"]["mcc"],
    })

    for index, name in enumerate(CYCLE, start=1):
        cycle_dir = seed_dir / f"cycle_{index}_{name}"
        cycle_dir.mkdir(parents=True)
        candidate = cycle_dir / "candidate.joblib"
        plan = {
            "models": [{
                "family": f"r3_seed{seed}_cycle{index}",
                "current_model": str(active),
                "candidate_model": str(candidate),
                "current_metrics": str(cycle_dir / "current_metrics.csv"),
                "candidate_metrics": str(cycle_dir / "comparison_metrics.csv"),
                "validation_csv": str(val_csv),
                "validation_sep": ",",
                "label_column": "label",
                "metric": METRIC,
                "min_delta": MIN_DELTA,
                "train_command": [
                    python_exe, str(HERE / "train_candidate.py"), "--bundle", str(bundle),
                    "--candidate", name, "--seed", str(seed), "--model-out", str(candidate),
                ],
            }]
        }
        plan_text = json.dumps(plan, ensure_ascii=False, indent=2)
        assert "test_iid" not in plan_text and "test_ddos" not in plan_text, "un test apparait dans le plan"
        plan_path = cycle_dir / "plan.json"
        plan_path.write_text(plan_text + "\n", encoding="utf-8")

        hash_before = sha256_file(active)
        result = run_plan(
            plan_path,
            audit_path=audit_path,
            feedback_csv=cycle_dir / "feedback.csv",
            report_out=cycle_dir / "report.json",
            backups_dir=cycle_dir / "backups",
            promote=True,
            dry_run=False,
        )[0]
        if result.get("status") == "train_failed":
            raise RuntimeError(f"entrainement en echec: seed={seed} cycle={index} {name}")

        hash_after = sha256_file(active)
        hash_candidate = sha256_file(candidate)
        backup = Path(result["backup"]) if result.get("backup") else None
        backup_hash = sha256_file(backup) if backup and backup.exists() else None
        promoted = bool(result["promoted"])

        # Controle independant de la decision, sur la validation figee relue.
        if promoted and backup is None:
            raise RuntimeError(f"promotion sans sauvegarde: seed={seed} cycle={index}")
        val_current = score_on_csv(backup if promoted else active, val_csv)
        val_candidate = score_on_csv(candidate, val_csv)
        delta_indep = val_candidate[METRIC] - val_current[METRIC]
        expected_promotion = delta_indep >= MIN_DELTA
        checks = {
            "validation_unchanged": sha256_file(val_csv) == val_hash_frozen,
            "decision_matches_rule": promoted == expected_promotion,
            "delta_matches_code": abs(delta_indep - float(result["delta"])) <= 1e-6,
            "borderline": abs(delta_indep - MIN_DELTA) <= 1e-6,
        }
        if promoted:
            checks["backup_is_previous_active"] = backup_hash == hash_before
            checks["active_is_candidate"] = hash_after == hash_candidate
        else:
            checks["active_unchanged"] = hash_after == hash_before
            checks["no_backup"] = backup is None
        checks_ok = all(value for key, value in checks.items() if key != "borderline")

        active_before = active_name
        if promoted:
            active_name = name

        # Lecture des tests apres la decision uniquement.
        cand_test = {"iid": score_on_csv(candidate, test_iid_csv), "ddos": score_on_csv(candidate, test_ddos_csv)}
        act_test = {"iid": score_on_csv(active, test_iid_csv), "ddos": score_on_csv(active, test_ddos_csv)}
        prev_iid_f1 = rows[-1]["active_after_test_iid_f1"]
        rows.append({
            "seed": seed, "cycle": index, "candidate": name, "active_before": active_before,
            "val_current_f1": val_current[METRIC], "val_candidate_f1": val_candidate[METRIC],
            "delta_val": delta_indep, "min_delta": MIN_DELTA,
            "decision": "promoted" if promoted else "rejected", "code_status": result["status"],
            "active_after": active_name,
            "checks_ok": checks_ok, "checks": json.dumps(checks, sort_keys=True),
            "hash_active_before": hash_before, "hash_candidate": hash_candidate,
            "hash_backup": backup_hash or "", "hash_active_after": hash_after,
            "candidate_test_iid_f1": cand_test["iid"]["f1"], "candidate_test_ddos_f1": cand_test["ddos"]["f1"],
            "active_before_test_iid_f1": prev_iid_f1,
            "active_after_test_iid_f1": act_test["iid"]["f1"], "active_after_test_iid_mcc": act_test["iid"]["mcc"],
            "active_after_test_ddos_f1": act_test["ddos"]["f1"], "active_after_test_ddos_mcc": act_test["ddos"]["mcc"],
            "harmful_promotion": bool(promoted and cand_test["iid"]["f1"] < prev_iid_f1),
            "missed_promotion": bool((not promoted) and cand_test["iid"]["f1"] - prev_iid_f1 >= MIN_DELTA),
        })
    return rows


def summarize(rows: list[dict[str, object]], seeds: tuple[int, ...]) -> dict[str, object]:
    cycle_rows = [r for r in rows if r["cycle"] != 0]
    all_checks = all(bool(r["checks_ok"]) for r in cycle_rows)
    exercised = {
        seed: {
            "promotions": sum(1 for r in cycle_rows if r["seed"] == seed and r["decision"] == "promoted"),
            "rejections": sum(1 for r in cycle_rows if r["seed"] == seed and r["decision"] == "rejected"),
        }
        for seed in seeds
    }
    fully_exercised = all(v["promotions"] >= 1 and v["rejections"] >= 1 for v in exercised.values())
    if not all_checks:
        r3 = "R3_non_verifiee"
    elif not fully_exercised:
        r3 = "cycle_non_exerce"
    else:
        r3 = "R3_verifiee"

    gains = {}
    for split in ("iid", "ddos"):
        diffs = []
        for seed in seeds:
            seed_rows = [r for r in rows if r["seed"] == seed]
            first = next(r for r in seed_rows if r["cycle"] == 0)
            last = max(seed_rows, key=lambda r: r["cycle"])
            diffs.append(float(last[f"active_after_test_{split}_f1"]) - float(first[f"active_after_test_{split}_f1"]))
        ci = mean_ci(diffs)
        ci["per_seed"] = diffs
        ci["label"] = "benefice_confirme" if ci["low"] > 0 else "benefice_non_confirme"
        gains[split] = ci

    return {
        "experiment_id": EXPERIMENT_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "seeds": list(seeds),
        "initial_model": INITIAL_MODEL,
        "cycle": list(CYCLE),
        "metric": METRIC,
        "min_delta": MIN_DELTA,
        "decisions": len(cycle_rows),
        "promotions": sum(1 for r in cycle_rows if r["decision"] == "promoted"),
        "rejections": sum(1 for r in cycle_rows if r["decision"] == "rejected"),
        "all_checks_ok": all_checks,
        "borderline_decisions": sum(1 for r in cycle_rows if json.loads(r["checks"]).get("borderline")),
        "exercised_per_seed": {str(k): v for k, v in exercised.items()},
        "r3_decision": r3,
        "final_minus_initial_test_f1": gains,
        "harmful_promotions_iid": sum(1 for r in cycle_rows if r["harmful_promotion"]),
        "missed_promotions_iid": sum(1 for r in cycle_rows if r["missed_promotion"]),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial", action="store_true")
    parser.add_argument("--trial-dir", type=Path, default=None)
    args = parser.parse_args()

    seeds = TRIAL_SEEDS if args.trial else SEEDS
    if args.trial:
        if args.trial_dir is None:
            raise SystemExit("--trial-dir requis pour l'essai technique")
        out_dir = args.trial_dir
    else:
        out_dir = OUT_DIR
        if (out_dir / "summary.json").exists():
            raise SystemExit("summary.json existe deja : execution enregistree deja faite")
    work = out_dir / "_work"
    work.mkdir(parents=True, exist_ok=True)
    audit_path = out_dir / "audit.jsonl"
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.time()

    rows: list[dict[str, object]] = []
    for seed in seeds:
        rows.extend(run_seed(seed, work, audit_path, sys.executable))
        print(f"graine {seed} terminee ({time.time() - t0:.0f} s)", flush=True)

    summary = summarize(rows, seeds)
    summary["started_at"] = started
    summary["duration_s"] = round(time.time() - t0, 1)
    summary["programs_sha256"] = {
        rel(HERE / "run_e_r3_governance_cycle.py"): sha256_file(HERE / "run_e_r3_governance_cycle.py"),
        rel(HERE / "train_candidate.py"): sha256_file(HERE / "train_candidate.py"),
        "scripts/monthly_model_retraining.py": sha256_file(ROOT / "scripts" / "monthly_model_retraining.py"),
    }

    fields = sorted({key for row in rows for key in row}, key=lambda k: (k not in ("seed", "cycle", "candidate"), k))
    with (out_dir / "cycles.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    if args.trial:
        # L'essai technique ne divulgue aucune metrique : seulement les invariants.
        print(json.dumps({"all_checks_ok": summary["all_checks_ok"], "decisions": summary["decisions"]}))
        return 0

    for seed in seeds:
        src = work / f"seed_{seed}" / "split.json"
        shutil.copy2(src, out_dir / f"split_seed_{seed}.json")
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    manifest = [p for p in sorted(out_dir.rglob("*")) if p.is_file() and p.name != "MANIFEST_SHA256.csv"]
    with (out_dir / "MANIFEST_SHA256.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "sha256", "bytes"])
        for path in manifest:
            writer.writerow([rel(path), sha256_file(path), path.stat().st_size])
    print(json.dumps({k: summary[k] for k in ("r3_decision", "all_checks_ok", "promotions", "rejections")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
