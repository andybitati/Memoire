"""Analyse préenregistrée des trois politiques d'allocation Redis distribuée."""
from __future__ import annotations

import csv
import hashlib
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "experiments/phase_revision_20261112/E-MULTIVM-DYNAMIC-ALLOCATION"
POLICIES = ("utility_agent_id", "utility_load", "least_loaded")
TOP_RATE = 32.0


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(run_id: str) -> dict:
    return json.loads((OUT / f"{run_id}__saturation_summary.json").read_text(encoding="utf-8"))


def aggregate(summary: dict) -> dict:
    top = [level for level in summary["levels"] if float(level["offered_tasks_sec"]) == TOP_RATE]
    all_levels = list(summary["levels"])
    completed = sum(int(level["completed_ok"]) for level in all_levels)
    failed = sum(int(level["failed"]) for level in all_levels)
    by_agent: dict[str, int] = {}
    for level in all_levels:
        for agent_id, count in level["tasks_by_agent"].items():
            by_agent[agent_id] = by_agent.get(agent_id, 0) + int(count)
    total_assigned = sum(by_agent.values())
    shares = {agent_id: count / total_assigned for agent_id, count in sorted(by_agent.items())}
    capacities = [float(level["completed_tasks_sec"]) for level in top]
    return {
        "capacity_tasks_sec_at_rate32": {"median": statistics.median(capacities), "values": capacities},
        "completed": completed,
        "failed": failed,
        "tasks_by_agent": by_agent,
        "agent_shares": shares,
    }


def main() -> int:
    if len(sys.argv) != 4:
        raise SystemExit("Usage: analyse_dynamic.py RUN_HISTORIQUE RUN_UTILITY_LOAD RUN_LEAST_LOADED")
    run_ids = dict(zip(POLICIES, sys.argv[1:4]))
    aggregates = {policy: aggregate(load(run_id)) for policy, run_id in run_ids.items()}
    historical = aggregates["utility_agent_id"]
    dynamic = aggregates["utility_load"]
    least = aggregates["least_loaded"]
    capacity_ratio = (
        dynamic["capacity_tasks_sec_at_rate32"]["median"]
        / historical["capacity_tasks_sec_at_rate32"]["median"]
    )
    ubuntu_dynamic = dynamic["agent_shares"].get("ubuntu-beta", 0.0)
    capacity_equivalence = (
        dynamic["capacity_tasks_sec_at_rate32"]["median"]
        / least["capacity_tasks_sec_at_rate32"]["median"]
    )
    share_gap = max(
        abs(dynamic["agent_shares"].get(agent_id, 0.0) - least["agent_shares"].get(agent_id, 0.0))
        for agent_id in {"debian-alpha", "ubuntu-beta"}
    )
    if dynamic["failed"] == 0 and ubuntu_dynamic >= 0.25 and capacity_ratio >= 1.20:
        decision = "allocation_dynamique_confirmee"
    elif dynamic["failed"] == 0 and ubuntu_dynamic >= 0.25:
        decision = "partage_confirme_sans_gain_capacite"
    else:
        decision = "allocation_dynamique_non_confirmee"
    least_loaded_equivalent = 0.90 <= capacity_equivalence <= 1.10 and share_gap <= 0.10
    result = {
        "experiment_id": "E-MULTIVM-DYNAMIC-ALLOCATION",
        "analysed_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_ids": run_ids,
        "policies": aggregates,
        "utility_load_over_historical_capacity": capacity_ratio,
        "utility_load_over_least_loaded_capacity": capacity_equivalence,
        "utility_load_least_loaded_max_agent_share_gap": share_gap,
        "least_loaded_equivalent_under_equal_utilities": least_loaded_equivalent,
        "decision": decision,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    artifacts = sorted(OUT.glob("*__saturation_*.csv")) + sorted(OUT.glob("*__saturation_*.json")) + [summary_path]
    sources = [
        HERE / "PROTOCOLE.md",
        HERE / "run_dynamic_arm.py",
        HERE / "run_campaign.ps1",
        HERE / "analyse_dynamic.py",
        ROOT / "revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/run_saturation_arm.py",
        ROOT / "revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/start_agents.ps1",
        ROOT / "revision_reports/agent_3/hdfs_redis_agent.py",
        ROOT / "src/logminer/agents/redis_contract_net.py",
    ]
    with (OUT / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["role", "path", "bytes", "sha256"])
        for role, path in [("artifact", item) for item in artifacts] + [("source", item) for item in sources]:
            writer.writerow([role, path.relative_to(ROOT).as_posix(), path.stat().st_size, sha256(path)])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
