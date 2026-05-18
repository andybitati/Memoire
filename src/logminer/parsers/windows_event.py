"""Parseur Windows Event pour exports XML et fichiers EVTX.

Role dans le memoire:
    Les journaux Windows font partie des sources systemes a normaliser pour la
    detection d'anomalies. Ce parseur extrait les champs essentiels d'un Event
    Log et les transforme dans le schema commun Logminer.

Formats acceptes:
    - `.xml`: export Windows Event Viewer ou XML contenant des balises `<Event>`.
    - `.evtx`: fichier natif Windows Event Log, si la dependance `python-evtx`
      est installee (`pip install python-evtx`).

Champs principaux:
    timestamp_iso, host, event, severity, source, user, message.
"""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Dict, Iterable, Iterator, Optional

from writer import emit


def clean(value: str) -> str:
    """Nettoie un message sans dependre de `common.py`.

    Le fichier `common.py` recupere depuis bytecode contient encore des zones
    imparfaites; on garde donc ici une version locale minimale et fiable.
    """

    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())


try:
    # Dependances optionnelles: elles ne sont necessaires que pour les .evtx.
    from Evtx.Evtx import Evtx
    from Evtx.Views import evtx_record_xml_view

    HAVE_EVTX = True
except Exception:
    Evtx = None
    evtx_record_xml_view = None
    HAVE_EVTX = False


WINDOWS_LEVELS = {
    # Mapping Microsoft classique:
    # https://learn.microsoft.com/windows/win32/eventlog/event-types
    "0": "",
    "1": "CRITICAL",
    "2": "ERROR",
    "3": "WARNING",
    "4": "INFO",
    "5": "VERBOSE",
}


class Parser:
    """Parseur conforme a l'interface commune des parseurs Logminer."""

    subtype = "win_event"

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
        """Parcourt un fichier Windows Event et ecrit chaque evenement en CSV."""

        low = path.lower()

        if low.endswith(".evtx"):
            if not HAVE_EVTX:
                raise RuntimeError(
                    "Lecture .evtx impossible: installez la dependance python-evtx "
                    "ou exportez le journal Windows en XML."
                )
            iterator = _iter_evtx_events(path)
        else:
            iterator = _iter_xml_events(path)

        for recno, ev in enumerate(iterator, start=1):
            try:
                row = _parse_event_elem(ev, path, recno)
                emit(writer, row)
            except Exception as exc:
                # Un evenement mal forme ne doit pas interrompre tout le batch.
                if debug:
                    print(f"[windows_event] evenement ignore dans {path}: {exc}", file=sys.stderr)


def _strip_ns(tag: str) -> str:
    """Supprime le namespace XML pour comparer facilement les noms de balises."""

    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def _children(elem: ET.Element, name: str) -> Iterator[ET.Element]:
    """Itere sur les enfants directs dont le nom local correspond."""

    for child in list(elem):
        if _strip_ns(child.tag) == name:
            yield child


def _first_child(elem: Optional[ET.Element], name: str) -> Optional[ET.Element]:
    """Retourne le premier enfant direct d'un nom donne."""

    if elem is None:
        return None
    return next(_children(elem, name), None)


def _text_or_attr(elem: Optional[ET.Element], child_name: str, attr: Optional[str] = None) -> str:
    """Lit soit le texte d'un enfant, soit l'attribut de cet enfant.

    Exemple:
        `_text_or_attr(system, "Provider", "Name")` renvoie Provider/@Name.
        `_text_or_attr(system, "Computer")` renvoie le texte de Computer.
    """

    child = _first_child(elem, child_name)
    if child is None:
        return ""
    if attr:
        return child.attrib.get(attr, "")
    return (child.text or "").strip()


def _iso(value: str) -> str:
    """Convertit un timestamp Windows/ISO en ISO UTC quand possible."""

    if not value:
        return ""

    try:
        # Windows Event Log utilise souvent Z pour UTC.
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return ""


def _level_to_severity(level: str) -> str:
    """Transforme le niveau Windows numerique en severite lisible."""

    return WINDOWS_LEVELS.get(str(level).strip(), str(level or "").strip().upper())


def _event_data_to_message(ev: ET.Element) -> str:
    """Construit un message lisible depuis EventData/UserData/RenderingInfo."""

    parts = []

    # EventData contient souvent des balises <Data Name="...">valeur</Data>.
    event_data = _first_child(ev, "EventData")
    if event_data is not None:
        for data in _children(event_data, "Data"):
            name = data.attrib.get("Name", "")
            value = (data.text or "").strip()
            if name and value:
                parts.append(f"{name}={value}")
            elif value:
                parts.append(value)

    # UserData varie selon les providers; on capture les feuilles textuelles.
    user_data = _first_child(ev, "UserData")
    if user_data is not None:
        for node in user_data.iter():
            if node is user_data:
                continue
            text = (node.text or "").strip()
            if text:
                parts.append(f"{_strip_ns(node.tag)}={text}")

    # Certains exports contiennent un message deja rendu.
    rendering = _first_child(ev, "RenderingInfo")
    message_node = _first_child(rendering, "Message")
    if message_node is not None and message_node.text:
        parts.append(message_node.text.strip())

    return clean(" | ".join(parts))


def _parse_event_elem(ev: ET.Element, path: str, recno: int) -> Dict[str, str]:
    """Transforme une balise `<Event>` en evenement normalise Logminer."""

    system = _first_child(ev, "System")

    provider = _text_or_attr(system, "Provider", "Name")
    event_id = _text_or_attr(system, "EventID")
    level = _text_or_attr(system, "Level")
    computer = _text_or_attr(system, "Computer")
    process_id = _text_or_attr(system, "Execution", "ProcessID")
    thread_id = _text_or_attr(system, "Execution", "ThreadID")
    user_id = _text_or_attr(system, "Security", "UserID")

    time_node = _first_child(system, "TimeCreated")
    timestamp = ""
    if time_node is not None:
        timestamp = _iso(time_node.attrib.get("SystemTime", ""))

    message = _event_data_to_message(ev)

    return {
        "dataset": "windows_event",
        "subtype": Parser.subtype,
        "filepath": path,
        "recno": recno,
        "timestamp_iso": timestamp,
        "severity": _level_to_severity(level),
        "event": event_id,
        "source": provider,
        "component": provider,
        "host": computer,
        "pid": process_id,
        "tid": thread_id,
        "user": user_id,
        "message": message,
    }


def _iter_xml_events(path: str) -> Iterator[ET.Element]:
    """Lit un export XML Windows Event sans charger inutilement les gros fichiers."""

    # iterparse permet de traiter de gros exports. Quand une balise Event est
    # terminee, on la renvoie puis on libere sa memoire.
    for _, elem in ET.iterparse(path, events=("end",)):
        if _strip_ns(elem.tag) == "Event":
            yield elem
            elem.clear()


def _iter_evtx_events(path: str) -> Iterator[ET.Element]:
    """Convertit les records EVTX en elements XML exploitables."""

    assert Evtx is not None and evtx_record_xml_view is not None

    with Evtx(path) as log:
        for record in log.records():
            try:
                xml_record = evtx_record_xml_view(record)
                yield ET.fromstring(xml_record)
            except Exception:
                # Les exports reels peuvent contenir quelques records que
                # python-evtx ne sait pas rendre; on garde le reste du journal.
                continue
