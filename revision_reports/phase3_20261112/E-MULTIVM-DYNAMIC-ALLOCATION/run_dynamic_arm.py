"""Exécute un bras du diagnostic multi-VM avec une politique de sélection donnée.

Le protocole de charge, les métriques et les entrées restent ceux du runner gelé
E-MULTIVM-SATURATION-DIAG. Seule la construction du coordinateur ajoute
``selection_policy``.
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "revision_reports/phase2_20261112/E-MULTIVM-SATURATION-DIAG/run_saturation_arm.py"


def main() -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--selection-policy",
        required=True,
        choices=("utility_agent_id", "utility_load", "least_loaded"),
    )
    known, remaining = parser.parse_known_args()
    spec = importlib.util.spec_from_file_location("dynamic_allocation_base", BASE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossible de charger {BASE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    coordinator_class = module.RedisContractNetCoordinator

    def coordinator_factory(*args, **kwargs):
        kwargs["selection_policy"] = known.selection_policy
        return coordinator_class(*args, **kwargs)

    module.RedisContractNetCoordinator = coordinator_factory
    sys.argv = [sys.argv[0], *remaining]
    return int(module.main())


if __name__ == "__main__":
    raise SystemExit(main())
