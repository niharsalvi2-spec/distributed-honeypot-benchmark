"""
Telemetry Collector: E04_cross_service
Simulates a multi-stage attack pivoting across HTTP, SSH, and FTP services.
"""
import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import os
import json
import yaml
from typing import Dict, Any
from benchmark.collector import BenchmarkCollector
from collectors.normalization.normalize import EventNormalizer

def collect_telemetry(run_id: str) -> Dict[str, Any]:
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    collector = BenchmarkCollector(os.path.join(project_root, "data", "raw"))
    normalizer = EventNormalizer()

    timeline_path = os.path.join(project_root, "workloads", "controlled_attack", "campaign_A", "timeline.yaml")
    with open(timeline_path, "r", encoding="utf-8") as f:
        timeline = yaml.safe_load(f)

    raw_events = []
    for step in timeline.get("steps", []):
        raw_events.append({
            "event_id": step.get("step_id"),
            "service": step.get("service"),
            "timestamp": f"2026-09-06T02:00:{int(step.get('offset_sec', 0)):02d}.000000Z",
            "src_ip": "198.51.100.42",
            "action": step.get("action"),
            "payload": step.get("payload"),
            "node": step.get("node")
        })

    raw_dir = os.path.join(project_root, "data", "raw", "cross_service", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "raw_cross_service.jsonl")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in raw_events:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("cowrie", run_id, "node_cs", raw_file)
    normalized = [normalizer.normalize_event("cowrie", ev) for ev in raw_events]

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in normalized:
            f.write(json.dumps(ev) + "\n")

    return {"run_id": run_id, "cross_service_steps": len(raw_events), "normalized_file": norm_file}
