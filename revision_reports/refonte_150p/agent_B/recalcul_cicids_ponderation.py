"""Recalcul, sans nouvelle experience, des F1 micro et sans Infiltration a partir des matrices de confusion par graine."""
import pandas as pd
d = pd.read_csv("data/processed/cicids_model_candidates_metrics.csv")
for m, g in d.groupby("model"):
    tp, fp, fn = g.tp.sum(), g.fp.sum(), g.fn.sum()
    print(m, "microF1=%.4f" % (2 * tp / (2 * tp + fp + fn)), "macroF1=%.4f" % g.f1.mean(),
          "F1_sans_Infiltration=%.4f" % g[~g.heldout_file.str.contains("Infil")].f1.mean())
g = d[d.model == "LogisticRegression"]
pos, neg = g.tp + g.fn, g.fp + g.tn
ap = 2 * pos / (2 * pos + neg)
print("prevalence_test", (pos / (pos + neg)).round(4).tolist())
print("tout_positif_par_scenario", ap.round(4).tolist(), "macro=%.4f" % ap.mean(),
      "micro=%.4f" % (2 * pos.sum() / (2 * pos.sum() + neg.sum())),
      "sans_Infiltration=%.4f" % ap[~g.heldout_file.str.contains("Infil")].mean())
print("pr_auc_LR", g.pr_auc.round(4).tolist())
