"""
Baseline Temporal Proximity Correlation.
Links any events occurring within a fixed sliding time window.
"""
from typing import List, Dict, Any, Tuple
import dateutil.parser

class TimestampCorrelation:
    def __init__(self, window_seconds: float = 60.0):
        self.window = window_seconds

    @staticmethod
    def is_within_window(e1: Dict[str, Any], e2: Dict[str, Any], window_ms: float = 5000.0) -> bool:
        t1 = e1.get("timestamps", {}).get("epoch_ms")
        t2 = e2.get("timestamps", {}).get("epoch_ms")
        if t1 is not None and t2 is not None:
            return abs(t1 - t2) <= window_ms
        # Fallback to physical_raw
        raw1 = e1.get("timestamps", {}).get("physical_raw")
        raw2 = e2.get("timestamps", {}).get("physical_raw")
        if raw1 and raw2:
            dt1 = dateutil.parser.parse(raw1).timestamp() * 1000
            dt2 = dateutil.parser.parse(raw2).timestamp() * 1000
            return abs(dt1 - dt2) <= window_ms
        return False

    def correlate(self, events: List[Dict[str, Any]]) -> List[Tuple[str, str, float]]:
        linked_pairs = []
        n = len(events)
        for i in range(n):
            t_i = dateutil.parser.parse(events[i]["timestamps"]["physical_raw"]).timestamp()
            for j in range(i + 1, n):
                t_j = dateutil.parser.parse(events[j]["timestamps"]["physical_raw"]).timestamp()
                diff = abs(t_i - t_j)
                if diff <= self.window:
                    score = 1.0 - (diff / self.window)
                    linked_pairs.append((events[i]["event_id"], events[j]["event_id"], score))
        return linked_pairs

# Alias for backward compatibility
TimestampCorrelationEngine = TimestampCorrelation
