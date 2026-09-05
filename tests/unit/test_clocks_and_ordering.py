"""
Unit Tests for Distributed Clocks, Ordering & Comparator.
"""
import pytest
from distributed.clocks.lamport_clock import LamportClock
from distributed.clocks.vector_clock import VectorClock
from distributed.clocks.clock_comparator import ClockComparator
from distributed.ordering.lamport_ordering import LamportOrdering

def test_lamport_clock_mechanics():
    c1 = LamportClock()
    c2 = LamportClock()
    
    t1 = c1.tick()
    assert t1 == 1
    
    # Message send from c1 to c2
    t2 = c2.update(t1)
    assert t2 == 2
    assert c2.time == 2

def test_vector_clock_causality():
    v1 = VectorClock("node_A")
    v2 = VectorClock("node_B")
    
    v1.tick()  # node_A: 1
    assert VectorClock.compare(v1.clock, v2.clock) == "AFTER"
    assert VectorClock.compare(v2.clock, v1.clock) == "BEFORE"
    
    v2.tick()  # node_B: 1 (independent)
    # Concurrent!
    assert VectorClock.compare(v1.clock, v2.clock) == "CONCURRENT"
    
    # Message from A to B
    v2.update(v1.clock)
    assert VectorClock.compare(v1.clock, v2.clock) == "BEFORE"

def test_clock_comparator():
    truth = ["e1", "e2", "e3", "e4"]
    observed_inverted = ["e1", "e3", "e2", "e4"]  # e2 and e3 inverted
    
    inversions, rate = ClockComparator.compute_inversions(truth, observed_inverted)
    assert inversions == 1
    assert rate == round(1 / 6.0, 4)
    
    tau = ClockComparator.compute_kendall_tau(truth, observed_inverted)
    assert 0.0 < tau < 1.0

def test_lamport_ordering_sort():
    events = [
        {"node_id": "B", "timestamps": {"lamport_logical": 2}},
        {"node_id": "A", "timestamps": {"lamport_logical": 1}},
        {"node_id": "A", "timestamps": {"lamport_logical": 2}}
    ]
    sorted_evts = LamportOrdering.sort(events)
    assert sorted_evts[0]["node_id"] == "A"
    assert sorted_evts[0]["timestamps"]["lamport_logical"] == 1
    # Tie-breaker by node_id: A before B for lamport=2
    assert sorted_evts[1]["node_id"] == "A"
    assert sorted_evts[2]["node_id"] == "B"
