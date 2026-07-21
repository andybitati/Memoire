"""Build final supervised proof CSVs and thesis tables."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


STRICT_COLUMNS = [
    "dataset",
    "seed",
    "split",
    "train_rows",
    "test_rows",
    "train_positive_rate",
    "test_positive_rate",
    "precision",
    "recall",
    "f1",
    "accuracy",
    "pr_auc",
    "mcc",
    "tn",
    "fp",
    "fn",
    "tp",
    "notes",
]


def _add_proof_columns(frame: pd.DataFrame, *, n_estimators: int, max_depth: int) -> pd.DataFrame:
    out = frame.copy()
    defaults = {
        "model": "RandomForest",
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "min_samples_leaf": 2,
        "class_weight": "balanced",
        "features": "pipeline documented in scripts; numeric network-flow columns for network datasets; mixed numeric/categorical auth features for Linux",
    }
    insert_at = 1
    for column, value in defaults.items():
        if column not in out.columns:
            out.insert(insert_at, column, value)
        insert_at += 1
    return out


def _write_proof(frame: pd.DataFrame, filename: str, *, n_estimators: int, max_depth: int) -> None:
    out = _add_proof_columns(frame, n_estimators=n_estimators, max_depth=max_depth)
    for root in [
        Path("data/processed"),
        Path("docs/memoire/pack_redaction_final/06_reproductibilite_preuves"),
    ]:
        root.mkdir(parents=True, exist_ok=True)
        out.to_csv(root / filename, index=False, encoding="utf-8-sig")


def _write_strict_table(summary: pd.DataFrame) -> None:
    rows = [
        "# Splits Supervises Stricts",
        "",
        "| Dataset | Split | Seeds | Test moy. | Precision | Rappel | F1 | PR-AUC | MCC | FP moy. | FN moy. |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in summary.iterrows():
        rows.append(
            "| {dataset} | {split} | {seeds:.0f} | {test_rows:.0f} | {precision:.6f} | {recall:.6f} | {f1:.6f} | {pr_auc:.6f} | {mcc:.6f} | {fp:.1f} | {fn:.1f} |".format(
                **row
            )
        )
    rows.extend(
        [
            "",
            "Note: ces resultats sont calcules sur cinq graines. Les holdouts tiennent hors entrainement des serveurs, fichiers ou scenarios entiers; CICIDS2017 utilise les memes hyperparametres que le modele reseau principal dans la comparaison controlee.",
        ]
    )
    for path in [
        Path("docs/memoire/tables/table_supervised_strict_splits.md"),
        Path("memoire_logminer_latex_overleaf/tables/table_supervised_strict_splits.md"),
        Path("docs/memoire/pack_redaction_final/10_latex_overleaf/tables/table_supervised_strict_splits.md"),
    ]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def main() -> int:
    linux = pd.read_csv("data/processed/supervised_strict_linux_metrics.csv")
    cicddos = pd.read_csv("data/processed/supervised_strict_cicddos_metrics.csv")
    cicids_controlled = pd.read_csv("data/processed/controlled_split_cicids_metrics.csv")
    cicids = cicids_controlled[cicids_controlled["split"].eq("file_or_scenario_holdout")].copy()

    strict = pd.concat(
        [linux[STRICT_COLUMNS], cicids[STRICT_COLUMNS], cicddos[STRICT_COLUMNS]],
        ignore_index=True,
    )
    strict.to_csv("data/processed/supervised_strict_split_metrics.csv", index=False, encoding="utf-8-sig")

    _write_proof(linux, "random_forest_linux_auth_strict_metrics.csv", n_estimators=120, max_depth=24)
    _write_proof(cicids, "random_forest_cicids2017_controlled_split_metrics.csv", n_estimators=100, max_depth=28)
    _write_proof(cicddos, "random_forest_cic_ddos2019_metrics.csv", n_estimators=100, max_depth=28)

    summary = (
        strict.groupby(["dataset", "split"], as_index=False)
        .agg(
            seeds=("seed", "nunique"),
            test_rows=("test_rows", "mean"),
            precision=("precision", "mean"),
            precision_std=("precision", "std"),
            recall=("recall", "mean"),
            recall_std=("recall", "std"),
            f1=("f1", "mean"),
            f1_std=("f1", "std"),
            pr_auc=("pr_auc", "mean"),
            pr_auc_std=("pr_auc", "std"),
            mcc=("mcc", "mean"),
            mcc_std=("mcc", "std"),
            fp=("fp", "mean"),
            fn=("fn", "mean"),
        )
        .sort_values(["dataset", "split"])
    )
    summary.to_csv("data/processed/supervised_strict_split_summary.csv", index=False, encoding="utf-8-sig")
    _write_strict_table(summary)
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
