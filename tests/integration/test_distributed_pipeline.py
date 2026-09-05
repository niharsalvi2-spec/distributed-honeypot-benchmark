"""
Integration Test: Distributed Pipeline
Tests full lifecycle from raw logs -> normalizer -> logical clocks -> ordering -> correlation.
"""
import pytest
from collectors.normalization.normalize import EventNormalizer
from distributed.clocks.lamport_clock import LamportClock
from distributed.ordering.lamport_ordering import LamportOrder
from correlation.cross_service.service_linker import CrossServiceLinker
from correlation.evaluation.correlation_accuracy import CorrelationEvaluator

def test_full_distributed_lifecycle():
    raw_events = [
        {"event_id": "EV1", "service": "http", "src_ip": "198.51.100.42", "node_id": "node_alpha"},
        {"event_id": "EV2", "service": "ssh", "src_ip": "198.51.100.42", "node_id": "node_alpha"},
        {"event_id": "EV3", "service": "ftp", "src_ip": "198.51.100.42", "node_id": "node_beta"}
    ]

    # 1. Normalization
    normalizer = EventNormalizer()
    normalized = [normalizer.normalize_event("cowrie", ev) for ev in raw_events]
    assert len(normalized) == 3

    # 2. Lamport Clock Tagging
    clock = LamportClock()
    tagged = []
    for ev in normalized:
        c = clock.tick()
        tagged.append((ev, c))

    # 3. Lamport Ordering
    ordered = LamportOrder.sort_by_lamport(tagged)
    assert len(ordered) == 3
    assert ordered[0]["event_id"] == "EV1"

    # 4. Correlation
    linker = CrossServiceLinker()
    for ev in ordered:
        linker.ingest_event(ev)
    links = linker.get_cross_service_links()
    assert len(links) > 0

    # 5. Evaluation
    gt = {("EV1", "EV2"), ("EV2", "EV3")}
    metrics = CorrelationEvaluator.evaluate(set(links), gt)
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics
