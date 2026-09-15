#!/usr/bin/env python3
"""Audit anti-fuite et explicabilité de la LR externe CSE-CIC-IDS2018."""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path
from time import perf_counter
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from dataset_strengthening_common import descriptive, metrics_from_prediction  # noqa: E402
from final_consolidation_common import (  # noqa: E402
    CONFIG_PATH, PHASE_ROOT, append_ledger, ensure_phase_dirs, relative,
    run_id, sha256_file, utc_now, write_csv, write_json,
)
from run_external_csecicids2018_strengthening import (  # noqa: E402
    candidate_models, prediction_scores, seed_sample,
)

EXPERIMENT_ID = "final_p1_csecicids2018_lr_forensic"
SOURCE_PHASE = ROOT / "experiments" / "phase_dataset_strengthening"
META_COLUMNS = {"target", "__source_row", "__priority"}
METRICS = ("precision", "recall", "f1", "pr_auc", "mcc", "fpr")


def latest_principal_manifest() -> Path:
    pattern = re.compile(r"external_csecicids2018_\d{8}T\d{6}Z_manifest\.json$")
    candidates = [path for path in SOURCE_PHASE.glob("manifests/*.json") if pattern.search(path.name)]
    if not candidates:
        raise FileNotFoundError("Manifeste principal CSE-CIC-IDS2018 absent.")
    return sorted(candidates)[-1]


def permute_training_labels(labels: pd.Series, seed: int) -> pd.Series:
    rng = np.random.default_rng(seed + 1_000_003)
    return pd.Series(rng.permutation(labels.to_numpy()), index=labels.index, dtype=np.int8)


def fit_lr(x_train: pd.DataFrame, y_train: pd.Series, seed: int) -> Any:
    model = candidate_models(seed)["LogisticRegression"]
    model.fit(x_train, y_train)
    return model


def evaluate(model: Any, x_test: pd.DataFrame, y_test: pd.Series) -> dict[str, Any]:
    prediction = np.asarray(model.predict(x_test), dtype=np.int8)
    scores = prediction_scores(model, x_test)
    return metrics_from_prediction(y_test.to_numpy(), prediction, scores)


def coefficient_rows(model: Any, features: list[str], seed: int) -> list[dict[str, Any]]:
    coefficients = np.asarray(model.named_steps["model"].coef_[0], dtype=float)
    if len(coefficients) != len(features):
        raise AssertionError("Nombre de coefficients incompatible avec le schéma de caractéristiques.")
    return [
        {
            "seed": seed,
            "feature": feature,
            "coefficient": float(coefficient),
            "absolute_coefficient": float(abs(coefficient)),
            "coefficient_space": "after_train_only_standardization",
        }
        for feature, coefficient in zip(features, coefficients, strict=True)
    ]


def training_only_ranking(model: Any, features: list[str]) -> list[str]:
    rows = coefficient_rows(model, features, seed=-1)
    return [row["feature"] for row in sorted(rows, key=lambda row: (-row["absolute_coefficient"], row["feature"]))]


