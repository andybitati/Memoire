# Source Generated with Decompyle++
# File: base.cpython-311.pyc (Python 3.11)

"""Normalisation sémantique.

Aujourd'hui, les parseurs Logminer produisent déjà des événements proches du schéma unifié.
Ce package formalise une étape optionnelle de normalisation, utile pour:
- harmoniser les niveaux de sévérité (ex: HTTP->WARNING/ERROR)
- enrichir les champs (ex: géoloc IP, mapping user, etc.)
- préparer des 'views' spécifiques ML/SIEM

Les agents IA pourront brancher ici des normaliseurs spécialisés.
"""
from typing import Dict, Any

class BaseNormalizer:
    name: str = 'base'
    
    def normalize(self = None, event = None):
        return event


