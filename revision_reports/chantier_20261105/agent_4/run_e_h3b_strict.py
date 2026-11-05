"""E-H3B-STRICT-HOLDOUT : modèle commun contre modèles par famille, catégorie d'attaque tenue à l'écart.

Corrige deux défauts du chargement de ``scripts/run_family_routing_ablation.py`` sans modifier ce
script : la sélection par premières lignes, qui réduit CICIDS à un seul fichier, et l'inclusion de
``target`` dans le résumé numérique d'UNSW. Hors mode ``--smoke``, le programme refuse de s'exécuter
si le protocole n'est pas commité et inscrit au registre.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[3]
ID = "E-H3B-STRICT-HOLDOUT"
PROTOCOL = ROOT / "revision_reports/chantier_20261105/agent_4/protocoles" / f"{ID}.md"
REGISTRY = ROOT / "revision_reports/chantier_20261105/PROTOCOLES_PREENREGISTRES.md"
OUT = ROOT / "experiments/phase_revision_20261105" / ID
SOURCE_SCRIPT = ROOT / "scripts/run_family_routing_ablation.py"
LINUX = ROOT / "data/raw/Datasets/linux_auth_logs_labeled.csv"
CICIDS = ROOT / "data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"
UNSW_TRAIN = ROOT / "data/raw/Datasets/UNSW_NB15_training-set.parquet"
UNSW_TEST = ROOT / "data/raw/Datasets/UNSW_NB15_testing-set.parquet"
SEEDS = (42, 43, 44, 45, 46)
PER_CLASS = 6000
TEST_POSITIVE_CAP = 1500
MARGIN = -0.01
T_CRITICAL = 2.7764451051977987
WORKERS = 6
HOLDOUTS = {
    "cicids": ("DDoS", "PortScan", "Bot", "Infiltration", "WebAttacks"),
    "linux_auth": ("brute_force", "geo_anomaly", "port_scan", "privilege_escalation"),
    "unsw": ("Analysis", "Backdoor", "DoS", "Exploits", "Fuzzers", "Generic", "Reconnaissance", "Shellcode", "Worms"),
}


def load_source():
    spec = importlib.util.spec_from_file_location("family_ablation_source", SOURCE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["family_ablation_source"] = module
    spec.loader.exec_module(module)
    return module


source = load_source()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def derived_seed(*parts: object) -> int:
    material = "|".join(str(part) for part in parts).encode("utf-8")
    return int.from_bytes(hashlib.blake2b(material, digest_size=4).digest(), "big")


def prepare_linux(raw: pd.DataFrame) -> pd.DataFrame:
    """Mêmes variables que ``load_linux_auth``."""

    ts = pd.to_datetime(raw["timestamp"], errors="coerce", utc=True)
    out = pd.DataFrame(index=raw.index)
    out["family"] = "linux_auth"
    out["category"] = raw["anomaly_label"].astype(str).str.strip().str.lower()
    out["target"] = out["category"].ne("normal").astype(int)
    out["duration"] = 0
    out["src_port"] = 0
    out["dst_port"] = pd.to_numeric(raw.get("port", 0), errors="coerce").fillna(0)
    out["packet_count"] = 0
    out["byte_count"] = 0
    out["rate"] = 0
    out["attempts"] = pd.to_numeric(raw.get("attempts", 0), errors="coerce").fillna(0)
    out["hour"] = ts.dt.hour.fillna(0).astype(int)
    out["weekday"] = ts.dt.weekday.fillna(0).astype(int)
    out["protocol"] = raw.get("protocol", "").astype(str).fillna("")
    out["service"] = raw.get("service", "").astype(str).fillna("")
    out["state"] = ""
    out["status"] = raw.get("status", "").astype(str).fillna("")
    summary = source._numeric_summary(out[["dst_port", "attempts", "hour", "weekday"]])
    return pd.concat([out, summary], axis=1)


def cicids_category(labels: pd.Series) -> pd.Series:
    upper = labels.astype(str).str.strip().str.upper()
    result = pd.Series("other_attack", index=upper.index, dtype=object)
    result[upper.eq("BENIGN")] = "normal"
    result[upper.eq("DDOS")] = "DDoS"
    result[upper.eq("PORTSCAN")] = "PortScan"
    result[upper.eq("BOT")] = "Bot"
    result[upper.eq("INFILTRATION")] = "Infiltration"
    result[upper.str.startswith("WEB ATTACK")] = "WebAttacks"
    return result


def prepare_cicids(raw: pd.DataFrame) -> pd.DataFrame:
    """Mêmes variables que ``load_cicids``."""

    label_col = next(column for column in raw.columns if column.lower() == "label")
    numeric = raw.drop(columns=[label_col])
    summary = source._numeric_summary(numeric.astype(str).replace(["Infinity", "INF", "-Infinity"], np.nan))
    out = pd.DataFrame(index=raw.index)
    out["family"] = "cicids"
    out["category"] = cicids_category(raw[label_col])
    out["target"] = out["category"].ne("normal").astype(int)
    out["duration"] = pd.to_numeric(raw.get("Flow Duration", 0), errors="coerce").fillna(0)
    out["src_port"] = 0
    out["dst_port"] = pd.to_numeric(raw.get("Destination Port", 0), errors="coerce").fillna(0)
    out["packet_count"] = pd.to_numeric(raw.get("Total Fwd Packets", 0), errors="coerce").fillna(0) + pd.to_numeric(
        raw.get("Total Backward Packets", 0), errors="coerce"
    ).fillna(0)
    out["byte_count"] = pd.to_numeric(raw.get("Total Length of Fwd Packets", 0), errors="coerce").fillna(0) + pd.to_numeric(
        raw.get("Total Length of Bwd Packets", 0), errors="coerce"
    ).fillna(0)
    out["rate"] = pd.to_numeric(raw.get("Flow Packets/s", 0), errors="coerce").fillna(0)
    out["attempts"] = 0
    out["hour"] = 0
    out["weekday"] = 0
    out["protocol"] = "flow"
    out["service"] = ""
    out["state"] = ""
    out["status"] = ""
    return pd.concat([out, summary], axis=1)


def prepare_unsw(raw: pd.DataFrame) -> pd.DataFrame:
    """Mêmes variables que ``load_unsw``, mais le résumé numérique exclut l'étiquette."""

    target = pd.to_numeric(raw["label"], errors="coerce").fillna(0).astype(int)
    summary = source._numeric_summary(raw.drop(columns=["label", "attack_cat"], errors="ignore").astype(str))
    out = pd.DataFrame(index=raw.index)
    out["family"] = "unsw"
    out["category"] = raw["attack_cat"].astype(str).str.strip()
    out.loc[target.eq(0), "category"] = "normal"
    out["target"] = target
    out["duration"] = pd.to_numeric(raw.get("dur", 0), errors="coerce").fillna(0)
    out["src_port"] = 0
    out["dst_port"] = 0
    out["packet_count"] = pd.to_numeric(raw.get("spkts", 0), errors="coerce").fillna(0) + pd.to_numeric(
        raw.get("dpkts", 0), errors="coerce"
    ).fillna(0)
    out["byte_count"] = pd.to_numeric(raw.get("sbytes", 0), errors="coerce").fillna(0) + pd.to_numeric(
        raw.get("dbytes", 0), errors="coerce"
    ).fillna(0)
    out["rate"] = pd.to_numeric(raw.get("rate", 0), errors="coerce").fillna(0)
    out["attempts"] = 0
    out["hour"] = 0
    out["weekday"] = 0
    out["protocol"] = raw.get("proto", "").astype(str).fillna("")
    out["service"] = raw.get("service", "").astype(str).fillna("")
    out["state"] = raw.get("state", "").astype(str).fillna("")
    out["status"] = ""
    return pd.concat([out, summary], axis=1)


