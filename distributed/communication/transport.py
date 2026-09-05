"""
Pluggable Transport Layer supporting in-memory queues and HTTP REST endpoints.
"""
import requests
import json
from typing import Dict, Any, Optional
from distributed.communication.message import Message

class Transport:
    def __init__(self, endpoint_url: Optional[str] = None):
        self.endpoint_url = endpoint_url

    def send(self, message: Message) -> bool:
        if not self.endpoint_url:
            return True
        try:
            resp = requests.post(self.endpoint_url, json=message.to_dict(), timeout=2.0)
            return resp.status_code in [200, 201, 202]
        except Exception:
            return False
