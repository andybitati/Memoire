# Route-Level Confusion Matrix for SupervisorAgent Sources

| Expected route | Predicted fallback | Predicted linux |
| --- | ---: | ---: |
| fallback | 4 | 0 |
| linux | 0 | 1 |

Interpretation: route-level accuracy is 5/5 at distinct-source level and 30/30 across repeated SupervisorAgent cycles. This matrix evaluates family/fallback routing after parsing/normalization, not detector-level intrusion classification.
