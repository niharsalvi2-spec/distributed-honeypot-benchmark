"""
Heartbeat Health Monitor with Failure Detection.
"""
import time
from typing import Dict, Any

class HealthMonitor:
    def __init__(self, heartbeat_timeout_sec: float = 10.0):
        self.timeout = heartbeat_timeout_sec
        self.last_heartbeats: Dict[str, float] = {}

    def record_heartbeat(self, node_id: str):
        self.last_heartbeats[node_id] = time.time()

    def check_status(self, node_id: str) -> str:
        last = self.last_heartbeats.get(node_id)
        if not last:
            return "UNREGISTERED"
        if time.time() - last > self.timeout:
            return "TIMED_OUT"
        return "HEALTHY"
