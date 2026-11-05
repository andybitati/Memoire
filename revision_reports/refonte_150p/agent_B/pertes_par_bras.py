"""Echecs finaux par experience, scenario, bras et nombre de coordinateurs (lecture seule des runs.csv)."""
import csv, collections
B = "experiments/phase_revision_20261105/"
for d in ["E-CNP-STATIC-ASSIGNMENT", "E-CNP-LEAST-LOADED", "E-H5-MEMORY-RELIABILITY"]:
    agg = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in csv.DictReader(open(B + d + "/runs.csv", encoding="utf-8")):
        a = agg[(r["scenario"], r["arm"], r["workers"])]
        a[0] += int(r["final_failures"]); a[1] += 1; a[2] += int(r["load"]); a[3] += int(r["final_failures"]) > 0
    print(d)
    for k, v in sorted(agg.items()):
        print("  ", k, "echecs_finaux=", v[0], "executions=", v[1], "taches=", v[2], "executions_avec_perte=", v[3])
