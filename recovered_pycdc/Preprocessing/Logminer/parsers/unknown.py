# Source Generated with Decompyle++
# File: unknown.cpython-311.pyc (Python 3.11)

"""
Parseur fallback (unknown): ne casse jamais le pipeline.
- Tente de reconnaître le format à partir des premières lignes
- Sinon, écrit au moins l'événement brut en 'message'
"""
from __future__ import annotations
from typing import Optional
import os
from writer import emit

class Parser:
    subtype = 'unknown'
    
    def parse(self, path, writer, sep, split_rows, progress_every, use_tqdm, debug = (';', 0, 0, False, False)):
        
        try:
            f = open(path, 'rb')
            raw = f.read(4096)
            
            try:
                None(None, None)
            with None:
                if not None:
                    
                    try:
                        
                        try:
                            sample = raw.decode('utf-8', errors = 'ignore').splitlines()
                        except Exception:
                            e = None
                            if debug:
                                print(f'''[unknown] Cannot read {path}: {e}''')
                            e = None
                            del e
                            return None
                            e = None
                            del e

                        for i, line in enumerate(sample[:200]):
                            if not line.strip():
                                continue
                            base = {
                                'timestamp': '',
                                'host': os.path.basename(path),
                                'proc': 'unknown',
                                'pid': '',
                                'msg': line.strip(),
                                'severity': '',
                                'subtype': self.subtype,
                                'ip': '' }
                            emit(writer, base)
                            return None





