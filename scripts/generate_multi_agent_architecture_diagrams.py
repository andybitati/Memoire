"""Génère les diagrammes d'architecture et de séquence multi-agents."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "architecture"


def box(axis, x, y, width, height, text, color):
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.02",
        facecolor=color,
        edgecolor="#263238",
        linewidth=1.2,
    )
    axis.add_patch(patch)
    axis.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=9)


def arrow(axis, start, end, label=""):
    axis.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=12, color="#37474f", linewidth=1.2))
    if label:
        axis.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.02, label, ha="center", fontsize=8)


def architecture_diagram(path: Path):
    fig, axis = plt.subplots(figsize=(11, 6.5))
    axis.set_xlim(0, 11)
    axis.set_ylim(0, 7)
    axis.axis("off")
    box(axis, 0.4, 5.5, 2.0, 0.8, "Source de tâches", "#e3f2fd")
    box(axis, 4.2, 5.5, 2.6, 0.8, "Coordinateur\nregistre · santé · audit", "#fff3e0")
    box(axis, 8.4, 5.5, 2.0, 0.8, "Redis Streams\ntransport central", "#ffebee")
    for index, (name, x) in enumerate((("Agent A · Debian", 0.7), ("Agent B · Ubuntu", 4.45), ("Agent C · local", 8.2))):
        box(axis, x, 2.3, 2.1, 1.3, f"{name}\nétat · capacités\npolitique · mémoire", "#e8f5e9")
        box(axis, x, 0.5, 2.1, 0.8, "Plusieurs handlers", "#f3e5f5")
        arrow(axis, (x + 1.05, 2.3), (x + 1.05, 1.3), "exécute")
    arrow(axis, (2.4, 5.9), (4.2, 5.9), "soumet")
    arrow(axis, (6.8, 5.9), (8.4, 5.9), "messages")
    for redis_x, agent_x in ((8.75, 1.75), (9.4, 5.5), (10.05, 9.25)):
        axis.add_patch(
            FancyArrowPatch(
                (redis_x, 5.5),
                (agent_x, 3.65),
                arrowstyle="<->",
                mutation_scale=12,
                color="#37474f",
                linewidth=1.2,
            )
        )
    axis.text(5.5, 6.7, "Ariel Logminer — architecture multi-agents légère", ha="center", fontsize=14, weight="bold")
    axis.text(5.5, 0.05, "Décision locale dans les agents; transport Redis central dans le laboratoire", ha="center", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def sequence_diagram(path: Path):
    participants = ["TaskSource", "Coordinateur", "Redis", "A · Debian", "B · Ubuntu", "C · local"]
    x_values = list(range(len(participants)))
    fig, axis = plt.subplots(figsize=(12, 8))
    axis.set_xlim(-0.5, len(participants) - 0.5)
    axis.set_ylim(0, 11)
    axis.axis("off")
    for x, participant in zip(x_values, participants):
        box(axis, x - 0.38, 10.2, 0.76, 0.45, participant, "#eceff1")
        axis.plot([x, x], [0.5, 10.2], linestyle="--", color="#90a4ae", linewidth=0.8)
    exchanges = [
        (9.5, 0, 1, "tâche"),
        (8.9, 1, 2, "CFP"),
        (8.3, 2, 3, "CFP"),
        (7.9, 2, 4, "CFP"),
        (7.5, 2, 5, "CFP"),
        (6.9, 3, 2, "PROPOSE"),
        (6.5, 4, 2, "REFUSE"),
        (6.1, 5, 2, "PROPOSE"),
        (5.5, 2, 1, "offres"),
        (4.9, 1, 2, "AWARD / REJECT"),
        (4.3, 2, 5, "AWARD"),
        (3.7, 5, 2, "ACCEPT"),
        (3.1, 5, 5, "execute"),
        (2.5, 5, 2, "RESULT"),
        (1.9, 2, 1, "résultat"),
        (1.3, 1, 2, "FEEDBACK"),
        (0.8, 2, 5, "FEEDBACK → mémoire"),
    ]
    for y, source, target, label in exchanges:
        if source == target:
            axis.annotate(
                label,
                xy=(source + 0.15, y - 0.2),
                xytext=(source + 0.65, y + 0.2),
                arrowprops={"arrowstyle": "->", "connectionstyle": "arc3,rad=0.45"},
                fontsize=8,
            )
        else:
            arrow(axis, (source, y), (target, y), label)
    axis.text(2.5, 10.9, "Séquence Contract Net sur Redis Streams", ha="center", fontsize=14, weight="bold")
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    architecture_diagram(OUTPUT / "true_multi_agent_architecture.png")
    sequence_diagram(OUTPUT / "contract_net_sequence.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
