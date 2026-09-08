# Local Routing Sensitivity on SupervisorAgent Sources

| Source type | Expected | +/-10% route | Interpretation |
| --- | --- | --- | --- |
| CEF/LEEF | fallback | stable | Unsupported SIEM-like format is preserved without claiming a specialized detector |
| CloudTrail | fallback | stable | Cloud JSON records are retained as fallback in this article |
| Apache access | fallback | stable | Web logs are not forced into the network-flow detector after normalization |
| Linux/auth syslog | linux | stable | Syslog evidence dominates generic Windows-like normalized columns |
| Corrupted input | fallback | stable | Unknown/corrupted markers trigger graceful degradation |

Interpretation: limited local replay on the five distinct SupervisorAgent sources after parsing/normalization. This is a stability check, not a complete factorial sensitivity analysis.
