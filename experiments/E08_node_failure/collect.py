"""
Telemetry Collector: E08_node_failure
Injects node crash-stop fault into honeypot topology.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from benchmark.collector import BenchmarkCollector
from collectors.normalization.normalize import EventNormalizer

def collect_telemetry(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    collector = BenchmarkCollector(os.path.join(project_root, "data", "raw"))
    normalizer = EventNormalizer()

    # 100 events scheduled, node_beta crashed during events 40..60
    total_scheduled = 100
    events = []
    for i in range(total_scheduled):
        node = "node_alpha" if i % 2 == 0 else "node_beta"
        is_lost = (node == "node_beta" and 40 <= i <= 60)
        if not is_lost:
            events.append({
                "event_id": f"EV_FAIL_{i:04d}",
                "node_id": node,
                "timestamp": f"2026-09-06T05:00:{i:02d}.000Z",
                "service": "ssh"
            })

    raw_dir = os.path.join(project_root, "data", "raw", "failure", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "raw_node_failure.jsonl")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("cowrie", run_id, "node_fail", raw_file)

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")

    return {
        "run_id": run_id,
        "scheduled_events": total_scheduled,
        "received_events": len(events),
        "normalized_file": norm_file
    }
