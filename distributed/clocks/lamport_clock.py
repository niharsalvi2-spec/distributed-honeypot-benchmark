"""
Lamport Logical Clock implementation for partial event ordering.
"""
import threading
from typing import Optional, Union, Dict, Any

class LamportClock:
    def __init__(self, node_id: Union[str, int] = "node_0", initial_time: int = 0, initial_value: Optional[int] = None):
        if isinstance(node_id, int):
            self.node_id = f"node_{node_id}"
            self.time = node_id
        else:
            self.node_id = str(node_id)
            self.time = initial_value if initial_value is not None else initial_time
        self.lock = threading.Lock()

    def tick(self) -> int:
        with self.lock:
            self.time += 1
            return self.time

    def update(self, received_time: int) -> int:
        with self.lock:
            self.time = max(self.time, received_time) + 1
            return self.time

    def read(self) -> int:
        with self.lock:
            return self.time

    def to_dict(self) -> Dict[str, Any]:
        with self.lock:
            return {"node_id": self.node_id, "value": self.time}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LamportClock":
        return cls(node_id=data.get("node_id", "node_0"), initial_time=data.get("value", 0))
