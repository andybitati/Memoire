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
import tracemalloc
import warnings
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Callable, Dict, Optional

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
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
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
DetectorTask = tuple[Callable[..., ModelResult], tuple[object, ...]]

AUTO_LABEL_COLUMNS = [
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

ADAPTABILITY_SCORE = {
    "rule_baseline": 0.55,
    "static_thresholds": 0.35,
    "z_score": 0.45,
    "iqr": 0.45,
    "histogram": 0.55,
    "entropy": 0.60,
    "isolation_forest": 0.85,
    "kmeans": 0.70,
    "one_class_svm": 0.65,
    "local_outlier_factor": 0.65,
    "autoencoder_mlp": 0.80,
    "lstm_tensorflow": 0.85,
    "lstm_pytorch": 0.85,
    "ensemble_global": 0.75,
    "ensemble_selected": 0.80,
}


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


def _run_with_resource_tracking(runner, *args) -> ModelResult:
    """Execute un detecteur et mesure le pic memoire Python.

    La duree reste mesuree dans chaque detecteur pour garder les notes locales.
    `tracemalloc` donne ici une estimation utile pour comparer les methodes
    entre elles pendant l'objectif 2. Ce n'est pas une mesure OS parfaite, mais
    elle suffit pour une grille experimentale reproductible.
    """

    tracemalloc.start()
    try:
        result = runner(*args)
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    result["memory_peak_mb"] = round(peak / (1024 * 1024), 4)
    return result


def _run_without_tracemalloc_tracking(runner, *args) -> ModelResult:
    """Execute un detecteur dans un lot parallele.

    `tracemalloc` est global au processus Python: si plusieurs detecteurs
    tournent en meme temps, son pic memoire n'est plus attribuable proprement a
    un modele. En mode parallele, on conserve donc une estimation locale basee
    sur les objets de sortie, suffisante pour comparer sans bloquer les threads.
    """

    result = runner(*args)
    labels = pd.Series(result.get("labels", []))
    scores = pd.Series(result.get("scores", []))
    result["memory_peak_mb"] = round((labels.memory_usage(deep=True) + scores.memory_usage(deep=True)) / (1024 * 1024), 4)
    return result


def _run_detector_tasks(tasks: list[DetectorTask], parallel_workers: int) -> list[ModelResult]:
    """Execute les detecteurs independants en conservant leur ordre logique."""

    workers = max(1, int(parallel_workers))
    if workers == 1 or len(tasks) <= 1:
        return [_run_with_resource_tracking(runner, *args) for runner, args in tasks]

    ordered: list[ModelResult | None] = [None] * len(tasks)
    max_workers = min(workers, len(tasks))
    with ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="logminer-model") as executor:
        futures = {
            executor.submit(_run_without_tracemalloc_tracking, runner, *args): index
            for index, (runner, args) in enumerate(tasks)
        }
        for future in as_completed(futures):
            ordered[futures[future]] = future.result()

    return [result for result in ordered if result is not None]


def _score_direction(result: ModelResult) -> str:
    """Indique si un score fort ou faible represente une anomalie."""

    if result["model"] in {"isolation_forest", "one_class_svm", "local_outlier_factor"}:
        return "lower"
    return "higher"


def _anomaly_strength(result: ModelResult) -> pd.Series:
    """Transforme les scores heterogenes en force d'anomalie 0..1."""

    scores = pd.Series(result["scores"]).astype(float)
    if scores.nunique(dropna=False) <= 1:
        return pd.Series(0.0, index=scores.index)
    if _score_direction(result) == "lower":
        scores = -scores
    return scores.rank(method="average", pct=True).fillna(0.0)


def _shannon_entropy(value: str) -> float:
    """Entropie de Shannon d'une chaine, utile pour reperer messages atypiques."""

    text = str(value or "")
    if not text:
        return 0.0
    counts = pd.Series(list(text)).value_counts(normalize=True)
    return float(-(counts * np.log2(counts)).sum())


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


