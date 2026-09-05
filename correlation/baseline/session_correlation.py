"""
Baseline Session Correlation.
Links events sharing identical local session identifiers.
"""
from typing import List, Dict, Any, Tuple

class SessionCorrelation:
    @staticmethod
    def match(e1: Dict[str, Any], e2: Dict[str, Any]) -> bool:
        s1 = e1.get("details", {}).get("session_id") or e1.get("session_id") or e1.get("details", {}).get("session") or e1.get("session")
        s2 = e2.get("details", {}).get("session_id") or e2.get("session_id") or e2.get("details", {}).get("session") or e2.get("session")
        if not s1 or not s2:
            return False
        return s1 == s2

    @classmethod
    def correlate(cls, events: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        linked = []
        n = len(events)
        for i in range(n):
            for j in range(i + 1, n):
                if cls.match(events[i], events[j]):
                    linked.append((events[i]["event_id"], events[j]["event_id"], 1.0))
        return linked

# Alias for backward compatibility
SessionCorrelationEngine = SessionCorrelation
