"""
Vector Clock Concurrency Rate Analyzer.
Calculates percentage of events determined to be causally concurrent (A || B).
"""
from typing import List, Dict, Any
from distributed.clocks.vector_clock import VectorClock

def compute_concurrency_rate(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    n = len(events)
    total_pairs = 0
    concurrent_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            total_pairs += 1
            vc1 = events[i].get("timestamps", {}).get("vector_clock", {})
            vc2 = events[j].get("timestamps", {}).get("vector_clock", {})
            if VectorClock.compare(vc1, vc2) == "CONCURRENT":
                concurrent_pairs += 1
    rate = concurrent_pairs / total_pairs if total_pairs > 0 else 0.0
    return {
        "total_evaluated_pairs": total_pairs,
        "concurrent_pairs": concurrent_pairs,
        "concurrency_rate": round(rate, 4)
    }
