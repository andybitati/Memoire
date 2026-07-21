"""Consolidate controlled monolith-vs-agents benchmark outputs."""

from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd


CSV_PATH = Path("data/processed/controlled_monolith_vs_agents.csv")
TABLE = Path("docs/memoire/tables/table_controlled_monolith_vs_agents.md")
PACK_TABLE = Path("docs/memoire/pack_redaction_final/10_latex_overleaf/tables/table_controlled_monolith_vs_agents.md")
PACK_CSV = Path("docs/memoire/pack_redaction_final/06_reproductibilite_preuves/controlled_monolith_vs_agents.csv")


def main() -> int:
    frame = pd.read_csv(CSV_PATH)
    frame["cpu_core_max"] = frame[["cpu_core_max", "cpu_core_avg"]].max(axis=1)
    frame.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")
    rows = [
        "# Comparaison Controlee Monolithique Vs Agents",
        "",
        "| Mode | Taches | Echecs | Duree s | Debit t/s | Latence moy. | Latence p95 | CPU moy. | CPU max | RAM max MB | Reprises | Pending final |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for _, row in frame.iterrows():
        rows.append(
            "| {mode} | {tasks_completed:.0f}/{tasks_total:.0f} | {tasks_failed:.0f} | {elapsed_sec:.4f} | {throughput_tasks_sec:.4f} | {task_latency_mean:.4f} | {task_latency_p95:.4f} | {cpu_core_avg:.3f} | {cpu_core_max:.3f} | {ram_mb_max:.3f} | {recovered_tasks:.0f} | {pending_final:.0f} |".format(
                **row
            )
        )
    rows.extend(
        [
            "",
            "Note: les modes executent les memes types de taches et le meme volume sur le meme poste. La variante avec panne simule une tache non acquittee puis une reprise controlee.",
        ]
    )
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text("\n".join(rows) + "\n", encoding="utf-8")
    PACK_TABLE.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(TABLE, PACK_TABLE)
    PACK_CSV.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(CSV_PATH, PACK_CSV)
    print(TABLE.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
