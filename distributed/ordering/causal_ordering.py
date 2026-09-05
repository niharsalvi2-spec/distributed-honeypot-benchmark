"""
Causal Event Ordering & Dependency Resolution.
Ensures an event is not processed until all its causal predecessors have been observed.
"""
from typing import List, Dict, Any

class CausalOrdering:
    @staticmethod
    def is_causally_ready(event: Dict[str, Any], delivered_vector: Dict[str, int]) -> bool:
        event_vc = event.get("timestamps", {}).get("vector_clock", {})
        node = event.get("node_id")
        for n, t in event_vc.items():
            if n == node:
                if t != delivered_vector.get(n, 0) + 1:
                    return False
            else:
                if t > delivered_vector.get(n, 0):
                    return False
        return True
