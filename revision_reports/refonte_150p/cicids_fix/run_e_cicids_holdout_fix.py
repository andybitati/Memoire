"""E-CICIDS-HOLDOUT-FIX : réexécution du holdout par scénario de CICIDS2017.

Corrige le défaut de sélection de ``collect_network_sample`` (premières lignes du
premier fichier rencontré, donc un seul scénario à l'entraînement). Tout le reste
est repris à l'identique de la campagne d'origine : mêmes huit CSV, mêmes cinq
scénarios tenus à l'écart, mêmes variables (``_network_features``), mêmes plafonds
(8 000 lignes par classe à l'entraînement, 4 000 au test), mêmes cinq modèles et
hyperparamètres (``evaluate_cicids_model_candidates._candidate_models``), même
seuil de décision par défaut (``predict``).

Seule différence : pour chaque (scénario, graine), les lignes sont tirées
uniformément sans remise, avec un générateur fixé par la graine, dans **toutes**
les lignes de chaque classe de **tous** les fichiers d'entraînement (resp. du
fichier tenu à l'écart pour le test).

Lecture en deux passes, par blocs, pour tenir dans une mémoire réduite :
1. étiquettes seules, pour construire les réservoirs par classe ;
2. variables des seules lignes tirées.

Usage :
    python run_e_cicids_holdout_fix.py --dry-run   # tirage et composition, sans modèle ni métrique
    python run_e_cicids_holdout_fix.py             # exécution complète
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_cicids_model_candidates import _candidate_models, _score  # noqa: E402
from evaluate_supervised_strict_splits import (  # noqa: E402
    DROP_COLUMNS,
    _clean_columns,
    _label_column,
    _network_feature_columns,
    _network_features,
)

INPUT_DIR = ROOT / "data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"
OUTPUT_DIR = ROOT / "experiments/phase_revision_20261105/E-CICIDS-HOLDOUT-FIX"
SCENARIO_FILES = {
    "DDoS": "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "PortScan": "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
    "Bot": "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Infiltration": "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "WebAttacks": "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
}
SCENARIOS = list(SCENARIO_FILES)
SEEDS = [42, 43, 44, 45, 46]
TRAIN_PER_CLASS = 8000
TEST_PER_CLASS = 4000
CHUNKSIZE = 100_000
MARGIN = 0.01
MIN_SCENARIOS_WON = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_labels(path: Path) -> np.ndarray:
    header = _clean_columns(pd.read_csv(path, nrows=0, encoding_errors="ignore"))
    label_col = _label_column(header.columns)
    raw_names = pd.read_csv(path, nrows=0, encoding_errors="ignore").columns
    raw_label = raw_names[list(header.columns).index(label_col)]
    labels = pd.read_csv(
        path, usecols=[raw_label], dtype=str, keep_default_na=False, encoding_errors="ignore"
    )[raw_label]
    return labels.astype(str).str.strip().to_numpy()


def draw(pool: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """Tirage uniforme sans remise ; tout le réservoir s'il est plus petit que n."""
    if len(pool) <= n:
        return np.sort(pool)
    return np.sort(rng.choice(pool, size=n, replace=False))


def build_plans(files: list[Path], labels: dict[str, np.ndarray]) -> list[dict]:
    """Une entrée par (scénario, graine) : lignes tirées, par fichier et par classe."""
    attack = {name: np.char.upper(values.astype(str)) != "BENIGN" for name, values in labels.items()}
    plans = []
    for scenario_index, scenario in enumerate(SCENARIOS):
        heldout = SCENARIO_FILES[scenario]
        train_files = [path.name for path in files if path.name != heldout]
        for seed in SEEDS:
            rng = np.random.default_rng([seed, scenario_index])
            plan = {"scenario": scenario, "seed": seed, "heldout": heldout, "train": {}, "test": {}}
            for cls in (0, 1):
                # Réservoir global = (fichier, ligne) de toutes les lignes de la classe.
                keys = []
                for file_id, name in enumerate(train_files):
                    rows = np.flatnonzero(attack[name] == bool(cls))
                    keys.append(np.stack([np.full(len(rows), file_id), rows], axis=1))
                pool = np.concatenate(keys)
                chosen = pool[draw(np.arange(len(pool)), TRAIN_PER_CLASS, rng)]
                for file_id, name in enumerate(train_files):
                    picked = chosen[chosen[:, 0] == file_id, 1]
                    if len(picked):
                        plan["train"].setdefault(name, {})[cls] = picked
                rows = np.flatnonzero(attack[heldout] == bool(cls))
                plan["test"].setdefault(heldout, {})[cls] = draw(rows, TEST_PER_CLASS, rng)
            plans.append(plan)
    return plans


