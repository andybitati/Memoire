#!/usr/bin/env python3
"""Run the frozen phase-5 functional multiformat validation."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from evaluate_supervised_strict_splits import (  # noqa: E402
    _clean_columns,
    _label_column,
    _network_feature_columns,
    _network_features,
)
from logminer.detectors.file_detector import detect_kind  # noqa: E402
from logminer.pipeline import run_pipeline  # noqa: E402
from prepare_wazuh_dataset import _normalise_chunk  # noqa: E402
from train_linux_auth_model import prepare_linux_auth_frame  # noqa: E402


DOC_ROOT = ROOT / "docs" / "memoire" / "final_experiments_2026"
DATA_ROOT = ROOT / "data" / "processed" / "final_experiments_2026"
PHASE_ROOT = DATA_ROOT / "phase_5"
LEDGER = DOC_ROOT / "state" / "EXPERIMENT_LEDGER.csv"
DEFAULT_CONFIG = DOC_ROOT / "configs" / "multiformat_validation_protocol.json"
STANDARD_FIELDS = ("timestamp", "source", "host", "family", "category", "severity", "message")


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    names = fieldnames or (list(rows[0]) if rows else [])
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        if not names:
            return
        writer = csv.DictWriter(handle, fieldnames=names, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", errors="ignore", newline="") as handle:
        return list(csv.DictReader(handle))


def append_ledger(row: dict[str, Any]) -> None:
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as handle:
        fieldnames = next(csv.reader(handle))
    with LEDGER.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writerow({name: row.get(name, "") for name in fieldnames})


def ledger_latest() -> dict[str, dict[str, str]]:
    latest: dict[str, dict[str, str]] = {}
    with LEDGER.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            latest[row["experiment_id"]] = row
    return latest


def ledger_row(item: dict[str, Any], status: str, *, started_at: str = "", completed_at: str = "", notes: str = "") -> dict[str, Any]:
    experiment_id = f"e5_multiformat_{item['id']}"
    return {
        "experiment_id": experiment_id,
        "phase": 5,
        "run_id": experiment_id,
        "dataset": item["display_name"],
        "scenario": "functional_multiformat_current_code",
        "seed": "",
        "model": item["adapter"],
        "status": status,
        "started_at": started_at,
        "completed_at": completed_at,
        "command": "scripts/run_multiformat_validation.py --resume",
        "config_path": str(DEFAULT_CONFIG.relative_to(ROOT)).replace("\\", "/"),
        "raw_result_path": f"data/processed/final_experiments_2026/phase_5/{experiment_id}.json",
        "summary_path": "data/processed/final_experiments_2026/multiformat_validation_summary.csv",
        "figure_path": "docs/memoire/final_experiments_2026/figures/validation_multiformat.png",
        "git_commit": "1e184ab",
        "notes": notes,
    }


def register_plans(config: dict[str, Any]) -> None:
    latest = ledger_latest()
    for item in config["formats"]:
        experiment_id = f"e5_multiformat_{item['id']}"
        if experiment_id in latest:
            continue
        append_ledger(ledger_row(item, "PLANNED", notes="registered before multiformat execution"))


def select_text_lines(source: Path, destination: Path, limit: int) -> list[str]:
    rows: list[str] = []
    with source.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            value = line.rstrip("\r\n")
            if not value.strip():
                continue
            rows.append(value)
            if len(rows) >= limit:
                break
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("\n".join(rows) + ("\n" if rows else ""), encoding="utf-8")
    return rows


def select_evtx(source: Path, destination: Path, limit: int) -> list[str]:
    from Evtx.Evtx import Evtx
    from Evtx.Views import evtx_record_xml_view

    rows: list[str] = []
    with Evtx(str(source)) as log:
        for record in log.records():
            rows.append(evtx_record_xml_view(record))
            if len(rows) >= limit:
                break
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text("<Events>\n" + "\n".join(rows) + "\n</Events>\n", encoding="utf-8")
    return rows


def pipeline_adapter(item: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]], str, str, Callable[[int], str | None]]:
    source = ROOT / item["source"]
    sample_suffix = ".xml" if item["adapter"] == "pipeline_evtx_sample" else source.suffix
    sample = PHASE_ROOT / "samples" / f"{item['id']}{sample_suffix}"
    raw_rows = select_evtx(source, sample, item["limit"]) if item["adapter"] == "pipeline_evtx_sample" else select_text_lines(source, sample, item["limit"])
    detected = detect_kind(str(sample))
    output_dir = PHASE_ROOT / "normalized"
    output_name = f"{item['id']}.csv"
    error = ""
    normalized: list[dict[str, Any]] = []
    try:
        outputs = run_pipeline(str(sample), out_dir=str(output_dir), out_name=output_name, sep=";", debug=False)
        for output in outputs:
            with Path(output).open("r", encoding="utf-8-sig", errors="ignore", newline="") as handle:
                normalized.extend(csv.DictReader(handle, delimiter=";"))
    except Exception as exc:  # validation must retain format failures
        error = f"{type(exc).__name__}: {exc}"

    def raw_message(index: int) -> str | None:
        return raw_rows[index]

    return raw_rows, normalized, detected, error, raw_message


def linux_auth_adapter(item: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]], str, str, Callable[[int], str | None]]:
    source = ROOT / item["source"]
    raw = pd.read_csv(source, dtype=str, keep_default_na=False, nrows=item["limit"], encoding_errors="ignore")
    prepared = prepare_linux_auth_frame(raw)
    output = PHASE_ROOT / "normalized" / "linux_auth.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(output, index=False, encoding="utf-8-sig")
    raw_rows = [json.dumps(row, sort_keys=True, ensure_ascii=True) for row in raw.to_dict(orient="records")]
    normalized = prepared.to_dict(orient="records")
    comments = prepared["comment"].astype(str).tolist()
    return raw_rows, normalized, "not_applicable", "", lambda index: comments[index] or None


def wazuh_adapter(item: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]], str, str, Callable[[int], str | None]]:
    source = ROOT / item["source"]
    raw = pd.read_csv(source, dtype=str, keep_default_na=False, nrows=item["limit"], encoding_errors="ignore")
    normalized_frame = _normalise_chunk(raw.copy(), source, 0)
    output = PHASE_ROOT / "normalized" / "wazuh.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    normalized_frame.to_csv(output, sep=";", index=False, encoding="utf-8-sig")
    raw_rows = [json.dumps(row, sort_keys=True, ensure_ascii=True) for row in raw.to_dict(orient="records")]
    normalized = normalized_frame.to_dict(orient="records")
    full_logs = raw.get("_source.full_log", pd.Series("", index=raw.index)).astype(str).tolist()
    return raw_rows, normalized, "not_applicable", "", lambda index: full_logs[index] or None


def network_adapter(item: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]], str, str, Callable[[int], str | None]]:
    source = ROOT / item["source"]
    raw = pd.read_csv(source, dtype=str, keep_default_na=False, nrows=item["limit"], encoding_errors="ignore")
    clean = _clean_columns(raw)
    label_column = _label_column(clean.columns)
    feature_columns = _network_feature_columns(source)
    features = _network_features(clean, feature_columns)
    output_frame = features.copy()
    output_frame["label"] = clean[label_column].astype(str).values
    output = PHASE_ROOT / "normalized" / "network_tabular.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    output_frame.to_csv(output, index=False, encoding="utf-8-sig")
    raw_rows = [json.dumps(row, sort_keys=True, ensure_ascii=True) for row in raw.to_dict(orient="records")]
    normalized = output_frame.to_dict(orient="records")
    return raw_rows, normalized, "not_applicable", "", lambda index: None


ADAPTERS = {
    "pipeline_evtx_sample": pipeline_adapter,
    "pipeline_text_sample": pipeline_adapter,
    "linux_auth_feature_preparation": linux_auth_adapter,
    "wazuh_csv_normalizer": wazuh_adapter,
    "network_feature_preparation": network_adapter,
}


FIELD_MAPS: dict[str, dict[str, str | None]] = {
    "pipeline": {"timestamp": "timestamp_iso", "source": "source", "host": "host", "family": "subtype", "category": "category", "severity": "severity", "message": "message"},
    "linux_auth_feature_preparation": {"timestamp": "timestamp", "source": "service", "host": "server", "family": None, "category": None, "severity": None, "message": "comment"},
    "wazuh_csv_normalizer": {"timestamp": "timestamp_iso", "source": "source", "host": "host", "family": "subtype", "category": "category", "severity": "severity", "message": "message"},
    "network_feature_preparation": {name: None for name in STANDARD_FIELDS},
}


def field_map(item: dict[str, Any]) -> dict[str, str | None]:
    if item["adapter"].startswith("pipeline_"):
        return FIELD_MAPS["pipeline"]
    return FIELD_MAPS[item["adapter"]]


def analyse_item(item: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    source = ROOT / item["source"]
    actual_hash = sha256_file(source)
    if actual_hash != item["source_sha256"]:
        raise RuntimeError(f"Source hash mismatch for {item['id']}: {actual_hash}")
    raw_rows, normalized, detected, execution_error, source_message = ADAPTERS[item["adapter"]](item)
    mapping = field_map(item)
    n_raw = len(raw_rows)
    n_parsed = len(normalized)
    detail: list[dict[str, Any]] = []
    preserved = 0
    testable = 0
    for index, raw_value in enumerate(raw_rows):
        output = normalized[index] if index < n_parsed else {}
        message_key = mapping["message"]
        output_message = str(output.get(message_key, "")) if message_key else ""
        original_message = source_message(index)
        if original_message is None or str(original_message) == "":
            preservation = "NOT_APPLICABLE"
        else:
            testable += 1
            preservation = "TRUE" if output_message == str(original_message) else "FALSE"
            preserved += int(preservation == "TRUE")
        detail.append(
            {
                "experiment_id": f"e5_multiformat_{item['id']}",
                "format": item["display_name"],
                "event_index": index + 1,
                "source_path": item["source"],
                "raw_sha256": sha256_text(raw_value),
                "raw_length": len(raw_value),
                "read": True,
                "parsed": index < n_parsed,
                "normalized": index < n_parsed,
                "detected_kind": detected,
                "parse_error": "" if index < n_parsed else (execution_error or "no_normalized_row_emitted"),
                "original_message_test": preservation,
                "normalized_message_sha256": sha256_text(output_message) if output_message else "",
            }
        )
    completeness: list[dict[str, Any]] = []
    for standard_field in STANDARD_FIELDS:
        key = mapping[standard_field]
        present = sum(1 for row in normalized if key and str(row.get(key, "")).strip())
        completeness.append(
            {
                "experiment_id": f"e5_multiformat_{item['id']}",
                "format": item["display_name"],
                "field": standard_field,
                "source_column": key or "",
                "n_present": present,
                "n_normalized": n_parsed,
                "completeness_rate": round(present / n_parsed, 6) if n_parsed else "",
                "status": "MEASURED" if n_parsed else "NOT_EVALUABLE_NO_NORMALIZED_ROWS",
            }
        )
    n_errors = n_raw - n_parsed
    summary = {
        "experiment_id": f"e5_multiformat_{item['id']}",
        "format": item["display_name"],
        "adapter": item["adapter"],
        "source_path": item["source"],
        "source_sha256": actual_hash,
        "source_status": item["source_status"],
        "raw_unit": item["raw_unit"],
        "target_limit": item["limit"],
        "n_brut": n_raw,
        "n_lu": n_raw,
        "n_parse": n_parsed,
        "n_normalise": n_parsed,
        "n_erreur": n_errors,
        "n_perdu": n_raw - n_parsed,
        "taux_ingestion": 1.0 if n_raw else 0.0,
        "taux_parsing": round(n_parsed / n_raw, 6) if n_raw else 0.0,
        "taux_normalisation": round(n_parsed / n_raw, 6) if n_raw else 0.0,
        "expected_kind": item["expected_detector_kind"],
        "detected_kind": detected,
        "detector_match": detected == item["expected_detector_kind"] if detected != "not_applicable" else "NOT_APPLICABLE",
        "message_preservation_testable": testable,
        "message_preserved": preserved,
        "message_preservation_rate": round(preserved / testable, 6) if testable else "",
        "execution_error": execution_error,
        "status": "COMPLETE" if not execution_error else "COMPLETE_WITH_FORMAT_ERROR",
    }
    return summary, detail, completeness


def write_case_artifacts(item: dict[str, Any], summary: dict[str, Any], detail: list[dict[str, Any]], completeness: list[dict[str, Any]]) -> None:
    experiment_id = summary["experiment_id"]
    write_csv(PHASE_ROOT / f"{experiment_id}_raw.csv", detail)
    write_csv(PHASE_ROOT / f"{experiment_id}_fields.csv", completeness)
    payload = {
        "schema_version": 1,
        "generated_at": utcnow(),
        "config": item,
        "summary": summary,
        "field_completeness": completeness,
    }
    (PHASE_ROOT / f"{experiment_id}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_case_artifacts(item: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]] | None:
    experiment_id = f"e5_multiformat_{item['id']}"
    case_path = PHASE_ROOT / f"{experiment_id}.json"
    raw_path = PHASE_ROOT / f"{experiment_id}_raw.csv"
    fields_path = PHASE_ROOT / f"{experiment_id}_fields.csv"
    if not (case_path.exists() and raw_path.exists() and fields_path.exists()):
        return None
    payload = json.loads(case_path.read_text(encoding="utf-8"))
    return payload["summary"], read_csv_rows(raw_path), read_csv_rows(fields_path)


def aggregate_outputs(summaries: list[dict[str, Any]], details: list[dict[str, Any]], completeness: list[dict[str, Any]]) -> None:
    write_csv(DATA_ROOT / "multiformat_validation_raw.csv", details)
    write_csv(DATA_ROOT / "multiformat_validation_summary.csv", summaries)
    write_csv(DATA_ROOT / "multiformat_field_completeness.csv", completeness)
    failures = [row for row in details if str(row["parsed"]).lower() not in ("true", "1")]
    write_csv(
        DATA_ROOT / "multiformat_failures.csv",
        failures,
        fieldnames=list(details[0]) if details else ["experiment_id", "format", "event_index", "parse_error"],
    )

    table = DOC_ROOT / "tables" / "validation_multiformat.md"
    lines = [
        "# Validation fonctionnelle multiformat",
        "",
        "| Format | N brut | N parsé | N normalisé | Erreurs | Perdus | Taux parsing | Conservation message |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summaries:
        preservation = f"{float(row['message_preservation_rate']):.3f}" if row["message_preservation_rate"] != "" else "n/a"
        lines.append(
            f"| {row['format']} | {row['n_brut']} | {row['n_parse']} | {row['n_normalise']} | "
            f"{row['n_erreur']} | {row['n_perdu']} | {float(row['taux_parsing']):.3f} | {preservation} |"
        )
    lines.extend(["", "Statut : VALIDATION FONCTIONNELLE MULTIFORMAT. Ce tableau ne démontre pas une robustesse universelle."])
    table.parent.mkdir(parents=True, exist_ok=True)
    table.write_text("\n".join(lines) + "\n", encoding="utf-8")

    import matplotlib.pyplot as plt

    labels = [row["format"] for row in summaries]
    rates = [float(row["taux_parsing"]) for row in summaries]
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    bars = ax.bar(labels, rates, color=["#4C78A8" if value == 1 else "#E45756" for value in rates])
    for bar, value, row in zip(bars, rates, summaries):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.025, f"{value:.1%}\nN={row['n_brut']}", ha="center", va="bottom", fontsize=8)
    ax.set_ylim(0, 1.16)
    ax.set_ylabel("Taux de parsing / normalisation")
    ax.set_title("Validation fonctionnelle multiformat — code courant\nPremiers événements, maximum 1 000 par format")
    ax.tick_params(axis="x", rotation=25)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    figure = DOC_ROOT / "figures" / "validation_multiformat.png"
    figure.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(figure, dpi=180)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--register-plan", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    if args.dry_run:
        print(json.dumps({"status": "DRY_RUN", "formats": [{"id": row["id"], "source": row["source"], "limit": row["limit"]} for row in config["formats"]]}, ensure_ascii=True, indent=2))
        return 0
    if args.register_plan:
        register_plans(config)
        print(json.dumps({"status": "PLANS_REGISTERED", "count": len(config["formats"])}, ensure_ascii=True))
        return 0

    PHASE_ROOT.mkdir(parents=True, exist_ok=True)
    latest = ledger_latest()
    summaries: list[dict[str, Any]] = []
    details: list[dict[str, Any]] = []
    completeness: list[dict[str, Any]] = []
    for item in config["formats"]:
        experiment_id = f"e5_multiformat_{item['id']}"
        cached = load_case_artifacts(item) if args.resume and latest.get(experiment_id, {}).get("status") == "COMPLETED" else None
        if cached:
            summary, item_details, item_fields = cached
            print(f"SKIPPED_ALREADY_COMPLETED {experiment_id}")
        else:
            started = utcnow()
            append_ledger(ledger_row(item, "RUNNING", started_at=started))
            summary, item_details, item_fields = analyse_item(item)
            write_case_artifacts(item, summary, item_details, item_fields)
            append_ledger(
                ledger_row(
                    item,
                    "COMPLETED",
                    started_at=started,
                    completed_at=utcnow(),
                    notes=f"n_brut={summary['n_brut']} n_parse={summary['n_parse']} n_perdu={summary['n_perdu']}",
                )
            )
            print(f"{experiment_id}: {summary['n_parse']}/{summary['n_brut']} parsed")
        summaries.append(summary)
        details.extend(item_details)
        completeness.extend(item_fields)
    aggregate_outputs(summaries, details, completeness)
    print(json.dumps({"status": "COMPLETED", "formats": len(summaries), "events": len(details)}, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
