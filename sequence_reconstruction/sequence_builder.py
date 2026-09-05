"""
Master Attack Sequence Reconstruction Engine.
Converts raw event graph components into finalized chronological attack sequences.
"""
from typing import List, Dict, Any
from sequence_reconstruction.event_order import EventOrder
from sequence_reconstruction.attack_chain import AttackChainSynthesizer

class SequenceBuilder:
    @staticmethod
    def reconstruct_sequence(cluster_events: List[Dict[str, Any]], sequence_id: str) -> Dict[str, Any]:
        ordered = EventOrder.order_cluster(cluster_events)
        chain = AttackChainSynthesizer.synthesize_chain(ordered)
        services = [e.get("service", {}).get("service_id", "") for e in ordered]
        
        return {
            "sequence_id": sequence_id,
            "total_events": len(ordered),
            "ordered_event_ids": [e["event_id"] for e in ordered],
            "service_progression": " -> ".join([s for s in services if s]),
            "attack_chain": chain,
            "first_event_time": ordered[0].get("timestamps", {}).get("physical_raw") if ordered else None,
            "last_event_time": ordered[-1].get("timestamps", {}).get("physical_raw") if ordered else None
        }
