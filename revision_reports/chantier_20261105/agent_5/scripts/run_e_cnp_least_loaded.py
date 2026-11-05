"""E-CNP-LEAST-LOADED : Contract Net contre un répartiteur au moindre chargé, sans négociation.

Réutilise sans modification le runner d'E-H5 et d'E-CNP (instrumentation, scénarios, contrastes et
règle de décision). Seul le répartiteur est nouveau. Hors mode ``--smoke``, le programme refuse de
s'exécuter si le protocole n'est pas commité et inscrit au registre.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import run_e_h5_e_cnp as base  # noqa: E402

ID = "E-CNP-LEAST-LOADED"
PROTOCOL = base.CHANTIER / "agent_5/protocoles" / f"{ID}.md"
OUT = base.ROOT / "experiments/phase_revision_20261105" / ID
SEEDS = tuple(20_261_205 + index for index in range(30))
ARMS = ("least_loaded", "C", "static")
_ORIGINAL_STATIC = base.run_static


def run_least_loaded(agents, tasks, workers):
    """Choisit l'agent le moins chargé ; confiance déclarée puis identifiant en départage."""

    table = base.declared_order(agents)

    def run_one(task):
        started = time.perf_counter()
        order = table[task.task_type]
        rank = {agent.agent_id: index for index, agent in enumerate(order)}
        remaining = list(order)
        reassignments = 0
        success = False
        attempt = 0
        while remaining:
            agent = min(remaining, key=lambda item: (item.perceive().load_ratio, rank[item.agent_id]))
            remaining.remove(agent)
            if attempt > 0:
                reassignments += 1
            attempt += 1
            if not agent.accept(task):
                continue
            result = agent.execute_task(task, 0.0, [])
            if result.status == "ok":
                success = True
                break
        return task.task_id, success, time.perf_counter() - started, reassignments

    if workers <= 1:
        return [run_one(task) for task in tasks], 0
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="least") as executor:
        futures = [executor.submit(run_one, task) for task in tasks]
        return [future.result() for future in as_completed(futures)], 0


def execute(scenario, arm, seed, load):
    if arm != "least_loaded":
        return base.execute_run(ID, scenario, arm, seed, base.WORKERS, load)
    # L'instrumentation et les invariants d'execute_run sont réutilisés tels quels.
    base.run_static = run_least_loaded
    try:
        row = base.execute_run(ID, scenario, "static", seed, base.WORKERS, load)
    finally:
        base.run_static = _ORIGINAL_STATIC
    row["arm"] = "least_loaded"
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", type=Path)
    args = parser.parse_args()
    if args.smoke is not None:
        seeds, load, out = (1, 2), 40, args.smoke
    else:
        base.require_preregistered(ID, PROTOCOL)
        seeds, load, out = SEEDS, base.LOAD, OUT
        if (out / "summary.json").exists():
            raise SystemExit("Artefacts déjà présents, refus d'écraser")
    out.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()

    rows = []
    for scenario in base.E_CNP_SCENARIOS:
        for position, seed in enumerate(seeds):
            rotation = position % len(ARMS)
            for arm in ARMS[rotation:] + ARMS[:rotation]:
                rows.append(execute(scenario, arm, seed, load))
        print(f"{scenario.name} terminé", flush=True)
    runs_path = out / "runs.csv"
    base.write_csv(runs_path, rows)

    results = {}
    for arm, reference in (("C", "least_loaded"), ("least_loaded", "static"), ("C", "static")):
        contrasts = {s.name: base.contrast(rows, s.name, arm, reference, base.WORKERS) for s in base.E_CNP_SCENARIOS}
        decisions = {name: base.decide_contract_net(contrasts[name]) for name in base.E_CNP_DECISION_SCENARIOS}
        results[f"{arm}_minus_{reference}"] = {
            "contrasts": contrasts,
            "decisions": decisions,
            "global_decision": base.global_contract_net(decisions),
        }
    if args.smoke is not None:
        print(f"essai technique conforme : {len(rows)} exécutions, invariants vérifiés")
        return 0

    summary = {
        "experiment_id": ID,
        "started_at_utc": started,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "load": load,
        "workers": base.WORKERS,
        "seeds": list(seeds),
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "results": results,
        "global_decision_primary": results["C_minus_least_loaded"]["global_decision"],
    }
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entries = [("protocol", PROTOCOL), ("runner", Path(__file__).resolve()), ("runner_base", Path(base.__file__).resolve())]
    entries += [("source", path) for path in base.SOURCES]
    entries += [("artifact", runs_path), ("artifact", summary_path)]
    with (out / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "path", "sha256", "bytes"])
        writer.writeheader()
        for role, path in entries:
            writer.writerow({"role": role, "path": base.relative(path), "sha256": base.sha256(path), "bytes": path.stat().st_size})
    print(f"terminé : {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
