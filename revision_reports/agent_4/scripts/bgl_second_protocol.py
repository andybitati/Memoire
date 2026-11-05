"""Agent 4 -- BGL : protocoles complementaires contenant des anomalies a template connu.

Protocole de reference (R0) : reproduit a l'identique le run ds_bgl_known_unknown_20260910T082706Z
(train 49 999 evenements, Drain3 ajuste sur train seul, seuil Histogram sur validation).

Protocole B (taille/diversite de l'entrainement) : memes plages validation et test que R0, mais
l'entrainement est forme de K blocs contigus de 10 000 lignes repartis uniformement dans la partie
du journal anterieure a la validation (lignes 1 .. 3 313 573). Selection sans label. Drain3 est
ajuste sur tous les messages train (sans label, comme R0) ; les statistiques Histogram restent
calculees sur les seuls evenements train etiquetes normaux (comme R0). K in {5, 10, 20}.

Protocole C (adaptation non supervisee du parseur avant calibration) : train R0 ; Drain3 est
ajuste sur les messages train puis validation, sans label, puis gele avant le test. Les
statistiques Histogram restent celles de R0 (train normal).

Pour chaque protocole : F1, matrice de confusion, seuil choisi sur validation, couverture du
parseur (part connue/inconnue parmi positifs et negatifs), baselines UnknownTemplate et
SeverityNovelty (severite absente des evenements train normaux), et decomposition de la decision
Histogram. Aucune information du test n'est utilisee pour le seuil.
"""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from drain3 import TemplateMiner
from drain3.file_persistence import FilePersistence

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import run_strict_sequence_experiments as rs  # noqa: E402

