# Source Generated with Decompyle++
# File: cef_leef.cpython-311.pyc (Python 3.11)

'''Parseur CEF & LEEF (Common/Log Event Format) — streaming, tolérant.'''
import os
import re
import sys
from datetime import datetime, timezone
from common import clean, make_pbar, norm_sev
from writer import emit
CEF_HDR = re.compile('^CEF:(?P<v>\\d+)\\|(?P<vendor>[^|]*)\\|(?P<product>[^|]*)\\|(?P<dver>[^|]*)\\|(?P<sig>[^|]*)\\|(?P<name>[^|]*)\\|(?P<sev>[^|]*)(?:\\|(?P<ext>.*))?$')
LEEF_HDR = re.compile('^LEEF:(?P<v>\\d+)\\|(?P<vendor>[^|]*)\\|(?P<product>[^|]*)\\|(?P<dver>[^|]*)\\|(?P<sig>[^\\t|]*)(?:\\t(?P<ext>.*))?$')

def _unescape_cef(s = None):
    return s.replace('\\n', '\n').replace('\\r', '\r').replace('\\=', '=').replace('\\|', '|').replace('\\\\', '\\')


def _parse_kv_ext(ext = None, sep = None):
    """
    Analyse k=v k2=v2 ... (CEF: sep=' ', LEEF: sep='\\t').
    Respecte les '=' échappés côté CEF.
    """
    out = { }
    if not ext:
        return out
    if None == '\t':
        parts = ext.split('\t')
        for p in parts:
            if '=' in p:
                (k, v) = p.split('=', 1)
                out[k.strip()] = v.strip()
            return out
            (buf, key, val, in_key) = ('', '', '', True)
            parts = []
            for ch in ext:
                if ch == ' ' and buf and buf.endswith('\\\\') and '=' not in buf:
                    parts.append(buf)
                    buf = ''
                    continue
                buf += ch
                if buf:
                    parts.append(buf)
# WARNING: Decompyle incomplete


def _pick_ts(d = None):
    '''
    CEF/LEEF timestamps:
    - rt: epoch ms
    - end/start: epoch ms
    - devTime / devtimeFormat (varie)
    '''
    for k in ('rt', 'end', 'start'):
        if k in d:
            s = d[k].strip()
            val = int(s)
            if val > 0x2540BE400:
                val = val / 1000
            dt = datetime.utcfromtimestamp(val).replace(tzinfo = timezone.utc)
            
            return None, dt.isoformat()
        except Exception:
            continue
        for None in ('dvcpdt', 'devTime', 'deviceTime', 'endTime', 'startTime'):
            if k in d:
                d[k].replace(' ', 'T') = None
                dt = datetime.fromisoformat(txt.replace('Z', '+00:00'))
                
                return None, dt if dt.tzinfo else dt.replace(tzinfo = timezone.utc).isoformat()
            except Exception:
                continue
        return ''


class Parser:
    subtype = 'cef_leef'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


