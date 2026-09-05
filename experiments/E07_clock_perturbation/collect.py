"""
Telemetry Collector: E07_clock_perturbation
Injects asymmetric clock skew and jitter into multi-node events.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
import random
from typing import Dict, Any
from benchmark.collector import BenchmarkCollector
from collectors.normalization.normalize import EventNormalizer

def collect_telemetry(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    collector = BenchmarkCollector(os.path.join(project_root, "data", "raw"))
    normalizer = EventNormalizer()

    # Create sequence of 10 causal events across node_alpha, node_beta, node_gamma
    # Node beta has +5000ms clock skew; Node gamma has -3000ms clock skew
    nodes = ["node_alpha", "node_beta", "node_gamma"]
    node_skews = {"node_alpha": 0.0, "node_beta": 5.0, "node_gamma": -3.0}

    events = []
    base_t = 1757120000.0
    for i in range(12):
        node = nodes[i % 3]
        real_time = base_t + (i * 1.5)
        skewed_time = real_time + node_skews[node] + random.uniform(-0.1, 0.1)

        events.append({
            "event_id": f"EV_PERTRUB_{i:03d}",
            "real_timestamp": real_time,
            "skewed_timestamp": skewed_time,
            "node_id": node,
            "service": "ssh" if i % 2 == 0 else "http",
            "logical_order": i
        })

    raw_dir = os.path.join(project_root, "data", "raw", "skewed", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "raw_skewed_events.jsonl")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("cowrie", run_id, "node_skew", raw_file)

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    return {"run_id": run_id, "skewed_events_generated": len(events), "normalized_file": norm_file}