def load_all() -> dict[str, pd.DataFrame]:
    linux = pd.concat(
        [prepare_linux(chunk) for chunk in pd.read_csv(LINUX, dtype=str, keep_default_na=False, chunksize=100_000)],
        ignore_index=True,
    )
    parts = []
    for path in sorted(CICIDS.glob("*.csv")):
        for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=100_000, encoding_errors="ignore"):
            chunk.columns = [str(column).strip().lstrip("﻿") for column in chunk.columns]
            parts.append(prepare_cicids(chunk))
    cicids = pd.concat(parts, ignore_index=True)
    raw = pd.concat([pd.read_parquet(UNSW_TRAIN), pd.read_parquet(UNSW_TEST)], ignore_index=True)
    return {"linux_auth": linux, "cicids": cicids, "unsw": prepare_unsw(raw)}


def sample(frame: pd.DataFrame, count: int, seed: int) -> pd.DataFrame:
    return frame if len(frame) <= count else frame.sample(count, random_state=seed)


def balanced_train(frame: pd.DataFrame, seed: int, family: str, per_class: int) -> pd.DataFrame:
    normal = sample(frame[frame["target"] == 0], per_class, derived_seed(seed, family, "normal"))
    attack = sample(frame[frame["target"] == 1], per_class, derived_seed(seed, family, "attack"))
    return pd.concat([normal, attack], ignore_index=True)


