"""Produit les preuves manquantes rapides pour le suivi technique du TFE.

Sorties:
- tableaux Markdown pour faux positifs, campagne ressources, resilience,
  comparaison operationnelle;
- rapport de disponibilite des figures/tableaux pour memoire et articles.

Le script reste volontairement sans dependances externes.
"""

from __future__ import annotations

import csv
import json
import statistics
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
TABLES = ROOT / "docs" / "memoire" / "tables"
FIGURES = ROOT / "docs" / "memoire" / "figures"
REPORT = ROOT / "docs" / "memoire" / "verification_assets_articles.md"


def read_csv(path: Path, sep: str = ",") -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=sep))


def number(value: object, default: float = 0.0) -> float:
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return default


def write_markdown_table(path: Path, title: str, headers: list[str], rows: list[list[object]]) -> None:
    lines = [
        f"# {title}",
        "",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_svg_bar_chart(path: Path, title: str, subtitle: str, rows: list[tuple[str, float]]) -> None:
    width = 980
    left = 250
    right = 90
    top = 88
    bar_h = 28
    gap = 14
    height = top + len(rows) * (bar_h + gap) + 60
    max_value = max([value for _, value in rows] + [1.0])
    plot_w = width - left - right
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        "<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172026}.title{font-size:22px;font-weight:700}.sub{font-size:13px;fill:#5b6770}.axis{font-size:11px;fill:#5b6770}.label{font-size:12px}</style>",
        f'<text x="36" y="36" class="title">{title}</text>',
        f'<text x="36" y="58" class="sub">{subtitle}</text>',
    ]
    for tick in range(6):
        x = left + plot_w * tick / 5
        value = max_value * tick / 5
        parts.append(f'<line x1="{x:.1f}" y1="{top - 16}" x2="{x:.1f}" y2="{height - 46}" stroke="#d9dee3"/>')
        parts.append(f'<text x="{x:.1f}" y="{height - 24}" text-anchor="middle" class="axis">{value:.1f}</text>')
    for index, (label, value) in enumerate(rows):
        y = top + index * (bar_h + gap)
        w = plot_w * value / max_value
        color = "#c23b38" if value >= 50 else "#d9822b" if value >= 5 else "#2f8f46"
        parts.append(f'<text x="{left - 12}" y="{y + 19}" text-anchor="end" class="label">{label}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="3" fill="{color}"/>')
        parts.append(f'<text x="{left + w + 8:.1f}" y="{y + 19}" class="label">{value:.3f}</text>')
    parts.append(f'<text x="{left + plot_w / 2:.1f}" y="{height - 4}" text-anchor="middle" class="sub">Faux positifs pour 1000 lignes</text>')
    parts.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(parts), encoding="utf-8")


def false_positive_rows() -> list[list[object]]:
    rows: list[list[object]] = []

    sources = [
        ("Linux/auth", PROCESSED / "random_forest_linux_auth_metrics.csv", ","),
        ("CICIDS2017", PROCESSED / "random_forest_network_cicids_metrics.csv", ","),
        ("CIC-DDoS2019", ROOT / "data" / "random_forest_unsw_80_20_metrics.csv", ";"),
    ]
    for label, path, sep in sources:
        if not path.exists():
            continue
        row = read_csv(path, sep=sep)[0]
        fp = number(row.get("fp"))
        tn = number(row.get("tn"))
        fn = number(row.get("fn"))
        tp = number(row.get("tp"))
        test_rows = number(row.get("test_rows"), tp + fp + fn + tn)
        fpr = fp / max(fp + tn, 1)
        fp_per_1000 = fp / max(test_rows, 1) * 1000
        rows.append(
            [
                label,
                row.get("model", ""),
                int(test_rows),
                int(fp),
                int(tn),
                f"{fpr:.6f}",
                f"{fp_per_1000:.3f}",
                "Periode non calculable: metriques agregees sans horodatage ligne par ligne",
            ]
        )

    validation = PROCESSED / "validation_selection_summary.csv"
    if validation.exists():
        for row in read_csv(validation, sep=";"):
            fp = number(row.get("fp"))
            tn = number(row.get("tn"))
            events = number(row.get("events"))
            fpr = fp / max(fp + tn, 1)
            rows.append(
                [
                    row.get("dataset", ""),
                    row.get("model", ""),
                    int(events),
                    int(fp),
                    int(tn),
                    f"{fpr:.6f}",
                    f"{fp / max(events, 1) * 1000:.3f}",
                    "Validation controlee; periode non conservee dans le CSV de metriques",
                ]
            )
    return rows


