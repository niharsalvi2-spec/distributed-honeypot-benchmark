"""
Lamport Total Ordering Engine.
Orders events by monotonically increasing scalar clock with node ID tie-breaker.
(e1 < e2) <=> (L(e1) < L(e2) OR (L(e1) == L(e2) AND NodeId(e1) < NodeId(e2)))
"""
from typing import List, Dict, Any, Tuple, Union

class LamportOrdering:
    @staticmethod
    def sort(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return sorted(events, key=lambda e: (
            e.get("timestamps", {}).get("lamport_logical", 0),
            e.get("node_id", "")
        ))

    @staticmethod
    def sort_by_lamport(tagged_events: List[Tuple[Dict[str, Any], int]]) -> List[Dict[str, Any]]:
        """Sorts tuples of (event_dict, lamport_clock_int)."""
        sorted_pairs = sorted(tagged_events, key=lambda p: (p[1], p[0].get("node_id", "")))
        return [p[0] for p in sorted_pairs]

# Alias for backward compatibility
LamportOrder = LamportOrdering
