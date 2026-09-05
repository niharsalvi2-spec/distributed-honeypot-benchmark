"""
Causal Sequence Graph Builder.
Generates DAG based on Lamport and Vector Clock precedence.
"""
import networkx as nx
from typing import List, Dict, Any, Optional
from distributed.clocks.vector_clock import VectorClock

class CausalGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, event_id: str, data: Optional[Dict[str, Any]] = None):
        self.graph.add_node(event_id, data=data or {})

    def add_causal_edge(self, u: str, v: str, relation: str = "causes"):
        self.graph.add_edge(u, v, relation=relation)

    def get_topological_sequence(self) -> List[str]:
        return list(nx.topological_sort(self.graph))

    @staticmethod
    def build_dag(events: List[Dict[str, Any]]) -> nx.DiGraph:
        dag = nx.DiGraph()
        for e in events:
            dag.add_node(e["event_id"], data=e)
        n = len(events)
        for i in range(n):
            for j in range(i + 1, n):
                rel = VectorClock.compare(
                    events[i].get("timestamps", {}).get("vector_clock", {}),
                    events[j].get("timestamps", {}).get("vector_clock", {})
                )
                if rel == "BEFORE":
                    dag.add_edge(events[i]["event_id"], events[j]["event_id"])
                elif rel == "AFTER":
                    dag.add_edge(events[j]["event_id"], events[i]["event_id"])
        return dag
