"""
Central Telemetry Consumer.
Dequeues messages, updates central clock states, and provides ordered access.
"""
from typing import Optional, Dict, Any
from distributed.communication.queue import ResilientQueue
from distributed.communication.message import Message
from distributed.clocks.lamport_clock import LamportClock
from distributed.clocks.vector_clock import VectorClock

class EventConsumer:
    def __init__(self, queue: ResilientQueue, central_node_id: str = "central_collector"):
        self.queue = queue
        self.lamport_clock = LamportClock()
        self.vector_clock = VectorClock(central_node_id)

    def consume(self, timeout: float = 1.0) -> Optional[Message]:
        msg = self.queue.get(block=True, timeout=timeout)
        if msg:
            self.lamport_clock.update(msg.timestamp_lamport)
            self.vector_clock.update(msg.vector_clock)
        return msg
