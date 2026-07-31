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

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "logminer"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from agents.audit import DEFAULT_AUDIT_PATH, read_audit, write_audit
from agents.detector import align_features
from agents.model_router import _linux_auth_features, _positive_class_probability, _supervised_features
from features.event_features import build_feature_frame


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
    validation_csv: Path | None = None
    validation_sep: str = "auto"
    label_column: str = ""
    expected_anomaly_rate: float | None = None


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


def _infer_sep(path: Path, sep: str = "auto") -> str:
    if sep.lower() != "auto":
        return sep
    sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:8192]
    return max([";", ",", "\t"], key=sample.count)


def _detect_label_column(frame: pd.DataFrame, label_column: str = "") -> str:
    if label_column and label_column in frame.columns:
        return label_column
    candidates = [
        "label",
        "Label",
        "is_anomaly",
        "is_attack",
        "anomaly",
        "anomaly_label",
        "class",
        "Class",
        "target",
        "Target",
    ]
    for candidate in candidates:
        if candidate in frame.columns:
            return candidate
    return ""


def _labels_from_frame(frame: pd.DataFrame, label_column: str = "") -> pd.Series | None:
    selected = _detect_label_column(frame, label_column)
    if not selected:
        return None

    values = frame[selected].astype(str).str.strip().str.lower()
    positive_values = {
        "1",
        "true",
        "yes",
        "y",
        "anomaly",
        "anomalous",
        "abnormal",
        "attack",
        "attacked",
        "malicious",
        "failure",
        "failed",
        "fail",
        "error",
        "analyst_confirmed",
    }
    negative_values = {"0", "false", "no", "n", "normal", "benign", "none", "-"}

    numeric = pd.to_numeric(values, errors="coerce")
    labels = values.isin(positive_values).astype(int)
    labels = labels.mask(values.isin(negative_values), 0)
    labels = labels.mask(numeric.notna(), (numeric.fillna(0) != 0).astype(int))
    return labels.astype(int)


def _load_validation(path: Path, sep: str) -> pd.DataFrame:
    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path).astype(str)
    return pd.read_csv(path, sep=_infer_sep(path, sep), dtype=str, keep_default_na=False)


def _score_artifact(artifact_path: Path, events: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    artifact = joblib.load(artifact_path)
    if not isinstance(artifact, dict) or "model" not in artifact:
        raise ValueError(f"Artefact modele invalide: {artifact_path}")

    model = artifact["model"]
    model_type = str(artifact.get("model_type", type(model).__name__)).lower()
    feature_columns = list(artifact.get("feature_columns", []))

    if model_type == "random_forest_linux_auth":
        features = _linux_auth_features(events, feature_columns)
        labels = pd.Series(model.predict(features).astype(int), index=events.index)
        scores = pd.Series(_positive_class_probability(model, features, labels.to_numpy()), index=events.index)
        return labels, scores

    if model_type.startswith("random_forest"):
        features = _supervised_features(events, feature_columns)
        labels = pd.Series(model.predict(features).astype(int), index=events.index)
        scores = pd.Series(_positive_class_probability(model, features, labels.to_numpy()), index=events.index)
        return labels, scores

    features = build_feature_frame(events)
    features = align_features(features, feature_columns)
    raw_labels = model.predict(features)
    scores = pd.Series(model.decision_function(features), index=events.index)
    labels = pd.Series((raw_labels == -1).astype(int), index=events.index)
    return labels, scores


def evaluate_model(
    artifact_path: Path,
    validation_csv: Path,
    *,
    sep: str = "auto",
    label_column: str = "",
    expected_anomaly_rate: float | None = None,
) -> dict[str, float | int | str]:
    events = _load_validation(validation_csv, sep)
    labels, scores = _score_artifact(artifact_path, events)
    truth = _labels_from_frame(events, label_column)
    anomaly_rate = float(labels.mean()) if len(labels) else 0.0

    metrics: dict[str, float | int | str] = {
        "artifact": str(artifact_path),
        "validation_csv": str(validation_csv),
        "events": int(len(events)),
        "anomalies": int(labels.sum()),
        "anomaly_rate": anomaly_rate,
        "score_min": float(scores.min()) if len(scores) else 0.0,
        "score_mean": float(scores.mean()) if len(scores) else 0.0,
        "score_max": float(scores.max()) if len(scores) else 0.0,
    }

    if truth is not None and int(truth.nunique()) >= 2:
        metrics.update(
            {
                "accuracy": float(accuracy_score(truth, labels)),
                "precision": float(precision_score(truth, labels, zero_division=0)),
                "recall": float(recall_score(truth, labels, zero_division=0)),
                "f1": float(f1_score(truth, labels, zero_division=0)),
            }
        )
    else:
        target_rate = expected_anomaly_rate
        if target_rate is None:
            target_rate = min(max(anomaly_rate, 0.001), 0.5)
        # Score proxy quand aucun label n'existe: il recompense un taux
        # d'alertes proche du taux operationnel attendu, sans pretendre mesurer
        # une verite-terrain. Les familles sans labels doivent garder un seuil
        # de promotion prudent dans le plan.
        metrics["stability_score"] = float(max(0.0, 1.0 - abs(anomaly_rate - target_rate) / max(target_rate, 1e-9)))
    return metrics


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
                validation_csv=_resolve(item["validation_csv"]) if item.get("validation_csv") else None,
                validation_sep=str(item.get("validation_sep", "auto")),
                label_column=str(item.get("label_column", "")),
                expected_anomaly_rate=(
                    float(item["expected_anomaly_rate"]) if item.get("expected_anomaly_rate") is not None else None
                ),
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

    current_metrics: dict[str, object]
    candidate_metrics: dict[str, object]
    if job.validation_csv is not None:
        current_metrics = evaluate_model(
            job.current_model,
            job.validation_csv,
            sep=job.validation_sep,
            label_column=job.label_column,
            expected_anomaly_rate=job.expected_anomaly_rate,
        )
        candidate_metrics = evaluate_model(
            job.candidate_model,
            job.validation_csv,
            sep=job.validation_sep,
            label_column=job.label_column,
            expected_anomaly_rate=job.expected_anomaly_rate,
        )
        job.candidate_metrics.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame([{f"current_{k}": v for k, v in current_metrics.items()} | {f"candidate_{k}": v for k, v in candidate_metrics.items()}]).to_csv(
            job.candidate_metrics,
            index=False,
            encoding="utf-8-sig",
        )
        current_score = float(current_metrics[job.metric])
        candidate_score = float(candidate_metrics[job.metric])
    else:
        current_metrics = {"metrics_csv": str(job.current_metrics)}
        candidate_metrics = {"metrics_csv": str(job.candidate_metrics)}
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
        "current_metrics": current_metrics,
        "candidate_metrics": candidate_metrics,
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
