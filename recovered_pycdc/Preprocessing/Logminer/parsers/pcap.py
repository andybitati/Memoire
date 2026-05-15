# Source Generated with Decompyle++
# File: pcap.cpython-311.pyc (Python 3.11)

'''Parseur PCAP/PCAPNG (streaming via Scapy).'''
from typing import Iterable
from common import make_pbar
from writer import emit

try:
    from scapy.all import PcapReader, IP, IPv6, TCP, UDP
except Exception:
    PcapReader = None


class Parser:
    subtype = 'pcap'
    
    def parse(self = None, path = None, writer = None, sep = ('path', str, 'sep', str, 'split_rows', int, 'progress_every', int, 'use_tqdm', bool, 'debug', bool, 'return', Iterable[str]), *, split_rows, progress_every, use_tqdm, debug):
        pass
    # WARNING: Decompyle incomplete


