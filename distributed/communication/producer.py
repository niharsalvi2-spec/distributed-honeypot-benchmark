"""
Distributed Node Event Producer.
Ticks local logical clock, envelopes payload into Message, and dispatches via transport.
"""
from typing import Dict, Any
from distributed.communication.message import Message
from distributed.communication.transport import Transport
from distributed.clocks.lamport_clock import LamportClock
from distributed.clocks.vector_clock import VectorClock

class EventProducer:
    def __init__(self, node_id: str, transport: Transport):
        self.node_id = node_id
        self.transport = transport
        self.lamport_clock = LamportClock()
        self.vector_clock = VectorClock(node_id)

    def produce(self, event_payload: Dict[str, Any]) -> bool:
        l_ts = self.lamport_clock.tick()
        v_ts = self.vector_clock.tick()
        msg = Message(
            sender_id=self.node_id,
            payload=event_payload,
            lamport_ts=l_ts,
            vector_clock=v_ts
        )
        return self.transport.send(msg)
