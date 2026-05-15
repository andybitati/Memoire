# Source Generated with Decompyle++
# File: categorizer.cpython-311.pyc (Python 3.11)

"""Catégorisation des événements (point 4).

Objectif:
- attribuer une catégorie/sous-catégorie sécurité à chaque événement normalisé.

Approche:
- rule-based (explicable) : utile en mémoire/rapport et robuste sur des logs bruts.
- extensible : les agents IA pourront affiner/remplacer ces règles.

Notes:
- Les règles sont volontairement conservatrices (faible faux-positifs).
- On s'appuie sur `message`, `dataset/subtype`, et quelques champs structurés
  (http_status, event, severity...).
"""
from __future__ import annotations
import re
from typing import Dict, Any, Tuple
from base import BaseNormalizer
SYSTEM_ERROR = 'SYSTEM_ERROR'
AUTHENTICATION = 'AUTHENTICATION'
AUTHORIZATION = 'AUTHORIZATION'
CONFIGURATION_CHANGE = 'CONFIGURATION_CHANGE'
NETWORK_ACTIVITY = 'NETWORK_ACTIVITY'
APPLICATION_ERROR = 'APPLICATION_ERROR'
INTRUSION_ATTEMPT = 'INTRUSION_ATTEMPT'
DOS_ATTACK = 'DOS_ATTACK'
MALWARE = 'MALWARE'
INFORMATIONAL = 'INFORMATIONAL'
_RE_FAILED_PWD = re.compile('\\bfailed password\\b|\\bauthentication failure\\b', re.I)
_RE_ACCEPTED_PWD = re.compile('\\baccepted password\\b|\\bsession opened\\b', re.I)
_RE_INVALID_USER = re.compile('\\binvalid user\\b', re.I)
_RE_SUDO = re.compile('\\bsudo\\b|\\bCOMMAND=', re.I)
_RE_PERM_DENIED = re.compile('permission denied|access denied|not authorized', re.I)
_RE_SCAN = re.compile('\\b(nmap|masscan|port ?scan|scan detected|recon)\\b', re.I)
_RE_BRUTE = re.compile('\\b(bruteforce|brute force|too many authentication failures)\\b', re.I)
_RE_DOS = re.compile('\\b(ddos|dos|syn flood|syn flooding|flood detected)\\b', re.I)
_RE_MALWARE = re.compile('\\b(malware|trojan|ransomware|backdoor|virus)\\b', re.I)
_RE_KERNEL = re.compile('\\b(kernel|panic|oops)\\b', re.I)
_RE_CRASH = re.compile('segfault|core dumped|stack trace', re.I)

def _safe_int(x = None):
    
    try:
        return int(str(x).strip())
    except Exception:
        return -1



def categorize(event = None):
