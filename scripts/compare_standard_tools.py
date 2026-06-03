"""Comparaison prudente avec outils standards de supervision securite.

Ce script ne pretend pas executer fail2ban, OSSEC ou Wazuh en production.
Il produit trois niveaux de comparaison scientifiquement defendables:

1. Baseline experimentale "fail2ban-like" sur Linux/auth labellise.
2. Analyse d'exports Wazuh existants et recouvrement avec anomalies Logminer.
3. Matrice fonctionnelle Logminer / fail2ban / OSSEC / Wazuh.

Les sorties sont destinees au memoire et aux articles.
"""

from __future__ import annotations

import csv
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Datasets"
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "docs" / "memoire" / "tables"
FIGURES = ROOT / "docs" / "memoire" / "figures"
METHOD = ROOT / "docs" / "memoire" / "comparaison_scientifique_outils_standards.md"


def read_csv_limited(path: Path, sep: str = ",", limit: int | None = None) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8-sig", newline="", errors="ignore") as handle:
        reader = csv.DictReader(handle, delimiter=sep)
        for row in reader:
            rows.append(row)
            if limit is not None and len(rows) >= limit:
                break
    return rows


def write_csv(path: Path, rows: list[dict[str, object]], headers: list[str], sep: str = ";") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, delimiter=sep)
        writer.writeheader()
        writer.writerows(rows)


