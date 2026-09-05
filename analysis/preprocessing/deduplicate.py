"""
Event Deduplication Engine.
Eliminates duplicate events using unique fingerprints.
"""
from typing import List, Dict, Any

def deduplicate_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen_ids = set()
    unique = []
    for e in events:
        eid = e.get("event_id")
        if eid and eid not in seen_ids:
            seen_ids.add(eid)
            unique.append(e)
    return unique
