"""
Service Attack Frequency Analyzer.
"""
from collections import Counter
from typing import List, Dict, Any

def get_service_frequencies(events: List[Dict[str, Any]]) -> Dict[str, int]:
    counts = Counter()
    for e in events:
        svc = e.get("service", {}).get("service_id", e.get("service", "unknown"))
        counts[svc] += 1
    return dict(counts)
