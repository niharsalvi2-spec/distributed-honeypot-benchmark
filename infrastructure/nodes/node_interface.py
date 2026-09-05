"""
Common Node Interface for Distributed Honeypot Benchmark Framework.
Both Native (Python process) and Containerized (Docker) nodes implement this contract.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class Node(ABC):
    """
    Abstract base class defining the operational contract for all sensor and decoy nodes.
    """

    def __init__(self, node_id: str, service: str, port: int, execution_mode: str = "native"):
        self.node_id = node_id
        self.service = service
        self.port = port
        self.execution_mode = execution_mode
        self.is_running = False

    @abstractmethod
    def start(self) -> bool:
        """Starts the node process or container."""
        pass

    @abstractmethod
    def stop(self) -> bool:
        """Stops the node process or container."""
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Checks if the service port is reachable and process is healthy."""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, Any]:
        """Returns runtime resource utilization (CPU, memory, uptime, events emitted)."""
        pass

    @abstractmethod
    def emit_event(self, event_payload: Dict[str, Any]) -> bool:
        """Transmits an observed attack event to the designated central collector."""
        pass
