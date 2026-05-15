"""Detection du format des journaux pour Logminer.

Ce module choisit le parseur a utiliser avant l'etape de normalisation CSV.
Dans le memoire, il correspond a la partie "identifier, categoriser et
structurer les differents types de journaux systemes et reseaux".

La strategie est volontairement robuste:
    1. regarder les signatures binaires fiables, par exemple pcap/pcapng;
    2. regarder l'extension quand elle donne une information forte;
    3. lire un petit echantillon de lignes;
    4. appliquer des heuristiques simples par format;
    5. retourner `unknown` si rien n'est reconnu, afin de ne jamais perdre le log.
"""

from __future__ import annotations

import json
import os
import re
from typing import Iterable, Iterator, List, Tuple


# Magic numbers pcap classiques, dans les deux endianness.
PCAP_MAGIC = (0xA1B2C3D4, 0xA1B23C4D)

# Magic pcapng: 0A 0D 0D 0A.
PCAPNG_MAGIC = b"\x0a\x0d\x0d\x0a"

# Les formats textuels sont detectes sur un petit extrait, pas sur tout le
# fichier. Cela evite de charger des journaux volumineux en memoire.
DEFAULT_SAMPLE_LINES = 40


def sniff_pcap(path: str) -> bool:
    """Retourne True si le fichier ressemble a une capture pcap/pcapng."""

    try:
        with open(path, "rb") as f_in:
            sig = f_in.read(4)
    except OSError:
        return False

    if sig == PCAPNG_MAGIC:
        return True

    if len(sig) != 4:
        return False

    big = int.from_bytes(sig, "big")
    little = int.from_bytes(sig, "little")
    return big in PCAP_MAGIC or little in PCAP_MAGIC


def sniff_xml(path: str) -> bool:
    """Retourne True si le fichier commence comme du XML."""

    try:
        with open(path, "rb") as f_in:
            head = f_in.read(256)
    except OSError:
        return False

    return head.lstrip().startswith(b"<")


def sample_lines(path: str, n: int = DEFAULT_SAMPLE_LINES) -> List[str]:
    """Lit les `n` premieres lignes d'un fichier texte.

    Les octets invalides sont ignores afin de supporter des logs reels parfois
    melanges, tronques ou exportes depuis differents systemes.
    """

    lines: List[str] = []
    try:
        with open(path, "rb") as f_in:
            for _ in range(n):
                raw = f_in.readline()
                if not raw:
                    break
                lines.append(raw.decode("utf-8", errors="ignore").rstrip("\r\n"))
    except OSError:
        return []

    return lines


def _joined(lines: Iterable[str]) -> str:
    """Concatene un echantillon pour les recherches multi-lignes."""

    return "\n".join(lines)


def looks_like_cef_leef(lines: List[str]) -> bool:
    """Detecte les formats CEF/LEEF utilises par SIEM/IDS/IPS."""

    return any(line.startswith(("CEF:", "LEEF:")) for line in lines)


def looks_like_win_xml(lines: List[str]) -> bool:
    """Detecte un export XML Windows Event Log."""

    text = _joined(lines)
    return "<Event" in text and "<System" in text and ("<EventID" in text or "<Provider" in text)


def looks_like_cloudtrail(lines: List[str]) -> bool:
    """Detecte AWS CloudTrail au format JSON/JSONL."""

    text = _joined(lines[:10])
    if '"Records"' in text and ("eventSource" in text or "eventTime" in text):
        return True

    return any('"eventTime"' in line and '"eventSource"' in line for line in lines[:20])


def looks_like_bgl(lines: List[str]) -> bool:
    """Detecte les logs BGL/BlueGene-L cites dans le memoire."""

    # Exemples BGL: timestamp avec tirets, source, mot-cle RAS, severite.
    bgl_re = re.compile(
        r"\d{4}-\d{2}-\d{2}-\d{2}\.\d{2}\.\d{2}\.\d+\s+\S+\s+RAS\s+\S+\s+\w+",
        re.I,
    )
    return any(bool(bgl_re.search(line)) or " RAS " in line for line in lines)


