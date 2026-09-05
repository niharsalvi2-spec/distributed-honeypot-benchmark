"""
Clock Skew & Network Perturbation Generator
Injects asymmetric clock drift (delta in [-T, +T]) and network transport jitter into event timestamps.
"""
import random
from typing import List, Dict, Any, Optional

class ClockSkewGenerator:
    """
    Simulates physical clock drift across distributed honeypot nodes.
    Each node S_i is assigned a clock drift offset delta_i.
    """
    def __init__(self, node_skews: Optional[Dict[str, float]] = None, max_skew_sec: float = 3.0, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.node_skews = node_skews or {}
        self.max_skew_sec = max_skew_sec

    def get_node_skew(self, node_id: str) -> float:
        if node_id not in self.node_skews:
            self.node_skews[node_id] = random.uniform(-self.max_skew_sec, self.max_skew_sec)
        return self.node_skews[node_id]

    def apply_skew(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Returns a copy of events with uncorrected physical timestamps skewed by local node drift.
        Preserves true_timestamp in metadata for oracle validation.
        """
        skewed_events = []
        for ev in events:
            ev_copy = dict(ev)
            node = ev.get("target_node") or ev.get("node_id", "default_node")
            drift = self.get_node_skew(node)
            
            true_ts = ev.get("timestamp", 1700000000.0)
            ev_copy["_true_timestamp"] = true_ts
            ev_copy["timestamp"] = true_ts + drift
            ev_copy["_applied_drift_sec"] = drift
            skewed_events.append(ev_copy)
        return skewed_events
