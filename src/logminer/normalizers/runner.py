"""Chaine de normalisation appliquee avant l'ecriture CSV."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

try:
    from .base import BaseNormalizer
    from .categorizer import CategorizerNormalizer
    from .default import DefaultNormalizer
except ImportError:
    from base import BaseNormalizer
    from categorizer import CategorizerNormalizer
    from default import DefaultNormalizer


_DEFAULTS: List[BaseNormalizer] | None = None


def get_default_normalizers() -> List[BaseNormalizer]:
    """Retourne les normaliseurs standards dans un ordre stable."""

    global _DEFAULTS
    if _DEFAULTS is None:
        _DEFAULTS = [DefaultNormalizer(), CategorizerNormalizer()]
    return _DEFAULTS


def normalize_event(
    event: Dict[str, Any] | None,
    normalizers: Iterable[BaseNormalizer] | None = None,
) -> Dict[str, Any]:
    """Applique les normaliseurs et preserve l'evenement en cas d'erreur."""

    normalized = dict(event or {})
    chain = list(normalizers) if normalizers is not None else get_default_normalizers()

    for normalizer in chain:
        try:
            normalized = normalizer.normalize(normalized)
        except Exception:
            continue

    return normalized
