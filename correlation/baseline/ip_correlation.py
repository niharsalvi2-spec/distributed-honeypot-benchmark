"""
Baseline Source IP Correlation.
Links events having identical source IP addresses.
"""
from typing import List, Dict, Any, Tuple

class IPCorrelation:
    @staticmethod
    def match(e1: Dict[str, Any], e2: Dict[str, Any]) -> bool:
        ip1 = e1.get("source", {}).get("ip") or e1.get("src_ip")
        ip2 = e2.get("source", {}).get("ip") or e2.get("src_ip")
        if not ip1 or not ip2 or ip1 == "0.0.0.0":
            return False
        return ip1 == ip2

    @classmethod
    def correlate(cls, events: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        linked_pairs = []
        n = len(events)
        for i in range(n):
            for j in range(i + 1, n):
                if cls.match(events[i], events[j]):
                    linked_pairs.append((events[i]["event_id"], events[j]["event_id"], 1.0))
        return linked_pairs

# Alias for backward compatibility
IPCorrelationEngine = IPCorrelation