def looks_like_hdfs(lines: List[str]) -> bool:
    """Detecte HDFS, dataset public important pour les tests d'anomalies."""

    hdfs_long = re.compile(r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[,.]\d+")
    hdfs_short = re.compile(r"^\d{6}\s+\d{6}\s+\d+\s+\w+")

    for line in lines:
        low = line.lower()
        if "blk_" in low or "hdfs" in low or "dfs." in low:
            return True
        if hdfs_long.match(line) and (" INFO " in line or " WARN " in line or " ERROR " in line):
            return True
        if hdfs_short.match(line):
            return True
    return False


def looks_like_praudit_text(lines: List[str]) -> bool:
    """Detecte grossierement les sorties `praudit` texte."""

    keywords = ("header,", "subject,", "return,", "path,", "exec_args,")
    return any(any(key in line for key in keywords) for line in lines)


def looks_like_tcpdump_text(lines: List[str]) -> bool:
    """Detecte une sortie tcpdump texte."""

    tcpdump_re = re.compile(
        r"(\d{2}:\d{2}:\d{2}\.\d+|\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+).*?\s>\s.*?:"
    )
    return any(bool(tcpdump_re.search(line)) or " Flags [" in line for line in lines)


def looks_like_syslog(lines: List[str]) -> bool:
    """Detecte syslog RFC3164/RFC5424 de maniere heuristique."""

    rfc3164 = re.compile(r"^[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\S+")
    rfc5424 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}")
    return any(rfc3164.match(line) or rfc5424.match(line) for line in lines)


def looks_like_apache(lines: List[str]) -> bool:
    """Detecte les access logs Apache/Nginx."""

    apache_re = re.compile(
        r'^\S+\s+\S+\s+\S+\s+\[[^\]]+\]\s+"(?:GET|POST|PUT|DELETE|HEAD|OPTIONS|PATCH)\s+[^"]+"\s+\d{3}'
    )
    return any(bool(apache_re.match(line)) or " HTTP/" in line for line in lines)


def looks_like_jsonl(lines: List[str]) -> bool:
    """Detecte un fichier JSON ligne par ligne."""

    checked = 0
    valid = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        checked += 1
        if not (stripped.startswith("{") and stripped.endswith("}")):
            continue
        try:
            json.loads(stripped)
            valid += 1
        except json.JSONDecodeError:
            pass

    # Une seule ligne JSON valide suffit pour les petits exports; sur plusieurs
    # lignes, on demande une majorite pour eviter les faux positifs.
    return valid >= 1 and valid >= max(1, checked // 2)


def looks_like_win_event(lines: List[str]) -> bool:
    """Detecte les exports Windows Event non strictement XML."""

    keys = ("EventID", "Provider", "Level", "Computer", "TimeCreated")
    return any(sum(1 for key in keys if key in line) >= 2 for line in lines)


def detect_kind(path: str) -> str:
    """Detecte le type d'un fichier unique.

    Returns:
        Une cle compatible avec `registry.PARSERS` et `pipeline.PARSER_MODULES`.
    """

    low = path.lower()

    # Extensions ou signatures binaires tres fiables.
    if low.endswith(".evtx"):
        return "win_event"
    if low.endswith((".pcap", ".pcapng")) or sniff_pcap(path):
        return "pcap"
    if low.endswith((".tcpdump", ".tcpdump.txt", ".dump")):
        return "tcpdump_text"

    lines = sample_lines(path)

    # XML: Windows Event ou audit XML.
    if sniff_xml(path):
        if looks_like_win_xml(lines):
            return "win_event"
        return "praudit_xml"

    # Ordre important: CloudTrail est aussi JSON, donc on le teste avant JSONL.
    if looks_like_cloudtrail(lines):
        return "cloudtrail"
    if looks_like_jsonl(lines):
        return "jsonl"

    # Formats securite/applicatifs/reseau.
    if looks_like_cef_leef(lines):
        return "cef_leef"
    if looks_like_apache(lines):
        return "apache"
    if looks_like_tcpdump_text(lines):
        return "tcpdump_text"
    if looks_like_praudit_text(lines):
        return "praudit_text"

    # Jeux de donnees publics de reference dans le memoire.
    if looks_like_bgl(lines):
        return "bgl"
    if looks_like_hdfs(lines):
        return "hdfs"

    # Logs systemes generiques.
    if looks_like_syslog(lines):
        return "syslog"
    if looks_like_win_event(lines):
        return "win_event"

    return "unknown"


def iter_files(input_path: str) -> Iterator[str]:
    """Itere sur tous les fichiers d'un chemin.

    Si `input_path` est un fichier, il est renvoye directement. Si c'est un
    dossier, le parcours est recursif et ignore quelques fichiers temporaires.
    """

    if os.path.isfile(input_path):
        yield input_path
        return

    if not os.path.isdir(input_path):
        raise FileNotFoundError(f"Chemin introuvable: {input_path}")

    for root, _, files in os.walk(input_path):
        for name in sorted(files):
            if name.startswith(".") or name.endswith((".tmp", ".temp", ".pyc")):
                continue
            yield os.path.join(root, name)


def detect_file(input_path: str) -> Tuple[str, str]:
    """Retourne `(kind, path)` pour le premier fichier plausible.

    Cette fonction conserve l'API d'origine du module recupere. Elle est utile
    pour tester rapidement un dossier sans lancer tout le pipeline.
    """

    for path in iter_files(input_path):
        return detect_kind(path), path

    raise SystemExit("Aucun fichier exploitable trouve.")
