"""Split experimental propre pour datasets labellises Logminer.

Le but est d'eviter les validations trop optimistes:
    - HDFS: split par groupe (`block_id`) pour qu'un meme bloc ne soit pas a la
      fois dans train et test;
    - BGL/autres logs horodates: split chronologique par `timestamp_iso`.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd


def _label_counts(frame: pd.DataFrame, label_column: str) -> dict[str, int]:
    if label_column not in frame:
        return {}
    counts = frame[label_column].astype(str).value_counts().sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def _write_outputs(
    train: pd.DataFrame,
    test: pd.DataFrame,
    train_out: Path,
    test_out: Path,
    summary_out: Path,
    *,
    sep: str,
    input_csv: Path,
    strategy: str,
    label_column: str,
) -> None:
    train_out.parent.mkdir(parents=True, exist_ok=True)
    test_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    train.to_csv(train_out, sep=sep, index=False, encoding="utf-8-sig")
    test.to_csv(test_out, sep=sep, index=False, encoding="utf-8-sig")

    summary = pd.DataFrame(
        [
            {
                "input_csv": str(input_csv),
                "strategy": strategy,
                "split": "train",
                "rows": int(len(train)),
                "label_counts": _label_counts(train, label_column),
            },
            {
                "input_csv": str(input_csv),
                "strategy": strategy,
                "split": "test",
                "rows": int(len(test)),
                "label_counts": _label_counts(test, label_column),
            },
        ]
    )
    summary.to_csv(summary_out, sep=sep, index=False, encoding="utf-8-sig")


def split_chronological(frame: pd.DataFrame, *, test_size: float, timestamp_column: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    if timestamp_column not in frame:
        raise ValueError(f"Colonne timestamp introuvable: {timestamp_column}")
    ordered = frame.copy()
    ordered["_split_time"] = pd.to_datetime(ordered[timestamp_column], errors="coerce", utc=True)
    ordered["_split_order"] = range(len(ordered))
    ordered = ordered.sort_values(["_split_time", "_split_order"], na_position="last")
    cutoff = max(1, min(len(ordered) - 1, int(round(len(ordered) * (1 - test_size)))))
    train = ordered.iloc[:cutoff].drop(columns=["_split_time", "_split_order"])
    test = ordered.iloc[cutoff:].drop(columns=["_split_time", "_split_order"])
    return train, test


def split_group_chronological(
    frame: pd.DataFrame,
    *,
    test_size: float,
    group_column: str,
    timestamp_column: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if group_column not in frame:
        raise ValueError(f"Colonne de groupe introuvable: {group_column}")

    working = frame.copy()
    if timestamp_column in working:
        working["_split_time"] = pd.to_datetime(working[timestamp_column], errors="coerce", utc=True)
    else:
        working["_split_time"] = pd.NaT
    working["_split_order"] = range(len(working))

    groups = (
        working.groupby(group_column, dropna=False)
        .agg(first_time=("_split_time", "min"), first_order=("_split_order", "min"), rows=("_split_order", "count"))
        .reset_index()
        .sort_values(["first_time", "first_order"], na_position="last")
    )

    target_test_rows = max(1, int(round(len(working) * test_size)))
    test_groups: set[str] = set()
    test_rows = 0
    for _, row in groups.iloc[::-1].iterrows():
        test_groups.add(str(row[group_column]))
        test_rows += int(row["rows"])
        if test_rows >= target_test_rows:
            break

    group_values = working[group_column].astype(str)
    test_mask = group_values.isin(test_groups)
    train = working[~test_mask].drop(columns=["_split_time", "_split_order"])
    test = working[test_mask].drop(columns=["_split_time", "_split_order"])
    if train.empty or test.empty:
        raise ValueError("Split invalide: train ou test vide")
    return train, test


def split_stratified_chronological(
    frame: pd.DataFrame,
    *,
    test_size: float,
    label_column: str,
    timestamp_column: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if label_column not in frame:
        raise ValueError(f"Colonne label introuvable: {label_column}")

    train_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []
    for _, group in frame.groupby(label_column, dropna=False):
        train, test = split_chronological(group, test_size=test_size, timestamp_column=timestamp_column)
        train_parts.append(train)
        test_parts.append(test)
    return pd.concat(train_parts).sort_index(), pd.concat(test_parts).sort_index()


def split_stratified_group_chronological(
    frame: pd.DataFrame,
    *,
    test_size: float,
    label_column: str,
    group_column: str,
    timestamp_column: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if label_column not in frame:
        raise ValueError(f"Colonne label introuvable: {label_column}")

    train_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []
    for _, group in frame.groupby(label_column, dropna=False):
        if group[group_column].astype(str).nunique(dropna=False) <= 1:
            train, test = split_chronological(group, test_size=test_size, timestamp_column=timestamp_column)
        else:
            train, test = split_group_chronological(
                group,
                test_size=test_size,
                group_column=group_column,
                timestamp_column=timestamp_column,
            )
        train_parts.append(train)
        test_parts.append(test)
    return pd.concat(train_parts).sort_index(), pd.concat(test_parts).sort_index()


def split_dataset(
    input_csv: Path,
    train_out: Path,
    test_out: Path,
    summary_out: Path,
    *,
    sep: str = ";",
    strategy: str = "chronological",
    test_size: float = 0.2,
    label_column: str = "label",
    group_column: str = "block_id",
    timestamp_column: str = "timestamp_iso",
) -> tuple[Path, Path, Path]:
    frame = pd.read_csv(input_csv, sep=sep, dtype=str, keep_default_na=False)
    if frame.empty:
        raise ValueError(f"Dataset vide: {input_csv}")
    test_size = min(max(float(test_size), 0.01), 0.9)

    if strategy == "group_chronological":
        train, test = split_group_chronological(
            frame,
            test_size=test_size,
            group_column=group_column,
            timestamp_column=timestamp_column,
        )
    elif strategy == "chronological":
        train, test = split_chronological(frame, test_size=test_size, timestamp_column=timestamp_column)
    elif strategy == "stratified_chronological":
        train, test = split_stratified_chronological(
            frame,
            test_size=test_size,
            label_column=label_column,
            timestamp_column=timestamp_column,
        )
    elif strategy == "stratified_group_chronological":
        train, test = split_stratified_group_chronological(
            frame,
            test_size=test_size,
            label_column=label_column,
            group_column=group_column,
            timestamp_column=timestamp_column,
        )
    else:
        raise ValueError(f"Strategie inconnue: {strategy}")

    _write_outputs(
        train,
        test,
        train_out,
        test_out,
        summary_out,
        sep=sep,
        input_csv=input_csv,
        strategy=strategy,
        label_column=label_column,
    )
    return train_out, test_out, summary_out


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Split chronologique/par groupe pour validation Logminer")
    parser.add_argument("-i", "--input", required=True, type=Path, help="CSV labellise")
    parser.add_argument("--train-out", required=True, type=Path, help="CSV train")
    parser.add_argument("--test-out", required=True, type=Path, help="CSV test")
    parser.add_argument("--summary-out", required=True, type=Path, help="Resume du split")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument(
        "--strategy",
        choices=[
            "chronological",
            "group_chronological",
            "stratified_chronological",
            "stratified_group_chronological",
        ],
        default="chronological",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--group-column", default="block_id")
    parser.add_argument("--timestamp-column", default="timestamp_iso")
    args = parser.parse_args(argv)

    train_out, test_out, summary_out = split_dataset(
        args.input,
        args.train_out,
        args.test_out,
        args.summary_out,
        sep=args.sep,
        strategy=args.strategy,
        test_size=args.test_size,
        label_column=args.label_column,
        group_column=args.group_column,
        timestamp_column=args.timestamp_column,
    )
    summary = pd.read_csv(summary_out, sep=args.sep, dtype=str, keep_default_na=False)
    print(f"Train: {train_out}")
    print(f"Test: {test_out}")
    print(f"Resume: {summary_out}")
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
