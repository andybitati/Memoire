# Source Generated with Decompyle++
# File: detectors.cpython-311.pyc (Python 3.11)

'''Détection du type de fichier (format) pour dispatcher vers le bon parseur.'''
import os
import re
import json
from typing import Tuple, List

def sniff_pcap(path = None):
    
    try:
        f = open(path, 'rb')
        sig = f.read(4)
        
        try:
            None(None, None)
        with None:
            if not None:
                
                try:
                    
                    try:
                        if sig == b'\n\r\r\n':
                            return True
                        bval = None.from_bytes(sig, 'big')
                        lval = int.from_bytes(sig, 'little')
                        if not bval in (0xA1B2C3D4, 0xA1B23C4D):
                            return lval in (0xA1B2C3D4, 0xA1B23C4D)
                        except Exception:
                            return False






def sniff_xml(path = None):
    
    try:
        f = open(path, 'rb')
        head = f.read(128)
        
        try:
            None(None, None)
        with None:
            if not None:
                
                try:
                    
                    try:
                        return head.lstrip().startswith(b'<')
                    except Exception:
                        return False






def sample_lines(path = None, n = None):
    out = []
    
    try:
        fb = open(path, 'rb')
        for _ in range(n):
            raw = fb.readline()
            if not raw:
                pass
            else:
                out.append(raw.decode('utf-8', errors = 'ignore').rstrip('\n'))
            
            try:
                None(None, None)
            with None:
                if not None:
                    
                    try:
                        
                        try:
                            pass
                        except Exception:
                            pass

                        return out





def looks_like_cef_leef(lines):
    return (lambda .0: pass# WARNING: Decompyle incomplete
)(lines())


def looks_like_win_xml(lines):
    pass
# WARNING: Decompyle incomplete


def looks_like_cloudtrail(lines):
    
    try:
        s = ''.join(lines[:5]).strip()
        if s.startswith('{') and '"Records"' in s:
            return True
    except Exception:
        pass

    for l in lines[:20]:
        if '"eventTime"' in l and '"eventSource"' in l:
            return True
        return False


def looks_like_bgl(lines = None):
    pass
# WARNING: Decompyle incomplete


def looks_like_hdfs(lines = None):
    pass
# WARNING: Decompyle incomplete


def looks_like_praudit_text(lines = None):
    return (lambda .0: pass# WARNING: Decompyle incomplete
)(lines())


def looks_like_tcpdump_text(lines = None):
    return (lambda .0: pass# WARNING: Decompyle incomplete
)(lines())


def detect_file(input_path = None):
    """Retourne (kind, path) pour le premier fichier plausible.
       kind ∈ {'pcap','praudit_xml','praudit_text','bgl','hdfs','tcpdump_text','unknown'}"""
    if os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for fn in files:
                p = os.path.join(root, fn)
                if sniff_pcap(p):
                    
                    
                    return None, None, ('pcap', p)
                if None(p):
                    
                    
                    return None, None, ('praudit_xml', p)
                for root, _, files in os.walk(input_path):
                    for fn in files:
                        p = os.path.join(root, fn)
                        lines = sample_lines(p)
                        if looks_like_bgl(lines):
                            
                            
                            return None, None, ('bgl', p)
                        if None(lines):
                            
                            
                            return None, None, ('hdfs', p)
                        if None(lines):
                            
                            
                            return None, None, ('praudit_text', p)
                        if None(lines):
                            
                            
                            return None, None, ('tcpdump_text', p)
                        for root, _, files in os.walk(input_path):
                            for fn in files:
                                
                                
                                return None, None, ('unknown', os.path.join(root, fn))
                                raise SystemExit('Dossier vide.')
                                if sniff_pcap(path):
                                    return ('pcap', path)
                                if input_path(path):
                                    return ('praudit_xml', path)
                                None(path) = None
                                if looks_like_bgl(lines):
                                    return ('bgl', path)
                                if None(lines):
                                    return ('hdfs', path)
                                if None(lines):
                                    return ('praudit_text', path)
                                if None(lines):
                                    return ('tcpdump_text', path)
                                return (None, path)

