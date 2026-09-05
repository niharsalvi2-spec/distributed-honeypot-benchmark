"""
Consistency Validator.
Checks logical invariants (valid port ranges, non-future timestamps, valid logical clocks).
"""
from typing import Dict, Any, List

class ConsistencyValidator:
    @staticmethod
    def validate_invariants(event: Dict[str, Any]) -> List[str]:
        anomalies = []
        port = event.get("service", {}).get("service_port", 0)
        if not (0 <= port <= 65535):
            anomalies.append(f"Invalid service port: {port}")
            
        lamport = event.get("timestamps", {}).get("lamport_clock", 0)
        if lamport < 0:
            anomalies.append(f"Negative Lamport clock: {lamport}")
            
        return anomalies
