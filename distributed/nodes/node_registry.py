"""
Node Registry & Service Discovery Engine.
Tracks active honeypot nodes, service allocations, and cluster membership.
"""
import threading
from typing import Dict, Any, List, Optional

class NodeRegistry:
    def __init__(self):
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register(self, node_id: str, service: str, port: int, execution_mode: str = "native") -> bool:
        with self._lock:
            self._nodes[node_id] = {
                "node_id": node_id,
                "service": service,
                "port": port,
                "mode": execution_mode,
                "status": "HEALTHY",
                "registered_at": time.time() if 'time' in globals() else 0.0
            }
            return True

    def deregister(self, node_id: str) -> bool:
        with self._lock:
            if node_id in self._nodes:
                del self._nodes[node_id]
                return True
            return False

    def list_nodes(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._nodes.values())
