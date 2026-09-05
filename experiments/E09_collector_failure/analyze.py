"""
Metric Analyzer: E09_collector_failure
Validates zero-loss queue recovery and draining throughput.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from analysis.reliability.event_loss import EventLossAnalyzer

def analyze_run(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    norm_file = os.path.join(project_root, "data", "normalized", run_id, "normalized_events.jsonl")
    
    events = []
    if os.path.exists(norm_file):
        with open(norm_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    events.append(json.loads(line))

    expected = 50
    received = len(events)
    loss = EventLossAnalyzer.compute_event_loss(expected, received)

    return {
        "experiment_id": "E09",
        "run_id": run_id,
        "spooled_events_expected": expected,
        "recovered_events": received,
        "loss_rate": loss,
        "zero_loss_guaranteed": loss == 0.0
    }
