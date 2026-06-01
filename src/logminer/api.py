"""API FastAPI V2 pour piloter les agents Logminer.

La V2 expose la logique stable de la V1 CLI sans la remplacer. Les endpoints
acceptent des chemins locaux du projet, puis appellent les fonctions deja
utilisees par les commandes CLI: parsing, routage, detection et correlation.
"""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.model_router import MODEL_DEFAULTS, route_model, run_routed_detection
from agents.correlator import correlate_anomalies
from pipeline import run_pipeline


app = FastAPI(
    title="Logminer API",
    description="API V2 locale pour router, detecter et correler des journaux heterogenes.",
    version="0.1.0",
)


class RouteRequest(BaseModel):
    input_path: str = Field(..., description="Chemin local vers un CSV, Parquet ou log brut")
    sep: str = "auto"
    sample_rows: int = 1000


class ParseRequest(BaseModel):
    input_path: str
    out_dir: str = "data/processed"
    out_name: str = "api_parsed.csv"
    sep: str = ";"
    debug: bool = False


class DetectRequest(BaseModel):
    input_path: str
    sep: str = "auto"
    sample_rows: int = 1000
    output: str | None = None
    incidents_output: str | None = None
    window_minutes: int = 15


class CorrelateRequest(BaseModel):
    input_path: str = Field(..., description="CSV d'anomalies produit par la detection")
    output: str = "data/processed/api_incidents.csv"
    sep: str = "auto"
    window_minutes: int = 15


class RunRequest(BaseModel):
    input_path: str
    parse_if_needed: bool = True
    out_dir: str = "data/processed"
    sep: str = "auto"
    sample_rows: int = 1000
    window_minutes: int = 15
    run_id: str | None = None


def _path(value: str | Path) -> Path:
    path = Path(value).expanduser()
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _existing_path(value: str | Path) -> Path:
    path = _path(value)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Chemin introuvable: {path}")
    return path


def _infer_sep(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:8192]
    return max([";", ",", "\t"], key=sample.count)


def _count_rows(path: str | Path, sep: str = "auto") -> int | None:
    file_path = _path(path)
    try:
        if file_path.suffix.lower() == ".csv":
            return max(sum(1 for _ in file_path.open("r", encoding="utf-8-sig", errors="ignore")) - 1, 0)
        if file_path.suffix.lower() == ".parquet":
            return int(len(pd.read_parquet(file_path, columns=[])))
    except Exception:
        return None
    return None


def _model_summary(family: str, artifact: str) -> dict[str, Any]:
    path = _path(artifact)
    return {
        "family": family,
        "artifact": str(path),
        "exists": path.exists(),
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def _model_paths() -> dict[str, Path]:
    return {family: _path(artifact) for family, artifact in MODEL_DEFAULTS.items()}


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": "v2-fastapi",
        "time_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/models")
def models() -> dict[str, Any]:
    return {"models": [_model_summary(family, artifact) for family, artifact in MODEL_DEFAULTS.items()]}


@app.post("/route")
def route(request: RouteRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    try:
        return route_model(input_path, sep=request.sep, sample_rows=request.sample_rows, models=_model_paths())
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/parse")
def parse(request: ParseRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    try:
        produced = run_pipeline(
            input_path,
            request.out_dir,
            request.out_name,
            sep=request.sep,
            debug=request.debug,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"produced": produced, "count": len(produced)}


@app.post("/detect")
def detect(request: DetectRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    try:
        result = run_routed_detection(
            input_path,
            sep=request.sep,
            sample_rows=request.sample_rows,
            output=request.output,
            incidents_output=request.incidents_output,
            window_minutes=request.window_minutes,
            models=_model_paths(),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        **result,
        "input_rows": _count_rows(input_path, request.sep),
        "anomalies_rows": _count_rows(result["anomalies_csv"], _infer_sep(_path(result["anomalies_csv"]))),
        "incidents_rows": _count_rows(result["incidents_csv"], _infer_sep(_path(result["incidents_csv"]))),
    }


@app.post("/correlate")
def correlate(request: CorrelateRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    output_path = _path(request.output)
    sep = _infer_sep(input_path) if request.sep == "auto" else request.sep
    try:
        incidents_csv = correlate_anomalies(
            input_path,
            output_path,
            sep=sep,
            window_minutes=request.window_minutes,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "input_path": str(input_path),
        "incidents_csv": incidents_csv,
        "incidents_rows": _count_rows(incidents_csv, sep),
    }


@app.post("/run")
def run(request: RunRequest) -> dict[str, Any]:
    input_path = _existing_path(request.input_path)
    run_id = request.run_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = _path(request.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    source_for_detection = input_path
    parsed_csv = ""
    if request.parse_if_needed and input_path.suffix.lower() not in {".csv", ".parquet"}:
        parsed_name = f"api_{run_id}_parsed.csv"
        parse_sep = ";" if request.sep == "auto" else request.sep
        produced = run_pipeline(input_path, out_dir, parsed_name, sep=parse_sep)
        if not produced:
            raise HTTPException(status_code=400, detail="Aucun CSV produit par le parsing")
        source_for_detection = _path(produced[0])
        parsed_csv = str(source_for_detection)

    anomalies_csv = out_dir / f"api_{run_id}_anomalies.csv"
    incidents_csv = out_dir / f"api_{run_id}_incidents.csv"
    try:
        result = run_routed_detection(
            source_for_detection,
            sep=request.sep,
            sample_rows=request.sample_rows,
            output=anomalies_csv,
            incidents_output=incidents_csv,
            window_minutes=request.window_minutes,
            models=_model_paths(),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "run_id": run_id,
        "input_path": str(input_path),
        "parsed_csv": parsed_csv,
        **result,
        "input_rows": _count_rows(source_for_detection, request.sep),
        "anomalies_rows": _count_rows(result["anomalies_csv"], _infer_sep(_path(result["anomalies_csv"]))),
        "incidents_rows": _count_rows(result["incidents_csv"], _infer_sep(_path(result["incidents_csv"]))),
    }
