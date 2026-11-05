"""Agent 4 -- BGL : localisation des familles d'anomalies dans le journal (diagnostic descriptif).

Famille = six premiers jetons du message, chiffres et hexadecimaux remplaces par '#'.
Sorties : effectif par famille et par tranche de 475 000 lignes ; composition des positifs du
test R0 (lignes 4 263 167 .. 4 283 166) ; premiere ligne d'apparition de chaque famille de test.
"""

from __future__ import annotations

import collections
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "Datasets" / "BGL" / "BGL.log"
OUT = ROOT / "revision_reports" / "agent_4" / "artifacts" / "bgl"
RUN_ID = "agent4_bgl_anomaly_family_map_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SIG = re.compile(r"0x[0-9a-fA-F]+|\d+")
TEST = (4263167, 4283166)
SLICE = 475000


def family(message: str) -> str:
    return " ".join(SIG.sub("#", message).split()[:6])


def main() -> None:
    total = collections.Counter()
    by_slice: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    first_line: dict[str, int] = {}
    test_pos = collections.Counter()
    h = hashlib.sha256()
    with RAW.open("rb") as fb:
        for chunk in iter(lambda: fb.read(1 << 20), b""):
            h.update(chunk)
    with RAW.open("r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if line.startswith("- "):
                continue
            parts = line.split(None, 9)
            if len(parts) < 10:
                continue
            fam = family(parts[9])
            total[fam] += 1
            by_slice[fam][str((i - 1) // SLICE)] += 1
            first_line.setdefault(fam, i)
            if TEST[0] <= i <= TEST[1]:
                test_pos[fam] += 1
    result = {
        "run_id": RUN_ID,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input": {"path": "data/raw/Datasets/BGL/BGL.log", "sha256": h.hexdigest()},
        "definition": "anomalie = premier jeton different de '-' ; famille = 6 premiers jetons normalises",
        "slice_lines": SLICE,
        "anomalous_lines_total": int(sum(total.values())),
        "top_families": [{"family": k, "count": v, "by_slice": dict(sorted(by_slice[k].items(), key=lambda x: int(x[0]))),
                          "first_line": first_line[k]} for k, v in total.most_common(20)],
        "test_R0_positive_families": [{"family": k, "count_in_test": v, "first_line_in_log": first_line[k],
                                       "count_before_test_start": int(total[k] - sum(
                                           c for s, c in by_slice[k].items() if int(s) * SLICE + 1 >= TEST[0]))
                                       if False else None}
                                      for k, v in test_pos.most_common()],
    }
    # nombre exact d'occurrences anterieures au test : second passage limite aux familles du test
    fams = set(test_pos)
    before = collections.Counter()
    with RAW.open("r", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f, 1):
            if i >= TEST[0]:
                break
            if line.startswith("- "):
                continue
            parts = line.split(None, 9)
            if len(parts) >= 10:
                fam = family(parts[9])
                if fam in fams:
                    before[fam] += 1
    for row in result["test_R0_positive_families"]:
        row["count_before_test_start"] = int(before[row["family"]])
    out = OUT / f"{RUN_ID}__result.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result["test_R0_positive_families"], ensure_ascii=False, indent=1))
    print(out)


if __name__ == "__main__":
    main()
