# Source Generated with Decompyle++
# File: runner.cpython-311.pyc (Python 3.11)

"""Runner de normalisation.

Les parseurs appellent actuellement `emit(writer, base)` directement.
Pour éviter de modifier tous les parseurs, on applique ici une chaîne de
normalizers juste avant l'écriture CSV.

Cette chaîne est volontairement simple:
- DefaultNormalizer: harmonise les niveaux de sévérité
- CategorizerNormalizer: ajoute `category/subcategory`

Les agents IA pourront ajouter d'autres normalizers (enrichissement, mapping MITRE, etc.).
"""
from __future__ import annotations
from typing import Dict, Any, List
from default import DefaultNormalizer
from categorizer import CategorizerNormalizer
from base import BaseNormalizer
_DEFAULTS: 'List[BaseNormalizer] | None' = None

def get_default_normalizers():
    '''Retourne une liste singleton de normalizers par défaut.'''
    pass
# WARNING: Decompyle incomplete


def normalize_event(event = None, normalizers = None):
    """Applique les normalizers (non destructifs) et retourne l'événement."""
    if not normalizers:
        pass
    chain = get_default_normalizers()
    for n in chain:
        event = n.normalize(event)
        except Exception:
            continue
        return event

