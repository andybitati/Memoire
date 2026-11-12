"""E-CICIDS-WTMC2021-HOLDOUT : holdout par scénario sur CICIDS2017 corrigé (Engelen et al.).

Reprend la campagne E-CICIDS-HOLDOUT-FIX (revision_reports/refonte_150p/cicids_fix/
run_e_cicids_holdout_fix.py) sur la version régénérée et réétiquetée de CICIDS2017 publiée
par Engelen, Rimmer et Joosen (WTMC 2021). Sont importés sans modification : tirage
(``draw``), lecture des lignes tirées (``load_rows``), assemblage, métriques (``metric_row``),
règle de décision (``decide``), cinq modèles et hyperparamètres (``_candidate_models``),
plafonds 8 000 / 4 000 lignes par classe, graines 42 à 46.

Adaptations imposées par le format (un fichier par jour au lieu d'un fichier par scénario) :
- un scénario est défini par ses étiquettes ; le test réunit ses attaques et les flux bénins
  de son jour ; l'entraînement tire les bénins des autres jours et les attaques de tous les
  autres scénarios, tous jours confondus ;
- les flux étiquetés « - Attempted » sont exclus des deux classes ;
- variables : celles du fichier, moins Flow ID, Src IP, Src Port, Dst IP, Protocol,
  Timestamp et Label (le CSV d'origine ne contenait ni IP, ni port source, ni protocole,
  ni horodatage).

Usage : python run_e_cicids_wtmc2021_holdout.py [--dry-run]
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

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "refonte_150p" / "cicids_fix"))
sys.path.insert(0, str(ROOT / "scripts"))
import run_e_cicids_holdout_fix as base  # noqa: E402

INPUT_DIR = ROOT / "data/raw/external/CICIDS2017-WTMC2021/csv"
OUTPUT_DIR = ROOT / "experiments/phase_revision_20261112/E-CICIDS-WTMC2021-HOLDOUT"
SCENARIOS = {
    "DDoS": ("Friday-WorkingHours.csv", lambda l: l == "DDoS"),
    "PortScan": ("Friday-WorkingHours.csv", lambda l: l == "PortScan"),
    "Bot": ("Friday-WorkingHours.csv", lambda l: l == "Bot"),
    "Infiltration": ("Thursday-WorkingHours.csv", lambda l: l == "Infiltration"),
    "WebAttacks": ("Thursday-WorkingHours.csv", lambda l: l.startswith("Web Attack")),
}
DROP = {"flow id", "src ip", "src port", "dst ip", "protocol", "timestamp", "label"}
SEEDS = base.SEEDS
TRAIN, TEST = base.TRAIN_PER_CLASS, base.TEST_PER_CLASS


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def read_labels(path: Path) -> np.ndarray:
    return pd.read_csv(path, usecols=["Label"], dtype=str, keep_default_na=False)["Label"].str.strip().to_numpy()


def build_plans(files, labels):
    plans = []
    for s_index, (scenario, (day, is_scn)) in enumerate(SCENARIOS.items()):
        flags = {}
        for name, lab in labels.items():
            attempted = np.char.endswith(lab.astype(str), "- Attempted")
            benign = lab == "BENIGN"
            in_scn = np.array([is_scn(x) for x in lab]) & ~attempted
            flags[name] = (benign, in_scn, ~benign & ~attempted & ~in_scn)
        for seed in SEEDS:
            rng = np.random.default_rng([seed, s_index])
            plan = {"scenario": scenario, "seed": seed, "heldout": day, "train": {}, "test": {}}
            for cls in (0, 1):
                keys = []
                for fid, path in enumerate(files):
                    benign, _scn, other = flags[path.name]
                    mask = (benign if path.name != day else np.zeros_like(benign)) if cls == 0 else other
                    rows = np.flatnonzero(mask)
                    keys.append(np.stack([np.full(len(rows), fid), rows], axis=1))
                pool = np.concatenate(keys)
                chosen = pool[base.draw(np.arange(len(pool)), TRAIN, rng)]
                for fid, path in enumerate(files):
                    picked = chosen[chosen[:, 0] == fid, 1]
                    if len(picked):
                        plan["train"].setdefault(path.name, {})[cls] = picked
                benign, scn, _ = flags[day]
                plan["test"].setdefault(day, {})[cls] = base.draw(np.flatnonzero(scn if cls else benign), TEST, rng)
            plans.append(plan)
    return plans


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    started = datetime.now(timezone.utc)
    files = sorted(INPUT_DIR.glob("*.csv"))
    assert len(files) == 5, len(files)
    header = pd.read_csv(files[0], nrows=0).columns
    features = [c for c in header if c.strip().lower() not in DROP]
    assert not {c.strip().lower() for c in features} & DROP
    base.DROP_COLUMNS = base.DROP_COLUMNS | DROP  # utilisé par _network_features
    import evaluate_supervised_strict_splits as ess
    ess.DROP_COLUMNS = ess.DROP_COLUMNS | DROP

    labels = {p.name: read_labels(p) for p in files}
    plans = build_plans(files, labels)
    comp = []
    for plan in plans:
        for part in ("train", "test"):
            for name, by in plan[part].items():
                for cls, rows in by.items():
                    comp.append({"scenario": plan["scenario"], "seed": plan["seed"], "part": part,
                                 "file": name, "class": int(cls), "rows": int(len(rows))})
    comp = pd.DataFrame(comp)
    for (scn, seed), g in comp[comp.part == "train"].groupby(["scenario", "seed"]):
        assert g[g["class"] == 0].rows.sum() == TRAIN and g[g["class"] == 1].rows.sum() == TRAIN, (scn, seed)
        assert g[g["class"] == 0].file.nunique() >= 3 and g[g["class"] == 1].file.nunique() >= 2, (scn, seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    comp.to_csv(OUTPUT_DIR / "sample_composition.csv", index=False, encoding="utf-8")
    if args.dry_run:
        print("Dry run : composition écrite, aucun modèle entraîné.")
        print(comp.groupby(["scenario", "part", "class"]).rows.sum().unstack(["part", "class"]).to_string())
        return 0

    cache = base.load_rows(files, base.needed_rows(plans), features)
    rows = []
    for plan in plans:
        x_train, y_train, _ = base.assemble(plan["train"], cache)
        x_test, y_test, _ = base.assemble(plan["test"], cache)
        y_test = y_test.to_numpy()
        rows.append(base.metric_row(plan["scenario"], plan["seed"], "AllPositive", y_test, np.ones_like(y_test), None, 0.0, len(y_train)))
        for name, model in base._candidate_models(plan["seed"]).items():
            t0 = time.perf_counter()
            model.fit(x_train, y_train)
            y_pred = np.asarray(model.predict(x_test), dtype=int)
            rows.append(base.metric_row(plan["scenario"], plan["seed"], name, y_test, y_pred,
                                        base._score(model, x_test), time.perf_counter() - t0, len(y_train)))
        print(f"  {plan['scenario']} graine {plan['seed']} : terminé", flush=True)
    metrics = pd.DataFrame(rows)
    metrics.to_csv(OUTPUT_DIR / "metrics.csv", index=False, encoding="utf-8")
    decision = base.decide(metrics)
    (OUTPUT_DIR / "decision.json").write_text(json.dumps(decision, indent=2, ensure_ascii=False), encoding="utf-8")
    meta = {"protocol": "E-CICIDS-WTMC2021-HOLDOUT", "started_utc": started.isoformat(),
            "finished_utc": datetime.now(timezone.utc).isoformat(), "python": platform.python_version(),
            "sklearn": sklearn.__version__, "pandas": pd.__version__, "numpy": np.__version__,
            "features": features, "input_files": {p.relative_to(ROOT).as_posix(): sha256(p) for p in files},
            "archive_sha256": sha256(INPUT_DIR.parent / "dataset.zip")}
    (OUTPUT_DIR / "run_metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    sources = [Path(__file__), Path(base.__file__), ROOT / "scripts/evaluate_cicids_model_candidates.py",
               ROOT / "scripts/evaluate_supervised_strict_splits.py"]
    outputs = sorted(p for p in OUTPUT_DIR.iterdir() if p.name != "MANIFEST_SHA256.csv")
    man = [{"role": "source", "path": p.resolve().relative_to(ROOT).as_posix(), "sha256": sha256(p)} for p in sources]
    man += [{"role": "artefact", "path": p.relative_to(ROOT).as_posix(), "sha256": sha256(p)} for p in outputs]
    pd.DataFrame(man).to_csv(OUTPUT_DIR / "MANIFEST_SHA256.csv", index=False, encoding="utf-8")
    print(json.dumps(decision, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
