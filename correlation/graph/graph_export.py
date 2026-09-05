"""
Graph Serializer & Export Engine.
Exports correlation graphs into JSON, GraphML, and DOT for dashboard rendering.
"""
import json
import networkx as nx
from typing import Dict, Any

class GraphExporter:
    @staticmethod
    def to_json_dict(graph: nx.Graph) -> Dict[str, Any]:
        return {
            "nodes": [{"id": n, "data": graph.nodes[n].get("event_data", {})} for n in graph.nodes],
            "edges": [{"source": u, "target": v, "weight": graph.edges[u, v].get("weight", 1.0)}
                      for u, v in graph.edges]
        }
