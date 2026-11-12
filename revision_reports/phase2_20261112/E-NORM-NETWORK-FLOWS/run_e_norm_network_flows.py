"""E-NORM-NETWORK-FLOWS : remplissage du schéma commun par les flux réseau, avec un adaptateur.

Applique ``normalizers.network_flow.normalize_flows`` aux 1 000 premières lignes de chaque
CSV de flux local (CICIDS2017 MachineLearningCVE, CSE-CIC-IDS2018), comme la campagne
multiformat d'origine, et mesure deux ensembles de sept champs :
- champs « journal », ceux de la campagne d'origine (scripts/run_multiformat_validation.py) ;
- champs « réseau » du schéma (timestamp_iso, src_ip, src_port, dst_ip, dst_port, proto, bytes_sent).

Protocole : revision_reports/phase2_20261112/E-NORM-NETWORK-FLOWS/PROTOCOLE.md.
Usage : python run_e_norm_network_flows.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src" / "logminer"))
from normalizers.network_flow import normalize_flows  # noqa: E402

EXPERIMENT = "E-NORM-NETWORK-FLOWS"
OUT = ROOT / "experiments" / "phase_revision_20261112" / EXPERIMENT
LIMIT = 1000
SOURCES = {
    "cicids2017": sorted((ROOT / "data/raw/Datasets/MachineLearningCSV/MachineLearningCVE").glob("*.csv")),
    "cse_cic_ids2018": sorted((ROOT / "data/raw/external/CSE-CIC-IDS2018").glob("*.csv")),
}
LOG_FIELDS = {"timestamp": "timestamp_iso", "source": "source", "host": "host", "family": "subtype",
              "category": "category", "severity": "severity", "message": "message"}
NETWORK_FIELDS = ("timestamp_iso", "src_ip", "src_port", "dst_ip", "dst_port", "proto", "bytes_sent")
PREDICTED = {  # nombre de champs renseignés à 100 %, fixé avant exécution (protocole § 4)
    "cicids2017": {"log": 1, "network": 2},
    "cse_cic_ids2018": {"log": 2, "network": 4},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(4 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rate(series: pd.Series) -> float:
    return float(series.astype(str).str.strip().ne("").mean())


def main() -> int:
    started = datetime.now(timezone.utc)
    rows, files = [], []
    for dataset, paths in SOURCES.items():
        if not paths:
            raise SystemExit(f"aucun fichier pour {dataset}")
        for path in paths:
            raw = pd.read_csv(path, dtype=str, keep_default_na=False, nrows=LIMIT, encoding_errors="ignore")
            labels = {str(v) for c in raw.columns if c.strip().lower() == "label" for v in raw[c].unique()}
            out = normalize_flows(raw, dataset=dataset, filepath=path.relative_to(ROOT).as_posix())
            leak = any(out[col].isin(labels).any() for col in out.columns if col not in ("dataset", "subtype"))
            rec = {"dataset": dataset, "file": path.name, "rows": len(out), "label_leak": leak}
            for name, col in LOG_FIELDS.items():
                rec[f"log_{name}"] = rate(out[col])
            for col in NETWORK_FIELDS:
                rec[f"net_{col}"] = rate(out[col])
            rec["log_full_fields"] = sum(rec[f"log_{n}"] == 1.0 for n in LOG_FIELDS)
            rec["net_full_fields"] = sum(rec[f"net_{c}"] == 1.0 for c in NETWORK_FIELDS)
            rows.append(rec)
            files.append(path)
    decision = {}
    for dataset in SOURCES:
        sub = [r for r in rows if r["dataset"] == dataset]
        ok = all(r["log_full_fields"] == PREDICTED[dataset]["log"] and r["net_full_fields"] == PREDICTED[dataset]["network"]
                 and not r["label_leak"] for r in sub)
        decision[dataset] = "conforme_a_la_prediction" if ok else "ecart_a_la_prediction"
    decision["conclusion"] = ("lacune_d_adaptateur_comblee" if all(v == "conforme_a_la_prediction" for v in decision.values())
                              else "a_examiner")
    OUT.mkdir(parents=True, exist_ok=True)
    runs = OUT / "fill_rates.csv"
    with runs.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    summary = OUT / "summary.json"
    summary.write_text(json.dumps({
        "experiment_id": EXPERIMENT, "started_at_utc": started.isoformat(),
        "completed_at_utc": datetime.now(timezone.utc).isoformat(), "limit_rows_per_file": LIMIT,
        "environment": {"python": platform.python_version(), "pandas": pd.__version__},
        "predicted_full_fields": PREDICTED, "decision": decision}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (OUT / "MANIFEST_SHA256.csv").open("w", encoding="utf-8", newline="") as h:
        w = csv.writer(h)
        w.writerow(["role", "path", "bytes", "sha256"])
        for role, p in ([("artifact", runs), ("artifact", summary), ("source", Path(__file__).resolve()),
                         ("source", ROOT / "src/logminer/normalizers/network_flow.py")]
                        + [("data", p) for p in files]):
            w.writerow([role, p.relative_to(ROOT).as_posix(), p.stat().st_size, sha256(p)])
    print("terminé :", summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
