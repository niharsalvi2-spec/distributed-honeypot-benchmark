"""
Telemetry Collector: E02_authentication
Simulates high-density authentication workloads against SSH and Telnet interfaces.
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

    # Load authentication workload
    workload_path = os.path.join(project_root, "workloads", "benign", "ssh", "login_attempts.yaml")
    with open(workload_path, "r", encoding="utf-8") as f:
        workload = yaml.safe_load(f)

    raw_events = []
    for idx, attempt in enumerate(workload.get("attempts", [])):
        raw_events.append({
            "eventid": "cowrie.login.success" if attempt.get("success") else "cowrie.login.failed",
            "timestamp": f"2026-09-06T01:00:{idx*2:02d}.000000Z",
            "src_ip": attempt.get("source_ip", "10.0.0.1"),
            "dst_port": attempt.get("port", 2222),
            "username": attempt.get("user", "root"),
            "password": attempt.get("password", "pass"),
            "session": f"sess_auth_{idx:03d}"
        })

    # Stage raw logs
    raw_dir = os.path.join(project_root, "data", "raw", "cowrie", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, f"node_auth_cowrie.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in raw_events:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("cowrie", run_id, "node_auth", raw_file)

    # Normalize
    normalized_events = [normalizer.normalize_event("cowrie", ev) for ev in raw_events]
    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in normalized_events:
            f.write(json.dumps(ev) + "\n")

    return {
        "run_id": run_id,
        "attempts_simulated": len(raw_events),
        "normalized_file": norm_file
    }
