"""
Canonical Normalization Engine with Strict Data Lineage.
Implements the invariant: RAW -> NORMALIZED -> ORDERED -> CORRELATED -> RECONSTRUCTED -> EVALUATED
Guarantees raw data is never modified.
"""
import os
import json
import uuid
import hashlib
from datetime import datetime
from typing import Dict, Any, List

def compute_checksum(data: Any) -> str:
    serialized = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()

def normalize_event(raw_event: Dict[str, Any], repo_name: str, run_id: str) -> Dict[str, Any]:
    """
    Transforms heterogeneous raw honeypot events into unified canonical schema with lineage.
    """
    event_uuid = str(uuid.uuid4())
    now_iso = datetime.utcnow().isoformat() + "Z"
    
    canonical = {
        "event_id": str(raw_event.get("event_id") or raw_event.get("eventid") or f"can_{event_uuid[:8]}"),
        "node_id": raw_event.get("node_id", f"node_{repo_name}"),
        "service_id": raw_event.get("service", raw_event.get("service_id", repo_name)),
        "transport_protocol": raw_event.get("protocol", "TCP"),
        "source": {
            "ip": raw_event.get("src_ip", raw_event.get("source_ip", "127.0.0.1")),
            "port": raw_event.get("src_port", raw_event.get("source_port", 0))
        },
        "timestamps": {
            "physical_raw": raw_event.get("timestamp", now_iso),
            "physical_ingested": now_iso,
            "lamport_logical": raw_event.get("lamport_clock", 0),
            "vector_clock": raw_event.get("vector_clock", {})
        },
        "event_type": raw_event.get("event_type", raw_event.get("eventid", "GENERIC_EVENT")),
        "payload_features": raw_event.get("features", {}),
        "details": {
            "username": raw_event.get("username", raw_event.get("user")),
            "password": raw_event.get("password", raw_event.get("pass")),
            "command": raw_event.get("input", raw_event.get("command")),
            "session_id": raw_event.get("session", raw_event.get("session_id")),
            **{k: v for k, v in raw_event.items() if k not in ["src_ip", "source_ip", "src_port", "source_port", "timestamp"]}
        },
        "data_lineage": {
            "run_id": run_id,
            "raw_repo": repo_name,
            "raw_checksum": compute_checksum(raw_event),
            "normalization_timestamp": now_iso
        }
    }
    return canonical

def process_run_lifecycle(raw_run_dir: str, normalized_run_dir: str, repo_name: str, run_id: str) -> List[Dict[str, Any]]:
    """
    Reads raw events without touching raw files, normalizes, and writes to data/normalized/<run_id>/
    """
    os.makedirs(normalized_run_dir, exist_ok=True)
    raw_files = [f for f in os.listdir(raw_run_dir) if f.endswith(".json")]
    
    all_normalized = []
    for rf in raw_files:
        full_p = os.path.join(raw_run_dir, rf)
        with open(full_p, "r", encoding="utf-8") as f:
            try:
                content = json.load(f)
                if isinstance(content, dict):
                    content = [content]
                for raw_evt in content:
                    norm_evt = normalize_event(raw_evt, repo_name, run_id)
                    all_normalized.append(norm_evt)
            except Exception:
                pass
                
    out_file = os.path.join(normalized_run_dir, "canonical_events.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_normalized, f, indent=2)
        
    # Write lineage manifest
    manifest = {
        "run_id": run_id,
        "repo": repo_name,
        "raw_source_dir": raw_run_dir,
        "normalized_file": out_file,
        "event_count": len(all_normalized),
        "pipeline_stage": "NORMALIZED",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    with open(os.path.join(normalized_run_dir, "lineage_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        
    return all_normalized

class EventNormalizer:
    @staticmethod
    def normalize_event(repo_name: str, raw_event: Dict[str, Any], run_id: str = "run_default") -> Dict[str, Any]:
        return normalize_event(raw_event, repo_name, run_id)

    @staticmethod
    def normalize_dataset(repo_name: str, raw_events: List[Dict[str, Any]], run_id: str = "run_default") -> List[Dict[str, Any]]:
        return [normalize_event(ev, repo_name, run_id) for ev in raw_events]
