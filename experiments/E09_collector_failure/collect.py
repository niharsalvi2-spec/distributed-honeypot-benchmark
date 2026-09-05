"""
Telemetry Collector: E09_collector_failure
Simulates collector daemon downtime and local disk queue spooling.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
from typing import Dict, Any
from benchmark.collector import BenchmarkCollector
from distributed.communication.queue import ResilientDiskQueue

def collect_telemetry(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    queue_dir = os.path.join(project_root, "data", "spool", run_id)
    os.makedirs(queue_dir, exist_ok=True)
    
    queue = ResilientDiskQueue(queue_dir)
    
    # Simulate events arriving while central collector is unreachable
    spooled_events = []
    for i in range(50):
        ev = {"event_id": f"EV_SPOOL_{i:03d}", "node_id": "node_alpha", "timestamp": f"2026-09-06T06:00:{i:02d}.000Z"}
        queue.enqueue(ev)
        spooled_events.append(ev)

    # Reconnection phase: drain queue into raw storage
    drained_events = []
    while not queue.is_empty():
        item = queue.dequeue()
        if item:
            drained_events.append(item)

    raw_dir = os.path.join(project_root, "data", "raw", "spool_recovery", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "drained_events.jsonl")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in drained_events:
            f.write(json.dumps(ev) + "\n")

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in drained_events:
            f.write(json.dumps(ev) + "\n")

    return {
        "run_id": run_id,
        "spooled_count": len(spooled_events),
        "drained_count": len(drained_events),
        "normalized_file": norm_file
    }
