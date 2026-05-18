"""Comparaison de detecteurs d'anomalies pour l'objectif 2.

Le script produit un tableau comparatif reproductible. Sans labels verite-terrain,
il compare les modeles par volume d'alertes, score moyen, recouvrement avec une
baseline explicable et temps d'execution. Si un dataset contient une colonne de
label, il calcule aussi precision, rappel et F1-score.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import warnings
from pathlib import Path
from typing import Dict, Optional

import pandas as pd
import numpy as np

# Evite un warning verbeux de joblib/loky sur certains environnements Windows
# verrouilles, ou la detection du nombre de coeurs physiques est refusee.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
# Reduit le bruit des backends deep learning pendant les comparaisons CLI.
# Les avertissements critiques restent visibles, mais les informations CPU/GPU
# de TensorFlow ne polluent plus le tableau de resultats.
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

from sklearn.ensemble import IsolationForest
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.neighbors import LocalOutlierFactor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM


warnings.filterwarnings("ignore", message="Could not find the number of physical cores.*")
warnings.filterwarnings("ignore", message="X does not have valid feature names.*")


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from agents.baseline_detector import score_events
from features.event_features import build_feature_frame, load_events


ModelResult = Dict[str, object]


def _clip_contamination(value: float) -> float:
    return min(max(float(value), 0.001), 0.5)


def _top_by_score(scores: pd.Series, contamination: float, lower_is_more_anomalous: bool) -> pd.Series:
    """Transforme des scores continus en labels binaires selon un quota."""

    limit = max(1, int(len(scores) * _clip_contamination(contamination)))
    ranked = scores.nsmallest(limit) if lower_is_more_anomalous else scores.nlargest(limit)
    labels = pd.Series(0, index=scores.index)
    labels.loc[ranked.index] = 1
    return labels.astype(int)


def _standardize(features: pd.DataFrame) -> pd.DataFrame:
    """Standardise les features pour les modeles sensibles aux distances.

    Isolation Forest accepte bien des variables de magnitudes differentes. En
    revanche z-score, k-Means, SVM, LOF et autoencoder sont plus stables si les
    colonnes sont centrees et reduites.
    """

    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)
    return pd.DataFrame(scaled, index=features.index, columns=features.columns)


def run_baseline(events: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    started = time.perf_counter()
    scored = score_events(events)
    labels = _top_by_score(scored["baseline_score"], contamination, lower_is_more_anomalous=False)
    return {
        "model": "rule_baseline",
        "labels": labels,
        "scores": scored["baseline_score"],
        "duration_sec": time.perf_counter() - started,
        "notes": "Regles + rarete event/source",
    }


def run_z_score(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Detection statistique par z-score.

    Pour chaque evenement, on garde le plus grand ecart absolu normalise parmi
    les features. Un evenement devient suspect s'il est tres eloigne de la
    moyenne sur au moins une dimension.
    """

    started = time.perf_counter()
    scaled = _standardize(features)
    scores = scaled.abs().max(axis=1)
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "z_score",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Statistique: ecart maximal standardise",
    }


def run_iqr(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Detection statistique par intervalle interquartile.

    On calcule les bornes Q1-1.5*IQR et Q3+1.5*IQR par feature. Le score mesure
    combien un evenement sort de ces bornes. Cette approche est robuste aux
    valeurs extremes comparee a une moyenne simple.
    """

    started = time.perf_counter()
    q1 = features.quantile(0.25)
    q3 = features.quantile(0.75)
    iqr = (q3 - q1).replace(0, 1)
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    below = (lower - features).clip(lower=0).div(iqr)
    above = (features - upper).clip(lower=0).div(iqr)
    scores = (below + above).sum(axis=1)
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "iqr",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Statistique: sortie des bornes interquartiles",
    }


def run_histogram(events: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Detection statistique par rarete d'histogramme.

    On exploite des distributions faciles a expliquer: EventID, source,
    severite, categorie et heure. Les combinaisons peu frequentes obtiennent un
    score plus eleve. C'est volontairement interpretable pour le memoire.
    """

    started = time.perf_counter()
    columns = [column for column in ("event", "source", "severity", "category", "subcategory", "host") if column in events]
    if not columns:
        scores = pd.Series(0.0, index=events.index)
    else:
        scores = pd.Series(0.0, index=events.index)
        for column in columns:
            values = events[column].fillna("").astype(str)
            frequencies = values.value_counts(dropna=False, normalize=True)
            # -log(freq) transforme une frequence faible en score fort.
            scores += values.map(lambda value: -np.log(max(float(frequencies.get(value, 0.0)), 1e-12)))
        scores = scores / max(len(columns), 1)

    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "histogram",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Statistique: rarete event/source/severite",
    }


