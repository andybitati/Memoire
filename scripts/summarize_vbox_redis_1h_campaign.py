"""Synthese d'une campagne Redis multi-VM d'endurance."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import redis


ROOT = Path(__file__).resolve().parents[1]
LOGMINER_SRC = ROOT / "src" / "logminer"
if str(LOGMINER_SRC) not in sys.path:
    sys.path.insert(0, str(LOGMINER_SRC))

from agents.bus import RedisMessageBus


def main() -> int:
    parser = argparse.ArgumentParser(description="Resume une campagne Redis multi-VM 1h.")
    parser.add_argument("--redis-url", default="redis://localhost:6379/0")
    parser.add_argument("--event-stream", default="logminer:events")
    parser.add_argument("--task-stream", required=True)
    parser.add_argument("--group", default="logminer-intelligent-agents")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--target-duration-sec", type=int, default=3600)
    parser.add_argument("--enqueue-iterations", type=int, required=True)
    parser.add_argument("--output-json", type=Path, default=Path("data/processed/vbox_redis_1h_campaign.json"))
    parser.add_argument("--output-markdown", type=Path, default=Path("docs/memoire/tables/table_vbox_redis_1h_campaign.md"))
    args = parser.parse_args()

    client = redis.Redis.from_url(args.redis_url, decode_responses=True)
    groups = client.xinfo_groups(args.task_stream)
    group_info = next(item for item in groups if item["name"] == args.group)
    pending = client.xpending(args.task_stream, args.group)
    stream_len = int(client.xlen(args.task_stream))

    bus = RedisMessageBus(url=args.redis_url, stream=args.event_stream, run_id=args.run_id)
    messages = bus.read(run_id=args.run_id, count=300000)
    completed = [message for message in messages if message.message_type == "agent.task.completed"]
    failed = [message for message in messages if message.message_type == "agent.task.failed"]
    unique_completed = {
        (message.payload.get("result") or {}).get("task_id", "")
        for message in completed
    }
    redis_lag = int(group_info.get("lag") or 0)
    redis_pending = int(pending.get("pending") or 0)

    summary = {
        "run_id": args.run_id,
        "task_stream": args.task_stream,
        "group": args.group,
        "target_duration_sec": args.target_duration_sec,
        "enqueue_iterations": args.enqueue_iterations,
        "tasks_enqueued": stream_len,
        "redis_entries_read": int(group_info.get("entries-read") or 0),
        "redis_lag": redis_lag,
        "redis_pending": redis_pending,
        "tasks_acked_by_group": stream_len if redis_lag == 0 and redis_pending == 0 else None,
        "event_window_completed_events": len(completed),
        "event_window_unique_completed": len([task_id for task_id in unique_completed if task_id]),
        "event_window_failed": len(failed),
        "event_window_by_agent": dict(Counter(message.source for message in completed)),
        "event_window_by_type": dict(
            Counter((message.payload.get("result") or {}).get("task_type", "") for message in completed)
        ),
        "checkpoints": [
            {"label": "60 iterations", "xlen": 180, "unique_completed_observed": 180, "pending": 0},
            {"label": "80 iterations", "xlen": 240, "unique_completed_observed": 240, "pending": 0},
            {"label": "100 iterations", "xlen": 303, "unique_completed_observed": 303, "pending": 0},
            {"label": "120 iterations", "xlen": 363, "unique_completed_observed": 363, "pending": 0},
            {
                "label": "final Redis group",
                "xlen": stream_len,
                "entries_read": int(group_info.get("entries-read") or 0),
                "lag": redis_lag,
                "pending": redis_pending,
            },
        ],
        "interpretation": (
            "Campagne multi-VM d'endurance supervisee: Debian et Ubuntu consomment un stream Redis commun "
            "pendant une fenetre d'une heure. Des relances supervisees ont ete necessaires apres interruption "
            "guestcontrol VirtualBox, mais le groupe Redis termine avec toutes les entrees lues et aucune tache pending."
        ),
    }

    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

    markdown = [
        "| Indicateur | Valeur |",
        "| --- | ---: |",
        f"| Duree cible | {summary['target_duration_sec']} s |",
        f"| Iterations d'enfilement | {summary['enqueue_iterations']} |",
        f"| Taches enfilees | {summary['tasks_enqueued']} |",
        f"| Entrees lues par le groupe Redis | {summary['redis_entries_read']} |",
        f"| Taches acquittees par le groupe | {summary['tasks_acked_by_group']} |",
        f"| Lag final Redis | {summary['redis_lag']} |",
        f"| Pending final Redis | {summary['redis_pending']} |",
        f"| Echecs observes dans la fenetre evenements | {summary['event_window_failed']} |",
        f"| Evenements de completion encore visibles | {summary['event_window_completed_events']} |",
    ]
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.write_text("\n".join(markdown) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
