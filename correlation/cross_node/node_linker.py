"""
Cross-Node Correlation Engine.
Correlates events originating on different physical/logical sensor nodes.
"""
from typing import List, Dict, Any, Tuple, Set
from correlation.cross_service.session_linker import SessionLinker

class NodeLinker:
    def __init__(self, sliding_window_sec: float = 120.0):
        self.sliding_window_sec = sliding_window_sec
        self.session_linker = SessionLinker()
        self.events: List[Dict[str, Any]] = []

    def ingest_event(self, event: Dict[str, Any]):
        self.events.append(event)

    def get_cross_node_links(self) -> List[Tuple[str, str]]:
        links = []
        n = len(self.events)
        for i in range(n):
            for j in range(i + 1, n):
                ev1 = self.events[i]
                ev2 = self.events[j]
                n1 = ev1.get("node_id") or ev1.get("node")
                n2 = ev2.get("node_id") or ev2.get("node")
                if n1 != n2:
                    links.append((ev1["event_id"], ev2["event_id"]))
        return links

    def find_cross_node_links(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        links = []
        n = len(events)
        for i in range(n):
            for j in range(i + 1, n):
                if events[i].get("node_id") != events[j].get("node_id"):
                    score, conf = self.session_linker.evaluate_pair(events[i], events[j])
                    if conf in ["STRONG", "WEAK"]:
                        links.append({
                            "event_1": events[i]["event_id"],
                            "event_2": events[j]["event_id"],
                            "node_1": events[i]["node_id"],
                            "node_2": events[j]["node_id"],
                            "score": score,
                            "confidence": conf
                        })
        return links

# Alias for backward compatibility
CrossNodeLinker = NodeLinker
