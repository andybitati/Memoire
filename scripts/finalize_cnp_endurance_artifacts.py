#!/usr/bin/env python3
"""Finalise la provenance d'un run CNP après collecte des journaux invités."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE_ROOT = ROOT / "experiments" / "phase_cnp_endurance"
RUN_ID_PATTERN = re.compile(r"^cnp_endurance_multivm_\d{8}T\d{6}Z$")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, payload: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Finalisation des artefacts CNP multi-VM")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run_id = args.run_id
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("run_id non canonique")

    summary_path = PHASE_ROOT / "aggregated" / f"{run_id}__summary.json"
    report_path = PHASE_ROOT / "reports" / f"{run_id}__report.md"
    messages_path = PHASE_ROOT / "logs" / f"{run_id}__messages.jsonl"
    manifest_path = PHASE_ROOT / "manifests" / f"{run_id}__manifest.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("status") != "COMPLETED":
        raise RuntimeError("seul un run COMPLETED peut être finalisé")

    retained_events = sum(1 for _ in messages_path.open("r", encoding="utf-8"))
    summary["message_events_retained"] = retained_events
    summary["message_counts_scope"] = "retained tail only; not complete-run totals"
    summary["message_stream_retention_note"] = (
        "During this run, agent writers used approximate maxlen=10000; "
        "protocol-message counts are therefore excluded from scientific conclusions."
    )
    write_json_atomic(summary_path, summary)

    report = report_path.read_text(encoding="utf-8").rstrip()
    marker = "## Complétude de la trace de messages"
    if marker not in report:
        report += (
            "\n\n## Complétude de la trace de messages\n\n"
            f"La trace conserve la fenêtre terminale de `{retained_events}` événements. "
            "Les compteurs de types de messages ne décrivent donc pas l'heure complète et "
            "ne sont pas utilisés pour les conclusions scientifiques. Les métriques par tâche, "
            "le résultat de reprise et le magasin d'idempotence restent complets.\n"
        )
        report_path.write_text(report + "\n", encoding="utf-8")

    provenance = [
        ROOT / "scripts" / "run_cnp_endurance_multivm.py",
        ROOT / "scripts" / "logminer_redis_cnp_agent.py",
        ROOT / "scripts" / "start_cnp_endurance_multivm_agents.ps1",
        ROOT / "scripts" / "finalize_cnp_endurance_multivm_agents.ps1",
        ROOT / "scripts" / "finalize_cnp_endurance_artifacts.py",
        ROOT / "src" / "logminer" / "agents" / "bus.py",
        ROOT / "src" / "logminer" / "agents" / "contract_net.py",
        ROOT / "src" / "logminer" / "agents" / "redis_contract_net.py",
        ROOT / "src" / "logminer" / "agents" / "idempotency.py",
        ROOT / "src" / "logminer" / "agents" / "intelligent_runtime.py",
        PHASE_ROOT / "configs" / "cnp_endurance_multivm_protocol.json",
    ]
    run_files = [path for path in PHASE_ROOT.rglob(f"{run_id}__*") if path != manifest_path]
    records = []
    for path in sorted(set(run_files + provenance)):
        if path.is_file():
            records.append(
                {
                    "path": path.relative_to(ROOT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
    write_json_atomic(
        manifest_path,
        {
            "schema_version": 1,
            "run_id": run_id,
            "generated_at": utc_now(),
            "files": records,
        },
    )
    print(json.dumps({"run_id": run_id, "files": len(records), "retained_events": retained_events}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
