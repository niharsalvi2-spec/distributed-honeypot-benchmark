"""
Event Cleaning & Sanitization Engine.
Filters malformed payloads and handles missing required fields.
"""
from typing import List, Dict, Any

def clean_event_list(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cleaned = []
    for e in events:
        if not isinstance(e, dict):
            continue
        if "event_id" not in e or not e["event_id"]:
            continue
        cleaned.append(e)
    return cleaned
