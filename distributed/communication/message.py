"""
Message Envelope Specification for Inter-Process & Distributed Communication.
Encapsulates payload with physical and logical distributed clock metadata.
"""
import uuid
import time
from typing import Dict, Any, Optional

class Message:
    def __init__(self, sender_id: str, payload: Dict[str, Any], recipient_id: str = "collector",
                 lamport_ts: int = 0, vector_clock: Optional[Dict[str, int]] = None,
                 message_id: Optional[str] = None):
        self.message_id = message_id or f"msg_{uuid.uuid4().hex[:8]}"
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.payload = payload
        self.timestamp_physical = time.time()
        self.timestamp_lamport = lamport_ts
        self.vector_clock = vector_clock or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message_id": self.message_id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "timestamp_physical": self.timestamp_physical,
            "timestamp_lamport": self.timestamp_lamport,
            "vector_clock": self.vector_clock,
            "payload": self.payload
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        msg = cls(
            sender_id=data["sender_id"],
            payload=data["payload"],
            recipient_id=data.get("recipient_id", "collector"),
            lamport_ts=data.get("timestamp_lamport", 0),
            vector_clock=data.get("vector_clock", {}),
            message_id=data.get("message_id")
        )
        msg.timestamp_physical = data.get("timestamp_physical", time.time())
        return msg
