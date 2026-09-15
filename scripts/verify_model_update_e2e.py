"""Verify promotion/rejection integrity and emit the required phase-4 evidence files."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "docs" / "memoire" / "final_experiments_2026" / "state" / "EXPERIMENT_LEDGER.csv"


def append_completed(case_name: str, payload: dict[str, object]) -> None:
    experiment_id = f"e4_model_update_{'min_delta' if case_name == 'positive_but_insufficient' else case_name}"
    with LEDGER_PATH.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        columns = list(rows[0]) if rows else []
    latest = {row["experiment_id"]: row for row in rows}
    if latest.get(experiment_id, {}).get("status") == "COMPLETED":
        return
    raw_name = "model_update_min_delta_case.json" if case_name == "positive_but_insufficient" else f"model_update_{case_name}_case.json"
    values = {
        "experiment_id": experiment_id,
        "phase": "4",
        "run_id": experiment_id,
        "dataset": "CICIDS2017",
        "scenario": "DDoS_holdout_seed42",
        "seed": "42",
        "model": "controlled_model_update",
        "status": "COMPLETED",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "command": "scripts/monthly_model_retraining.py --plan docs/memoire/final_experiments_2026/configs/model_update_e2e_plan.json --promote",
        "config_path": "docs/memoire/final_experiments_2026/configs/model_update_e2e_plan.json",
        "raw_result_path": f"data/processed/final_experiments_2026/phase_4/{raw_name}",
        "summary_path": "data/processed/final_experiments_2026/phase_4/model_update_integrity_report.json",
        "notes": f"decision={payload['decision']} delta={payload['delta']} integrity_verified={payload['integrity_verified']}",
    }
    with LEDGER_PATH.open("a", encoding="utf-8-sig", newline="") as handle:
        csv.DictWriter(handle, fieldnames=columns).writerow({column: values.get(column, "") for column in columns})


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase-dir", type=Path, default=Path("data/processed/final_experiments_2026/phase_4"))
    args = parser.parse_args()
    phase_dir = args.phase_dir if args.phase_dir.is_absolute() else ROOT / args.phase_dir
    preparation = json.loads((phase_dir / "model_update_preparation.json").read_text(encoding="utf-8"))
    report_path = phase_dir / "model_update_end_to_end_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    plan = json.loads((ROOT / "docs/memoire/final_experiments_2026/configs/model_update_e2e_plan.json").read_text(encoding="utf-8"))
    plan_by_family = {item["family"]: item for item in plan["models"]}
    case_keys = {"phase4_promotion": "promotion", "phase4_rejection": "rejection", "phase4_min_delta": "min_delta"}
    results: dict[str, object] = {}
    for row in report["results"]:
        family = row["family"]
        case_key = case_keys[family]
        plan_row = plan_by_family[family]
        current_path = ROOT / plan_row["current_model"]
        candidate_path = ROOT / plan_row["candidate_model"]
        before_hash = preparation["current_models"][case_key]["sha256_before"]
        current_after = sha256_file(current_path)
        candidate_hash = sha256_file(candidate_path)
        backup_path = Path(row.get("backup") or "")
        backup_exists = bool(row.get("backup")) and backup_path.exists()
        backup_hash = sha256_file(backup_path) if backup_exists else None
        promoted = bool(row["promoted"])
        integrity = {
            "backup_matches_current_before": backup_hash == before_hash if promoted else None,
            "current_after_matches_candidate": current_after == candidate_hash if promoted else None,
            "current_unchanged": current_after == before_hash if not promoted else None,
        }
        verified = all(value is not False for value in integrity.values())
        case_payload = {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "case": plan_row["case"],
            "family": family,
            "metric": row["metric"],
            "current_score": row["current_score"],
            "candidate_score": row["candidate_score"],
            "delta": row["delta"],
            "min_delta": row["min_delta"],
            "decision": row["status"],
            "promoted": promoted,
            "current_hash_before": before_hash,
            "candidate_hash": candidate_hash,
            "backup_path": str(backup_path) if backup_exists else "",
            "backup_hash": backup_hash,
            "current_hash_after": current_after,
            "integrity_checks": integrity,
            "integrity_verified": verified,
            "current_metrics": row.get("current_metrics", {}),
            "candidate_metrics": row.get("candidate_metrics", {}),
        }
        output_name = {
            "promotion": "model_update_promotion_case.json",
            "rejection": "model_update_rejection_case.json",
            "positive_but_insufficient": "model_update_min_delta_case.json",
        }[plan_row["case"]]
        (phase_dir / output_name).write_text(json.dumps(case_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        results[plan_row["case"]] = case_payload
    consolidated = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report": str(report_path),
        "production_models_touched": False,
        "isolated_root": str(phase_dir),
        "all_integrity_checks_passed": all(item["integrity_verified"] for item in results.values()),
        "cases": results,
    }
    (phase_dir / "model_update_integrity_report.json").write_text(
        json.dumps(consolidated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    for case_name, case_payload in results.items():
        append_completed(case_name, case_payload)
    print(json.dumps(consolidated, ensure_ascii=False, indent=2))
    return 0 if consolidated["all_integrity_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