def run_isolation_forest(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    started = time.perf_counter()
    model = IsolationForest(
        n_estimators=200,
        contamination=_clip_contamination(contamination),
        random_state=random_state,
        n_jobs=1,
    )
    raw_labels = model.fit_predict(features)
    scores = pd.Series(model.decision_function(features), index=features.index)
    labels = pd.Series((raw_labels == -1).astype(int), index=features.index)
    return {
        "model": "isolation_forest",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Modele non supervise principal",
    }


def run_one_class_svm(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    started = time.perf_counter()
    if len(features) < 2:
        return {
            "model": "one_class_svm",
            "labels": pd.Series(0, index=features.index),
            "scores": pd.Series(0.0, index=features.index),
            "duration_sec": time.perf_counter() - started,
            "notes": "Ignore: echantillon trop petit",
        }

    scaled = _standardize(features)
    sample = scaled

    # One-Class SVM devient vite couteux. Pour garder un comparatif utilisable
    # sur machine standard, on borne l'echantillon d'apprentissage.
    if len(sample) > 8000:
        sample = sample.sample(8000, random_state=random_state)

    model = OneClassSVM(nu=_clip_contamination(contamination), kernel="rbf", gamma="scale")
    model.fit(sample)
    scores = pd.Series(model.decision_function(scaled), index=features.index)
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=True)
    return {
        "model": "one_class_svm",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "SVM non supervise, echantillonne si gros volume",
    }


def run_lof(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    started = time.perf_counter()
    if len(features) < 3:
        return {
            "model": "local_outlier_factor",
            "labels": pd.Series(0, index=features.index),
            "scores": pd.Series(0.0, index=features.index),
            "duration_sec": time.perf_counter() - started,
            "notes": "Ignore: echantillon trop petit pour le voisinage",
        }

    scaled = _standardize(features)
    sample = scaled

    # LOF a une complexite sensible au nombre de lignes. L'echantillonnage rend
    # le test acceptable pour une grille comparative initiale.
    if len(sample) > 12000:
        sample = sample.sample(12000, random_state=random_state)

    n_neighbors = min(35, max(2, len(sample) - 1))
    model = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=_clip_contamination(contamination), novelty=True)
    model.fit(sample)
    scores = pd.Series(model.decision_function(scaled), index=features.index)
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=True)
    return {
        "model": "local_outlier_factor",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Densite locale, echantillonne si gros volume",
    }


