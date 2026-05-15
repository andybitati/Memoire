# Source Generated with Decompyle++
# File: apache.cpython-311.pyc (Python 3.11)

'''Parseur Apache/Nginx access (Combined + JSON access).'''
import os
import re
import json
import sys
from typing import Iterable
from common import make_pbar
from writer import emit
APACHE_COMBINED = re.compile('^(?P<ip>\\S+)\\s+\\S+\\s+\\S+\\s+\\[(?P<dt>[^\\]]+)\\]\\s+"(?P<met>[A-Z]+)\\s+(?P<url>[^"]*)"\\s+(?P<st>\\d{3})\\s+(?P<bytes>\\S+)\\s+"(?P<ref>[^"]*)"\\s+"(?P<ua>[^"]*)"')

def parse_apache_dt(s = None):
    
    try:
        datetime = datetime
        timezone = timezone
        import datetime
        dt = datetime.strptime(s, '%d/%b/%Y:%H:%M:%S %z')
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return ''



class Parser:
    subtype = 'apache'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


