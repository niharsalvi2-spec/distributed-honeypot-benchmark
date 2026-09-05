"""
Native Python Process Node Implementation.
Executes honeypot sensors as managed asynchronous processes or threads.
"""
import time
import socket
import psutil
import requests
import logging
from typing import Dict, Any, Optional
from infrastructure.nodes.node_interface import Node

logger = logging.getLogger(__name__)

class NativeNode(Node):
    def __init__(self, node_id: str, service: str, port: int, collector_url: str = "http://127.0.0.1:8000/events"):
        super().__init__(node_id=node_id, service=service, port=port, execution_mode="native")
        self.collector_url = collector_url
        self.process: Optional[psutil.Process] = None
        self.start_time: Optional[float] = None
        self.events_emitted = 0

    def start(self) -> bool:
        """Marks node as active and records start time."""
        self.start_time = time.time()
        self.is_running = True
        logger.info("[NativeNode:%s] Started on port %d (%s)", self.node_id, self.port, self.service)
        return True

    def stop(self) -> bool:
        """Shuts down the node."""
        self.is_running = False
        logger.info("[NativeNode:%s] Stopped", self.node_id)
        return True

    def health_check(self) -> Dict[str, Any]:
        """Verifies if the designated service port is bound or accessible."""
        status = "HEALTHY" if self.is_running else "STOPPED"
        port_open = False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                port_open = (s.connect_ex(('127.0.0.1', self.port)) == 0)
        except Exception:
            port_open = False

        return {
            "node_id": self.node_id,
            "status": status,
            "execution_mode": self.execution_mode,
            "port": self.port,
            "port_accessible": port_open,
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0.0
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Returns CPU, memory, and emission counts."""
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent
        return {
            "node_id": self.node_id,
            "execution_mode": "native",
            "cpu_percent": cpu,
            "memory_percent": mem,
            "events_emitted": self.events_emitted,
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0.0
        }

    def emit_event(self, event_payload: Dict[str, Any]) -> bool:
        """Emits event to collector HTTP API."""
        event_payload["node_id"] = self.node_id
        event_payload["service"] = self.service
        event_payload["execution_mode"] = self.execution_mode
        self.events_emitted += 1
        try:
            resp = requests.post(self.collector_url, json=event_payload, timeout=2.0)
            return resp.status_code in [200, 201, 202]
        except Exception:
            # Buffer locally if collector is down
            return False
