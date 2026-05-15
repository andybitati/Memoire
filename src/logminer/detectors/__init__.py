"""Detecteurs de formats de logs.

Ce package expose les fonctions publiques du detecteur principal afin que les
autres modules puissent utiliser simplement:

    from detectors import detect_kind

ou:

    from detectors.file_detector import detect_kind
"""

from .file_detector import detect_file, detect_kind, iter_files

__all__ = ["detect_file", "detect_kind", "iter_files"]
