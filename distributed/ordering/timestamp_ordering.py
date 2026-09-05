"""
Physical Timestamp Ordering Engine (Baseline 1 & 2).
Orders events strictly by arrival epoch timestamp.
"""
from typing import List, Dict, Any

class TimestampOrdering:
    @staticmethod
    def sort(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(events, key=lambda e: e.get("timestamps", {}).get("physical_raw", ""))
