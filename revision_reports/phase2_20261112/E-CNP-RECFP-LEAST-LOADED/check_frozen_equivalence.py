"""Contrôle technique : le mode ``fallback_policy="frozen"`` du coordinateur corrigé
reproduit exactement l'ancien coordinateur (commit b92ea2e) sur les scénarios E-CNP.

Exécution séquentielle (1 worker), donc déterministe : on compare, par scénario et
graine, les compteurs qui ne dépendent pas du temps (succès, échecs à la première
exécution, exécutions par agent, réattributions, messages). Graines 1 et 2, charge 200 :
aucune graine de campagne n'est consommée.

Usage : python check_frozen_equivalence.py
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "chantier_20261105" / "agent_5" / "scripts"))
import run_e_h5_e_cnp as base  # noqa: E402

OLD_COMMIT = "b92ea2e"
KEYS = ("successful_tasks", "final_failures", "first_execution_failures", "executions",
        "executions_by_agent", "reassignments", "messages_per_task")


def load_old_coordinator():
    source = subprocess.run(["git", "show", f"{OLD_COMMIT}:src/logminer/agents/contract_net.py"],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=True).stdout
    tmp = Path(tempfile.mkdtemp()) / "contract_net_old.py"
    tmp.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("agents.contract_net_old", tmp)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.ContractNetCoordinator


def run(coordinator_factory):
    original = base.ContractNetCoordinator
    base.ContractNetCoordinator = coordinator_factory
    try:
        rows = []
        for scenario in base.E_CNP_SCENARIOS:
            for seed in (1, 2):
                rows.append(base.execute_run("CHECK", scenario, "C", seed, 1, 200))
        return rows
    finally:
        base.ContractNetCoordinator = original


def main() -> int:
    from agents.contract_net import ContractNetCoordinator as New
    old_rows = run(load_old_coordinator())
    frozen_rows = run(lambda agents, **kw: New(agents, fallback_policy="frozen", **kw))
    mismatches = 0
    for a, b in zip(old_rows, frozen_rows):
        for key in KEYS:
            if a[key] != b[key]:
                mismatches += 1
                print("ECART", a["scenario"], a["seed"], key, a[key], b[key])
    print(f"{len(old_rows)} exécutions comparées, {mismatches} écart(s)")
    return 1 if mismatches else 0


if __name__ == "__main__":
    raise SystemExit(main())