OUT = ROOT / "revision_reports" / "agent_4" / "artifacts" / "bgl"
OUT.mkdir(parents=True, exist_ok=True)
RAW = ROOT / "data" / "raw" / "Datasets" / "BGL" / "BGL.log"
PREP = ROOT / "data" / "processed" / "final_experiments_2026" / "phase_3" / "prepared" / "bgl_preparation.json"
TOTAL = 4747963
BLOCK = 10000


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def train_blocks(k: int, upper: int, lower: int = 1) -> list[tuple[int, int]]:
    # k blocs de BLOCK lignes, centres equidistants dans [lower, upper]
    centres = np.linspace(lower - 1 + BLOCK, upper - BLOCK, k)
    return [(int(c) - BLOCK // 2, int(c) - BLOCK // 2 + BLOCK - 1) for c in centres]


def read_ranges(ranges: dict[str, list[tuple[int, int]]]) -> dict[str, pd.DataFrame]:
    flat = sorted((s, e, name) for name, rr in ranges.items() for s, e in rr)
    rows: dict[str, list[dict]] = {name: [] for name in ranges}
    max_line = max(e for s, e, _ in flat)
    idx = 0
    with RAW.open("r", encoding="utf-8", errors="replace") as handle:
        for lineno, line in enumerate(handle, start=1):
            if lineno > max_line:
                break
            while idx < len(flat) and lineno > flat[idx][1]:
                idx += 1
            if idx >= len(flat):
                break
            hits = [name for s, e, name in flat[idx:idx + 8] if s <= lineno <= e]
            if not hits:
                continue
            row = rs.parse_bgl(line, lineno)
            if row is not None:
                for name in hits:
                    rows[name].append(row)
    return {name: pd.DataFrame(v) for name, v in rows.items()}


def fit_drain(messages: list[pd.Series], state_path: Path) -> tuple[TemplateMiner, str, int]:
    if state_path.exists():
        state_path.unlink()
    miner = TemplateMiner(config=rs.drain_config())
    for series in messages:
        for message in series.fillna("").astype(str):
            miner.add_log_message(message)
    miner.persistence_handler = FilePersistence(str(state_path))
    miner.save_state("fit_complete")
    frozen = TemplateMiner(persistence_handler=FilePersistence(str(state_path)), config=rs.drain_config())
    return frozen, sha256(state_path), len(frozen.drain.clusters)


def group_metrics(y: np.ndarray, pred: np.ndarray, scores: np.ndarray | None, mask: np.ndarray) -> dict:
    yt, pr = y[mask], pred[mask]
    tp = int(np.sum((yt == 1) & (pr == 1))); fp = int(np.sum((yt == 0) & (pr == 1)))
    fn = int(np.sum((yt == 1) & (pr == 0))); tn = int(np.sum((yt == 0) & (pr == 0)))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"n": int(mask.sum()), "positives": int(yt.sum()), "tp": tp, "fp": fp, "tn": tn, "fn": fn,
            "precision": prec, "recall": rec, "f1": f1,
            "fpr": fp / (fp + tn) if fp + tn else 0.0}


def evaluate(name: str, frames: dict[str, pd.DataFrame], drain_fit_parts: list[str], description: str) -> dict:
    t0 = time.perf_counter()
    state_path = OUT / f"{RUN_ID}__{name}_drain3_state.bin"
    miner, state_sha, clusters = fit_drain([frames[p]["message"] for p in drain_fit_parts], state_path)
    ids = {}
    for split in ("train", "validation", "test"):
        ids[split], _ = rs.assign_templates(miner, frames[split])
    hist = rs.histogram_scores(frames, ids)
    y = {s: frames[s]["label"].astype(int).to_numpy() for s in ("train", "validation", "test")}
    threshold, val_metrics = rs.select_threshold(y["validation"], hist["validation"])
    test_metrics = rs.prediction_metrics(y["test"], hist["test"], threshold)

    normal = y["train"] == 0
    normal_count = int(normal.sum())
    normal_sev = set(frames["train"].loc[normal, "severity"].astype(str))
    normal_src = set(frames["train"].loc[normal, "source"].astype(str))
    normal_tpl = set(ids["train"][normal].tolist())
    te = frames["test"]
    unknown = ids["test"] == 0
    known = ~unknown
    hist_pred = (hist["test"] >= threshold).astype(int)
    unk_pred = unknown.astype(int)
    sev_novel = (~te["severity"].astype(str).isin(normal_sev)).to_numpy()
    sev_pred = sev_novel.astype(int)
    tpl_absent_normal = ~np.isin(ids["test"], list(normal_tpl))
    src_absent_normal = (~te["source"].astype(str).isin(normal_src)).to_numpy()

    all_mask = np.ones(len(te), dtype=bool)
    groups = {"ALL": all_mask, "KNOWN_TEMPLATE": known, "UNKNOWN_TEMPLATE": unknown}
    rows = []
    for model, pred in (("Histogram", hist_pred), ("UnknownTemplateBaseline", unk_pred),
                        ("SeverityNoveltyBaseline", sev_pred)):
        for g, m in groups.items():
            if m.any():
                rows.append({"run_id": RUN_ID, "protocol": name, "model": model, "group": g,
                             **group_metrics(y["test"], pred, None, m)})
    pos = y["test"] == 1
    coverage = {
        "test_events": int(len(te)),
        "test_positives": int(pos.sum()),
        "unknown_template_rate_all": float(unknown.mean()),
        "unknown_template_rate_validation": float(np.mean(ids["validation"] == 0)),
        "unknown_rate_among_positives": float(unknown[pos].mean()) if pos.any() else None,
        "unknown_rate_among_negatives": float(unknown[~pos].mean()),
        "positives_known_template": int(np.sum(known & pos)),
        "positives_unknown_template": int(np.sum(unknown & pos)),
        "negatives_known_template": int(np.sum(known & ~pos)),
        "negatives_unknown_template": int(np.sum(unknown & ~pos)),
        "drain3_clusters": clusters,
        "test_distinct_templates_known": int(len(set(ids["test"][known].tolist()))),
    }
    # decomposition de la decision Histogram : score = moyenne de trois -log(p) (template, source, severite)
    max_score = math.log(max(normal_count, 1))
    decomposition = {
        "train_normal_events": normal_count,
        "train_positive_events": int((~normal).sum()),
        "train_normal_severities": sorted(normal_sev),
        "max_possible_histogram_score_log_n_normal": max_score,
        "threshold_equals_max_possible_score": bool(abs(threshold - max_score) < 1e-9),
        "hist_pred_equals_severity_novelty": bool(np.array_equal(hist_pred, sev_pred)),
        "hist_pred_equals_sev_and_src_and_tpl_absent": bool(np.array_equal(
            hist_pred, (sev_novel & src_absent_normal & tpl_absent_normal).astype(int))),
        "test_severity_by_label": {f"{k[0]}|{k[1]}": int(v) for k, v in
                                    te.groupby(["severity", "label"]).size().items()},
    }
    if pos.any() and len(np.unique(y["test"])) > 1:
        from sklearn.metrics import average_precision_score
        test_metrics["pr_auc_hist"] = float(average_precision_score(y["test"], hist["test"]))
    return {
        "protocol": name, "description": description,
        "drain3_fit_partitions": drain_fit_parts, "drain3_state_sha256": state_sha,
        "drain3_state_path": str(state_path.relative_to(ROOT)).replace("\\", "/"),
        "split_rows": {s: int(len(frames[s])) for s in frames},
        "split_positives": {s: int(frames[s]["label"].sum()) for s in frames},
        "threshold": threshold, "threshold_selected_on": "validation_only",
        "validation_metrics": val_metrics, "test_metrics_histogram": test_metrics,
        "coverage": coverage, "histogram_decision_decomposition": decomposition,
        "group_rows": rows, "elapsed_sec": time.perf_counter() - t0,
    }


RUN_ID = "agent4_bgl_second_protocol_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def main() -> None:
    prep = json.loads(PREP.read_text(encoding="utf-8"))
    r = prep["source_ranges_one_based_inclusive"]
    val_rng, test_rng, r0_train = tuple(r["validation"]), tuple(r["test"]), tuple(r["train"])
    upper = val_rng[0] - 1
    ks = (5, 10, 20)
    ranges = {"train_R0": [r0_train], "validation": [val_rng], "test": [test_rng]}
    for k in ks:
        ranges[f"train_B{k}"] = train_blocks(k, upper)
    # Protocole D : decoupage chronologique 60/20/20 du journal complet, blocs repartis dans chaque segment
    d60, d80 = int(TOTAL * 0.6), int(TOTAL * 0.8)
    ranges["train_D"] = train_blocks(20, d60, 1)
    ranges["validation_D"] = train_blocks(10, d80, d60 + 1)
    ranges["test_D"] = train_blocks(10, TOTAL, d80 + 1)
    # Protocole E : horizon court ; test R0 inchange, validation = 20 000 lignes precedant le test,
    # train = 20 blocs de 10 000 lignes entre la ligne 3 800 001 et le debut de cette validation
    e_val = (test_rng[0] - 20000, test_rng[0] - 1)
    ranges["validation_E"] = [e_val]
    ranges["train_E"] = train_blocks(20, e_val[0] - 1, 3800001)
    t0 = time.perf_counter()
    frames_all = read_ranges(ranges)
    read_sec = time.perf_counter() - t0
    base = {"validation": frames_all["validation"], "test": frames_all["test"]}
    results = []
    results.append(evaluate("R0_reproduction", {"train": frames_all["train_R0"], **base}, ["train"],
                            "Reproduction du protocole publie (train lignes %d-%d)." % r0_train))
    for k in ks:
        results.append(evaluate(f"B{k}_train_{k}x{BLOCK}_lines", {"train": frames_all[f"train_B{k}"], **base}, ["train"],
                                f"Train = {k} blocs de {BLOCK} lignes repartis uniformement sur lignes 1..{upper}."))
    results.append(evaluate("C_drain3_adapted_on_unlabelled_validation", {"train": frames_all["train_R0"], **base},
                            ["train", "validation"],
                            "Train R0 ; Drain3 ajuste sans label sur train+validation, gele avant test."))
    results.append(evaluate("D_chrono_60_20_20_multiblock",
                            {"train": frames_all["train_D"], "validation": frames_all["validation_D"],
                             "test": frames_all["test_D"]}, ["train"],
                            "Decoupage chronologique 60/20/20 du journal ; train 20 blocs, validation 10 blocs, test 10 blocs de %d lignes, repartis uniformement dans chaque segment." % BLOCK))
    results.append(evaluate("E_short_horizon_train_before_test",
                            {"train": frames_all["train_E"], "validation": frames_all["validation_E"],
                             "test": frames_all["test"]}, ["train"],
                            "Test R0 ; validation = 20 000 lignes precedant le test ; train = 20 blocs de %d lignes entre 3 800 001 et le debut de la validation." % BLOCK))
    all_rows = [row for res in results for row in res["group_rows"]]
    csv_path = OUT / f"{RUN_ID}__group_metrics.csv"
    pd.DataFrame(all_rows).to_csv(csv_path, index=False, encoding="utf-8")
    summary = {
        "run_id": RUN_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "reference_run": "ds_bgl_known_unknown_20260910T082706Z",
        "inputs": {"raw_log": "data/raw/Datasets/BGL/BGL.log", "raw_log_sha256": sha256(RAW),
                   "expected_raw_sha256_from_preparation": prep["raw_sha256"],
                   "preparation_json": "data/processed/final_experiments_2026/phase_3/prepared/bgl_preparation.json"},
        "ranges_one_based_inclusive": {k: [list(x) for x in v] for k, v in ranges.items()},
        "observation_unit": "raw log event (une ligne BGL), pas une fenetre",
        "label_rule": "premier token '-' = normal, sinon anomalie (rs.parse_bgl)",
        "drain3_parameters": {"sim_th": 0.4, "depth": 4, "max_children": 100, "parametrize_numeric_tokens": True},
        "histogram_definition": "score = moyenne de -log(max(count,1)/N_normal_train) sur (template, source, severite) ; scripts/run_strict_sequence_experiments.py::histogram_scores",
        "threshold_rule": "max F1 sur validation, puis min FPR, max MCC, seuil le plus haut (rs.select_threshold)",
        "read_sec": read_sec,
        "results": results,
        "artifacts": [str(csv_path.relative_to(ROOT)).replace("\\", "/")],
    }
    out_json = OUT / f"{RUN_ID}__result.json"
    out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2, default=float), encoding="utf-8")
    for res in results:
        m = res["test_metrics_histogram"]; c = res["coverage"]
        print(res["protocol"], "F1=%.6f" % m["f1"], "tp", m["tp"], "fp", m["fp"], "fn", m["fn"], "tn", m["tn"],
              "unk_pos=%.4f" % (c["unknown_rate_among_positives"] or -1), "pos_known", c["positives_known_template"],
              "eq_sev", res["histogram_decision_decomposition"]["hist_pred_equals_severity_novelty"])
    print(out_json)


if __name__ == "__main__":
    main()
