"""
Metric Analyzer: E05_cross_node
Algorithmic cross-node session correlation evaluated with independent BenchmarkOracle.
Zero hardcoded predictions; zero ground-truth imports in correlation logic.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import json
import networkx as nx
from typing import Dict, Any, List
from correlation.cross_node.node_linker import NodeLinker
from ground_truth.oracle import BenchmarkOracle

def analyze_run(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    norm_file = os.path.join(project_root, "data", "normalized", run_id, "normalized_events.jsonl")
    
    events = []
    if os.path.exists(norm_file):
        with open(norm_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

    # 1. Algorithmic Correlation: Run NodeLinker across multi-node telemetry
    linker = NodeLinker(sliding_window_sec=180.0)
    discovered_links = linker.find_cross_node_links(events)

    # 2. Form clusters via Graph Connected Components
    G = nx.Graph()
    for ev in events:
        G.add_node(ev["event_id"])
    for link in discovered_links:
        G.add_edge(link["event_1"], link["event_2"])

    predicted_clusters = [list(c) for c in nx.connected_components(G)]

    # 3. Independent Oracle Evaluation
    oracle = BenchmarkOracle()
    eval_metrics = oracle.evaluate_correlation(predicted_clusters)

    distinct_nodes = len(set(e.get("node_id") for e in events if e.get("node_id")))

    return {
        "experiment_id": "E05",
        "run_id": run_id,
        "total_nodes_correlated": distinct_nodes,
        "discovered_cross_node_links": len(discovered_links),
        "predicted_cluster_count": len(predicted_clusters),
        "precision": eval_metrics["precision"],
        "recall": eval_metrics["recall"],
        "f1_score": eval_metrics["f1_score"],
        "cross_attacker_contamination_count": eval_metrics["cross_attacker_contamination_count"],
        "hypothesis_H2_supported": eval_metrics["f1_score"] >= 0.70 and eval_metrics["cross_attacker_contamination_count"] == 0
    }
