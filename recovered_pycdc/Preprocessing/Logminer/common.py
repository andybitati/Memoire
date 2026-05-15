# Source Generated with Decompyle++
# File: common.cpython-311.pyc (Python 3.11)

'''Outils communs : nettoyage, timestamps, tqdm, normalisation.'''
import re
from datetime import datetime, timezone
from typing import Optional

def clean(s = None):
    '''Compacte les espaces et supprime CR/LF.'''
    if not s:
        return ''
    return None.sub('\\s+', ' ', s.replace('\r', ' ').replace('\n', ' ')).strip()


def to_iso(dt = None):
    return dt.isoformat() if dt else ''


def parse_epoch(sec = None, subsec = None):
    '''Epoch secondes + sous-secondes (ns/us).'''
    
    try:
        s = int(sec)
        ns = int(subsec) if subsec else 0
        us = ns // 1000 if ns > 999999 else ns
        return datetime.fromtimestamp(s, tz = timezone.utc).replace(microsecond = us)
    except Exception:
        return None


DATETIME_RE = re.compile('\\d{4}-\\d{2}-\\d{2}[ T]\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{1,9})?')
EPOCH_RE = re.compile('(?P<sec>\\d{10})(?:\\.(?P<sub>\\d{1,9}))?')
IP4_RE = re.compile('\\b\\d{1,3}(?:\\.\\d{1,3}){3}\\b')
IP6_RE = re.compile('\\b[0-9a-fA-F:]{2,}\\b')
PORT_BOTH_RE = re.compile('(?:^|[^A-Za-z])(src|sport|s_port)\\D*(?P<s>\\d+)|(?:^|[^A-Za-z])(dst|dport|d_port)\\D*(?P<d>\\d+)', re.I)
ALIASES_SEV = {
    'WARNING': 'WARN',
    'WARN': 'WARN',
    'ERR': 'ERROR',
    'CRIT': 'CRITICAL',
    'SEVERE': 'CRITICAL',
    'INF': 'INFO',
    'DBG': 'DEBUG' }

def norm_sev(sev = None):
    if not sev:
        return ''
    up = None.upper()
    return ALIASES_SEV.get(up, up)


try:
    from tqdm import tqdm
except Exception:
    tqdm = None


def make_pbar(total = None, desc = None, unit = None):
    '''Crée une barre tqdm optionnelle.
       total=None -> total=0 pour éviter bool(None) indéfini.'''
    if not tqdm:
        return None
# WARNING: Decompyle incomplete

