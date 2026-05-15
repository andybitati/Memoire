# Source Generated with Decompyle++
# File: default.cpython-311.pyc (Python 3.11)

from typing import Dict, Any
from base import BaseNormalizer

class DefaultNormalizer(BaseNormalizer):
    name = 'default'
    
    def normalize(self = None, event = None):
        if not event.get('severity'):
            sev = ''.upper()
            if sev in ('WARN', 'WARNING'):
                event['severity'] = 'WARNING'
            elif sev in ('ERR', 'ERROR'):
                event['severity'] = 'ERROR'
            elif sev in ('CRIT', 'CRITICAL', 'PANIC', 'ALERT'):
                event['severity'] = 'CRITICAL'
        return event


