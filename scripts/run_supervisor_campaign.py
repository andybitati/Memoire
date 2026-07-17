"""Campagne multi-cycles du SupervisorAgent.

Produit des artefacts exploitables dans le memoire et l'article:
- data/processed/supervisor_campaign.csv
- docs/memoire/tables/table_supervisor_campaign.md
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from logminer.agents.supervisor_agent import run_supervisor_campaign


TABLES = ROOT / "docs" / "memoire" / "tables"


def _family(result: Any) -> str:
    return str(((result.workflow or {}).get("route") or {}).get("family") or "")


def _timing(result: Any, key: str) -> str:
    value = ((result.workflow or {}).get("timings") or {}).get(key)
    return "" if value is None else str(value)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def write_table(path: Path, rows: list[dict[str, Any]]) -> None:
    ok = sum(1 for row in rows if row["status"] == "ok")
    families = sorted({row["family"] for row in rows if row["family"]})
    selected = ", ".join(Path(row["selected_path"]).name for row in rows if row["selected_path"])
    lines = [
        "# Campagne Multi-Cycles SupervisorAgent",
        "",
        "| Indicateur | Valeur |",
        "| --- | --- |",
        f"| Cycles | {len(rows)} |",
        f"| Cycles OK | {ok} |",
        f"| Familles routees | {', '.join(families) or 'n/a'} |",
        f"| Sources choisies | {selected or 'n/a'} |",
        f"| Duree moyenne | {sum(float(row['elapsed_sec']) for row in rows) / max(1, len(rows)):.4f} s |",
        "",
        "| Cycle | Source | Famille | Decision | Statut | Duree s |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        decision = f"sample={row['sample_rows']}, window={row['window_minutes']}, max_mb={row['max_mb']}"
        lines.append(
            f"| {row['cycle']} | `{Path(row['selected_path']).name}` | {row['family']} | {decision} | {row['status']} | {row['elapsed_sec']} |"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Campagne SupervisorAgent")
    parser.add_argument("--root", action="append", dest="roots", default=[])
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--max-files", type=int, default=20)
    parser.add_argument("--max-mb", type=int, default=1)
    parser.add_argument("--out-dir", default="data/processed")
    parser.add_argument("--bus", default="data/processed/supervisor_campaign_messages.jsonl")
    parser.add_argument("--memory", default="data/processed/supervisor_campaign_state.json")
    parser.add_argument("--output", type=Path, default=Path("data/processed/supervisor_campaign.csv"))
    args = parser.parse_args()

    results = run_supervisor_campaign(
        cycles=args.cycles,
        roots=args.roots or None,
        max_files=args.max_files,
        max_mb=args.max_mb,
        out_dir=args.out_dir,
        bus_path=args.bus,
        memory_path=args.memory,
    )
    rows: list[dict[str, Any]] = []
    for index, result in enumerate(results, start=1):
        decision = result.decision
        rows.append(
            {
                "cycle": index,
                "run_id": result.run_id,
                "status": result.status,
                "selected_path": decision.selected_path,
                "selected_kind": result.state.selected_kind,
                "family": _family(result),
                "sample_rows": decision.sample_rows,
                "window_minutes": decision.window_minutes,
                "max_mb": decision.max_mb,
                "parse_sec": _timing(result, "parse_sec"),
                "route_sec": _timing(result, "route_sec"),
                "detect_sec": _timing(result, "detect_sec"),
                "correlate_sec": _timing(result, "correlate_sec"),
                "elapsed_sec": result.elapsed_sec,
                "reasons": " | ".join(decision.reasons),
            }
        )
    write_csv(args.output, rows)
    write_table(TABLES / "table_supervisor_campaign.md", rows)
    print(f"Campagne superviseur ecrite: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
