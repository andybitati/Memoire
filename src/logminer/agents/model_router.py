"""Agent routeur de modeles.

Cet agent choisit le modele d'anomalie adapte a la famille du journal:

- windows: Windows Event, Security, System, Application;
- hdfs: journaux HDFS;
- bgl: journaux BlueGene/L;
- network: tcpdump, pcap, UNSWNB15, flux IP/ports/protocoles;
- linux: syslog/Linux structure;
- fallback: modele general si la famille reste incertaine.

Il peut seulement afficher la route choisie, ou lancer detection + correlation
avec le modele selectionne.

Cet agent evite d'appliquer un modele appris sur une distribution a une autre
distribution trop differente. C'est important depuis que le projet a montre que
le modele global detectait parfois le "format rare" plutot que l'anomalie
interne au dataset.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Optional

import joblib
import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.correlator import correlate_anomalies
from agents.detector import detect_anomalies
from detectors.file_detector import detect_kind


MODEL_DEFAULTS = {
    "windows": "models/isolation_forest_windows_local.joblib",
    "hdfs": "models/isolation_forest_hdfs_colab.joblib",
    "bgl": "models/isolation_forest_bgl_colab.joblib",
    "network": "models/random_forest_network_unsw_80_20_sampled.joblib",
    "linux": "models/isolation_forest_linux_colab.joblib",
    "fallback": "models/isolation_forest_colab.joblib",
}

# Types issus du detecteur de fichiers bruts. Ils servent surtout quand l'entree
# n'est pas encore un CSV/Parquet normalise.
KIND_FAMILY = {
    "win_event": "windows",
    "hdfs": "hdfs",
    "bgl": "bgl",
    "pcap": "network",
    "tcpdump_text": "network",
    "apache": "network",
    "syslog": "linux",
}

FAMILY_LABELS = {
    "windows": ("windows", "win_event", "security.evtx", "microsoft-windows", "security-auditing"),
    "hdfs": ("hdfs", "blk_", "dfs."),
    "bgl": ("bgl", "bluegene", "ras"),
    "network": ("pcap", "tcpdump", "unsw", "ddos", "drdos", "tcp", "udp", "icmp"),
    "linux": ("linux", "syslog", "ubuntu", "kernel"),
}
IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
PORT_RE = re.compile(r"^\d{1,5}$")
WINDOWS_EVENT_RE = re.compile(r"^\d{3,5}$")

# Colonnes typiques d'un dataset reseau. Plus il y en a, plus le score reseau
# augmente. On garde les noms en minuscules car les CSV viennent de sources tres
# differentes.
NETWORK_COLUMNS = {
    "src_ip",
    "dst_ip",
    "src_port",
    "dst_port",
    "proto",
    "service",
    "state",
    "dur",
    "spkts",
    "dpkts",
    "sbytes",
    "dbytes",
    "rate",
    "sload",
    "dload",
    "attack_cat",
}
# Colonnes typiques des journaux systeme/applicatifs normalises par Logminer.
SYSTEM_COLUMNS = {
    "event",
    "source",
    "host",
    "user",
    "severity",
    "component",
    "pid",
    "tid",
    "session",
}
FAMILY_COLUMNS = {
    "windows": SYSTEM_COLUMNS | {"recno", "session"},
    "hdfs": {"blockid", "block_id", "blk", "event", "component"},
    "bgl": {"event", "component", "severity", "source"},
    "network": NETWORK_COLUMNS,
    "linux": {"facility", "program", "severity", "host", "pid", "message"},
}


def _infer_sep(path: Path) -> str:
    """Detecte rapidement le separateur d'un CSV sans charger le fichier."""

    sample = path.read_text(encoding="utf-8-sig", errors="ignore")[:8192]
    return max([";", ",", "\t"], key=sample.count)