def run_static_thresholds(events: pd.DataFrame, features: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Detection traditionnelle par seuils simples.

    Cette methode represente les approches classiques: severite elevee, statut
    HTTP critique, message contenant erreur/echec/refus, ou taille/message
    anormalement long. Elle est moins flexible qu'un modele IA, mais tres
    explicable dans le memoire.
    """

    started = time.perf_counter()
    severity_score = features.get("severity_score", pd.Series(0, index=events.index)).astype(float)
    http_status = pd.to_numeric(events.get("http_status", pd.Series("", index=events.index)), errors="coerce").fillna(0)
    message = events.get("message", pd.Series("", index=events.index)).astype(str)
    message_len = features.get("message_len", pd.Series(0, index=events.index)).astype(float)
    length_threshold = float(message_len.quantile(0.95)) if len(message_len) else 0.0

    scores = pd.Series(0.0, index=events.index)
    scores += (severity_score >= 4).astype(float) * 1.0
    scores += (http_status >= 500).astype(float) * 0.8
    scores += (http_status.isin([401, 403])).astype(float) * 0.6
    scores += message.str.contains("error|failed|failure|denied|attack|malware|exception", case=False, regex=True).astype(float) * 0.8
    scores += (message_len >= length_threshold).astype(float) * 0.3

    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "static_thresholds",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Traditionnel: seuils severite/http/message",
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


def run_entropy(events: pd.DataFrame, contamination: float, random_state: int) -> ModelResult:
    """Detection par entropie et surprise categorielle.

    Les approches par entropie cherchent des distributions inhabituelles. Ici,
    on combine l'entropie du message avec la surprise des champs categoriels
    principaux. Un message tres aleatoire ou une combinaison rare obtient un
    score plus eleve.
    """

    started = time.perf_counter()
    message = events.get("message", pd.Series("", index=events.index)).astype(str)
    entropy = message.map(_shannon_entropy)

    surprise = pd.Series(0.0, index=events.index)
    columns = [column for column in ("event", "source", "host", "severity", "category") if column in events]
    for column in columns:
        values = events[column].fillna("").astype(str)
        frequencies = values.value_counts(dropna=False, normalize=True)
        surprise += values.map(lambda value: -np.log2(max(float(frequencies.get(value, 0.0)), 1e-12)))

    if columns:
        surprise = surprise / len(columns)
    scores = entropy + surprise
    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": "entropy",
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "notes": "Traditionnel: entropie message + surprise categorielle",
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


def run_ensemble(
    results: list[ModelResult],
    contamination: float,
    model_name: str = "ensemble_global",
    include_models: set[str] | None = None,
) -> ModelResult:
    """Agrege plusieurs detecteurs en score global.

    Le score global moyenne les rangs d'anomalie des detecteurs individuels. Il
    respecte l'idee de pipeline multi-modeles: chaque methode vote selon sa
    vision de l'anomalie, puis l'ensemble retient les evenements les plus
    consensuellement suspects.
    """

    started = time.perf_counter()
    usable = [
        result
        for result in results
        if result["model"] not in {"ensemble_global", "ensemble_selected"}
        and (include_models is None or str(result["model"]) in include_models)
        and not str(result.get("notes", "")).lower().startswith("ignore:")
    ]
    if not usable:
        index = pd.Series(results[0]["scores"]).index if results else pd.RangeIndex(0)
        scores = pd.Series(0.0, index=index)
    else:
        strengths = [_anomaly_strength(result) for result in usable]
        scores = pd.concat(strengths, axis=1).mean(axis=1)

    labels = _top_by_score(scores, contamination, lower_is_more_anomalous=False)
    return {
        "model": model_name,
        "labels": labels,
        "scores": scores,
        "duration_sec": time.perf_counter() - started,
        "memory_peak_mb": round(scores.memory_usage(deep=True) / (1024 * 1024), 4),
        "notes": f"Pipeline ensemble: moyenne de {len(usable)} detecteurs",
    }


def _detect_label_column(events: pd.DataFrame, label_column: str = "") -> str:
    """Retourne la colonne de verite terrain a utiliser pour la validation.

    Les datasets publics ne nomment pas toujours le label de la meme maniere:
    HDFS utilise souvent `Label`, UNSW-NB15 utilise parfois `label` ou
    `attack_cat`, et nos CSV prepares utilisent `label`. Cette detection evite
    de devoir memoriser chaque nom de colonne a chaque execution.
    """

    if label_column and label_column in events.columns:
        return label_column

    for candidate in AUTO_LABEL_COLUMNS:
        if candidate in events.columns:
            return candidate

    return ""


def _labels_from_column(events: pd.DataFrame, label_column: str) -> pd.Series | None:
    selected_column = _detect_label_column(events, label_column)
    if not selected_column:
        return None

    values = events[selected_column].astype(str).str.strip().str.lower()
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
    }
    negative_values = {"0", "false", "no", "n", "normal", "benign", "none", "-"}

    numeric_values = pd.to_numeric(values, errors="coerce")
    labels = values.isin(positive_values).astype(int)
    labels = labels.mask(values.isin(negative_values), 0)
    labels = labels.mask(numeric_values.notna(), (numeric_values.fillna(0) != 0).astype(int))
    return labels.astype(int)


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
        "memory_peak_mb": round(float(result.get("memory_peak_mb", 0.0)), 4),
        "adaptability_score": ADAPTABILITY_SCORE.get(str(result["model"]), 0.5),
        "notes": result["notes"],
    }

    if truth is not None:
        true_positive = int(((truth == 1) & (labels == 1)).sum())
        false_positive = int(((truth == 0) & (labels == 1)).sum())
        false_negative = int(((truth == 1) & (labels == 0)).sum())
        true_negative = int(((truth == 0) & (labels == 0)).sum())
        specificity = true_negative / max(true_negative + false_positive, 1)

        row["precision"] = round(float(precision_score(truth, labels, zero_division=0)), 6)
        row["recall"] = round(float(recall_score(truth, labels, zero_division=0)), 6)
        row["f1"] = round(float(f1_score(truth, labels, zero_division=0)), 6)
        row["accuracy"] = round(float(accuracy_score(truth, labels)), 6)
        row["specificity"] = round(float(specificity), 6)
        row["tp"] = true_positive
        row["fp"] = false_positive
        row["fn"] = false_negative
        row["tn"] = true_negative

    return row


def _add_selection_scores(summary: list[dict[str, object]], has_truth: bool) -> pd.DataFrame:
    """Ajoute un score multicritere pour choisir le modele final.

    Le score respecte les criteres de l'objectif 2:
    precision/F1 si labels disponibles, temps de traitement, consommation
    memoire et capacite d'adaptation. Les poids restent volontairement simples
    et explicites pour le memoire.
    """

    frame = pd.DataFrame(summary)
    if frame.empty:
        return frame

    duration = pd.to_numeric(frame["duration_sec"], errors="coerce").fillna(0)
    memory = pd.to_numeric(frame["memory_peak_mb"], errors="coerce").fillna(0)
    adaptability = pd.to_numeric(frame["adaptability_score"], errors="coerce").fillna(0.5)

    duration_score = 1 - (duration / max(float(duration.max()), 1e-9))
    memory_score = 1 - (memory / max(float(memory.max()), 1e-9))

    if has_truth and "f1" in frame.columns:
        quality = pd.to_numeric(frame["f1"], errors="coerce").fillna(0)
    else:
        # Sans labels, on utilise un proxy prudent: proximite avec la baseline
        # explicable et taux d'anomalies non nul.
        quality = pd.to_numeric(frame["overlap_rate"], errors="coerce").fillna(0)

    frame["time_score"] = duration_score.round(6)
    frame["memory_score"] = memory_score.round(6)
    frame["selection_score"] = (
        quality * 0.45
        + duration_score * 0.20
        + memory_score * 0.15
        + adaptability * 0.20
    ).round(6)
    return frame


def compare_models(
    input_csv: str | Path,
    output_csv: str | Path = "data/processed/model_comparison.csv",
    sep: str = ";",
    contamination: float | str = 0.05,
    random_state: int = 42,
    label_column: str = "",
    max_categorical_unique: int = 100,
    parallel_workers: int = 1,
) -> str:
    """Execute les modeles retenus pour l'objectif 2 et ecrit un tableau CSV."""

    events = load_events(input_csv, sep=sep)
    if events.empty:
        raise ValueError(f"Aucun evenement a comparer dans {input_csv}")

    truth = _labels_from_column(events, label_column)
    if isinstance(contamination, str) and contamination.lower() == "auto":
        if truth is None:
            raise ValueError("--contamination auto demande une colonne de label detectable")
        effective_contamination = max(float(truth.mean()), 1 / max(len(truth), 1))
    else:
        effective_contamination = float(contamination)

    features = build_feature_frame(events, max_categorical_unique=max_categorical_unique)
    if features.empty:
        raise ValueError("Impossible de construire des features ML depuis le CSV fourni")

    results: list[ModelResult] = []
    baseline_result = _run_with_resource_tracking(run_baseline, events, effective_contamination, random_state)
    results.append(baseline_result)

    # Methodes traditionnelles et statistiques. Elles servent de repere
    # explicable avant les modeles IA: seuils, entropie, rarete, distance a la
    # moyenne ou sortie des quartiles.
    independent_tasks: list[DetectorTask] = [
        (run_static_thresholds, (events, features, effective_contamination, random_state)),
        (run_z_score, (features, effective_contamination, random_state)),
        (run_iqr, (features, effective_contamination, random_state)),
        (run_histogram, (events, effective_contamination, random_state)),
        (run_entropy, (events, effective_contamination, random_state)),
        # Modeles IA non supervises. Ils exploitent la meme matrice numerique
        # pour rendre la comparaison reproductible entre approches.
        (run_isolation_forest, (features, effective_contamination, random_state)),
        (run_kmeans, (features, effective_contamination, random_state)),
        (run_one_class_svm, (features, effective_contamination, random_state)),
        (run_lof, (features, effective_contamination, random_state)),
        (run_autoencoder, (features, effective_contamination, random_state)),
        (run_lstm, (events, effective_contamination, random_state)),
    ]
    results.extend(_run_detector_tasks(independent_tasks, parallel_workers))

    # Pipeline global: agrege les signaux des detecteurs precedents pour tester
    # si la combinaison ameliore la precision globale.
    selected_models = {
        "rule_baseline",
        "static_thresholds",
        "histogram",
        "entropy",
        "isolation_forest",
        "autoencoder_mlp",
        "lstm_tensorflow",
        "lstm_pytorch",
    }
    results.append(run_ensemble(results, effective_contamination, "ensemble_global"))
    results.append(run_ensemble(results, effective_contamination, "ensemble_selected", selected_models))

    baseline_labels = pd.Series(baseline_result["labels"]).astype(int)
    summary = [_summarize(result, len(events), baseline_labels, truth) for result in results]
    output_frame = _add_selection_scores(summary, has_truth=truth is not None)

    output_path = Path(output_csv)
    if output_path.parent:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_frame.to_csv(output_path, sep=sep, index=False, encoding="utf-8-sig")
    return str(output_path)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Compare plusieurs detecteurs d'anomalies legers")
    parser.add_argument("-i", "--input", required=True, help="CSV normalise Logminer")
    parser.add_argument("-o", "--output", default="data/processed/model_comparison.csv", help="CSV comparatif")
    parser.add_argument("--sep", default=";", help="Separateur CSV")
    parser.add_argument("--contamination", default="0.05", help="Proportion attendue d'anomalies, ou 'auto' avec labels")
    parser.add_argument("--random-state", type=int, default=42, help="Graine aleatoire")
    parser.add_argument("--label-column", default="", help="Colonne optionnelle de verite terrain")
    parser.add_argument("--max-categorical-unique", type=int, default=100, help="Limite one-hot par colonne")
    parser.add_argument(
        "--parallel-workers",
        type=int,
        default=1,
        help="Nombre de detecteurs independants executes en parallele (1 = sequentiel)",
    )
    args = parser.parse_args(argv)

    output = compare_models(
        input_csv=args.input,
        output_csv=args.output,
        sep=args.sep,
        contamination=args.contamination,
        random_state=args.random_state,
        label_column=args.label_column,
        max_categorical_unique=args.max_categorical_unique,
        parallel_workers=args.parallel_workers,
    )
    print(f"Comparaison modeles: {output}")
    print(pd.read_csv(output, sep=args.sep).to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
