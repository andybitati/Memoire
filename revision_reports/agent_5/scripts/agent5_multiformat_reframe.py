#!/usr/bin/env python3
"""Agent 5 - relecture du run multiformat_balanced_20260910T094422Z (sans ré-exécution).

Dérive des artefacts existants les comptes nécessaires pour présenter 7 001/7 001
comme un test d'intégration : part de la fixture Apache, complétude des sept champs
standard par source, et recherche d'un corpus Apache réel local.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
AGG = ROOT / "experiments/phase_dataset_strengthening/aggregated"
SUMMARY = AGG / "multiformat_balanced_summary.csv"
FIELDS = AGG / "multiformat_mandatory_field_completeness.csv"
SEARCHED = ["data/ (glob **/*{pache,ccess}*)", "dépôt complet (git ls-files --cached --others | grep -i apache|access.log|loghub)",
            "E:/Mémoire (glob)", "C:/Users/aoliv/Downloads (glob)",
            "E:/ récursif : interrompu par la limite de temps (expérience HDFS concurrente), résultat non conclusif"]


def main() -> int:
    run_id = "agent5_multiformat_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = ROOT / "revision_reports/agent_5/multiformat" / run_id
    out.mkdir(parents=True, exist_ok=True)
    s = pd.read_csv(SUMMARY)
    f = pd.read_csv(FIELDS)
    per_source = []
    for row in s.itertuples(index=False):
        sub = f[f["source_id"] == row.source_id]
        full = int((sub["completeness_rate"] >= 1.0).sum())
        empty = sub.loc[sub["n_present"] == 0, "field"].tolist()
        per_source.append({"source_id": row.source_id, "source_status": row.source_status, "read": int(row.read),
                           "normalized": int(row.normalized), "routed_family": row.routed_family,
                           "standard_fields_complete_7": f"{full}/7", "standard_fields_empty": empty})
    total_read = int(s["read"].sum())
    apache = s[s["source_id"] == "apache"].iloc[0]
    result = {
        "run_id": run_id, "status": "COMPLETED", "reference_run": str(s["run_id"].iloc[0]),
        "inputs": [SUMMARY.relative_to(ROOT).as_posix(), FIELDS.relative_to(ROOT).as_posix(),
                   "scripts/run_multiformat_validation.py (analyse_item : n_normalise = n_parse = nombre de lignes émises)"],
        "total_read": total_read, "total_normalized": int(s["normalized"].sum()),
        "real_sources_units": total_read - int(apache["read"]), "real_sources_count": int((s["source_id"] != "apache").sum()),
        "apache_fixture_units": int(apache["read"]), "apache_routed_family": apache["routed_family"],
        "definition_note": "« normalisé » compte les lignes émises par l'adaptateur ; il est égal à « parsé » par construction et ne garantit pas le remplissage du schéma commun.",
        "per_source": per_source,
        "real_apache_corpus_found_locally": False, "apache_search_scope": SEARCHED,
    }
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("run_id", "total_read", "real_sources_units", "apache_fixture_units")}, ensure_ascii=False))
    for p in per_source:
        print(p["source_id"], p["standard_fields_complete_7"], p["standard_fields_empty"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
