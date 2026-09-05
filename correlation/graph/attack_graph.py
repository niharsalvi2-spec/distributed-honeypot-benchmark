"""
Attack Kill-Chain DAG.
Constructs Directed Acyclic Graph following MITRE ATT&CK tactical progression.
"""
import networkx as nx
from typing import List, Dict, Any

class AttackDAG:
    def __init__(self):
        self.dag = nx.DiGraph()

    def construct_chain(self, ordered_events: List[Dict[str, Any]]) -> nx.DiGraph:
        for i in range(len(ordered_events) - 1):
            e1 = ordered_events[i]["event_id"]
            e2 = ordered_events[i+1]["event_id"]
            self.dag.add_edge(e1, e2)
        return self.dag