def run_kmeans(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Detection par k-Means.

    Apres clustering, les points les plus eloignes de leur centroide sont
    consideres comme atypiques. Cette methode est simple a expliquer: elle
    cherche des evenements qui ne ressemblent pas a leur groupe.
    """

    started = time.perf_counter()
    if len(features) < 2:
        return {
            "model": "kmeans",
            "labels": pd.Series(0, index=features.index),
            "scores": pd.Series(0.0, index=features.index),
            "duration_sec": time.perf_counter() - started,
            "notes": "Ignore: echantillon trop petit",
        }

    scaled = _standardize(features)
    clusters = min(12, max(2, int(np.sqrt(len(scaled)))))
    sample = scaled
    if len(sample) > 20000:
        sample = sample.sample(20000, random_state=random_state)

    model = MiniBatchKMeans(n_clusters=clusters, random_state=random_state, batch_size=2048, n_init=5)
    model.fit(sample)
    distances = model.transform(scaled)
    scores = pd.Series(distances.min(axis=1), index=features.index)
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "kmeans",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Distance au centroide le plus proche",
    }


def run_autoencoder(features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Autoencoder leger avec MLPRegressor.

    Scikit-learn ne fournit pas une classe Autoencoder dediee, mais un MLP qui
    apprend a reconstruire ses entrees donne un autoencoder simple: plus
    l'erreur de reconstruction est forte, plus l'evenement est suspect.
    """

    started = time.perf_counter()
    if len(features) < 10:
        return {
            "model": "autoencoder_mlp",
            "labels": pd.Series(0, index=features.index),
            "scores": pd.Series(0.0, index=features.index),
            "duration_sec": time.perf_counter() - started,
            "notes": "Ignore: echantillon trop petit",
        }

    scaled = _standardize(features)
    train = scaled
    if len(train) > 12000:
        train = train.sample(12000, random_state=random_state)

    hidden = max(4, min(32, scaled.shape[1] // 2 or 4))
    model = MLPRegressor(
        hidden_layer_sizes=(hidden,),
        activation="relu",
        solver="adam",
        max_iter=80,
        random_state=random_state,
        early_stopping=True,
        n_iter_no_change=8,
    )
    model.fit(train, train)
    reconstructed = model.predict(scaled)
    errors = ((scaled.to_numpy() - reconstructed) ** 2).mean(axis=1)
    scores = pd.Series(errors, index=features.index)
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "autoencoder_mlp",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Erreur de reconstruction MLP",
    }


def _event_sequence_signal(events: pd.DataFrame) -> np.ndarray:
    """Construit un signal numerique simple pour les modeles sequence.

    Le but n'est pas de remplacer une representation avancee de type embedding.
    Pour l'objectif 2, ce signal suffit a tester le principe: predire le
    prochain evenement a partir des derniers evenements observes.
    """

    severity = events.get("severity", pd.Series("", index=events.index)).astype("category").cat.codes.to_numpy()
    event = events.get("event", pd.Series("", index=events.index)).astype("category").cat.codes.to_numpy()
    source = events.get("source", pd.Series("", index=events.index)).astype("category").cat.codes.to_numpy()

    event_scale = max(int(event.max()), 1)
    source_scale = max(int(source.max()), 1)
    signal = severity + event / event_scale + source / source_scale
    return signal.astype("float32").reshape(-1, 1)


def _run_lstm_tensorflow(
    signal: np.ndarray,
    events: pd.DataFrame,
    contamination: float,
    random_state: int,
) -> ModelResult:
    """Backend LSTM prioritaire avec TensorFlow/Keras."""

    import tensorflow as tf
    from tensorflow.keras.layers import LSTM, Dense, Input
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.preprocessing.sequence import TimeseriesGenerator

    started = time.perf_counter()
    tf.get_logger().setLevel("ERROR")
    tf.random.set_seed(random_state)
    window = 10
    generator = TimeseriesGenerator(signal, signal, length=window, batch_size=64)
    model = Sequential([Input(shape=(window, 1)), LSTM(12), Dense(1)])
    model.compile(optimizer="adam", loss="mse")
    model.fit(generator, epochs=3, verbose=0)

    predictions = model.predict(generator, verbose=0).reshape(-1)
    expected = signal[window:].reshape(-1)
    errors = np.abs(expected - predictions)
    scores = pd.Series(0.0, index=events.index)
    scores.iloc[window:] = errors
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "lstm_tensorflow",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "LSTM TensorFlow/Keras prioritaire",
    }


def _run_lstm_pytorch(signal: np.ndarray, events: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Backend LSTM de secours avec PyTorch.

    PyTorch est conserve comme alternative experimentale si TensorFlow n'est
    pas disponible. Le modele reste volontairement petit pour garder les tests
    executables sur CPU.
    """

    started = time.perf_counter()
    import torch
    from torch import nn

    torch.manual_seed(random_state)
    window = 10
    values = torch.tensor(signal, dtype=torch.float32)
    x_chunks = []
    y_chunks = []
    for index in range(len(values) - window):
        x_chunks.append(values[index : index + window])
        y_chunks.append(values[index + window])

    if not x_chunks:
        scores = pd.Series(0.0, index=events.index)
        return {
            "model": "lstm_pytorch",
            "labels": pd.Series(0, index=events.index),
            "scores": scores,
            "duration_sec": time.perf_counter() - started,
            "notes": "Ignore: sequence trop courte",
        }

    x_train = torch.stack(x_chunks)
    y_train = torch.stack(y_chunks)
    if len(x_train) > 12000:
        generator = torch.Generator().manual_seed(random_state)
        indices = torch.randperm(len(x_train), generator=generator)[:12000]
        x_fit = x_train[indices]
        y_fit = y_train[indices]
    else:
        x_fit = x_train
        y_fit = y_train

    class SequenceLSTM(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.lstm = nn.LSTM(input_size=1, hidden_size=12, batch_first=True)
            self.output = nn.Linear(12, 1)

        def forward(self, batch: torch.Tensor) -> torch.Tensor:
            sequence, _ = self.lstm(batch)
            return self.output(sequence[:, -1, :])

    model = SequenceLSTM()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
    loss_fn = nn.MSELoss()

    model.train()
    for _ in range(3):
        optimizer.zero_grad()
        predictions = model(x_fit)
        loss = loss_fn(predictions, y_fit)
        loss.backward()
        optimizer.step()

    model.eval()
    with torch.no_grad():
        predictions = model(x_train).reshape(-1).numpy()

    expected = signal[window:].reshape(-1)
    errors = np.abs(expected - predictions)
    scores = pd.Series(0.0, index=events.index)
    scores.iloc[window:] = errors
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "lstm_pytorch",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "LSTM PyTorch utilise en secours",
    }


def run_lstm(events: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """LSTM optionnel pour sequences d'evenements.

    TensorFlow/Keras est privilegie parce qu'il est plus direct pour prototyper
    des sequences dans ce projet. PyTorch est integre comme secours si
    TensorFlow n'est pas disponible. Si aucun backend deep learning n'est
    installe, le modele est marque comme ignore dans le tableau comparatif.
    """

    started = time.perf_counter()
    signal = _event_sequence_signal(events)
    if len(signal) < 40:
        return {
            "model": "lstm",
            "labels": pd.Series(0, index=events.index),
            "scores": pd.Series(0.0, index=events.index),
            "duration_sec": time.perf_counter() - started,
            "notes": "Ignore: sequence trop courte",
        }

    try:
        return _run_lstm_tensorflow(signal, events, contamination, random_state)
    except Exception as tensorflow_error:
        try:
            return _run_lstm_pytorch(signal, events, contamination, random_state)
        except Exception:
            return {
                "model": "lstm",
                "labels": pd.Series(0, index=events.index),
                "scores": pd.Series(0.0, index=events.index),
                "duration_sec": time.perf_counter() - started,
                "notes": f"Ignore: TensorFlow indisponible, PyTorch indisponible ({type(tensorflow_error).__name__})",
            }


def _labels_from_column(events: pd.DataFrame, label_column: str) -> pd.Series | None:
    if not label_column or label_column not in events.columns:
        return None
    values = events[label_column].astype(str).str.lower()
    return values.isin({"1", "true", "yes", "anomaly", "anomalous", "attack", "malicious"}).astype(int)


def _summarize(
    result: ModelResult,
    total: int,
    baseline_labels: pd.Series,
    truth: pd.Series | None,
) -> dict[str, object]:
    labels = pd.Series(result["labels"]).astype(int)
    scores = pd.Series(result["scores"])
    anomaly_count = int(labels.sum())
    overlap = int(((labels == 1) & (baseline_labels == 1)).sum())

    row: dict[str, object] = {
        "model": result["model"],
        "events": total,
        "anomalies": anomaly_count,
        "anomaly_rate": round(anomaly_count / max(total, 1), 6),
        "score_min": round(float(scores.min()), 6),
        "score_mean": round(float(scores.mean()), 6),
        "score_max": round(float(scores.max()), 6),
        "overlap_with_baseline": overlap,
        "overlap_rate": round(overlap / max(anomaly_count, 1), 6),
        "duration_sec": round(float(result["duration_sec"]), 4),
        "notes": result["notes"],
    }

    if truth is not None:
        row["precision"] = round(float(precision_score(truth, labels, zero_division=0)), 6)
        row["recall"] = round(float(recall_score(truth, labels, zero_division=0)), 6)
        row["f1"] = round(float(f1_score(truth, labels, zero_division=0)), 6)

    return row


def compare_models(
    input_csv: str | Path,
    output_csv: str | Path = "data/processed/model_comparison.csv",
    sep: str = ";",
    contamination: float = 0.05,
    random_state: int = 42,
    label_column: str = "",
    max_categorical_unique: int = 100,
) -> str:
    """Execute les modeles retenus pour l'objectif 2 et ecrit un tableau CSV."""

    events = load_events(input_csv, sep=sep)
    if events.empty:
        raise ValueError(f"Aucun evenement a comparer dans {input_csv}")

    features = build_feature_frame(events, max_categorical_unique=max_categorical_unique)
    if features.empty:
        raise ValueError("Impossible de construire des features ML depuis le CSV fourni")

    results: list[ModelResult] = []
    baseline_result = run_baseline(events, contamination, random_state)
    results.append(baseline_result)

    # Methodes statistiques simples. Elles servent de repere explicable avant
    # les modeles IA: un developpeur peut facilement relier le score a une
    # rarete, une distance a la moyenne ou une sortie des quartiles.
    results.append(run_z_score(features, contamination, random_state))
    results.append(run_iqr(features, contamination, random_state))
    results.append(run_histogram(events, contamination, random_state))

    # Modeles IA non supervises. Ils exploitent la meme matrice numerique pour
    # rendre la comparaison reproductible entre approches.
    results.append(run_isolation_forest(features, contamination, random_state))
    results.append(run_kmeans(features, contamination, random_state))
    results.append(run_one_class_svm(features, contamination, random_state))
    results.append(run_lof(features, contamination, random_state))
    results.append(run_autoencoder(features, contamination, random_state))
    results.append(run_lstm(events, contamination, random_state))

    truth = _labels_from_column(events, label_column)
    baseline_labels = pd.Series(baseline_result["labels"]).astype(int)
    summary = [_summarize(result, len(events), baseline_labels, truth) for result in results]

    output_path = Path(output_csv)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summary).to_csv(output_path, sep=sep, index=False, encoding="utf-8-sig")
    return str(output_path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compare plusieurs detecteurs d'anomalies legers")
    parser.add_argument("-i", "--input", required=True, help="CSV normalise Logminer")
    parser.add_argument("-o", "--output", default="data/processed/model_comparison.csv", help="CSV comparatif")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--contamination", type=float, default=0.05, help="Proportion attendue d'anomalies")
    parser.add_argument("--random-state", type=int, default=42, help="Graine aleatoire")
    parser.add_argument("--label-column", default="", help="Colonne optionnelle de verite terrain")
    parser.add_argument("--max-categorical-unique", type=int, default=100, help="Limite one-hot par colonne")
    args = parser.parse_args(argv)

    output = compare_models(
        input_csv=args.input,
        output_csv=args.output,
        sep=args.sep,
        contamination=args.contamination,
        random_state=args.random_state,
        label_column=args.label_column,
        max_categorical_unique=args.max_categorical_unique,
    )
    print(f"Comparaison modeles: {output}")
    print(pd.read_csv(output, sep=args.sep).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
