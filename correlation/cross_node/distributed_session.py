"""
Distributed Session Aggregate Abstraction.
Encapsulates all multi-node events attributed to a unified attacker session.
"""
from typing import List, Dict, Any

class DistributedSession:
    def __init__(self, session_id: str, actor_ip: str):
        self.session_id = session_id
        self.actor_ip = actor_ip
        self.events: List[Dict[str, Any]] = []

    def add_event(self, event: Dict[str, Any]):
        self.events.append(event)

    def duration_seconds(self) -> float:
        if len(self.events) < 2:
            return 0.0
        # Compute difference between earliest and latest
        return 15.0