def needed_rows(plans: list[dict]) -> dict[str, np.ndarray]:
    needed: dict[str, set] = {}
    for plan in plans:
        for part in ("train", "test"):
            for name, by_class in plan[part].items():
                for rows in by_class.values():
                    needed.setdefault(name, set()).update(int(r) for r in rows)
    return {name: np.array(sorted(rows)) for name, rows in needed.items()}


def load_rows(files: list[Path], needed: dict[str, np.ndarray], feature_columns: list[str]) -> dict[str, pd.DataFrame]:
    """Deuxième passe : variables des seules lignes tirées, indexées par numéro de ligne."""
    cache = {}
    for path in files:
        wanted = needed.get(path.name)
        if wanted is None or not len(wanted):
            continue
        parts = []
        offset = 0
        for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=CHUNKSIZE, encoding_errors="ignore"):
            lo, hi = offset, offset + len(chunk)
            sel = wanted[(wanted >= lo) & (wanted < hi)]
            if len(sel):
                part = _network_features(chunk.iloc[sel - lo], feature_columns).astype("float32")
                part.index = sel
                parts.append(part)
            offset = hi
        cache[path.name] = pd.concat(parts)
        print(f"  {path.name}: {len(cache[path.name])} lignes chargées", flush=True)
    return cache


def assemble(part: dict, cache: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.Series, list[dict]]:
    xs, ys, comp = [], [], []
    for name, by_class in part.items():
        for cls, rows in by_class.items():
            xs.append(cache[name].loc[rows])
            ys.append(pd.Series(np.full(len(rows), cls, dtype=int)))
            comp.append({"file": name, "class": int(cls), "rows": int(len(rows))})
    x = pd.concat(xs, ignore_index=True).astype("float64")
    y = pd.concat(ys, ignore_index=True)
    return x, y, comp


