"""Construit les statistiques transversales sans pseudo-réplication."""

from __future__ import annotations

import argparse
import csv
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import t as student_t


ROOT = Path(__file__).resolve().parents[1]
DOC_ROOT = ROOT / "docs" / "memoire" / "final_experiments_2026"
DATA_ROOT = ROOT / "data" / "processed" / "final_experiments_2026"
CONFIG_PATH = DOC_ROOT / "configs" / "transversal_statistics_protocol.json"
LEDGER_PATH = DOC_ROOT / "state" / "EXPERIMENT_LEDGER.csv"
REPEATED_PATH = DATA_ROOT / "transversal_repeated_statistics.csv"
EFFECTS_PATH = DATA_ROOT / "cicids_model_scenario_effects.csv"
SINGLE_PATH = DATA_ROOT / "transversal_single_evaluations.csv"
REPORT_PATH = DOC_ROOT / "experiment_transversal_statistics_summary.md"
TABLE_PATH = DOC_ROOT / "tables" / "transversal_statistics_key_results.md"
EXPERIMENT_ID = "e9_transversal_statistics"
METRICS = ["f1", "precision", "recall", "pr_auc", "mcc", "fpr"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def current_git_commit() -> str:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, check=False)
    return result.stdout.strip() if result.returncode == 0 else ""


def append_ledger(status: str, started: str, completed: str = "", notes: str = "") -> None:
    row = {
        "experiment_id": EXPERIMENT_ID,
        "phase": "9",
        "run_id": EXPERIMENT_ID,
        "dataset": "cross-experiment summaries",
        "scenario": "descriptive statistics without pseudo-replication",
        "seed": "",
        "model": "",
        "status": status,
        "started_at": started,
        "completed_at": completed,
        "command": "scripts/build_transversal_statistics.py --resume",
        "config_path": str(CONFIG_PATH.relative_to(ROOT)).replace("\\", "/"),
        "raw_result_path": str(REPEATED_PATH.relative_to(ROOT)).replace("\\", "/"),
        "summary_path": str(REPORT_PATH.relative_to(ROOT)).replace("\\", "/"),
        "figure_path": "",
        "error_path": "",
        "git_commit": current_git_commit(),
        "notes": notes,
    }
    with LEDGER_PATH.open("r", encoding="utf-8", newline="") as handle:
        fields = next(csv.reader(handle))
    with LEDGER_PATH.open("a", encoding="utf-8", newline="") as handle:
        csv.DictWriter(handle, fieldnames=fields, lineterminator="\n").writerow(row)


def completed_is_valid() -> bool:
    if not all(path.exists() and path.stat().st_size > 0 for path in [REPEATED_PATH, EFFECTS_PATH, SINGLE_PATH, REPORT_PATH, TABLE_PATH]):
        return False
    try:
        repeated = pd.read_csv(REPEATED_PATH)
    except Exception:
        return False
    return len(repeated) == 228 and set(repeated["metric"]) == set(METRICS)


def summarize_group(values: pd.Series) -> dict[str, float | int | str]:
    clean = pd.to_numeric(values, errors="coerce").dropna().astype(float)
    n = len(clean)
    if n == 0:
        raise ValueError("Groupe sans valeur métrique")
    mean = float(clean.mean())
    std = float(clean.std(ddof=1)) if n > 1 else math.nan
    if n > 1:
        half = float(student_t.ppf(0.975, df=n - 1) * std / math.sqrt(n))
        low, high = mean - half, mean + half
        ci_method = "Student_t_95_conditional_on_fixed_seeds"
    else:
        low = high = math.nan
        ci_method = "not_applicable_n1"
    return {
        "n": n,
        "mean": mean,
        "sample_std": std,
        "median": float(clean.median()),
        "min": float(clean.min()),
        "max": float(clean.max()),
        "ci95_low": low,
        "ci95_high": high,
        "ci_method": ci_method,
    }


def repeated_statistics() -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    cicids = pd.read_csv(DATA_ROOT / "cicids_model_multiseed_raw.csv")
    for (scenario, model), group in cicids.groupby(["scenario", "model"], sort=True):
        for metric in METRICS:
            rows.append({
                "experiment": "CICIDS scenario holdout",
                "dataset": "CICIDS2017 local copy",
                "scenario": scenario,
                "method": model,
                "metric": metric,
                "experimental_unit": "seed run within fixed scenario-model",
                **summarize_group(group[metric]),
                "interpretation": "conditional dispersion across seeds; same scenario test set",
            })

    random = pd.read_csv(DATA_ROOT / "cicids_random_multiseed_raw.csv")
    for metric in METRICS:
        rows.append({
            "experiment": "CICIDS random stratified control",
            "dataset": "CICIDS2017 local copy",
            "scenario": "RandomStratified",
            "method": "RandomForest",
            "metric": metric,
            "experimental_unit": "seed run within random stratified protocol",
            **summarize_group(random[metric]),
            "interpretation": "optimistic control; not inferentially comparable to scenario holdout",
        })

    for dataset in ["hdfs", "bgl"]:
        frame = pd.read_csv(DATA_ROOT / f"{dataset}_strict_drain3_raw.csv")
        for method, group in frame.groupby("method", sort=True):
            for metric in METRICS:
                rows.append({
                    "experiment": "Strict train-only Drain3",
                    "dataset": dataset.upper(),
                    "scenario": "chronological train-validation-test",
                    "method": method,
                    "metric": metric,
                    "experimental_unit": "seed run" if len(group) > 1 else "deterministic method result",
                    **summarize_group(group[metric]),
                    "interpretation": "conditional dispersion across seeds" if len(group) > 1 else "n=1; no dispersion or CI",
                })

    result = pd.DataFrame(rows)
    if len(result) != 228:
        raise AssertionError(f"228 lignes attendues, obtenu {len(result)}")
    return result


