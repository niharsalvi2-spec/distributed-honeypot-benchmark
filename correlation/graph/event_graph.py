"""
Event Correlation Graph Builder.
Constructs NetworkX graph G=(V,E) where V=Events and E=Association Weights.
Uses connected components to extract multi-stage attack sequences.
"""
import networkx as nx
from typing import List, Dict, Any, Tuple, Optional
from correlation.cross_service.session_linker import SessionLinker

class EventGraphBuilder:
    def __init__(self, linker: Optional[SessionLinker] = None):
        self.linker = linker or SessionLinker()
        self.graph = nx.Graph()

    def build_graph(self, events: List[Dict[str, Any]]) -> nx.Graph:
        self.graph.clear()
        for e in events:
            self.graph.add_node(e["event_id"], event_data=e)

        n = len(events)
        for i in range(n):
            for j in range(i + 1, n):
                score, conf = self.linker.evaluate_pair(events[i], events[j])
                if conf == "STRONG":
                    self.graph.add_edge(events[i]["event_id"], events[j]["event_id"], weight=score, confidence=conf)
        return self.graph

    def get_attack_clusters(self) -> List[List[str]]:
        """Extracts connected components representing coordinated attack clusters."""
        return [list(c) for c in nx.connected_components(self.graph) if len(c) > 1]
