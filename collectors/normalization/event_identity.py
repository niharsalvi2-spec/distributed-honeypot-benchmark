"""
Event Identity & Deduplication Engine.
Produces UUIDv4 identifiers and deterministic SHA-256 fingerprint hashes.
"""
import uuid
import hashlib
import json
from typing import Dict, Any

class EventIdentity:
    @staticmethod
    def generate_event_id() -> str:
        return f"evt_{uuid.uuid4().hex[:12]}"

    @staticmethod
    def compute_fingerprint(event_dict: Dict[str, Any]) -> str:
        """Calculates deterministic hash across source, service, and core payload."""
        features = {
            "src": event_dict.get("source", {}).get("ip"),
            "svc": event_dict.get("service", {}).get("service_id"),
            "type": event_dict.get("event_type"),
            "payload": event_dict.get("payload", {})
        }
        serialized = json.dumps(features, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
