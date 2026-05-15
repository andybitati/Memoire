# Source Generated with Decompyle++
# File: jsonl.cpython-311.pyc (Python 3.11)

'''Parseur JSON Lines (1 JSON par ligne).'''
import os
import json
import sys
from typing import Iterable
from common import clean, make_pbar, norm_sev
from writer import emit

class Parser:
    subtype = 'jsonl'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


