"""E-R1-LINEAGE : rattachement unité par unité entre source, schéma commun et résultat (exigence R1).

Partie A — émission dans le schéma commun : pour chacune des huit sources du protocole
multiformat, les adaptateurs de la campagne multiformat (inchangés) produisent les lignes
normalisées. Chaque ligne doit porter un localisateur (`filepath` + `lineno` ou `recno`)
qui désigne, sans ambiguïté, une unité brute du fichier d'origine dont le contenu
correspond à la ligne.

Partie B — chaîne de bout en bout avec reprise : chaque unité devient une tâche Contract
Net (chaîne multi-source, inchangée), exécutée par les agents avec magasin d'idempotence ;
une panne est injectée sur une tâche par source, après l'effet et avant le résultat.
Chaque résultat doit renvoyer à l'unité d'origine, relue indépendamment dans le fichier
source, avec un seul effet par unité, y compris pour les tâches reprises.

Partie C (descriptive, hors critère) : les anomalies candidates et les incidents
permettent-ils de remonter à l'unité par identifiant ?

Usage :
  python run_e_r1_lineage.py                         # exécution enregistrée
  python run_e_r1_lineage.py --trial --trial-dir D   # essai technique (20 unités/source), aucun taux affiché
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for extra in (ROOT / "scripts", ROOT / "src", ROOT / "src" / "logminer", ROOT / "src" / "logminer" / "parsers"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

import run_multiformat_validation as legacy  # noqa: E402
import run_multisource_cnp_e2e_strengthening as e2e  # noqa: E402
from logminer.agents.contract_net import ContractNetCoordinator  # noqa: E402
from logminer.agents.idempotency import SQLiteIdempotencyStore  # noqa: E402
from logminer.agents.intelligent_runtime import AgentTask, TaskResult  # noqa: E402

EXPERIMENT_ID = "E-R1-LINEAGE"
CONFIG = ROOT / "experiments" / "phase_dataset_strengthening" / "configs" / "multiformat_balanced_protocol.json"
OUT_DIR = ROOT / "experiments" / "phase_revision_20261112" / EXPERIMENT_ID
CRASH_UNIT = 10  # unité (1-based) dont l'exécution tombe en panne, par source ; 1 si la source en a moins
TRIAL_LIMIT = 20


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="surrogatepass")).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


# --------------------------------------------------------------------------------------
# Relecture indépendante des unités brutes dans le fichier d'origine
# --------------------------------------------------------------------------------------

def original_units(item: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    """Unités brutes relues dans le fichier d'origine, avec leur position physique."""
    path = ROOT / item["source"]
    adapter = item["adapter"]
    units: list[dict[str, Any]] = []
    if adapter == "pipeline_evtx_sample":
        from Evtx.Evtx import Evtx
        from Evtx.Views import evtx_record_xml_view

        with Evtx(str(path)) as log:
            for position, record in enumerate(log.records(), start=1):
                xml = evtx_record_xml_view(record)
                root = ET.fromstring(xml)
                ns = {"e": root.tag.split("}")[0].strip("{")} if root.tag.startswith("{") else {}
                rid = root.find(".//e:EventRecordID", ns) if ns else root.find(".//EventRecordID")
                eid = root.find(".//e:EventID", ns) if ns else root.find(".//EventID")
                units.append({"position": position, "raw": xml, "record_id": (rid.text or "").strip() if rid is not None else "",
                              "event_id": (eid.text or "").strip() if eid is not None else ""})
                if len(units) >= limit:
                    break
        return units
    if adapter == "pipeline_text_sample":
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for physical, line in enumerate(handle, start=1):
                value = line.rstrip("\r\n")
                if not value.strip():
                    continue
                units.append({"position": len(units) + 1, "physical_line": physical, "raw": value})
                if len(units) >= limit:
                    break
        return units
    header = path.open("r", encoding="utf-8-sig", errors="ignore").readline()
    separator = max((",", ";", "\t"), key=header.count)
    frame = pd.read_csv(path, sep=separator, dtype=str, keep_default_na=False, nrows=limit, encoding_errors="ignore")
    for position, row in enumerate(frame.to_dict(orient="records"), start=1):
        units.append({"position": position, "physical_line": position + 1, "raw": row})
    return units