def scenario_effects() -> pd.DataFrame:
    raw = pd.read_csv(DATA_ROOT / "cicids_model_multiseed_raw.csv")
    means = raw.groupby(["scenario", "model"], as_index=False)["f1"].mean()
    pivot = means.pivot(index="scenario", columns="model", values="f1")
    rows = []
    reference = "LogisticRegression"
    for comparator in sorted(model for model in pivot.columns if model != reference):
        diffs = pivot[reference] - pivot[comparator]
        rows.append({
            "reference": reference,
            "comparator": comparator,
            "unit": "scenario-level mean F1",
            "n_scenarios": len(diffs),
            "mean_difference": float(diffs.mean()),
            "median_difference": float(diffs.median()),
            "min_difference": float(diffs.min()),
            "max_difference": float(diffs.max()),
            "reference_wins": int((diffs > 1e-12).sum()),
            "ties": int((diffs.abs() <= 1e-12).sum()),
            "reference_losses": int((diffs < -1e-12).sum()),
            "inferential_test": "not_performed_fixed_five_scenarios",
        })
    return pd.DataFrame(rows)


def single_evaluations() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    benchmark_path = ROOT / "docs" / "memoire" / "pack_redaction_final" / "06_reproductibilite_preuves" / "controlled_monolith_vs_agents.csv"
    benchmark = pd.read_csv(benchmark_path)
    for row in benchmark.to_dict("records"):
        for metric, unit in [
            ("elapsed_sec", "s"),
            ("throughput_tasks_sec", "task/s"),
            ("cpu_core_avg", "% of one logical-core equivalent"),
            ("ram_mb_max", "MiB"),
        ]:
            rows.append({"experiment": "controlled monolith vs agents", "item": row["mode"], "metric": metric, "value": row[metric], "n": 1, "unit": unit, "dispersion": "not_available", "evidence": str(benchmark_path.relative_to(ROOT)).replace("\\", "/")})

    router_path = DATA_ROOT / "router_evaluation_summary.json"
    router = json.loads(router_path.read_text(encoding="utf-8"))
    for metric in ["accuracy", "macro_f1", "fallback_rate", "error_rate"]:
        rows.append({"experiment": "real router evaluation", "item": "81 derived files", "metric": metric, "value": router[metric], "n": 1, "unit": "ratio", "dispersion": "not_available", "evidence": str(router_path.relative_to(ROOT)).replace("\\", "/")})

    correlation_path = DATA_ROOT / "correlation_synthetic_summary.json"
    correlation = json.loads(correlation_path.read_text(encoding="utf-8"))
    for metric in ["pairwise_precision", "pairwise_recall", "pairwise_f1"]:
        rows.append({"experiment": "synthetic controlled correlation", "item": "120 anomalous-event pairs", "metric": metric, "value": correlation[metric], "n": 1, "unit": "ratio", "dispersion": "not_available", "evidence": str(correlation_path.relative_to(ROOT)).replace("\\", "/")})

    multi_path = DATA_ROOT / "multiformat_validation_summary.csv"
    multi = pd.read_csv(multi_path)
    total_raw = int(multi["n_brut"].sum())
    total_normalized = int(multi["n_normalise"].sum())
    rows.append({"experiment": "multiformat functional validation", "item": "8 adapters", "metric": "overall_normalization_rate", "value": total_normalized / total_raw, "n": 1, "unit": "ratio of input units", "dispersion": "not_available", "evidence": str(multi_path.relative_to(ROOT)).replace("\\", "/")})
    return pd.DataFrame(rows)


