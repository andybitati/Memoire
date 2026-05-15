"""Ecriture CSV normalisee pour Logminer.

Ce module est volontairement simple: tous les parseurs lui envoient un
dictionnaire `base`, et lui garantit que la ligne finale respecte le schema
commun defini dans `schema.columns.COLUMNS`.

Dans le cadre du memoire, ce fichier correspond a la sortie de l'agent de
pretraitement: les logs heterogenes deviennent un tableau propre, stable et
exploitable par les agents IA, le dashboard ou les modeles de detection.
"""

from __future__ import annotations

import csv
import os
from typing import Any, Dict, Tuple

from schema.columns import COLUMNS


try:
    # La chaine de normalisation ajoute/standardise notamment severity,
    # category et subcategory. Comme certains fichiers recuperes depuis .pyc
    # peuvent encore etre incomplets, on protege l'import pour que l'ecriture
    # CSV reste utilisable meme si les normalizers doivent etre repares plus tard.
    from normalizers.runner import normalize_event
except Exception:

    def normalize_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback minimal quand les normalizers ne sont pas disponibles."""

        return event


def open_writer(base_out: str, part: int = 0, sep: str = ";") -> Tuple[Any, csv.DictWriter, str]:
    """Ouvre un fichier CSV et ecrit l'en-tete normalise.

    Args:
        base_out: Chemin du CSV principal, par exemple `Dataset_csv/dataset.csv`.
        part: Numero de partie. `0` signifie fichier principal; `1`, `2`, ...
            creent `dataset_part001.csv`, `dataset_part002.csv`, etc.
        sep: Separateur CSV. Le point-virgule est pratique avec Excel en
            environnement francophone.

    Returns:
        Tuple `(file_handle, writer, path)` afin que le pipeline puisse fermer
        proprement le fichier et connaitre le chemin produit.
    """

    # Si `split_rows` est active dans le pipeline, plusieurs fichiers doivent
    # etre produits sans perdre l'extension originale.
    if part == 0:
        path = base_out
    else:
        root, ext = os.path.splitext(base_out)
        path = f"{root}_part{part:03d}{ext or '.csv'}"

    # On cree le dossier de sortie ici aussi pour rendre le writer autonome.
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    # utf-8-sig ajoute un BOM compatible Excel, sans gener les outils Python.
    f_out = open(path, "w", newline="", encoding="utf-8-sig")

    # DictWriter force l'ordre des colonnes, ce qui est essentiel pour les
    # notebooks, les modeles ML et les comparaisons experimentales du memoire.
    writer = csv.DictWriter(
        f_out,
        fieldnames=COLUMNS,
        delimiter=sep,
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL,
        extrasaction="ignore",
    )
    writer.writeheader()
    return f_out, writer, path


def emit(writer: csv.DictWriter, base: Dict[str, Any] | None) -> None:
    """Ecrit une ligne en garantissant toutes les colonnes du schema.

    Les parseurs peuvent envoyer seulement les champs qu'ils connaissent. Cette
    fonction complete automatiquement les champs manquants avec une chaine vide.
    C'est ce qui permet de melanger syslog, Windows Event, Apache, HDFS, BGL,
    tcpdump, etc. dans une structure commune.
    """

    if writer is None:
        raise ValueError("emit() a besoin d'un csv.DictWriter valide")

    # Copie defensive: le normalizer peut modifier le dictionnaire.
    event = normalize_event(dict(base or {}))

    # Valeurs par defaut: toutes les colonnes existent toujours.
    row = {column: "" for column in COLUMNS}

    # On ne conserve que les champs prevus par le schema, pour eviter que des
    # clefs propres a un parseur cassent le CSV.
    for key, value in event.items():
        if key in row:
            row[key] = "" if value is None else value

    writer.writerow(row)