def metric_row(scenario, seed, model, y_test, y_pred, y_score, duration, n_train):
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred, labels=[0, 1]).ravel()
    return {
        "scenario": scenario,
        "seed": seed,
        "model": model,
        "train_rows": n_train,
        "test_rows": int(len(y_test)),
        "test_positive_rate": float(np.mean(y_test)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "pr_auc": float(average_precision_score(y_test, y_score)) if y_score is not None else np.nan,
        "mcc": float(matthews_corrcoef(y_test, y_pred)),
        "duration_sec": float(duration),
    }


def decide(metrics: pd.DataFrame) -> dict:
    """Règle préenregistrée (protocole §5), appliquée à chacun des cinq modèles."""
    ap = metrics[metrics.model == "AllPositive"]
    ap_mean = float(ap.f1.mean())
    ap_by_scn = ap.groupby("scenario").f1.mean()
    out = {"all_positive_f1_mean": ap_mean, "margin": MARGIN, "min_scenarios_won": MIN_SCENARIOS_WON, "models": {}}
    for model in [m for m in metrics.model.unique() if m != "AllPositive"]:
        sub = metrics[metrics.model == model]
        mean = float(sub.f1.mean())
        by_scn = sub.groupby("scenario").f1.mean()
        won = int((by_scn > ap_by_scn.reindex(by_scn.index)).sum())
        beats = (mean - ap_mean > MARGIN) and (won >= MIN_SCENARIOS_WON)
        out["models"][model] = {"f1_mean": mean, "delta_vs_all_positive": mean - ap_mean, "scenarios_won": won, "beats_rule": bool(beats)}
    out["any_model_beats_rule"] = any(v["beats_rule"] for v in out["models"].values())
    out["decision"] = (
        "au_moins_un_modele_bat_la_regle" if out["any_model_beats_rule"] else "aucun_modele_ne_bat_la_regle"
    )
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="tirage et composition seulement, sans modèle ni métrique")
    args = parser.parse_args()

    started = datetime.now(timezone.utc)
    files = sorted(INPUT_DIR.glob("*.csv"))
    assert len(files) == 8, f"8 CSV attendus, {len(files)} trouvés"
    assert set(SCENARIO_FILES.values()) <= {p.name for p in files}
    feature_columns = _network_feature_columns(files[0])
    # Garde-fou anti-fuite : aucune colonne d'étiquette ni d'identifiant parmi les variables.
    assert not {c.lower() for c in feature_columns} & DROP_COLUMNS
    assert "label" not in {c.strip().lower() for c in feature_columns}

    print("Passe 1 : étiquettes", flush=True)
    labels = {path.name: read_labels(path) for path in files}
    plans = build_plans(files, labels)

    composition = []
    for plan in plans:
        for part in ("train", "test"):
            for name, by_class in plan[part].items():
                for cls, rows in by_class.items():
                    composition.append({"scenario": plan["scenario"], "seed": plan["seed"], "part": part,
                                        "file": name, "class": int(cls), "rows": int(len(rows))})
    comp = pd.DataFrame(composition)
    # Garde-fous de couverture : l'entraînement puise dans tous les fichiers hors scénario
    # pour la classe BENIGN, et dans plusieurs fichiers pour la classe attaque.
    for (scn, seed), g in comp[comp.part == "train"].groupby(["scenario", "seed"]):
        assert g[g["class"] == 0].file.nunique() == 7, (scn, seed, "BENIGN non tiré de 7 fichiers")
        assert g[g["class"] == 1].file.nunique() >= 3, (scn, seed, "attaques tirées de moins de 3 fichiers")
        assert g[g["class"] == 0].rows.sum() == TRAIN_PER_CLASS and g[g["class"] == 1].rows.sum() == TRAIN_PER_CLASS
    # La sélection dépend de la graine.
    first = plans[0]["train"]
    other = plans[1]["train"]
    common = set(first) & set(other)
    same = sum(len(np.intersect1d(first[n].get(0, []), other[n].get(0, []))) for n in common)
    assert same < 0.1 * TRAIN_PER_CLASS, "le tirage ne dépend pas de la graine"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    comp.to_csv(OUTPUT_DIR / "sample_composition.csv", index=False, encoding="utf-8")
    print(comp[comp.part == "train"].groupby(["scenario", "class"]).file.nunique().to_string(), flush=True)
    if args.dry_run:
        print("Dry run : composition écrite, aucun modèle entraîné, aucune métrique calculée.")
        return 0

    print("Passe 2 : variables des lignes tirées", flush=True)
    cache = load_rows(files, needed_rows(plans), feature_columns)

    rows = []
    for plan in plans:
        x_train, y_train, _ = assemble(plan["train"], cache)
        x_test, y_test, _ = assemble(plan["test"], cache)
        y_test = y_test.to_numpy()
        rows.append(metric_row(plan["scenario"], plan["seed"], "AllPositive", y_test,
                               np.ones_like(y_test), None, 0.0, len(y_train)))
        for name, model in _candidate_models(plan["seed"]).items():
            t0 = time.perf_counter()
            model.fit(x_train, y_train)
            y_pred = np.asarray(model.predict(x_test), dtype=int)
            y_score = _score(model, x_test)
            rows.append(metric_row(plan["scenario"], plan["seed"], name, y_test, y_pred, y_score,
                                   time.perf_counter() - t0, len(y_train)))
        print(f"  {plan['scenario']} graine {plan['seed']} : terminé", flush=True)

    metrics = pd.DataFrame(rows)
    metrics.to_csv(OUTPUT_DIR / "metrics.csv", index=False, encoding="utf-8")
    summary = (metrics.groupby("model").agg(evaluations=("f1", "size"), f1_mean=("f1", "mean"), f1_std=("f1", "std"),
                                             precision_mean=("precision", "mean"), recall_mean=("recall", "mean"),
                                             pr_auc_mean=("pr_auc", "mean"), mcc_mean=("mcc", "mean"))
               .sort_values("f1_mean", ascending=False))
    summary.to_csv(OUTPUT_DIR / "summary.csv", encoding="utf-8")
    by_scenario = metrics.pivot_table(index="scenario", columns="model", values="f1", aggfunc="mean")
    by_scenario.to_csv(OUTPUT_DIR / "f1_by_scenario.csv", encoding="utf-8")
    # Mesure secondaire : F1 micro (matrices de confusion cumulées sur les 25 évaluations).
    micro = metrics.groupby("model")[["tp", "fp", "fn"]].sum()
    micro["f1_micro"] = 2 * micro.tp / (2 * micro.tp + micro.fp + micro.fn)
    micro.to_csv(OUTPUT_DIR / "f1_micro.csv", encoding="utf-8")
    decision = decide(metrics)
    (OUTPUT_DIR / "decision.json").write_text(json.dumps(decision, indent=2, ensure_ascii=False), encoding="utf-8")

    metadata = {
        "protocol": "E-CICIDS-HOLDOUT-FIX",
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "sklearn": sklearn.__version__,
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "scenarios": SCENARIOS,
        "seeds": SEEDS,
        "train_per_class": TRAIN_PER_CLASS,
        "test_per_class": TEST_PER_CLASS,
        "input_files": {rel(p): sha256(p) for p in files},
    }
    (OUTPUT_DIR / "run_metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")

    sources = [Path(__file__), ROOT / "scripts/evaluate_cicids_model_candidates.py",
               ROOT / "scripts/evaluate_supervised_strict_splits.py"]
    outputs = sorted(p for p in OUTPUT_DIR.iterdir() if p.name != "MANIFEST_SHA256.csv")
    manifest = [{"role": "source", "path": rel(p), "sha256": sha256(p)} for p in sources]
    manifest += [{"role": "artefact", "path": rel(p), "sha256": sha256(p)} for p in outputs]
    pd.DataFrame(manifest).to_csv(OUTPUT_DIR / "MANIFEST_SHA256.csv", index=False, encoding="utf-8")
    print(summary.to_string())
    print(json.dumps(decision, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
