"""Worker Redis Streams pour executer les workflows Logminer en file.

Le worker lit `logminer:jobs` avec un consumer group, execute le workflow
route -> detection -> correlation, publie les etats dans `logminer:events`,
puis acquitte le job. Plusieurs workers peuvent tourner en parallele avec des
noms de consumer differents.
"""

from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path
from time import sleep
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = REPO_ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

import api  # noqa: E402


def _run_job(job: dict[str, Any], *, job_stream: str, group: str, ack_failed: bool) -> bool:
    payload = dict(job.get("payload") or {})
    run_id = str(payload.get("run_id") or job.get("run_id") or "")
    bus = api._redis_bus(run_id)
    job_id = str(job.get("id"))
    try:
        input_path = api._existing_path(str(payload["input_path"]))
        request = api.RunRequest(
            input_path=str(input_path),
            parse_if_needed=bool(payload.get("parse_if_needed", True)),
            out_dir=str(payload.get("out_dir", "data/processed")),
            sep=str(payload.get("sep", "auto")),
            sample_rows=int(payload.get("sample_rows", 1000)),
            window_minutes=int(payload.get("window_minutes", 15)),
            run_id=run_id,
            use_redis=True,
        )
        bus.publish(
            source="worker",
            target="orchestrator",
            message_type="workflow.worker.started",
            payload={"job_id": job_id, "job_stream": job_stream, "run_id": run_id},
        )
        result = api._run_workflow(request, input_path, run_id, bus)
        bus.publish(
            source="worker",
            target="api",
            message_type="workflow.worker.completed",
            payload={"job_id": job_id, "job_stream": job_stream, **result},
        )
        bus.ack_job(job_id, stream=job_stream, group=group)
        return True
    except Exception as exc:
        bus.publish(
            source="worker",
            target="api",
            message_type="workflow.worker.failed",
            payload={"job_id": job_id, "job_stream": job_stream, "error": str(exc)},
            status="error",
        )
        if ack_failed:
            bus.ack_job(job_id, stream=job_stream, group=group)
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consomme les jobs Logminer depuis Redis Streams")
    parser.add_argument("--stream", default=None, help="Stream de jobs Redis")
    parser.add_argument("--group", default=None, help="Consumer group Redis")
    parser.add_argument("--consumer", default=None, help="Nom du consumer")
    parser.add_argument("--count", type=int, default=1, help="Nombre de jobs lus par cycle")
    parser.add_argument("--block-ms", type=int, default=5000, help="Attente Redis XREADGROUP en millisecondes")
    parser.add_argument("--once", action="store_true", help="Traiter un lot puis quitter")
    parser.add_argument("--idle-sleep", type=float, default=0.5, help="Pause quand aucun job n'est disponible")
    parser.add_argument("--claim-idle-ms", type=int, default=0, help="Reprendre les jobs pending plus vieux que ce delai")
    parser.add_argument("--keep-failed-pending", action="store_true", help="Ne pas acquitter les jobs en erreur")
    args = parser.parse_args(argv)

    settings = api._redis_settings()
    job_stream = args.stream or settings["job_stream"]
    group = args.group or settings["job_group"]
    consumer = args.consumer or f"{socket.gethostname()}-{Path(sys.argv[0]).stem}"
    bus = api._redis_bus()
    bus.ensure_group(group, stream=job_stream, start_id="0")

    while True:
        jobs = []
        if args.claim_idle_ms > 0:
            jobs = bus.claim_stale_jobs(
                stream=job_stream,
                group=group,
                consumer=consumer,
                min_idle_ms=args.claim_idle_ms,
                count=max(1, args.count),
            )
        if not jobs:
            jobs = bus.read_group_jobs(
                stream=job_stream,
                group=group,
                consumer=consumer,
                count=max(1, args.count),
                block_ms=max(0, args.block_ms),
            )
        if not jobs:
            if args.once:
                return 0
            sleep(max(0.0, args.idle_sleep))
            continue

        failures = 0
        for job in jobs:
            ok = _run_job(job, job_stream=job_stream, group=group, ack_failed=not args.keep_failed_pending)
            failures += 0 if ok else 1

        if args.once:
            return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
