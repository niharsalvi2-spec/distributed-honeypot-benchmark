"""
Event Loss Rate Calculator during Node / Network Failures.
Computes absolute event loss, loss percentages, missing event IDs, and delivery ratios.
"""
from typing import List, Set, Dict, Any, Optional

class EventLossAnalyzer:
    """
    Computes packet and telemetry message loss during network partitions,
    node crashes, and buffer overflows.
    """
    @staticmethod
    def compute_event_loss(expected_count: int, received_count: int) -> float:
        """Computes fractional event loss rate [0.0 - 1.0]."""
        lost = max(0, expected_count - received_count)
        return round(float(lost) / float(expected_count), 4) if expected_count > 0 else 0.0

    @staticmethod
    def identify_missing_events(expected_ids: List[str], received_ids: List[str]) -> Dict[str, Any]:
        exp_set = set(expected_ids)
        rec_set = set(received_ids)
        missing = sorted(list(exp_set - rec_set))
        unexpected = sorted(list(rec_set - exp_set))
        loss_rate = len(missing) / len(exp_set) if exp_set else 0.0
        
        return {
            "expected_count": len(exp_set),
            "received_count": len(rec_set),
            "missing_count": len(missing),
            "unexpected_count": len(unexpected),
            "loss_rate": round(loss_rate, 4),
            "delivery_ratio": round(1.0 - loss_rate, 4),
            "missing_sample_ids": missing[:20],
            "zero_loss_verified": len(missing) == 0
        }

def compute_event_loss(expected_count: int, received_count: int) -> float:
    return EventLossAnalyzer.compute_event_loss(expected_count, received_count)
