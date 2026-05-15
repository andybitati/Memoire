"""Pipeline de pretraitement Logminer.

Role dans le memoire:
    Ce fichier represente le coeur de l'agent "collecte + parsing". Il prend
    des journaux bruts, detecte leur format, appelle le parseur specialise, puis
    produit un CSV normalise. Ce CSV devient l'entree des agents de
    normalisation, detection d'anomalies, correlation et visualisation.

Flux:
    fichier/dossier -> detection du type -> parseur -> csv_writer.emit() -> CSV
"""

from __future__ import annotations

import importlib
import os
import sys
from typing import Dict, Iterable, List, Optional, Type


# Dossier contenant ce fichier. On l'ajoute a sys.path pour conserver le style
# d'import absolu des fichiers recuperes (`from writer import emit`,
# `from common import clean`, etc.) meme quand le script est lance depuis un
# autre repertoire.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Le projet recupere contient un dossier `io`, mais Python possede deja un
# module standard nomme `io`. Pour eviter ce conflit, on ajoute explicitement le
# dossier local `io` au path et on importe `csv_writer` par son nom de fichier.
IO_DIR = os.path.join(BASE_DIR, "io")
if IO_DIR not in sys.path:
    sys.path.insert(0, IO_DIR)

from csv_writer import open_writer


class UnknownParser:
    """Parseur de secours integre au pipeline.

    Il conserve les lignes brutes quand le parseur specialise n'est pas encore
    repare. C'est important pour le memoire: meme si un format n'est pas reconnu,
    on garde de la matiere exploitable pour l'analyse et l'amelioration future.
    """

    subtype = "unknown"

    def parse(
        self,
        path: str,
        writer,
        sep: str = ";",
        split_rows: int = 0,
        progress_every: int = 0,
        use_tqdm: bool = False,
        debug: bool = False,
    ) -> None:
        from csv_writer import emit

        with open(path, "rb") as f_in:
            for lineno, raw in enumerate(f_in, start=1):
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue
                emit(
                    writer,
                    {
                        "dataset": "unknown",
                        "subtype": self.subtype,
                        "filepath": path,
                        "lineno": lineno,
                        "message": line,
                    },
                )


# Association stable entre un type logique de journal et le module du parseur.
# On evite d'importer tous les parseurs au demarrage, car certains fichiers
# recuperes depuis .pyc peuvent encore etre incomplets. Le chargement se fait
# seulement quand le type est detecte.
PARSER_MODULES: Dict[str, str] = {
    "hdfs": "parsers.hdfs",
    "bgl": "parsers.bgl",
    "tcpdump_text": "parsers.tcpdump_text",
    "praudit_text": "parsers.praudit_text",
    "pcap": "parsers.pcap",
    "praudit_xml": "parsers.praudit_xml",
    "syslog": "parsers.syslog",
    "apache": "parsers.apache",
    "jsonl": "parsers.jsonl",
    "cef_leef": "parsers.cef_leef",
    "win_event": "parsers.windows_event",
    "cloudtrail": "parsers.cloudtrail",
    "unknown": "parsers.unknown",
}


def _ensure_dir(path: str) -> None:
    """Cree un dossier s'il n'existe pas deja."""

    os.makedirs(path, exist_ok=True)


def iter_files(input_path: str) -> Iterable[str]:
    """Retourne tous les fichiers a traiter.

    Args:
        input_path: Chemin vers un fichier unique ou un dossier.

    Yields:
        Chemins de fichiers, en parcours recursif si `input_path` est un dossier.
    """

    if os.path.isfile(input_path):
        yield input_path
        return

    if not os.path.isdir(input_path):
        raise FileNotFoundError(f"Chemin introuvable: {input_path}")

    for root, _, files in os.walk(input_path):
        for name in sorted(files):
            # On ignore les fichiers caches/temporaires qui ne sont pas des logs.
            if name.startswith(".") or name.endswith((".tmp", ".temp", ".pyc")):
                continue
            yield os.path.join(root, name)


def _sample_text(path: str, max_bytes: int = 8192) -> str:
    """Lit un petit echantillon texte pour la detection heuristique."""

    try:
        with open(path, "rb") as f_in:
            return f_in.read(max_bytes).decode("utf-8", errors="ignore")
    except OSError:
        return ""


def _looks_like_pcap(path: str) -> bool:
    """Detecte rapidement les signatures binaires pcap/pcapng."""

    try:
        with open(path, "rb") as f_in:
            sig = f_in.read(4)
    except OSError:
        return False

    # pcapng: 0A 0D 0D 0A. pcap classique: magic en big/little endian.
    if sig == b"\x0a\x0d\x0d\x0a":
        return True
    return int.from_bytes(sig, "big") in (0xA1B2C3D4, 0xA1B23C4D) or int.from_bytes(
        sig, "little"
    ) in (0xA1B2C3D4, 0xA1B23C4D)


