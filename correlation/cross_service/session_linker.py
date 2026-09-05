"""
Cross-Service Multi-Evidence Scoring Engine.
Combines Source, Temporal, Service Transition, and Causal Order evidence.
Score = w_s * S_source + w_t * S_temporal + w_v * S_service + w_o * S_order
"""
from typing import Dict, Any, Tuple
from correlation.cross_service.service_linker import ServiceLinker
from correlation.cross_service.temporal_linker import TemporalLinker

class SessionLinker:
    def __init__(self, w_source: float = 0.35, w_temporal: float = 0.25,
                 w_service: float = 0.25, w_order: float = 0.15,
                 high_threshold: float = 0.75, low_threshold: float = 0.45):
        self.w_s = w_source
        self.w_t = w_temporal
        self.w_v = w_service
        self.w_o = w_order
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold
        self.temporal_linker = TemporalLinker()

    def evaluate_pair(self, e1: Dict[str, Any], e2: Dict[str, Any]) -> Tuple[float, str]:
        # 1. Source score
        ip1 = e1.get("source", {}).get("ip")
        ip2 = e2.get("source", {}).get("ip")
        sub1 = e1.get("source", {}).get("subnet")
        sub2 = e2.get("source", {}).get("subnet")
        s_source = 1.0 if ip1 == ip2 else (0.6 if sub1 and sub1 == sub2 else 0.1)

        # 2. Temporal score
        s_temporal = self.temporal_linker.compute_proximity(e1, e2)

        # 3. Service transition score
        svc1 = e1.get("service", {}).get("service_id", "unknown")
        svc2 = e2.get("service", {}).get("service_id", "unknown")
        s_service = ServiceLinker.score_transition(svc1, svc2)

        # 4. Causal order score (Lamport / Vector consistency)
        l1 = e1.get("timestamps", {}).get("lamport_logical", 0)
        l2 = e2.get("timestamps", {}).get("lamport_logical", 0)
        s_order = 1.0 if l1 != l2 else 0.5

        total_score = (self.w_s * s_source +
                       self.w_t * s_temporal +
                       self.w_v * s_service +
                       self.w_o * s_order)

        confidence = "STRONG" if total_score >= self.high_threshold else (
            "WEAK" if total_score >= self.low_threshold else "UNCERTAIN"
        )
        return total_score, confidence
