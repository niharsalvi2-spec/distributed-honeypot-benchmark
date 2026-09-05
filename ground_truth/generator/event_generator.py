"""
Synthetic Canonical Event Generator
Emits realistic, schema-valid canonical events for given threat actors, services, and nodes.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ground_truth.generator.actor_generator import ThreatActor
from ground_truth.generator.topology_generator import HoneypotNode

class EventGenerator:
    """
    Generates canonical JSON event records conforming to the 2.0.0 canonical event schema.
    """
    @staticmethod
    def create_event(
        event_id: str,
        actor: ThreatActor,
        node: HoneypotNode,
        service: str,
        tactic: str,
        timestamp_sec: float,
        session_id: Optional[str] = None,
        source_ip: Optional[str] = None,
        payload_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        iso_ts = datetime.utcfromtimestamp(timestamp_sec).isoformat() + "Z"
        src_ip = source_ip or actor.source_ips[0]
        sess = session_id or f"sess_{actor.actor_id}_{uuid.uuid4().hex[:8]}"

        payload = {
            "tactic": tactic,
            "username": actor.credential_profile.get("username", "admin"),
            "user_agent": actor.user_agent
        }
        if payload_details:
            payload.update(payload_details)

        return {
            "event_id": event_id,
            "timestamp": iso_ts,
            "real_timestamp": timestamp_sec,
            "node_id": node.node_id,
            "service_id": service,
            "source_ip": src_ip,
            "source_port": 40000 + (hash(event_id) % 20000),
            "dest_ip": node.ip_address,
            "dest_port": 22 if service == "ssh" else (80 if service == "http" else 445),
            "session_id": sess,
            "actor_id": actor.actor_id,
            "payload": payload,
            "data_lineage": {
                "raw_repo": node.honeypot_type,
                "schema_version": "2.0.0",
                "ingest_timestamp": iso_ts
            }
        }