def resource_campaign_rows() -> list[list[object]]:
    snapshots = sorted(PROCESSED.glob("resource_snapshot*.json"))
    samples: list[dict[str, object]] = []
    for path in snapshots:
        try:
            payload = json.loads(path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            continue
        for agent in payload.get("agents", []):
            samples.append(
                {
                    "agent": agent.get("agent", ""),
                    "cpu_core": number(agent.get("cpu_percent")),
                    "cpu_machine": number(agent.get("cpu_machine_percent")),
                    "memory_mb": number(agent.get("memory_mb")),
                }
            )

    grouped: dict[str, list[dict[str, object]]] = {}
    for sample in samples:
        grouped.setdefault(str(sample["agent"]), []).append(sample)

    rows: list[list[object]] = []
    for agent, values in sorted(grouped.items()):
        cpu_core = [number(item["cpu_core"]) for item in values]
        cpu_machine = [number(item["cpu_machine"]) for item in values if number(item["cpu_machine"]) > 0]
        memory = [number(item["memory_mb"]) for item in values]
        rows.append(
            [
                agent,
                len(values),
                f"{statistics.mean(cpu_core):.2f}",
                f"{max(cpu_core):.2f}",
                f"{statistics.mean(cpu_machine):.2f}" if cpu_machine else "n/a",
                f"{statistics.mean(memory):.2f}",
                f"{max(memory):.2f}",
                "Campagne courte; a repeter pendant plusieurs cycles pour une evaluation finale",
            ]
        )
    return rows


def benchmark_rows() -> list[list[object]]:
    paths = [
        path
        for path in [
            PROCESSED / "realtime_workflow_benchmark.csv",
            PROCESSED / "realtime_workflow_benchmark_20260604.csv",
        ]
        if path.exists()
    ]
    if not paths:
        return []
    path = max(paths, key=lambda item: item.stat().st_mtime)
    rows = read_csv(path, sep=";")
    ok = [row for row in rows if row.get("status") == "ok"]
    values = [number(row.get("workflow_sec")) for row in ok]
    return [
        ["Cycles OK", len(ok)],
        ["Lignes par cycle", ok[0].get("input_rows", "") if ok else ""],
        ["Latence moyenne", f"{statistics.mean(values):.4f} s" if values else "n/a"],
        ["Latence min", f"{min(values):.4f} s" if values else "n/a"],
        ["Latence max", f"{max(values):.4f} s" if values else "n/a"],
    ]


def asset_report() -> str:
    required_figures = [
        "fig_architecture_logminer.svg",
        "fig_validation_selection_f1.svg",
        "fig_supervised_models_f1.svg",
        "fig_realtime_workflow_latency.svg",
        "fig_robustness_multiformat.svg",
        "fig_model_portfolio_scale.svg",
        "fig_false_positive_rates.svg",
        "fig_wazuh_logminer_overlap.svg",
        "fig_resource_campaign_multicycle.svg",
    ]
    required_tables = [
        "table_resultats_principaux.md",
        "table_datasets_scenarios.md",
        "table_realtime_benchmark.md",
        "table_resource_snapshot.md",
        "table_comparaison_outils_standards.md",
        "table_false_positives.md",
        "table_resource_campaign.md",
        "table_resilience_agent.md",
        "table_operational_tool_comparison.md",
        "table_fail2ban_like_baseline.md",
        "table_wazuh_logminer_summary.md",
        "table_wazuh_logminer_overlap.md",
        "table_resource_campaign_multicycle.md",
    ]

    lines = [
        "# Verification Des Assets Pour Memoire Et Articles",
        "",
        "## Figures",
        "",
        "| Fichier | Etat | Taille |",
        "| --- | --- | --- |",
    ]
    for name in required_figures:
        path = FIGURES / name
        ok = path.exists() and path.stat().st_size > 0 and "<svg" in path.read_text(encoding="utf-8", errors="ignore")
        lines.append(f"| `{name}` | {'pret' if ok else 'manquant'} | {path.stat().st_size if path.exists() else 0} |")

    lines.extend(["", "## Tableaux", "", "| Fichier | Etat | Taille |", "| --- | --- | --- |"])
    for name in required_tables:
        path = TABLES / name
        ok = path.exists() and path.stat().st_size > 0
        lines.append(f"| `{name}` | {'pret' if ok else 'manquant'} | {path.stat().st_size if path.exists() else 0} |")

    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Les assets principaux pour la redaction scientifique sont disponibles si tous les etats ci-dessus sont `pret`.",
            "Les captures dashboard restent a produire separement depuis le navigateur.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    TABLES.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)

    fp_rows = false_positive_rows()

    write_markdown_table(
        TABLES / "table_false_positives.md",
        "Faux Positifs Et Taux Associes",
        ["Dataset", "Modele", "Lignes test", "FP", "TN", "FPR", "FP / 1000 lignes", "Periode"],
        fp_rows,
    )
    write_svg_bar_chart(
        FIGURES / "fig_false_positive_rates.svg",
        "Faux positifs par 1000 lignes",
        "Comparaison des modeles/datasets avec metriques agregees disponibles",
        [(f"{row[0]} / {row[1]}", number(row[6])) for row in fp_rows],
    )

    write_markdown_table(
        TABLES / "table_resource_campaign.md",
        "Campagne Ressources Agents",
        ["Agent", "Snapshots", "CPU equiv. coeur moy.", "CPU equiv. coeur max", "CPU machine moy.", "RAM moy. MB", "RAM max MB", "Commentaire"],
        resource_campaign_rows(),
    )

    write_markdown_table(
        TABLES / "table_resilience_agent.md",
        "Resilience Et Modes De Degradation",
        ["Scenario", "Etat actuel", "Preuve", "Conclusion"],
        [
            ["Redis indisponible", "Supporte", "FastAPI et dashboard fonctionnent sans Redis; bus JSONL/CSV reste exploitable", "Degradation acceptable pour prototype local"],
            ["Log corrompu/incomplet", "Supporte", "robustness_scalability_report.csv: statut kept_unknown", "Pas de perte silencieuse; entree conservee"],
            ["Agent collecteur sans acces admin", "Supporte partiellement", "Privilege agent genere une demande/lanceur admin", "Le systeme ne contourne pas les droits OS"],
            ["Arret volontaire d'un agent", "Non prouve en campagne longue", "Architecture modulaire V1/V2; pas de stress test prolonge", "A presenter comme limite/perspective"],
        ],
    )

    write_markdown_table(
        TABLES / "table_operational_tool_comparison.md",
        "Comparaison Operationnelle Outils Standards",
        ["Point", "Logminer", "fail2ban", "OSSEC/Wazuh", "Conclusion"],
        [
            ["Reaction automatique", "Decision analyste/audit, pas de bannissement systeme", "Bannissement IP operationnel", "Alertes/regles HIDS/SIEM", "Logminer complete plus qu'il ne remplace"],
            ["Detection inconnue", "IA legere et rarete statistique", "Limitee aux filtres", "Depend des regles/decoders", "Avantage Logminer sur signaux atypiques"],
            ["Maturite SOC", "Prototype recherche", "Outil operationnel cible", "Plateforme mature", "Wazuh/OSSEC restent references production"],
            ["Interpretabilite", "Scores, incidents, dashboard", "Regles simples", "Regles et contexte SIEM", "Complementarite forte"],
            ["Donnees heterogenes", "Routeur multi-modeles", "Principalement logs auth/service", "Tres large via agents", "Logminer interessant comme couche analytique"],
        ],
    )

    write_markdown_table(
        TABLES / "table_realtime_benchmark_detailed.md",
        "Benchmark Temps Reel Detaille",
        ["Indicateur", "Valeur"],
        benchmark_rows(),
    )

    REPORT.write_text(asset_report(), encoding="utf-8")
    print(f"Tables completees: {TABLES}")
    print(f"Rapport assets: {REPORT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
