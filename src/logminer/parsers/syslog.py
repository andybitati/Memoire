# Source Generated with Decompyle++
# File: syslog.cpython-311.pyc (Python 3.11)

'''Parseur Syslog (RFC3164/5424 — heuristique).'''
import os
import re
import sys
from datetime import datetime, timezone
from typing import Iterable
from common import clean, make_pbar
from writer import emit
SYSLOG1 = re.compile('^(?P<mon>[A-Z][a-z]{2})\\s+(?P<day>\\d{1,2})\\s+(?P<time>\\d\\d:\\d\\d:\\d\\d)\\s+(?P<host>\\S+)\\s+(?P<proc>[^:]+):\\s*(?P<msg>.*)$')
SYSLOG2 = re.compile('^(?P<ts>\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d+)?(?:Z|[+-]\\d{2}:\\d{2})?)\\s+(?P<host>\\S+)\\s+(?P<app>\\S+)\\s+(?P<msg>.*)$')
MONTHS = enumerate([
    'Jan',
    'Feb',
    'Mar',
    'Apr',
    'May',
    'Jun',
    'Jul',
    'Aug',
    'Sep',
    'Oct',
    'Nov',
    'Dec'])()

class Parser:
    subtype = 'syslog'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


