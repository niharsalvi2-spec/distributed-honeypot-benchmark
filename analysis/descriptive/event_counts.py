"""
Event Distribution & Volume Analyzer.
"""
import pandas as pd
from typing import List, Dict, Any

def analyze_event_counts(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not events:
        return {"total_events": 0, "by_node": {}, "by_service": {}}
    df = pd.DataFrame(events)
    node_counts = df["node_id"].value_counts().to_dict() if "node_id" in df else {}
    svc_counts = {}
    if "service" in df:
        svc_counts = df["service"].apply(lambda s: s.get("service_id") if isinstance(s, dict) else str(s)).value_counts().to_dict()
    return {
        "total_events": len(events),
        "by_node": node_counts,
        "by_service": svc_counts
    }
