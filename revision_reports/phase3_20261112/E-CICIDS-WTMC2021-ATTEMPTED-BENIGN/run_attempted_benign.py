"""E-CICIDS-WTMC2021-ATTEMPTED-BENIGN : variante d'E-CICIDS-WTMC2021-HOLDOUT.

Seule différence : les flux étiquetés « - Attempted » sont comptés **bénins**, comme le
recommandent les auteurs du jeu (page Dataset_Download du projet CNS 2022), au lieu d'être
exclus. Tout le reste (données, scénarios, variables, tirage, modèles, graines, plafonds,
règle de décision) est importé sans modification de
revision_reports/phase2_20261112/E-CICIDS-WTMC2021-HOLDOUT/run_e_cicids_wtmc2021_holdout.py.

Usage : python run_attempted_benign.py [--dry-run]
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "revision_reports" / "phase2_20261112" / "E-CICIDS-WTMC2021-HOLDOUT"))
import run_e_cicids_wtmc2021_holdout as wtmc  # noqa: E402

wtmc.OUTPUT_DIR = ROOT / "experiments/phase_revision_20261112/E-CICIDS-WTMC2021-ATTEMPTED-BENIGN"


def build_plans(files, labels):
    plans = []
    for s_index, (scenario, (day, is_scn)) in enumerate(wtmc.SCENARIOS.items()):
        flags = {}
        for name, lab in labels.items():
            attempted = np.char.endswith(lab.astype(str), "- Attempted")
            benign = (lab == "BENIGN") | attempted
            in_scn = np.array([is_scn(x) for x in lab]) & ~attempted
            flags[name] = (benign, in_scn, ~benign & ~in_scn)
        for seed in wtmc.SEEDS:
            rng = np.random.default_rng([seed, s_index])
            plan = {"scenario": scenario, "seed": seed, "heldout": day, "train": {}, "test": {}}
            for cls in (0, 1):
                keys = []
                for fid, path in enumerate(files):
                    benign, _scn, other = flags[path.name]
                    mask = (benign if path.name != day else np.zeros_like(benign)) if cls == 0 else other
                    rows = np.flatnonzero(mask)
                    keys.append(np.stack([np.full(len(rows), fid), rows], axis=1))
                pool = np.concatenate(keys)
                chosen = pool[wtmc.base.draw(np.arange(len(pool)), wtmc.TRAIN, rng)]
                for fid, path in enumerate(files):
                    picked = chosen[chosen[:, 0] == fid, 1]
                    if len(picked):
                        plan["train"].setdefault(path.name, {})[cls] = picked
                benign, scn, _ = flags[day]
                plan["test"].setdefault(day, {})[cls] = wtmc.base.draw(np.flatnonzero(scn if cls else benign), wtmc.TEST, rng)
            plans.append(plan)
    return plans


wtmc.build_plans = build_plans

if __name__ == "__main__":
    raise SystemExit(wtmc.main())
