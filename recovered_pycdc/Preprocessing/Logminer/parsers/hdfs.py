# Source Generated with Decompyle++
# File: hdfs.cpython-311.pyc (Python 3.11)

'''Parseur HDFS (formats long et court).'''
import re
import os
import sys
from datetime import datetime, timezone
from typing import Optional, Iterable
from common import clean, to_iso, make_pbar, norm_sev
from writer import emit
TS_FORMATS = [
    '%Y-%m-%d %H:%M:%S,%f',
    '%Y-%m-%d %H:%M:%S.%f',
    '%Y-%m-%d %H:%M:%S']

def parse_dt(s = None):
    s = s.strip()
# WARNING: Decompyle incomplete

HDFS_SHORT_RE = re.compile('^(?P<d>\\d{6})\\s+(?P<t>\\d{6})\\s+\\d+\\s+(?P<lev>[A-Za-z]+)\\s+(?P<src>[^:]+):\\s+(?P<msg>.*)$')

def to_iso_yyMMdd_HHmmss(d = None, t = None):
    y = int(d[0:2])
    m = int(d[2:4])
    dd = int(d[4:6])
    hh = int(t[0:2])
    mm = int(t[2:4])
    ss = int(t[4:6])
    year = 2000 + y if y < 70 else 1900 + y
    return datetime(year, m, dd, hh, mm, ss, tzinfo = timezone.utc).isoformat()

HDFS_RE = re.compile('^(?P<ts>\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}(?:[.,]\\d{3,6})?)\\s+(?P<level>[A-Za-z]+)\\s+(?P<src>[A-Za-z0-9_.$\\-]+(?:\\([^)]+\\))?)\\s*(?::|\\s-\\s)\\s*(?P<msg>.*)$')

def parse_line(line = None):
    m = HDFS_SHORT_RE.match(line)
    if m:
        return (to_iso_yyMMdd_HHmmss(m.group('d'), m.group('t')), m.group('src'), norm_sev(m.group('lev')), m.group('msg'))
    m = None.match(line)
    if m:
        return (to_iso(parse_dt(m.group('ts'))), m.group('src'), norm_sev(m.group('level')), m.group('msg').strip())
    pm = None.match('^\\s*(\\d{4}-\\d{2}-\\d{2}\\s+\\d{2}:\\d{2}:\\d{2}(?:[.,]\\d{3,6})?)\\s+(.*)$', line)
    if not pm:
        return None
    ts = None(parse_dt(pm.group(1)))
    rest = pm.group(2)
    m2 = re.match('^(?P<lev>[A-Za-z]{3,7})\\b\\s*(?P<rest>.*)$', rest)
    sev = norm_sev(m2.group('lev')) if m2 else ''
    rest = m2.group('rest') if m2 else rest
    m3 = re.match('^(?P<src>[^:-]+?)\\s*(?::|\\s-\\s)\\s*(?P<msg>.*)$', rest)
    if m3:
        return (ts, m3.group('src').strip(), sev, m3.group('msg').strip())
    return (None, '', sev, rest.strip())


class Parser:
    subtype = 'hdfs'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


