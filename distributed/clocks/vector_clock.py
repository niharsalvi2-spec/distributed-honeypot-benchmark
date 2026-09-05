"""
Vector Clock implementation for causal ordering and concurrency tracking.
"""
import threading
from typing import Dict, Optional, Any

class VectorClock:
    def __init__(self, node_id: str, num_nodes: Optional[int] = None):
        self.node_id = str(node_id)
        self.num_nodes = num_nodes
        self.clock: Dict[str, int] = {self.node_id: 0}
        self.lock = threading.Lock()

    def tick(self) -> Dict[str, int]:
        with self.lock:
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
            return dict(self.clock)

    def update(self, received_clock: Dict[str, int]) -> Dict[str, int]:
        with self.lock:
            for node, t in received_clock.items():
                self.clock[node] = max(self.clock.get(node, 0), t)
            self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
            return dict(self.clock)

    def is_concurrent(self, other: "VectorClock") -> bool:
        return self.compare(self.clock, other.clock) == "CONCURRENT"

    def happens_before(self, other: "VectorClock") -> bool:
        return self.compare(self.clock, other.clock) == "BEFORE"

    @staticmethod
    def compare(vc1: Dict[str, int], vc2: Dict[str, int]) -> str:
        le = all(vc1.get(k, 0) <= vc2.get(k, 0) for k in set(vc1) | set(vc2))
        ge = all(vc1.get(k, 0) >= vc2.get(k, 0) for k in set(vc1) | set(vc2))
        if le and not ge:
            return "BEFORE"
        elif ge and not le:
            return "AFTER"
        elif le and ge:
            return "EQUAL"
        return "CONCURRENT"

    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {"node_id": self.node_id, "clock": dict(self.clock)}