def aggregate_by(rows: list[dict[str, Any]], keys: list[str]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    output: list[dict[str, Any]] = []
    for values, group in frame.groupby(keys, sort=True, dropna=False):
        if not isinstance(values, tuple):
            values = (values,)
        item = dict(zip(keys, values, strict=True))
        item["seeds"] = ",".join(str(int(seed)) for seed in sorted(group["seed"].unique()))
        for metric in METRICS:
            if metric in group:
                for name, value in descriptive(group[metric].astype(float)).items():
                    item[f"{metric}_{name}"] = value
        output.append(item)
    return output


def aggregate_coefficients(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frame = pd.DataFrame(rows)
    result: list[dict[str, Any]] = []
    for feature, group in frame.groupby("feature", sort=True):
        coefficients = group["coefficient"].astype(float)
        absolute = group["absolute_coefficient"].astype(float)
        result.append({
            "feature": feature,
            "coefficient_mean": float(coefficients.mean()),
            "coefficient_sample_std": float(coefficients.std(ddof=1)),
            "absolute_coefficient_mean": float(absolute.mean()),
            "positive_seed_count": int((coefficients > 0).sum()),
            "negative_seed_count": int((coefficients < 0).sum()),
            "n": int(len(group)),
            "interpretation": "association discriminante dans le modèle",
        })
    ranked = sorted(result, key=lambda row: (-row["absolute_coefficient_mean"], row["feature"]))
    for rank, row in enumerate(ranked, start=1):
        row["absolute_rank"] = rank
    return ranked


def plot_coefficients(rows: list[dict[str, Any]], output: Path) -> None:
    frame = pd.DataFrame(rows).nlargest(20, "absolute_coefficient_mean").sort_values("coefficient_mean")
    colors = ["#b04a5a" if value < 0 else "#2a7185" for value in frame["coefficient_mean"]]
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(frame["feature"], frame["coefficient_mean"], color=colors)
    ax.set_xlabel("Coefficient moyen après standardisation train-only")
    ax.set_title("CSE-CIC-IDS2018 — associations discriminantes de la LR")
    ax.axvline(0, color="black", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_single_features(rows: list[dict[str, Any]], output: Path) -> None:
    frame = pd.DataFrame(rows).sort_values(["f1_mean", "pr_auc_mean"], ascending=False).head(20).sort_values("f1_mean")
    y = np.arange(len(frame))
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(y - 0.18, frame["f1_mean"], 0.36, label="F1")
    ax.barh(y + 0.18, frame["pr_auc_mean"], 0.36, label="PR-AUC")
    ax.set_yticks(y, frame["feature"])
    ax.set_xlim(0, 1.02)
    ax.set_title("CSE-CIC-IDS2018 — meilleures baselines mono-feature")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_ablation(rows: list[dict[str, Any]], output: Path) -> None:
    frame = pd.DataFrame(rows).sort_values("removed_count")
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    for metric in ("f1_mean", "pr_auc_mean", "mcc_mean", "recall_mean"):
        ax.plot(frame["removed_count"], frame[metric], marker="o", label=metric.removesuffix("_mean").upper())
    ax.set_xticks(frame["removed_count"])
    ax.set_ylim(-0.05, 1.03)
    ax.set_xlabel("Nombre de caractéristiques dominantes retirées")
    ax.set_ylabel("Score moyen")
    ax.set_title("CSE-CIC-IDS2018 — ablation figée sur classement train-only")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def plot_permutation(observed: list[dict[str, Any]], permuted: list[dict[str, Any]], output: Path) -> None:
    left = pd.DataFrame(observed).set_index("seed")
    right = pd.DataFrame(permuted).set_index("seed")
    seeds = sorted(set(left.index) & set(right.index))
    x = np.arange(len(seeds))
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.bar(x - 0.2, left.loc[seeds, "f1"], 0.4, label="Labels réels")
    ax.bar(x + 0.2, right.loc[seeds, "f1"], 0.4, label="Labels permutés")
    ax.set_xticks(x, [str(seed) for seed in seeds])
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("Graine")
    ax.set_ylabel("F1 test")
    ax.set_title("CSE-CIC-IDS2018 — contrôle négatif par permutation")
    ax.legend()
    fig.tight_layout()
    fig.savefig(output, dpi=180)
    plt.close(fig)


def choose_conclusion(permutation_summary: dict[str, Any], ablation_summary: list[dict[str, Any]], config: dict[str, Any]) -> str:
    guard = config["p1"]["negative_control_guard"]
    if permutation_summary["f1_mean"] >= guard["max_f1"] or permutation_summary["pr_auc_mean"] >= guard["max_pr_auc"]:
        return "C"
    by_removed = {int(row["removed_count"]): row for row in ablation_summary}
    drop = by_removed[0]["f1_mean"] - by_removed[10]["f1_mean"]
    return "B" if drop >= config["p1"]["dominant_feature_f1_drop"] else "A"


def main() -> int:
    ensure_phase_dirs()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    principal_path = latest_principal_manifest()
    principal = json.loads(principal_path.read_text(encoding="utf-8"))
    principal_run = principal["run_id"]
    train_pool_path = SOURCE_PHASE / "processed" / f"{principal_run}_train_pool.csv.gz"
    test_pool_path = SOURCE_PHASE / "processed" / f"{principal_run}_test_pool.csv.gz"
    if not train_pool_path.exists() or not test_pool_path.exists():
        raise FileNotFoundError("Pools CSE-CIC-IDS2018 figés absents.")

    current_run = run_id("final_csecic_lr_forensic")
    started_at = utc_now()
    error_path = PHASE_ROOT / "logs" / f"{current_run}_error.txt"
    append_ledger(
        experiment_id=EXPERIMENT_ID, phase="P1", run_id=current_run,
        dataset="CSE-CIC-IDS2018", protocol="temporal_forensic_controls_train15_test16",
        status="RUNNING", started_at=started_at,
        command="python scripts/run_final_csecicids2018_lr_forensic.py",
        error_path=relative(error_path),
    )
    try:
        train_pool = pd.read_csv(train_pool_path)
        test_pool = pd.read_csv(test_pool_path)
        features = [column for column in train_pool.columns if column not in META_COLUMNS]
        if len(features) != int(config["p1"]["single_feature_count"]):
            raise AssertionError(f"78 caractéristiques attendues, {len(features)} observées.")
        seeds = [int(seed) for seed in config["seeds"]]
        per_class = int(principal["protocol"]["sampling"]["sample_per_class_per_seed"])

        observed_rows: list[dict[str, Any]] = []
        permutation_rows: list[dict[str, Any]] = []
        single_rows: list[dict[str, Any]] = []
        coefficients_raw: list[dict[str, Any]] = []
        ablation_rows: list[dict[str, Any]] = []

        for seed in seeds:
            train = seed_sample(train_pool, per_class=per_class, seed=seed)
            test = seed_sample(test_pool, per_class=per_class, seed=seed)
            x_train = train[features]
            y_train = train["target"].astype(np.int8)
            x_test = test[features]
            y_test = test["target"].astype(np.int8)

            fitted = fit_lr(x_train, y_train, seed)
            observed = {"run_id": current_run, "seed": seed, "condition": "real_labels", **evaluate(fitted, x_test, y_test)}
            observed_rows.append(observed)
            coefficients_raw.extend(coefficient_rows(fitted, features, seed))
            ranking = training_only_ranking(fitted, features)

            permuted_model = fit_lr(x_train, permute_training_labels(y_train, seed), seed)
            permutation_rows.append({
                "run_id": current_run, "seed": seed, "condition": "permuted_train_labels",
                **evaluate(permuted_model, x_test, y_test),
            })

            for feature in features:
                mono = fit_lr(x_train[[feature]], y_train, seed)
                mono_metrics = evaluate(mono, x_test[[feature]], y_test)
                coefficient = float(mono.named_steps["model"].coef_[0, 0])
                single_rows.append({
                    "run_id": current_run, "seed": seed, "feature": feature,
                    **mono_metrics, "coefficient": coefficient,
                })

            for removed_count in config["p1"]["ablation_levels"]:
                removed = ranking[: int(removed_count)]
                retained = [feature for feature in features if feature not in set(removed)]
                ablated = fit_lr(x_train[retained], y_train, seed)
                ablation_rows.append({
                    "run_id": current_run, "seed": seed, "removed_count": int(removed_count),
                    "retained_count": len(retained), "removed_features": " | ".join(removed),
                    "ranking_source": "training_fit_only", **evaluate(ablated, x_test[retained], y_test),
                })

        single_summary = aggregate_by(single_rows, ["feature"])
        ablation_summary = aggregate_by(ablation_rows, ["removed_count", "retained_count"])
        coefficient_summary = aggregate_coefficients(coefficients_raw)
        permutation_summary = aggregate_by(permutation_rows, ["condition"])[0]
        observed_summary = aggregate_by(observed_rows, ["condition"])[0]
        conclusion = choose_conclusion(permutation_summary, ablation_summary, config)

        paths = {
            "observed": PHASE_ROOT / "raw" / f"{current_run}_observed_metrics.csv",
            "permutation": PHASE_ROOT / "raw" / f"{current_run}_label_permutation.csv",
            "single_raw": PHASE_ROOT / "raw" / f"{current_run}_single_feature_by_seed.csv",
            "coeff_raw": PHASE_ROOT / "raw" / f"{current_run}_coefficients_by_seed.csv",
            "ablation_raw": PHASE_ROOT / "raw" / f"{current_run}_ablation_by_seed.csv",
            "single": PHASE_ROOT / "aggregated" / "external_csecicids2018_single_feature_scores.csv",
            "coeff": PHASE_ROOT / "aggregated" / "external_csecicids2018_lr_coefficients.csv",
            "ablation": PHASE_ROOT / "aggregated" / "external_csecicids2018_feature_ablation.csv",
            "summary": PHASE_ROOT / "aggregated" / "external_csecicids2018_lr_forensic_summary.json",
            "report": PHASE_ROOT / "reports" / "CSE_CIC_IDS2018_LR_FORENSIC_AUDIT.md",
        }
        write_csv(paths["observed"], observed_rows)
        write_csv(paths["permutation"], permutation_rows)
        write_csv(paths["single_raw"], single_rows)
        write_csv(paths["coeff_raw"], coefficients_raw)
        write_csv(paths["ablation_raw"], ablation_rows)
        write_csv(paths["single"], single_summary)
        write_csv(paths["coeff"], coefficient_summary)
        write_csv(paths["ablation"], ablation_summary)

        figures = [
            PHASE_ROOT / "figures" / "dataset_12_external_lr_coefficients.png",
            PHASE_ROOT / "figures" / "dataset_13_external_single_feature_scores.png",
            PHASE_ROOT / "figures" / "dataset_14_external_feature_ablation.png",
            PHASE_ROOT / "figures" / "dataset_15_external_label_permutation.png",
        ]
        plot_coefficients(coefficient_summary, figures[0])
        plot_single_features(single_summary, figures[1])
        plot_ablation(ablation_summary, figures[2])
        plot_permutation(observed_rows, permutation_rows, figures[3])

        top_positive = sorted(coefficient_summary, key=lambda row: (-row["coefficient_mean"], row["feature"]))[:10]
        top_negative = sorted(coefficient_summary, key=lambda row: (row["coefficient_mean"], row["feature"]))[:10]
        top_absolute = coefficient_summary[:10]
        summary = {
            "run_id": current_run,
            "principal_run_id": principal_run,
            "feature_count": len(features),
            "seeds": seeds,
            "observed": observed_summary,
            "label_permutation": permutation_summary,
            "best_single_feature_by_f1": max(single_summary, key=lambda row: row["f1_mean"]),
            "best_single_feature_by_pr_auc": max(single_summary, key=lambda row: row["pr_auc_mean"]),
            "top_positive_coefficients": top_positive,
            "top_negative_coefficients": top_negative,
            "top_absolute_coefficients": top_absolute,
            "ablation": ablation_summary,
            "conclusion": conclusion,
            "assertions": {
                "train_test_files_distinct": principal["audit"]["assertions"]["partitions_are_distinct_files"],
                "scaler_fit_train_only": True,
                "permutation_changes_train_labels_only": True,
                "ablation_levels_frozen_before_execution": config["p1"]["ablation_levels"] == [0, 1, 3, 5, 10],
                "ablation_ranking_training_only": True,
                "test_used_for_feature_ranking": False
            },
        }
        write_json(paths["summary"], summary)

        conclusion_text = {
            "A": "A — aucune fuite évidente détectée par les contrôles exécutés",
            "B": "B — performance très dépendante de quelques features",
            "C": "C — anomalie méthodologique détectée, résultat principal à requalifier",
        }[conclusion]
        report_lines = [
            "# Audit forensique de la LogisticRegression sur CSE-CIC-IDS2018", "",
            f"Run : `{current_run}`. Protocole : 15 février 2018 pour l’apprentissage et 16 février 2018 pour le test, avec cinq graines et 10 000 observations par classe et par partition.", "",
            "## Contrôle négatif par permutation", "",
            f"La permutation porte uniquement sur `y_train`. Le F1 moyen est `{permutation_summary['f1_mean']:.6f}`, la PR-AUC `{permutation_summary['pr_auc_mean']:.6f}` et le MCC `{permutation_summary['mcc_mean']:.6f}`. Les labels et caractéristiques de test restent inchangés.", "",
            "## Baselines mono-feature", "",
            f"La meilleure baseline selon F1 est `{summary['best_single_feature_by_f1']['feature']}` avec `{summary['best_single_feature_by_f1']['f1_mean']:.6f}`. Selon PR-AUC, il s’agit de `{summary['best_single_feature_by_pr_auc']['feature']}` avec `{summary['best_single_feature_by_pr_auc']['pr_auc_mean']:.6f}`.", "",
            "## Coefficients", "",
            "Les coefficients sont extraits après ajustement du `StandardScaler` et de la LR sur le train uniquement. Ils décrivent une association discriminante dans le modèle et non une cause de l’attaque.", "",
            "## Ablation", "",
            "Les niveaux 1/3/5/10 ont été gelés avant exécution. Le classement des variables est recalculé pour chaque graine à partir du modèle ajusté sur le train ; aucun résultat test n’intervient dans ce classement.", "",
            "| Variables retirées | Variables conservées | F1 moyen | PR-AUC moyenne | MCC moyen | Rappel moyen | FPR moyen |", "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in sorted(ablation_summary, key=lambda item: item["removed_count"]):
            report_lines.append(f"| {int(row['removed_count'])} | {int(row['retained_count'])} | {row['f1_mean']:.6f} | {row['pr_auc_mean']:.6f} | {row['mcc_mean']:.6f} | {row['recall_mean']:.6f} | {row['fpr_mean']:.6f} |")
        report_lines.extend([
            "", "## Conclusion", "", conclusion_text + ".", "",
            "Les contrôles exécutés n’ont pas mis en évidence de fuite triviale correspondant aux mécanismes testés." if conclusion != "C" else "Le contrôle négatif impose de requalifier le résultat principal avant toute interprétation.", "",
            "Cette conclusion ne signifie pas qu’aucune autre fuite est possible. Elle reste limitée aux contrôles exécutés et au holdout de deux journées DoS.", "",
            "## Artefacts", "",
            *[f"- `{relative(path)}`" for path in [*paths.values(), *figures]],
        ])
        paths["report"].write_text("\n".join(report_lines) + "\n", encoding="utf-8")

        manifest_path = PHASE_ROOT / "manifests" / f"{current_run}_manifest.json"
        write_json(manifest_path, {
            "run_id": current_run, "experiment_id": EXPERIMENT_ID, "status": "COMPLETED",
            "config": {"path": relative(CONFIG_PATH), "sha256": sha256_file(CONFIG_PATH)},
            "principal_manifest": {"path": relative(principal_path), "sha256": sha256_file(principal_path)},
            "inputs": [
                {"path": relative(train_pool_path), "sha256": sha256_file(train_pool_path)},
                {"path": relative(test_pool_path), "sha256": sha256_file(test_pool_path)},
            ],
            "raw_sources": principal["sources"],
            "artifacts": [{"path": relative(path), "sha256": sha256_file(path)} for path in [*paths.values(), *figures] if path.exists()],
            "conclusion": conclusion,
        })
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P1", run_id=current_run,
            dataset="CSE-CIC-IDS2018", protocol="temporal_forensic_controls_train15_test16",
            status="COMPLETED", started_at=started_at, completed_at=utc_now(),
            command="python scripts/run_final_csecicids2018_lr_forensic.py",
            raw_result_path=relative(paths["permutation"]), summary_path=relative(paths["summary"]),
            figure_path=" | ".join(relative(path) for path in figures), error_path=relative(error_path),
            notes=f"Conclusion {conclusion}; 78 mono-features; ablations 0/1/3/5/10 train-only.",
        )
        print(json.dumps({"status": "COMPLETED", "run_id": current_run, "conclusion": conclusion, "summary": relative(paths["summary"])}, ensure_ascii=False))
        return 0
    except Exception as exc:
        error_path.write_text(f"{type(exc).__name__}: {exc}\n", encoding="utf-8")
        append_ledger(
            experiment_id=EXPERIMENT_ID, phase="P1", run_id=current_run,
            dataset="CSE-CIC-IDS2018", protocol="temporal_forensic_controls_train15_test16",
            status="FAILED", started_at=started_at, completed_at=utc_now(),
            command="python scripts/run_final_csecicids2018_lr_forensic.py",
            error_path=relative(error_path), notes=f"{type(exc).__name__}: {exc}",
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
