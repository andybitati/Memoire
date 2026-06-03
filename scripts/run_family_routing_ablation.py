"""Run a family-aware routing ablation for the Logminer paper.

The experiment compares a monolithic classifier trained on a minimal common
feature space against one classifier per log family trained on the same feature
space and evaluated on the same held-out split.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


COMMON_NUMERIC = [
    "duration",
    "src_port",
    "dst_port",
    "packet_count",
    "byte_count",
    "rate",
    "attempts",
    "hour",
    "weekday",
    "numeric_mean",
    "numeric_std",
    "numeric_max",
    "numeric_nonzero_ratio",
]
COMMON_CATEGORICAL = ["protocol", "service", "state", "status"]
COMMON_FEATURES = COMMON_NUMERIC + COMMON_CATEGORICAL


def _metric_row(variant: str, family: str, y_true: pd.Series, y_pred: np.ndarray, rows: int) -> dict[str, object]:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "variant": variant,
        "family": family,
        "test_rows": int(rows),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "false_positive_rate": float(fp / (fp + tn)) if (fp + tn) else 0.0,
        "false_positives_per_1000": float(fp / rows * 1000) if rows else 0.0,
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
    }


def _balanced(frame: pd.DataFrame, *, normal: int, anomaly: int, random_state: int) -> pd.DataFrame:
    normal_df = frame[frame["target"] == 0]
    anomaly_df = frame[frame["target"] == 1]
    if len(normal_df) > normal:
        normal_df = normal_df.sample(normal, random_state=random_state)
    if len(anomaly_df) > anomaly:
        anomaly_df = anomaly_df.sample(anomaly, random_state=random_state)
    return pd.concat([normal_df, anomaly_df], ignore_index=True).sample(frac=1, random_state=random_state)


def _numeric_summary(frame: pd.DataFrame) -> pd.DataFrame:
    numeric = frame.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    return pd.DataFrame(
        {
            "numeric_mean": numeric.mean(axis=1).fillna(0),
            "numeric_std": numeric.std(axis=1).fillna(0),
            "numeric_max": numeric.max(axis=1).fillna(0),
            "numeric_nonzero_ratio": numeric.fillna(0).ne(0).mean(axis=1).fillna(0),
        },
        index=frame.index,
    )


def load_linux_auth(path: Path, *, normal: int, anomaly: int, random_state: int) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    normal_seen = anomaly_seen = 0
    for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=100_000):
        labels = chunk["anomaly_label"].astype(str).str.lower().str.strip()
        chunk = chunk.assign(target=(labels.ne("normal")).astype(int))
        normal_part = chunk[chunk["target"] == 0].head(max(0, normal - normal_seen))
        anomaly_part = chunk[chunk["target"] == 1].head(max(0, anomaly - anomaly_seen))
        if not normal_part.empty:
            parts.append(normal_part)
            normal_seen += len(normal_part)
        if not anomaly_part.empty:
            parts.append(anomaly_part)
            anomaly_seen += len(anomaly_part)
        if normal_seen >= normal and anomaly_seen >= anomaly:
            break

    raw = pd.concat(parts, ignore_index=True)
    ts = pd.to_datetime(raw["timestamp"], errors="coerce", utc=True)
    prepared = pd.DataFrame(index=raw.index)
    prepared["family"] = "linux_auth"
    prepared["target"] = raw["target"].astype(int)
    prepared["duration"] = 0
    prepared["src_port"] = 0
    prepared["dst_port"] = pd.to_numeric(raw.get("port", 0), errors="coerce").fillna(0)
    prepared["packet_count"] = 0
    prepared["byte_count"] = 0
    prepared["rate"] = 0
    prepared["attempts"] = pd.to_numeric(raw.get("attempts", 0), errors="coerce").fillna(0)
    prepared["hour"] = ts.dt.hour.fillna(0).astype(int)
    prepared["weekday"] = ts.dt.weekday.fillna(0).astype(int)
    prepared["protocol"] = raw.get("protocol", "").astype(str).fillna("")
    prepared["service"] = raw.get("service", "").astype(str).fillna("")
    prepared["state"] = ""
    prepared["status"] = raw.get("status", "").astype(str).fillna("")
    summary = _numeric_summary(prepared[["dst_port", "attempts", "hour", "weekday"]])
    return pd.concat([prepared, summary], axis=1)


def load_cicids(input_dir: Path, *, normal: int, anomaly: int, random_state: int) -> pd.DataFrame:
    parts: list[pd.DataFrame] = []
    normal_seen = anomaly_seen = 0
    for csv_path in sorted(input_dir.glob("*.csv")):
        for chunk in pd.read_csv(csv_path, dtype=str, keep_default_na=False, chunksize=100_000, encoding_errors="ignore"):
            chunk.columns = [str(c).strip().lstrip("\ufeff") for c in chunk.columns]
            label_col = next(c for c in chunk.columns if c.lower() == "label")
            labels = chunk[label_col].astype(str).str.strip().str.upper()
            chunk = chunk.assign(target=(labels.ne("BENIGN")).astype(int))
            normal_part = chunk[chunk["target"] == 0].head(max(0, normal - normal_seen))
            anomaly_part = chunk[chunk["target"] == 1].head(max(0, anomaly - anomaly_seen))
            if not normal_part.empty:
                parts.append(normal_part)
                normal_seen += len(normal_part)
            if not anomaly_part.empty:
                parts.append(anomaly_part)
                anomaly_seen += len(anomaly_part)
            if normal_seen >= normal and anomaly_seen >= anomaly:
                break
        if normal_seen >= normal and anomaly_seen >= anomaly:
            break

    raw = pd.concat(parts, ignore_index=True)
    numeric_cols = raw.drop(columns=[c for c in raw.columns if c.lower() == "label"] + ["target"], errors="ignore")
    summary = _numeric_summary(numeric_cols.astype(str).replace(["Infinity", "INF", "-Infinity"], np.nan))
    prepared = pd.DataFrame(index=raw.index)
    prepared["family"] = "cicids"
    prepared["target"] = raw["target"].astype(int)
    prepared["duration"] = pd.to_numeric(raw.get("Flow Duration", 0), errors="coerce").fillna(0)
    prepared["src_port"] = 0
    prepared["dst_port"] = pd.to_numeric(raw.get("Destination Port", 0), errors="coerce").fillna(0)
    prepared["packet_count"] = (
        pd.to_numeric(raw.get("Total Fwd Packets", 0), errors="coerce").fillna(0)
        + pd.to_numeric(raw.get("Total Backward Packets", 0), errors="coerce").fillna(0)
    )
    prepared["byte_count"] = (
        pd.to_numeric(raw.get("Total Length of Fwd Packets", 0), errors="coerce").fillna(0)
        + pd.to_numeric(raw.get("Total Length of Bwd Packets", 0), errors="coerce").fillna(0)
    )
    prepared["rate"] = pd.to_numeric(raw.get("Flow Packets/s", 0), errors="coerce").fillna(0)
    prepared["attempts"] = 0
    prepared["hour"] = 0
    prepared["weekday"] = 0
    prepared["protocol"] = "flow"
    prepared["service"] = ""
    prepared["state"] = ""
    prepared["status"] = ""
    return pd.concat([prepared, summary], axis=1)


def load_unsw(train_path: Path, test_path: Path, *, normal: int, anomaly: int, random_state: int) -> pd.DataFrame:
    raw = pd.concat([pd.read_parquet(train_path), pd.read_parquet(test_path)], ignore_index=True)
    raw = raw.assign(target=pd.to_numeric(raw["label"], errors="coerce").fillna(0).astype(int))
    raw = _balanced(raw, normal=normal, anomaly=anomaly, random_state=random_state)
    summary = _numeric_summary(raw.drop(columns=["label", "attack_cat"], errors="ignore").astype(str))
    prepared = pd.DataFrame(index=raw.index)
    prepared["family"] = "unsw"
    prepared["target"] = raw["target"].astype(int)
    prepared["duration"] = pd.to_numeric(raw.get("dur", 0), errors="coerce").fillna(0)
    prepared["src_port"] = 0
    prepared["dst_port"] = 0
    prepared["packet_count"] = (
        pd.to_numeric(raw.get("spkts", 0), errors="coerce").fillna(0)
        + pd.to_numeric(raw.get("dpkts", 0), errors="coerce").fillna(0)
    )
    prepared["byte_count"] = (
        pd.to_numeric(raw.get("sbytes", 0), errors="coerce").fillna(0)
        + pd.to_numeric(raw.get("dbytes", 0), errors="coerce").fillna(0)
    )
    prepared["rate"] = pd.to_numeric(raw.get("rate", 0), errors="coerce").fillna(0)
    prepared["attempts"] = 0
    prepared["hour"] = 0
    prepared["weekday"] = 0
    prepared["protocol"] = raw.get("proto", "").astype(str).fillna("")
    prepared["service"] = raw.get("service", "").astype(str).fillna("")
    prepared["state"] = raw.get("state", "").astype(str).fillna("")
    prepared["status"] = ""
    return pd.concat([prepared, summary], axis=1)


def make_model(random_state: int) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
                COMMON_NUMERIC,
            ),
            (
                "cat",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore", min_frequency=5)),
                    ]
                ),
                COMMON_CATEGORICAL,
            ),
        ]
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=120,
                    max_depth=22,
                    min_samples_leaf=2,
                    class_weight="balanced",
                    random_state=random_state,
                    n_jobs=1,
                ),
            ),
        ]
    )


def write_table(metrics: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        "# Ablation Routage Familial",
        "",
        "| Variante | Famille | Lignes test | Precision | Rappel | F1 | Faux positifs / 1000 |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for _, row in metrics.sort_values(["family", "variant"]).iterrows():
        rows.append(
            "| {variant} | {family} | {test_rows} | {precision:.6f} | {recall:.6f} | {f1:.6f} | {false_positives_per_1000:.3f} |".format(
                **row
            )
        )
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def _read_metric(path: Path, *, sep: str = ",") -> dict[str, float]:
    frame = pd.read_csv(path, sep=sep)
    row = frame.iloc[0].to_dict()
    return {
        "precision": float(row["precision"]),
        "recall": float(row["recall"]),
        "f1": float(row["f1"]),
        "fp": float(row["fp"]),
        "tn": float(row["tn"]),
        "test_rows": float(row.get("test_rows", row.get("events", 0))),
    }


def write_operational_table(common_metrics: pd.DataFrame, output: Path) -> None:
    """Compare the common global baseline with full specialized configurations.

    This table is intentionally labelled as operational because specialized
    models use their native feature spaces, whereas the global model is limited
    to the minimal common feature space required by heterogeneous logs.
    """

    specialized = {
        "linux_auth": _read_metric(Path("data/processed/random_forest_linux_auth_metrics.csv")),
        "cicids": _read_metric(Path("data/processed/random_forest_network_cicids_metrics.csv")),
        "unsw": _read_metric(Path("data/random_forest_unsw_80_20_metrics.csv"), sep=";"),
    }
    rows = [
        "# Ablation Operationnelle Routage Familial",
        "",
        "Comparaison entre une baseline globale limitee a un espace commun minimal et les configurations specialisees completes.",
        "",
        "| Famille | Global common F1 | Family-aware full F1 | Delta F1 | Global FP/1000 | Family-aware FP/1000 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for family in ["linux_auth", "cicids", "unsw"]:
        global_row = common_metrics[
            (common_metrics["variant"] == "global_common_model") & (common_metrics["family"] == family)
        ].iloc[0]
        spec = specialized[family]
        spec_fp_per_1000 = spec["fp"] / spec["test_rows"] * 1000 if spec["test_rows"] else 0.0
        rows.append(
            "| {family} | {global_f1:.6f} | {spec_f1:.6f} | {delta:.6f} | {global_fp:.3f} | {spec_fp:.3f} |".format(
                family=family,
                global_f1=float(global_row["f1"]),
                spec_f1=spec["f1"],
                delta=spec["f1"] - float(global_row["f1"]),
                global_fp=float(global_row["false_positives_per_1000"]),
                spec_fp=spec_fp_per_1000,
            )
        )
    rows.extend(
        [
            "",
            "Interpretation: the controlled common-space ablation isolates routing under the same feature space, while this operational comparison measures the full Logminer contribution: family detection, native feature compatibility and specialized model selection.",
        ]
    )
    output.write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_svg(metrics: pd.DataFrame, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    families = list(metrics["family"].drop_duplicates())
    variants = ["global_common_model", "family_aware_models"]
    width = 980
    height = 130 + len(families) * 90
    left = 180
    right = 920
    max_f1 = 1.0
    colors = {"global_common_model": "#8aa6c1", "family_aware_models": "#d9822b"}
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172026}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#5b6770}.label{font-size:12px}.axis{font-size:11px;fill:#5b6770}</style>",
        '<text x="36" y="36" class="title">Family-aware routing ablation</text>',
        '<text x="36" y="58" class="sub">Global common model vs specialized models on the same supervised split</text>',
    ]
    for tick in [0, 0.25, 0.5, 0.75, 1.0]:
        x = left + (right - left) * tick / max_f1
        lines.append(f'<line x1="{x:.1f}" y1="76" x2="{x:.1f}" y2="{height-38}" stroke="#d9dee3"/>')
        lines.append(f'<text x="{x:.1f}" y="{height-16}" text-anchor="middle" class="axis">{tick:.2f}</text>')
    for idx, family in enumerate(families):
        y = 100 + idx * 90
        lines.append(f'<text x="{left-12}" y="{y+22}" text-anchor="end" class="label">{family}</text>')
        for offset, variant in enumerate(variants):
            found = metrics[(metrics["family"] == family) & (metrics["variant"] == variant)]
            if found.empty:
                continue
            value = float(found.iloc[0]["f1"])
            bar_w = (right - left) * value / max_f1
            yy = y + offset * 28
            lines.append(f'<rect x="{left}" y="{yy}" width="{bar_w:.1f}" height="20" rx="3" fill="{colors[variant]}"/>')
            lines.append(f'<text x="{left + bar_w + 8:.1f}" y="{yy+15}" class="label">{value:.3f}</text>')
    lines.append(f'<rect x="650" y="28" width="16" height="16" fill="{colors["global_common_model"]}"/><text x="672" y="41" class="label">Global model</text>')
    lines.append(f'<rect x="780" y="28" width="16" height="16" fill="{colors["family_aware_models"]}"/><text x="802" y="41" class="label">Family-aware</text>')
    lines.append("</svg>")
    output.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Logminer family routing ablation")
    parser.add_argument("--per-class", type=int, default=6000, help="Rows per class and per family")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--linux-auth", type=Path, default=Path("data/raw/Datasets/linux_auth_logs_labeled.csv"))
    parser.add_argument("--cicids-dir", type=Path, default=Path("data/raw/Datasets/MachineLearningCSV/MachineLearningCVE"))
    parser.add_argument("--unsw-train", type=Path, default=Path("data/raw/Datasets/UNSW_NB15_training-set.parquet"))
    parser.add_argument("--unsw-test", type=Path, default=Path("data/raw/Datasets/UNSW_NB15_testing-set.parquet"))
    args = parser.parse_args(argv)

    frames = [
        load_linux_auth(args.linux_auth, normal=args.per_class, anomaly=args.per_class, random_state=args.random_state),
        load_cicids(args.cicids_dir, normal=args.per_class, anomaly=args.per_class, random_state=args.random_state),
        load_unsw(args.unsw_train, args.unsw_test, normal=args.per_class, anomaly=args.per_class, random_state=args.random_state),
    ]
    dataset = pd.concat(frames, ignore_index=True).sample(frac=1, random_state=args.random_state)
    dataset = dataset.replace([np.inf, -np.inf], np.nan)

    train_parts = []
    test_parts = []
    for family, group in dataset.groupby("family"):
        stratify = group["target"].astype(str)
        train, test = train_test_split(group, test_size=0.25, stratify=stratify, random_state=args.random_state)
        train_parts.append(train)
        test_parts.append(test)
    train_df = pd.concat(train_parts, ignore_index=True)
    test_df = pd.concat(test_parts, ignore_index=True)

    metrics: list[dict[str, object]] = []
    global_model = make_model(args.random_state)
    global_model.fit(train_df[COMMON_FEATURES], train_df["target"])
    for family, test_group in test_df.groupby("family"):
        pred = global_model.predict(test_group[COMMON_FEATURES])
        metrics.append(_metric_row("global_common_model", family, test_group["target"], pred, len(test_group)))

    for family, train_group in train_df.groupby("family"):
        model = make_model(args.random_state)
        model.fit(train_group[COMMON_FEATURES], train_group["target"])
        test_group = test_df[test_df["family"] == family]
        pred = model.predict(test_group[COMMON_FEATURES])
        metrics.append(_metric_row("family_aware_models", family, test_group["target"], pred, len(test_group)))

    out_csv = Path("data/processed/family_routing_ablation.csv")
    out_table = Path("docs/memoire/tables/table_family_routing_ablation.md")
    out_operational_table = Path("docs/memoire/tables/table_family_routing_operational_ablation.md")
    out_svg = Path("docs/memoire/figures/fig_family_routing_ablation.svg")
    metrics_df = pd.DataFrame(metrics)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    write_table(metrics_df, out_table)
    write_operational_table(metrics_df, out_operational_table)
    write_svg(metrics_df, out_svg)

    print(f"Ablation CSV: {out_csv}")
    print(f"Table: {out_table}")
    print(f"Operational table: {out_operational_table}")
    print(f"Figure: {out_svg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
