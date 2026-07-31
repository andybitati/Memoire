"""Orchestre un reentrainement mensuel controle des modeles Logminer.

Le script ne remplace jamais un modele directement apres entrainement. Il:

1. exporte les decisions analyste depuis l'audit vers un CSV de feedback;
2. execute les commandes de reentrainement declarees dans un plan JSON;
3. compare le modele courant et le candidat avec une metrique explicite;
4. promeut le candidat seulement si le seuil d'amelioration est atteint.

Le plan JSON garde les commandes propres a chaque famille de modele, car les
artefacts supervises et non supervises n'utilisent pas les memes datasets.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "logminer"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agents.audit import DEFAULT_AUDIT_PATH, read_audit, write_audit


POSITIVE_DECISIONS = {"accept", "reclassify"}
NEGATIVE_DECISIONS = {"reject"}


@dataclass(frozen=True)
class ModelJob:
    family: str
    current_model: Path
    candidate_model: Path
    current_metrics: Path
    candidate_metrics: Path
    train_command: list[str]
    metric: str = "f1"
    min_delta: float = 0.0


def _resolve(path: str | Path) -> Path:
    candidate = Path(path)
    return candidate if candidate.is_absolute() else ROOT / candidate


def export_feedback_dataset(audit_path: Path, output_csv: Path, *, limit: int = 10000) -> int:
    """Exporte les decisions analyste en lignes labelisees reutilisables."""

    rows: list[dict[str, object]] = []
    for entry in read_audit(limit=limit, path=audit_path):
        if not entry.action.startswith("alert."):
            continue
        decision = entry.action.replace("alert.", "", 1)
        if decision not in POSITIVE_DECISIONS | NEGATIVE_DECISIONS:
            continue

        details = entry.details or {}
        rows.append(
            {
                "timestamp": entry.timestamp,
                "decision": decision,
                "label": 1 if decision in POSITIVE_DECISIONS else 0,
                "anomaly_label": "analyst_confirmed" if decision in POSITIVE_DECISIONS else "normal",
                "target": entry.target,
                "category": details.get("category", ""),
                "severity": details.get("severity", ""),
                "event": details.get("event", entry.target),
                "source": details.get("source", ""),
                "message": details.get("reason", ""),
            }
        )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "timestamp",
                "decision",
                "label",
                "anomaly_label",
                "target",
                "category",
                "severity",
                "event",
                "source",
                "message",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _read_metric(path: Path, metric: str) -> float:
    if not path.exists():
        raise FileNotFoundError(f"Fichier de metriques introuvable: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        row = next(reader, None)
    if row is None:
        raise ValueError(f"Fichier de metriques vide: {path}")
    if metric not in row:
        raise ValueError(f"Metrique '{metric}' absente dans {path}")
    return float(str(row[metric]).replace(",", "."))


def _copy_with_backup(source: Path, target: Path, backup_dir: Path) -> Path:
    if not source.exists():
        raise FileNotFoundError(f"Modele candidat introuvable: {source}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = backup_dir / f"{target.stem}.{timestamp}{target.suffix}"
    if target.exists():
        shutil.copy2(target, backup)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return backup


def load_plan(path: Path) -> list[ModelJob]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    jobs = raw.get("models", raw if isinstance(raw, list) else [])
    if not isinstance(jobs, list):
        raise ValueError("Le plan doit contenir une liste 'models'.")

    result: list[ModelJob] = []
    for item in jobs:
        result.append(
            ModelJob(
                family=str(item["family"]),
                current_model=_resolve(item["current_model"]),
                candidate_model=_resolve(item["candidate_model"]),
                current_metrics=_resolve(item["current_metrics"]),
                candidate_metrics=_resolve(item["candidate_metrics"]),
                train_command=[str(part) for part in item["train_command"]],
                metric=str(item.get("metric", "f1")),
                min_delta=float(item.get("min_delta", 0.0)),
            )
        )
    return result


def _expand_command(parts: Iterable[str], feedback_csv: Path) -> list[str]:
    values = {
        "{python}": sys.executable,
        "{root}": str(ROOT),
        "{feedback_csv}": str(feedback_csv),
    }
    expanded: list[str] = []
    for part in parts:
        value = str(part)
        for key, replacement in values.items():
            value = value.replace(key, replacement)
        expanded.append(value)
    return expanded


def run_job(job: ModelJob, *, feedback_csv: Path, promote: bool, dry_run: bool, backups_dir: Path) -> dict[str, object]:
    command = _expand_command(job.train_command, feedback_csv)
    if dry_run:
        return {
            "family": job.family,
            "status": "dry_run",
            "metric": job.metric,
            "current_score": None,
            "candidate_score": None,
            "delta": None,
            "min_delta": job.min_delta,
            "promoted": False,
            "backup": "",
            "command": " ".join(command),
        }
    else:
        completed = subprocess.run(command, cwd=ROOT, check=False)
        if completed.returncode != 0:
            return {"family": job.family, "status": "train_failed", "returncode": completed.returncode}

    current_score = _read_metric(job.current_metrics, job.metric)
    candidate_score = _read_metric(job.candidate_metrics, job.metric)
    delta = candidate_score - current_score
    better = delta >= job.min_delta

    promoted = False
    backup = ""
    if better and promote and not dry_run:
        backup = str(_copy_with_backup(job.candidate_model, job.current_model, backups_dir))
        promoted = True
        status = "promoted"
    elif better:
        status = "candidate_better"
    else:
        status = "kept_current"

    return {
        "family": job.family,
        "status": status,
        "metric": job.metric,
        "current_score": round(current_score, 6),
        "candidate_score": round(candidate_score, 6),
        "delta": round(delta, 6),
        "min_delta": job.min_delta,
        "promoted": promoted,
        "backup": backup,
        "command": " ".join(command),
    }


def run_plan(
    plan_path: Path,
    *,
    audit_path: Path,
    feedback_csv: Path,
    report_out: Path,
    backups_dir: Path,
    promote: bool,
    dry_run: bool,
) -> list[dict[str, object]]:
    feedback_rows = export_feedback_dataset(audit_path, feedback_csv)
    jobs = load_plan(plan_path)
    rows = [
        run_job(job, feedback_csv=feedback_csv, promote=promote, dry_run=dry_run, backups_dir=backups_dir)
        for job in jobs
    ]

    report_out.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan": str(plan_path),
        "audit_path": str(audit_path),
        "feedback_csv": str(feedback_csv),
        "feedback_rows": feedback_rows,
        "promote": promote,
        "dry_run": dry_run,
        "results": rows,
    }
    report_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_audit(
        action="models.monthly_retraining",
        actor="scheduler",
        target=str(plan_path),
        details={"report": str(report_out), "feedback_rows": feedback_rows, "results": rows},
    )
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reentrainement mensuel controle des modeles Logminer")
    parser.add_argument("--plan", required=True, type=Path, help="Plan JSON des modeles a reentrainer")
    parser.add_argument("--audit-path", default=DEFAULT_AUDIT_PATH, type=Path)
    parser.add_argument("--feedback-csv", default=Path("data/processed/monthly_feedback_labels.csv"), type=Path)
    parser.add_argument("--report-out", default=Path("data/processed/monthly_retraining_report.json"), type=Path)
    parser.add_argument("--backups-dir", default=Path("models/backups"), type=Path)
    parser.add_argument("--promote", action="store_true", help="Remplace le modele courant si le candidat gagne")
    parser.add_argument("--dry-run", action="store_true", help="N'execute pas les commandes d'entrainement")
    args = parser.parse_args(argv)

    rows = run_plan(
        _resolve(args.plan),
        audit_path=_resolve(args.audit_path),
        feedback_csv=_resolve(args.feedback_csv),
        report_out=_resolve(args.report_out),
        backups_dir=_resolve(args.backups_dir),
        promote=args.promote,
        dry_run=args.dry_run,
    )
    for row in rows:
        if row.get("status") == "dry_run":
            print(f"{row['family']}: dry_run command={row['command']}")
        elif row.get("status") == "train_failed":
            print(f"{row['family']}: train_failed returncode={row.get('returncode')}")
        else:
            print(
                "{family}: {status} {metric} current={current_score} candidate={candidate_score} delta={delta}".format(
                    **row
                )
            )
    print(f"Rapport: {_resolve(args.report_out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
