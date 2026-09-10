#!/usr/bin/env python3
"""Évalue deux journées officielles de CSE-CIC-IDS2018 en holdout strict.

Le jeudi 15 février constitue l'apprentissage et le vendredi 16 février le
test. Les hyperparamètres et le seuil sont figés dans la configuration avant
lecture des résultats. Les deux fichiers sont balayés intégralement pour
construire des réservoirs stratifiés reproductibles sans remise.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dataset_strengthening_common import (  # noqa: E402
    PHASE_ROOT,
    append_ledger,
    descriptive,
    ensure_phase_dirs,
    metrics_from_prediction,
    relative,
    run_id,
    sha256_file,
    utc_now,
    write_csv,
    write_json,
)

EXPERIMENT_ID = "dataset_07_external_csecicids2018"
CONFIG_PATH = PHASE_ROOT / "configs/external_csecicids2018_protocol.json"
DROP_COLUMNS = {
    "unnamed: 0",
    "label",
    "timestamp",
    "flow id",
    "source ip",
    "destination ip",
    "src ip",
    "dst ip",
}


def clean_columns(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    result.columns = [str(column).strip().lstrip("\ufeff") for column in result.columns]
    return result


def label_column(columns: list[str]) -> str:
    for column in columns:
        if column.strip().lower() == "label":
            return column
    raise ValueError("Colonne Label absente du fichier CSE-CIC-IDS2018.")


def feature_columns(train_path: Path, test_path: Path) -> tuple[list[str], dict[str, list[str]]]:
    train_header = clean_columns(pd.read_csv(train_path, nrows=0, encoding_errors="strict"))
    test_header = clean_columns(pd.read_csv(test_path, nrows=0, encoding_errors="strict"))
    train = [column for column in train_header.columns if column.lower() not in DROP_COLUMNS]
    test = [column for column in test_header.columns if column.lower() not in DROP_COLUMNS]
    common = [column for column in train if column in set(test)]
    if not common:
        raise RuntimeError("Aucune caractéristique commune entre apprentissage et test.")
    differences = {
        "train_only": sorted(set(train) - set(test)),
        "test_only": sorted(set(test) - set(train)),
    }
    return common, differences


def numeric_features(frame: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    values = clean_columns(frame).reindex(columns=columns, fill_value=0)
    values = values.replace(["Infinity", "INF", "inf", "-inf", "-Infinity", "NaN", "nan", ""], np.nan)
    for column in values.columns:
        values[column] = values[column].astype(str).str.replace(",", ".", regex=False)
    values = values.apply(pd.to_numeric, errors="coerce")
    return values.replace([np.inf, -np.inf], np.nan).fillna(0).clip(-1e12, 1e12).astype("float64")


def build_priority_pool(
    path: Path,
    columns: list[str],
    *,
    per_class: int,
    seed: int,
    chunksize: int,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    rng = np.random.default_rng(seed)
    reservoirs: dict[int, pd.DataFrame] = {0: pd.DataFrame(), 1: pd.DataFrame()}
    label_counts: dict[str, int] = {}
    source_row = 0
    header_rows_dropped = 0
    rows_scanned = 0
    for chunk in pd.read_csv(
        path,
        dtype=str,
        keep_default_na=False,
        chunksize=chunksize,
        encoding="utf-8",
        encoding_errors="strict",
        low_memory=False,
    ):
        chunk = clean_columns(chunk)
        label = label_column(list(chunk.columns))
        labels = chunk[label].astype(str).str.strip()
        header_mask = labels.str.upper().eq("LABEL")
        header_rows_dropped += int(header_mask.sum())
        if header_mask.any():
            chunk = chunk.loc[~header_mask].copy()
            labels = labels.loc[~header_mask]
        for value, count in labels.value_counts().items():
            label_counts[str(value)] = label_counts.get(str(value), 0) + int(count)
        targets = labels.str.upper().ne("BENIGN").astype(np.int8)
        features = numeric_features(chunk, columns)
        features["target"] = targets.to_numpy()
        features["__source_row"] = np.arange(source_row, source_row + len(features), dtype=np.int64)
        features["__priority"] = rng.random(len(features))
        source_row += len(features)
        rows_scanned += len(features)
        for target in (0, 1):
            candidate = features.loc[features["target"] == target]
            if candidate.empty:
                continue
            merged = pd.concat([reservoirs[target], candidate], ignore_index=True)
            reservoirs[target] = merged.nsmallest(per_class, "__priority").reset_index(drop=True)
    if reservoirs[0].empty or reservoirs[1].empty:
        raise RuntimeError(f"Classe absente dans {path.name}: {label_counts}")
    pool = pd.concat([reservoirs[0], reservoirs[1]], ignore_index=True)
    audit = {
        "rows_scanned": rows_scanned,
        "header_rows_dropped": header_rows_dropped,
        "label_counts": label_counts,
        "pool_counts": {str(target): int((pool["target"] == target).sum()) for target in (0, 1)},
    }
    return pool, audit


def seed_sample(pool: pd.DataFrame, *, per_class: int, seed: int) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    for target in (0, 1):
        group = pool.loc[pool["target"] == target]
        parts.append(group.sample(n=min(per_class, len(group)), replace=False, random_state=seed + target))
    return pd.concat(parts, ignore_index=True).sample(frac=1, random_state=seed).reset_index(drop=True)


def candidate_models(seed: int) -> dict[str, Any]:
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=120,
            max_depth=28,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=seed,
            n_jobs=1,
        ),
        "LogisticRegression": Pipeline(
            [
                ("scale", StandardScaler()),
                (
                    "model",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight="balanced",
                        solver="lbfgs",
                        random_state=seed,
                    ),
                ),
            ]
        ),
    }


def prediction_scores(model: Any, frame: pd.DataFrame) -> np.ndarray:
    if hasattr(model, "predict_proba"):
        return np.asarray(model.predict_proba(frame), dtype=float)[:, 1]
    values = np.asarray(model.decision_function(frame), dtype=float)
    return 1.0 / (1.0 + np.exp(-np.clip(values, -40, 40)))


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    output: list[dict[str, Any]] = []
    for model, group in frame.groupby("model", sort=True):
        row: dict[str, Any] = {
            "dataset": "CSE-CIC-IDS2018",
            "protocol": "2018-02-15_train_vs_2018-02-16_test",
            "model": model,
            "seeds": ",".join(str(seed) for seed in sorted(group["seed"].unique())),
        }
        for metric in ("precision", "recall", "f1", "pr_auc", "mcc", "fpr", "train_time_sec", "test_time_sec"):
            for name, value in descriptive(group[metric].astype(float)).items():
                row[f"{metric}_{name}"] = value
        output.append(row)
    return output


def plot_results(summary: list[dict[str, Any]], output: Path) -> None:
    frame = pd.DataFrame(summary)
    metrics = ["f1_mean", "pr_auc_mean", "mcc_mean", "recall_mean"]
    x = np.arange(len(frame))
    width = 0.18
    fig, ax = plt.subplots(figsize=(9.2, 5.5))
    for index, metric in enumerate(metrics):
        ax.bar(x + (index - 1.5) * width, frame[metric], width, label=metric.removesuffix("_mean").upper())
    ax.set_xticks(x, frame["model"])
    ax.set_ylim(-0.1, 1.05)
    ax.set_ylabel("Score moyen sur cinq sous-échantillons")
    ax.set_title("CSE-CIC-IDS2018 — jeudi DoS → vendredi DoS")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(ncol=4)
    fig.tight_layout()
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=180)
    plt.close(fig)


def write_analysis(
    output: Path,
    *,
    current_run: str,
    summary: list[dict[str, Any]],
    manifest_path: Path,
    audit: dict[str, Any],
) -> None:
    by_model = {row["model"]: row for row in summary}
    lines = [
        "# CSE-CIC-IDS2018 — validation externe légère",
        "",
        f"Run : `{current_run}`.",
        "",
        "## Protocole",
        "",
        "Le fichier officiel du 15 février 2018 est utilisé uniquement pour l’apprentissage; celui du 16 février est utilisé uniquement pour le test. Les scénarios DoS diffèrent entre les deux journées. Les timestamps ne sont pas des caractéristiques. Le seuil de décision reste fixé à `0,5` et aucun modèle n’est choisi sur le test.",
        "",
        "## Résultats",
        "",
        "| Modèle | F1 moyen | PR-AUC moyenne | MCC moyen | Rappel moyen | FPR moyen | N |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for model in ("RandomForest", "LogisticRegression"):
        row = by_model[model]
        lines.append(
            f"| {model} | {row['f1_mean']:.10f} | {row['pr_auc_mean']:.10f} | {row['mcc_mean']:.10f} | {row['recall_mean']:.10f} | {row['fpr_mean']:.10f} | {int(row['f1_n'])} |"
        )
    lines.extend(
        [
            "",
            "## Audit des données",
            "",
            f"- lignes d’apprentissage balayées : `{audit['train']['rows_scanned']}` ;",
            f"- lignes de test balayées : `{audit['test']['rows_scanned']}` ;",
            f"- en-têtes répétés écartés : train `{audit['train']['header_rows_dropped']}`, test `{audit['test']['header_rows_dropped']}` ;",
            f"- caractéristiques numériques communes : `{audit['feature_count']}` ;",
            "- cinq graines sont évaluées, mais elles partagent les mêmes pools parents figés.",
            "",
            "## Interprétation autorisée",
            "",
            "La campagne mesure la robustesse de deux familles de modèles légers face à un changement de journée et de sous-scénarios DoS dans un dataset officiel indépendant de CICIDS2017.",
            "",
            "## Limites",
            "",
            "Elle ne constitue pas un transfert direct des poids appris sur CICIDS2017. Elle ne démontre pas une généralisation à toutes les attaques de CSE-CIC-IDS2018, ni une validité industrielle. Les sous-échantillons équilibrés ne reproduisent pas la prévalence opérationnelle.",
            "",
            f"Manifeste : `{relative(manifest_path)}`.",
        ]
    )
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--chunksize", type=int, default=100_000)
    args = parser.parse_args()
    ensure_phase_dirs()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    train_path = ROOT / config["partition"]["train"]["local_path"]
    test_path = ROOT / config["partition"]["test"]["local_path"]
    plan = {
        "config": relative(CONFIG_PATH),
        "train_path": relative(train_path),
        "test_path": relative(test_path),
        "train_exists": train_path.exists(),
        "test_exists": test_path.exists(),
        "models": list(config["models"]),
        "seeds": config["sampling"]["evaluation_seeds"],
        "selection_on_test": config["model_or_threshold_selection_on_test"],
    }
    if args.dry_run:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    for partition, path in (("train", train_path), ("test", test_path)):
        if not path.exists():
            raise FileNotFoundError(f"Fichier officiel {partition} absent: {path}")
        expected = int(config["partition"][partition]["content_length_head"])
        if path.stat().st_size != expected:
            raise AssertionError(f"Taille {partition} inattendue: {path.stat().st_size} != {expected}")

    current_run = run_id("external_csecicids2018")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID,
        phase="7/7",
        run_id=current_run,
        dataset="CSE-CIC-IDS2018",
        protocol="official_day_scenario_holdout_15Feb_vs_16Feb",
        status="RUNNING",
        started_at=started_at,
        command="python scripts/run_external_csecicids2018_strengthening.py",
        config_path=relative(CONFIG_PATH),
        error_path=relative(error_path),
    )
    try:
        columns, differences = feature_columns(train_path, test_path)
        sampling = config["sampling"]
        train_pool, train_audit = build_priority_pool(
            train_path,
            columns,
            per_class=int(sampling["pool_per_class"]),
            seed=int(sampling["pool_seeds"]["train"]),
            chunksize=args.chunksize,
        )
        test_pool, test_audit = build_priority_pool(
            test_path,
            columns,
            per_class=int(sampling["pool_per_class"]),
            seed=int(sampling["pool_seeds"]["test"]),
            chunksize=args.chunksize,
        )
        train_pool_path = PHASE_ROOT / "processed" / f"{current_run}_train_pool.csv.gz"
        test_pool_path = PHASE_ROOT / "processed" / f"{current_run}_test_pool.csv.gz"
        train_pool.to_csv(train_pool_path, index=False, compression="gzip", encoding="utf-8")
        test_pool.to_csv(test_pool_path, index=False, compression="gzip", encoding="utf-8")

        rows: list[dict[str, Any]] = []
        meta = {"target", "__source_row", "__priority"}
        per_class = int(sampling["sample_per_class_per_seed"])
        for seed in sampling["evaluation_seeds"]:
            train = seed_sample(train_pool, per_class=per_class, seed=int(seed))
            test = seed_sample(test_pool, per_class=per_class, seed=int(seed))
            x_train = train[[column for column in train.columns if column not in meta]]
            y_train = train["target"].astype(np.int8)
            x_test = test[x_train.columns]
            y_test = test["target"].astype(np.int8)
            for model_name, model in candidate_models(int(seed)).items():
                train_started = perf_counter()
                model.fit(x_train, y_train)
                train_time = perf_counter() - train_started
                test_started = perf_counter()
                prediction = np.asarray(model.predict(x_test), dtype=np.int8)
                scores = prediction_scores(model, x_test)
                test_time = perf_counter() - test_started
                rows.append(
                    {
                        "run_id": current_run,
                        "dataset": "CSE-CIC-IDS2018",
                        "protocol": "2018-02-15_train_vs_2018-02-16_test",
                        "model": model_name,
                        "seed": int(seed),
                        "feature_count": len(columns),
                        "train_rows": len(train),
                        "test_rows": len(test),
                        **metrics_from_prediction(y_test.to_numpy(), prediction, scores),
                        "train_time_sec": train_time,
                        "test_time_sec": test_time,
                    }
                )

        raw_path = PHASE_ROOT / "raw" / f"{current_run}_metrics.csv"
        summary_path = PHASE_ROOT / "aggregated/external_csecicids2018_summary.csv"
        figure_path = PHASE_ROOT / "figures/dataset_11_external_csecicids2018.png"
        report_path = PHASE_ROOT / "reports/CSECICIDS2018_EXTERNAL_ANALYSIS.md"
        write_csv(raw_path, rows)
        summary = aggregate(rows)
        write_csv(summary_path, summary)
        plot_results(summary, figure_path)

        audit = {
            "feature_count": len(columns),
            "feature_differences": differences,
            "train": train_audit,
            "test": test_audit,
            "assertions": {
                "partitions_are_distinct_files": train_path.resolve() != test_path.resolve(),
                "timestamps_excluded": all(column.lower() != "timestamp" for column in columns),
                "model_or_threshold_selection_on_test": False,
                "sampling_without_replacement": True,
                "official_content_lengths_match": True,
            },
        }
        manifest_path = PHASE_ROOT / "manifests" / f"{current_run}_manifest.json"
        manifest = {
            "run_id": current_run,
            "dataset": "CSE-CIC-IDS2018",
            "official_page": config["official_page"],
            "official_bucket": config["official_bucket"],
            "config": {"path": relative(CONFIG_PATH), "sha256": sha256_file(CONFIG_PATH)},
            "sources": [
                {
                    "partition": partition,
                    "path": relative(path),
                    "url": config["partition"][partition]["url"],
                    "object_key": config["partition"][partition]["object_key"],
                    "size_bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                    "etag_head": config["partition"][partition]["etag_head"],
                }
                for partition, path in (("train", train_path), ("test", test_path))
            ],
            "protocol": config,
            "audit": audit,
            "pool_artifacts": [
                {"path": relative(train_pool_path), "sha256": sha256_file(train_pool_path)},
                {"path": relative(test_pool_path), "sha256": sha256_file(test_pool_path)},
            ],
            "result_artifacts": [
                relative(raw_path),
                relative(summary_path),
                relative(figure_path),
                relative(report_path),
            ],
        }
        write_json(manifest_path, manifest)
        write_analysis(report_path, current_run=current_run, summary=summary, manifest_path=manifest_path, audit=audit)
        append_ledger(
            experiment_id=EXPERIMENT_ID,
            phase="7/7",
            run_id=current_run,
            dataset="CSE-CIC-IDS2018",
            protocol="official_day_scenario_holdout_15Feb_vs_16Feb",
            status="COMPLETED",
            started_at=started_at,
            completed_at=utc_now(),
            command="python scripts/run_external_csecicids2018_strengthening.py",
            config_path=relative(CONFIG_PATH),
            raw_result_path=relative(raw_path),
            summary_path=relative(summary_path),
            figure_path=relative(figure_path),
            error_path=relative(error_path),
            notes="Dataset officiel UNB/AWS; jours et sous-scénarios DoS disjoints; cinq graines corrélées par pools parents.",
        )
        print(f"COMPLETED {current_run} {summary_path}")
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID,
            phase="7/7",
            run_id=current_run,
            dataset="CSE-CIC-IDS2018",
            protocol="official_day_scenario_holdout_15Feb_vs_16Feb",
            status="FAILED",
            started_at=started_at,
            completed_at=utc_now(),
            command="python scripts/run_external_csecicids2018_strengthening.py",
            config_path=relative(CONFIG_PATH),
            error_path=relative(error_path),
            notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
