"""E-CNP-RECFP-LEAST-LOADED : Contract Net à repli corrigé contre répartiteur au moindre chargé.

Reprend sans modification le runner d'E-CNP-LEAST-LOADED (bras, scénarios, contrastes,
règle de décision, manifeste) ; seuls changent l'identifiant, le protocole, le dossier de
sortie, les graines et le coordinateur Contract Net, désormais doté d'un nouvel appel
d'offres après échec (``fallback_policy="recfp"``, valeur par défaut depuis le
2026-11-12). Hors ``--smoke``, refuse de s'exécuter si le protocole n'est pas commité et
inscrit au registre.

Usage : python run_e_cnp_recfp_least_loaded.py [--smoke DOSSIER]
"""
from __future__ import annotations

import inspect
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "chantier_20261105" / "agent_5" / "scripts"))

import run_e_cnp_least_loaded as ll  # noqa: E402

ID = "E-CNP-RECFP-LEAST-LOADED"
ll.ID = ID
ll.PROTOCOL = Path(__file__).resolve().parent / "PROTOCOLE.md"
ll.OUT = ROOT / "experiments" / "phase_revision_20261112" / ID
ll.SEEDS = tuple(20_261_305 + index for index in range(30))

# Garde-fou : le bras C doit utiliser le coordinateur corrigé.
_default = inspect.signature(ll.base.ContractNetCoordinator.__init__).parameters["fallback_policy"].default
if _default != "recfp":
    raise SystemExit(f"Coordinateur inattendu : fallback_policy par défaut = {_default!r}")
ll.base.SOURCES = tuple(ll.base.SOURCES) + (Path(__file__).resolve(),)

if __name__ == "__main__":
    raise SystemExit(ll.main())
