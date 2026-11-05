#!/usr/bin/env python3
"""Agent 5 - inventaire des copies de données et de leur provenance.

Calcul borné (expérience HDFS concurrente) : SHA-256 calculé seulement pour les
fichiers < 64 Mio ; au-delà, on reprend le hash de la matrice de traçabilité
lorsqu'il existe, sinon le fichier est marqué ``hash_non_calcule_io``.
Les archives ZIP sont comparées par liste d'entrées (nom + taille), sans lecture
complète. Aucune donnée n'est modifiée.
"""

from __future__ import annotations

import csv
import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TRACE = ROOT / "ARIEL_LOGMINER_MEMOIRE_FINAL/evidence/data_traceability/final_data_source_traceability.csv"
OUT_ROOT = ROOT / "revision_reports/agent_5/provenance"
LIMIT = 64 * 1024 * 1024
SCAN = [ROOT / "data/raw", ROOT / "data/samples"]
EXTRA = [
    "data/processed/robustness_scalability_inputs/apache_access.log",
    "data/processed/parallel_robustness_inputs/apache_access.log",
    "data/processed/final_experiments_2026/phase_5/samples/apache.log",
    "experiments/phase_dataset_strengthening/processed/multiformat_balanced_20260910T094422Z/samples/apache.log",
]
USED_IN = {
    "router_independent_sources.json": ROOT / "experiments/phase_dataset_strengthening/configs/router_independent_sources.json",
    "multiformat_balanced_protocol.json": ROOT / "experiments/phase_dataset_strengthening/configs/multiformat_balanced_protocol.json",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    run_id = "agent5_provenance_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = OUT_ROOT / run_id
    out.mkdir(parents=True, exist_ok=True)
    trace: dict[str, dict] = {}
    with TRACE.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            trace[row["local_file"].replace("\\", "/")] = row
    usage_text = {k: v.read_text(encoding="utf-8") for k, v in USED_IN.items()}
    files = [p for base in SCAN for p in base.rglob("*") if p.is_file()]
    files += [ROOT / p for p in EXTRA if (ROOT / p).exists()]
    rows = []
    for p in sorted(set(files)):
        rel = p.relative_to(ROOT).as_posix()
        size = p.stat().st_size
        tr = trace.get(rel)
        if size < LIMIT:
            digest, how = sha(p), "computed"
        elif tr and tr.get("local_sha256", "").strip():
            digest, how = tr["local_sha256"].strip(), "from_traceability_csv"
        else:
            digest, how = "", "hash_non_calcule_io"
        zip_sig = ""
        if p.suffix.lower() == ".zip":
            with zipfile.ZipFile(p) as z:
                zip_sig = hashlib.sha256(json.dumps(sorted((i.filename, i.file_size) for i in z.infolist())).encode()).hexdigest()
        rows.append({
            "path": rel, "size_bytes": size, "sha256": digest, "sha256_method": how, "zip_entry_signature": zip_sig,
            "traceability_status": tr["traceability_status"] if tr else "ABSENT_DE_LA_MATRICE",
            "used_in_router_config": rel in usage_text["router_independent_sources.json"],
            "used_in_multiformat_config": rel in usage_text["multiformat_balanced_protocol.json"],
        })
    by_hash: dict[str, list[str]] = {}
    by_zip: dict[str, list[str]] = {}
    for r in rows:
        if r["sha256"]:
            by_hash.setdefault(r["sha256"], []).append(r["path"])
        if r["zip_entry_signature"]:
            by_zip.setdefault(r["zip_entry_signature"], []).append(r["path"])
    for r in rows:
        dups = [x for x in by_hash.get(r["sha256"], []) if x != r["path"]] if r["sha256"] else []
        zdups = [x for x in by_zip.get(r["zip_entry_signature"], []) if x != r["path"]] if r["zip_entry_signature"] else []
        r["identical_copies_sha256"] = " | ".join(dups)
        r["same_zip_entry_list"] = " | ".join(zdups)
    fields = list(rows[0])
    with (out / "inventory.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    summary = {
        "run_id": run_id, "status": "COMPLETED", "traceability_matrix": TRACE.relative_to(ROOT).as_posix(),
        "n_files": len(rows),
        "n_absent_from_traceability_matrix": sum(r["traceability_status"] == "ABSENT_DE_LA_MATRICE" for r in rows),
        "n_hash_not_computed": sum(r["sha256_method"] == "hash_non_calcule_io" for r in rows),
        "duplicate_groups_sha256": [v for v in by_hash.values() if len(v) > 1],
        "duplicate_groups_zip_entries": [v for v in by_zip.values() if len(v) > 1],
        "absent_and_used_in_router_config": [r["path"] for r in rows if r["traceability_status"] == "ABSENT_DE_LA_MATRICE" and r["used_in_router_config"]],
        "inventory_csv": (out / "inventory.csv").relative_to(ROOT).as_posix(),
        "hash_size_limit_bytes": LIMIT,
    }
    (out / "result.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("run_id", "n_files", "n_absent_from_traceability_matrix", "n_hash_not_computed")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
