"""
Distributed Message Transport & Logical Clock Channel
Simulates inter-node message passing where send() and receive() update
Lamport Timestamps and Vector Clocks in accordance with distributed systems theory.
"""
import time
import random
from typing import Dict, Any, Optional, List
from distributed.communication.message import Message
from distributed.clocks.lamport_clock import LamportClock
from distributed.clocks.vector_clock import VectorClock

class DistributedNode:
    """
    A logical honeypot sensor or collector node participating in distributed event ordering.
    Maintains independent Lamport and Vector Clocks.
    """
    def __init__(self, node_id: str, cluster_nodes: Optional[List[str]] = None):
        self.node_id = node_id
        cluster = cluster_nodes or [node_id]
        if node_id not in cluster:
            cluster.append(node_id)
        self.lamport_clock = LamportClock()
        self.vector_clock = VectorClock(node_id=node_id, num_nodes=len(cluster))
        self.received_log: List[Dict[str, Any]] = []

    def send_event(
        self,
        event_payload: Dict[str, Any],
        recipient_id: str,
        channel: 'DistributedChannel'
    ) -> Message:
        """
        Sends an event to another node or collector.
        Advances local Lamport and Vector clocks, attaches clock envelopes, and delivers to channel.
        """
        # 1. Local clock ticks
        self.lamport_clock.tick()
        self.vector_clock.tick()

        # 2. Package message with clock metadata
        msg = Message(
            sender_id=self.node_id,
            recipient_id=recipient_id,
            payload=event_payload,
            lamport_ts=self.lamport_clock.read(),
            vector_clock=dict(self.vector_clock.clock)
        )

        # 3. Deliver to network channel
        channel.transmit(msg)
        return msg

    def receive_event(self, msg: Message) -> Dict[str, Any]:
        """
        Receives an event message from the channel.
        Applies Lamport max rule: L_recv = max(L_recv, L_msg) + 1
        Applies Vector max rule: V_recv[k] = max(V_recv[k], V_msg[k])
        """
        # Update clocks
        self.lamport_clock.update(msg.timestamp_lamport)
        self.vector_clock.update(msg.vector_clock)

        event_record = dict(msg.payload)
        event_record["_received_lamport_ts"] = self.lamport_clock.read()
        event_record["_received_vector_clock"] = dict(self.vector_clock.clock)
        event_record["_sender_node"] = msg.sender_id
        event_record["_receiver_node"] = self.node_id

        self.received_log.append(event_record)
        return event_record

class DistributedChannel:
    """
    Simulated network transport supporting synthetic latency, jitter, and packet loss.
    """
    def __init__(self, latency_ms: float = 5.0, jitter_ms: float = 0.0, drop_rate: float = 0.0):
        self.latency_ms = latency_ms
        self.jitter_ms = jitter_ms
        self.drop_rate = drop_rate
        self.transit_buffer: List[Message] = []

    def transmit(self, msg: Message) -> bool:
        """
        Transmits message through channel with simulated loss.
        """
        if self.drop_rate > 0.0 and random.random() < self.drop_rate:
            # Packet dropped due to simulated network partition/loss
            return False
        self.transit_buffer.append(msg)
        return True

    def deliver_all(self, nodes_registry: Dict[str, DistributedNode]) -> int:
        """
        Delivers all in-transit messages to their destination nodes in FIFO or causal order.
        """
        delivered = 0
        while self.transit_buffer:
            msg = self.transit_buffer.pop(0)
            recipient = nodes_registry.get(msg.recipient_id)
            if recipient:
                recipient.receive_event(msg)
                delivered += 1
        return delivered