def _read_sample(path: Path, sep: str, nrows: int) -> pd.DataFrame:
    """Lit un petit echantillon pour router sans cout eleve."""

    suffix = path.suffix.lower()
    if suffix == ".parquet":
        # Les fichiers UNSW Parquet sont deja structures; quelques lignes
        # suffisent pour identifier leurs colonnes reseau.
        return pd.read_parquet(path).head(nrows).astype(str)

    csv_sep = _infer_sep(path) if sep.lower() == "auto" else sep
    return pd.read_csv(path, sep=csv_sep, dtype=str, keep_default_na=False, nrows=nrows)


def _series_values(df: pd.DataFrame, column: str, limit: int = 300) -> pd.Series:
    if column not in df.columns:
        return pd.Series(dtype=str)
    return df[column].astype(str).head(limit).str.strip()


def _non_empty_ratio(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return 0.0
    values = df[column].astype(str).str.strip()
    if len(values) == 0:
        return 0.0
    return float((values != "").mean())


def _active_column(df: pd.DataFrame, lower_to_original: dict[str, str], *names: str, min_ratio: float = 0.05) -> bool:
    for name in names:
        column = lower_to_original.get(name)
        if column and _non_empty_ratio(df, column) >= min_ratio:
            return True
    return False


def _has_column(lower_columns: set[str], *names: str) -> bool:
    return any(name in lower_columns for name in names)


def _sample_profile(df: pd.DataFrame, path: Path | None = None) -> dict[str, object]:
    """Construit un profil de features pour router le fichier.

    Ce profil combine plusieurs signaux au lieu de se limiter au nom des
    colonnes. Cela reduit les confusions entre datasets qui partagent des champs
    generiques comme `severity`, `source` ou `message`.
    """

    original_columns = [str(column).lstrip("\ufeff") for column in df.columns]
    lower_columns = {column.lower() for column in original_columns}
    lower_to_original = {column.lower(): column for column in original_columns}

    text_parts: list[str] = []
    for column in original_columns[: min(len(original_columns), 20)]:
        text_parts.append(df[column].astype(str).str.lower().head(200).str.cat(sep=" "))
    if path is not None:
        text_parts.append(f"{path.name.lower()} {path.stem.lower()}")
    text = " ".join(text_parts)

    numeric_columns = 0
    for column in original_columns:
        values = pd.to_numeric(df[column].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        if values.notna().mean() >= 0.8:
            numeric_columns += 1

    dataset_values = ""
    if "dataset" in lower_to_original:
        dataset_values = _series_values(df, lower_to_original["dataset"], 300).str.lower().str.cat(sep=" ")

    proto_values = ""
    if "proto" in lower_to_original:
        proto_values = _series_values(df, lower_to_original["proto"], 300).str.lower().str.cat(sep=" ")
    elif "protocol" in lower_to_original:
        proto_values = _series_values(df, lower_to_original["protocol"], 300).str.lower().str.cat(sep=" ")

    event_values = ""
    if "event" in lower_to_original:
        event_values = _series_values(df, lower_to_original["event"], 300).str.cat(sep=" ")

    source_values = ""
    if "source" in lower_to_original:
        source_values = _series_values(df, lower_to_original["source"], 300).str.lower().str.cat(sep=" ")

    message_values = ""
    if "message" in lower_to_original:
        message_values = _series_values(df, lower_to_original["message"], 300).str.lower().str.cat(sep=" ")

    return {
        "columns": lower_columns,
        "lower_to_original": lower_to_original,
        "text": text,
        "dataset_values": dataset_values,
        "proto_values": proto_values,
        "event_values": event_values,
        "source_values": source_values,
        "message_values": message_values,
        "numeric_columns": numeric_columns,
        "column_count": len(original_columns),
        "row_count": len(df),
        "has_ips": bool(IP_RE.search(text)),
    }


def _score_dataframe(df: pd.DataFrame, path: Path | None = None) -> tuple[dict[str, int], list[str]]:
    """Attribue un score a chaque famille de logs.

    Le routage reste volontairement explicable. Les raisons retournees sont
    affichees en CLI pour justifier le choix du modele.
    """

    profile = _sample_profile(df, path=path)
    lower_columns = profile["columns"]
    lower_to_original = profile["lower_to_original"]
    text = str(profile["text"])
    dataset_values = str(profile["dataset_values"])
    proto_values = str(profile["proto_values"])
    event_values = str(profile["event_values"])
    source_values = str(profile["source_values"])
    message_values = str(profile["message_values"])
    reasons: list[str] = []

    scores = {family: 0 for family in MODEL_DEFAULTS}
    scores["fallback"] = 1

    # Signal principal: le nom des colonnes. C'est le plus stable pour les CSV
    # deja structures comme UNSW, tcpdump converti ou Windows normalise.
    for family, expected_columns in FAMILY_COLUMNS.items():
        matched = lower_columns & expected_columns
        if matched:
            scores[family] += len(matched) * 8
            reasons.append(f"colonnes {family}: " + ",".join(sorted(matched)[:8]))

    for family, tokens in FAMILY_LABELS.items():
        matched_tokens = [token for token in tokens if token in text or token in dataset_values]
        if matched_tokens:
            scores[family] += 35
            reasons.append(f"marqueurs {family}: " + ",".join(matched_tokens[:5]))

    # Features reseau: IP, ports, protocole, compteurs de paquets/bytes, labels
    # d'attaque. Ces signaux ensemble sont beaucoup plus fiables qu'un seul nom
    # de colonne.
    network_feature_hits = 0
    if _active_column(df, lower_to_original, "src_ip", "source ip") and _active_column(
        df, lower_to_original, "dst_ip", "destination ip"
    ):
        network_feature_hits += 2
    if _active_column(df, lower_to_original, "src_port", "source port") and _active_column(
        df, lower_to_original, "dst_port", "destination port"
    ):
        network_feature_hits += 2
    if _active_column(df, lower_to_original, "proto", "protocol") or any(token in proto_values for token in ("tcp", "udp", "icmp")):
        network_feature_hits += 2
    if lower_columns & {"spkts", "dpkts", "sbytes", "dbytes", "flow bytes/s", "flow packets/s"}:
        network_feature_hits += 2
    if lower_columns & {"attack_cat", "label", "inbound"} and any(token in text for token in ("ddos", "drdos", "normal", "attack")):
        network_feature_hits += 2
    if profile["has_ips"]:
        network_feature_hits += 1
    if network_feature_hits:
        scores["network"] += network_feature_hits * 12
        reasons.append(f"features reseau={network_feature_hits}")

    # Features Windows: provider Microsoft, EventID numerique, colonnes host/user
    # et champs typiques de l'Event Log.
    windows_feature_hits = 0
    if "microsoft-windows" in source_values or "security-auditing" in source_values or "microsoft-windows" in text:
        windows_feature_hits += 3
    if event_values and sum(1 for value in event_values.split()[:100] if WINDOWS_EVENT_RE.match(value)) >= 10:
        windows_feature_hits += 2
    if lower_columns & {"recno", "session", "event", "source", "host", "user"}:
        windows_feature_hits += min(len(lower_columns & {"recno", "session", "event", "source", "host", "user"}), 4)
    if "security.evtx" in text or "windows_event" in dataset_values:
        windows_feature_hits += 2
    if windows_feature_hits:
        scores["windows"] += windows_feature_hits * 10
        reasons.append(f"features windows={windows_feature_hits}")

    # Features HDFS: BlockId et vocabulaire NameNode/DataNode/DFS.
    hdfs_feature_hits = 0
    if "hdfs" in dataset_values or "hdfs" in text:
        hdfs_feature_hits += 2
    if "blk_" in text or "block" in " ".join(lower_columns):
        hdfs_feature_hits += 3
    if any(token in message_values for token in ("namenode", "datanode", "dfs", "block")):
        hdfs_feature_hits += 2
    if hdfs_feature_hits:
        scores["hdfs"] += hdfs_feature_hits * 12
        reasons.append(f"features hdfs={hdfs_feature_hits}")

    # Features BGL: dataset BGL, RAS, BlueGene/L et composants BGL.
    bgl_feature_hits = 0
    if "bgl" in dataset_values or "bgl" in text:
        bgl_feature_hits += 3
    if " ras " in f" {text} " or "bluegene" in text:
        bgl_feature_hits += 3
    if any(token in message_values for token in ("ciod", "ras", "kernel")):
        bgl_feature_hits += 1
    if bgl_feature_hits:
        scores["bgl"] += bgl_feature_hits * 12
        reasons.append(f"features bgl={bgl_feature_hits}")

    # Features Linux/syslog: marqueurs systeme Linux, colonnes process/pid et
    # messages kernel/auth. On garde ce score modere pour ne pas voler Windows.
    linux_feature_hits = 0
    if "linux" in dataset_values or "syslog" in dataset_values:
        linux_feature_hits += 3
    if any(token in message_values for token in ("kernel", "sudo", "sshd", "systemd", "ubuntu")):
        linux_feature_hits += 2
    if "pid" in lower_columns and "message" in lower_columns:
        linux_feature_hits += 1
    if linux_feature_hits:
        scores["linux"] += linux_feature_hits * 10
        reasons.append(f"features linux={linux_feature_hits}")

    # Signal statistique transversal: les datasets reseau tabulaires ont souvent
    # beaucoup plus de colonnes numeriques que les logs systeme normalises.
    if int(profile["numeric_columns"]) >= 15 and int(profile["column_count"]) >= 25:
        scores["network"] += 20
        reasons.append("profil numerique dense")

    return scores, reasons


def route_model(
    input_path: str | Path,
    *,
    sep: str = "auto",
    sample_rows: int = 1000,
    models: dict[str, str | Path] | None = None,
) -> dict[str, object]:
    """Retourne la famille de logs et le modele a utiliser.

    La fonction ne lance pas la detection. Elle decide seulement quelle route
    prendre, ce qui permet de la tester facilement et de l'utiliser dans un
    futur orchestrateur.
    """

    path = Path(input_path)
    if not path.exists():
        raise FileNotFoundError(f"Chemin introuvable: {path}")

    if path.is_file() and path.suffix.lower() in {".csv", ".parquet"}:
        # Pour les datasets deja tabulaires, le routeur lit un echantillon et
        # inspecte les colonnes/valeurs au lieu de passer par le parseur brut.
        df = _read_sample(path, sep=sep, nrows=sample_rows)
        scores, reasons = _score_dataframe(df, path=path)
        kind = path.suffix.lower().lstrip(".")
    else:
        # Pour un fichier brut, on reutilise le detecteur historique du projet.
        # Les dossiers restent marques "directory": ils doivent normalement
        # passer d'abord par le pipeline de parsing ou par la fusion dataset.
        kind = detect_kind(str(path)) if path.is_file() else "directory"
        scores = {family: 0 for family in MODEL_DEFAULTS}
        scores["fallback"] = 1
        if kind in KIND_FAMILY:
            scores[KIND_FAMILY[kind]] += 60
        reasons = [f"type detecte: {kind}"]

    # En cas d'egalite, l'ordre ci-dessous privilegie les familles specialisees
    # avant le fallback general.
    priority = ["windows", "hdfs", "bgl", "network", "linux", "fallback"]
    sorted_scores = sorted(priority, key=lambda family: scores.get(family, 0), reverse=True)
    family = sorted_scores[0]
    confidence = scores.get(sorted_scores[0], 0) - scores.get(sorted_scores[1], 0)

    model_map = dict(MODEL_DEFAULTS)
    if models:
        model_map.update({key: str(value) for key, value in models.items() if value})
    model = model_map[family]

    return {
        "family": family,
        "model": str(model),
        "kind": kind,
        "scores": scores,
        "confidence": confidence,
        "reasons": reasons,
    }


def _default_output(input_path: Path, suffix: str) -> Path:
    """Construit un nom de sortie stable pour le mode `--detect`."""

    stem = input_path.stem or "dataset"
    return Path("data/processed") / f"{stem}_{suffix}.csv"


SUPERVISED_DROP_COLUMNS = {
    "label",
    "Label",
    "Flow ID",
    "Source IP",
    "Destination IP",
    "Timestamp",
    "Unnamed: 0",
    "dataset",
}


def _supervised_features(events: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Prepare les features attendues par un modele supervise tabulaire.

    Le RandomForest reseau a ete entraine directement sur les colonnes CIC/DDoS
    (`Flow Duration`, `Total Fwd Packets`, etc.), et non sur les features
    generiques de `detector.py`. Le routeur garde donc une preparation dediee.
    """

    chunk = events.copy()
    chunk.columns = chunk.columns.astype(str).str.strip()
    features = chunk.drop(columns=[column for column in SUPERVISED_DROP_COLUMNS if column in chunk.columns], errors="ignore")
    features = features.reindex(columns=feature_columns, fill_value=0)
    features = features.replace(["Infinity", "INF", "inf", "-inf", "-Infinity", "NaN", "nan"], np.nan)

    for column in features.columns:
        features[column] = features[column].astype(str).str.replace(",", ".", regex=False)

    features = features.apply(pd.to_numeric, errors="coerce")
    features = features.replace([np.inf, -np.inf], np.nan).fillna(0)
    features = features.clip(lower=-1e12, upper=1e12)
    return features.astype("float64")


def _positive_class_probability(model: object, features: pd.DataFrame, labels: np.ndarray) -> np.ndarray:
    """Retourne la probabilite d'attaque si le modele l'expose."""

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(features)
        classes = list(getattr(model, "classes_", []))
        if 1 in classes:
            return probabilities[:, classes.index(1)]
        if len(classes) >= 2:
            return probabilities[:, -1]
    return labels.astype(float)


def _detect_supervised_model(
    input_csv: str | Path,
    output_csv: str | Path,
    *,
    sep: str,
    artifact: dict[str, object],
    chunksize: int = 100000,
) -> str:
    """Score un CSV avec un artefact supervise sauvegarde au format Logminer."""

    model = artifact["model"]
    if hasattr(model, "n_jobs"):
        # Les artefacts Colab/Kaggle peuvent avoir ete entraines avec n_jobs>1.
        # En inference locale routee, un seul worker evite les erreurs de pool
        # Windows/sandbox sans changer les predictions.
        model.n_jobs = 1
    if hasattr(model, "verbose"):
        model.verbose = 0
    feature_columns = list(artifact["feature_columns"])
    input_path = Path(input_csv)
    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    csv_sep = _infer_sep(input_path) if sep.lower() == "auto" else sep
    if input_path.suffix.lower() == ".parquet":
        chunks = [pd.read_parquet(input_path)]
    else:
        chunks = pd.read_csv(input_path, sep=csv_sep, dtype=str, keep_default_na=False, chunksize=chunksize)

    write_header = True
    total = 0
    anomaly_count = 0
    for events in chunks:
        features = _supervised_features(events, feature_columns)
        labels = model.predict(features).astype(int)
        probabilities = _positive_class_probability(model, features, labels)

        result = events.copy()
        # Convention Logminer: les scores les plus bas sont les plus anormaux.
        result["anomaly_score"] = -probabilities
        result["is_anomaly"] = (labels == 1).astype(int)
        result["anomaly_rank"] = pd.Series(result["anomaly_score"]).rank(method="first", ascending=True).astype(int) + total

        result.sort_values(["is_anomaly", "anomaly_score"], ascending=[False, True]).to_csv(
            output_path,
            sep=csv_sep,
            index=False,
            encoding="utf-8-sig",
            mode="w" if write_header else "a",
            header=write_header,
        )
        write_header = False
        total += len(result)
        anomaly_count += int(result["is_anomaly"].sum())

    print(f"CSV anomalies: {output_path}")
    print(f"Evenements analyses: {total}")
    print(f"Anomalies candidates: {anomaly_count}")
    print(f"Modele supervise charge: {artifact.get('model_type', type(model).__name__)}")
    return str(output_path)


def _load_model_artifact(path: Path) -> dict[str, object]:
    artifact = joblib.load(path)
    if not isinstance(artifact, dict) or "model" not in artifact:
        raise ValueError(f"Artefact modele invalide: {path}")
    return artifact


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Agent routeur systeme/reseau pour choisir le bon modele")
    parser.add_argument("-i", "--input", required=True, help="CSV/Parquet normalise ou fichier brut a classifier")
    parser.add_argument("--sep", default="auto", help="Separateur CSV ou auto")
    parser.add_argument("--sample-rows", type=int, default=1000, help="Nombre de lignes echantillonnees")
    parser.add_argument("--windows-model", default=MODEL_DEFAULTS["windows"], help="Modele Windows")
    parser.add_argument("--hdfs-model", default=MODEL_DEFAULTS["hdfs"], help="Modele HDFS")
    parser.add_argument("--bgl-model", default=MODEL_DEFAULTS["bgl"], help="Modele BGL")
    parser.add_argument("--network-model", default=MODEL_DEFAULTS["network"], help="Modele reseau")
    parser.add_argument("--linux-model", default=MODEL_DEFAULTS["linux"], help="Modele Linux/syslog")
    parser.add_argument("--fallback-model", default=MODEL_DEFAULTS["fallback"], help="Modele general de secours")
    parser.add_argument("--detect", action="store_true", help="Lance detection + correlation avec le modele choisi")
    parser.add_argument("-o", "--output", default="", help="CSV anomalies si --detect")
    parser.add_argument("--incidents-output", default="", help="CSV incidents si --detect")
    parser.add_argument("--window-minutes", type=int, default=15, help="Fenetre de correlation")
    args = parser.parse_args(argv)

    # Etape 1: expliquer quelle famille de logs a ete detectee.
    route = route_model(
        args.input,
        sep=args.sep,
        sample_rows=args.sample_rows,
        models={
            "windows": args.windows_model,
            "hdfs": args.hdfs_model,
            "bgl": args.bgl_model,
            "network": args.network_model,
            "linux": args.linux_model,
            "fallback": args.fallback_model,
        },
    )

    print(f"Famille detectee: {route['family']}")
    print(f"Type/source: {route['kind']}")
    print(f"Modele choisi: {route['model']}")
    score_text = " ".join(f"{family}={score}" for family, score in route["scores"].items())
    print(f"Scores: {score_text} confidence={route['confidence']}")
    if route["reasons"]:
        print("Raisons: " + " | ".join(str(reason) for reason in route["reasons"]))

    if not args.detect:
        return 0

    # Etape 2 optionnelle: lancer le detecteur avec le modele route.
    model_path = Path(str(route["model"]))
    if not model_path.exists():
        raise FileNotFoundError(f"Modele choisi introuvable: {model_path}")

    input_path = Path(args.input)
    anomalies_output = Path(args.output) if args.output else _default_output(input_path, f"{route['family']}_anomalies")
    incidents_output = (
        Path(args.incidents_output)
        if args.incidents_output
        else _default_output(input_path, f"{route['family']}_incidents")
    )

    artifact = _load_model_artifact(model_path)
    if artifact.get("model_type") == "random_forest":
        _detect_supervised_model(args.input, anomalies_output, sep=args.sep, artifact=artifact)
        correlation_sep = _infer_sep(anomalies_output) if args.sep == "auto" else args.sep
        correlate_anomalies(anomalies_output, incidents_output, sep=correlation_sep, window_minutes=args.window_minutes)
    else:
        # Le detecteur Isolation Forest lit un CSV avec separateur explicite. Si
        # le routeur a detecte automatiquement le separateur, on garde la
        # convention Logminer `;`.
        detect_anomalies(args.input, anomalies_output, sep=";" if args.sep == "auto" else args.sep, model_in=model_path)
        correlate_anomalies(anomalies_output, incidents_output, window_minutes=args.window_minutes)

    print(f"CSV anomalies: {anomalies_output}")
    print(f"CSV incidents: {incidents_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
