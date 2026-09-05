"""
Metric Analyzer: E04_cross_service
Evaluates Cross-Service Precision, Recall, and F1 against Campaign A ground truth.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from correlation.cross_service.service_linker import CrossServiceLinker
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

    # Link events using CrossServiceLinker
    linker = CrossServiceLinker(time_window_sec=60.0)
    for ev in events:
        linker.ingest_event(ev)
    predicted_links = set(linker.get_cross_service_links())

    # Ground truth links: sequential chain of steps
    gt_pairs = set()
    for i in range(len(events) - 1):
        gt_pairs.add((events[i]["event_id"], events[i+1]["event_id"]))

    metrics = CorrelationEvaluator.evaluate(predicted_links, gt_pairs)

    return {
        "experiment_id": "E04",
        "run_id": run_id,
        "total_cross_service_events": len(events),
        "predicted_links_count": len(predicted_links),
        "ground_truth_links_count": len(gt_pairs),
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "f1_score": metrics["f1"],
        "hypothesis_H3_supported": metrics["f1"] >= 0.85
    }
