"""Compatibilite avec l'ancien module `writer`.

Les parseurs recuperes depuis les `.pyc` font souvent:

    from writer import emit

Le vrai code d'ecriture vit dans `io/csv_writer.py`. Comme `io` est aussi le
nom d'un module standard Python, on ajoute explicitement ce dossier au path puis
on reexporte `open_writer` et `emit`.
"""

from __future__ import annotations

import os
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IO_DIR = os.path.join(BASE_DIR, "io")

if IO_DIR not in sys.path:
    sys.path.insert(0, IO_DIR)

from csv_writer import emit, open_writer

__all__ = ["emit", "open_writer"]
