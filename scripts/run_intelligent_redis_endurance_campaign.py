"""Campagne Redis longue par iterations bornees dans le temps.

Ce pilote relance la campagne Redis panne/reprise jusqu'a atteindre une duree
cible. Il conserve un resume cumulatif apres chaque iteration pour qu'un run de
plusieurs heures reste exploitable meme en cas d'interruption.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import quantiles


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = REPO_ROOT / "data" / "processed" / "intelligent_redis_endurance_runs"
SUMMARY_PATH = REPO_ROOT / "data" / "processed" / "intelligent_redis_6h_campaign_summary.json"
TABLE_PATH = REPO_ROOT / "docs" / "memoire" / "tables" / "table_intelligent_redis_6h_campaign.md"


def percentile(values: list[float], percent: int) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return round(values[0], 4)
    index = 94 if percent == 95 else 98
    return round(quantiles(values, n=100, method="inclusive")[index], 4)


def write_table(path: Path, summary: dict[str, object]) -> None:
    lines = [
        "# Campagne Redis Endurance 6h Agents Intelligents",
        "",
        "| Indicateur | Valeur |",
        "| --- | ---: |",
        f"| Debut | `{summary['start']}` |",
        f"| Fin | `{summary['end']}` |",
        f"| Duree cible | {summary['target_duration_sec']} s |",
        f"| Duree observee | {summary['elapsed_sec']} s |",
        f"| Iterations terminees | {summary['iterations_completed']} |",
        f"| Iterations echouees | {summary['iterations_failed']} |",
        f"| Taches enfilees | {summary['tasks_enqueued']} |",
        f"| Taches uniques terminees | {summary['unique_completed']} |",
        f"| Echecs de taches | {summary['failed']} |",
        f"| Pannes simulees avant ack | {summary['simulated_crashes']} |",
        f"| Pending final cumule | {summary['pending_after']} |",
        f"| Perte estimee cumulee | {summary['estimated_loss']} |",
        f"| Debit observe | {summary['tasks_per_sec']} taches/s |",
        f"| Latence p95 | {summary['elapsed_p95_sec']} s |",
        f"| Latence p99 | {summary['elapsed_p99_sec']} s |",
        "",
        "## Repartition Par Agent",
        "",
        "| Agent | Taches terminees |",
        "| --- | ---: |",
    ]
    for agent, count in sorted(dict(summary["by_agent"]).items()):
        lines.append(f"| `{agent}` | {count} |")
    lines.extend(
        [
            "",
            "## Repartition Par Type",
            "",
            "| Type de tache | Taches terminees |",
            "| --- | ---: |",
        ]
    )
    for task_type, count in sorted(dict(summary["by_type"]).items()):
        lines.append(f"| `{task_type}` | {count} |")
    lines.extend(
        [
            "",
            "Note: cette table est mise a jour apres chaque iteration du run d'endurance.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def merge_counts(target: dict[str, int], source: dict[str, int]) -> None:
    for key, value in source.items():
        target[key] = target.get(key, 0) + int(value)


def build_summary(
    *,
    start: str,
    target_duration_sec: int,
    started: float,
    runs: list[dict[str, object]],
) -> dict[str, object]:
    by_agent: dict[str, int] = {}
    by_type: dict[str, int] = {}
    latencies_p95: list[float] = []
    latencies_p99: list[float] = []
    totals = {
        "tasks_enqueued": 0,
        "completed": 0,
        "unique_completed": 0,
        "failed": 0,
        "unique_failed": 0,
        "simulated_crashes": 0,
        "pending_after": 0,
        "estimated_loss": 0,
    }
    completed_iterations = 0
    failed_iterations = 0
    for run in runs:
        if run.get("returncode") == 0 and run.get("summary"):
            completed_iterations += 1
        else:
            failed_iterations += 1
        summary = run.get("summary") if isinstance(run.get("summary"), dict) else {}
        for key in totals:
            totals[key] += int(summary.get(key, 0) or 0)
        merge_counts(by_agent, dict(summary.get("by_agent", {})))
        merge_counts(by_type, dict(summary.get("by_type", {})))
        latencies_p95.append(float(summary.get("elapsed_p95_sec", 0) or 0))
        latencies_p99.append(float(summary.get("elapsed_p99_sec", 0) or 0))

    elapsed = round(time.perf_counter() - started, 4)
    return {
        "start": start,
        "end": datetime.now(timezone.utc).isoformat(),
        "target_duration_sec": target_duration_sec,
        "elapsed_sec": elapsed,
        "iterations_completed": completed_iterations,
        "iterations_failed": failed_iterations,
        "tasks_per_sec": round(totals["completed"] / elapsed, 4) if elapsed > 0 else 0,
        "elapsed_p95_sec": percentile(latencies_p95, 95),
        "elapsed_p99_sec": percentile(latencies_p99, 99),
        "by_agent": by_agent,
        "by_type": by_type,
        "runs": runs,
        **totals,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne Redis endurance 6h")
    parser.add_argument("--duration-sec", type=int, default=21600)
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--repetitions", type=int, default=4)
    parser.add_argument("--cycles", type=int, default=8)
    parser.add_argument("--max-parallel-tasks", type=int, default=2)
    parser.add_argument("--block-ms", type=int, default=1000)
    parser.add_argument("--iteration-timeout-sec", type=int, default=900)
    parser.add_argument("--output-json", type=Path, default=SUMMARY_PATH)
    parser.add_argument("--output-table", type=Path, default=TABLE_PATH)
    args = parser.parse_args()

    started = time.perf_counter()
    start = datetime.now(timezone.utc).isoformat()
    output_json = args.output_json if args.output_json.is_absolute() else REPO_ROOT / args.output_json
    output_table = args.output_table if args.output_table.is_absolute() else REPO_ROOT / args.output_table
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)

    runs: list[dict[str, object]] = []
    iteration = 0
    while time.perf_counter() - started < max(1, args.duration_sec):
        iteration += 1
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        run_json = RUN_DIR / f"redis_endurance_{iteration:04d}_{stamp}.json"
        run_md = RUN_DIR / f"redis_endurance_{iteration:04d}_{stamp}.md"
        run_log = RUN_DIR / f"redis_endurance_{iteration:04d}_{stamp}.log"
        command = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "run_intelligent_redis_campaign.py"),
            "--redis-url",
            args.redis_url,
            "--workers",
            str(args.workers),
            "--repetitions",
            str(args.repetitions),
            "--cycles",
            str(args.cycles),
            "--max-parallel-tasks",
            str(args.max_parallel_tasks),
            "--block-ms",
            str(args.block_ms),
            "--worker-timeout-sec",
            str(args.iteration_timeout_sec),
            "--compact-worker-output",
            "--output-json",
            str(run_json.relative_to(REPO_ROOT)),
            "--output-markdown",
            str(run_md.relative_to(REPO_ROOT)),
        ]
        run_record: dict[str, object] = {
            "iteration": iteration,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "summary_path": str(run_json.relative_to(REPO_ROOT)),
            "log_path": str(run_log.relative_to(REPO_ROOT)),
        }
        with run_log.open("w", encoding="utf-8") as log:
            try:
                completed = subprocess.run(
                    command,
                    cwd=REPO_ROOT,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True,
                    timeout=max(60, args.iteration_timeout_sec),
                    check=False,
                )
                run_record["returncode"] = completed.returncode
            except subprocess.TimeoutExpired:
                run_record["returncode"] = 124
                run_record["timed_out"] = True

        if run_json.exists():
            run_record["summary"] = json.loads(run_json.read_text(encoding="utf-8"))
        run_record["ended_at"] = datetime.now(timezone.utc).isoformat()
        runs.append(run_record)
        summary = build_summary(
            start=start,
            target_duration_sec=max(1, args.duration_sec),
            started=started,
            runs=runs,
        )
        output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        write_table(output_table, summary)

    final_summary = build_summary(
        start=start,
        target_duration_sec=max(1, args.duration_sec),
        started=started,
        runs=runs,
    )
    output_json.write_text(json.dumps(final_summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_table(output_table, final_summary)
    print(json.dumps(final_summary, ensure_ascii=False, indent=2))
    return 0 if final_summary["iterations_completed"] > 0 and final_summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