def holdout_split(
    frame: pd.DataFrame, seed: int, family: str, held: str, per_class: int, cap: int
) -> tuple[pd.DataFrame, pd.DataFrame]:
    positives = frame[frame["category"] == held]
    if positives.empty:
        raise AssertionError(f"Catégorie absente : {family}/{held}")
    test_pos = sample(positives, cap, derived_seed(seed, family, held, "test_pos"))
    normals = frame[frame["target"] == 0]
    test_neg = normals.sample(len(test_pos), random_state=derived_seed(seed, family, held, "test_neg"))
    remaining_normals = normals.drop(index=test_neg.index)
    attacks = frame[(frame["target"] == 1) & (frame["category"] != held)]
    train = pd.concat(
        [
            sample(remaining_normals, per_class, derived_seed(seed, family, held, "train_neg")),
            sample(attacks, per_class, derived_seed(seed, family, held, "train_pos")),
        ],
        ignore_index=True,
    )
    return train, pd.concat([test_pos, test_neg], ignore_index=True)


def fit_eval(job: dict) -> list[dict]:
    """Ajuste le modèle commun et le modèle spécialisé sur un même test."""

    seed, family, held = job["seed"], job["family"], job["held"]
    features = source.COMMON_FEATURES
    test, rows = job["test"], []
    for variant, train in (("global_common_model", job["train_common"]), ("family_aware_models", job["train_family"])):
        model = source.make_model(seed)
        model.fit(train[features], train["target"])
        row = source._metric_row(
            variant, family, test["target"], model.predict(test[features]), len(test),
            seed=seed, y_score=source._positive_scores(model, test[features]),
        )
        row.update(split=job["split"], heldout=held, train_rows=len(train))
        rows.append(row)
    return rows


def build_jobs(data, seeds, per_class, cap, holdouts) -> list[dict]:
    clean = {family: frame.replace([np.inf, -np.inf], np.nan) for family, frame in data.items()}
    jobs = []
    for seed in seeds:
        others = {family: balanced_train(frame, seed, family, per_class) for family, frame in clean.items()}
        for family, categories in holdouts.items():
            for held in categories:
                train, test = holdout_split(clean[family], seed, family, held, cap=cap, per_class=per_class)
                common = pd.concat([train] + [others[name] for name in clean if name != family], ignore_index=True)
                jobs.append(dict(seed=seed, family=family, held=held, split="category_holdout",
                                 train_common=common, train_family=train, test=test))
        # Référence sans fuite ni sélection par premières lignes : split aléatoire 75/25.
        splits = {}
        for family, frame in others.items():
            splits[family] = train_test_split(
                frame, test_size=0.25, stratify=frame["target"].astype(str), random_state=seed
            )
        common = pd.concat([part[0] for part in splits.values()], ignore_index=True)
        for family, (train, test) in splits.items():
            jobs.append(dict(seed=seed, family=family, held="", split="random_reference",
                             train_common=common, train_family=train, test=test))
    return jobs


