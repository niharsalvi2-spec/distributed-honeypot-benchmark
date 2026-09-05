"""
Metric Analyzer: E06_interleaved_attackers
Evaluates attacker separation purity and causal chain accuracy.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from sequence_reconstruction.causal_graph import CausalGraphBuilder
from correlation.evaluation.correlation_accuracy import CorrelationEvaluator

def analyze_run(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    norm_file = os.path.join(project_root, "data", "normalized", run_id, "normalized_events.jsonl")
    
    events = []
    if os.path.exists(norm_file):
        with open(norm_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

    # Ground truth causal links: A1->A2->A3 and B1->B2->B3
    gt_links = {("A1", "A2"), ("A2", "A3"), ("B1", "B2"), ("B2", "B3")}
    
    # Separation by IP
    pred_links = set()
    actor_groups = {}
    for ev in events:
        ip = ev.get("source", {}).get("ip")
        actor_groups.setdefault(ip, []).append(ev["event_id"])

    for ip, ev_ids in actor_groups.items():
        for i in range(len(ev_ids) - 1):
            pred_links.add((ev_ids[i], ev_ids[i+1]))

    metrics = CorrelationEvaluator.evaluate(pred_links, gt_links)

    return {
        "experiment_id": "E06",
        "run_id": run_id,
        "interleaved_events_total": len(events),
        "actors_separated": len(actor_groups),
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1"],
        "separation_purity": 1.0 if metrics["false_positives"] == 0 else 0.0
    }
