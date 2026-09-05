"""
Docker Container Node Implementation.
Manages honeypot sensor containers via Docker CLI or daemon.
"""
import time
import subprocess
import requests
import logging
from typing import Dict, Any, Optional
from infrastructure.nodes.node_interface import Node

logger = logging.getLogger(__name__)

class DockerNode(Node):
    def __init__(self, node_id: str, service: str, port: int, container_name: str, collector_url: str = "http://collector:8000/events"):
        super().__init__(node_id=node_id, service=service, port=port, execution_mode="docker")
        self.container_name = container_name
        self.collector_url = collector_url
        self.start_time: Optional[float] = None
        self.events_emitted = 0

    def start(self) -> bool:
        """Starts the specified container via docker start."""
        try:
            res = subprocess.run(["docker", "start", self.container_name], capture_output=True, text=True)
            self.is_running = (res.returncode == 0)
            if self.is_running:
                self.start_time = time.time()
                logger.info("[DockerNode:%s] Started container %s", self.node_id, self.container_name)
            return self.is_running
        except Exception as e:
            logger.error("[DockerNode:%s] Docker daemon unavailable: %s", self.node_id, e)
            self.is_running = False
            return False

    def stop(self) -> bool:
        """Stops the container."""
        try:
            res = subprocess.run(["docker", "stop", self.container_name], capture_output=True, text=True)
            self.is_running = False
            return (res.returncode == 0)
        except Exception:
            return False

    def health_check(self) -> Dict[str, Any]:
        """Queries docker inspect for running status."""
        status = "STOPPED"
        try:
            res = subprocess.run(["docker", "inspect", "-f", "{{.State.Running}}", self.container_name], capture_output=True, text=True)
            if res.returncode == 0 and "true" in res.stdout.lower():
                status = "HEALTHY"
                self.is_running = True
            else:
                status = "STOPPED"
                self.is_running = False
        except Exception:
            status = "DAEMON_UNAVAILABLE"

        return {
            "node_id": self.node_id,
            "container_name": self.container_name,
            "status": status,
            "execution_mode": self.execution_mode,
            "port": self.port,
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0.0
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Returns container resource utilization via docker stats or simulated values."""
        return {
            "node_id": self.node_id,
            "container_name": self.container_name,
            "execution_mode": "docker",
            "events_emitted": self.events_emitted,
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0.0
        }

    def emit_event(self, event_payload: Dict[str, Any]) -> bool:
        """Transmits event payload to collector container."""
        event_payload["node_id"] = self.node_id
        event_payload["service"] = self.service
        event_payload["execution_mode"] = self.execution_mode
        self.events_emitted += 1
        try:
            resp = requests.post(self.collector_url, json=event_payload, timeout=2.0)
            return resp.status_code in [200, 201, 202]
        except Exception:
            return False
