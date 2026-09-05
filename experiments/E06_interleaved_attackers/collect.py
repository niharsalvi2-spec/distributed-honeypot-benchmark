"""
Telemetry Collector: E06_interleaved_attackers
Simulates concurrent, interleaved attacks from Attacker-Alpha and Attacker-Beta.
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

    # Interleaved events from two distinct actors
    interleaved_raw = [
        {"event_id": "A1", "src_ip": "192.0.2.77", "service": "ssh", "timestamp": "2026-09-06T04:00:01.000Z", "actor": "A"},
        {"event_id": "B1", "src_ip": "198.51.100.99", "service": "http", "timestamp": "2026-09-06T04:00:02.000Z", "actor": "B"},
        {"event_id": "A2", "src_ip": "192.0.2.77", "service": "ssh", "timestamp": "2026-09-06T04:00:03.000Z", "actor": "A"},
        {"event_id": "B2", "src_ip": "198.51.100.99", "service": "http", "timestamp": "2026-09-06T04:00:04.000Z", "actor": "B"},
        {"event_id": "A3", "src_ip": "192.0.2.77", "service": "ftp", "timestamp": "2026-09-06T04:00:05.000Z", "actor": "A"},
        {"event_id": "B3", "src_ip": "198.51.100.99", "service": "ssh", "timestamp": "2026-09-06T04:00:06.000Z", "actor": "B"}
    ]

    raw_dir = os.path.join(project_root, "data", "raw", "interleaved", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "raw_interleaved.jsonl")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in interleaved_raw:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("cowrie", run_id, "node_interleaved", raw_file)
    normalized = [normalizer.normalize_event("cowrie", ev) for ev in interleaved_raw]

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in normalized:
            f.write(json.dumps(ev) + "\n")

    return {"run_id": run_id, "interleaved_events": len(interleaved_raw), "normalized_file": norm_file}