def raw_fingerprint(raw: Any) -> str:
    if isinstance(raw, dict):
        return sha256_text(json.dumps({str(k).strip().lstrip("﻿"): v for k, v in raw.items()}, sort_keys=True, ensure_ascii=True))
    return sha256_text(str(raw))


# --------------------------------------------------------------------------------------
# Partie A
# --------------------------------------------------------------------------------------

def content_matches(item: dict[str, Any], row: dict[str, Any], unit: dict[str, Any]) -> bool:
    adapter = item["adapter"]
    if adapter == "pipeline_evtx_sample":
        return str(row.get("event", "")).strip() == unit["event_id"]
    if adapter == "pipeline_text_sample":
        message = str(row.get("message", "")).strip()
        return bool(message) and message in unit["raw"]
    if adapter == "wazuh_csv_normalizer":
        full_log = str(unit["raw"].get("_source.full_log", "")).strip()
        message = str(row.get("message", "")).strip()
        return bool(message) and (message == full_log or message in full_log or full_log in message)
    return False


def part_a(item: dict[str, Any], limit: int, phase_root: Path) -> dict[str, Any]:
    legacy.PHASE_ROOT = phase_root
    item = dict(item, limit=limit)
    raw_rows, normalized, _, error, _ = legacy.ADAPTERS[item["adapter"]](item)
    units = original_units(item, limit)
    n_units = len(units)
    sample_suffix = ".xml" if item["adapter"] == "pipeline_evtx_sample" else (ROOT / item["source"]).suffix
    sample_path = (phase_root / "samples" / f"{item['id']}{sample_suffix}").resolve()
    original_path = (ROOT / item["source"]).resolve()

    with_locator = 0
    resolved: list[int] = []
    content_ok = 0
    locator_points_to = Counter()
    for row in normalized:
        filepath = str(row.get("filepath", "")).strip()
        locator = str(row.get("recno" if item["adapter"] == "pipeline_evtx_sample" else "lineno", "")).strip()
        if not filepath or not locator:
            continue
        with_locator += 1
        target = Path(filepath).resolve()
        if target == original_path:
            locator_points_to["source_originale"] += 1
        elif target == sample_path:
            locator_points_to["extrait_de_campagne"] += 1
        else:
            locator_points_to["autre"] += 1
            continue
        try:
            position = int(float(locator))
        except ValueError:
            continue
        if not 1 <= position <= n_units:
            continue
        resolved.append(position)
        if content_matches(item, row, units[position - 1]):
            content_ok += 1
    counts = Counter(resolved)
    unique_resolved = sum(1 for _, c in counts.items() if c == 1)
    linked = min(content_ok, unique_resolved)
    return {
        "source_id": item["id"],
        "adapter": item["adapter"],
        "units": n_units,
        "normalized_rows": len(normalized),
        "adapter_error": error,
        "rows_with_locator": with_locator,
        "locator_target": dict(locator_points_to),
        "locators_resolved_in_range": len(resolved),
        "locators_unique": unique_resolved,
        "content_matches": content_ok,
        "linked_units": linked,
        "linked_rate": round(linked / n_units, 6) if n_units else 0.0,
        "pass": n_units > 0 and linked == n_units and len(normalized) == n_units,
    }


# --------------------------------------------------------------------------------------
# Partie B
# --------------------------------------------------------------------------------------

