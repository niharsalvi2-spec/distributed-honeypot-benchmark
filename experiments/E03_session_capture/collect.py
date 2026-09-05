"""
Telemetry Collector: E03_session_capture
Simulates interactive shell commands (tty keystrokes, downloads, execution) in Cowrie.
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

    cmd_path = os.path.join(project_root, "workloads", "benign", "ssh", "command_sequence.yaml")
    with open(cmd_path, "r", encoding="utf-8") as f:
        cmd_workload = yaml.safe_load(f)

    raw_events = []
    for idx, c in enumerate(cmd_workload.get("commands", [])):
        raw_events.append({
            "eventid": "cowrie.command.input",
            "timestamp": f"2026-09-06T01:10:{idx*3:02d}.000000Z",
            "src_ip": "198.51.100.42",
            "session": "sess_pty_001",
            "input": c.get("command"),
            "dst_port": 2222
        })

    raw_dir = os.path.join(project_root, "data", "raw", "cowrie", run_id)
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "node_session_cowrie.json")
    with open(raw_file, "w", encoding="utf-8") as f:
        for ev in raw_events:
            f.write(json.dumps(ev) + "\n")

    collector.stage_node_logs("cowrie", run_id, "node_session", raw_file)
    normalized = [normalizer.normalize_event("cowrie", ev) for ev in raw_events]

    norm_dir = os.path.join(project_root, "data", "normalized", run_id)
    os.makedirs(norm_dir, exist_ok=True)
    norm_file = os.path.join(norm_dir, "normalized_events.jsonl")
    with open(norm_file, "w", encoding="utf-8") as f:
        for ev in normalized:
            f.write(json.dumps(ev) + "\n")

    return {"run_id": run_id, "commands_simulated": len(raw_events), "normalized_file": norm_file}