def write_reports(repeated: pd.DataFrame, effects: pd.DataFrame, single: pd.DataFrame) -> None:
    key = repeated[(repeated["metric"] == "f1") & (((repeated["dataset"] == "CICIDS2017 local copy") & repeated["scenario"].isin(["DDoS", "RandomStratified"])) | repeated["dataset"].isin(["HDFS", "BGL"]))]
    selected = key[((key["scenario"] == "DDoS") & (key["method"].isin(["RandomForest", "LogisticRegression"]))) | (key["scenario"] == "RandomStratified") | ((key["dataset"] == "HDFS") & (key["method"].isin(["Histogram", "EnsembleTrainCalibrated"]))) | ((key["dataset"] == "BGL") & (key["method"].isin(["Histogram", "AutoencoderMLP"])))]
    lines = ["| Expérience | Dataset/scénario | Méthode | N | Moyenne F1 | Écart-type | Médiane | Min | Max | IC95 |", "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in selected.itertuples(index=False):
        std = "N/A" if pd.isna(row.sample_std) else f"{row.sample_std:.6f}"
        ci = "N/A" if pd.isna(row.ci95_low) else f"[{row.ci95_low:.6f}; {row.ci95_high:.6f}]"
        lines.append(f"| {row.experiment} | {row.dataset}/{row.scenario} | {row.method} | {row.n} | {row.mean:.6f} | {std} | {row.median:.6f} | {row.min:.6f} | {row.max:.6f} | {ci} |")
    TABLE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    lr_effect = effects.set_index("comparator")
    rf = lr_effect.loc["RandomForest"]
    report = f"""# Analyse statistique transversale

## Objectif

Uniformiser les statistiques descriptives des campagnes terminées, sans transformer des scénarios, fichiers ou méthodes déterministes en répétitions indépendantes.

## Règles d'unité

- CICIDS: agrégation séparée pour chaque couple scénario–modèle sur les cinq seeds.
- HDFS/BGL: agrégation par dataset–méthode; trois méthodes stochastiques ont N=5, les méthodes déterministes ont N=1.
- Comparaison de modèles CICIDS: différences descriptives entre les cinq moyennes de scénario.
- Routeur, multiformat, corrélation et benchmark architectural: évaluations uniques; aucune dispersion inter-run inventée.
- IC95 de Student uniquement quand N≥2, conditionnel au protocole et aux seeds fixés.
- Aucun test inférentiel: les cinq scénarios sont un ensemble fixe et N=5 seeds est insuffisant pour une inférence transversale crédible.

## Résultats structurants

- RandomForest random stratifié: F1 moyen `0,995142`, écart-type `0,001013`, IC95 `[0,993884; 0,996400]`, N=5.
- RandomForest DDoS holdout: F1 moyen `0,778774`, écart-type `0,001342`, IC95 `[0,777107; 0,780441]`, N=5.
- Le contraste random contre holdout est descriptif seulement, car les unités et les tests diffèrent.
- LogisticRegression a le meilleur F1 macro historique (`0,233670`) sur cinq scénarios, mais face à RandomForest elle gagne {int(rf.reference_wins)} scénario(s), fait {int(rf.ties)} égalité(s) et perd {int(rf.reference_losses)} scénario(s); différence moyenne de scénario `{rf.mean_difference:+.6f}`.
- HDFS Histogram F1 `0,269307` avec N=1; aucune dispersion ni IC ne peut être donnée.
- BGL Histogram F1 `0,913698` avec N=1; aucune dispersion ni IC ne peut être donnée.
- Les tableaux transversaux conservent séparément les évaluations uniques de l'architecture, du routeur, du multiformat et de la corrélation.

## Limites

- Les seeds mesurent une sensibilité conditionnelle, pas la variabilité de nouveaux datasets.
- Les scénarios CICIDS ne sont pas des répétitions identiques.
- Les IC95 N=5 sont larges ou dégénérés lorsque les résultats sont constants; ils ne démontrent pas une généralisation externe.
- Les lignes N=1 ne permettent aucune estimation de variance.
- Aucun test statistique n'est utilisé pour donner artificiellement du poids aux conclusions.

## Artefacts

- `configs/transversal_statistics_protocol.json`.
- `data/processed/final_experiments_2026/transversal_repeated_statistics.csv`.
- `data/processed/final_experiments_2026/cicids_model_scenario_effects.csv`.
- `data/processed/final_experiments_2026/transversal_single_evaluations.csv`.
- `tables/transversal_statistics_key_results.md`.
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps({"experiment_id": EXPERIMENT_ID, "status": "PLANNED", "metrics": len(config["metrics"]), "inferential_tests": "none"}, indent=2))
        return 0
    if args.resume and completed_is_valid():
        print("SKIPPED_ALREADY_COMPLETED")
        return 0
    started = now_iso()
    append_ledger("RUNNING", started)
    repeated = repeated_statistics()
    effects = scenario_effects()
    single = single_evaluations()
    repeated.to_csv(REPEATED_PATH, index=False, encoding="utf-8-sig")
    effects.to_csv(EFFECTS_PATH, index=False, encoding="utf-8-sig")
    single.to_csv(SINGLE_PATH, index=False, encoding="utf-8-sig")
    write_reports(repeated, effects, single)
    completed = now_iso()
    append_ledger("COMPLETED", started, completed, f"repeated_rows={len(repeated)} effects={len(effects)} single_rows={len(single)} inferential_tests=none")
    print(json.dumps({"experiment_id": EXPERIMENT_ID, "status": "COMPLETED", "repeated_rows": len(repeated), "effect_rows": len(effects), "single_rows": len(single), "inferential_tests": "none"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
