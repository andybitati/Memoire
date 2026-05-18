"""Classes de base pour la normalisation semantique des evenements."""

from __future__ import annotations

from typing import Any, Dict


class BaseNormalizer:
    """Interface minimale commune a tous les normaliseurs."""

    name = "base"

    def normalize(self, event: Dict[str, Any] | None) -> Dict[str, Any]:
        return dict(event or {})
