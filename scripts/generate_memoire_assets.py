"""Genere les figures et tableaux exploitables dans le memoire/articles.

Le script n'utilise que la bibliotheque standard pour rester reproductible sur
la machine locale. Les graphiques sont produits en SVG afin de pouvoir etre
retouches dans un editeur vectoriel ou inseres tels quels dans le memoire.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path
from statistics import mean
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "docs" / "memoire" / "figures"
TABLES = ROOT / "docs" / "memoire" / "tables"


COLORS = {
    "ink": "#172026",
    "muted": "#5b6770",
    "grid": "#d9dee3",
    "blue": "#2f6fbb",
    "teal": "#148f77",
    "orange": "#d9822b",
    "red": "#c23b38",
    "green": "#2f8f46",
    "purple": "#6f58a8",
    "gray": "#8a96a3",
}


@dataclass
class Bar:
    label: str
    value: float
    color: str = COLORS["blue"]
    note: str = ""


def read_csv(path: Path, sep: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=sep))


def as_float(value: str | None, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return default


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_existing(*paths: Path) -> Path:
    existing = [path for path in paths if path.exists()]
    if not existing:
        return paths[0]
    return max(existing, key=lambda path: path.stat().st_mtime)


def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
        "<style>",
        "text{font-family:Arial,Helvetica,sans-serif;fill:#172026}",
        ".title{font-size:22px;font-weight:700}",
        ".subtitle{font-size:13px;fill:#5b6770}",
        ".axis{font-size:11px;fill:#5b6770}",
        ".label{font-size:12px}",
        ".small{font-size:10px;fill:#5b6770}",
        "</style>",
    ]


def save_svg(path: Path, parts: Iterable[str]) -> None:
    write_text(path, "\n".join(parts))


def bar_chart(path: Path, title: str, subtitle: str, bars: list[Bar], x_label: str = "") -> None:
    width = 980
    left = 260
    right = 70
    top = 92
    bar_h = 28
    gap = 17
    height = top + len(bars) * (bar_h + gap) + 70
    max_value = max([bar.value for bar in bars] + [1.0])
    max_axis = 1.0 if max_value <= 1.0 else max_value * 1.08
    plot_w = width - left - right

    parts = svg_header(width, height)
    parts.append(f'<text x="36" y="36" class="title">{escape(title)}</text>')
    parts.append(f'<text x="36" y="59" class="subtitle">{escape(subtitle)}</text>')

    for tick in range(0, 6):
        value = max_axis * tick / 5
        x = left + plot_w * tick / 5
        parts.append(f'<line x1="{x:.1f}" y1="{top - 15}" x2="{x:.1f}" y2="{height - 55}" stroke="{COLORS["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{x:.1f}" y="{height - 32}" text-anchor="middle" class="axis">{value:.2f}</text>')

    for index, bar in enumerate(bars):
        y = top + index * (bar_h + gap)
        value_w = plot_w * bar.value / max_axis
        parts.append(f'<text x="{left - 14}" y="{y + 19}" text-anchor="end" class="label">{escape(bar.label)}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{value_w:.1f}" height="{bar_h}" rx="3" fill="{bar.color}"/>')
        parts.append(f'<text x="{left + value_w + 8:.1f}" y="{y + 19}" class="label">{bar.value:.4g}</text>')
        if bar.note:
            parts.append(f'<text x="{left}" y="{y + bar_h + 12}" class="small">{escape(bar.note)}</text>')

    if x_label:
        parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 8}" text-anchor="middle" class="subtitle">{escape(x_label)}</text>')
    parts.append("</svg>")
    save_svg(path, parts)


def line_chart(path: Path, title: str, subtitle: str, rows: list[dict[str, str]]) -> None:
    width, height = 980, 470
    left, right, top, bottom = 80, 45, 82, 72
    plot_w, plot_h = width - left - right, height - top - bottom
    values = [as_float(row.get("workflow_sec")) for row in rows]
    cycles = [int(as_float(row.get("cycle"))) for row in rows]
    max_value = max(values + [1.0]) * 1.1

    parts = svg_header(width, height)
    parts.append(f'<text x="36" y="36" class="title">{escape(title)}</text>')
    parts.append(f'<text x="36" y="59" class="subtitle">{escape(subtitle)}</text>')
    for tick in range(0, 6):
        value = max_value * tick / 5
        y = top + plot_h - plot_h * tick / 5
        parts.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="{COLORS["grid"]}" stroke-width="1"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" class="axis">{value:.1f}s</text>')

    points: list[tuple[float, float]] = []
    for idx, value in enumerate(values):
        x = left + (plot_w * idx / max(1, len(values) - 1))
        y = top + plot_h - (plot_h * value / max_value)
        points.append((x, y))
    point_attr = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    parts.append(f'<polyline points="{point_attr}" fill="none" stroke="{COLORS["blue"]}" stroke-width="4"/>')
    for idx, ((x, y), value) in enumerate(zip(points, values)):
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{COLORS["orange"]}"/>')
        parts.append(f'<text x="{x:.1f}" y="{y - 11:.1f}" text-anchor="middle" class="small">{value:.2f}s</text>')
        parts.append(f'<text x="{x:.1f}" y="{height - 35}" text-anchor="middle" class="axis">{cycles[idx]}</text>')
    parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 10}" text-anchor="middle" class="subtitle">Cycles du workflow</text>')
    parts.append(f'<text x="20" y="{top + plot_h / 2:.1f}" transform="rotate(-90 20 {top + plot_h / 2:.1f})" text-anchor="middle" class="subtitle">Latence workflow</text>')
    parts.append("</svg>")
    save_svg(path, parts)


def matrix_diagram(path: Path) -> None:
    width, height = 980, 560
    parts = svg_header(width, height)
    parts.append('<text x="36" y="36" class="title">Architecture logique Logminer</text>')
    parts.append('<text x="36" y="59" class="subtitle">Flux agents: collecte, normalisation, routage, detection, correlation et visualisation</text>')
    nodes = [
        ("Collecteur", 55, 130, COLORS["blue"]),
        ("Parseur", 230, 130, COLORS["teal"]),
        ("Normaliseur", 405, 130, COLORS["teal"]),
        ("Routeur", 580, 130, COLORS["purple"]),
        ("Detecteur IA", 755, 130, COLORS["orange"]),
        ("Correlateur", 315, 310, COLORS["red"]),
        ("Dashboard", 525, 310, COLORS["green"]),
        ("Audit / Bus", 735, 310, COLORS["gray"]),
    ]
    for label, x, y, color in nodes:
        parts.append(f'<rect x="{x}" y="{y}" width="145" height="68" rx="8" fill="{color}" opacity="0.96"/>')
        parts.append(f'<text x="{x + 72.5}" y="{y + 41}" text-anchor="middle" fill="#fff" style="font-family:Arial;font-size:15px;font-weight:700">{escape(label)}</text>')
    arrows = [
        (200, 164, 230, 164),
        (375, 164, 405, 164),
        (550, 164, 580, 164),
        (725, 164, 755, 164),
        (827, 198, 388, 310),
        (460, 344, 525, 344),
        (670, 344, 735, 344),
    ]
    parts.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#172026"/></marker></defs>')
    for x1, y1, x2, y2 in arrows:
        parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#172026" stroke-width="2.2" marker-end="url(#arrow)"/>')
    notes = [
        ("V1 CLI stable", 82, 245),
        ("V2 FastAPI locale", 382, 245),
        ("V3 Redis/MQTT en extension", 662, 245),
    ]
    for text, x, y in notes:
        parts.append(f'<text x="{x}" y="{y}" class="subtitle">{escape(text)}</text>')
    parts.append("</svg>")
    save_svg(path, parts)


def write_markdown_table(path: Path, title: str, headers: list[str], rows: list[list[str]]) -> None:
    lines = [f"# {title}", "", "| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(escape(str(cell), quote=False) for cell in row) + " |")
    lines.append("")
    write_text(path, "\n".join(lines))


def generate() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)

    validation = read_csv(PROCESSED / "validation_selection_summary.csv", sep=";")
    validation_bars = [
        Bar(
            label=f"{row['dataset']} / {row['model']}",
            value=as_float(row.get("f1")),
            color=[COLORS["blue"], COLORS["teal"], COLORS["orange"]][idx % 3],
            note=f"duree={as_float(row.get('duration_sec')):.4g}s; memoire={as_float(row.get('memory_peak_mb')):.4g} MB",
        )
        for idx, row in enumerate(validation)
    ]
    bar_chart(
        FIGURES / "fig_validation_selection_f1.svg",
        "Comparaison des meilleurs detecteurs par dataset",
        "Score F1 des modeles retenus dans les validations BGL, HDFS et Windows simule",
        validation_bars,
        "F1-score",
    )

    supervised_rows: list[Bar] = []
    linux = read_csv(PROCESSED / "random_forest_linux_auth_metrics.csv")[0]
    cicids = read_csv(PROCESSED / "random_forest_network_cicids_metrics.csv")[0]
    unsw = read_csv(ROOT / "data" / "random_forest_unsw_80_20_metrics.csv", sep=";")[0]
    supervised_rows.extend(
        [
            Bar("Linux/auth RF", as_float(linux["f1"]), COLORS["green"], "dataset Linux/auth tabulaire"),
            Bar("CICIDS RF", as_float(cicids["f1"]), COLORS["blue"], "MachineLearningCVE"),
            Bar("UNSW/CIC-DDoS RF", as_float(unsw["f1"]), COLORS["orange"], "test 80/20 par chunks"),
        ]
    )
    bar_chart(
        FIGURES / "fig_supervised_models_f1.svg",
        "Performances des modeles supervises",
        "RandomForest specialises par famille de journaux ou flux reseau",
        supervised_rows,
        "F1-score",
    )

    benchmark_path = latest_existing(
        PROCESSED / "realtime_workflow_benchmark.csv",
        PROCESSED / "realtime_workflow_benchmark_20260604.csv",
    )
    benchmark = read_csv(benchmark_path, sep=";")
    benchmark_ok = [row for row in benchmark if row.get("status") == "ok"]
    line_chart(
        FIGURES / "fig_realtime_workflow_latency.svg",
        "Latence du workflow quasi temps reel",
        f"Endpoint FastAPI /run/discovered, {len(benchmark_ok)} cycles, max_mb=5, source selectionnee automatiquement",
        benchmark,
    )

    robustness = read_csv(PROCESSED / "robustness_scalability_report.csv", sep=";")
    robustness_bars = [
        Bar(row["detected_kind"], as_float(row["normalized_rows"]), COLORS["teal"], row["file"])
        for row in robustness
    ]
    bar_chart(
        FIGURES / "fig_robustness_multiformat.svg",
        "Robustesse du parsing multi-format",
        "Controle sur Apache, CEF/LEEF, CloudTrail, Linux auth et log incomplet",
        robustness_bars,
        "Lignes normalisees",
    )

    registry = read_csv(PROCESSED / "model_registry.csv")
    model_bars: list[Bar] = []
    for row in registry:
        raw = row["events_or_train_rows"].split()[0]
        value = as_float(raw)
        if value <= 0:
            continue
        model_bars.append(
            Bar(
                row["family"],
                math.log10(value),
                COLORS["purple"] if "random_forest" in row["model_type"] else COLORS["gray"],
                f"{row['model_type']} - {row['events_or_train_rows']}",
            )
        )
    bar_chart(
        FIGURES / "fig_model_portfolio_scale.svg",
        "Portefeuille des modeles entraines",
        "Volume d'entrainement ou d'evenements, represente en log10 pour lisibilite",
        model_bars,
        "log10(volume)",
    )

    matrix_diagram(FIGURES / "fig_architecture_logminer.svg")

    latency_values = [as_float(row["workflow_sec"]) for row in benchmark_ok]
    write_markdown_table(
        TABLES / "table_realtime_benchmark.md",
        "Benchmark Quasi Temps Reel",
        ["Indicateur", "Valeur"],
        [
            ["Cycles OK", str(len(latency_values))],
            ["Lignes par cycle", benchmark[0].get("input_rows", "") if benchmark else ""],
            ["Latence moyenne workflow", f"{mean(latency_values):.4f} s" if latency_values else ""],
            ["Latence min workflow", f"{min(latency_values):.4f} s" if latency_values else ""],
            ["Latence max workflow", f"{max(latency_values):.4f} s" if latency_values else ""],
        ],
    )

    write_markdown_table(
        TABLES / "table_resultats_principaux.md",
        "Resultats Principaux",
        ["Famille", "Dataset", "Modele", "Type", "Resultat principal"],
        [
            ["Windows", "Security/Application/System", "Isolation Forest", "Non supervise", "Anomalies candidates et incidents correles"],
            ["Wazuh", "Exports Janvier/Octobre/Decembre", "Isolation Forest", "Non supervise", "122563 evenements, 3676 anomalies candidates"],
            ["Linux/auth", "linux_auth_logs_*", "RandomForest", "Supervise", f"F1={as_float(linux['f1']):.6f}"],
            ["CICIDS", "MachineLearningCVE", "RandomForest", "Supervise", f"F1={as_float(cicids['f1']):.6f}"],
            ["UNSW/CIC-DDoS", "UNSWNB15/CIC-DDoS", "RandomForest", "Supervise", f"F1={as_float(unsw['f1']):.6f}"],
            ["HDFS", "HDFS logs", "Ensemble/Isolation Forest", "Non supervise", "Meilleure selection autour de F1=0.599333"],
            ["BGL", "BlueGene/L", "Ensemble/Autoencoder/IForest", "Non supervise", "Meilleure selection autour de F1=0.994333"],
        ],
    )

    write_markdown_table(
        TABLES / "table_datasets_scenarios.md",
        "Datasets Et Scenarios Experimentaux",
        ["Categorie", "Source", "Nature", "Objectif de test", "Preuve locale"],
        [
            ["Reel local", "Windows Event/Application/System/Security", "Journaux systeme Windows", "Collecte, parsing EVTX/XML, detection locale", "windows_collection_summary.txt; windows_*_pipeline.csv"],
            ["Reel/SIEM", "Wazuh exports", "Alertes et evenements SIEM/HIDS", "Detection non supervisee sur signaux securite", "wazuh_months_logminer.csv; wazuh_months_anomalies.csv"],
            ["Reel/tabulaire", "Linux/auth", "Authentification Linux labelisee", "Evaluation supervisee et faux positifs", "random_forest_linux_auth_metrics.csv"],
            ["Public systeme", "HDFS", "Logs distribues avec labels", "Validation detecteurs sur logs sequentiels", "validation_hdfs_metrics.csv"],
            ["Public systeme", "BGL", "Logs BlueGene/L avec labels", "Validation detecteurs sur logs HPC", "validation_bgl_metrics.csv"],
            ["Public reseau", "CICIDS2017/MachineLearningCVE", "Flux reseau labelises", "Detection supervisee attaques connues", "random_forest_network_cicids_metrics.csv"],
            ["Public reseau", "UNSW/CIC-DDoS", "Flux reseau/DDoS", "Evaluation 80/20 par chunks", "random_forest_unsw_80_20_metrics.csv"],
            ["Controle simule", "Windows simule", "Evenements avec anomalies injectees", "Comparer baseline, statistiques et IA", "validation_simulated_windows_metrics.csv"],
            ["Robustesse", "Apache, CEF/LEEF, CloudTrail, Linux auth, log incomplet", "Multi-format et entree corrompue", "Tolerance parser et conservation unknown", "robustness_scalability_report.csv"],
        ],
    )

    write_markdown_table(
        TABLES / "table_comparaison_outils_standards.md",
        "Comparaison Qualitative Avec Outils Standards",
        ["Critere", "Logminer", "fail2ban", "OSSEC/Wazuh"],
        [
            ["Detection", "Anomalies statistiques/IA et correlation contextuelle", "Regles sur echecs d'authentification et bannissement IP", "Regles, decodage, alertes SIEM/HIDS"],
            ["Sources", "Windows, Linux, Wazuh, HDFS, BGL, reseau, cloud", "Principalement services exposes et logs auth", "Tres large via agents et decoders"],
            ["Adaptation", "Routage multi-modeles; apprentissage par famille", "Seuils et filtres configures manuellement", "Regles, listes, enrichissements et configuration SOC"],
            ["Explicabilite", "Scores, incidents, justification locale/dashboard", "Tres explicable par regle", "Alertes riches mais dependantes des regles"],
            ["Positionnement", "Complement analytique leger pour anomalies candidates", "Protection operationnelle immediate", "Socle SIEM/HIDS mature a completer par IA"],
        ],
    )

    resource_snapshot = PROCESSED / "resource_snapshot_20260603.json"
    if resource_snapshot.exists():
        resources = json.loads(resource_snapshot.read_text(encoding="utf-8-sig"))
        write_markdown_table(
            TABLES / "table_resource_snapshot.md",
            "Instantane Ressources Agents",
            ["Agent", "Role", "PID", "CPU", "Memoire", "Statut"],
            [
                [
                    agent.get("agent", ""),
                    agent.get("role", ""),
                    agent.get("pids", ""),
                    f"{as_float(str(agent.get('cpu_percent', ''))):.2f} %",
                    f"{as_float(str(agent.get('memory_mb', ''))):.2f} MB",
                    agent.get("status", ""),
                ]
                for agent in resources.get("agents", [])
            ],
        )

    figure_index = [
        "# Index Des Figures Generees",
        "",
        "| Figure | Usage recommande |",
        "| --- | --- |",
        "| `fig_architecture_logminer.svg` | Chapitre architecture, article architecture multi-agents |",
        "| `fig_validation_selection_f1.svg` | Etat de l'art experimental et chapitre resultats |",
        "| `fig_supervised_models_f1.svg` | Resultats supervises Linux/auth, CICIDS, UNSW |",
        "| `fig_realtime_workflow_latency.svg` | Objectifs 4 et 7: temps quasi reel, latence |",
        "| `fig_robustness_multiformat.svg` | Objectifs 1, 6 et 7: robustesse multi-format |",
        "| `fig_model_portfolio_scale.svg` | Methodologie: portefeuille de modeles specialises |",
        "| `fig_parallel_resource_campaign.svg` | Scalabilite locale: execution parallele de detecteurs et consommation CPU/RAM |",
        "",
        "Tableaux principaux: `docs/memoire/tables/table_resultats_principaux.md`,",
        "`docs/memoire/tables/table_datasets_scenarios.md`,",
        "`docs/memoire/tables/table_realtime_benchmark.md`,",
        "`docs/memoire/tables/table_comparaison_outils_standards.md`,",
        "`docs/memoire/tables/table_resource_snapshot.md`,",
        "`docs/memoire/tables/table_parallel_resource_campaign.md`.",
        "",
    ]
    write_text(FIGURES / "README.md", "\n".join(figure_index))


def main() -> int:
    generate()
    print(f"Figures: {FIGURES}")
    print(f"Tables: {TABLES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
