# Source Generated with Decompyle++
# File: __init__.cpython-311.pyc (Python 3.11)

"""Normalizers.

Les parseurs Logminer produisent des événements proches du schéma unifié.
Cette couche applique des transformations *non destructives* avant l'export CSV:
- harmonisation de sévérité
- catégorisation (point 4)

Les futurs agents IA pourront être branchés ici sous forme de normalizers supplémentaires.
"""
from base import BaseNormalizer
from default import DefaultNormalizer
from categorizer import CategorizerNormalizer
from runner import normalize_event, get_default_normalizers
