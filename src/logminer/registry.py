# Source Generated with Decompyle++
# File: registry.cpython-311.pyc (Python 3.11)

'''Registre (type détecté -> classe parseur).'''
from parsers.hdfs import Parser as HDFSParser
from parsers.bgl import Parser as BGLParser
from parsers.tcpdump_text import Parser as TcpdumpTextParser
from parsers.praudit_text import Parser as PrauditTextParser
from parsers.pcap import Parser as PCAPParser
from parsers.praudit_xml import Parser as PrauditXMLParser
from parsers.syslog import Parser as SyslogParser
from parsers.apache import Parser as ApacheParser
from parsers.jsonl import Parser as JSONLParser
from parsers.cef_leef import Parser as CEFLEEFParser
from parsers.windows_event import Parser as WinEventParser
from parsers.cloudtrail import Parser as CloudTrailParser
from parsers.unknown import Parser as UnknownParser
PARSERS = {
    'hdfs': HDFSParser,
    'bgl': BGLParser,
    'tcpdump_text': TcpdumpTextParser,
    'praudit_text': PrauditTextParser,
    'pcap': PCAPParser,
    'praudit_xml': PrauditXMLParser,
    'syslog': SyslogParser,
    'apache': ApacheParser,
    'jsonl': JSONLParser,
    'cef_leef': CEFLEEFParser,
    'win_event': WinEventParser,
    'cloudtrail': CloudTrailParser,
    'unknown': UnknownParser }
