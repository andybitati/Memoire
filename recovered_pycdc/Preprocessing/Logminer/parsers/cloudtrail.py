# Source Generated with Decompyle++
# File: cloudtrail.cpython-311.pyc (Python 3.11)

'''Parseur AWS CloudTrail (JSON / JSON.GZ).'''
import os
import sys
import json
import gzip
from common import clean, make_pbar
from writer import emit

def _open_maybe_gz(path = None):
    return gzip.open(path, 'rt', encoding = 'utf-8', errors = 'ignore') if path.lower().endswith('.gz') else open(path, 'r', encoding = 'utf-8', errors = 'ignore')


def _emit_record(writer, path, rec):
