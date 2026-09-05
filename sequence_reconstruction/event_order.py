"""
Event Sequence Disentangler.
Orders events within a correlated cluster by logical and physical clocks.
"""
from typing import List, Dict, Any

class EventOrder:
    @staticmethod
    def order_cluster(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(events, key=lambda e: (
            e.get("timestamps", {}).get("lamport_logical", 0),
            e.get("timestamps", {}).get("physical_raw", "")
        ))
