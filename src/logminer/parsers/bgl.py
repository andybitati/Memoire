# Source Generated with Decompyle++
# File: bgl.cpython-311.pyc (Python 3.11)

'''Parseur BGL (BlueGene/L).'''
import re
import os
from datetime import datetime, timezone
from typing import Iterable
from common import clean, make_pbar, norm_sev
from writer import emit
BGL_HDR_RE = re.compile('^\\s*[-*]?\\s*(?P<eid>\\d+)\\s+\\d{4}\\.\\d{2}\\.\\d{2}\\s+\\S+\\s+(?P<ts>\\d{4}-\\d{2}-\\d{2}-\\d{2}\\.\\d{2}\\.\\d{2}\\.\\d+)\\s+(?P<src>\\S+)\\s+RAS\\s+(?P<subsys>\\S+)\\s+(?P<sev>[A-Za-z]+)\\s+(?P<rest>.*)$')
BGL_FALLBACK = re.compile('^(?P<ts>\\d{4}-\\d{2}-\\d{2}-\\d{2}\\.\\d{2}\\.\\d{2}\\.\\d+)\\s+(?:(?P<src>\\S+)\\s+)?RAS\\s+(?P<subsys>\\S+)\\s+(?P<sev>[A-Za-z]+)\\s+(?P<rest>.*)$')

def iso_from_bgl_ts(ts = None):
    
    try:
        return datetime.strptime(ts, '%Y-%m-%d-%H.%M.%S.%f').replace(tzinfo = timezone.utc).isoformat()
    except Exception:
        return ''



class Parser:
    subtype = 'bgl'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


