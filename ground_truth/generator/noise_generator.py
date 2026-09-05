"""
Background Noise & Perturbation Generator
Injects internet-wide scanning noise, duplicate telemetry events, and packet drops.
"""
import random
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from ground_truth.generator.topology_generator import HoneypotNode

class NoiseGenerator:
    """
    Generates realistic uncoordinated scanning noise and fault perturbations.
    """
    SCANNER_IPS = [
        "198.51.100.4", "198.51.100.8", "203.0.113.88",
        "71.6.135.131", "162.142.125.0", "192.241.220.10"
    ]

    def __init__(self, seed: Optional[int] = 42):
        self.rng = random.Random(seed)

    def generate_noise_events(self, nodes: List[HoneypotNode], count: int,
                              start_time: float, end_time: float) -> List[Dict[str, Any]]:
        noise_events = []
        for i in range(count):
            node = self.rng.choice(nodes)
            ts_sec = self.rng.uniform(start_time, end_time)
            iso_ts = datetime.utcfromtimestamp(ts_sec).isoformat() + "Z"
            service = self.rng.choice(node.services)
            ev_id = f"noise_{self.rng.randint(0, 0xFFFFFFFF):08x}"

            ev = {
                "event_id": ev_id,
                "timestamp": iso_ts,
                "real_timestamp": ts_sec,
                "node_id": node.node_id,
                "service_id": service,
                "source_ip": self.rng.choice(self.SCANNER_IPS),
                "source_port": self.rng.randint(30000, 65000),
                "dest_ip": node.ip_address,
                "dest_port": 22 if service == "ssh" else (80 if service == "http" else 445),
                "session_id": f"sess_noise_{self.rng.randint(0, 0xFFFFFF):06x}",
                "actor_id": "BENIGN_SCANNER_NOISE",
                "payload": {
                    "scan_type": "SYN_PROBE",
                    "user_agent": "masscan/1.0"
                },
                "data_lineage": {
                    "raw_repo": node.honeypot_type,
                    "schema_version": "2.0.0",
                    "ingest_timestamp": iso_ts
                }
            }
            noise_events.append(ev)
        return noise_events

    def inject_duplicates(self, events: List[Dict[str, Any]], rate: float = 0.05) -> List[Dict[str, Any]]:
        """
        Duplicates a fraction of events to simulate transport-layer retransmissions.
        """
        res = list(events)
        for ev in events:
            if self.rng.random() < rate:
                dup = dict(ev)
                res.append(dup)
        return res

    def inject_drops(self, events: List[Dict[str, Any]], drop_rate: float = 0.05) -> List[Dict[str, Any]]:
        """
        Randomly drops a fraction of events to simulate telemetry loss.
        """
        return [ev for ev in events if self.rng.random() >= drop_rate]
