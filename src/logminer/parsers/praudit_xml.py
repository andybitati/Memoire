# Source Generated with Decompyle++
# File: praudit_xml.cpython-311.pyc (Python 3.11)

'''Parseur praudit XML (OpenBSM, streaming via iterparse).'''

ElementTree
from typing import Iterable
import xml.etree.ElementTree, etree
from common import clean, to_iso, parse_epoch, DATETIME_RE, IP4_RE, IP6_RE, PORT_BOTH_RE, make_pbar
from writer import emit

class Parser:
    subtype = 'praudit_xml'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


