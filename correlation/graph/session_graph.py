"""
Session Graph Model.
Represents interactions between services as a directed state machine.
"""
import networkx as nx

class SessionGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_transition(self, from_svc: str, to_svc: str, weight: float = 1.0):
        self.graph.add_edge(from_svc, to_svc, weight=weight)
