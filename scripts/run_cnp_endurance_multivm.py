#!/usr/bin/env python3
"""Campagne d'endurance canonique du Contract Net Redis sur deux VM."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import socket
import sys
import time
import traceback
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean, median
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus
from agents.idempotency import RedisIdempotencyStore
from agents.intelligent_runtime import AgentTask
from agents.redis_contract_net import RedisContractNetCoordinator, RedisContractNetTransport


PHASE_ROOT = ROOT / "experiments" / "phase_cnp_endurance"
DEFAULT_CONFIG = PHASE_ROOT / "configs" / "cnp_endurance_multivm_protocol.json"
PHASE_LEDGER = PHASE_ROOT / "LEDGER.csv"
GLOBAL_LEDGER = ROOT / "state" / "EXPERIMENT_LEDGER.csv"
RUN_ID_PATTERN = re.compile(r"^cnp_endurance_multivm_\d{8}T\d{6}Z$")
LEDGER_FIELDS = [
    "experiment_id", "phase", "run_id", "dataset", "protocol", "status",
    "started_at", "completed_at", "command", "config_path", "raw_result_path",
    "summary_path", "figure_path", "error_path", "git_commit", "notes",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_run_id() -> str:
    return "cnp_endurance_multivm_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT.resolve()).as_posix()


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def git_commit() -> str:
    import subprocess

    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "INFORMATION_A_VERIFIER"


def write_json_atomic(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)


def append_ledger(**values: Any) -> None:
    row = {field: values.get(field, "") for field in LEDGER_FIELDS}
    row["git_commit"] = row["git_commit"] or git_commit()
    for path in (PHASE_LEDGER, GLOBAL_LEDGER):
        path.parent.mkdir(parents=True, exist_ok=True)
        needs_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=LEDGER_FIELDS, extrasaction="ignore")
            if needs_header:
                writer.writeheader()
            writer.writerow(row)


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(len(ordered) - 1, lower + 1)
    fraction = position - lower
    return ordered[lower] * (1 - fraction) + ordered[upper] * fraction


def ensure_phase_dirs() -> None:
    for name in ("configs", "raw", "processed", "aggregated", "figures", "logs", "reports", "manifests"):
        (PHASE_ROOT / name).mkdir(parents=True, exist_ok=True)


def make_checkpoint(
    *,
    run_id: str,
    started_at: str,
    target_duration_sec: float,
    campaign_started: float,
    submitted: int,
    successful: int,
    failed: int,
    winners: Counter[str],
    last_task_id: str,
) -> dict[str, Any]:
    elapsed = time.monotonic() - campaign_started
    return {
        "run_id": run_id,
        "status": "RUNNING",
        "started_at": started_at,
        "updated_at": utc_now(),
        "target_duration_sec": target_duration_sec,
        "elapsed_sec": round(elapsed, 6),
        "completion_ratio": round(min(1.0, elapsed / target_duration_sec), 6),
        "submitted_tasks": submitted,
        "successful_tasks": successful,
        "failed_tasks": failed,
        "tasks_by_agent": dict(winners),
        "last_task_id": last_task_id,
    }


def build_manifest(path: Path, run_id: str, files: list[Path]) -> None:
    records = []
    for item in sorted(set(files)):
        if item.is_file():
            records.append(
                {
                    "path": relative(item),
                    "bytes": item.stat().st_size,
                    "sha256": sha256_file(item),
                }
            )
    write_json_atomic(
        path,
        {
            "schema_version": 1,
            "run_id": run_id,
            "generated_at": utc_now(),
            "files": records,
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Endurance CNP Redis multi-VM canonique")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--run-id", default="")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--duration-sec", type=float)
    parser.add_argument("--task-interval-sec", type=float)
    parser.add_argument("--checkpoint-interval-sec", type=float)
    parser.add_argument("--response-timeout-sec", type=float)
    parser.add_argument("--registry-timeout-sec", type=float)
    parser.add_argument("--agents", default="")
    parser.add_argument("--skip-controlled-crash", action="store_true")
    args = parser.parse_args()

    ensure_phase_dirs()
    config_path = args.config.resolve()
    config = json.loads(config_path.read_text(encoding="utf-8"))
    run_id = args.run_id or canonical_run_id()
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("run_id non canonique: cnp_endurance_multivm_YYYYMMDDTHHMMSSZ attendu")

    duration_sec = float(args.duration_sec if args.duration_sec is not None else config["duration_sec"])
    task_interval_sec = float(args.task_interval_sec if args.task_interval_sec is not None else config["task_interval_sec"])
    checkpoint_interval_sec = float(
        args.checkpoint_interval_sec
        if args.checkpoint_interval_sec is not None
        else config["checkpoint_interval_sec"]
    )
    response_timeout_sec = float(
        args.response_timeout_sec
        if args.response_timeout_sec is not None
        else config["response_timeout_sec"]
    )
    registry_timeout_sec = float(
        args.registry_timeout_sec
        if args.registry_timeout_sec is not None
        else config["registry_timeout_sec"]
    )
    agent_ids = [item.strip() for item in (args.agents.split(",") if args.agents else config["agents"]) if item.strip()]
    task_types = tuple(str(item) for item in config["task_types"])
    if duration_sec <= 0 or task_interval_sec < 0 or checkpoint_interval_sec <= 0:
        raise ValueError("Duree et intervalles invalides")
    if len(agent_ids) < 2:
        raise ValueError("Deux agents au minimum sont requis")

    paths = {
        "summary": PHASE_ROOT / "aggregated" / f"{run_id}__summary.json",
        "tasks": PHASE_ROOT / "raw" / f"{run_id}__task_metrics.csv",
        "messages": PHASE_ROOT / "logs" / f"{run_id}__messages.jsonl",
        "checkpoint": PHASE_ROOT / "raw" / f"{run_id}__checkpoint.json",
        "error": PHASE_ROOT / "logs" / f"{run_id}__error.log",
        "report": PHASE_ROOT / "reports" / f"{run_id}__report.md",
        "manifest": PHASE_ROOT / "manifests" / f"{run_id}__manifest.json",
    }
    if any(path.exists() for path in paths.values()):
        raise FileExistsError(f"Des artefacts existent deja pour {run_id}")

    started_at = utc_now()
    command = "python scripts/run_cnp_endurance_multivm.py"
    ledger_base = {
        "experiment_id": "cnp_endurance_multivm",
        "phase": "CNP-ENDURANCE",
        "run_id": run_id,
        "dataset": "deterministic synthetic orchestration workload",
        "protocol": "timed_multivm_CNP_with_post_persist_pre_RESULT_crash",
        "started_at": started_at,
        "command": command,
        "config_path": relative(config_path),
    }
    append_ledger(status="RUNNING", **ledger_base)

    try:
        namespace = f"logminer:cnp:{run_id}"
        event_stream = f"logminer:events:{run_id}"
        bus = RedisMessageBus(url=args.redis_url, stream=event_stream, run_id=run_id, maxlen=250_000)
        if not bus.ping():
            raise RuntimeError("Redis ne repond pas")
        transport = RedisContractNetTransport(bus, namespace=namespace, run_id=run_id)
        deadline = time.monotonic() + registry_timeout_sec
        registry: dict[str, Any] = {}
        while time.monotonic() < deadline:
            registry = transport.registered_agents()
            if all(agent_id in registry for agent_id in agent_ids):
                break
            time.sleep(0.25)
        if not all(agent_id in registry for agent_id in agent_ids):
            raise RuntimeError(f"Registre multi-VM incomplet: {sorted(registry)}")
        registry_hosts = {str(registry[agent_id].get("host", "")) for agent_id in agent_ids}
        if len(registry_hosts) < 2:
            raise RuntimeError(f"Deux hotes agents distincts sont requis: {sorted(registry_hosts)}")

        coordinator = RedisContractNetCoordinator(
            transport,
            agent_ids,
            response_timeout_sec=response_timeout_sec,
        )
        task_columns = [
            "task_index", "task_id", "task_type", "submitted_at", "completed_at",
            "campaign_elapsed_sec", "winner", "status", "latency_ms", "reassignments",
            "proposals_json", "refusals_json", "result_pid", "result_host",
            "idempotency_replayed",
        ]
        latencies: list[float] = []
        winners: Counter[str] = Counter()
        submitted = successful = failed = reassignments = 0
        campaign_started = time.monotonic()
        next_submission = campaign_started
        next_checkpoint = campaign_started + checkpoint_interval_sec
        last_task_id = ""

        with paths["tasks"].open("w", encoding="utf-8-sig", newline="") as task_handle:
            writer = csv.DictWriter(task_handle, fieldnames=task_columns)
            writer.writeheader()
            while time.monotonic() - campaign_started < duration_sec:
                now = time.monotonic()
                if now < next_submission:
                    time.sleep(min(0.25, next_submission - now))
                    continue
                task_index = submitted
                task_type = task_types[task_index % len(task_types)]
                task_id = f"{run_id}-task-{task_index:07d}"
                last_task_id = task_id
                submitted_at = utc_now()
                outcome = coordinator.negotiate(
                    AgentTask(
                        task_id=task_id,
                        task_type=task_type,
                        payload={
                            "values": [task_index + 1, task_index * 3 + 7, 17, 31],
                            "idempotency_key": f"{run_id}-effect-{task_index:07d}",
                        },
                    )
                )
                submitted += 1
                successful += int(outcome.status == "ok")
                failed += int(outcome.status != "ok")
                reassignments += int(outcome.reassignments)
                winners[str(outcome.winner)] += int(outcome.status == "ok")
                latency_ms = round(outcome.elapsed_sec * 1000, 6)
                latencies.append(latency_ms)
                result_output = outcome.result.output if outcome.result else {}
                writer.writerow(
                    {
                        "task_index": task_index,
                        "task_id": task_id,
                        "task_type": task_type,
                        "submitted_at": submitted_at,
                        "completed_at": utc_now(),
                        "campaign_elapsed_sec": round(time.monotonic() - campaign_started, 6),
                        "winner": outcome.winner,
                        "status": outcome.status,
                        "latency_ms": latency_ms,
                        "reassignments": outcome.reassignments,
                        "proposals_json": json.dumps(outcome.proposals, ensure_ascii=False, sort_keys=True),
                        "refusals_json": json.dumps(outcome.refusals, ensure_ascii=False, sort_keys=True),
                        "result_pid": result_output.get("pid", ""),
                        "result_host": result_output.get("host", ""),
                        "idempotency_replayed": bool(result_output.get("_idempotency_replayed")),
                    }
                )
                task_handle.flush()
                next_submission += task_interval_sec
                if time.monotonic() >= next_checkpoint:
                    write_json_atomic(
                        paths["checkpoint"],
                        make_checkpoint(
                            run_id=run_id,
                            started_at=started_at,
                            target_duration_sec=duration_sec,
                            campaign_started=campaign_started,
                            submitted=submitted,
                            successful=successful,
                            failed=failed,
                            winners=winners,
                            last_task_id=last_task_id,
                        ),
                    )
                    next_checkpoint = time.monotonic() + checkpoint_interval_sec

            controlled = {
                "enabled": not args.skip_controlled_crash,
                "status": "SKIPPED" if args.skip_controlled_crash else "PENDING",
            }
            if not args.skip_controlled_crash:
                counter_key = f"{namespace}:controlled_crash_effect_counter"
                crash_task_id = f"{run_id}-controlled-crash"
                crash_outcome = coordinator.negotiate(
                    AgentTask(
                        task_id=crash_task_id,
                        task_type=str(config["controlled_failure"]["task_type"]),
                        payload={
                            "values": [2, 3, 5, 7],
                            "idempotency_key": f"{run_id}-controlled-crash-effect",
                            "effect_counter_key": counter_key,
                            "crash_after_persisted_result": True,
                        },
                    )
                )
                result_output = crash_outcome.result.output if crash_outcome.result else {}
                effect_count = int(bus.client.get(counter_key) or 0)
                writer.writerow(
                    {
                        "task_index": submitted,
                        "task_id": crash_task_id,
                        "task_type": str(config["controlled_failure"]["task_type"]),
                        "submitted_at": utc_now(),
                        "completed_at": utc_now(),
                        "campaign_elapsed_sec": round(time.monotonic() - campaign_started, 6),
                        "winner": crash_outcome.winner,
                        "status": crash_outcome.status,
                        "latency_ms": round(crash_outcome.elapsed_sec * 1000, 6),
                        "reassignments": crash_outcome.reassignments,
                        "proposals_json": json.dumps(crash_outcome.proposals, ensure_ascii=False, sort_keys=True),
                        "refusals_json": json.dumps(crash_outcome.refusals, ensure_ascii=False, sort_keys=True),
                        "result_pid": result_output.get("pid", ""),
                        "result_host": result_output.get("host", ""),
                        "idempotency_replayed": bool(result_output.get("_idempotency_replayed")),
                    }
                )
                task_handle.flush()
                controlled = {
                    "enabled": True,
                    "status": "PASSED"
                    if crash_outcome.status == "ok"
                    and crash_outcome.reassignments >= 1
                    and bool(result_output.get("_idempotency_replayed"))
                    and effect_count == 1
                    else "FAILED",
                    "task_id": crash_task_id,
                    "winner_after_reassignment": crash_outcome.winner,
                    "reassignments": crash_outcome.reassignments,
                    "idempotency_replayed": bool(result_output.get("_idempotency_replayed")),
                    "persistent_effects": effect_count,
                    "duplicate_effects": max(0, effect_count - 1),
                    "latency_ms": round(crash_outcome.elapsed_sec * 1000, 6),
                }

        elapsed_sec = time.monotonic() - campaign_started
        events = bus.read(run_id=run_id, count=250_000)
        with paths["messages"].open("w", encoding="utf-8") as handle:
            for message in events:
                handle.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
        message_counts = Counter(message.message_type for message in events)
        completed_keys = RedisIdempotencyStore(bus.client, f"{namespace}:idempotency").completed_count()
        run_status = (
            "COMPLETED"
            if successful == submitted
            and elapsed_sec >= duration_sec
            and len(registry_hosts) >= 2
            and (args.skip_controlled_crash or controlled["status"] == "PASSED")
            else "FAILED"
        )
        summary = {
            "schema_version": 1,
            "experiment_id": "cnp_endurance_multivm",
            "run_id": run_id,
            "status": run_status,
            "started_at": started_at,
            "completed_at": utc_now(),
            "config": relative(config_path),
            "git_commit": git_commit(),
            "topology": {
                "coordinator_host": socket.gethostname(),
                "redis_url": args.redis_url,
                "redis_version": bus.client.info("server").get("redis_version"),
                "agents": {agent_id: registry[agent_id] for agent_id in agent_ids},
                "distinct_agent_hosts": sorted(registry_hosts),
            },
            "target_duration_sec": duration_sec,
            "observed_duration_sec": round(elapsed_sec, 6),
            "task_interval_sec": task_interval_sec,
            "submitted_tasks": submitted,
            "successful_tasks": successful,
            "failed_tasks": failed,
            "throughput_tasks_sec": round(successful / elapsed_sec, 6),
            "latency_mean_ms": round(fmean(latencies), 6) if latencies else 0.0,
            "latency_median_ms": round(median(latencies), 6) if latencies else 0.0,
            "latency_p95_ms": round(percentile(latencies, 0.95), 6),
            "latency_p99_ms": round(percentile(latencies, 0.99), 6),
            "tasks_by_agent": dict(winners),
            "reassignments_during_endurance": reassignments,
            "message_counts": dict(message_counts),
            "message_events_retained": len(events),
            "message_counts_scope": "retained Redis stream snapshot",
            "redis_completed_idempotency_keys": completed_keys,
            "controlled_failure": controlled,
            "scope": config["claim_scope"],
        }
        write_json_atomic(paths["summary"], summary)
        write_json_atomic(
            paths["checkpoint"],
            {
                "run_id": run_id,
                "status": run_status,
                "started_at": started_at,
                "completed_at": summary["completed_at"],
                "target_duration_sec": duration_sec,
                "elapsed_sec": round(elapsed_sec, 6),
                "submitted_tasks": submitted,
                "successful_tasks": successful,
                "failed_tasks": failed,
            },
        )
        paths["report"].write_text(
            "\n".join(
                [
                    "# Campagne d'endurance CNP Redis multi-VM",
                    "",
                    f"- Run : `{run_id}`",
                    f"- Statut : `{run_status}`",
                    f"- Duree cible/observee : `{duration_sec:.3f}` / `{elapsed_sec:.3f}` s",
                    f"- Taches reussies : `{successful}/{submitted}`",
                    f"- Debit : `{summary['throughput_tasks_sec']}` tache/s",
                    f"- Latence p95/p99 : `{summary['latency_p95_ms']}` / `{summary['latency_p99_ms']}` ms",
                    f"- Repartition : `{json.dumps(dict(winners), ensure_ascii=False)}`",
                    f"- Hotes agents : `{json.dumps(sorted(registry_hosts), ensure_ascii=False)}`",
                    f"- Test post-persistance/pre-RESULT : `{controlled['status']}`",
                    f"- Effets persistants/dupliques : `{controlled.get('persistent_effects', 'NA')}` / `{controlled.get('duplicate_effects', 'NA')}`",
                    "",
                    "Portee : endurance et reprise du Contract Net dans la topologie de laboratoire. Redis reste centralise ; la haute disponibilite et les partitions reseau ne sont pas evaluees.",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        build_manifest(
            paths["manifest"],
            run_id,
            [
                config_path,
                paths["summary"],
                paths["tasks"],
                paths["messages"],
                paths["checkpoint"],
                paths["report"],
                Path(__file__),
                ROOT / "scripts" / "logminer_redis_cnp_agent.py",
                ROOT / "scripts" / "start_cnp_endurance_multivm_agents.ps1",
                ROOT / "scripts" / "finalize_cnp_endurance_multivm_agents.ps1",
                ROOT / "src" / "logminer" / "agents" / "bus.py",
                ROOT / "src" / "logminer" / "agents" / "contract_net.py",
                ROOT / "src" / "logminer" / "agents" / "redis_contract_net.py",
                ROOT / "src" / "logminer" / "agents" / "idempotency.py",
                ROOT / "src" / "logminer" / "agents" / "intelligent_runtime.py",
            ],
        )
        append_ledger(
            status=run_status,
            completed_at=summary["completed_at"],
            raw_result_path=relative(paths["tasks"]),
            summary_path=relative(paths["summary"]),
            notes=(
                f"duration={elapsed_sec:.3f}; tasks={successful}/{submitted}; "
                f"controlled_failure={controlled['status']}"
            ),
            **ledger_base,
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
        return 0 if run_status == "COMPLETED" else 1
    except Exception as exc:
        paths["error"].write_text(traceback.format_exc(), encoding="utf-8")
        append_ledger(
            status="FAILED",
            completed_at=utc_now(),
            error_path=relative(paths["error"]),
            notes=f"{type(exc).__name__}: {exc}",
            **ledger_base,
        )
        raise


if __name__ == "__main__":
    raise SystemExit(main())
