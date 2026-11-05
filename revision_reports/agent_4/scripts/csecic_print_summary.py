"""Affiche les tableaux clefs du run csecic_shortcut_audit (lecture seule)."""
import glob
import json
import sys

path = sys.argv[1] if len(sys.argv) > 1 else sorted(glob.glob("revision_reports/agent_4/artifacts/csecic/agent4_csecic_shortcut_*__result.json"))[-1]
d = json.load(open(path, encoding="utf-8"))
print(d["run_id"])
print("== part1 (reglage publie, test equilibre)")
for r in d["part1_summary"]:
    print(f"{r['model']:38s} {r['feature_set']:14s} f1={r['f1_mean']:.6f} [{r['f1_min']:.6f};{r['f1_max']:.6f}] rec={r['recall_mean']:.4f} fpr={r['fpr_mean']:.4f}")
print("== importances")
for k, v in d["part1_top_importances"].items():
    print(k, [(x["feature"], round(x["importance"], 4)) for x in v[:6]])
print("== familles part1")
for r in d["part1_family_predicted_attack_rate"]:
    if r["feature_set"] in ("ALL", "NO_DST_PORT"):
        print(r)
print("== dst port pools", json.dumps(d["part1_dst_port_pools"], ensure_ascii=False))
print("== part2 audit", json.dumps(d["part2_audit"], ensure_ascii=False))
print("== part2 (prevalence observee)")
for r in d["part2_summary"]:
    print(f"{r['direction']:9s} {r['model']:24s} {r['feature_set']:14s} prev={r['prevalence_mean']:.4f} f1={r['f1_mean']:.6f} [{r['f1_min']:.6f};{r['f1_max']:.6f}] p={r['precision_mean']:.4f} rec={r['recall_mean']:.4f} fpr={r['fpr_mean']:.4f} mcc={r['mcc_mean']:.4f}" + (f" prauc={r['pr_auc_mean']:.4f}" if r["pr_auc_mean"] is not None else ""))
print("== familles part2 (15_to_16)")
for r in d["part2_family_predicted_attack_rate"]:
    if r["direction"] in ("15_to_16", "16_to_15"):
        print(r)
print("== ports part2", json.dumps(d["part2_dst_port_by_family_sample"], ensure_ascii=False))
