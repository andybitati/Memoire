"""E-R2-AGENTS-NO-STORE : ablation du magasin d'idempotence sur les architectures à agents.

Complète la panne appariée A-D (revision_reports/agent_3/run_paired_failure_abcd.py),
dont il réutilise sans modification la charge, le point de panne, la politique de reprise
et les fonctions d'exécution. Huit architectures, exécutées dans le même processus et sur
les mêmes graines : A, B, C, D, A+I, B+I (identiques à la campagne d'origine), et
C-I, D-I : Contract Net (mémoire désactivée ou activée) **sans** magasin d'idempotence.

Protocole : revision_reports/phase2_20261112/E-R2-AGENTS-NO-STORE/PROTOCOLE.md.
Sorties : experiments/phase_revision_20261112/E-R2-AGENTS-NO-STORE/.

Usage : python run_e_r2_agents_no_store.py [--smoke]
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import statistics
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "agent_3"))

import run_paired_failure_abcd as base  # noqa: E402

EXPERIMENT = "E-R2-AGENTS-NO-STORE"
OUT = ROOT / "experiments" / "phase_revision_20261112" / EXPERIMENT
SEEDS = tuple(range(42, 52))
ARCHITECTURES = ("A", "B", "C", "D", "A+I", "B+I", "C-I", "D-I")
STORE_ARCHITECTURES = {"C", "D", "A+I", "B+I"}


def run_one(architecture: str, seed: int, run_id: str, scratch: Path) -> dict:
    tasks = base.workload(seed)
    ledger = base.EffectLedger()
    uses_store = architecture in STORE_ARCHITECTURES
    store = (
        base.SQLiteIdempotencyStore(scratch / f"{architecture.replace('+', '_')}_{seed}.sqlite3")
        if uses_store else None
    )
    if architecture in {"A", "A+I"}:
        info = base.run_plain(tasks, workers=1, store=store, ledger=ledger)
    elif architecture in {"B", "B+I"}:
        info = base.run_plain(tasks, workers=base.WORKERS, store=store, ledger=ledger)
    else:
        info = base.run_cnp(
            tasks,
            memory_enabled=architecture in {"D", "D-I"},
            store=store,
            ledger=ledger,
            run_id=run_id,
        )
    keys = [str(task.payload["idempotency_key"]) for task in tasks]
    crashed_key = keys[base.CRASH_INDEX]
    lost = sum(key not in ledger.committed for key in keys)
    return {
        "run_id": run_id,
        "architecture": architecture,
        "seed": seed,
        "tasks": len(tasks),
        "crash_index": base.CRASH_INDEX,
        "idempotency_store": uses_store,
        "lost_tasks": lost,
        "duplicate_effects": sum(max(0, ledger.effects[key] - 1) for key in keys),
        "crashed_task_effects": ledger.effects[crashed_key],
        "recovered_tasks": int(crashed_key in ledger.committed),
        "idempotency_replayed": bool(info["idempotency_replayed"]),
        "reassignments": info["reassignments"],
        "recovery_latency_ms": round((info["recovered_at"] - info["crash_at"]) * 1000.0, 6),
    }


def decide(summary: dict) -> dict:
    """Règle de décision préenregistrée (PROTOCOLE.md, section 4)."""
    out = {}
    for arch in ("C-I", "D-I"):
        s = summary[arch]
        if s["lost_tasks_total"] > 0:
            verdict = "invalide_perte_de_tache"
        elif s["seeds_with_duplicate"] >= 9:
            verdict = "doublon_sans_magasin"
        elif s["seeds_with_duplicate"] == 0:
            verdict = "pas_de_doublon_sans_magasin"
        else:
            verdict = "indetermine"
        out[arch] = verdict
    if all(v == "doublon_sans_magasin" for v in out.values()):
        out["conclusion"] = "absence_de_doublon_due_au_magasin"
    elif all(v == "pas_de_doublon_sans_magasin" for v in out.values()):
        out["conclusion"] = "les_agents_evitent_le_doublon_sans_magasin"
    else:
        out["conclusion"] = "non_tranche"
    return out


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="une graine, sans écrire d'artefact")
    args = parser.parse_args()
    seeds = SEEDS[:1] if args.smoke else SEEDS
    started = datetime.now(timezone.utc)
    run_id = EXPERIMENT.lower().replace("-", "_") + "_" + started.strftime("%Y%m%dT%H%M%SZ")
    rows = []
    with tempfile.TemporaryDirectory(prefix="e_r2_") as tmp:
        for seed in seeds:
            for architecture in ARCHITECTURES:
                rows.append(run_one(architecture, seed, run_id, Path(tmp)))
    summary = {}
    for architecture in ARCHITECTURES:
        subset = [r for r in rows if r["architecture"] == architecture]
        lat = [r["recovery_latency_ms"] for r in subset]
        summary[architecture] = {
            "repetitions": len(subset),
            "idempotency_store": subset[0]["idempotency_store"],
            "lost_tasks_total": sum(r["lost_tasks"] for r in subset),
            "duplicate_effects_total": sum(r["duplicate_effects"] for r in subset),
            "seeds_with_duplicate": sum(r["duplicate_effects"] > 0 for r in subset),
            "recovered_tasks_total": sum(r["recovered_tasks"] for r in subset),
            "idempotency_replays": sum(r["idempotency_replayed"] for r in subset),
            "recovery_latency_median_ms": round(statistics.median(lat), 6),
        }
    if args.smoke:
        print(json.dumps({"smoke": True, "summary": summary}, ensure_ascii=False, indent=2))
        return 0
    decision = decide(summary)
    OUT.mkdir(parents=True, exist_ok=True)
    runs_path = OUT / "runs.csv"
    with runs_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    payload = {
        "experiment_id": EXPERIMENT,
        "run_id": run_id,
        "started_at_utc": started.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "seeds": list(seeds),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "summary": summary,
        "decision": decision,
    }
    summary_path = OUT / "summary.json"
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sources = [Path(__file__).resolve(), ROOT / "revision_reports" / "agent_3" / "run_paired_failure_abcd.py",
               ROOT / "src" / "logminer" / "agents" / "contract_net.py",
               ROOT / "src" / "logminer" / "agents" / "intelligent_runtime.py",
               ROOT / "src" / "logminer" / "agents" / "idempotency.py"]
    with (OUT / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["role", "path", "bytes", "sha256"])
        for role, path in [("artifact", runs_path), ("artifact", summary_path)] + [("source", p) for p in sources]:
            writer.writerow([role, path.relative_to(ROOT).as_posix(), path.stat().st_size, sha256(path)])
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
