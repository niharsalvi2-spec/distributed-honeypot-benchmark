"""
Composite Rule-Based Correlation (Baseline 2).
Requires matching IP AND temporal proximity within window.
"""
from typing import List, Dict, Any, Tuple
import dateutil.parser

class RuleBasedCorrelation:
    def __init__(self, window_seconds: float = 60.0):
        self.window = window_seconds

    def evaluate(self, e1: Dict[str, Any], e2: Dict[str, Any]) -> float:
        ip1 = e1.get("source", {}).get("ip") or e1.get("src_ip")
        ip2 = e2.get("source", {}).get("ip") or e2.get("src_ip")
        if not ip1 or not ip2 or ip1 != ip2:
            return 0.0

        svc1 = e1.get("service") or e1.get("service_id")
        svc2 = e2.get("service") or e2.get("service_id")
        # Base confidence for IP match
        score = 0.70
        if svc1 and svc2 and svc1 != svc2:
            score += 0.15
        return score

    def correlate(self, events: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        links = []
        n = len(events)
        for i in range(n):
            for j in range(i + 1, n):
                score = self.evaluate(events[i], events[j])
                if score > 0.5:
                    links.append((events[i]["event_id"], events[j]["event_id"], score))
        return links

# Alias for backward compatibility
RuleBasedCorrelationEngine = RuleBasedCorrelation