def write_md_table(path: Path, title: str, headers: list[str], rows: list[list[object]]) -> None:
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def as_int(value: object, default: int = 0) -> int:
    try:
        return int(float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return default


def is_positive_label(row: dict[str, str]) -> bool:
    label = str(row.get("anomaly_label") or row.get("label") or "").strip().lower()
    return label not in {"", "0", "normal", "benign", "false"}


def fail2ban_like(row: dict[str, str], attempt_threshold: int = 6) -> bool:
    status = str(row.get("status", "")).lower()
    username = str(row.get("username", "")).lower()
    service = str(row.get("service", "")).lower()
    attempts = as_int(row.get("attempts"))
    risky_users = {"root", "admin", "administrator", "www-data", "oracle", "postgres"}
    risky_services = {"ssh", "sshd", "sudo", "su"}
    return "fail" in status and (attempts >= attempt_threshold or username in risky_users or service in risky_services)


def metrics(rows: list[dict[str, str]]) -> dict[str, object]:
    tp = fp = fn = tn = 0
    for row in rows:
        predicted = fail2ban_like(row)
        actual = is_positive_label(row)
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / max(tp + fp, 1)
    recall = tp / max(tp + fn, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-12)
    accuracy = (tp + tn) / max(tp + fp + fn + tn, 1)
    fpr = fp / max(fp + tn, 1)
    return {
        "dataset": "linux_auth_logs_labeled",
        "baseline": "fail2ban_like_rules",
        "rows": len(rows),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": f"{precision:.6f}",
        "recall": f"{recall:.6f}",
        "f1": f"{f1:.6f}",
        "accuracy": f"{accuracy:.6f}",
        "fpr": f"{fpr:.6f}",
        "note": "Baseline controlee inspiree de fail2ban; ce n'est pas une execution de fail2ban.",
    }


def wazuh_overlap(limit: int | None = None) -> tuple[list[dict[str, object]], list[list[object]]]:
    path = PROCESSED / "wazuh_months_anomalies.csv"
    rows = read_csv_limited(path, sep=";", limit=limit)
    grouped: dict[tuple[str, str, str], dict[str, int]] = defaultdict(lambda: {"events": 0, "logminer_anomalies": 0})
    level_counter: Counter[str] = Counter()
    anomaly_level_counter: Counter[str] = Counter()

    for row in rows:
        level = str(row.get("wazuh_rule_level") or row.get("severity") or "unknown")
        decoder = str(row.get("wazuh_decoder") or row.get("source") or "unknown")
        category = str(row.get("category") or row.get("wazuh_groups") or "unknown")
        is_anomaly = str(row.get("is_anomaly", "")).strip() == "1"
        key = (level, decoder, category)
        grouped[key]["events"] += 1
        level_counter[level] += 1
        if is_anomaly:
            grouped[key]["logminer_anomalies"] += 1
            anomaly_level_counter[level] += 1

    rows_out: list[dict[str, object]] = []
    for (level, decoder, category), values in sorted(grouped.items(), key=lambda item: item[1]["events"], reverse=True)[:30]:
        events = values["events"]
        anomalies = values["logminer_anomalies"]
        rows_out.append(
            {
                "wazuh_rule_level": level,
                "wazuh_decoder": decoder,
                "category": category,
                "events": events,
                "logminer_anomalies": anomalies,
                "overlap_rate": f"{anomalies / max(events, 1):.6f}",
            }
        )

    summary = [
        ["Evenements Wazuh analyses", len(rows)],
        ["Anomalies Logminer dans export Wazuh", sum(anomaly_level_counter.values())],
        ["Niveaux Wazuh distincts", len(level_counter)],
        ["Groupes niveau/decoder/categorie", len(grouped)],
        ["Limite de lecture", limit or "complete"],
    ]
    return rows_out, summary


def svg_wazuh_overlap(path: Path, rows: list[dict[str, object]]) -> None:
    width = 980
    top = 84
    left = 260
    right = 80
    bar_h = 26
    gap = 12
    rows = rows[:12]
    height = top + len(rows) * (bar_h + gap) + 58
    max_events = max([as_int(row["events"]) for row in rows] + [1])
    plot_w = width - left - right
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172026}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#5b6770}.label{font-size:12px}.small{font-size:11px;fill:#5b6770}</style>",
        '<text x="36" y="36" class="title">Recouvrement Wazuh / Logminer</text>',
        '<text x="36" y="58" class="sub">Groupes Wazuh les plus frequents et part marquee anomalie par Logminer</text>',
    ]
    for index, row in enumerate(rows):
        y = top + index * (bar_h + gap)
        events = as_int(row["events"])
        anomalies = as_int(row["logminer_anomalies"])
        event_w = plot_w * events / max_events
        anomaly_w = plot_w * anomalies / max_events
        label = f"L{row['wazuh_rule_level']} / {row['wazuh_decoder']}"
        parts.append(f'<text x="{left - 12}" y="{y + 18}" text-anchor="end" class="label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{event_w:.1f}" height="{bar_h}" rx="3" fill="#8a96a3"/>')
        parts.append(f'<rect x="{left}" y="{y}" width="{anomaly_w:.1f}" height="{bar_h}" rx="3" fill="#c23b38"/>')
        parts.append(f'<text x="{left + event_w + 8:.1f}" y="{y + 18}" class="small">{events} evt / {anomalies} anomalies</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def write_method_note() -> None:
    METHOD.write_text(
        """# Comparaison Scientifique Avec Outils Standards

Cette comparaison est volontairement prudente. Elle ne pretend pas que
fail2ban, OSSEC et Wazuh ont tous ete executes dans une meme infrastructure de
production. Trois niveaux sont separes:

1. **Baseline experimentale inspiree de fail2ban**: une regle locale detecte
   des echecs d'authentification repetes ou a risque sur un dataset Linux/auth
   labellise. Elle sert de baseline rule-based, pas d'execution officielle de
   fail2ban.
2. **Analyse d'exports Wazuh**: les fichiers Wazuh deja presents dans le corpus
   sont compares aux anomalies candidates produites par Logminer. Cette partie
   est experimentale sur donnees Wazuh exportees.
3. **Comparaison fonctionnelle OSSEC/fail2ban/Wazuh**: les outils standards
   sont utilises comme references de capacites, de maturite et de positionnement.

Formulation recommandee pour article:

> To avoid overstating the comparison, fail2ban and OSSEC are used as
> functional references, while a lightweight rule-based baseline inspired by
> fail2ban is implemented for controlled authentication scenarios. Wazuh is
> evaluated through exported alerts/logs available in the experimental corpus.

Limites:

- La baseline fail2ban-like ne remplace pas une execution reelle de fail2ban.
- OSSEC n'est pas execute directement; il sert de reference fonctionnelle.
- Les anomalies non supervisees de Logminer sont des candidates, pas des
  intrusions confirmees.
- Les comparaisons de F1 ne doivent etre faites que sur les datasets labelises.
""",
        encoding="utf-8",
    )


def main() -> int:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    linux_path = RAW / "linux_auth_logs_labeled.csv"
    linux_rows = read_csv_limited(linux_path, limit=200_000)
    baseline = metrics(linux_rows)
    write_csv(
        PROCESSED / "standard_tools_fail2ban_like_baseline.csv",
        [baseline],
        ["dataset", "baseline", "rows", "tp", "fp", "fn", "tn", "precision", "recall", "f1", "accuracy", "fpr", "note"],
    )
    write_md_table(
        TABLES / "table_fail2ban_like_baseline.md",
        "Baseline Rule-Based Inspiree De fail2ban",
        ["Dataset", "Baseline", "Lignes", "Precision", "Recall", "F1", "FP", "FN", "Note"],
        [[baseline["dataset"], baseline["baseline"], baseline["rows"], baseline["precision"], baseline["recall"], baseline["f1"], baseline["fp"], baseline["fn"], baseline["note"]]],
    )

    wazuh_rows, summary = wazuh_overlap()
    write_csv(
        PROCESSED / "standard_tools_wazuh_logminer_overlap.csv",
        wazuh_rows,
        ["wazuh_rule_level", "wazuh_decoder", "category", "events", "logminer_anomalies", "overlap_rate"],
    )
    write_md_table(
        TABLES / "table_wazuh_logminer_overlap.md",
        "Recouvrement Wazuh Et Logminer",
        ["Niveau Wazuh", "Decoder", "Categorie", "Evenements", "Anomalies Logminer", "Taux recouvrement"],
        [[row["wazuh_rule_level"], row["wazuh_decoder"], row["category"], row["events"], row["logminer_anomalies"], row["overlap_rate"]] for row in wazuh_rows],
    )
    write_md_table(
        TABLES / "table_wazuh_logminer_summary.md",
        "Synthese Wazuh / Logminer",
        ["Indicateur", "Valeur"],
        summary,
    )
    svg_wazuh_overlap(FIGURES / "fig_wazuh_logminer_overlap.svg", wazuh_rows)
    write_method_note()

    print("Comparaison standards produite.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
