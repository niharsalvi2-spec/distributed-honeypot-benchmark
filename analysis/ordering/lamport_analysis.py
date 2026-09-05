"""
Lamport Clock Scaling & Tie-Breaker Analysis.
"""
from typing import List, Dict, Any

def analyze_lamport_stream(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    ticks = [e.get("timestamps", {}).get("lamport_logical", 0) for e in events]
    return {
        "max_tick": max(ticks) if ticks else 0,
        "is_strictly_monotonic": all(ticks[i] <= ticks[i+1] for i in range(len(ticks)-1))
    }
