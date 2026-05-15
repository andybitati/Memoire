# Source Generated with Decompyle++
# File: tcpdump_text.cpython-311.pyc (Python 3.11)

'''Parseur tcpdump texte.'''
import re
import os
import sys
from datetime import datetime, timezone
from typing import Iterable, Tuple
from common import clean, make_pbar
from writer import emit
TS_FULL_RE = re.compile('^(?P<ts>\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}\\.\\d+)\\s+(?P<rest>.*)$')
TS_SHORT_RE = re.compile('^(?P<ts>\\d{2}:\\d{2}:\\d{2}\\.\\d+)\\s+(?P<rest>.*)$')
PROTO_RE = re.compile('^(?P<proto>\\S+)\\s+(?P<rest>.*)$')
IP4_EP_RE = re.compile('(?P<sip>\\d{1,3}(?:\\.\\d{1,3}){3})(?:\\.(?P<sport>\\d+))?\\s*>\\s*(?P<dip>\\d{1,3}(?:\\.\\d{1,3}){3})(?:\\.(?P<dport>\\d+))?:\\s*(?P<msg>.*)$')
IP6_EP_RE = re.compile('(?P<sip>\\[[0-9a-fA-F:]+\\]|[0-9a-fA-F:]+)(?:\\.(?P<sport>\\d+))?\\s*>\\s*(?P<dip>\\[[0-9a-fA-F:]+\\]|[0-9a-fA-F:]+)(?:\\.(?P<dport>\\d+))?:\\s*(?P<msg>.*)$')
FLAGS_RE = re.compile('Flags\\s+\\[([A-Za-z\\.]+)\\]')
LEN_RE = re.compile('(?:length|len)\\s+(\\d+)')

def parse_line(line = None):
    ts_iso = ''
    rest1 = line
    m = TS_FULL_RE.match(line)
    if m:
        ts = datetime.strptime(m.group('ts'), '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo = timezone.utc)
        ts_iso = ts.isoformat()
        rest1 = m.group('rest')
    else:
        m2 = TS_SHORT_RE.match(line)
        if m2:
            today = datetime.utcnow().date()
            ts = datetime.strptime(f'''{today} {m2.group('ts')}''', '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo = timezone.utc)
            ts_iso = ts.isoformat()
            rest1 = m2.group('rest')
    proto = ''
    rest2 = rest1
    m = PROTO_RE.match(rest1)
    if m:
        proto = m.group('proto')
        rest2 = m.group('rest')
    sip = ''
    sport = ''
    dip = ''
    dport = ''
    msg = rest2
    if not IP4_EP_RE.search(rest2):
        ep = IP6_EP_RE.search(rest2)
        if ep:
            sip = ep.group('sip').strip('[]')
            dip = ep.group('dip').strip('[]')
            if not ep.group('sport'):
                sport = ''
                if not ep.group('dport'):
                    dport = ''
                    msg = ep.group('msg')
    flags = FLAGS_RE.search(msg).group(1) if FLAGS_RE.search(msg) else ''
    length = LEN_RE.search(msg).group(1) if LEN_RE.search(msg) else ''
    return (ts_iso, proto, sip, sport, dip, dport, flags, clean(msg))


class Parser:
    subtype = 'tcpdump_text'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