def part_b(config: dict[str, Any], limit: int, run_id: str, scratch: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    effects: Counter[str] = Counter()
    original_handler = e2e.real_handler

    def counting_handler(task: AgentTask, context: Any) -> dict[str, Any]:
        effects[str(task.payload["idempotency_key"])] += 1
        return original_handler(task, context)

    tasks: list[AgentTask] = []
    reference: dict[str, dict[str, Any]] = {}
    crash_task_ids: set[str] = set()
    for item in config["formats"]:
        units = e2e.load_raw_units(item, min(limit, int(item["limit"])))
        crash_at = CRASH_UNIT if len(units) >= CRASH_UNIT else 1
        for index, unit in enumerate(units, start=1):
            key = f"{run_id}:{item['id']}:{index}"
            task = AgentTask.create(
                f"pipeline.{item['id']}",
                {"end_to_end_run_id": run_id, "source_id": item["id"], "unit_index": index, "raw_unit": unit, "idempotency_key": key},
                priority=50,
            )
            tasks.append(task)
            reference[task.task_id] = {"source_id": item["id"], "unit_index": index, "key": key, "raw_sha": raw_fingerprint(unit)}
            if index == crash_at:
                crash_task_ids.add(task.task_id)

    store = SQLiteIdempotencyStore(scratch / "lineage_idempotency.sqlite3")
    agents = e2e.build_agents(run_id)
    for agent in agents:
        agent.idempotency_store = store
        agent.handlers = {task_type: counting_handler for task_type in agent.handlers}
    coordinator = ContractNetCoordinator(agents, run_id=run_id)
    crashed: set[str] = set()

    def crash_once(agent, original):
        def wrapped(task: AgentTask, score: float = 0.0, reasons: list[str] | None = None) -> TaskResult:
            result = original(task, score, reasons)
            if task.task_id in crash_task_ids and task.task_id not in crashed:
                crashed.add(task.task_id)
                return replace(result, status="error", error="worker_crash_before_result", output={})
            return result
        return wrapped

    for agent in agents:
        agent.execute_task = crash_once(agent, agent.execute_task)

    outcomes = [coordinator.negotiate(task) for task in tasks]

    # Relecture indépendante des fichiers d'origine
    reread: dict[str, list[dict[str, Any]]] = {item["id"]: original_units(item, min(limit, int(item["limit"]))) for item in config["formats"]}

    rows: list[dict[str, Any]] = []
    for task, outcome in zip(tasks, outcomes):
        ref = reference[task.task_id]
        output = outcome.result.output if outcome.result is not None else {}
        status = outcome.result.status if outcome.result is not None else "no_result"
        src = str(output.get("source_id", ""))
        idx = output.get("unit_index", "")
        resolved_sha = ""
        try:
            unit = reread[src][int(idx) - 1]
            resolved_sha = raw_fingerprint(unit["raw"])
        except (KeyError, ValueError, IndexError, TypeError):
            pass
        rows.append({
            "task_id": task.task_id,
            "source_id": ref["source_id"],
            "unit_index": ref["unit_index"],
            "status": status,
            "result_source_id": src,
            "result_unit_index": idx,
            "result_matches_task": src == ref["source_id"] and str(idx) == str(ref["unit_index"]),
            "resolves_to_original_unit": resolved_sha == ref["raw_sha"] and resolved_sha != "",
            "effects": effects[ref["key"]],
            "crash_injected": task.task_id in crash_task_ids,
            "reassignments": outcome.reassignments,
            "idempotency_replayed": bool(output.get("_idempotency_replayed", False)),
            "is_anomaly": int(output.get("is_anomaly", 0) or 0),
        })

    per_source: list[dict[str, Any]] = []
    for item in config["formats"]:
        subset = [r for r in rows if r["source_id"] == item["id"]]
        ok = [r for r in subset if r["status"] == "ok" and r["result_matches_task"] and r["resolves_to_original_unit"] and r["effects"] == 1]
        crash_rows = [r for r in subset if r["crash_injected"]]
        per_source.append({
            "source_id": item["id"],
            "units": len(subset),
            "results_ok": sum(r["status"] == "ok" for r in subset),
            "result_matches_task": sum(r["result_matches_task"] for r in subset),
            "resolves_to_original_unit": sum(r["resolves_to_original_unit"] for r in subset),
            "single_effect": sum(r["effects"] == 1 for r in subset),
            "crashes_injected": len(crash_rows),
            "crashes_recovered_with_lineage": sum(r["status"] == "ok" and r["result_matches_task"] and r["resolves_to_original_unit"] and r["effects"] == 1 for r in crash_rows),
            "crashes_replayed_from_store": sum(r["idempotency_replayed"] for r in crash_rows),
            "linked_units": len(ok),
            "pass": len(subset) > 0 and len(ok) == len(subset) and all(r["status"] == "ok" for r in crash_rows),
        })

    # Partie C (descriptive) : anomalies candidates et incidents
    candidate_rows = [{"task_id": r["task_id"], "source_id": r["source_id"]} for r in rows if r["is_anomaly"]]
    task_ids = Counter(r["task_id"] for r in rows)
    part_c = {
        "candidate_anomalies": len(candidate_rows),
        "candidate_anomalies_carry_unit_index": False,
        "candidate_anomalies_resolvable_by_task_id": sum(task_ids[c["task_id"]] == 1 for c in candidate_rows),
        "incident_columns_with_unit_identifier": [],
        "note": "Les lignes candidates de la chaîne portent task_id et source_id (pas unit_index) ; "
                "les incidents du corrélateur listent des noms d'événements, sans identifiant d'unité ni de tâche.",
    }
    return rows, per_source, part_c


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trial", action="store_true")
    parser.add_argument("--trial-dir", type=Path)
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.trial:
        if args.trial_dir is None:
            raise SystemExit("--trial-dir requis")
        out_dir, limit = args.trial_dir, TRIAL_LIMIT
    else:
        out_dir, limit = OUT_DIR, max(int(item["limit"]) for item in config["formats"])
        if (out_dir / "summary.json").exists():
            raise SystemExit("summary.json existe déjà : exécution enregistrée déjà faite")
    out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    run_id = f"e_r1_lineage_{started.strftime('%Y%m%dT%H%M%SZ')}"
    t0 = time.time()

    with tempfile.TemporaryDirectory(prefix="e_r1_lineage_") as tmp:
        scratch = Path(tmp)
        part_a_rows = [part_a(item, min(limit, int(item["limit"])), scratch / "phase") for item in config["formats"]]
        b_rows, b_sources, c_summary = part_b(config, limit, run_id, scratch)

    a_pass = {r["source_id"]: r["pass"] for r in part_a_rows}
    b_pass = {r["source_id"]: r["pass"] for r in b_sources}
    failing = sorted(s for s in a_pass if not (a_pass[s] and b_pass.get(s, False)))
    decision = "R1_rattachement_verifie" if not failing else "R1_rattachement_partiel"

    summary = {
        "experiment_id": EXPERIMENT_ID,
        "run_id": run_id,
        "started_at": started.isoformat(),
        "duration_s": round(time.time() - t0, 1),
        "config": rel(CONFIG),
        "config_sha256": sha256_file(CONFIG),
        "source_sha256": {item["id"]: sha256_file(ROOT / item["source"]) for item in config["formats"]},
        "crash_unit": CRASH_UNIT,
        "part_a": part_a_rows,
        "part_b": b_sources,
        "part_c": c_summary,
        "sources_failing": failing,
        "decision": decision,
        "programs_sha256": {
            rel(HERE / "run_e_r1_lineage.py"): sha256_file(HERE / "run_e_r1_lineage.py"),
            "scripts/run_multiformat_validation.py": sha256_file(ROOT / "scripts" / "run_multiformat_validation.py"),
            "scripts/run_multisource_cnp_e2e_strengthening.py": sha256_file(ROOT / "scripts" / "run_multisource_cnp_e2e_strengthening.py"),
            "src/logminer/agents/intelligent_runtime.py": sha256_file(ROOT / "src" / "logminer" / "agents" / "intelligent_runtime.py"),
            "src/logminer/agents/idempotency.py": sha256_file(ROOT / "src" / "logminer" / "agents" / "idempotency.py"),
        },
    }
    if args.trial:
        print(json.dumps({"trial": "ok", "tasks": len(b_rows), "sources": len(part_a_rows),
                          "crashes_injected": sum(r["crash_injected"] for r in b_rows)}))
        return 0

    with (out_dir / "part_b_units.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(b_rows[0]))
        writer.writeheader()
        writer.writerows(b_rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "MANIFEST_SHA256.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["path", "sha256", "bytes"])
        for path in sorted(p for p in out_dir.iterdir() if p.is_file() and p.name != "MANIFEST_SHA256.csv"):
            writer.writerow([rel(path), sha256_file(path), path.stat().st_size])
    print(json.dumps({"decision": decision, "sources_failing": failing}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
