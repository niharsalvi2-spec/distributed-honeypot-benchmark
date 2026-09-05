"""
Causal Graph & Directed Acyclic Graph (DAG) Generator
Constructs distributed causal attack chains with explicit happens-before edges
and identifies concurrent event pairs (a || b) across independent nodes.
"""
import networkx as nx
from typing import List, Dict, Any, Tuple, Set

class CausalGraphGenerator:
    """
    Generates synthetic causal DAGs for distributed attack workflows.
    Nodes represent events; directed edges represent happens-before causal relations.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, event_id: str, node_id: str, service: str, event_type: str, actor_id: str = "ACTOR_A"):
        self.graph.add_node(
            event_id,
            node_id=node_id,
            service=service,
            event_type=event_type,
            actor_id=actor_id
        )

    def add_causal_edge(self, from_event: str, to_event: str, relation_type: str = "causal_transition"):
        """
        Adds directed edge: from_event -> to_event (from_event happens-before to_event).
        """
        self.graph.add_edge(from_event, to_event, relation=relation_type)

    def get_topological_order(self) -> List[str]:
        """
        Returns a valid topological sort (linearization) of the causal DAG.
        """
        return list(nx.topological_sort(self.graph))

    def get_concurrent_pairs(self) -> Set[Tuple[str, str]]:
        """
        Identifies all pairs of events (u, v) that are concurrent (neither u -> v nor v -> u).
        """
        nodes = list(self.graph.nodes)
        concurrent = set()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                u, v = nodes[i], nodes[j]
                u_reaches_v = nx.has_path(self.graph, u, v)
                v_reaches_u = nx.has_path(self.graph, v, u)
                if not u_reaches_v and not v_reaches_u:
                    concurrent.add(tuple(sorted((u, v))))
        return concurrent

    def export_spec(self) -> Dict[str, Any]:
        """
        Exports the DAG specification in manifest format for BenchmarkOracle.
        """
        return {
            "linear_sequence": self.get_topological_order(),
            "causal_edges": [
                {"from": u, "to": v, "relation": d.get("relation", "causal")}
                for u, v, d in self.graph.edges(data=True)
            ],
            "concurrent_pairs_count": len(self.get_concurrent_pairs())
        }