def detect_kind(path: str) -> str:
    """Detecte le type de journal a partir de l'extension et du contenu.

    Cette detection est volontairement conservatrice: si aucun format n'est
    reconnu, on renvoie `unknown` pour conserver les lignes brutes au lieu de
    perdre des donnees.
    """

    low = path.lower()

    # Les extensions connues sont les signaux les plus fiables.
    if low.endswith(".evtx"):
        return "win_event"
    if low.endswith(".pcap") or low.endswith(".pcapng") or _looks_like_pcap(path):
        return "pcap"
    if low.endswith(".tcpdump") or low.endswith(".tcpdump.txt") or low.endswith(".dump"):
        return "tcpdump_text"

    sample = _sample_text(path)
    stripped = sample.lstrip()
    first_lines = [line.strip() for line in sample.splitlines()[:40] if line.strip()]

    # Exports XML Windows Event ou praudit XML.
    if stripped.startswith("<"):
        if "<Event" in sample and "<System" in sample:
            return "win_event"
        return "praudit_xml"

    # JSONL applicatif ou AWS CloudTrail.
    if stripped.startswith("{"):
        if '"Records"' in sample or ('"eventTime"' in sample and '"eventSource"' in sample):
            return "cloudtrail"
        return "jsonl"

    # Formats securite/SIEM.
    if any(line.startswith(("CEF:", "LEEF:")) for line in first_lines):
        return "cef_leef"

    # Web access logs Apache/Nginx.
    if any('"' in line and ("GET " in line or "POST " in line or "HTTP/" in line) for line in first_lines):
        return "apache"

    # Jeux de donnees publics cites dans le memoire.
    if any(" RAS " in line and "-" in line for line in first_lines):
        return "bgl"
    if any("hdfs" in line.lower() or "blk_" in line.lower() for line in first_lines):
        return "hdfs"

    # Syslog Linux/RFC: mois court ou timestamp ISO au debut.
    months = ("Jan ", "Feb ", "Mar ", "Apr ", "May ", "Jun ", "Jul ", "Aug ", "Sep ", "Oct ", "Nov ", "Dec ")
    if any(line.startswith(months) for line in first_lines):
        return "syslog"
    if any(len(line) > 19 and line[4:5] == "-" and line[13:14] == ":" for line in first_lines):
        return "syslog"

    return "unknown"


def _load_parser(kind: str) -> Type:
    """Charge la classe Parser du module correspondant au type detecte."""

    module_name = PARSER_MODULES.get(kind, PARSER_MODULES["unknown"])

    try:
        module = importlib.import_module(module_name)
        return module.Parser
    except Exception as exc:
        # En phase de recuperation, certains parseurs peuvent etre incomplets.
        # On bascule alors vers `unknown` pour ne pas interrompre tout le batch.
        if kind != "unknown":
            print(f"[pipeline] Parseur '{kind}' indisponible ({exc}); fallback unknown.")
        return UnknownParser


def _default_output_name(input_path: str, out_name: str) -> str:
    """Construit un nom de CSV stable."""

    return out_name or f"{os.path.basename(os.path.abspath(input_path))}.csv"


def run_pipeline(
    input_path: str,
    out_dir: str = "Dataset_csv",
    out_name: str = "dataset.csv",
    sep: str = ";",
    split_rows: int = 0,
    progress_every: int = 0,
    use_tqdm: bool = False,
    debug: bool = False,
) -> List[str]:
    """Traite un fichier ou dossier de logs et produit un ou plusieurs CSV.

    Args:
        input_path: Fichier ou dossier contenant les journaux bruts.
        out_dir: Dossier de sortie.
        out_name: Nom du CSV principal.
        sep: Separateur CSV.
        split_rows: Nombre maximal de lignes par CSV. `0` desactive la rotation.
        progress_every: Frequence d'affichage de progression transmise aux parseurs.
        use_tqdm: Active les barres de progression si les parseurs les supportent.
        debug: Affiche les details utiles lors de la detection/parsing.

    Returns:
        Liste des chemins CSV produits.
    """

    _ensure_dir(out_dir)

    output_csv = os.path.join(out_dir, _default_output_name(input_path, out_name))
    produced: List[str] = []

    part = 0
    rows_in_part = 0
    f_out, writer, out_path = open_writer(output_csv, part=part, sep=sep)
    produced.append(out_path)

    def rotate_if_needed() -> None:
        """Ouvre un nouveau CSV si `split_rows` est atteint."""

        nonlocal part, rows_in_part, f_out, writer, out_path

        if not split_rows or rows_in_part < split_rows:
            return

        f_out.close()
        part += 1
        rows_in_part = 0
        f_out, writer, out_path = open_writer(output_csv, part=part, sep=sep)
        produced.append(out_path)

    try:
        for path in iter_files(input_path):
            # On evite de reprocesser les CSV deja produits dans le meme dossier.
            if os.path.abspath(path) in {os.path.abspath(p) for p in produced}:
                continue

            kind = detect_kind(path)
            parser_cls = _load_parser(kind)
            parser = parser_cls()

            if debug:
                print(f"[pipeline] {path} -> {kind}")

            # Les parseurs recuperes suivent la signature commune suivante.
            # Ils ecrivent eux-memes via `emit(writer, base)`.
            before = getattr(writer, "line_num", 0)
            parser.parse(
                path=path,
                writer=writer,
                sep=sep,
                split_rows=split_rows,
                progress_every=progress_every,
                use_tqdm=use_tqdm,
                debug=debug,
            )

            # DictWriter expose `line_num` via son fichier sous-jacent seulement
            # dans certains cas; on garde donc une estimation minimale. La
            # rotation precise dependra des parseurs complets.
            after = getattr(writer, "line_num", before)
            rows_in_part += max(0, after - before)
            rotate_if_needed()
    finally:
        f_out.close()

    return produced
