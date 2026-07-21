"""Templateur Drain-like leger pour journaux systeme.

Ce module n'implemente pas toute la bibliotheque Drain originale. Il reprend
son principe central utile au prototype: regrouper des messages proches dans
des templates, puis remplacer les tokens variables par `<*>`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd


NUMBER_RE = re.compile(r"\b(?:0x[0-9a-fA-F]+|\d+(?:\.\d+)*)\b")
BLOCK_RE = re.compile(r"\bblk_-?\d+\b", re.IGNORECASE)
IP_RE = re.compile(r"\b\d{1,3}(?:\.\d{1,3}){3}\b")
PATH_RE = re.compile(r"(?:[A-Za-z]:)?[/\\][^\s]+")
WHITESPACE_RE = re.compile(r"\s+")
WILDCARD = "<*>"


@dataclass
class _Cluster:
    template_tokens: list[str]
    count: int = 0


def tokenize_message(message: str) -> list[str]:
    """Tokenise un message apres normalisation des valeurs tres variables."""

    text = str(message or "").strip().lower()
    text = BLOCK_RE.sub("blk_<*>", text)
    text = IP_RE.sub(WILDCARD, text)
    text = PATH_RE.sub(WILDCARD, text)
    text = NUMBER_RE.sub(WILDCARD, text)
    text = WHITESPACE_RE.sub(" ", text)
    return text.split() if text else []


def _similarity(template: list[str], tokens: list[str]) -> float:
    if len(template) != len(tokens):
        return 0.0
    if not template:
        return 1.0
    matches = 0
    for left, right in zip(template, tokens):
        if left == right or left == WILDCARD:
            matches += 1
    return matches / len(template)


def _merge_template(template: list[str], tokens: list[str]) -> list[str]:
    return [left if left == right else WILDCARD for left, right in zip(template, tokens)]


def drain_like_templates(
    messages: pd.Series,
    *,
    similarity_threshold: float = 0.5,
    max_clusters_per_length: int = 512,
) -> pd.DataFrame:
    """Assigne un identifiant et un template Drain-like a chaque message.

    Les clusters sont separes par longueur de message, comme dans Drain. Pour
    rester sobre, on borne le nombre de clusters par longueur; au-dela, le
    meilleur cluster existant est force meme si le seuil n'est pas atteint.
    """

    threshold = min(max(float(similarity_threshold), 0.0), 1.0)
    clusters_by_length: dict[int, list[_Cluster]] = {}
    cluster_ids_by_length: dict[int, list[int]] = {}
    next_id = 1
    assigned_ids: list[int] = []
    assigned_templates: list[str] = []

    for message in messages.fillna("").astype(str):
        tokens = tokenize_message(message)
        length = len(tokens)
        clusters = clusters_by_length.setdefault(length, [])
        cluster_ids = cluster_ids_by_length.setdefault(length, [])

        best_index = -1
        best_score = -1.0
        for index, cluster in enumerate(clusters):
            score = _similarity(cluster.template_tokens, tokens)
            if score > best_score:
                best_index = index
                best_score = score

        if best_index >= 0 and (best_score >= threshold or len(clusters) >= max_clusters_per_length):
            cluster = clusters[best_index]
            cluster.template_tokens = _merge_template(cluster.template_tokens, tokens)
            cluster.count += 1
            cluster_id = cluster_ids[best_index]
        else:
            cluster = _Cluster(template_tokens=list(tokens), count=1)
            clusters.append(cluster)
            cluster_id = next_id
            cluster_ids.append(cluster_id)
            next_id += 1

        assigned_ids.append(cluster_id)
        assigned_templates.append(" ".join(cluster.template_tokens))

    return pd.DataFrame(
        {
            "drain_event_id": assigned_ids,
            "drain_template": assigned_templates,
        },
        index=messages.index,
    )


def drain3_templates(messages: pd.Series) -> pd.DataFrame:
    """Assigne les templates avec la librairie `drain3` si elle est installee."""

    try:
        from drain3 import TemplateMiner
        from drain3.template_miner_config import TemplateMinerConfig
    except ImportError as exc:
        raise RuntimeError("La librairie drain3 n'est pas installee") from exc

    config = TemplateMinerConfig()
    miner = TemplateMiner(config=config)
    assigned_ids: list[int] = []
    assigned_templates: list[str] = []

    for message in messages.fillna("").astype(str):
        result = miner.add_log_message(message)
        assigned_ids.append(int(result.get("cluster_id", 0) or 0))
        assigned_templates.append(str(result.get("template_mined", "")))

    return pd.DataFrame(
        {
            "drain_event_id": assigned_ids,
            "drain_template": assigned_templates,
        },
        index=messages.index,
    )


def build_templates(
    messages: pd.Series,
    *,
    method: str = "drain3",
    similarity_threshold: float = 0.5,
    allow_fallback: bool = True,
) -> pd.DataFrame:
    """Construit les templates avec Drain3 officiel ou fallback Drain-like."""

    selected = str(method or "drain3").lower()
    if selected == "drain3":
        try:
            frame = drain3_templates(messages)
            frame["drain_template_method"] = "drain3"
            return frame
        except RuntimeError:
            if not allow_fallback:
                raise
            frame = drain_like_templates(messages, similarity_threshold=similarity_threshold)
            frame["drain_template_method"] = "drain_like_fallback"
            return frame
    if selected in {"drain", "drain_like"}:
        frame = drain_like_templates(messages, similarity_threshold=similarity_threshold)
        frame["drain_template_method"] = "drain_like"
        return frame
    raise ValueError(f"Template method inconnue: {method}")
