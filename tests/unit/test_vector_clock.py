"""
Unit Test: Vector Clock
Tests multi-node causal tracking, concurrent event detection, and vector updates.
"""
import pytest
from distributed.clocks.vector_clock import VectorClock

def test_vector_clock_tick_and_comparison():
    v1 = VectorClock("node_1", 2)
    v2 = VectorClock("node_2", 2)

    v1.tick()  # node_1: [1, 0]
    v2.tick()  # node_2: [0, 1]

    # Concurrent events (neither happens before the other)
    assert v1.is_concurrent(v2) is True
    assert v1.happens_before(v2) is False

def test_vector_clock_message_passing():
    v1 = VectorClock("node_1", 2)
    v2 = VectorClock("node_2", 2)

    v1.tick()  # node_1: [1, 0]
    v2.update(v1.clock)  # node_2 absorbs v1 and ticks: [1, 1]

    assert v1.happens_before(v2) is True
    assert v2.happens_before(v1) is False
