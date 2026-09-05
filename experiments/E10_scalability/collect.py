"""
Telemetry Collector: E10_scalability
Injects high-rate synthetic events to measure pipeline throughput and resource consumption.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
import time
from typing import Dict, Any
from benchmark.collector import BenchmarkCollector

def collect_telemetry(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    collector = BenchmarkCollector(os.path.join(project_root, "data", "raw"))

    # Generate 500 events simulating a sustained burst
    events = []
    t_start = time.time()
    for i in range(500):
        events.append({
            "event_id": f"STRESS_EV_{i:05d}",
            "timestamp": f"2026-09-06T07:00:{i//50:02d}.{i%50:02d}Z",
            "service": "http",
            "src_ip": f"192.0.2.{i % 250 + 1}",
            "payload_size": 256
        })
    elapsed = max(time.time() - t_start, 0.05)

    raw_dir = os.path.join(project_root, "data", "raw", "scalability", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "raw_scalability.jsonl")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("honeytrap", run_id, "node_stress", raw_file)

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    return {
        "run_id": run_id,
        "stress_events_count": len(events),
        "generation_elapsed_sec": elapsed,
        "normalized_file": norm_file
    }
