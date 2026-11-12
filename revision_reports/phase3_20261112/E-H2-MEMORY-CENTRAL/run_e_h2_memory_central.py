"""E-H2-MEMORY-CENTRAL : mémoire de fiabilité greffée sur un répartiteur centralisé.

Question : le gain de la mémoire observé pour Contract Net (E-H5-MEMORY-RELIABILITY) tient-il
aux agents, ou un répartiteur centralisé doté du même compteur lissé l'obtient-il aussi ?

Réutilise sans modification le runner d'E-H5 et d'E-CNP
(revision_reports/chantier_20261105/agent_5/scripts/run_e_h5_e_cnp.py : scénarios E-H5,
instrumentation, contrastes, règle ``decide_memory_level``) et le répartiteur au moindre
chargé d'E-CNP-LEAST-LOADED. Bras :
- ``least_loaded`` : agent le moins occupé, confiance déclarée puis identifiant en départage ;
- ``least_loaded_mem`` : même répartiteur, mais le départage entre agents également chargés
  se fait d'abord par la fiabilité lissée (succès + 1) / (exécutions + 2), tenue par le
  répartiteur pour chaque couple (agent, type de tâche) et mise à jour après chaque exécution ;
- ``D`` : Contract Net avec mémoire (référence d'E-H5).

Hors ``--smoke``, refuse de s'exécuter si le protocole n'est pas commité et inscrit au registre.
Usage : python run_e_h2_memory_central.py [--smoke DOSSIER]
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "chantier_20261105" / "agent_5" / "scripts"))
import run_e_h5_e_cnp as base  # noqa: E402
import run_e_cnp_least_loaded as ll  # noqa: E402

ID = "E-H2-MEMORY-CENTRAL"
PROTOCOL = Path(__file__).resolve().parent / "PROTOCOLE.md"
OUT = ROOT / "experiments" / "phase_revision_20261112" / ID
SEEDS = tuple(20_261_601 + index for index in range(30))
ARMS = ("least_loaded", "least_loaded_mem", "D")
_ORIGINAL_STATIC = base.run_static


def run_least_loaded_memory(agents, tasks, workers):
    table = base.declared_order(agents)
    lock = threading.Lock()
    successes: dict[tuple[str, str], int] = {}
    executions: dict[tuple[str, str], int] = {}

    def reliability(agent_id, task_type):
        key = (agent_id, task_type)
        with lock:
            return (successes.get(key, 0) + 1) / (executions.get(key, 0) + 2)

    def record(agent_id, task_type, ok):
        key = (agent_id, task_type)
        with lock:
            executions[key] = executions.get(key, 0) + 1
            successes[key] = successes.get(key, 0) + int(ok)

    def run_one(task):
        started = time.perf_counter()
        order = table[task.task_type]
        rank = {agent.agent_id: index for index, agent in enumerate(order)}
        remaining = list(order)
        reassignments, attempt, success = 0, 0, False
        while remaining:
            agent = min(remaining, key=lambda a: (a.perceive().load_ratio,
                                                  -reliability(a.agent_id, task.task_type),
                                                  rank[a.agent_id]))
            remaining.remove(agent)
            if attempt > 0:
                reassignments += 1
            attempt += 1
            if not agent.accept(task):
                continue
            result = agent.execute_task(task, 0.0, [])
            record(agent.agent_id, task.task_type, result.status == "ok")
            if result.status == "ok":
                success = True
                break
        return task.task_id, success, time.perf_counter() - started, reassignments

    if workers <= 1:
        return [run_one(task) for task in tasks], 0
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="llmem") as executor:
        futures = [executor.submit(run_one, task) for task in tasks]
        return [future.result() for future in as_completed(futures)], 0


def execute(scenario, arm, seed, load):
    if arm == "D":
        return base.execute_run(ID, scenario, "D", seed, base.WORKERS, load)
    base.run_static = ll.run_least_loaded if arm == "least_loaded" else run_least_loaded_memory
    try:
        row = base.execute_run(ID, scenario, "static", seed, base.WORKERS, load)
    finally:
        base.run_static = _ORIGINAL_STATIC
    row["arm"] = arm
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
    for scenario in base.E_H5_SCENARIOS:
        for position, seed in enumerate(seeds):
            rotation = position % len(ARMS)
            for arm in ARMS[rotation:] + ARMS[:rotation]:
                rows.append(execute(scenario, arm, seed, load))
        print(f"{scenario.name} terminé", flush=True)
    runs_path = out / "runs.csv"
    base.write_csv(runs_path, rows)
    results = {}
    for arm, reference in (("least_loaded_mem", "least_loaded"), ("least_loaded_mem", "D"), ("D", "least_loaded")):
        contrasts = {s.name: base.contrast(rows, s.name, arm, reference, base.WORKERS) for s in base.E_H5_SCENARIOS}
        levels = {name: base.decide_memory_level(item) for name, item in contrasts.items()}
        results[f"{arm}_minus_{reference}"] = {"contrasts": contrasts, "levels": levels,
                                               "global_decision": base.global_memory(levels)}
    if args.smoke is not None:
        print(f"essai technique conforme : {len(rows)} exécutions, invariants vérifiés")
        return 0
    summary = {"experiment_id": ID, "started_at_utc": started, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
               "load": load, "workers": base.WORKERS, "seeds": list(seeds),
               "environment": {"python": platform.python_version(), "platform": platform.platform()},
               "results": results,
               "global_decision_primary": results["least_loaded_mem_minus_least_loaded"]["global_decision"]}
    summary_path = out / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entries = [("protocol", PROTOCOL), ("runner", Path(__file__).resolve()), ("runner_base", Path(base.__file__).resolve()),
               ("runner_least_loaded", Path(ll.__file__).resolve())]
    entries += [("source", path) for path in base.SOURCES] + [("artifact", runs_path), ("artifact", summary_path)]
    with (out / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["role", "path", "sha256", "bytes"])
        writer.writeheader()
        for role, path in entries:
            writer.writerow({"role": role, "path": base.relative(path), "sha256": base.sha256(path), "bytes": path.stat().st_size})
    print(f"terminé : {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
