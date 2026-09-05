"""
Partial Order Resolver.
Groups concurrent events into concurrency equivalence sets without forcing artificial serialization.
"""
from typing import List, Dict, Any
from distributed.clocks.vector_clock import VectorClock

class PartialOrderResolver:
    @staticmethod
    def group_concurrent_events(events: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Groups events into concurrent tiers."""
        layers = []
        for e in events:
            placed = False
            for layer in layers:
                if all(VectorClock.compare(e.get("timestamps", {}).get("vector_clock", {}),
                                           other.get("timestamps", {}).get("vector_clock", {})) == "CONCURRENT"
                       for other in layer):
                    layer.append(e)
                    placed = True
                    break
            if not placed:
                layers.append([e])
        return layers
