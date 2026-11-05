#!/usr/bin/env python3
"""Agent 5 - routeur open-set : familles inconnues supplémentaires et IC exacts.

* Politique GELÉE relue depuis
  experiments/phase_final_scientific_consolidation/configs/router_open_set_selected_policy.json
  (run final_router_open_set_20260911T000746Z). Aucune recalibration.
* Les 31 sources d'origine sont rejouées à partir de leurs artefacts neutres
  (router_independent_20260910T094257Z) ; les nouvelles sources sont lues avec
  les mêmes adaptateurs (scripts/run_router_independent_strengthening.py) ou,
  pour les formats texte inconnus, avec le pipeline du projet (run_pipeline).
* Étiquettes attendues figées dans sources_config.json AVANT l'exécution.
* Deux modes d'entrée :
    P = trame telle que produite par les adaptateurs du projet ;
    N = même trame, colonnes ``dataset``, ``subtype`` et ``filepath`` retirées
        (ablation d'une fuite possible : ces colonnes sont écrites par
        l'adaptateur choisi par l'expérimentateur, pas lues dans la source).
* IC de Clopper-Pearson à 95 % (scipy.stats.beta).
Sortie : revision_reports/agent_5/router_open_set/<run_id>/.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[3]
for d in (ROOT / "src", ROOT / "src" / "logminer" / "parsers", ROOT / "scripts"):
    sys.path.insert(0, str(d))

from logminer.agents.model_router import apply_open_set_rejection, route_dataframe  # noqa: E402
from logminer.pipeline import run_pipeline  # noqa: E402
import run_router_independent_strengthening as ris  # noqa: E402

POLICY_PATH = ROOT / "experiments/phase_final_scientific_consolidation/configs/router_open_set_selected_policy.json"
PREV_ROUTES = ROOT / "experiments/phase_dataset_strengthening/raw/router_independent_20260910T094257Z_routes.csv"
PREV_CONFIG = ROOT / "experiments/phase_dataset_strengthening/configs/router_independent_sources.json"
OUT_ROOT = ROOT / "revision_reports" / "agent_5" / "router_open_set"
SAMPLE_ROWS = 200
LEAK_COLUMNS = {"dataset", "subtype", "filepath"}

DS = "data/raw/Datasets"
# stratum : U = famille inconnue (aucun modèle du portefeuille entraîné sur ce schéma)
#           K = famille connue du portefeuille, source nouvelle
#           A = ambigu (exclu des taux principaux, rapporté à part)
# schema_group : sources partageant le même schéma (non indépendantes).
NEW_SOURCES = [
    # --- U : CSV locaux de Dataset_csv (provenance non établie, cf. inventaire) ---
    {"source_id": "u_authentication", "path": f"{DS}/Dataset_csv/Authentication_Logs_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_auth_method_status"},
    {"source_id": "u_cloud_based_services", "path": f"{DS}/Dataset_csv/Cloud-Based_Services_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_service_operation"},
    {"source_id": "u_netsec_appliances", "path": f"{DS}/Dataset_csv/Network_Security_Appliances_Logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_ip_eventtype_description"},
    {"source_id": "u_operating_system", "path": f"{DS}/Dataset_csv/Operating_System_Logs_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_host_event_details"},
    {"source_id": "u_proxy_server", "path": f"{DS}/Dataset_csv/Proxy_Server_Logs_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_proxy_url_status"},
    {"source_id": "u_security_events", "path": f"{DS}/Dataset_csv/security_events.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_eventtype_ip_description"},
    {"source_id": "u_server_logs", "path": f"{DS}/Dataset_csv/Server_Logs_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_server_message"},
    {"source_id": "u_syslog_data", "path": f"{DS}/Dataset_csv/Syslog_Data_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_syslog_facility_severity", "label_note": "étiquette discutable : syslog réseau tabulaire, schéma distinct de Linux_2k"},
    {"source_id": "u_throughput", "path": f"{DS}/Dataset_csv/Throughput.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_metrics_throughput"},
    {"source_id": "u_router_log", "path": f"{DS}/Dataset_csv/router_log_log.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_ip_ports_proto_logtype"},
    {"source_id": "u_switch_log", "path": f"{DS}/Dataset_csv/switch_log_log.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_ip_ports_proto_logtype"},
    {"source_id": "u_network_one_month", "path": f"{DS}/Dataset_csv/network_data_one_month.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_ip_proto_size_event"},
    {"source_id": "u_network_flow", "path": f"{DS}/Dataset_csv/Network_Flow_Data_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_ip_ports_proto_bytes"},
    {"source_id": "u_packet_captures", "path": f"{DS}/Dataset_csv/Packet_Captures_logs.csv", "adapter": "csv", "stratum": "U", "expected": "unknown", "schema_group": "csv_ip_size_proto"},
    # --- U : DARPA 1998 (MIT Lincoln Laboratory, échantillon public) ---
    {"source_id": "u_darpa_bsm_praudit", "path": f"{DS}/DARPA_eval_b/DARPA_eval_b/sample_data01.praudit/sample_data01.praudit", "adapter": "text_pipeline", "text_lines": 2000, "stratum": "U", "expected": "unknown", "schema_group": "solaris_bsm_praudit"},
    {"source_id": "u_darpa_bsm_list", "path": f"{DS}/DARPA_eval_b/DARPA_eval_b/bsm.list", "adapter": "text_pipeline", "text_lines": 200, "stratum": "U", "expected": "unknown", "schema_group": "darpa_session_list"},
    {"source_id": "u_darpa_tcpdump_list", "path": f"{DS}/DARPA_eval_b/DARPA_eval_b/tcpdump.list", "adapter": "text_pipeline", "text_lines": 200, "stratum": "U", "expected": "unknown", "schema_group": "darpa_session_list"},
    # --- K : familles connues, sources nouvelles ---
    {"source_id": "k_cicids2018_thu", "path": "data/raw/external/CSE-CIC-IDS2018/Thursday-15-02-2018_TrafficForML_CICFlowMeter.csv", "adapter": "csv", "stratum": "K", "expected": "network_cicids", "schema_group": "cicflowmeter_2018_names"},
    {"source_id": "k_cicids2018_fri", "path": "data/raw/external/CSE-CIC-IDS2018/Friday-16-02-2018_TrafficForML_CICFlowMeter.csv", "adapter": "csv", "stratum": "K", "expected": "network_cicids", "schema_group": "cicflowmeter_2018_names"},
    {"source_id": "k_cicddos_udplag", "path": f"{DS}/UNSWNB15/UDPLag_data_2_0_per.csv", "adapter": "csv", "stratum": "K", "expected": "network_cicids", "schema_group": "cicflowmeter_ddos_archive", "label_note": "dossier nommé UNSWNB15 mais contenu de type CIC-DDoS2019 ; provenance inconnue"},
    {"source_id": "k_unsw_train", "path": f"{DS}/UNSW_NB15_training-set.parquet", "adapter": "parquet", "stratum": "K", "expected": "network", "schema_group": "unsw_nb15_parquet"},
    {"source_id": "k_unsw_test", "path": f"{DS}/UNSW_NB15_testing-set.parquet", "adapter": "parquet", "stratum": "K", "expected": "network", "schema_group": "unsw_nb15_parquet"},
    {"source_id": "k_linux_auth_labeled", "path": f"{DS}/linux_auth_logs_labeled.csv", "adapter": "csv", "stratum": "K", "expected": "linux_auth", "schema_group": "linux_auth_csv"},
    {"source_id": "k_linux_2k_structured", "path": f"{DS}/Dataset_csv/Linux_2k.log_structured.csv", "adapter": "csv", "stratum": "K", "expected": "linux", "schema_group": "loghub_structured_csv", "label_note": "même contenu que Linux_2k.log, forme structurée Loghub"},
    {"source_id": "k_win_samples_app", "path": "data/samples/Application.evtx", "adapter": "windows_evtx", "stratum": "K", "expected": "windows", "schema_group": "windows_evtx"},
] + [
    {"source_id": f"k_wazuh_{name.split('.')[0].replace('-', '_').lower()}", "path": f"{DS}/{name}", "adapter": "csv", "stratum": "K", "expected": "wazuh", "schema_group": "wazuh_export_csv"}
    for name in ["03-04-January.csv", "04-06-January.csv", "06-07-January.csv", "21-25-December.csv", "25-26-December.csv", "26-27-December.csv",
                 "26-December.csv", "28-31-December.csv", "31-December-3-January.csv", "31-December.csv"]
] + [
    # --- A : ambigus (paquets convertis par le parseur pcap du projet) ---
    {"source_id": "a_outside_tcpdump_csv", "path": f"{DS}/Dataset_csv/outside_tcp_dump_part001.csv", "adapter": "csv", "stratum": "A", "expected": "network_or_unknown", "schema_group": "project_pcap_csv"},
    {"source_id": "a_darpa_sample_pcap_csv", "path": f"{DS}/Dataset_csv/sample_data01.csv", "adapter": "csv", "stratum": "A", "expected": "network_or_unknown", "schema_group": "project_pcap_csv"},
]


def cp(k: int, n: int, alpha: float = 0.05) -> list[float]:
    if n == 0:
        return [float("nan"), float("nan")]
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return [round(lo, 6), round(hi, 6)]


def text_pipeline_frame(item: dict, work: Path) -> pd.DataFrame:
    src = ROOT / item["path"]
    lines: list[str] = []
    with src.open("r", encoding="utf-8", errors="ignore") as h:
        for line in h:
            if line.strip():
                lines.append(line.rstrip("\r\n"))
            if len(lines) >= int(item.get("text_lines", 200)):
                break
    sample = work / f"{item['source_id']}{src.suffix or '.log'}"
    sample.write_text("\n".join(lines) + "\n", encoding="utf-8")
    outs = run_pipeline(str(sample), out_dir=str(work / "normalized"), out_name=f"{item['source_id']}.csv", sep=";")
    frame = pd.concat([pd.read_csv(o, sep=";", dtype=str, keep_default_na=False) for o in outs], ignore_index=True)
    return frame.head(SAMPLE_ROWS)


def load_new(item: dict, work: Path) -> pd.DataFrame:
    path = ROOT / item["path"]
    if item["adapter"] == "csv":
        frame = ris.read_csv_sample(path, SAMPLE_ROWS)
    elif item["adapter"] == "parquet":
        frame = pd.read_parquet(path).head(SAMPLE_ROWS).astype(str)
    elif item["adapter"] == "windows_evtx":
        frame = ris.read_windows(path, SAMPLE_ROWS)
    elif item["adapter"] == "text_pipeline":
        frame = text_pipeline_frame(item, work)
    else:
        raise ValueError(item["adapter"])
    return frame.drop(columns=[c for c in frame.columns if str(c).lower() == "filepath"], errors="ignore")


def decide(frame: pd.DataFrame, policy: dict) -> dict:
    route = route_dataframe(frame)
    d = apply_open_set_rejection(route, policy)
    return {"predicted": d["family"], "original_family": d["original_family"], "rejected": bool(d["rejected"]),
            "top_score": d["top_score"], "second_score": d["second_score"], "decision_margin": d["decision_margin"],
            "rejection_reasons": " | ".join(d["rejection_reasons"]), "reasons": " | ".join(map(str, route["reasons"]))}


def rates(rows: list[dict], label: str) -> dict:
    unk = [r for r in rows if r["stratum"] == "U"]
    kno = [r for r in rows if r["stratum"] == "K"]
    ur = sum(r["rejected"] for r in unk)
    kr = sum(r["rejected"] for r in kno)
    kacc = [r for r in kno if not r["rejected"]]
    kcorrect = sum(r["predicted"] == r["expected"] for r in kacc)
    ugroups: dict[str, list[bool]] = {}
    for r in unk:
        ugroups.setdefault(r["schema_group"], []).append(r["rejected"])
    kgroups: dict[str, list[bool]] = {}
    for r in kno:
        kgroups.setdefault(r["schema_group"], []).append(r["rejected"])
    ug_all = sum(all(v) for v in ugroups.values())
    kg_any = sum(any(v) for v in kgroups.values())
    return {
        "subset": label,
        "unknown_files_rejected": f"{ur}/{len(unk)}", "unknown_rejection_rate": ur / len(unk) if unk else None,
        "unknown_rejection_cp95": cp(ur, len(unk)),
        "unknown_schema_groups_all_rejected": f"{ug_all}/{len(ugroups)}", "unknown_schema_group_cp95": cp(ug_all, len(ugroups)),
        "known_files_falsely_rejected": f"{kr}/{len(kno)}", "false_rejection_rate": kr / len(kno) if kno else None,
        "false_rejection_cp95": cp(kr, len(kno)),
        "known_schema_groups_with_false_rejection": f"{kg_any}/{len(kgroups)}", "known_group_false_rejection_cp95": cp(kg_any, len(kgroups)),
        "known_accepted_correct": f"{kcorrect}/{len(kacc)}",
        "known_accepted_misrouted": len(kacc) - kcorrect,
    }


def main() -> int:
    run_id = "agent5_router_open_set_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = OUT_ROOT / run_id
    work = out / "work"
    work.mkdir(parents=True, exist_ok=True)
    policy_doc = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    policy = policy_doc["policy"]
    prev_cfg = {s["source_id"]: s for s in json.loads(PREV_CONFIG.read_text(encoding="utf-8"))["sources"]}
    prev = pd.read_csv(PREV_ROUTES)
    sources: list[dict] = []
    for item in prev.to_dict(orient="records"):
        s = prev_cfg[item["source_id"]]
        fam = s["true_family"]
        sources.append({"source_id": s["source_id"], "origin": "original_31", "path": s["path"], "neutral_artifact": item["neutral_artifact"],
                        "stratum": "U" if fam == "unknown_family" else "K", "expected": "unknown" if fam == "unknown_family" else fam,
                        "schema_group": ("csv_ip_ports_proto_logtype" if s["source_id"] in ("open_cloud_service", "open_virtualization")
                                         else "csv_dns_query" if s["source_id"] == "open_dns" else s["source_group"])})
    for item in NEW_SOURCES:
        sources.append({**item, "origin": "agent5_new"})
    (out / "sources_config.json").write_text(json.dumps({"run_id": run_id, "frozen_before_execution": True, "policy_source": str(POLICY_PATH.relative_to(ROOT)).replace("\\", "/"),
                                                         "policy": policy, "sample_rows": SAMPLE_ROWS, "leak_columns_removed_in_mode_N": sorted(LEAK_COLUMNS),
                                                         "sources": sources}, ensure_ascii=False, indent=2), encoding="utf-8")
    rows: list[dict] = []
    for s in sources:
        base = {k: s.get(k, "") for k in ("source_id", "origin", "path", "stratum", "expected", "schema_group", "label_note")}
        try:
            if s["origin"] == "original_31":
                # Lecture identique au run de référence (pd.read_csv par défaut).
                frame = pd.read_csv(ROOT / s["neutral_artifact"])
            else:
                frame = load_new(s, work)
            frame.columns = [str(c).strip().lstrip("﻿") for c in frame.columns]
            frame.to_csv(work / f"{s['source_id']}_P.csv", index=False, encoding="utf-8")
            for mode, fr in (("P", frame), ("N", frame.drop(columns=[c for c in frame.columns if c.lower() in LEAK_COLUMNS], errors="ignore"))):
                if fr.shape[1] == 0:
                    rows.append({**base, "mode": mode, "error": "empty_after_drop", "rejected": True, "predicted": "unknown"})
                    continue
                rows.append({**base, "mode": mode, "n_rows": len(fr), "n_cols": fr.shape[1], "error": "", **decide(fr, policy)})
        except Exception as exc:  # une source illisible est rapportée, jamais masquée
            for mode in ("P", "N"):
                rows.append({**base, "mode": mode, "error": f"{type(exc).__name__}: {exc}", "rejected": None, "predicted": ""})
    pd.DataFrame(rows).to_csv(out / "routes.csv", index=False, encoding="utf-8")
    ok = [r for r in rows if not r.get("error")]
    summary = {}
    for mode in ("P", "N"):
        m = [r for r in ok if r["mode"] == mode]
        summary[mode] = {
            "original_31": rates([r for r in m if r["origin"] == "original_31"], "original_31"),
            "agent5_new": rates([r for r in m if r["origin"] == "agent5_new"], "agent5_new"),
            "combined": rates(m, "combined"),
            "ambiguous_A": [{k: r[k] for k in ("source_id", "original_family", "predicted", "rejected", "top_score")} for r in m if r["stratum"] == "A"],
        }
    result = {
        "run_id": run_id, "status": "COMPLETED", "completed_at": datetime.now(timezone.utc).isoformat(),
        "reference_run": "final_router_open_set_20260911T000746Z", "policy": policy, "recalibrated": False,
        "protocol": {"modes": {"P": "trame produite par les adaptateurs du projet", "N": "P sans dataset/subtype/filepath"},
                     "strata": {"U": "inconnu", "K": "connu, source nouvelle ou d'origine", "A": "ambigu, hors taux"},
                     "ci": "Clopper-Pearson bilatéral 95 %", "unit": "fichier ; agrégat secondaire par groupe de schéma",
                     "coverage_metric": "retirée : 28/31 n'est qu'une conséquence de la composition 28 connus / 3 inconnus"},
        "errors": [{"source_id": r["source_id"], "mode": r["mode"], "error": r["error"]} for r in rows if r.get("error")],
        "summary": summary,
        "routes_csv": str((out / "routes.csv").relative_to(ROOT)).replace("\\", "/"),
    }
    (out / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"run_id": run_id, "errors": len(result["errors"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