def interval(values: np.ndarray) -> dict[str, float]:
    mean, sd = float(values.mean()), float(values.std(ddof=1))
    half = T_CRITICAL * sd / math.sqrt(len(values))
    return {"mean": mean, "sd": sd, "ci95_lower": mean - half, "ci95_upper": mean + half}


def analyse(metrics: pd.DataFrame, split: str) -> dict:
    subset = metrics[metrics["split"] == split]
    pivot = subset.pivot_table(index=["seed", "family", "heldout"], columns="variant", values="f1").reset_index()
    pivot["delta"] = pivot["family_aware_models"] - pivot["global_common_model"]
    per_seed = pivot.groupby(["seed", "family"], as_index=False)[["delta", "family_aware_models", "global_common_model"]].mean()
    families = {}
    for family, group in per_seed.groupby("family"):
        item = interval(group["delta"].to_numpy(dtype=float))
        item.update(
            non_inferior=bool(item["ci95_lower"] >= MARGIN),
            f1_family=float(group["family_aware_models"].mean()),
            f1_common=float(group["global_common_model"].mean()),
        )
        families[str(family)] = item
    by_category = (
        pivot.groupby(["family", "heldout"])[["family_aware_models", "global_common_model", "delta"]].mean().reset_index()
    )
    return {
        "families": families,
        "criterion_met": all(item["non_inferior"] for item in families.values()),
        "by_category": by_category.to_dict(orient="records"),
    }


def require_preregistered() -> None:
    if sha256(PROTOCOL) not in REGISTRY.read_text(encoding="utf-8"):
        raise SystemExit("Protocole absent du registre")
    rel = relative(PROTOCOL)
    shown = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{rel}"], capture_output=True, check=False)
    if shown.returncode or shown.stdout.replace(b"\r\n", b"\n") != PROTOCOL.read_bytes().replace(b"\r\n", b"\n"):
        raise SystemExit("Protocole non commité ou modifié")


