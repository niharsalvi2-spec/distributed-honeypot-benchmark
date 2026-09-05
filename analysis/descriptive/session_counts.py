"""
Session Metrics Analyzer.
"""
from collections import defaultdict
from typing import List, Dict, Any

def analyze_sessions(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    sessions = defaultdict(list)
    for e in events:
        sid = e.get("session_id", "default_session")
        sessions[sid].append(e)
    return {
        "total_sessions": len(sessions),
        "avg_events_per_session": round(len(events) / max(len(sessions), 1), 2)
    }