def smoke_equivalence() -> None:
    """Vérifie que la préparation reproduit le chargeur source, hormis la correction d'UNSW."""

    numeric = source.COMMON_NUMERIC
    chunk = next(pd.read_csv(LINUX, dtype=str, keep_default_na=False, chunksize=100_000))
    labels = chunk["anomaly_label"].str.lower().str.strip()
    raw = pd.concat([chunk[labels.eq("normal")].head(200), chunk[labels.ne("normal")].head(200)], ignore_index=True)
    ours, ref = prepare_linux(raw), source.load_linux_auth(LINUX, normal=200, anomaly=200, random_state=1)
    assert np.allclose(ours[numeric].astype(float), ref[numeric].astype(float)), "linux"
    assert (ours[source.COMMON_CATEGORICAL].astype(str).values == ref[source.COMMON_CATEGORICAL].astype(str).values).all()

    first = sorted(CICIDS.glob("*.csv"))[0]
    chunk = next(pd.read_csv(first, dtype=str, keep_default_na=False, chunksize=100_000, encoding_errors="ignore"))
    chunk.columns = [str(column).strip().lstrip("﻿") for column in chunk.columns]
    labels = chunk["Label"].str.strip().str.upper()
    raw = pd.concat([chunk[labels.eq("BENIGN")].head(200), chunk[labels.ne("BENIGN")].head(200)], ignore_index=True)
    ours, ref = prepare_cicids(raw), source.load_cicids(CICIDS, normal=200, anomaly=200, random_state=1)
    assert np.allclose(ours[numeric].astype(float), ref[numeric].astype(float), equal_nan=True), "cicids"

    raw = pd.concat([pd.read_parquet(UNSW_TRAIN), pd.read_parquet(UNSW_TEST)], ignore_index=True)
    raw = raw.assign(target=pd.to_numeric(raw["label"], errors="coerce").fillna(0).astype(int))
    sampled = source._balanced(raw, normal=200, anomaly=200, random_state=1)
    ours = prepare_unsw(sampled.drop(columns=["target"]).reset_index(drop=True))
    ref = source.load_unsw(UNSW_TRAIN, UNSW_TEST, normal=200, anomaly=200, random_state=1).reset_index(drop=True)
    kept = [column for column in numeric if not column.startswith("numeric_")]
    assert np.allclose(ours[kept].astype(float), ref[kept].astype(float)), "unsw"
    print("préparation conforme au chargeur source (résumé UNSW excepté)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", type=Path)
    args = parser.parse_args()
    started = datetime.now(timezone.utc).isoformat()
    if args.smoke is not None:
        smoke_equivalence()
        seeds, per_class, cap, out = (1, 2), 150, 40, args.smoke
        holdouts = {family: values[:1] for family, values in HOLDOUTS.items()}
    else:
        require_preregistered()
        seeds, per_class, cap, out, holdouts = SEEDS, PER_CLASS, TEST_POSITIVE_CAP, OUT, HOLDOUTS
        if (out / "summary.json").exists():
            raise SystemExit("Artefacts déjà présents, refus d'écraser")
    out.mkdir(parents=True, exist_ok=True)

    data = load_all()
    counts = {family: frame["category"].value_counts().to_dict() for family, frame in data.items()}
    for family, categories in holdouts.items():
        for held in categories:
            if counts[family].get(held, 0) == 0:
                raise AssertionError(f"{family}/{held} absent")
    jobs = build_jobs(data, seeds, per_class, cap, holdouts)
    del data
    print(f"{len(jobs)} ajustements appariés", flush=True)
    rows: list[dict] = []
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for index, result in enumerate(pool.map(fit_eval, jobs), start=1):
            rows.extend(result)
            if index % 10 == 0:
                print(f"{index}/{len(jobs)}", flush=True)
    metrics = pd.DataFrame(rows)
    metrics_path = out / "metrics_by_seed_family_category.csv"
    metrics.sort_values(["split", "family", "heldout", "seed", "variant"]).to_csv(metrics_path, index=False, encoding="utf-8")

    if args.smoke is not None:
        print(f"essai technique conforme : {len(metrics)} lignes")
        return 0

    summary = {
        "experiment_id": ID,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "seeds": list(seeds),
        "per_class": per_class,
        "test_positive_cap": cap,
        "margin": MARGIN,
        "available_rows_by_category": counts,
        "category_holdout": analyse(metrics, "category_holdout"),
        "random_reference": analyse(metrics, "random_reference"),
        "criterion": "Pour chaque famille, borne inférieure de l'IC t apparié à 95 % du delta F1, moyen par graine sur les catégories, >= -0,01.",
    }
    summary["criterion_met"] = summary["category_holdout"]["criterion_met"]
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float) + "\n", encoding="utf-8")

    inputs = [LINUX, UNSW_TRAIN, UNSW_TEST, *sorted(CICIDS.glob("*.csv"))]
    entries = [("protocol", PROTOCOL), ("runner", Path(__file__).resolve()), ("source_script", SOURCE_SCRIPT)]
    entries += [("input", path) for path in inputs] + [("artifact", metrics_path), ("artifact", summary_path)]
    with (out / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "path", "sha256", "bytes"])
        writer.writeheader()
        for role, path in entries:
            writer.writerow({"role": role, "path": relative(path), "sha256": sha256(path), "bytes": path.stat().st_size})
    print(f"terminé : {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
